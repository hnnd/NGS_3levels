#!/bin/bash
#$ -S /bin/bash
#$ -N antismash
#$ -cwd
#$ -j y
#$ -pe smp 4
# ============================================
# 脚本名称：07_run_antismash.sh
# 功能描述：用 antiSMASH 预测次级代谢产物生物合成基因簇 BGC（单元 u07 / 项目手册 §4.3）
#           优先使用 Prokka 的 .gbk 作为输入（带基因边界与基因名，报告可读性更好）
# 运行方式：qsub 07_run_antismash.sh [input.gbk|genome.fasta] [outdir]
# 前置条件：首次使用需先在**登录节点**下载数据库（download-antismash-databases），脚本会预检
# 作者：王运生
# 日期：2026-08-29
# ============================================

set -euo pipefail

INPUT="${1:-prokka_out/mygenome.gbk}"   # 优先 .gbk；没有则传 genome.fasta
OUTDIR="${2:-antismash_out}"
TAXON="bacteria"
THREADS="${NSLOTS:-4}"
CONDA_ROOT="/opt/miniconda3"
CONDA_ENV="ngs_ug_annot"
# 数据库目录：计算节点不通外网，必须先在登录节点下载（UP-037）：
#   conda activate ngs_ug_annot && download-antismash-databases [--database-dir DIR]
# 下到自定义目录时，提交作业要带上同一路径：qsub -v ANTISMASH_DB=DIR 07_run_antismash.sh
ANTISMASH_DB="${ANTISMASH_DB:-}"

main() {
    # shellcheck disable=SC1091
    source "${CONDA_ROOT}/bin/activate"
    conda activate "${CONDA_ENV}"

    if [[ ! -s "${INPUT}" ]]; then
        echo "[ERROR] 输入不存在或为空：${INPUT}" >&2
        echo "        先跑 07_run_prokka.sh，或改传 genome.fasta" >&2
        exit 1
    fi

    # 数据库预检：conda 包只含程序不含数据库，首次使用必须单独下载一次
    echo "[INFO] antiSMASH 版本：$(antismash --version)"
    local dbopt=()
    if [[ -n "${ANTISMASH_DB}" ]]; then
        [[ -d "${ANTISMASH_DB}" ]] || { echo "[ERROR] ANTISMASH_DB 目录不存在：${ANTISMASH_DB}" >&2; exit 1; }
        dbopt=(--databases "${ANTISMASH_DB}")
    fi
    if ! antismash ${dbopt[@]+"${dbopt[@]}"} --check-prereqs > antismash_prereqs.log 2>&1; then
        echo "[ERROR] 依赖或数据库检查未通过，详见 antismash_prereqs.log" >&2
        echo "        修复：conda activate ${CONDA_ENV} && download-antismash-databases" >&2
        echo "        （若提示 command not found 改用 antismash --prepare-data）" >&2
        echo "        磁盘紧张时加 --database-dir /d3/scratch/\${USER}/db/antismash" >&2
        exit 1
    fi

    # .gbk 已含基因边界，无需 --genefinding-tool；裸 FASTA 才需要现场找基因
    local genefinding=""
    if [[ "${INPUT}" != *.gbk && "${INPUT}" != *.gbff ]]; then
        genefinding="--genefinding-tool prodigal"
        echo "[INFO] 输入是核酸序列，启用 ${genefinding}"
    fi

    echo "[INFO] 开始 BGC 预测：${INPUT} → ${OUTDIR}（${THREADS} 线程）"
    # shellcheck disable=SC2086
    antismash ${dbopt[@]+"${dbopt[@]}"} --output-dir "${OUTDIR}" ${genefinding} \
              --taxon "${TAXON}" --cpus "${THREADS}" "${INPUT}"

    # 记录软件与数据库版本：报告的「方法」一节必须写，换库后 BGC 结果会变
    local dbdir="${ANTISMASH_DB}"
    [[ -z "${dbdir}" ]] && dbdir="$(python -c 'import antismash, os; print(os.path.join(os.path.dirname(antismash.__file__), "databases"))' 2>/dev/null || echo unknown)"
    {
        printf "%s\t%s\n" date "$(date +%F)"
        printf "%s\t%s\n" antismash "$(antismash --version)"
        printf "%s\t%s\n" database_dir "${dbdir}"
        # 版本信息体现在子目录名上（如 pfam/35.0、clusterblast 等）
        [[ -d "${dbdir}" ]] && find "${dbdir}" -mindepth 1 -maxdepth 2 -type d | sed "s|^${dbdir}/|db_subdir\t|" | sort
    } > "${OUTDIR}/software_versions.tsv" || true
    echo "[INFO] 版本记录：${OUTDIR}/software_versions.tsv（写进报告方法部分）"

    echo "[INFO] 完成。用 scp -r 把整个 ${OUTDIR} 目录拉回本机后打开 index.html"
    echo "       只拉单个 html 会是白页（依赖同目录的 js/css）"
    echo "[提示] 若某个簇标注 on contig edge，说明它被组装断点截断，报告中必须写明"
}

main "$@"
