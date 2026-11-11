#!/bin/bash
# ============================================
# 脚本名称：download_phd.sh
# 功能描述：下载并准备博士层主线数据集（水稻—稻瘟病菌体系）。
#           默认 dry-run 只打印命令，确认无误后加 --run 真正下载。
# 作者：王运生
# 日期：2026-08-30
# 用法：
#   bash 06_data/phd/download_phd.sh                      # 全部专题，dry-run
#   bash 06_data/phd/download_phd.sh --topic p03 --run    # 只下 p03 并真正执行
#   bash 06_data/phd/download_phd.sh --all --run --outdir /d3/scratch/$USER/ngs/data
#   bash 06_data/phd/download_phd.sh --topic p03 --run --full   # p03 下全量而非截取
#
# 【关键设计】p03/p04 的原始数据合计 > 200 GB，课堂不可能全量下载。
#   默认走**流式截取**：curl | zcat | head -N | gzip，只传输前 N 条 read 就断开连接。
#   代价：FASTQ 开头的 read 不是随机样本（按 flowcell 位置排序），质量与 GC 可能有偏。
#   要做正式分析请用 --full 下全量后再 `seqtk sample`。这一取舍已写进 README §注意事项。
# ============================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST_DIR="${SCRIPT_DIR}/manifests"
OUTDIR="${NGS_DATA_DIR:-./NGS_datasets/phd}"
TOPICS=(p02 p03 p04 p05 p06)
DRY_RUN=1
FULL=0
SUBSAMPLE_READS=2000000          # 每个样本截取的 read 数（p03）
ENA_API="https://www.ebi.ac.uk/ena/portal/api/filereport"
GEO_FTP="https://ftp.ncbi.nlm.nih.gov/geo"
RDP1="http://ricediversity.org/data/sets/44kgwas"
TENX="https://cf.10xgenomics.com/samples/spatial-exp/1.1.0/V1_Mouse_Brain_Sagittal_Anterior"

log()  { printf '[%s] %s\n' "$(date +%H:%M:%S)" "$*"; }
run()  { if [[ "${DRY_RUN}" -eq 1 ]]; then printf '  DRY  %s\n' "$*"; else eval "$@"; fi; }

usage() { sed -n '2,20p' "$0"; exit 0; }

while [[ $# -gt 0 ]]; do
    case "$1" in
        --topic)  TOPICS=("$2"); shift 2 ;;
        --all)    TOPICS=(p02 p03 p04 p05 p06); shift ;;
        --run)    DRY_RUN=0; shift ;;
        --dry-run) DRY_RUN=1; shift ;;
        --full)   FULL=1; shift ;;
        --reads)  SUBSAMPLE_READS="$2"; shift 2 ;;
        --outdir) OUTDIR="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) echo "未知参数：$1" >&2; exit 2 ;;
    esac
done

# 把一条 run 的 fastq 地址与 md5 从 ENA 取回来。
# 【坑】ENA filereport **总是**把 run_accession 作为第一列返回，无论 fields 里写没写它。
# 所以这里显式声明三列并取第 2、3 列——按 fields 的字面顺序去 cut -f1 会拿到登录号本身。
ena_urls() {
    curl -s --max-time 60 \
        "${ENA_API}?accession=$1&result=read_run&fields=run_accession,fastq_ftp,fastq_md5&format=tsv" |
        tail -n +2 | cut -f2,3
}

# 记录 SHA256，便于日后确认本地文件没被动过
record_hash() {
    local f="$1" manifest="$2"
    [[ "${DRY_RUN}" -eq 1 ]] && return 0
    [[ -f "${f}" ]] || return 0
    printf '%s\t%s\n' "$(sha256sum "${f}" | cut -c1-12)" "$(basename "${f}")" >> "${manifest}"
}

