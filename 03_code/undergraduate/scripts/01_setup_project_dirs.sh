#!/bin/bash
# ============================================
# 脚本名称：01_setup_project_dirs.sh
# 功能描述：建立本课程综合项目（u08）的规范目录树，并用软链接接入公共测序数据
#           对应讲义 u01 §⑤ 步骤 1–2；对应项目手册 §3.4、§4.1
# 配套讲义：02_lectures/undergraduate/unit01_linux_conda/01_linux_conda_lecture.md
# 作者：王运生
# 日期：2026-08-29
# ============================================

set -euo pipefail

# ---- 默认参数（可用命令行覆盖，不要在脚本里写死用户名）----
PROJECT_ROOT="/d3/scratch/${USER}/ngs"
DATA_SRC="/data/lab/ngs"
DATA_GLOB="reads*"

usage() {
    cat <<'USAGE'
用法: bash 01_setup_project_dirs.sh [-d 项目根目录] [-s 数据源目录] [-h]

  -d  项目根目录，默认 /d3/scratch/${USER}/ngs
  -s  公共数据源目录，默认 /data/lab/ngs
  -h  显示本帮助

示例:
  bash 01_setup_project_dirs.sh
  bash 01_setup_project_dirs.sh -d ~/ngs_practice -s /data/lab/ngs
USAGE
}

while getopts ":d:s:h" opt; do
    case "${opt}" in
        d) PROJECT_ROOT="${OPTARG}" ;;
        s) DATA_SRC="${OPTARG}" ;;
        h) usage; exit 0 ;;
        \?) echo "未知选项: -${OPTARG}" >&2; usage; exit 1 ;;
        :)  echo "选项 -${OPTARG} 需要参数" >&2; exit 1 ;;
    esac
done

# 项目六个分析模块，与手册 §4.1–§4.6 一一对应
ANALYSIS_DIRS=(survey assem anno ident phylo pangenome)
# 辅助目录：fq 放数据软链接，scripts 放作业脚本，logs 放 SGE 日志，results 放最终产出
SUPPORT_DIRS=(fq scripts logs results/figures results/tables)

make_dirs() {
    echo "[1/3] 创建目录树: ${PROJECT_ROOT}"
    local d
    for d in "${ANALYSIS_DIRS[@]}" "${SUPPORT_DIRS[@]}"; do
        # -p：父目录不存在就顺手建；目录已存在时不报错，脚本可反复执行
        mkdir -p "${PROJECT_ROOT}/${d}"
    done
}

link_data() {
    echo "[2/3] 用软链接接入原始数据（不复制，不占个人配额）"
    if [[ ! -d "${DATA_SRC}" ]]; then
        echo "  跳过：数据源目录不存在 -> ${DATA_SRC}"
        echo "  （本机练习时这是正常的；上集群后请重跑本脚本）"
        return 0
    fi
    local f base linked=0
    # shellcheck disable=SC2231
    for f in ${DATA_SRC}/${DATA_GLOB}; do
        [[ -e "${f}" ]] || continue
        base="$(basename "${f}")"
        if [[ -e "${PROJECT_ROOT}/fq/${base}" ]]; then
            echo "  已存在，跳过: fq/${base}"
        else
            ln -s "${f}" "${PROJECT_ROOT}/fq/${base}"   # -s 建软链接；不要用 cp
            echo "  已链接: fq/${base} -> ${f}"
            linked=$((linked + 1))
        fi
    done
    echo "  本次新建软链接 ${linked} 个"
}

verify() {
    echo "[3/3] 验收"
    echo "--- 目录树 ---"
    ls -1 "${PROJECT_ROOT}"
    echo "--- fq/ 内容（行首为 l 的才是软链接）---"
    ls -lh "${PROJECT_ROOT}/fq" || true
    echo "--- 磁盘剩余空间（经验建议 Use% 保持在约 85% 以下；写满时组装会中途失败）---"
    df -h "${PROJECT_ROOT}" || true
}

main() {
    echo "=== 项目目录初始化开始 ==="
    echo "项目根目录: ${PROJECT_ROOT}"
    echo "数据源目录: ${DATA_SRC}"
    make_dirs
    link_data
    verify
    echo "=== 完成。下一步: bash 01_conda_env_setup.sh ==="
}

main "$@"
