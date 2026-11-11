#!/bin/bash
# ============================================
# 脚本名称：05_align_and_sort.sh
# 功能描述：本科单元 u05 配套脚本。参考基因组建索引 → bwa mem 双端比对
#           → 管道排序为 BAM → 建索引 → flagstat/coverage 统计
#           → PCR 重复标记（collate/fixmate -m/sort/markdup）→ 去重前后计数
# 环境依赖：conda env ngs_ug_base（bwa 0.7.x, samtools >= 1.10）
# 作者：王运生
# 日期：2026-08-29
# ============================================

set -euo pipefail   # 严格模式：管道中任一环节失败即终止（讲义 ⑨-E3）

# ---------- 默认参数 ----------
REF=""
FQ1=""
FQ2=""
SAMPLE="sample01"
OUTDIR="./bam"
THREADS=4
SORT_MEM="2G"       # 每线程内存，实际占用 = THREADS x SORT_MEM（讲义 ⑨-E5）
PLATFORM="ILLUMINA"
DO_MARKDUP=1
ALIGNER="bwa"       # bwa | bowtie2

usage() {
    cat <<'USAGE'
用法：
  bash 05_align_and_sort.sh -r <ref.fa> -1 <R1.fq.gz> -2 <R2.fq.gz> \
       [-s sample01] [-o bam] [-t 4] [-m 2G] [-a bwa|bowtie2] [--no-markdup]

参数：
  -r    参考基因组 FASTA（必需）。bwa 用 FASTA 路径；bowtie2 用同名前缀的索引
  -1    双端 R1（clean 数据，必需）
  -2    双端 R2（clean 数据，必需）
  -s    样本名，写进 @RG 的 SM 字段（默认 sample01）
  -o    输出目录（默认 ./bam）
  -t    线程数（默认 4）
  -m    samtools sort 的每线程内存（默认 2G）
  -a    比对器：bwa（默认）或 bowtie2
  --no-markdup   跳过 PCR 重复标记
USAGE
}

# ---------- 参数解析 ----------
while [[ $# -gt 0 ]]; do
    case "$1" in
        -r) REF="$2"; shift 2 ;;
        -1) FQ1="$2"; shift 2 ;;
        -2) FQ2="$2"; shift 2 ;;
        -s) SAMPLE="$2"; shift 2 ;;
        -o) OUTDIR="$2"; shift 2 ;;
        -t) THREADS="$2"; shift 2 ;;
        -m) SORT_MEM="$2"; shift 2 ;;
        -a) ALIGNER="$2"; shift 2 ;;
        --no-markdup) DO_MARKDUP=0; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "[ERROR] 未知参数：$1" >&2; usage; exit 1 ;;
    esac
done

# ---------- 前置检查 ----------
check_inputs() {
    local missing=0
    for f in "$REF" "$FQ1" "$FQ2"; do
        if [[ -z "$f" ]]; then
            echo "[ERROR] -r / -1 / -2 三个参数都必须给出" >&2; missing=1; break
        fi
        if [[ ! -s "$f" ]]; then
            echo "[ERROR] 文件不存在或为空：$f" >&2; missing=1
        fi
    done
    [[ $missing -eq 0 ]] || { usage; exit 1; }

    for cmd in bwa samtools; do
        command -v "$cmd" >/dev/null 2>&1 || {
            echo "[ERROR] 找不到命令 $cmd —— 是否忘了 conda activate ngs_ug_base ?" >&2
            exit 1
        }
    done
    if [[ "$ALIGNER" == "bowtie2" ]]; then
        command -v bowtie2 >/dev/null 2>&1 || {
            echo "[ERROR] 找不到 bowtie2" >&2; exit 1; }
    fi
}