# ---------------------------------------------------------------- p02 单细胞与空间
fetch_p02() {
    local d="${OUTDIR}/p02_scrnaseq_spatial"
    log "p02 单细胞（GSE222584，水稻 RRSV/RGSV 侵染，9 样本 10X 矩阵，约 332 MB）"
    run "mkdir -p '${d}/scrna' '${d}/spatial'"
    tail -n +2 "${MANIFEST_DIR}/p02_gsm.tsv" | while IFS=$'\t' read -r gsm title files; do
        local pre="${gsm:0:${#gsm}-3}nnn"
        for f in ${files}; do
            run "curl -sL --retry 3 -C - -o '${d}/scrna/${f}' '${GEO_FTP}/samples/${pre}/${gsm}/suppl/${f}'"
            record_hash "${d}/scrna/${f}" "${d}/sha256.txt"
        done
    done
    log "p02 空间（10X 官方 Visium 演示，约 64 MB——植物公开 Visium 数据稀缺，见 README）"
    for f in filtered_feature_bc_matrix.tar.gz spatial.tar.gz; do
        run "curl -sL --retry 3 -C - -o '${d}/spatial/V1_Mouse_Brain_Sagittal_Anterior_${f}' '${TENX}/V1_Mouse_Brain_Sagittal_Anterior_${f}'"
        record_hash "${d}/spatial/V1_Mouse_Brain_Sagittal_Anterior_${f}" "${d}/sha256.txt"
    done
}

# ---------------------------------------------------------------- p03 双 RNA-seq
fetch_p03() {
    local d="${OUTDIR}/p03_dual_rnaseq"
    log "p03 双 RNA-seq（PRJNA661210 / GSE157400，Nip × G11|H2O × 12/24/48 hpi × 3 重复 = 18 样本，**单端**）"
    [[ "${FULL}" -eq 1 ]] && log "  模式：全量下载（约 104 GB，需 --full 且磁盘充足）" \
                          || log "  模式：流式截取每样本前 ${SUBSAMPLE_READS} 条 read（约 2 GB）"
    run "mkdir -p '${d}'"
    tail -n +2 "${MANIFEST_DIR}/p03_runs.tsv" | while IFS=$'\t' read -r acc title; do
        local line ftp md5
        line="$(ena_urls "${acc}")" || { log "  取 URL 失败：${acc}"; continue; }
        ftp="$(echo "${line}" | cut -f1 | cut -d';' -f1)"
        md5="$(echo "${line}" | cut -f2 | cut -d';' -f1)"
        [[ -z "${ftp}" ]] && { log "  ENA 无 fastq：${acc}"; continue; }
        if [[ "${FULL}" -eq 1 ]]; then
            run "curl -sL --retry 3 -C - -o '${d}/${title}.fastq.gz' 'https://${ftp}'"
            # 全量下载才有意义校验 md5——截取后的文件 md5 必然不同
            if [[ "${DRY_RUN}" -eq 0 && -n "${md5}" ]]; then
                echo "${md5}  ${d}/${title}.fastq.gz" | md5sum -c - || log "  ⚠ md5 不符：${acc}"
            fi
        else
            # 【坑】流式截取时 head 取够就退出，zcat 收到 SIGPIPE 返回非零；
            # 在 `set -euo pipefail` 下这会杀掉整个脚本（p04/p06 再也跑不到）。
            # 故与 download_master.sh 第 92-93 行同样加保护，再回头校验产物有效性。
            run "curl -sL --max-time 900 'https://${ftp}' | { zcat 2>/dev/null || true; } | head -n $(( SUBSAMPLE_READS * 4 )) | gzip > '${d}/${title}.sub.fastq.gz' || true"
            if [[ "${DRY_RUN}" -eq 0 ]]; then
                if [[ ! -s "${d}/${title}.sub.fastq.gz" ]] || ! gzip -t "${d}/${title}.sub.fastq.gz" 2>/dev/null; then
                    log "  ⚠ 截取失败或产物损坏，请重跑该样本：${acc}"
                fi
            fi
        fi
        record_hash "${d}/${title}.sub.fastq.gz" "${d}/sha256.txt"
    done
    log "  参考基因组需另备：水稻 IRGSP-1.0 + 稻瘟菌 70-15，合并成 gentrome（见 README §p03）"
}

