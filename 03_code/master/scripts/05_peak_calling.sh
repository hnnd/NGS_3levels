#!/bin/bash
#$ -S /bin/bash
#$ -N m05_peakcall
#$ -cwd
#$ -j y
#$ -pe smp 16
# ============================================
# 脚本名称：05_peak_calling.sh
# 功能描述：硕士 m05 转录调控与表观组 —— 上游主流程
#           Bowtie2 比对 → 去重/MAPQ/去线粒体清洗 → MACS2 peak calling
#           （narrow / broad / ATAC 三套参数）→ FRiP → deepTools bigwig
# 课程专题：m05（02_lectures/master/topic05_regulome/05_regulome_lecture.md ⑤ 步骤 1-3）
# 运行环境：ngs_ms_transcriptome（07_envs/conda/env_master_transcriptome.yml）
# 集群提交：qsub 05_peak_calling.sh   （SGE，10.7.254.22）
# 作者：王运生
# 日期：2026-08-29
# ============================================

set -euo pipefail

# --------------------------------------------
# 0. 环境激活
#    SGE 作业不继承你终端的 conda 状态，也不是交互式 shell，
#    conda 的 shell 钩子没有初始化 —— 必须显式 source activate。
#    （l0_01_linux §5「作业不继承环境变量与 conda 激活状态」）
# --------------------------------------------
CONDA_ROOT="${CONDA_ROOT:-/opt/miniconda3}"
# shellcheck disable=SC1091
source "${CONDA_ROOT}/bin/activate" ngs_ms_transcriptome

# --------------------------------------------
# 1. 参数（全部可用环境变量覆盖，不写死任何路径）
#    用法示例：
#      SAMPLE=TF_rep1 MODE=narrow CTRL_BAM=align/input.bam qsub 05_peak_calling.sh
# --------------------------------------------
PROJ_DIR="${PROJ_DIR:-/d3/scratch/${USER}/m05_regulome}"
FQ_DIR="${FQ_DIR:-${PROJ_DIR}/clean}"          # 已过 fastp 的 clean reads（l0_05_qc）
REF_DIR="${REF_DIR:-${PROJ_DIR}/ref}"
GENOME_FA="${GENOME_FA:-${REF_DIR}/genome.fa}"  # 需已有 .fai
BT2_IDX="${BT2_IDX:-${REF_DIR}/genome_idx}"     # bowtie2-build 生成的索引前缀
BLACKLIST="${BLACKLIST:-}"                      # 可选：blacklist BED，留空则跳过

SAMPLE="${SAMPLE:?请设置 SAMPLE，例如 SAMPLE=TF_rep1}"
R1="${R1:-${FQ_DIR}/${SAMPLE}_R1.clean.fq.gz}"
R2="${R2:-${FQ_DIR}/${SAMPLE}_R2.clean.fq.gz}"

# MODE 决定用哪一套 MACS2 参数：narrow（TF/CUT&Tag）| broad（组蛋白）| atac
MODE="${MODE:-narrow}"
CTRL_BAM="${CTRL_BAM:-}"                        # input / IgG 的 clean.bam；ATAC 留空

# 有效基因组大小：可唯一比对的碱基数，≈0.8-0.9 × 基因组总长（重复多取下限）。
# MACS2 与 deepTools 两处必须是同一个数，否则归一化与显著性不在同一尺度。
# 水稻 IRGSP-1.0（GCA_001433935）总长 373,795,655 bp → 0.8× ≈ 3.0e8。
# 注意：旧默认 1.2e8 是 MACS2 内置的果蝇（dm）值，会改变全局 λBG 与 peak 数（UP-050）。
GSIZE="${GSIZE:-3.0e8}"                         # MACS2 -g，接受科学计数
EGS="${EGS:-300000000}"                         # deepTools --effectiveGenomeSize，须整数
if ! awk -v a="${GSIZE}" -v b="${EGS}" 'BEGIN{exit !((a+0)==(b+0))}'; then
    echo "错误：GSIZE(${GSIZE}) 与 EGS(${EGS}) 不是同一个数，MACS2 与 deepTools 会不在同一尺度" >&2
    exit 1
fi
MT_PATTERN="${MT_PATTERN:-^(chrM|MT|Mt|mitochondrion)$}"
THREADS="${THREADS:-${NSLOTS:-16}}"             # SGE 用 -pe smp 申请的核数

