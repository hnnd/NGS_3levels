#!/bin/bash
# ============================================
# 脚本名称：verify_accessions.sh
# 功能描述：对课程用到的每个登录号做在线核验（ENA + NCBI），确认它真实存在且元数据与
#           讲义声明一致。**任何写进材料的登录号都必须先过这一关**——第 7 轮实查发现
#           m01 讲义原写的 PRJNA294222 在 NCBI 根本不存在（正确为 PRJNA295606）。
# 作者：王运生
# 日期：2026-08-30
# 用法：
#   bash 06_data/verify_accessions.sh                       # 核验清单文件里的全部登录号
#   bash 06_data/verify_accessions.sh SRR2584863 PRJNA295606 # 只核验指定的
# 清单：06_data/accessions.tsv（列：accession / 用途 / 期望物种关键词）
# 退出码：0 = 全部通过；1 = 有登录号查无此项或元数据不符
# ============================================
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIST="${SCRIPT_DIR}/accessions.tsv"
ENA="https://www.ebi.ac.uk/ena/portal/api/filereport"
EUTILS="https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TIMEOUT=40
fail=0

# 查 ENA 读取记录；成功则打印 run 数与物种
check_ena_reads() {
    local acc="$1"
    curl -s --max-time "${TIMEOUT}" \
        "${ENA}?accession=${acc}&result=read_run&fields=run_accession,scientific_name,instrument_platform,library_strategy,read_count&format=tsv" \
        2>/dev/null | tail -n +2
}

# 查 ENA 组装/序列记录（GCA_*、CP*、NZ_* 等）
check_ena_assembly() {
    local acc="$1"
    curl -s --max-time "${TIMEOUT}" \
        "${ENA}?accession=${acc}&result=assembly&fields=accession,scientific_name,assembly_level&format=tsv" \
        2>/dev/null | tail -n +2
}

# 查 NCBI（ENA 查不到时的第二源；BioProject / GEO 系列走这里）
check_ncbi() {
    local acc="$1" db="$2"
    curl -s --max-time "${TIMEOUT}" \
        "${EUTILS}/esearch.fcgi?db=${db}&term=${acc}&retmode=json" 2>/dev/null |
        python3 -c "import sys,json
try:
    d=json.load(sys.stdin)['esearchresult']
    print(len(d.get('idlist',[])))
except Exception:
    print(0)"
}

# 查 MetaboLights（代谢组，MTBLS*）——它既不在 ENA 也不在 NCBI
check_metabolights() {
    local acc="$1"
    curl -s --max-time "${TIMEOUT}" \
        "https://www.ebi.ac.uk/ebisearch/ws/rest/metabolights/entry/${acc}?fields=name&format=json" \
        2>/dev/null | python3 -c "import sys,json
try:
    e=json.load(sys.stdin).get('entries',[])
    print(e[0]['fields']['name'][0][:70] if e else '')
except Exception:
    print('')"
}

verify_one() {
    local acc="$1" note="${2:-}" expect="${3:-}"
    local out species=""

    # MetaboLights 单独走一条路
    if [[ "${acc}" == MTBLS* ]]; then
        local title
        title="$(check_metabolights "${acc}")"
        if [[ -n "${title}" ]]; then
            printf '  [通过] %-16s MetaboLights ｜ %s  %s\n' "${acc}" "${title}" "${note}"
        else
            printf '  [查无] %-16s MetaboLights 无此研究——不得写进材料  %s\n' "${acc}" "${note}"
            fail=1
        fi
        return
    fi
    out="$(check_ena_reads "${acc}")"
    if [[ -z "${out}" ]]; then
        out="$(check_ena_assembly "${acc}")"
    fi
    if [[ -n "${out}" ]]; then
        local n
        n="$(echo "${out}" | grep -c .)"
        species="$(echo "${out}" | head -1 | cut -f2)"
        if [[ -n "${expect}" ]] && ! echo "${species}" | grep -qi "${expect}"; then
            printf '  [不符] %-16s 期望物种含 "%s"，实际 "%s"  %s\n' "${acc}" "${expect}" "${species}" "${note}"
            fail=1
            return
        fi
        printf '  [通过] %-16s %s 条记录 ｜ %s  %s\n' "${acc}" "${n}" "${species}" "${note}"
        return
    fi
    # ENA 无记录：按前缀决定去 NCBI 的哪个库再确认一次
    local db="sra"
    case "${acc}" in
        PRJ*)  db="bioproject" ;;
        GSE*)  db="gds" ;;
        GCA_*|GCF_*) db="assembly" ;;
    esac
    local hits
    hits="$(check_ncbi "${acc}" "${db}")"
    if [[ "${hits}" -gt 0 ]]; then
        printf '  [通过] %-16s NCBI %s 命中 %s 条（ENA 无镜像）  %s\n' "${acc}" "${db}" "${hits}" "${note}"
    else
        printf '  [查无] %-16s ENA 与 NCBI %s 均无此登录号——不得写进材料  %s\n' "${acc}" "${db}" "${note}"
        fail=1
    fi
}

main() {
    if [[ $# -gt 0 ]]; then
        echo "核验指定登录号（$# 个）"
        for acc in "$@"; do verify_one "${acc}"; done
    else
        [[ -f "${LIST}" ]] || { echo "找不到清单 ${LIST}" >&2; exit 2; }
        echo "核验清单 ${LIST}"
        while IFS=$'\t' read -r acc note expect; do
            [[ -z "${acc}" || "${acc}" == \#* ]] && continue
            verify_one "${acc}" "${note}" "${expect}"
        done < "${LIST}"
    fi
    echo
    if [[ "${fail}" -eq 0 ]]; then
        echo "全部通过。"
    else
        echo "存在查无此项或元数据不符的登录号，请修正后再写进课程材料。" >&2
    fi
    return "${fail}"
}

main "$@"