# ---------------------------------------------------------------- p04 群体基因组
fetch_p04() {
    local d="${OUTDIR}/p04_popgen"
    log "p04 群体基因组（PRJEB53625，40 个稻瘟菌分离株，约 12.5 GB，单倍体约 11×）"
    # 【坑】产物按 ${iso}_${i}.fastq.gz 命名，同一分离株的多个 run 会**静默互相覆盖**：
    # 第 7 轮曾因 manifest 里 O23 出现 3 次、i76a 出现 2 次，40 行只落地 37 个分离株，
    # 而脚本照样 rc=0。这里显式校验，宁可报错也不要悄悄少 3 个样本。
    local dup
    dup="$(tail -n +2 "${MANIFEST_DIR}/p04_runs.tsv" | cut -f2 | sort | uniq -d | tr '\n' ' ')"
    if [[ -n "${dup// /}" ]]; then
        log "  ⚠ manifest 中分离株重复（产物会互相覆盖）：${dup}"
        log "    同一分离株的多个 run 属同一 biosample，应合并或只保留一个，不能同名落盘。"
    fi
    run "mkdir -p '${d}'"
    tail -n +2 "${MANIFEST_DIR}/p04_runs.tsv" | while IFS=$'\t' read -r acc iso bases bytes; do
        local line ftp md5 i=1
        line="$(ena_urls "${acc}")" || { log "  取 URL 失败：${acc}"; continue; }
        ftp="$(echo "${line}" | cut -f1)"; md5="$(echo "${line}" | cut -f2)"
        # 【坑】ENA portal API 在高并发下会返回空 body（不是 HTTP 错误），curl 退出码仍为 0。
        # 没有这道守卫的话，该分离株会被下面的 `[[ -z "${u}" ]] && continue` **静默跳过**，
        # 脚本照样 rc=0 退出——表现为"40 个分离株只下了 3 个却报成功"。与 fetch_p03 保持一致。
        [[ -z "${ftp}" ]] && { log "  ENA 无 fastq 或响应为空（可重跑续传）：${acc}"; continue; }
        IFS=';' read -ra URLS <<< "${ftp}"
        IFS=';' read -ra MD5S <<< "${md5}"
        for u in "${URLS[@]}"; do
            [[ -z "${u}" ]] && continue
            run "curl -sL --retry 3 -C - -o '${d}/${iso}_${i}.fastq.gz' 'https://${u}'"
            if [[ "${DRY_RUN}" -eq 0 && -n "${MD5S[$((i-1))]:-}" ]]; then
                echo "${MD5S[$((i-1))]}  ${d}/${iso}_${i}.fastq.gz" | md5sum -c - || log "  ⚠ md5 不符：${acc}"
            fi
            record_hash "${d}/${iso}_${i}.fastq.gz" "${d}/sha256.txt"
            i=$((i+1))
        done
    done
}

# ---------------------------------------------------------------- p05 GWAS（非 ENA 源）
fetch_p05() {
    local d="${OUTDIR}/p05_gwas"
    log "p05 GWAS（Rice Diversity Panel 1：413 份种质 × 44K SNP × 34 表型，约 8.5 MB）"
    run "mkdir -p '${d}'"
    for f in RiceDiversity.44K.MSU6.Genotypes_PLINK.zip \
             RiceDiversity_44K_Phenotypes_34traits_PLINK.txt \
             RiceDiversity.44K.germplasm.csv \
             RiceDiversity.44K.MSU6.SNP_Information.txt; do
        run "curl -sL --retry 3 -C - -o '${d}/${f}' '${RDP1}/${f}'"
        record_hash "${d}/${f}" "${d}/sha256.txt"
    done
    # 【坑】表型文件是旧 Mac 的 CR 行尾，不转换的话 wc -l 返回 0、R 只读进一行
    run "tr '\\r' '\\n' < '${d}/RiceDiversity_44K_Phenotypes_34traits_PLINK.txt' > '${d}/phenotypes_34traits.tsv'"
    log "  已发表 MLM p 值（可与自己的结果对答案，23 MB，可选）："
    run "curl -sL --retry 3 -C - -o '${d}/MixedModel_Pval_all.txt' '${RDP1}/RiceDiversity.44K.MSU6.GWAS_pvalues/MixedModel_Pval_all.txt'"
    run "unzip -o -d '${d}' '${d}/RiceDiversity.44K.MSU6.Genotypes_PLINK.zip'"
}

