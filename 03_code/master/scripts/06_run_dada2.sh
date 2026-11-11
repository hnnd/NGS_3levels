#!/bin/bash
#$ -S /bin/bash
#$ -N dada2
#$ -cwd
#$ -j y
#$ -pe smp 8
# ============================================================
# m06 扩增子测序分析 —— DADA2 流程的集群封装
# 环境：conda activate ngs_ms_microbiome
#
# 注意：QIIME2 官方要求独立环境（见契约 env_exempt_tools），
#      不在本环境中。本课主路径走 R 侧 DADA2 + phyloseq + vegan。
# ============================================================
set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_ms_microbiome

FQDIR="${FQDIR:?必须指定 FQDIR=双端 fastq 目录}"
OUTDIR="${OUTDIR:-./amplicon}"
TRUNC_F="${TRUNC_F:-240}"    # 由 FastQC 质量曲线决定，不要照抄
TRUNC_R="${TRUNC_R:-200}"
DB="${DB:?必须指定 DB=SILVA/UNITE 训练集 fasta.gz}"
THREADS="${NSLOTS:-8}"
export TRIM_F="${TRIM_F:-0}"      # 引物长度；V4 515F/806R=19/20，V3–V4 341F/805R=17/21；已去引物写 0
export TRIM_R="${TRIM_R:-0}"
export BATCH_COL="${BATCH_COL:-batch}"   # metadata.tsv 的测序批次列：错误模型按批次分别学
export MINBOOT="${MINBOOT:-80}"

mkdir -p "${OUTDIR}"
echo "[提示] truncLen 必须由本批数据的质量曲线决定。"
echo "       截太短：双端拼不上（overlap 不足 12 bp）；截太长：低质量碱基毁掉错误模型。"
echo "       当前 F=${TRUNC_F} R=${TRUNC_R}、trimLeft F=${TRIM_F} R=${TRIM_R}——请确认你看过 FastQC 再跑。"
echo "       跑完先看 \${OUTDIR}/track.csv：merged 骤减 = 双端重叠不足，流程不会报错。"

Rscript "$(dirname "$0")/06_dada2_pipeline.R" \
    "${FQDIR}" "${OUTDIR}" "${TRUNC_F}" "${TRUNC_R}" "${DB}" "${THREADS}"
