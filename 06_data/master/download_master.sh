#!/bin/bash
# ============================================
# 脚本名称：download_master.sh
# 功能描述：下载硕士层各专题的主线数据（ENA FTP 直下 + md5 校验 + 断点续传 + SHA256 manifest）
# 作者：王运生
# 日期：2026-08-30
# ============================================
# 用法：
#   bash 06_data/master/download_master.sh --list                 # 只列清单与体积，不下载
#   bash 06_data/master/download_master.sh --topic m06            # 下载 m06（最小，242 MB，建议先跑这个）
#   bash 06_data/master/download_master.sh --topic m04 --subsample 3000000
#   bash 06_data/master/download_master.sh --all --run            # 全部真实下载
#   bash 06_data/master/download_master.sh --topic m02 --run --outdir /d3/scratch/$USER/ngs/data
#   bash 06_data/master/download_master.sh --topic m04 --run --subsample 3000000 \
#        --runs "DRR737491 DRR737492"        # 只重下这两个 run（下坏了 / 并行分片）
#
# 【默认 dry-run】不加 --run 只打印将要执行的命令，不产生任何下载。
#
# 关于 --subsample N：
#   m04/m05 的原始 fastq 每个 2–5 GB（全集 154 GB），课堂不可能全下。本脚本用
#   **ENA FTP 字节范围前缀下载 + zcat 截断** 取前 N 条 read——gzip 流从头解码即可，
#   不需要下完整个文件，也不需要 SRA Toolkit。取到的是文件头部的 read，
#   对教学足够（不是随机抽样，方法学里要如实写明）。
# ============================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
OUTDIR="${REPO_ROOT}/06_data/raw/master"
ENA_API="https://www.ebi.ac.uk/ena/portal/api/filereport"
DO_RUN=0
SUBSAMPLE=0
TOPICS=()
ONLY_RUNS=""          # --runs：只下指定的 run（用于重下单个样本 / 并行分片）
LIST_ONLY=0

# ---- 各专题的 run 清单（登录号均已由 06_data/verify_accessions.sh 实查通过）----
# m02 基因组组装与泛基因组：CIX2779 一株，ONT 组装 + Illumina 抛光
M02_RUNS="ERR15732374 ERR15732332"
# m03 重测序与变异检测：12 株西非 Xoo 的 Illumina
M03_RUNS="ERR15732323 ERR15732331 ERR15732332 ERR15732346 ERR15732333 ERR15732324 \
ERR15732325 ERR15732334 ERR15732326 ERR15732303 ERR15732304 ERR15732305"
# m04 转录组：水稻 Z 基因型，配对时间点 0030/0060/0120，处理 K(对照)/N(复氮)，重复 A/B
M04_RUNS="DRR737490 DRR737503 DRR737491 DRR737504 DRR737492 DRR737505 \
DRR737499 DRR737512 DRR737500 DRR737513 DRR737501 DRR737514"
# m05 调控组：与 m04 **完全相同的样本**的 ATAC-seq
M05_RUNS="DRR737541 DRR737554 DRR737542 DRR737555 DRR737543 DRR737556 \
DRR737550 DRR737563 DRR737551 DRR737564 DRR737552 DRR737565"
# m06 扩增子：铁毒稻田根际土 16S，Fe 10 个 vs nonFe 10 个，跨 2017/2018/2019 三年
M06_RUNS="DRR357521 DRR357522 DRR357529 DRR357530 DRR357531 DRR357532 DRR357545 DRR357546 DRR357547 DRR357548 \
DRR357523 DRR357524 DRR357533 DRR357534 DRR357535 DRR357536 DRR357549 DRR357550 DRR357551 DRR357552"
# m07 宏基因组：日本农田，水田 6 个 vs 旱地 6 个
M07_RUNS="DRR336839 DRR336851 DRR336863 DRR336843 DRR336855 DRR336867 \
DRR336847 DRR336871 DRR336848 DRR336872 DRR336859 DRR336860"

usage() { sed -n '2,30p' "$0"; exit 0; }

log() { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

# 取一个 run 的 fastq FTP 地址与 md5
fetch_meta() {
    local run="$1"
    curl -s --max-time 60 \
        "${ENA_API}?accession=${run}&result=read_run&fields=fastq_ftp,fastq_md5,fastq_bytes,read_count&format=tsv" |
        tail -n +2
}

# 下载单个 run 的全部 fastq 文件
download_run() {
    local run="$1" dest="$2"
    local meta ftp md5s
    meta="$(fetch_meta "${run}")"
    if [[ -z "${meta}" ]]; then
        echo "  !! ${run}: ENA 无记录，跳过（请先用 06_data/verify_accessions.sh 核验）" >&2
        return 1
    fi
    # 注意：ENA filereport 总是把 run_accession 作为第 1 列返回，即使没在 fields 里请求，
    # 所以 fastq_ftp 是第 2 列、fastq_md5 是第 3 列。写成 f1/f2 会把 run 号当成 URL。
    ftp="$(echo "${meta}" | cut -f2)"
    md5s="$(echo "${meta}" | cut -f3)"
    local sizes reads
    sizes="$(echo "${meta}" | cut -f4)"
    reads="$(echo "${meta}" | cut -f5)"
    local i=1
    IFS=';' read -ra urls <<< "${ftp}"
    IFS=';' read -ra md5arr <<< "${md5s}"
    IFS=';' read -ra sizearr <<< "${sizes}"
    for url in "${urls[@]}"; do
        local fname="${dest}/$(basename "${url}")"
        local want_md5="${md5arr[$((i-1))]:-}"
        if [[ "${SUBSAMPLE}" -gt 0 ]]; then
            # 前缀下载的字节数：用 ENA 元数据算**这个 run 的真实压缩比**，再留 1.5 倍冗余。
            # 【为什么不用固定常数】原实现按 250 B/read 估算，而实测 m04/m05 源文件只有
            # 71-86 B/read——多下了约 4.4 倍（每个文件 1072 MB vs 实际需要约 260 MB）。
            # 60 人的班级各跑一遍，这个系数就是几百 GB 的无谓流量。
            local per_read=0 bytes
            local this_size="${sizearr[$((i-1))]:-0}"
            if [[ "${reads:-0}" =~ ^[0-9]+$ && "${reads:-0}" -gt 0 && "${this_size}" =~ ^[0-9]+$ && "${this_size}" -gt 0 ]]; then
                per_read=$(( this_size / reads ))
            fi
            # 元数据缺失或异常时回退到保守常数；下限 120 B/read 防止压缩比异常导致取不满
            [[ "${per_read}" -lt 120 ]] && per_read=120
            bytes=$(( SUBSAMPLE * per_read * 3 / 2 ))
            local out="${fname%.fastq.gz}.sub${SUBSAMPLE}.fastq"
            # 【幂等】已有且 read 数达标的产物直接跳过——重跑不该把几百 MB 再下一遍。
            # 前缀下载没有断点续传的意义（每次都是从 0 开始的 range 请求），所以按产物判断。
            if [[ "${DO_RUN}" -eq 1 && -s "${out}.gz" ]]; then
                local have=$(( $(zcat "${out}.gz" 2>/dev/null | wc -l) / 4 ))
                if [[ "${have}" -ge "${SUBSAMPLE}" ]]; then
                    log "  ${run}: 已存在且 ${have} 条 read 达标，跳过 $(basename "${out}.gz")"
                    i=$((i+1)); continue
                fi
                log "  ${run}: 已有产物只有 ${have} 条 read（目标 ${SUBSAMPLE}），重下"
            fi
            if [[ "${DO_RUN}" -eq 0 ]]; then
                echo "  [dry-run] curl -r 0-${bytes} ftp://${url} | zcat | head -n $((SUBSAMPLE*4)) > ${out}"
            else
                log "  ${run}: 前缀下载 ${bytes} B（实测 ${per_read} B/read）→ 取前 ${SUBSAMPLE} 条 read"
                # 【坑】--max-time 与前缀大小必须匹配：原来 900 s 配 1125 MB，在竞争带宽下
                # （实测低至 0.5-1 MB/s）根本传不完，curl 被掐断 → 产物只有几十万条 read，
                # 而脚本不校验、不报错。实测曾出现 399 491 / 3 000 000 条的文件。
                # 现在前缀降到约 540 MB，同时把上限放宽到 3600 s，并在下面校验 read 数。
                curl -s --max-time 3600 -r "0-${bytes}" "ftp://${url}" 2>/dev/null |
                    { zcat 2>/dev/null || true; } | head -n $((SUBSAMPLE * 4)) > "${out}" || true
                # 【必须校验】前缀取短了不会报错，只会悄悄少 read——下游样本量与统计功效随之改变
                local got=$(( $(wc -l < "${out}" 2>/dev/null || echo 0) / 4 ))
                if [[ "${got}" -lt "${SUBSAMPLE}" ]]; then
                    log "  ⚠ ${run}: 只取到 ${got} 条 read（目标 ${SUBSAMPLE}）——前缀过短，重跑本 run 或调大冗余系数"
                fi
                gzip -f "${out}"
                log "  ${run}: $(du -h "${out}.gz" | cut -f1) → $(basename "${out}.gz")（${got} 条 read）"
            fi
        else
            if [[ "${DO_RUN}" -eq 0 ]]; then
                echo "  [dry-run] curl -C - -o ${fname} ftp://${url}   # md5 ${want_md5}"
            else
                log "  ${run}: 下载 $(basename "${url}")"
                curl -s --max-time 3600 -C - -o "${fname}" "ftp://${url}"
                if [[ -n "${want_md5}" ]]; then
                    local got
                    got="$(md5sum "${fname}" | cut -d' ' -f1)"
                    if [[ "${got}" != "${want_md5}" ]]; then
                        echo "  !! ${fname} md5 不符：期望 ${want_md5} 实得 ${got}" >&2
                        return 1
                    fi
                    log "  ${run}: md5 校验通过"
                fi
            fi
        fi
        i=$((i + 1))
    done
}

download_topic() {
    local topic="$1"
    local runs_var="${topic^^}_RUNS"
    local runs="${!runs_var:-}"
    # --runs 覆盖专题清单：用于「某个样本下坏了要重下」与并行分片下载。
    # 目的目录仍由 --topic 决定，所以产物路径与整批下载完全一致。
    if [[ -n "${ONLY_RUNS}" ]]; then
        runs="${ONLY_RUNS}"
        log "--runs 生效：只处理 ${runs}"
    fi
    if [[ -z "${runs}" ]]; then
        echo "未知专题 ${topic}（可用：m02 m03 m04 m05 m06 m07）" >&2
        return 2
    fi
    local dest="${OUTDIR}/${topic}"
    log "=== ${topic}：$(echo ${runs} | wc -w) 个 run → ${dest}"
    [[ "${DO_RUN}" -eq 1 ]] && mkdir -p "${dest}"
    for run in ${runs}; do
        download_run "${run}" "${dest}" || true
    done
    if [[ "${DO_RUN}" -eq 1 && -z "${ONLY_RUNS}" ]]; then
        # 只有整批下载才重写清单：--runs 分片时多个实例会把清单互相覆盖成残缺的
        ( cd "${dest}" && sha256sum ./*.gz 2>/dev/null | sed 's|^\([0-9a-f]\{12\}\)[0-9a-f]*|\1|' \
            > SHA256_MANIFEST.tsv ) || true
        log "${topic}: 已写 SHA256_MANIFEST.tsv（记录前 12 位，符合复现性规范）"
    elif [[ "${DO_RUN}" -eq 1 ]]; then
        log "${topic}: --runs 分片模式，未重写 SHA256_MANIFEST.tsv（全部下完后跑一次整批即可生成）"
    fi
}

list_topics() {
    printf '%-6s %-6s %s\n' 专题 run数 说明
    printf '%-6s %-6s %s\n' m02 2 "CIX2779 ONT+Illumina，约 0.6 GB；组装后与 GCA_024981335 比对"
    printf '%-6s %-6s %s\n' m03 12 "12 株西非 Xoo Illumina，约 4.0 GB"
    printf '%-6s %-6s %s\n' m04 12 "水稻 RNA-seq，全集约 32 GB；--subsample 3000000 后约 2 GB"
    printf '%-6s %-6s %s\n' m05 12 "同批样本 ATAC-seq，全集约 43 GB；建议同样 --subsample"
    printf '%-6s %-6s %s\n' m06 20 "16S 根际土，约 242 MB（最小，建议先跑这个）"
    printf '%-6s %-6s %s\n' m07 12 "宏基因组水田/旱地，约 1.1 GB"
}

main() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --topic)     TOPICS+=("$2"); shift 2 ;;
            --runs)      ONLY_RUNS="$2"; shift 2 ;;
            --all)       TOPICS=(m02 m03 m04 m05 m06 m07); shift ;;
            --run)       DO_RUN=1; shift ;;
            --dry-run)   DO_RUN=0; shift ;;
            --subsample) SUBSAMPLE="$2"; shift 2 ;;
            --outdir)    OUTDIR="$2"; shift 2 ;;
            --list)      LIST_ONLY=1; shift ;;
            -h|--help)   usage ;;
            *) echo "未知参数：$1" >&2; exit 2 ;;
        esac
    done

    if [[ "${LIST_ONLY}" -eq 1 ]]; then list_topics; exit 0; fi
    if [[ "${#TOPICS[@]}" -eq 0 ]]; then
        echo "未指定专题。用 --list 看清单，--topic m06 下载单个，--all 下载全部。" >&2
        list_topics
        exit 2
    fi
    [[ "${DO_RUN}" -eq 0 ]] && log "*** DRY-RUN 模式：只打印命令，不下载。加 --run 才真正执行。***"
    for t in "${TOPICS[@]}"; do download_topic "${t}"; done
    log "完成。"
}

main "$@"
