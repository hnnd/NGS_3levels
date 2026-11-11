#!/bin/bash
#$ -S /bin/bash
#$ -N p01_check_refs
#$ -cwd
#$ -j y
# ============================================================
# 脚本名称：01_check_refs.sh
# 功能描述：p01 §4.5 文献核查的前三步自动化 ——
#           ① DOI 是否可解析（doi.org 期望 302，404 即为伪造）
#           ② Crossref 元数据（标题 / 期刊 / 年份）是否与 AI 所说一致
#           ③ 按标题反查 PubMed，看是否真有这篇
#           第 ④ 步（打开摘要确认它支持你要引用的那句话）没有脚本，只能人做。
# 环境    ：conda activate ngs_phd_base（只需 curl + python3）
# 作者    ：王运生
# 日期    ：2026-08-29
#
# 用法：bash 01_check_refs.sh <doi_list.txt> [outfile]
#       doi_list.txt 每行一个 DOI（可带 https://doi.org/ 前缀，空行与 # 开头行忽略）
# ============================================================
set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_base

DOI_LIST="${1:?用法: bash 01_check_refs.sh <doi_list.txt> [outfile]}"
OUTFILE="${2:-${DOI_LIST%.txt}_checked.tsv}"
UA="p01-ref-check/1.0 (course NGS_3Levels; mailto:noreply@example.edu)"

printf 'doi\thttp_status\ttitle\tcontainer_or_publisher\tyear\tpubmed_hits\tverdict\n' > "${OUTFILE}"

n_total=0; n_bad=0
while IFS= read -r raw; do
    doi="$(printf '%s' "${raw}" | tr -d '[:space:]')"
    [[ -z "${doi}" || "${doi}" == \#* ]] && continue
    doi="${doi#https://doi.org/}"; doi="${doi#http://dx.doi.org/}"; doi="${doi#doi:}"
    n_total=$((n_total + 1))

    # ① DOI 解析：302 = 真；404 = 伪造
    status="$(curl -s -o /dev/null -w '%{http_code}' -I -A "${UA}" \
                --max-time 20 "https://doi.org/${doi}" || echo "000")"

    # ② Crossref 元数据（公开 API，无需密钥）
    meta="$(curl -s -A "${UA}" --max-time 25 "https://api.crossref.org/works/${doi}" \
            | python3 -c '
import json,sys
try:
    m = json.load(sys.stdin)["message"]
except Exception:
    print("NA\tNA\tNA"); sys.exit(0)
title = (m.get("title") or ["NA"])[0].replace("\t", " ")
cont  = (m.get("container-title") or ["NA"])[0].replace("\t", " ")
year  = str((m.get("issued", {}).get("date-parts") or [["NA"]])[0][0])
print(f"{title}\t{cont}\t{year}")' || printf 'NA\tNA\tNA')"

    title="$(printf '%s' "${meta}" | cut -f1)"

    # ②b Crossref 查不到不等于 DOI 无效：arXiv（10.48550）、Zenodo 等由 DataCite 注册，
    #     Crossref 一律 404。改查 DataCite 补元数据（项目 D047 的同一个坑）
    registry="crossref"
    if [[ "${title}" == "NA" ]]; then
        meta_dc="$(curl -s -A "${UA}" --max-time 25 "https://api.datacite.org/dois/${doi}" \
            | python3 -c '
import json,sys
try:
    a = json.load(sys.stdin)["data"]["attributes"]
except Exception:
    print("NA\tNA\tNA"); sys.exit(0)
title = ((a.get("titles") or [{}])[0].get("title") or "NA").replace("\t", " ")
cont  = (a.get("publisher") or "NA")
cont  = (cont.get("name", "NA") if isinstance(cont, dict) else cont).replace("\t", " ")
year  = str(a.get("publicationYear") or "NA")
print(f"{title}\t{cont}\t{year}")' || printf 'NA\tNA\tNA')"
        if [[ "$(printf '%s' "${meta_dc}" | cut -f1)" != "NA" ]]; then
            meta="${meta_dc}"; title="$(printf '%s' "${meta}" | cut -f1)"; registry="datacite"
        else
            registry="none"
        fi
    fi

    # ③ 按标题反查 PubMed（E-utilities，无需密钥）
    if [[ "${title}" != "NA" ]]; then
        q="$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1][:200]))" "${title}")"
        hits="$(curl -s -A "${UA}" --max-time 25 \
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&term=${q}%5BTitle%5D" \
                | python3 -c 'import json,sys
try: print(json.load(sys.stdin)["esearchresult"]["count"])
except Exception: print("NA")' || echo "NA")"
    else
        hits="NA"
    fi

    if [[ "${status}" == "404" ]]; then
        verdict="FAKE_or_UNRESOLVABLE"; n_bad=$((n_bad + 1))
    elif [[ "${status}" =~ ^(200|301|302|303)$ && "${title}" == "NA" ]]; then
        # 能解析但两家注册机构都无题录：少见，不能判伪造，要人工打开看
        verdict="RESOLVES_no_metadata_check_manually"
    elif [[ "${status}" =~ ^(200|301|302|303)$ && "${title}" =~ ^[[:space:]]*(RETRACTED|Retracted|WITHDRAWN|Withdrawn)[[:space:]:] ]]; then
        # 撤稿/撤回论文 DOI 照样 302，题名前缀才是标记（如 Frontiers 的 "RETRACTED: ..."）
        verdict="RETRACTED_do_not_cite"; n_bad=$((n_bad + 1))
    elif [[ "${status}" =~ ^(200|301|302|303)$ ]]; then
        verdict="RESOLVES_${registry}_check_abstract_manually"
    else
        verdict="UNCERTAIN_http_${status}"
    fi

    printf '%s\t%s\t%s\t%s\t%s\n' "${doi}" "${status}" "${meta}" "${hits}" "${verdict}" >> "${OUTFILE}"
    echo "[check] ${doi}  http=${status}  pubmed=${hits}  ${verdict}"
    sleep 1        # 对公开 API 保持礼貌，勿并发轰炸
done < "${DOI_LIST}"

echo "----------------------------------------------"
echo "共核查 ${n_total} 条，其中 ${n_bad} 条无法解析（疑似伪造）或已撤稿，见 verdict 列。"
echo "结果 -> ${OUTFILE}"
echo "提醒：解析得通 != 引用正确。第 ④ 步必须人工做——"
echo "      打开摘要，确认它真的说过你要引用的那句话。"
