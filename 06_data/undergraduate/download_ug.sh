#!/bin/bash
# ============================================
# 脚本名称：download_ug.sh
# 功能描述：下载本科层主线数据（Xanthomonas oryzae pv. oryzae，PRJEB100987）
#           —— u06 组装与 k-mer 扫描、u07 注释、u08 综合项目（定种 / 建树 / 泛基因组）
# 作者：王运生
# 日期：2026-08-30
# 用法：
#   bash 06_data/undergraduate/download_ug.sh                    # 默认 dry-run，只打印将要做什么
#   bash 06_data/undergraduate/download_ug.sh --run              # 真正下载（约 640 MB）
#   bash 06_data/undergraduate/download_ug.sh --run --module u06 # 只下 u06 需要的
#   bash 06_data/undergraduate/download_ug.sh --run --subsample  # 下载后把 ONT 降采样到 40x
#   bash 06_data/undergraduate/download_ug.sh --run --outdir /d3/scratch/$USER/ngs/data
#
# 设计说明：
#   · 走 ENA FTP 直下 fastq.gz，比 prefetch/fasterq-dump 稳且不需要 SRA Toolkit；
#     ENA 同时提供 fastq_md5，下载后逐个校验——**没有校验的下载等于没下载**
#   · 断点续传用 wget -c；重跑本脚本不会重复下载已完成且 md5 正确的文件
#   · 所有登录号都已通过 06_data/verify_accessions.sh 在线核验（2026-08-30）
# ============================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# ---- 默认参数 ----
OUTDIR="${REPO_ROOT}/06_data/raw/undergraduate"
DRY_RUN=1
MODULE="all"
SUBSAMPLE=0
TARGET_DEPTH=40
GENOME_SIZE=4770000          # CIX4481 完成图 4,768,212 bp（GCA_987216485）

ENA_FASTQ="https://ftp.sra.ebi.ac.uk/vol1/fastq"
ENA_FASTA_API="https://www.ebi.ac.uk/ena/browser/api/fasta"

# ---- 数据清单：run 登录号 | 用途 | 相对路径 ----
# ONT 长读长（u06 组装主数据）
readonly ONT_RUN="ERR15732384"
readonly ONT_MD5="e49f650409f896690a04b048a43a7805"
readonly ONT_URL="${ENA_FASTQ}/ERR157/084/ERR15732384/ERR15732384.fastq.gz"

# Illumina 双端（u06 k-mer 扫描，与 ONT 同一株 CIX4481）
readonly ILL_RUN="ERR15732342"
readonly ILL_MD5_1="eb42b14235d1f238145496db703aa50b"
readonly ILL_MD5_2="adf9121aae9e824846570ea04d8db27d"
readonly ILL_URL_1="${ENA_FASTQ}/ERR157/042/ERR15732342/ERR15732342_1.fastq.gz"
readonly ILL_URL_2="${ENA_FASTQ}/ERR157/042/ERR15732342/ERR15732342_2.fastq.gz"

# u08 泛基因组 / 建树用的完成图（12 株，含学生自己组装的那株 CIX4481 作对照）
readonly -a PANGENOME=(
    "GCA_987216485:CIX4481"   # 学生自己组装的这一株——用来核对组装是否正确
    "GCA_987216405:CIX2353"
    "GCA_987216395:CIX2951"
    "GCA_987216465:CIX2983"
    "GCA_987216755:CIX3029"
    "GCA_987216515:CIX3092"
    "GCA_987216715:CIX3097"
    "GCA_987216575:CIX4024"
    "GCA_987218935:CIX4100"
    "GCA_987216745:CIX4228"
    "GCA_987216825:CIX4275"
    "GCA_987216765:CIX4310"
)

# u08 定种（Mash / FastANI）外群：一个同种不同致病变种、一个不同种
readonly -a OUTGROUP=(
    "GCA_030177815:Xoc_HB8"       # X. oryzae pv. oryzicola —— 同种，ANI 应仍 > 95%
    "GCA_024298585:Xcc_CN02"      # X. campestris pv. campestris —— 异种，ANI 应 < 95%
)