ALIGN_DIR="${PROJ_DIR}/align"
PEAK_DIR="${PROJ_DIR}/peaks"
BW_DIR="${PROJ_DIR}/bigwig"
QC_DIR="${PROJ_DIR}/qc"
LOG_DIR="${PROJ_DIR}/logs"
mkdir -p "${ALIGN_DIR}" "${PEAK_DIR}" "${BW_DIR}" "${QC_DIR}" "${LOG_DIR}"

echo "运行节点 : $(hostname)"        # 好习惯：日志第一行确认不是登录节点
echo "开始时间 : $(date)"
echo "样本/模式: ${SAMPLE} / ${MODE}"

# --------------------------------------------
# 2. Bowtie2 比对
#    --very-sensitive 提灵敏度；-X 2000 允许长片段（ATAC 的多核小体片段需要）
# --------------------------------------------
RAW_BAM="${ALIGN_DIR}/${SAMPLE}.raw.bam"
bowtie2 -p "${THREADS}" -x "${BT2_IDX}" --very-sensitive -X 2000 \
    -1 "${R1}" -2 "${R2}" 2> "${LOG_DIR}/${SAMPLE}.bowtie2.log" \
  | samtools sort -@ 4 -o "${RAW_BAM}" -
samtools index "${RAW_BAM}"

# --------------------------------------------
# 3. 去 PCR 重复
#    env 里没有 picard，用 samtools markdup（与 picard MarkDuplicates 等价）。
#    markdup 依赖 fixmate -m 写入的 MC/ms 标签，且要求先按 name 排序。
# --------------------------------------------
DEDUP_BAM="${ALIGN_DIR}/${SAMPLE}.dedup.bam"
samtools sort -n -@ "${THREADS}" "${RAW_BAM}" \
  | samtools fixmate -m -@ 4 - - \
  | samtools sort -@ "${THREADS}" - \
  | samtools markdup -r -s -@ 4 - "${DEDUP_BAM}" 2> "${QC_DIR}/${SAMPLE}.markdup.txt"
samtools index "${DEDUP_BAM}"

# --------------------------------------------
# 4. 清洗：MAPQ≥30 去多重比对 + -F 1804 + 只留核基因组染色体
#    1804 = 未比对(4) + 配对未比对(8) + 次要比对(256) + QC失败(512) + 重复(1024)
# --------------------------------------------
# 课程参考 IRGSP-1.0 只有 12 条核染色体、不含 chrM/chrCp：此时细胞器读段在比对阶段就是
# unmapped，下面的过滤是空操作，「线粒体比例」也无法从 BAM 计算（UP-051）。显式提示，避免误读。
if ! cut -f1 "${GENOME_FA}.fai" | grep -q -E "${MT_PATTERN}"; then
    echo "【提示】参考中没有匹配 MT_PATTERN 的细胞器序列：细胞器读段已以 unmapped 形式消失，"
    echo "        线粒体比例不可由本流程计算，样本质量请看 FRiP 与 TSS 富集。"
fi
# shellcheck disable=SC2207
CHRS=($(cut -f1 "${GENOME_FA}.fai" | grep -v -E "${MT_PATTERN}" || true))
CLEAN_BAM="${ALIGN_DIR}/${SAMPLE}.clean.bam"
samtools view -b -q 30 -F 1804 "${DEDUP_BAM}" "${CHRS[@]}" > "${CLEAN_BAM}"

if [[ -n "${BLACKLIST}" && -s "${BLACKLIST}" ]]; then
    bedtools intersect -v -abam "${CLEAN_BAM}" -b "${BLACKLIST}" \
        > "${ALIGN_DIR}/${SAMPLE}.clean.bl.bam"
    mv "${ALIGN_DIR}/${SAMPLE}.clean.bl.bam" "${CLEAN_BAM}"
fi
samtools index "${CLEAN_BAM}"

# 线粒体比例（ATAC 的关键 QC，>60% 说明名义深度严重虚高）
samtools idxstats "${RAW_BAM}" > "${QC_DIR}/${SAMPLE}.idxstats.txt"
# ATAC 片段长度分布：应见 <100 / ~200 / ~400 bp 的核小体阶梯
samtools view -f 66 "${CLEAN_BAM}" \
  | awk '$9>0 && $9<1000 {print $9}' > "${QC_DIR}/${SAMPLE}.fraglen.txt"

# --------------------------------------------
# 5. MACS2 peak calling —— 三套参数按 MODE 分派
#    三条命令的差别不是风格问题，是三种数据的物理性质不同。
# --------------------------------------------
CTRL_OPT=()
if [[ -n "${CTRL_BAM}" ]]; then
    CTRL_OPT=(-c "${CTRL_BAM}")
