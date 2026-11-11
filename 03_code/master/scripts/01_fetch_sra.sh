#!/bin/bash
#$ -S /bin/bash
#$ -N fetch_sra
#$ -cwd
#$ -j y
#$ -pe smp 4
# ============================================================
# m01 高通量测序原理与实验设计 —— 公共数据检索与下载
# 作者：王运生 ｜ 课程：高通量测序技术与数据分析（硕士）
# 环境：conda activate ngs_ms_base
#
# 用途：从 SRA/ENA 拉取一批 run，并生成可核对的元数据表。
#      实验设计课要求学生能复现别人的数据来源——这一步就是起点。
# ============================================================
set -euo pipefail

# 非交互 shell 里 conda 未初始化，必须显式 source
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_ms_base

ACC_LIST="${1:?用法: $0 <accession_list.txt> [outdir]}"   # 每行一个 SRR/ERR/DRR
OUTDIR="${2:-./sra_data}"
THREADS="${NSLOTS:-4}"

mkdir -p "${OUTDIR}"/{fastq,meta}

# ---- 1) 拉取元数据（先看清楚再下载，避免下错几十 GB）----
echo "[1/3] 获取元数据 ..."
while read -r acc; do
    [[ -z "${acc}" || "${acc}" == \#* ]] && continue
    curl -sS "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=${acc}&result=read_run&fields=run_accession,sample_alias,library_layout,library_strategy,instrument_platform,read_count,base_count,fastq_ftp&format=tsv" \
        >> "${OUTDIR}/meta/ena_report.tsv"
done < "${ACC_LIST}"
# 去掉重复表头
awk 'NR==1 || $0 !~ /^run_accession/' "${OUTDIR}/meta/ena_report.tsv" > "${OUTDIR}/meta/ena_report.clean.tsv"

echo "  平台与文库类型分布："
awk -F'\t' 'NR>1 {print $5, $4, $3}' "${OUTDIR}/meta/ena_report.clean.tsv" | sort | uniq -c

# ---- 2) 下载 ----
echo "[2/3] 下载 FASTQ ..."
awk -F'\t' 'NR>1 {print $8}' "${OUTDIR}/meta/ena_report.clean.tsv" \
  | tr ';' '\n' | grep -v '^$' \
  | while read -r url; do
        f="${OUTDIR}/fastq/$(basename "${url}")"
        [[ -s "${f}" ]] && { echo "  已存在，跳过 $(basename "${f}")"; continue; }
        curl -sS -L -o "${f}" "ftp://${url#ftp://}"
    done

# ---- 3) 核对：实际条数与元数据声明是否一致 ----
echo "[3/3] 核对 read 数 ..."
for f in "${OUTDIR}"/fastq/*_1.fastq.gz "${OUTDIR}"/fastq/*.fastq.gz; do
    [[ -e "${f}" ]] || continue
    n=$(( $(zcat "${f}" | wc -l) / 4 ))
    printf "%-40s %12d reads\n" "$(basename "${f}")" "${n}"
done | sort -u | tee "${OUTDIR}/meta/actual_read_counts.txt"

echo "完成。元数据在 ${OUTDIR}/meta/，下载文件在 ${OUTDIR}/fastq/"
echo "提示：把 ena_report.clean.tsv 附进你的实验设计文档——数据来源必须可追溯。"