# ---------------------------------------------------------------- p06 多组学
fetch_p06() {
    local d="${OUTDIR}/p06_multiomics"
    log "p06 多组学（代谢组 MTBLS13460；转录组复用 p03 的 GSE157400）"
    log "  ⚠ 两层**不是同一批样本**，只能做流程练习，不能下跨组学生物学结论——见 README §p06"
    run "mkdir -p '${d}'"
    run "curl -sL --retry 3 -o '${d}/MTBLS13460_files.json' 'https://www.ebi.ac.uk/metabolights/ws/studies/MTBLS13460/files'"
    # 【2026-08-30 补全】原实现只拉回文件清单 JSON 就结束，学生手上没有任何矩阵，
    # p06 实践课无从下手。这里据清单把 ISA-Tab 元数据与 MAF 丰度表一并取回。
    # 注意 MetaboLights 的 ws/download 接口对本研究返回 400，走 FTP 镜像的 HTTPS 端点。
    local mtbls_base="https://ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/MTBLS13460"
    if [[ "${DRY_RUN}" -eq 0 && -s "${d}/MTBLS13460_files.json" ]]; then
        local files
        files="$(python3 -c "
import json,sys
d=json.load(open('${d}/MTBLS13460_files.json'))
for f in d.get('study', []):
    n=f.get('file','')
    if n.startswith(('m_','s_','a_','i_')):
        print(n)
" 2>/dev/null)"
        if [[ -z "${files}" ]]; then
            log "  ⚠ 清单解析不出 m_/s_/a_/i_ 文件，请手工核对 MTBLS13460_files.json"
        fi
        local nf=0
        while IFS= read -r fn; do
            [[ -z "${fn}" ]] && continue
            if curl -sfL --retry 3 --max-time 300 -o "${d}/${fn}" "${mtbls_base}/${fn}"; then
                nf=$((nf+1))
            else
                log "  ⚠ 取回失败：${fn}"
            fi
        done <<< "${files}"
        log "  代谢组 ISA-Tab + MAF 共取回 ${nf} 个文件"
        # MAF 是丰度表，学生实践课的输入；这里报一下规模，取空了立刻能看出来
        for maf in "${d}"/m_*_maf.tsv; do
            [[ -f "${maf}" ]] || continue
            log "  $(basename "${maf}")：$(( $(wc -l < "${maf}") - 1 )) 行代谢物 × $(head -1 "${maf}" | awk -F'\t' '{print NF}') 列"
            record_hash "${maf}" "${d}/sha256.txt"
        done
    else
        log "  [dry-run] 将据清单取回 m_*/s_*/a_*/i_* 到 ${d}"
    fi
}

main() {
    log "输出目录：${OUTDIR}"
    [[ "${DRY_RUN}" -eq 1 ]] && log "当前是 dry-run，只打印不执行；加 --run 才真正下载"
    run "mkdir -p '${OUTDIR}'"
    for t in "${TOPICS[@]}"; do
        case "${t}" in
            p02) fetch_p02 ;;
            p03) fetch_p03 ;;
            p04) fetch_p04 ;;
            p05) fetch_p05 ;;
            p06) fetch_p06 ;;
            p01|p07|p08)
                log "${t} 不需要外部数据（p01 自造 spike-in；p07 复用 p03/p04 子集；p08 用学生自己课题）" ;;
            *) echo "未知专题：${t}" >&2; exit 2 ;;
        esac
    done
    log "完成。核验登录号：bash 06_data/verify_accessions.sh"
}

main "$@"