else
    echo "【警告】未提供 CTRL_BAM。ChIP/CUT&Tag 缺 input/IgG 会让局部 λ 只能从处理样本自估，"
    echo "        产生大量假阳性 peak 且不报任何错（讲义 ⑨ 错误 2）。ATAC 无对照属正常。"
fi

case "${MODE}" in
  narrow)   # TF ChIP / CUT&Tag —— narrow，带对照
    macs2 callpeak -t "${CLEAN_BAM}" "${CTRL_OPT[@]}" -f BAMPE -g "${GSIZE}" \
        -n "${SAMPLE}" --outdir "${PEAK_DIR}" -q 0.05 \
        2> "${LOG_DIR}/${SAMPLE}.macs2.log"
    PEAK_FILE="${PEAK_DIR}/${SAMPLE}_peaks.narrowPeak"
    ;;
  broad)    # 组蛋白 broad mark（H3K27me3 / H3K9me3 / H3K36me3）
            # --broad-cutoff 0.1 比主阈值宽松是刻意的：连接用的阈值应更宽松
    macs2 callpeak -t "${CLEAN_BAM}" "${CTRL_OPT[@]}" -f BAMPE -g "${GSIZE}" \
        -n "${SAMPLE}" --outdir "${PEAK_DIR}" --broad --broad-cutoff 0.1 \
        2> "${LOG_DIR}/${SAMPLE}.macs2.log"
    PEAK_FILE="${PEAK_DIR}/${SAMPLE}_peaks.broadPeak"   # 注意：broadPeak 只有 9 列，无 summit
    ;;
  atac)     # ATAC —— 无对照，双端
            # -f BAMPE 用读段对的实际两端界定片段：MACS2 在 BAMPE 下强制 nomodel、
            # 把 shift 清零、extsize 不参与 pileup（OptValidator / PeakDetect 源码，UP-051），
            # 所以双端数据不需要也无法用 --shift/--extsize 做 Tn5 校正；那是单端（-f BAM）口径。
            # --keep-dup all 避免在已去重后 MACS2 再按坐标删一次真实读段。
    macs2 callpeak -t "${CLEAN_BAM}" -f BAMPE -g "${GSIZE}" \
        -n "${SAMPLE}" --outdir "${PEAK_DIR}" -q 0.05 \
        --keep-dup all \
        2> "${LOG_DIR}/${SAMPLE}.macs2.log"
    PEAK_FILE="${PEAK_DIR}/${SAMPLE}_peaks.narrowPeak"
    ;;
  *)
    echo "错误：MODE 只能是 narrow / broad / atac，当前为 '${MODE}'" >&2
    exit 1
    ;;
esac

# --------------------------------------------
# 6. FRiP（每个样本都要报告；TF ChIP >1%，ATAC >20%）
# --------------------------------------------
TOTAL=$(samtools view -c "${CLEAN_BAM}")
INPEAK=$(bedtools intersect -a "${CLEAN_BAM}" -b "${PEAK_FILE}" -u | samtools view -c)
FRIP=$(echo "scale=4; ${INPEAK}/${TOTAL}" | bc)
NPEAK=$(wc -l < "${PEAK_FILE}")
printf '%s\t%s\t%s\t%s\t%s\n' "${SAMPLE}" "${MODE}" "${TOTAL}" "${NPEAK}" "${FRIP}" \
    >> "${QC_DIR}/frip_summary.tsv"
echo "FRiP(${SAMPLE}) = ${FRIP} ；peak 数 = ${NPEAK}"
echo "【提醒】peak 数受深度/复杂度/IP效率/阈值共同驱动且远未饱和，"
echo "        深度不同的样本之间不要直接比 peak 数（讲义 ⑦ 第 3 条）。"

# --------------------------------------------
# 7. deepTools：RPGC 归一化 bigwig（1x 基因组覆盖度，跨样本可比）
# --------------------------------------------
bamCoverage -b "${CLEAN_BAM}" -o "${BW_DIR}/${SAMPLE}.bw" \
    --binSize 10 --normalizeUsing RPGC --effectiveGenomeSize "${EGS}" \
    --extendReads -p "${THREADS}"

echo "结束时间 : $(date)"
echo "产出：${PEAK_FILE} ｜ ${BW_DIR}/${SAMPLE}.bw ｜ ${QC_DIR}/frip_summary.tsv"
echo "下一步：computeMatrix/plotHeatmap（TSS 富集）、multiBigwigSummary/plotCorrelation（重复相关）、"
echo "        idr（重复一致性），随后 05_peak_annotation.R 做注释与联合解读。"
