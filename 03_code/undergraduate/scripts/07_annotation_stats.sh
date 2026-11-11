#!/bin/bash
# ============================================
# 脚本名称：07_annotation_stats.sh
# 功能描述：从 Prokka 输出计算注释质检指标——各类特征计数、编码密度、
#           平均基因长度、hypothetical protein 占比（单元 u07 ⑤5.3 / ⑥6.1）
# 运行方式：bash 07_annotation_stats.sh [prokka_outdir] [prefix]
#           计算量极小，可在登录节点直接运行，无需 qsub
# 作者：王运生
# 日期：2026-08-29
# ============================================

set -euo pipefail

OUTDIR="${1:-prokka_out}"
PREFIX="${2:-mygenome}"
GFF="${OUTDIR}/${PREFIX}.gff"
FNA="${OUTDIR}/${PREFIX}.fna"
TSV="${OUTDIR}/${PREFIX}.tsv"

check_inputs() {
    local f
    for f in "${GFF}" "${FNA}" "${TSV}"; do
        if [[ ! -s "${f}" ]]; then
            echo "[ERROR] 缺少或为空：${f}（Prokka 是否成功跑完？看 ${OUTDIR}/${PREFIX}.log）" >&2
            exit 1
        fi
    done
}

main() {
    check_inputs

    echo "== 各类特征计数（GFF 第 3 列）=="
    awk -F'\t' '!/^#/ && NF>=3 {print $3}' "${GFF}" | sort | uniq -c | sort -rn

    local cds_bp gen_bp cds_n trna_n rrna_n total hypo
    cds_bp=$(awk -F'\t' '$3=="CDS"{s+=$5-$4+1} END{print s+0}' "${GFF}")
    gen_bp=$(awk '/^>/{next}{n+=length($0)} END{print n+0}' "${FNA}")
    cds_n=$(awk -F'\t' '$3=="CDS"' "${GFF}" | wc -l)
    trna_n=$(awk -F'\t' '$3=="tRNA"' "${GFF}" | wc -l)
    rrna_n=$(awk -F'\t' '$3=="rRNA"' "${GFF}" | wc -l)
    total=$(awk -F'\t' '$2=="CDS"' "${TSV}" | wc -l)
    hypo=$(awk -F'\t' '$2=="CDS" && $7 ~ /hypothetical protein/' "${TSV}" | wc -l)

    echo
    echo "== 质检指标（可直接贴进实践报告 §3.1）=="
    echo "| 指标 | 数值 | 正常参考范围 |"
    echo "|---|---|---|"
    awk -v g="${gen_bp}" 'BEGIN{printf "| 基因组总长 | %.2f Mb | —— |\n", g/1e6}'
    awk -v n="${cds_n}" -v g="${gen_bp}" \
        'BEGIN{printf "| CDS 数 | %d（%.0f 个/Mb） | 约每 1 kb 一个基因，即 ~1000 个/Mb |\n", n, n/(g/1e6)}'
    awk -v c="${cds_bp}" -v g="${gen_bp}" \
        'BEGIN{printf "| 编码密度 | %.1f%% | 85-90%% |\n", 100*c/g}'
    awk -v c="${cds_bp}" -v n="${cds_n}" \
        'BEGIN{if(n>0) printf "| 平均基因长度 | %.0f bp | 850-1000 bp |\n", c/n}'
    echo "| tRNA 数 | ${trna_n} | 40-90 |"
    echo "| rRNA 基因数 | ${rrna_n} | 3-21（1-7 个 rrn 操纵子 × 5S/16S/23S；课程经验值）|"
    awk -v h="${hypo}" -v t="${total}" \
        'BEGIN{if(t>0) printf "| hypothetical protein | %d/%d = %.1f%% | 20-40%% |\n", h, t, 100*h/t}'

    echo
    echo "[提示] 任何一项明显偏离参考范围，先怀疑上游组装（回 u06 看 QUAST / BUSCO），"
    echo "       而不是怀疑 Prokka。判读表见讲义 ⑥6.2。"
}

main "$@"
