#!/bin/bash
# ============================================
# 脚本名称：03_parse_fastq_stats.sh
# 功能描述：识别测序文件格式（FASTA / FASTQ、是否 gzip），统计 read 数、
#           碱基总量、长度分布与 N50，并按给定基因组大小估算测序深度。
#           FASTQ 还会解码前若干条 read 的 Phred+33 质量字符。
# 对应单元：本科 u03（测序原理与数据格式）
# 运行环境：ngs_ug_base（本脚本只用 bash/awk/zcat，无额外依赖）
# 作者：王运生
# 日期：2026-08-29
# ============================================

set -euo pipefail

usage() {
    cat <<'USAGE'
用法：
    bash 03_parse_fastq_stats.sh <序列文件> [基因组大小] [解码条数]

参数：
    <序列文件>    .fq / .fastq / .fq.gz / .fastq.gz / .fa / .fasta / .fa.gz
    [基因组大小]  用于估算深度，支持 4m / 4M / 4000000 写法，默认 4m
    [解码条数]    FASTQ 质量字符解码的 read 条数，默认 2；写 0 表示不解码

示例：
    bash 03_parse_fastq_stats.sh /data/lab/ngs/reads.fa 4m
    bash 03_parse_fastq_stats.sh sample_R1.fq.gz 4m 3
USAGE
}

if [[ $# -lt 1 ]]; then
    usage
    exit 1
fi

INPUT="$1"
GENOME_SIZE_RAW="${2:-4m}"
DECODE_N="${3:-2}"

[[ -f "$INPUT" ]] || { echo "[ERROR] 文件不存在：$INPUT" >&2; exit 2; }

# ---- 1. 把 4m / 4M / 4000000 统一换算成碱基数 ----
to_bases() {
    local raw="$1"
    local num unit
    num="${raw%[a-zA-Z]}"
    unit="${raw#"$num"}"
    case "${unit,,}" in
        k) awk -v n="$num" 'BEGIN{printf "%.0f", n*1000}' ;;
        m) awk -v n="$num" 'BEGIN{printf "%.0f", n*1000000}' ;;
        g) awk -v n="$num" 'BEGIN{printf "%.0f", n*1000000000}' ;;
        "") printf "%s" "$num" ;;
        *) echo "[ERROR] 无法识别的基因组大小写法：$raw" >&2; exit 2 ;;
    esac
}
GENOME_SIZE="$(to_bases "$GENOME_SIZE_RAW")"

# ---- 2. 判断是否 gzip：看文件magic number，而不是看文件名后缀 ----
#     文件名会骗人（reads.fa.gz 可能根本没压缩），magic number 不会。
MAGIC="$(head -c 2 "$INPUT" | od -An -tx1 | tr -d ' \n')"
if [[ "$MAGIC" == "1f8b" ]]; then
    READER=(zcat)
    COMPRESSED="是（gzip）"
else
    READER=(cat)
    COMPRESSED="否（纯文本）"
fi

# ---- 3. 判断 FASTA 还是 FASTQ：看第一个非空行的首字符 ----
# peek：安全地取输入流的前 n 行。
#   head 读够就退出，会给上游的 zcat 送一个 SIGPIPE；在 `set -o pipefail` 下
#   整条管道的退出码会变成 141，再被 `set -e` 当成失败，脚本就在这里静默死掉。
#   所以这里在子 shell 内局部关掉 pipefail。
peek() {
    set +o pipefail
    "${READER[@]}" "$INPUT" 2>/dev/null | head -n "$1"
    set -o pipefail
}

FIRST_CHAR="$(peek 1 | cut -c1)"
case "$FIRST_CHAR" in
    ">") FORMAT="FASTA" ;;
    "@") FORMAT="FASTQ" ;;
    *)   echo "[ERROR] 首行既不以 '>' 也不以 '@' 开头，不是 FASTA/FASTQ：$INPUT" >&2
         "${READER[@]}" "$INPUT" | head -2 >&2
         exit 3 ;;
esac

echo "=============================================="
echo "文件            : $INPUT"
echo "是否压缩        : $COMPRESSED"
echo "推断格式        : $FORMAT"
echo "基因组大小(估算): ${GENOME_SIZE_RAW} = ${GENOME_SIZE} bp"
echo "=============================================="