# ---------- 建索引（已存在则跳过） ----------
build_index() {
    if [[ "$ALIGNER" == "bwa" ]]; then
        if [[ -s "${REF}.bwt" ]]; then
            echo "[INFO] BWA 索引已存在，跳过 bwa index"
        else
            echo "[INFO] 构建 BWA 索引（产出 .amb/.ann/.bwt/.pac/.sa 五个文件）"
            bwa index "$REF"
        fi
    else
        local prefix="${REF%.fa}"; prefix="${prefix%.fasta}"; prefix="${prefix}_bt2"
        if [[ -s "${prefix}.1.bt2" ]]; then
            echo "[INFO] Bowtie2 索引已存在，跳过 bowtie2-build"
        else
            echo "[INFO] 构建 Bowtie2 索引（产出 6 个 .bt2 文件），前缀 ${prefix}"
            bowtie2-build --threads "$THREADS" "$REF" "$prefix"
        fi
        BT2_PREFIX="$prefix"
    fi
}

# ---------- 比对 + 排序 + 索引 ----------
align_sort() {
    local sorted="${OUTDIR}/${SAMPLE}.sorted.bam"
    local rg="@RG\tID:${SAMPLE}_L001\tSM:${SAMPLE}\tPL:${PLATFORM}\tLB:${SAMPLE}_lib1\tPU:L001"

    if [[ "$ALIGNER" == "bwa" ]]; then
        echo "[INFO] bwa mem 比对（-M 兼容 Picard；-K 固定分批以保证结果可复现）"
        # -R 用双引号包裹变量，rg 变量里的 \t 由 bwa 自己解释（讲义 ⑨-E4）
        bwa mem -t "$THREADS" -M -K 10000000 -R "$rg" \
            "$REF" "$FQ1" "$FQ2" 2> "${OUTDIR}/logs/bwa_mem.log" \
          | samtools sort -@ "$THREADS" -m "$SORT_MEM" \
                -T "${OUTDIR}/tmp_${SAMPLE}_$$" -o "$sorted" -
    else
        echo "[INFO] bowtie2 比对（--very-sensitive）"
        bowtie2 -p "$THREADS" -x "$BT2_PREFIX" -1 "$FQ1" -2 "$FQ2" \
            --very-sensitive -X 800 \
            --rg-id "${SAMPLE}_L001" --rg "SM:${SAMPLE}" --rg "PL:${PLATFORM}" \
            2> "${OUTDIR}/logs/bowtie2.log" \
          | samtools sort -@ "$THREADS" -m "$SORT_MEM" \
                -T "${OUTDIR}/tmp_${SAMPLE}_$$" -o "$sorted" -
    fi

    samtools index -@ "$THREADS" "$sorted"
    echo "[INFO] 排序 BAM 与索引已生成：$sorted"
    verify_bam "$sorted"
}

# ---------- 产物验收：只靠 set -euo pipefail 不够（UP-032）----------
# 上游在写出有效表头后死亡，samtools sort 仍可能 rc=0 地产出 0 条记录的 BAM，
# 下游统计照样跑完。故补三项：quickcheck（EOF 块/表头）、非空、FASTQ 模板数↔BAM 主记录数对账。
verify_bam() {
    local bam="$1" n_fq n_primary
    samtools quickcheck -v "$bam" || { echo "[FATAL] BAM 损坏或被截断：$bam" >&2; exit 1; }
    # -F 0x900：排除 secondary/supplementary，只数主记录；双端每个模板应有 2 条
    n_primary=$(samtools view -c -F 0x900 "$bam")
    [[ "$n_primary" -gt 0 ]] || { echo "[FATAL] BAM 无任何记录：$bam（查 logs/ 下比对日志）" >&2; exit 1; }
    n_fq=$(( $(gzip -cdf "$FQ1" | wc -l) / 4 ))
    if [[ "$n_primary" -ne $(( 2 * n_fq )) ]]; then
        echo "[FATAL] 对账失败：R1 模板 ${n_fq} 个 → 期望主记录 $(( 2 * n_fq ))，BAM 实有 ${n_primary}" >&2
        echo "        比对或排序中途中断；不要用这份 BAM 做下游统计" >&2
        exit 1
    fi
    echo "[INFO] 验收通过：quickcheck OK；主记录 ${n_primary} = 2 × ${n_fq} 模板"
}

