#!/bin/bash
#$ -S /bin/bash
#$ -N p05_postgwas
#$ -cwd
#$ -j y
#$ -pe smp 4
#$ -l h_vmem=8G
# ============================================================
# 脚本名称：05_postgwas_interval.sh
# 功能描述：p05 后 GWAS 挖掘 —— LD clumping → 候选区间界定（用 p04 的 LD 半衰距离）
#           → bedtools 取区间内基因 → 候选基因证据表骨架
# 作者：王运生
# 日期：2026-08-29
# 提交方式：qsub 05_postgwas_interval.sh     【禁止在登录节点直接 bash 运行】
# 配套讲义：02_lectures/phd/topic05_gwas/05_gwas_lecture.md §5.8、④ 4.5、⑥ 6.3
# ============================================================
#
# 设计要点（讲义 §4.5、⑨）：
#   1) **候选区间不是一个 SNP**。区间宽度由 p04 的 LD 半衰距离决定，报告时
#      必须写明用的是哪个距离、怎么算出来的。
#   2) PLINK --clump 默认找列名 P 与 SNP，而 GEMMA 输出的是 p_wald 与 rs，
#      因此 --clump-field / --clump-snp-field 必须显式写（⑨ E8）。
#   3) assoc/GFF3 是 1-based，BED 是 0-based 半开。转换错**不会报错**，
#      只会让 intersect 的结果整体错一位（⑨ E9、l0_04_formats）。
#   4) 染色体命名不一致（Chr01 / chr01 / 1）同样是不报错的错误，脚本先核对再跑。
#
# 环境变量：
#   BFILE     GWAS 基因型前缀                        默认 ./gwas/gwas
#   ASSOC     选定模型的关联结果                     默认 ./gwas/output/mlm_pc4.assoc.txt
#   GFF       与基因型同版本的注释                   必填
#   HALF      p04 算出的 LD 半衰距离（bp）           必填
#   P1/P2/R2/KB  clump 参数                          默认 1e-5 / 1e-3 / 0.2 / 500
#   OUTDIR    输出目录                               默认 ./postgwas
# ============================================================

set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_popgen

for tool in plink bedtools awk sort; do
    command -v "${tool}" >/dev/null || { echo "[FATAL] ${tool} 不在 PATH，环境没激活成功"; exit 1; }
done

BFILE="${BFILE:-./gwas/gwas}"
ASSOC="${ASSOC:-./gwas/output/mlm_pc4.assoc.txt}"
GFF="${GFF:?必须指定 GFF=与基因型同版本的 GFF3 注释}"
HALF="${HALF:?必须指定 HALF=p04 算出的 LD 半衰距离（bp），见 ld_decay.txt}"
P1="${P1:-1e-5}"; P2="${P2:-1e-3}"; R2="${R2:-0.2}"; KB="${KB:-500}"
OUTDIR="${OUTDIR:-./postgwas}"
mkdir -p "${OUTDIR}"

# ---- 0) 染色体命名一致性核对（⑨ E9：不报错的错误，只能事先查）----
comm -12 <(awk '!/^#/{print $1}' "${GFF}" | sort -u) \
         <(awk 'NR>1{print $1}' "${ASSOC}" | sort -u) > "${OUTDIR}/chr_shared.txt" || true
if [[ ! -s "${OUTDIR}/chr_shared.txt" ]]; then
    echo "[FATAL] GFF3 与关联结果的染色体名没有任何交集（Chr01 vs chr01 vs 1？）。"
    echo "        GFF3 示例：$(awk '!/^#/{print $1; exit}' "${GFF}")；ASSOC 示例：$(awk 'NR==2{print $1}' "${ASSOC}")"
    exit 1
fi
echo "[INFO] 染色体名交集 $(wc -l < "${OUTDIR}/chr_shared.txt") 条，命名一致性通过"

# ---- 1) LD clumping：把显著 SNP 归并成"位点"----
plink --bfile "${BFILE}" --allow-extra-chr \
      --clump "${ASSOC}" --clump-field p_wald --clump-snp-field rs \
      --clump-p1 "${P1}" --clump-p2 "${P2}" --clump-r2 "${R2}" --clump-kb "${KB}" \
      --out "${OUTDIR}/clump"
