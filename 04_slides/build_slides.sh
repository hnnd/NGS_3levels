#!/bin/bash
# ============================================
# 脚本名称：build_slides.sh
# 功能描述：用 marp-cli 把 04_slides/<level>/*_slides.md 批量编译为 HTML（默认）或 PDF
# 作者：王运生
# 日期：2026-08-29
# 用法：
#   bash 04_slides/build_slides.sh                 # 全部层次 → HTML
#   bash 04_slides/build_slides.sh --pdf           # 全部层次 → PDF（需本机有 Chrome/Chromium）
#   bash 04_slides/build_slides.sh --level phd     # 只编译博士层
#   bash 04_slides/build_slides.sh --watch phd/05_gwas_slides.md   # 编辑时实时预览
# ============================================
set -euo pipefail

SLIDES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME="${SLIDES_DIR}/themes/ngs.css"
OUT_DIR="${SLIDES_DIR}/dist"
FORMAT="--html"
LEVELS=(undergraduate master phd)
WATCH_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --pdf)   FORMAT="--pdf"; shift ;;
        --html)  FORMAT="--html"; shift ;;
        --pptx)  FORMAT="--pptx"; shift ;;
        --level) LEVELS=("$2"); shift 2 ;;
        --watch) WATCH_FILE="$2"; shift 2 ;;
        -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
        *) echo "未知参数：$1" >&2; exit 2 ;;
    esac
done

command -v marp >/dev/null 2>&1 || { echo "未找到 marp（npm i -g @marp-team/marp-cli）" >&2; exit 1; }

main() {
    if [[ -n "${WATCH_FILE}" ]]; then
        exec marp --theme-set "${THEME}" --watch --preview "${SLIDES_DIR}/${WATCH_FILE}"
    fi
    local n=0
    for level in "${LEVELS[@]}"; do
        mkdir -p "${OUT_DIR}/${level}"
        shopt -s nullglob
        for deck in "${SLIDES_DIR}/${level}"/*_slides.md; do
            echo "[${level}] $(basename "${deck}")"
            marp --no-stdin --theme-set "${THEME}" ${FORMAT} --allow-local-files \
                 -o "${OUT_DIR}/${level}/$(basename "${deck%.md}")${FORMAT/--/.}" "${deck}"
            n=$((n + 1))
        done
    done
    echo "完成：${n} 份 deck → ${OUT_DIR}/"
}

main "$@"
