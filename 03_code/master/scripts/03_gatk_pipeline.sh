#!/bin/bash
#$ -S /bin/bash
#$ -N gatk_pipeline
#$ -cwd
#$ -j y
#$ -pe smp 16
#$ -l h_vmem=8G
# ============================================================
# m03 重测序与变异检测 —— GATK Best Practices 单样本流程
# 环境：conda activate ngs_ms_variant
#
# 输入：清洗后的双端 FASTQ + 参考基因组 FASTA
# 输出：分析就绪 BAM + 原始 VCF
# 注意：BQSR 需要已知变异位点集（known-sites）。非模式物种通常没有，
#      此时的通行做法是"自举"：先硬过滤一轮高置信变异当作 known-sites。
#      本脚本用 SKIP_BQSR=1 跳过该步，并在日志里说明。
# ============================================================
set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_ms_variant

SAMPLE="${SAMPLE:?必须指定 SAMPLE=样本名}"
R1="${R1:?必须指定 R1=前端 fastq}"
R2="${R2:?必须指定 R2=后端 fastq}"
REF="${REF:?必须指定 REF=参考基因组 fasta}"
OUTDIR="${OUTDIR:-./variant/${SAMPLE}}"
THREADS="${NSLOTS:-16}"
SKIP_BQSR="${SKIP_BQSR:-1}"
KNOWN_SITES="${KNOWN_SITES:-}"
# 倍性 = 每个细胞中该染色体的拷贝数，不是纯合程度。主线 Xoo 是单倍体细菌 → 1；
# 自交纯系二倍体植物仍是 2。GATK HaplotypeCaller 默认 2，不传就会按二倍体分型（UP-038）。
PLOIDY="${PLOIDY:-1}"

mkdir -p "${OUTDIR}"

# ---- 0) 参考基因组索引（缺一不可，GATK 三种索引都要）----
[[ -e "${REF}.bwt" ]]                 || bwa index "${REF}"
[[ -e "${REF}.fai" ]]                 || samtools faidx "${REF}"
[[ -e "${REF%.*}.dict" ]]             || gatk CreateSequenceDictionary -R "${REF}"

# ---- 1) 比对。-M 把 short split hit 标为 secondary，以兼容 Picard/GATK ----
# @RG 三字段缺一 GATK 就报错，这是最高频的坑
bwa mem -t "${THREADS}" -M \
    -R "@RG\tID:${SAMPLE}\tSM:${SAMPLE}\tPL:ILLUMINA\tLB:lib1" \
    "${REF}" "${R1}" "${R2}" \
  | samtools sort -@ 4 -o "${OUTDIR}/${SAMPLE}.sorted.bam" -
samtools index "${OUTDIR}/${SAMPLE}.sorted.bam"

# ---- 2) 标记重复 ----
gatk MarkDuplicates \
    -I "${OUTDIR}/${SAMPLE}.sorted.bam" \
    -O "${OUTDIR}/${SAMPLE}.dedup.bam" \
    -M "${OUTDIR}/${SAMPLE}.dup_metrics.txt"
samtools index "${OUTDIR}/${SAMPLE}.dedup.bam"

# ---- 3) BQSR（可选）----
BAM_FOR_CALL="${OUTDIR}/${SAMPLE}.dedup.bam"
if [[ "${SKIP_BQSR}" == "0" && -n "${KNOWN_SITES}" ]]; then
    gatk BaseRecalibrator -R "${REF}" -I "${BAM_FOR_CALL}" \
        --known-sites "${KNOWN_SITES}" -O "${OUTDIR}/${SAMPLE}.recal.table"
    gatk ApplyBQSR -R "${REF}" -I "${BAM_FOR_CALL}" \
        --bqsr-recal-file "${OUTDIR}/${SAMPLE}.recal.table" \
        -O "${OUTDIR}/${SAMPLE}.bqsr.bam"
    BAM_FOR_CALL="${OUTDIR}/${SAMPLE}.bqsr.bam"
else
    echo "[提示] 跳过 BQSR：未提供独立可信的 known-sites（本课 Xoo 即如此）。"
    echo "       请在方法中写明跳过及理由；自举 known-sites 存在循环依赖，不作为默认做法。"
fi

# ---- 4) 变异检出（GVCF 模式，便于后续多样本联合分型）----
gatk HaplotypeCaller -R "${REF}" -I "${BAM_FOR_CALL}" \
    -O "${OUTDIR}/${SAMPLE}.g.vcf.gz" -ERC GVCF \
    -ploidy "${PLOIDY}" \
    --native-pair-hmm-threads "${THREADS}"

# ---- 5) 比对与深度统计（报告要用）----
samtools flagstat "${BAM_FOR_CALL}" > "${OUTDIR}/${SAMPLE}.flagstat.txt"
samtools coverage "${BAM_FOR_CALL}" > "${OUTDIR}/${SAMPLE}.coverage.txt"
echo "完成。产出在 ${OUTDIR}/"