# ---------- 统计 ----------
run_stats() {
    local bam="$1" tag="$2"
    samtools flagstat -@ "$THREADS" "$bam" > "${OUTDIR}/logs/${tag}.flagstat.txt"
    samtools idxstats "$bam"              > "${OUTDIR}/logs/${tag}.idxstats.txt"
    samtools coverage "$bam"              > "${OUTDIR}/logs/${tag}.coverage.txt"
    # -a：深度为 0 的位点也输出，否则平均深度会被系统性高估（讲义 5.6）
    samtools depth -a "$bam" \
      | awk -v OUT="${OUTDIR}/logs/${tag}.depth_summary.txt" \
            '{s+=$3; if($3==0) z++}
             END {if (NR==0) {print "[FATAL] samtools depth 无输出" > "/dev/stderr"; exit 1}
                  printf "mean_depth\t%.2f\nzero_depth_sites\t%d\nzero_depth_pct\t%.4f\n",
                  s/NR, z, z/NR*100 > OUT}'
    echo "[INFO] 统计完成：${OUTDIR}/logs/${tag}.*"
}

# ---------- PCR 重复标记 + 去重前后计数 ----------
mark_duplicates() {
    local sorted="${OUTDIR}/${SAMPLE}.sorted.bam"
    local markdup="${OUTDIR}/${SAMPLE}.markdup.bam"
    local tmp="${OUTDIR}/tmp_md_${SAMPLE}_$$"

    echo "[INFO] PCR 重复标记：collate -> fixmate -m -> sort -> markdup"
    samtools collate -@ "$THREADS" -o "${tmp}.collate.bam" "$sorted" "${tmp}_c"
    # -m 不能省，否则 markdup 报 no ms score tag（讲义 ⑨-E7）
    samtools fixmate -m -@ "$THREADS" "${tmp}.collate.bam" "${tmp}.fixmate.bam"
    samtools sort -@ "$THREADS" -m "$SORT_MEM" -T "${tmp}_s" \
        -o "${tmp}.possort.bam" "${tmp}.fixmate.bam"
    # 只标记不删除：标记可逆，下游用 -F 1024 过滤即可
    samtools markdup -@ "$THREADS" -s "${tmp}.possort.bam" "$markdup" \
        2> "${OUTDIR}/logs/markdup.stats"
    samtools index -@ "$THREADS" "$markdup"
    rm -f "${tmp}".*.bam

    local total dedup dup
    total=$(samtools view -c              "$markdup")
    dedup=$(samtools view -c -F 1024      "$markdup")
    dup=$(samtools view -c -f 1024        "$markdup")
    {
        printf "total_records\t%s\n" "$total"
        printf "after_dedup(-F 1024)\t%s\n" "$dedup"
        printf "duplicates(-f 1024)\t%s\n" "$dup"
        awk -v d="$dup" -v t="$total" 'BEGIN{printf "duplicate_rate\t%.4f%%\n", (t>0? d/t*100 : 0)}'
    } > "${OUTDIR}/logs/dup_counts.txt"
    echo "[INFO] 去重前后计数写入 ${OUTDIR}/logs/dup_counts.txt"
    echo "[HINT] 该文件里的 duplicates 应与 logs/markdup.stats 的 DUPLICATE TOTAL 一致（自查用）"
}

main() {
    check_inputs
    mkdir -p "${OUTDIR}/logs"
    echo "[INFO] 样本=${SAMPLE} 比对器=${ALIGNER} 线程=${THREADS} 排序内存/线程=${SORT_MEM}"
    build_index
    align_sort
    run_stats "${OUTDIR}/${SAMPLE}.sorted.bam" "${SAMPLE}"
    if [[ $DO_MARKDUP -eq 1 ]]; then
        mark_duplicates
        run_stats "${OUTDIR}/${SAMPLE}.markdup.bam" "${SAMPLE}.markdup"
    fi
    echo "[DONE] 全部完成，结果在 ${OUTDIR}/ ，日志与统计在 ${OUTDIR}/logs/"
}

main "$@"
