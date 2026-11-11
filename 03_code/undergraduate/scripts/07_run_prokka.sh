#!/bin/bash
#$ -S /bin/bash
#$ -N prokka
#$ -cwd
#$ -j y
#$ -pe smp 4
# ============================================
# 脚本名称：07_run_prokka.sh
# 功能描述：用 Prokka 对 u06 的组装结果做原核基因组注释（单元 u07 / 项目手册 §4.3）
#           产出 .gff（Roary 泛基因组的唯一输入）与 .faa（系统进化分析的蛋白来源）
# 运行方式：qsub 07_run_prokka.sh [genome.fasta] [prefix] [outdir]
# 集群环境：10.7.254.22，SGE 调度，禁止在登录节点直接运行
# 作者：王运生
# 日期：2026-08-29
# ============================================

set -euo pipefail

# ---- 参数（可用位置参数覆盖默认值）----
GENOME="${1:-genome.fasta}"      # 输入：u06 的组装结果
# u06 产物路径：/d3/scratch/$USER/ngs/assem/canu/test-pacbio/test.contigs.fasta（Canu）
#   或 .../flye/out_pacbio/assembly.fasta（Flye）。"test" 是 u06 起的前缀，不是测试数据；
#   用你在 u06 评估后选定的那一个（UP-033）
PREFIX="${2:-mygenome}"          # 输出文件统一前缀
OUTDIR="${3:-prokka_out}"        # 输出目录，必须不存在
KINGDOM="Bacteria"               # 遗传密码表与功能数据库（细菌）
LOCUSTAG="MYGENOME"              # 基因 ID 前缀 → MYGENOME_00001
THREADS="${NSLOTS:-4}"           # SGE 分配的核数，未设置时退回 4
CONDA_ROOT="/opt/miniconda3"
CONDA_ENV="ngs_ug_annot"

main() {
    # 非交互式 shell 不读 ~/.bashrc，必须先 source 再 activate
    # shellcheck disable=SC1091
    source "${CONDA_ROOT}/bin/activate"
    conda activate "${CONDA_ENV}"

    if [[ ! -s "${GENOME}" ]]; then
        echo "[ERROR] 输入基因组不存在或为空：${GENOME}" >&2
        echo "        请确认 u06 的组装结果路径，或用 ln -sf 建好软链接" >&2
        exit 1
    fi
    if [[ -d "${OUTDIR}" ]]; then
        echo "[ERROR] 输出目录已存在：${OUTDIR}（Prokka 拒绝覆盖）" >&2
        echo "        换一个 --outdir，或确认旧结果不要了再手动加 --force" >&2
        exit 1
    fi

    # contig 名长度预检：Prokka 上限 37 字符，超长会中途报错
    local max_len
    max_len=$(grep "^>" "${GENOME}" | sed 's/^>//' | awk '{print $1}' \
              | awk '{print length($0)}' | sort -rn | head -1)
    echo "[INFO] 最长 contig 名长度：${max_len}"
    if (( max_len > 37 )); then
        echo "[WARN] contig 名超过 37 字符，自动追加 --compliant --centre XXX" >&2
        EXTRA="--compliant --centre XXX"
    else
        EXTRA=""
    fi

    echo "[INFO] 开始注释：${GENOME} → ${OUTDIR}/${PREFIX}.*（${THREADS} 线程）"
    # shellcheck disable=SC2086
    prokka --outdir "${OUTDIR}" --prefix "${PREFIX}" --kingdom "${KINGDOM}" \
           --locustag "${LOCUSTAG}" --cpus "${THREADS}" ${EXTRA} "${GENOME}"

    # 记录版本：Prokka 的数据库随 conda 包安装，版本即包版本；--listdb 列出实际可用库（UP-037）
    { echo -e "date\t$(date +%F)"; echo -e "prokka\t$(prokka --version 2>&1)"; prokka --listdb 2>&1; } \
        > "${OUTDIR}/software_versions.txt" || true

    echo "[INFO] 完成。关键产物："
    echo "  ${OUTDIR}/${PREFIX}.gff  → Roary 泛基因组分析（项目 §4.6）的唯一输入"
    echo "  ${OUTDIR}/${PREFIX}.faa  → 系统进化分析（项目 §4.5）的蛋白来源"
    echo "  ${OUTDIR}/${PREFIX}.gbk  → antiSMASH 的理想输入"
    echo "  ${OUTDIR}/${PREFIX}.txt  → 统计摘要，先看它做第一眼质检"
    cat "${OUTDIR}/${PREFIX}.txt"
}

main "$@"
