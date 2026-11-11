#!/bin/bash
#$ -S /bin/bash
#$ -N p04_qc_div
#$ -cwd
#$ -j y
#$ -pe smp 8
#$ -l h_vmem=8G
# ============================================================
# 脚本名称：04_popgen_qc_diversity.sh
# 功能描述：p04 群体遗传学基础 —— 群体层质控（两套产物）→ π / Watterson θ / Tajima's D
#           → 分群 F_ST → HWE（全样本 + 分群）
# 作者：王运生
# 日期：2026-08-29
# 提交方式：qsub 04_popgen_qc_diversity.sh    【禁止在登录节点直接 bash 运行】
# 配套讲义：02_lectures/phd/topic04_popgen/04_popgen_lecture.md §5.2–5.5
# ============================================================
#
# 设计要点（讲义 §4.3、§4.7）：
#   1) **产出两套过滤结果**：popgen.vcf.gz 不滤 MAF（π/θ/D/SFS 依赖低频等位，
#      滤 MAF 会把 Tajima's D 系统性推向正值）；struct.vcf.gz 滤 MAF，供
#      LD / PCA / ADMIXTURE / TreeMix 与 p05 的 GWAS 使用。照抄别人的单套
#      过滤脚本是本讲最常见的系统性错误。
#   2) **HWE 只算不滤**。自交 / 克隆繁殖群体里 --hwe 删掉的是真实生物学信号
#      （讲义 §4.3 与 ⑦ 7.2）。本脚本输出 hwe_*.hwe 供你按四条判别动作判断，
#      要不要过滤由你在报告里论证，不由脚本替你决定。
#   3) 个体缺失率**先算再定阈值**，不盲设 --mind。
#
# 环境变量（都有默认值，按需覆盖）：
#   VCF        输入群体 VCF（bgzip + tabix）        必填
#   OUTDIR     输出目录                             默认 ./popgen
#   POPS       分群定义目录，内含 <pop>.txt（每行一个样本名，与 VCF 头一致）
#   WIN/STEP   窗口大小 / 步长（bp）                默认 50000 / 10000
#   MINDP/MINGQ 个体基因型置缺失阈值               默认 5 / 20
# ============================================================

set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_popgen

for tool in bcftools vcftools plink tabix bgzip awk; do
    command -v "${tool}" >/dev/null || { echo "[FATAL] ${tool} 不在 PATH，环境没激活成功"; exit 1; }
done

VCF="${VCF:?必须指定 VCF=群体 VCF（bgzip 压缩且已建 tabix 索引）}"
OUTDIR="${OUTDIR:-./popgen}"
POPS="${POPS:-./pops}"
WIN="${WIN:-50000}"
STEP="${STEP:-10000}"
MINDP="${MINDP:-5}"
MINGQ="${MINGQ:-20}"
mkdir -p "${OUTDIR}"
cd "${OUTDIR}"

echo "[INFO] $(date '+%F %T') 输入 ${VCF}；窗口 ${WIN} bp / 步长 ${STEP} bp"

# ---- 0) 通用底座：双等位 SNP + 低质量基因型置缺失（置缺失，不是删位点）----
if [[ ! -s gtmask.vcf.gz ]]; then
    bcftools view -m2 -M2 -v snps "${VCF}" -Oz -o biallelic.vcf.gz
    bcftools filter -S . -e "FMT/DP<${MINDP} | FMT/GQ<${MINGQ}" \
        biallelic.vcf.gz -Oz -o gtmask.vcf.gz
    tabix -f -p vcf gtmask.vcf.gz
fi

# ---- 1) 两套过滤产物 ----
# ① 群体遗传学用：**不滤 MAF**
vcftools --gzvcf gtmask.vcf.gz --max-missing 0.8 --min-alleles 2 --max-alleles 2 \
         --recode --recode-INFO-all --stdout | bgzip -c > popgen.vcf.gz
tabix -f -p vcf popgen.vcf.gz
# ② 结构 / LD / 交付 p05 用：滤 MAF
vcftools --gzvcf gtmask.vcf.gz --max-missing 0.9 --maf 0.05 \
         --recode --recode-INFO-all --stdout | bgzip -c > struct.vcf.gz