# ---- 4. FASTQ 完整性：逐条校验，放在第 5 步主统计里同一遍完成 ----
#     只查「总行数整除 4」不够：少一行质量、+ 行错位、序列与质量不等长等损坏
#     都能整除 4，旧版会照常打印「完成」（UP-028）。现逐条校验 @ / + / 等长，
#     发现第一处损坏即报行号并以非零退出（退出码 5）。

# ---- 5. 主统计：read 数、碱基数、长度分布、N50 ----
#     分两步做：第一步只吐出每条序列的长度，第二步排序后统计。
#     不用 gawk 专有的 asort()，保证在集群的 mawk 上也能跑。
LEN_TMP="$(mktemp)"
trap 'rm -f "$LEN_TMP"' EXIT

"${READER[@]}" "$INPUT" | awk -v fmt="$FORMAT" '
    fmt == "FASTA" {
        if (substr($0,1,1) == ">") { if (have) print cur; have = 1; cur = 0; next }
        cur += length($0); next
    }
    fmt == "FASTQ" {
        k = NR % 4
        if (k == 1 && substr($0,1,1) != "@") { bad = "第 " NR " 行应为 @ 开头的标题行"; exit 5 }
        if (k == 2) { slen = length($0); print slen }
        if (k == 3 && substr($0,1,1) != "+") { bad = "第 " NR " 行应为 + 分隔行"; exit 5 }
        if (k == 0 && length($0) != slen) {
            bad = "第 " NR " 行质量长度 " length($0) " ≠ 序列长度 " slen; exit 5
        }
        next
    }
    END {
        if (bad != "") { print "[ERROR] FASTQ 损坏：" bad > "/dev/stderr"; exit 5 }
        if (fmt == "FASTQ" && NR % 4 != 0) {
            print "[ERROR] FASTQ 损坏：总行数 " NR " 不是 4 的整数倍（末条记录不完整/文件被截断）" > "/dev/stderr"
            exit 5
        }
        if (fmt == "FASTA" && have) print cur
    }
' | sort -n > "$LEN_TMP"

awk -v gsize="$GENOME_SIZE" '
    { len[NR] = $1; total += $1 }
    END {
        n = NR
        if (n == 0) { print "[ERROR] 没有解析到任何序列" > "/dev/stderr"; exit 4 }
        # N50：按长度从大到小累加，累计到总长一半时那条序列的长度
        half = total / 2; acc = 0; n50 = 0
        for (i = n; i >= 1; i--) { acc += len[i]; if (acc >= half) { n50 = len[i]; break } }
        printf "序列条数        : %d\n", n
        printf "碱基总量        : %d bp (%.2f Mb)\n", total, total/1000000
        printf "最短 / 最长     : %d / %d bp\n", len[1], len[n]
        printf "平均长度        : %.1f bp\n", total / n
        printf "中位长度        : %d bp\n", len[int((n+1)/2)]
        printf "N50             : %d bp\n", n50
        printf "估算测序深度    : %.1f X  (碱基总量 / 基因组大小)\n", total / gsize
    }
' "$LEN_TMP"

# ---- 6. FASTQ 质量字符解码（教学用：把字符还原成 Q 值与错误率） ----
if [[ "$FORMAT" == "FASTQ" && "$DECODE_N" -gt 0 ]]; then
    echo "----------------------------------------------"
    echo "前 ${DECODE_N} 条 read 的 Phred+33 解码（Q = ASCII - 33，P = 10^(-Q/10)）"
    peek $((DECODE_N * 4)) | awk '
        BEGIN { for (i = 33; i <= 126; i++) ord[sprintf("%c", i)] = i }
        (NR - 1) % 4 == 0 { printf "\n[read] %s\n", $0 }
        (NR - 2) % 4 == 0 { seq = $0 }
        (NR - 0) % 4 == 0 {
            qsum = 0
            printf "  pos  base  qchar  ASCII  Q   P(err)\n"
            for (i = 1; i <= length($0); i++) {
                ch = substr($0, i, 1); q = ord[ch] - 33; qsum += q
                if (i <= 10)
                    printf "  %-4d %-5s %-6s %-6d %-3d %.5f\n", i, substr(seq,i,1), ch, ord[ch], q, 10^(-q/10)
            }
            if (length($0) > 10) printf "  ...（只显示前 10 个碱基，共 %d bp）\n", length($0)
            printf "  该 read 平均 Q = %.1f\n", qsum / length($0)
        }
    '
fi

echo "=============================================="
echo "完成。把上面的『序列条数 / 碱基总量 / N50 / 估算深度』抄进"
echo "实践报告模板 §2.3『数据量和质量评估』。"
