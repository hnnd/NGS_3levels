#!/bin/bash
#$ -S /bin/bash
#$ -N p05_gwas
#$ -cwd
#$ -j y
#$ -pe smp 8
#$ -l h_vmem=16G
# ============================================================
# 脚本名称：05_gwas_gemma.sh
# 功能描述：p05 GWAS —— 基因型质控 → 表型写入 fam → Q 协变量 → 亲缘矩阵 K
#           → GLM 对照 + MLM 主线 + PC 数扫描（供 λ–PC 曲线）
# 作者：王运生
# 日期：2026-08-29
# 提交方式：qsub 05_gwas_gemma.sh            【禁止在登录节点直接 bash 运行】
# 配套讲义：02_lectures/phd/topic05_gwas/05_gwas_lecture.md §5.3–5.5
# ============================================================
#
# 设计要点（讲义 §4.2、⑦ 7.2、⑨）：
#   1) **一定要跑不校正的 GLM 对照**。只有把 GLM 与 MLM 的 QQ 图并排，才能
#      看出"校正到底做了什么"，也才能判断信号是不是被一起抹平了。
#   2) K 用 **LD 剪枝集**算（p04 的 struct.pruned），不用全标记集——长 LD
#      区块会主导亲缘估计。
#   3) GEMMA 的 -c 协变量文件**必须自带一列全 1 作截距**，它不会替你加（⑨ E3）。
#   4) HWE 过滤默认关闭。自交 / 克隆群体开 --hwe 会删掉真实生物学信号
#      （p04 §4.3）；确认你的体系是随机交配后再设 HWE=1e-6。
#   5) GEMMA 在 PLINK 过滤之上还有自己的默认过滤，输出 SNP 数会更少（⑨ E6）。
#      方法学里报告的必须是 GEMMA 日志里的 "number of analyzed SNPs"。
#
# 环境变量：
#   BFILE     p04 交付的 GWAS 版基因型前缀              默认 ./popgen/struct
#   PRUNED    p04 交付的 LD 剪枝集前缀                  默认 ${BFILE}.pruned
#   EIGENVEC  p04 交付的 pca.eigenvec                   默认 ./popgen/pca.eigenvec
#   PHENO     表型文件：FID  IID  value（三列，制表符） 必填
#   OUTDIR    输出目录                                  默认 ./gwas
#   MAF/GENO/MIND/HWE  质控阈值                          默认 0.05 / 0.1 / 0.1 / 0（0 = 不做）
#   PCLIST    PC 数扫描列表                             默认 "0 2 4 6 10"
# ============================================================

set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_popgen

for tool in plink gemma awk; do
    command -v "${tool}" >/dev/null || { echo "[FATAL] ${tool} 不在 PATH，环境没激活成功"; exit 1; }
done

BFILE="${BFILE:-./popgen/struct}"
PRUNED="${PRUNED:-${BFILE}.pruned}"
EIGENVEC="${EIGENVEC:-./popgen/pca.eigenvec}"
PHENO="${PHENO:?必须指定 PHENO=表型文件（三列：FID IID value；缺失写 NA）}"
OUTDIR="${OUTDIR:-./gwas}"
MAF="${MAF:-0.05}"; GENO="${GENO:-0.1}"; MIND="${MIND:-0.1}"; HWE="${HWE:-0}"
PCLIST="${PCLIST:-0 2 4 6 10}"
mkdir -p "${OUTDIR}"; cd "${OUTDIR}"

# ---- 0) 表型文件体检（⑨ E2：本讲最高频错误）----
# 查 \r 本身而不是只看 file 的 CRLF 字样：旧 Mac 纯 CR 行尾（RDP1 原始表型就是）file 报的是
# "with CR line terminators"，抓 CRLF 会漏掉，而那时 wc -l 为 0、列数检查却照样通过。
if LC_ALL=C grep -q $'\r' "${PHENO}"; then
    echo "[FATAL] ${PHENO} 含 \\r（CRLF 或旧 Mac 纯 CR 行尾）。\\r 会粘在 IID 上导致全部匹配失败。"
    echo "        CRLF 用 dos2unix；纯 CR 用 tr '\\r' '\\n'（download_phd.sh 已对 RDP1 表型做了这一步）。"
    exit 1
fi
[[ "$(wc -l < "${PHENO}")" -gt 0 ]] || { echo "[FATAL] ${PHENO} 没有换行符（0 行），格式不对"; exit 1; }
NCOL=$(head -1 "${PHENO}" | awk '{print NF}')
[[ "${NCOL}" -ge 3 ]] || { echo "[FATAL] ${PHENO} 只有 ${NCOL} 列。PLINK --pheno 要 FID IID value 三列（⑨ E2）"; exit 1; }
echo "[INFO] 表型样本数 $(wc -l < "${PHENO}")；基因型个体数 $(wc -l < "${BFILE}.fam")"

