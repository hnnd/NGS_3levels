#!/bin/bash
#$ -S /bin/bash
#$ -N p01_ai_practice
#$ -cwd
#$ -j y
#$ -pe smp 4
#$ -l h_vmem=8G
# ============================================================
# 脚本名称：01_run_ai_practice.sh
# 功能描述：p01「AI 辅助的生信工作流」实践一键跑通 ——
#           生成已知答案数据 → 跑"AI 生成"的脚本 → 执行三步验证法。
#           作业不继承登录终端环境，故必须显式 source activate（机理见 l0_01_linux，
#           写法见 l0_03_conda 自测 L0-3-Q10）。
# 环境    ：ngs_phd_base
# 作者    ：王运生
# 日期    ：2026-08-29
#
# 用法：qsub 01_run_ai_practice.sh          # 集群
#       bash 01_run_ai_practice.sh          # 本地（数据小，本地也跑得动）
# ============================================================
set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_base

echo "[host] $(hostname)"            # 提交成功时这里不应是登录节点
echo "[time] $(date '+%F %T')"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTDIR="${OUTDIR:-results/p01}"
AIOUT="${OUTDIR}/ai_out"
mkdir -p "${AIOUT}"

echo "=== [1/3] 生成已知答案数据 ==="
Rscript "${SCRIPT_DIR}/01_make_spikein_counts.R" "${OUTDIR}"

echo "=== [2/3] 运行 AI 生成的差异表达脚本（含教师植入错误） ==="
Rscript "${SCRIPT_DIR}/01_ai_generated_de.R" \
        "${OUTDIR}/counts.tsv" "${OUTDIR}/coldata.tsv" "${AIOUT}"

echo "=== [3/3] 三步验证法 ==="
Rscript "${SCRIPT_DIR}/01_verify_de.R" "${OUTDIR}" "${AIOUT}"

echo "----------------------------------------------"
echo "请先读 ${AIOUT}/verify_report.txt 并写下你的判断，再回讲义 §6.2 对指纹。"
echo "文献核查另跑： bash ${SCRIPT_DIR}/01_check_refs.sh refs.txt"
echo "[done] $(date '+%F %T')"
