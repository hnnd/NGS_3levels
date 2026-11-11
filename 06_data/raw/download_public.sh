#!/bin/bash
# ============================================
# 脚本名称：download_public.sh
# 功能描述：三层数据下载的统一入口。第 7 轮主线数据定案后，实际下载逻辑已按层拆分到
#           06_data/{undergraduate,master,phd}/download_*.sh，本脚本只做分发，
#           避免旧入口与新脚本各说各话（本脚本第 5 轮版本写的是"主线数据待定"，已过时）。
# 作者：王运生
# 日期：2026-08-30
# 用法：
#   bash 06_data/raw/download_public.sh                      # 列出三层数据包与下载量
#   bash 06_data/raw/download_public.sh --level undergraduate --run
#   bash 06_data/raw/download_public.sh --level master --topic m04 --run
#   其余参数原样透传给各层脚本（--dry-run 是各层脚本的默认行为）
# ============================================
set -euo pipefail

DATA_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

declare -A SCRIPTS=(
    [undergraduate]="undergraduate/download_ug.sh"
    [master]="master/download_master.sh"
    [phd]="phd/download_phd.sh"
)

usage() {
    sed -n '2,16p' "$0"
    cat <<'TXT'

三层数据包（详见各目录 README.md）：
  undergraduate  Xanthomonas oryzae pv. oryzae（PRJEB100987）        约 485 MB
  master         西非水稻农业生态系统（Xoo + 水稻氮响应 + 稻田土壤）  约 10 GB
  phd            水稻–稻瘟病菌（含 RDP1 GWAS 与代谢组）              约 15 GB

下载前请先核验登录号：bash 06_data/verify_accessions.sh
TXT
}

main() {
    local level=""
    local -a passthru=()
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --level) level="$2"; shift 2 ;;
            -h|--help) usage; return 0 ;;
            *) passthru+=("$1"); shift ;;
        esac
    done

    if [[ -z "${level}" ]]; then
        usage
        return 0
    fi
    if [[ -z "${SCRIPTS[${level}]:-}" ]]; then
        echo "未知层次：${level}（可选 undergraduate | master | phd）" >&2
        return 2
    fi

    local target="${DATA_DIR}/${SCRIPTS[${level}]}"
    [[ -x "${target}" ]] || { echo "找不到或不可执行：${target}" >&2; return 1; }
    echo "→ 分发到 ${SCRIPTS[${level}]}"
    exec bash "${target}" "${passthru[@]}"
}

main "$@"