tabix -f -p vcf struct.vcf.gz

echo "[INFO] 过滤前后位点数（写进方法学）："
for f in "${VCF}" popgen.vcf.gz struct.vcf.gz; do
    printf '  %-24s %s\n' "$(basename "${f}")" "$(bcftools index -n "${f}" 2>/dev/null || bcftools view -H "${f}" | wc -l)"
done

# ---- 2) 个体缺失率：先算分布再决定剔除谁 ----
vcftools --gzvcf popgen.vcf.gz --missing-indv --out qc
awk 'NR>1 && $5>0.2 {print $1}' qc.imiss > drop_indv.txt
echo "[INFO] 缺失率 > 0.2 的个体数：$(wc -l < drop_indv.txt)（清单 drop_indv.txt，交给 p05）"

# ---- 3) 多样性与中性检验（用不滤 MAF 的那套）----
vcftools --gzvcf popgen.vcf.gz --window-pi "${WIN}" --window-pi-step "${STEP}" --out div
vcftools --gzvcf popgen.vcf.gz --TajimaD "${WIN}" --out div          # --TajimaD 只接受窗口大小
echo "[INFO] 全基因组 Tajima's D 中位数（明显为正时先查是否误滤了 MAF，讲义 6.2）："
awk 'NR>1 && $4!="nan"{print $4}' div.Tajima.D | sort -g | awk '{a[NR]=$1} END{print "  median =", a[int(NR/2)+1], " n_windows =", NR}'

# ---- 4) 分群 F_ST（报告用 WEIGHTED_FST = ratio of averages，讲义 §4.2）----
if [[ -d "${POPS}" ]]; then
    mapfile -t POPLIST < <(find "${POPS}" -maxdepth 1 -name '*.txt' | sort)
    for ((i=0; i<${#POPLIST[@]}; i++)); do
      for ((j=i+1; j<${#POPLIST[@]}; j++)); do
        A=$(basename "${POPLIST[$i]}" .txt); B=$(basename "${POPLIST[$j]}" .txt)
        vcftools --gzvcf popgen.vcf.gz \
                 --weir-fst-pop "${POPLIST[$i]}" --weir-fst-pop "${POPLIST[$j]}" \
                 --fst-window-size "${WIN}" --fst-window-step "${STEP}" \
                 --out "fst_${A}_${B}"
      done
    done
else
    echo "[WARN] 未找到分群目录 ${POPS}，跳过 F_ST。分群定义是 p04 的交付物之一，别漏。"
fi

# ---- 5) HWE：只算不滤（讲义 §4.3 的误杀警告）----
plink --vcf struct.vcf.gz --allow-extra-chr --double-id --set-missing-var-ids '@:#' \
      --make-bed --out struct
plink --bfile struct --allow-extra-chr --hardy   --out hwe_all
plink --bfile struct --allow-extra-chr --missing --out miss
if [[ -d "${POPS}" ]]; then
    for P in "${POPS}"/*.txt; do
        NAME=$(basename "${P}" .txt)
        awk '{print $1"\t"$1}' "${P}" > "keep_${NAME}.txt"
        plink --bfile struct --allow-extra-chr --keep "keep_${NAME}.txt" --hardy --out "hwe_${NAME}"
    done
fi
echo "[INFO] HWE 偏离方向速览（O(HET) vs E(HET)，判别第一步）："
awk 'NR>1 && $9!="NA" && $9<1e-6 {if($7>$8) ex++; else de++} END{printf "  p<1e-6 位点中：杂合过量 %d，杂合缺失 %d\n", ex+0, de+0}' hwe_all.hwe

cat <<'EOF'
------------------------------------------------------------
下一步（人来做，脚本不替你决定）：
  1) 按讲义 §4.3 的四条动作判断 HWE 偏离是技术性还是生物学性；
     自交 / 克隆群体**不要**开 --hwe 过滤。
  2) 先跑 04_popgen_structure.sh 得到 LD 半衰距离，再回来把 WIN 调到
     半衰距离的 2–5 倍重跑本脚本的第 3、4 步（讲义 §5.4 的循环依赖）。
------------------------------------------------------------
EOF
echo "[INFO] $(date '+%F %T') 完成，输出在 ${OUTDIR}"