usage() {
    sed -n '2,20p' "${BASH_SOURCE[0]}"
    exit 0
}

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --run)        DRY_RUN=0; shift ;;
            --dry-run)    DRY_RUN=1; shift ;;
            --subsample)  SUBSAMPLE=1; shift ;;
            --depth)      TARGET_DEPTH="$2"; shift 2 ;;
            --module)     MODULE="$2"; shift 2 ;;
            --outdir)     OUTDIR="$2"; shift 2 ;;
            -h|--help)    usage ;;
            *) echo "未知参数：$1（用 --help 看用法）" >&2; exit 2 ;;
        esac
    done
}

# 下载单个文件并校验 md5；已存在且 md5 正确则跳过
fetch() {
    local url="$1" dest="$2" md5="${3:-}"
    if [[ -f "${dest}" && -n "${md5}" ]]; then
        if [[ "$(md5sum "${dest}" | cut -d' ' -f1)" == "${md5}" ]]; then
            log "已存在且校验通过，跳过：$(basename "${dest}")"
            return 0
        fi
        log "已存在但校验不符，重新下载：$(basename "${dest}")"
    fi
    if [[ "${DRY_RUN}" -eq 1 ]]; then
        printf '  [dry-run] wget -c -O %s %s\n' "${dest}" "${url}"
        [[ -n "${md5}" ]] && printf '  [dry-run] md5 期望 %s\n' "${md5}"
        return 0
    fi
    mkdir -p "$(dirname "${dest}")"
    wget -c -q --show-progress -O "${dest}" "${url}"
    if [[ -n "${md5}" ]]; then
        local got
        got="$(md5sum "${dest}" | cut -d' ' -f1)"
        if [[ "${got}" != "${md5}" ]]; then
            echo "md5 校验失败：${dest}（期望 ${md5}，实际 ${got}）" >&2
            return 1
        fi
        log "md5 通过：$(basename "${dest}")"
    fi
}

fetch_assembly() {
    local acc="$1" name="$2" dest="$3"
    if [[ -f "${dest}" ]]; then
        log "已存在，跳过：$(basename "${dest}")"
        return 0
    fi
    if [[ "${DRY_RUN}" -eq 1 ]]; then
        printf '  [dry-run] curl -sL %s/%s -o %s\n' "${ENA_FASTA_API}" "${acc}" "${dest}"
        return 0
    fi
    mkdir -p "$(dirname "${dest}")"
    curl -sL --max-time 300 "${ENA_FASTA_API}/${acc}?download=false" -o "${dest}"
    # 组装 FASTA 无官方 md5，改用"非空 + 首行是 FASTA 头 + 长度量级合理"三重自检
    if [[ ! -s "${dest}" ]] || ! head -1 "${dest}" | grep -q '^>'; then
        echo "下载的组装文件不是合法 FASTA：${dest}" >&2
        return 1
    fi
    local bp
    bp="$(grep -v '^>' "${dest}" | tr -d '\n' | wc -c)"
    if (( bp < 3000000 || bp > 7000000 )); then
        echo "警告：${name} 长度 ${bp} bp 超出 Xanthomonas 预期区间 3–7 Mb，请人工核查" >&2
    fi
    log "组装就位：${name} (${acc}) ${bp} bp"
}

download_reads() {
    log "── u06 读长数据（菌株 CIX4481：ONT 组装 + Illumina k-mer 扫描）"
    fetch "${ONT_URL}"   "${OUTDIR}/reads/${ONT_RUN}_ont.fastq.gz"  "${ONT_MD5}"
    fetch "${ILL_URL_1}" "${OUTDIR}/reads/${ILL_RUN}_1.fastq.gz"    "${ILL_MD5_1}"
    fetch "${ILL_URL_2}" "${OUTDIR}/reads/${ILL_RUN}_2.fastq.gz"    "${ILL_MD5_2}"
}

