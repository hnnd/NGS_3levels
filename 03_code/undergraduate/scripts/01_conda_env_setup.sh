#!/bin/bash
# ============================================
# 脚本名称：01_conda_env_setup.sh
# 功能描述：创建本科层 4 个 conda 环境并做工具可用性冒烟测试
#           对应讲义 u01 §⑤ 步骤 5；环境定义见 07_envs/conda/
# 配套讲义：02_lectures/undergraduate/unit01_linux_conda/01_linux_conda_lecture.md
# 作者：王运生
# 日期：2026-08-29
# ============================================

set -euo pipefail

CONDA_ROOT="/opt/miniconda3"
ENV_DIR="07_envs/conda"
USE_MAMBA="auto"          # auto | yes | no

usage() {
    cat <<'USAGE'
用法: bash 01_conda_env_setup.sh [-c conda根目录] [-e 环境yml目录] [-m auto|yes|no] [环境别名...]

  环境别名: base / assembly / annotation / phylo（不给则建全部 4 个）
  -c  conda 安装根目录，默认 /opt/miniconda3
  -e  环境 yml 所在目录，默认 07_envs/conda（相对仓库根目录）
  -m  是否用 mamba 加速：auto（有就用，默认）/ yes / no

示例:
  bash 01_conda_env_setup.sh                 # 建全部 4 个
  bash 01_conda_env_setup.sh base assembly   # 只建这两个
USAGE
}

while getopts ":c:e:m:h" opt; do
    case "${opt}" in
        c) CONDA_ROOT="${OPTARG}" ;;
        e) ENV_DIR="${OPTARG}" ;;
        m) USE_MAMBA="${OPTARG}" ;;
        h) usage; exit 0 ;;
        \?) echo "未知选项: -${OPTARG}" >&2; usage; exit 1 ;;
        :)  echo "选项 -${OPTARG} 需要参数" >&2; exit 1 ;;
    esac
done
shift $((OPTIND - 1))

# 别名 -> "yml 文件名:环境名:冒烟测试命令"
# 注意：注释环境的 yml 文件名是 env_ug_annotation.yml，而环境名是 ngs_ug_annot（两者不一致）
declare -A ENV_SPEC=(
    [base]="env_ug_base.yml:ngs_ug_base:samtools fastqc R"
    [assembly]="env_ug_assembly.yml:ngs_ug_assembly:flye quast.py jellyfish"
    [annotation]="env_ug_annotation.yml:ngs_ug_annot:prokka"
    [phylo]="env_ug_phylo.yml:ngs_ug_phylo:iqtree mash roary"
)
DEFAULT_ORDER=(base assembly annotation phylo)

init_conda() {
    if ! command -v conda >/dev/null 2>&1; then
        echo "[init] conda 未初始化，source ${CONDA_ROOT}/bin/activate"
        # shellcheck disable=SC1091
        source "${CONDA_ROOT}/bin/activate"
    fi
    conda --version
    # channel 优先级：--add 是插到最前面，所以倒着加，最终顺序 conda-forge > bioconda > defaults
    conda config --add channels defaults    >/dev/null 2>&1 || true
    conda config --add channels bioconda    >/dev/null 2>&1 || true
    conda config --add channels conda-forge >/dev/null 2>&1 || true
    conda config --set channel_priority strict >/dev/null 2>&1 || true
    echo "[init] 当前 channel 顺序："
    conda config --show channels
}

solver_cmd() {
    case "${USE_MAMBA}" in
        yes) echo "mamba" ;;
        no)  echo "conda" ;;
        *)   command -v mamba >/dev/null 2>&1 && echo "mamba" || echo "conda" ;;
    esac
}

create_env() {
    local alias_name="$1" spec yml env_name tools solver
    spec="${ENV_SPEC[${alias_name}]:-}"
    if [[ -z "${spec}" ]]; then
        echo "  未知环境别名: ${alias_name}（可选：${DEFAULT_ORDER[*]}）" >&2
        return 1
    fi
    IFS=':' read -r yml env_name tools <<< "${spec}"
    solver="$(solver_cmd)"

    if conda env list | awk '{print $1}' | grep -qx "${env_name}"; then
        echo "  环境已存在，跳过创建: ${env_name}"
    else
        echo "  用 ${solver} 创建 ${env_name}（solve 慢是正常的；长时间无进展见讲义 ⑨ 9.3）"
        "${solver}" env create -f "${ENV_DIR}/${yml}"
    fi
    smoke_test "${env_name}" "${tools}"
}

smoke_test() {
    local env_name="$1" tools="$2" t missing=0
    echo "  冒烟测试 ${env_name}:"
    # 用 conda run 在目标环境里执行，不改变当前 shell 的激活状态
    for t in ${tools}; do
        if conda run -n "${env_name}" which "${t}" >/dev/null 2>&1; then
            echo "    OK   ${t} -> $(conda run -n "${env_name}" which "${t}")"
        else
            echo "    FAIL ${t} 找不到（可能是包名变更，见 07_envs/conda/README.md 的已知别名）"
            missing=$((missing + 1))
        fi
    done
    [[ ${missing} -eq 0 ]] && echo "    -> ${env_name} 就绪" || echo "    -> ${env_name} 有 ${missing} 个工具缺失"
}

main() {
    local targets=("$@")
    [[ ${#targets[@]} -eq 0 ]] && targets=("${DEFAULT_ORDER[@]}")
    echo "=== conda 环境准备开始（目标：${targets[*]}）==="
    init_conda
    local a
    for a in "${targets[@]}"; do
        echo "[env] ${a}"
        create_env "${a}"
    done
    echo "--- 现有环境一览 ---"
    conda env list
    echo "=== 完成。导出复现文件： conda env export --no-builds > environment.yml ==="
}

main "$@"
