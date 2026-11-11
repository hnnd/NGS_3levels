#!/bin/bash
#$ -S /bin/bash
#$ -N rnaseq_quant
#$ -cwd
#$ -j y
#$ -pe smp 16
# ============================================================
# m04 转录组分析 —— 定量（Salmon 选择性比对 / STAR 基因组比对二选一）
# 环境：conda activate ngs_ms_transcriptome
#
# MODE=salmon  轻量、快、直接出转录本级 TPM 与 counts（推荐做差异表达）
# MODE=star    需要基因组比对产物时用（如 m05 调控组要联合看覆盖度）
# ============================================================
set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_ms_transcriptome

SAMPLES="${SAMPLES:?必须指定 SAMPLES=samples.tsv（列：sample R1 R2）}"
MODE="${MODE:-salmon}"
IDX="${IDX:?必须指定 IDX=索引目录}"
GTF="${GTF:-}"
OUTDIR="${OUTDIR:-./rnaseq}"
THREADS="${NSLOTS:-16}"
mkdir -p "${OUTDIR}"

while IFS=$'\t' read -r sample r1 r2; do
    [[ -z "${sample}" || "${sample}" == \#* || "${sample}" == "sample" ]] && continue
    echo "=== ${sample} (${MODE}) ==="
    case "${MODE}" in
      salmon)
        # --validateMappings 是 selective alignment，显著降低假阳性定量
        # --gcBias 校正 GC 偏好；样本量小时尤其值得开
        salmon quant -i "${IDX}" -l A -1 "${r1}" -2 "${r2}" \
            -p "${THREADS}" --validateMappings --gcBias \
            -o "${OUTDIR}/${sample}"
        ;;
      star)
        [[ -n "${GTF}" ]] || { echo "STAR 模式需要 GTF=注释文件"; exit 2; }
        STAR --genomeDir "${IDX}" --readFilesIn "${r1}" "${r2}" \
             --readFilesCommand zcat --runThreadN "${THREADS}" \
             --outSAMtype BAM SortedByCoordinate \
             --quantMode GeneCounts \
             --outFileNamePrefix "${OUTDIR}/${sample}."
        samtools index "${OUTDIR}/${sample}.Aligned.sortedByCoord.out.bam"
        ;;
      *) echo "MODE 只能是 salmon 或 star"; exit 2;;
    esac
done < "${SAMPLES}"

# ---- 定量质量核对：比对率过低说明索引物种错、rRNA 未去、或污染 ----
if [[ "${MODE}" == "salmon" ]]; then
    echo -e "\nsample\tmapping_rate"
    for d in "${OUTDIR}"/*/; do
        s=$(basename "${d}")
        rate=$(grep -o '"percent_mapped": *[0-9.]*' "${d}/aux_info/meta_info.json" 2>/dev/null | awk '{print $2}')
        printf "%s\t%s\n" "${s}" "${rate:-NA}"
    done | tee "${OUTDIR}/mapping_rates.tsv"
    echo "提示：真核转录组 selective alignment 通常 >70%。明显偏低先查物种与 rRNA。"
fi
