#!/bin/bash
# ============================================
# 脚本名称：01_qsub_hello.sh
# 功能描述：SGE 最小作业脚本 —— 首课"环境就绪检查"的冒烟测试
#           打印计算节点主机名、conda 环境名、关键工具路径与磁盘余量
#           对应讲义 u01 §⑤ 步骤 6
# 提交方式：qsub 01_qsub_hello.sh      （不要用 bash 直接跑，那样是在登录节点跑）
# 查看日志：less qsub_hello.o<作业号>
# 作者：王运生
# 日期：2026-08-29
# ============================================

#$ -S /bin/bash        # 用哪个 shell 解释本脚本
#$ -N qsub_hello       # 作业名：qstat 里显示，日志文件名也用它
#$ -cwd                # 在提交时所在目录里运行（否则默认家目录，相对路径全错）
#$ -j y                # stderr 并进 stdout，只产生一个日志文件
#$ -pe smp 1           # 申请并行环境 smp 的 1 个核

set -uo pipefail       # 冒烟测试要跑完全部检查项，故不用 -e（单项失败不中断）

CONDA_ROOT="/opt/miniconda3"
TARGET_ENV="${1:-ngs_ug_base}"

echo "=========================================="
echo " SGE 作业冒烟测试"
echo "=========================================="
echo "作业号     : ${JOB_ID:-<非 SGE 环境>}"
echo "作业名     : ${JOB_NAME:-<非 SGE 环境>}"
echo "运行节点   : $(hostname)          <-- 这里【不应该】是登录节点名"
echo "运行用户   : ${USER}"
echo "工作目录   : $(pwd)"
echo "开始时间   : $(date '+%F %T')"
echo "分配核数   : ${NSLOTS:-1}"
echo "------------------------------------------"

# 【关键】作业不继承你终端的环境，必须在脚本里重新初始化并激活
if [[ -f "${CONDA_ROOT}/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "${CONDA_ROOT}/bin/activate"
    conda activate "${TARGET_ENV}" 2>/dev/null \
        && echo "conda 环境 : ${CONDA_DEFAULT_ENV}" \
        || echo "conda 环境 : 激活失败 -> ${TARGET_ENV}（先跑 01_conda_env_setup.sh）"
else
    echo "conda 环境 : 找不到 ${CONDA_ROOT}/bin/activate，请与教师确认 conda 安装路径"
fi

echo "------------------------------------------"
echo "关键工具可用性（FAIL 说明环境没激活或拿错了环境）:"
for tool in samtools fastqc R jellyfish flye prokka; do
    path="$(command -v "${tool}" 2>/dev/null)"
    if [[ -n "${path}" ]]; then
        echo "  OK   ${tool} -> ${path}"
    else
        echo "  ---  ${tool} 不在当前环境（若本单元用不到它，属正常）"
    fi
done

echo "------------------------------------------"
echo "磁盘余量（经验建议 Use% 保持在约 85% 以下；写满时大文件写入会中途失败）:"
df -h "/d3/scratch/${USER}" 2>/dev/null || df -h "${HOME}"

echo "------------------------------------------"
echo "结束时间   : $(date '+%F %T')"
echo "日志末尾出现这一行，说明作业【完整跑完】，没有被中途 kill。"