if [[ ! -s "${OUTDIR}/clump.clumped" ]]; then
    cat <<EOF
[WARN] 没有位点通过 --clump-p1 ${P1}。这**不是**调大阈值的理由。
       先回讲义 ⑥ 6.1 看 QQ 图：若尾部也贴合对角线，说明本来就没有可检出信号，
       该做的是回 §4.1 检查遗传力与样本量，而不是放宽阈值制造结果。
EOF
    exit 0
fi
NCLUMP=$(awk 'NF>0 && $1!="CHR"' "${OUTDIR}/clump.clumped" | wc -l)
echo "[INFO] clump 得到 ${NCLUMP} 个独立位点（clump.clumped 的 SP2 列是被吸收的 SNP）"

# ---- 2) 候选区间：峰值 SNP ± LD 半衰距离；1-based → 0-based 半开 ----
awk -v H="${HALF}" 'NF>0 && $1!="CHR" {
        s = $4 - H; if (s < 1) s = 1;
        printf "%s\t%d\t%d\t%s\t%s\n", $1, s-1, $4+H, $3, $5   # BED: start-1
     }' "${OUTDIR}/clump.clumped" | sort -k1,1 -k2,2n > "${OUTDIR}/peaks.bed"
echo "[INFO] 候选区间 $(wc -l < "${OUTDIR}/peaks.bed") 个，每侧 ${HALF} bp（来自 p04 的 LD 半衰距离）"

# ---- 3) 区间内基因 ----
awk 'BEGIN{OFS="\t"} !/^#/ && $3=="gene" {print $1, $4-1, $5, $9, ".", $7}' "${GFF}" \
    | sort -k1,1 -k2,2n > "${OUTDIR}/genes.bed"
bedtools intersect -a "${OUTDIR}/peaks.bed" -b "${OUTDIR}/genes.bed" -wa -wb \
    > "${OUTDIR}/candidate_genes_raw.tsv"
if [[ ! -s "${OUTDIR}/candidate_genes_raw.tsv" ]]; then
    echo "[WARN] 区间内一个基因都没有。先查 ① 染色体命名（已过第 0 步则排除）"
    echo "        ② GFF3 第 3 列是否真的用 'gene' 这个词（有些注释用 'mRNA'/'transcript'）"
fi

# ---- 4) 候选基因证据表骨架：把"几十个基因"变成"三五个可做实验的基因"----
{
  printf 'locus\tchr\tstart\tend\tpeak_snp\tpeak_p\tgene_id\tgene_start\tgene_end\tstrand\t'
  printf 'evid_variant_effect\tevid_expression\tevid_homolog_function\tevid_colocalization\tpriority\n'
  awk 'BEGIN{OFS="\t"} {
        split($9, a, /[;=]/); gid = (a[2] != "" ? a[2] : $9);
        printf "%s:%s-%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t\t\t\t\t\n",
               $1, $2+1, $3, $1, $2+1, $3, $4, $5, gid, $7+1, $8, $10
      }' "${OUTDIR}/candidate_genes_raw.tsv"
} > "${OUTDIR}/candidate_genes_table.tsv"

cat <<'EOF'
------------------------------------------------------------
候选基因表已生成骨架，**四列证据要你自己填**（讲义 §4.5）：
  evid_variant_effect   区间内有无 HIGH/MODERATE 影响的变异（SnpEff 注释）
  evid_expression       处理/组织特异表达、eQTL
  evid_homolog_function 已知抗性基因家族 / 通路成员 / 同源功能
  evid_colocalization   表达关联与表型关联是否共享同一因果变异
     —— 长 LD 区间里"各自独立地落在同一区间"非常常见，共定位就是用来排除它的。
写作提醒：区间内基因数远多于预期是长 LD 物种的**物理限制**，不是分析没做好；
          如实写出区间宽度与基因数，比挑一个"看起来最像"的基因下结论更经得起审稿。
------------------------------------------------------------
EOF
echo "[INFO] $(date '+%F %T') 完成，输出在 ${OUTDIR}"