# ---- 1) 基因型质控。每个阈值的理由见讲义 §5.3 的表 ----
HWE_OPT=""
if [[ "${HWE}" != "0" ]]; then
    HWE_OPT="--hwe ${HWE}"
    echo "[WARN] 已开启 --hwe ${HWE}。确认你的群体是随机交配的；自交/克隆群体请把 HWE 设回 0。"
fi
# shellcheck disable=SC2086
plink --bfile "${BFILE}" --allow-extra-chr \
      --maf "${MAF}" --geno "${GENO}" --mind "${MIND}" ${HWE_OPT} \
      --pheno "${PHENO}" --allow-no-sex \
      --make-bed --out gwas
echo "[INFO] 质控后：$(wc -l < gwas.bim) 个标记 / $(wc -l < gwas.fam) 个个体"

# ---- 2) fam 第 6 列体检（GEMMA 只读它，不读 --pheno；⑨ E4）----
NVALID=$(awk '$6!="-9" && $6!="NA" && $6!=""' gwas.fam | wc -l)
[[ "${NVALID}" -gt 0 ]] || { echo "[FATAL] gwas.fam 第 6 列没有有效表型，GEMMA 会报 analyzed individuals = 0（⑨ E4）"; exit 1; }
echo "[INFO] fam 中有效表型个体数 ${NVALID}"

# ---- 3) 亲缘矩阵 K：用 LD 剪枝集 ----
# GEMMA 会剔除表型缺失的个体（-gk 也一样），所以剪枝集也要带上表型
plink --bfile "${PRUNED}" --allow-extra-chr --pheno "${PHENO}" --allow-no-sex --make-bed --out kin_in
gemma -bfile kin_in -gk 1 -o kin        # -gk 1 centered；-gk 2 standardized（换要写进方法学）
[[ -s output/kin.cXX.txt ]] || { echo "[FATAL] 没找到 output/kin.cXX.txt。GEMMA 默认写到 ./output/（⑨ E5）"; exit 1; }

# ---- 4) GLM 对照（不校正）----
gemma -bfile gwas -lm 4 -o glm_raw

# ---- 5) MLM + PC 数扫描：协变量第一列必须是全 1 的截距（⑨ E3）----
for NPC in ${PCLIST}; do
    if [[ "${NPC}" -eq 0 ]]; then
        awk '{print 1}' gwas.fam > "covar_pc0.txt"
    else
        # pca.eigenvec：第 1、2 列是 FID/IID，第 3 列起是 PC1..PC10
        awk -v n="${NPC}" 'NR==FNR{keep[$2]=1; next} ($2 in keep){
                printf "1"; for(i=3;i<=2+n;i++) printf "\t%s", $i; print ""
            }' gwas.fam "${EIGENVEC}" > "covar_pc${NPC}.txt"
    fi
    NROW=$(wc -l < "covar_pc${NPC}.txt")
    [[ "${NROW}" -eq "$(wc -l < gwas.fam)" ]] || \
        { echo "[FATAL] covar_pc${NPC}.txt 行数 ${NROW} 与 gwas.fam 不一致——协变量必须按 fam 行序"; exit 1; }
    gemma -bfile gwas -k output/kin.cXX.txt -c "covar_pc${NPC}.txt" -lmm 4 -o "mlm_pc${NPC}"
done

# ---- 6) 小样本预警：方差组分跑到边界（⑨ E10）----
for LOG in output/mlm_pc*.log.txt; do
    PVE=$(grep -m1 'pve estimate' "${LOG}" | awk -F'=' '{print $2}' | tr -d ' ')
    SE=$(grep -m1 'se(pve)'      "${LOG}" | awk -F'=' '{print $2}' | tr -d ' ')
    printf '  %-28s pve=%-10s se(pve)=%s\n' "$(basename "${LOG}")" "${PVE:-NA}" "${SE:-NA}"
    if [[ "${SE:-}" == "nan" || "${PVE:-}" == "1" ]]; then
        echo "  [WARN] 方差组分跑到边界——样本量相对标记数太小（⑨ E10）。减协变量或改用 GLM + 少量 PC，并如实说明。"
    fi
done

echo "[INFO] GEMMA 实际分析的标记数（**方法学里报这个**，不是 gwas.bim 的行数）："
grep -h 'number of analyzed SNPs' output/mlm_pc*.log.txt | sort -u | sed 's/^/  /'

cat <<'EOF'
------------------------------------------------------------
下一步：
  Rscript 05_gwas_diagnostics.R  gwas/output  <n_eff>   # 先 QQ + λ–PC 曲线，再看曼哈顿
  bash    05_postgwas_interval.sh                       # 选定模型后再做 clump 与区间
提醒：**不要**先看曼哈顿图（讲义 §4.4）。QQ 整体抬升时曼哈顿上的一切都不可解读。
------------------------------------------------------------
EOF
echo "[INFO] $(date '+%F %T') 完成，输出在 ${OUTDIR}/output"
