#!/bin/bash
# ============================================
# 脚本名称：01_seq_stats.sh
# 功能描述：统计 FASTA / FASTQ（可为 .gz）的序列条数、总碱基数与长度分布
#           并按给定基因组大小估算测序深度
#           对应讲义 u01 §⑤ 步骤 3（管道与重定向）；产出可直接填进报告模板 §2
# 配套讲义：02_lectures/undergraduate/unit01_linux_conda/01_linux_conda_lecture.md
# 作者：王运生
# 日期：2026-08-29
# ============================================

set -euo pipefail

GENOME_SIZE=4000000     # 默认按 4 Mb 细菌基因组估算深度，可用 -g 覆盖

usage() {
    cat <<'USAGE'
用法: bash 01_seq_stats.sh [-g 基因组大小bp] <序列文件>

  支持 .fa / .fasta / .fq / .fastq，以及它们的 .gz 压缩版本
  -g  基因组大小（bp），默认 4000000（4 Mb）

示例:
  bash 01_seq_stats.sh reads.fa
  bash 01_seq_stats.sh -g 4600000 sample_R1.fq.gz
USAGE
}

while getopts ":g:h" opt; do
    case "${opt}" in
        g) GENOME_SIZE="${OPTARG}" ;;
        h) usage; exit 0 ;;
        \?) echo "未知选项: -${OPTARG}" >&2; usage; exit 1 ;;
        :)  echo "选项 -${OPTARG} 需要参数" >&2; exit 1 ;;
    esac
done
shift $((OPTIND - 1))

if [[ $# -lt 1 ]]; then
    usage; exit 1
fi
INPUT="$1"

if [[ ! -f "${INPUT}" ]]; then
    echo "错误：文件不存在或是断链的软链接 -> ${INPUT}" >&2
    echo "提示：用 ls -lL 检查软链接是否指向真实存在的文件（见讲义 ⑥ 6.2）" >&2
    exit 1
fi

# 压缩文件用 zcat 读，未压缩用 cat —— 统一成一个"读取命令"
reader() {
    case "${INPUT}" in
        *.gz) zcat "${INPUT}" ;;
        *)    cat  "${INPUT}" ;;
    esac
}

# 判断格式：FASTA 以 > 开头，FASTQ 以 @ 开头
detect_format() {
    local first
    first="$(reader | head -n 1 | cut -c1)"
    case "${first}" in
        ">") echo "fasta" ;;
        "@") echo "fastq" ;;
        *)   echo "unknown" ;;
    esac
}

main() {
    local fmt
    fmt="$(detect_format)"
    echo "=========================================="
    echo " 序列文件统计"
    echo "=========================================="
    echo "文件     : ${INPUT}"
    echo "格式     : ${fmt}"
    echo "基因组大小: ${GENOME_SIZE} bp（用于估算深度）"
    echo "------------------------------------------"

    case "${fmt}" in
        fasta)
            # 一次 awk 扫完：累计序列条数与每条序列长度，避免多次读大文件
            reader | awk -v gsize="${GENOME_SIZE}" '
                /^>/ { if (len > 0) { record(len); len = 0 } n++; next }
                     { len += length($0) }
                function record(l) {
                    total += l
                    if (min == 0 || l < min) min = l
                    if (l > max) max = l
                }
                END {
                    if (len > 0) record(len)
                    printf "序列条数 : %d\n", n
                    printf "总碱基数 : %d bp (%.2f Mb)\n", total, total/1e6
                    printf "平均长度 : %.1f bp\n", (n > 0 ? total/n : 0)
                    printf "最长 / 最短: %d / %d bp\n", max, min
                    printf "估算深度 : %.1f X\n", total/gsize
                }'
            ;;
        fastq)
            # FASTQ 每条记录 4 行：第 2 行是序列
            reader | awk -v gsize="${GENOME_SIZE}" '
                NR % 4 == 2 {
                    n++; l = length($0); total += l
                    if (min == 0 || l < min) min = l
                    if (l > max) max = l
                }
                END {
                    printf "read 数  : %d\n", n
                    printf "总碱基数 : %d bp (%.2f Mb)\n", total, total/1e6
                    printf "平均读长 : %.1f bp\n", (n > 0 ? total/n : 0)
                    printf "最长 / 最短: %d / %d bp\n", max, min
                    printf "估算深度 : %.1f X\n", total/gsize
                }'
            ;;
        *)
            echo "无法识别格式：首字符既不是 '>' 也不是 '@'。" >&2
            echo "请先 head -n 4 ${INPUT} 看清文件长什么样。" >&2
            exit 1
            ;;
    esac
    echo "------------------------------------------"
    echo "说明：估算深度 = 总碱基数 / 基因组大小。深度过低会直接影响 u06 的组装质量。"
}

main "$@"