download_genomes() {
    log "── u08 泛基因组与建树：12 株完成图"
    local item acc name
    for item in "${PANGENOME[@]}"; do
        acc="${item%%:*}"; name="${item##*:}"
        fetch_assembly "${acc}" "${name}" "${OUTDIR}/genomes/${name}.fna"
    done
    log "── u08 定种外群：2 株"
    for item in "${OUTGROUP[@]}"; do
        acc="${item%%:*}"; name="${item##*:}"
        fetch_assembly "${acc}" "${name}" "${OUTDIR}/outgroup/${name}.fna"
    done
}

# 把 ONT 降采样到目标深度——课堂 4 核机器上 61x 组装约 25 min，40x 约 15 min
subsample_ont() {
    local src="${OUTDIR}/reads/${ONT_RUN}_ont.fastq.gz"
    local dst="${OUTDIR}/reads/${ONT_RUN}_ont_${TARGET_DEPTH}x.fastq.gz"
    local target_bases=$(( GENOME_SIZE * TARGET_DEPTH ))
    if [[ "${DRY_RUN}" -eq 1 ]]; then
        printf '  [dry-run] seqkit head -n <按 %s bp 估算> %s -o %s\n' "${target_bases}" "${src}" "${dst}"
        return 0
    fi
    command -v seqkit >/dev/null 2>&1 || {
        echo "未找到 seqkit（conda activate ngs_ug_assembly）" >&2; return 1; }
    [[ -f "${src}" ]] || { echo "先下载再降采样：${src} 不存在" >&2; return 1; }
    log "降采样 ONT 至 ${TARGET_DEPTH}x（目标 ${target_bases} bp）"
    # 长读长按碱基数截取，不能按 read 数——read 长度差异极大
    seqkit head -n 1000000 "${src}" 2>/dev/null |
        awk -v target="${target_bases}" 'BEGIN{n=0}
            NR%4==1{h=$0} NR%4==2{s=$0} NR%4==3{p=$0}
            NR%4==0{ if (n < target) { print h; print s; print p; print $0; n += length(s) } }' |
        gzip -c > "${dst}"
    log "降采样完成：$(basename "${dst}") $(du -h "${dst}" | cut -f1)"
}

write_manifest() {
    local manifest="${OUTDIR}/MANIFEST.tsv"
    if [[ "${DRY_RUN}" -eq 1 ]]; then
        printf '  [dry-run] 将写入 %s（文件 / 大小 / SHA256 前 12 位）\n' "${manifest}"
        return 0
    fi
    log "── 记录 manifest（可复现性要求：文件哈希入档）"
    {
        printf 'file\tbytes\tsha256_12\tdownloaded_at\n'
        local f
        while IFS= read -r -d '' f; do
            printf '%s\t%s\t%s\t%s\n' \
                "${f#"${OUTDIR}/"}" \
                "$(stat -c%s "${f}")" \
                "$(sha256sum "${f}" | cut -c1-12)" \
                "$(date -Iseconds)"
        done < <(find "${OUTDIR}" -type f ! -name 'MANIFEST.tsv' -print0 | sort -z)
    } > "${manifest}"
    log "manifest 就位：${manifest}（$(( $(wc -l < "${manifest}") - 1 )) 个文件）"
}

main() {
    parse_args "$@"
    log "输出目录 : ${OUTDIR}"
    log "模式     : $([[ "${DRY_RUN}" -eq 1 ]] && echo 'dry-run（加 --run 才真正下载）' || echo '真实下载')"
    log "模块     : ${MODULE}"
    echo

    case "${MODULE}" in
        u06)          download_reads ;;
        u07|u08)      download_genomes ;;
        all)          download_reads; download_genomes ;;
        *) echo "未知模块：${MODULE}（可选 u06 / u07 / u08 / all）" >&2; exit 2 ;;
    esac

    [[ "${SUBSAMPLE}" -eq 1 ]] && subsample_ont
    write_manifest

    echo
    if [[ "${DRY_RUN}" -eq 1 ]]; then
        log "以上为 dry-run。确认无误后加 --run 执行。"
    else
        log "完成。数据在 ${OUTDIR}"
        log "下一步：u06 用 reads/ 做 k-mer 扫描与组装；u08 用 genomes/ 做泛基因组与建树。"
    fi
}

main "$@"
