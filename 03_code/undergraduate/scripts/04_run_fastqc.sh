#!/bin/bash
# ============================================
# 脚本名称：04_run_fastqc.sh
# 功能描述：短读长质控三件套（FastQC → fastp → FastQC → MultiQC）；
#           另提供长读长模式（--long），跳过 FastQC，改为读长分布 / N50 /
#           总产出统计——PacBio、Nanopore 数据不能按短读长的方式判读。
# 对应单元：本科 u04（质量控制与数据预处理）
# 运行环境：conda activate ngs_ug_base（fastqc / fastp / multiqc）
# 作者：王运生
# 日期：2026-08-29
# ============================================

set -euo pipefail

usage() {
    cat <<'USAGE'
用法：
    短读长： bash 04_run_fastqc.sh <输入目录> <输出目录> [线程数]
    长读长： bash 04_run_fastqc.sh --long <序列文件> <输出目录> [基因组大小]

短读长模式做四件事：
    1) 对 <输入目录>/*.f*q.gz 跑 FastQC（raw）
    2) 用 fastp 去接头 + 质量修剪 + 长度过滤
    3) 对清洗后数据再跑一次 FastQC（clean）
    4) 用 MultiQC 把所有报告汇总成一张网页

长读长模式做一件事：
    统计读长分布 / N50 / 总碱基 / 估算深度，并给出一段可直接抄进
    报告模板 §2.3 的质量结论草稿。

示例：
    bash 04_run_fastqc.sh data/raw results/qc 4
    bash 04_run_fastqc.sh --long /data/lab/ngs/reads.fa results/qc_long 4m
USAGE
}

# ---------------------------------------------------------------
# 长读长模式
# ---------------------------------------------------------------
run_long_mode() {
    local input="$1" outdir="$2" gsize_raw="${3:-4m}"
    [[ -f "$input" ]] || { echo "[ERROR] 文件不存在：$input" >&2; exit 2; }
    mkdir -p "$outdir"

    local here script
    here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    script="${here}/03_parse_fastq_stats.sh"

    echo "==> 长读长质控：不跑 FastQC，改看读长分布与产出量"
    if [[ -f "$script" ]]; then
        bash "$script" "$input" "$gsize_raw" 0 | tee "${outdir}/longread_stats.txt"
    else
        echo "[WARN] 找不到 ${script}，改用内联统计" >&2
        awk '/^>/ {if (h) print c; h=1; c=0; next} {c+=length($0)} END{if(h) print c}' \
            "$input" | sort -n > "${outdir}/read_lengths.txt"
        awk '{l[NR]=$1; t+=$1} END{
                half=t/2; acc=0; for(i=NR;i>=1;i--){acc+=l[i]; if(acc>=half){n50=l[i]; break}}
                printf "reads=%d total=%d bp max=%d N50=%d\n", NR, t, l[NR], n50
             }' "${outdir}/read_lengths.txt" | tee "${outdir}/longread_stats.txt"
    fi

    # 读长直方图（纯文本，便于在没有图形界面的集群上直接看）
    echo "==> 读长分布直方图（每格 = 该区间的 read 条数）"
    awk '/^>/ {if (h) print c; h=1; c=0; next} {c+=length($0)} END{if(h) print c}' "$input" \
        | awk '{ bin = int($1/1000); cnt[bin]++; if (bin > maxbin) maxbin = bin }
               END {
                   for (b = 0; b <= maxbin; b++) {
                       if (cnt[b] == 0) continue
                       printf "%5d-%5d kb : %8d  ", b, b+1, cnt[b]
                       bars = int(cnt[b] / 50) + 1
                       if (bars > 60) bars = 60
                       for (i = 0; i < bars; i++) printf "#"
                       printf "\n"
                   }
               }' | tee "${outdir}/read_length_hist.txt"

    cat <<'NOTE'

----------------------------------------------------------------
长读长数据的判读要点（写进报告模板 §2.3 时按这几条组织）：
  1. 不要贴 FastQC 的 per-base quality 曲线——长读长的错误是随机分布的，
     不像 Illumina 那样在 3' 端系统性衰减，这条曲线读不出信息。
  2. 该看：总碱基量、估算深度（细菌基因组一般要求 ≥ 50X）、
     read N50（PacBio CLR 常见 10–20 kb，HiFi 常见 15–25 kb）、最长 read。
  3. 该判断：深度够不够、读长能不能跨过预期的重复区（rRNA 操纵子约 5 kb）。
  4. 不要对长读长做短读长式的质量修剪——Canu / Flye 自带纠错环节，
     外部修剪反而会破坏组装器依赖的读长优势。
----------------------------------------------------------------
NOTE
}

# ---------------------------------------------------------------
# 短读长模式
# ---------------------------------------------------------------
run_short_mode() {
    local indir="$1" outdir="$2" threads="${3:-4}"
    [[ -d "$indir" ]] || { echo "[ERROR] 输入目录不存在：$indir" >&2; exit 2; }

    local raw_dir="${outdir}/fastqc_raw"
    local clean_dir="${outdir}/clean"
    local cleanqc_dir="${outdir}/fastqc_clean"
    local report_dir="${outdir}/fastp_reports"
    mkdir -p "$raw_dir" "$clean_dir" "$cleanqc_dir" "$report_dir"

    # ---- 1. 原始数据 FastQC ----
    #   -t 并行线程数（一个线程处理一个文件，给多了也不会更快）
    #   -o 输出目录，必须已存在，FastQC 不会自动创建
    echo "==> [1/4] FastQC on raw data"
    shopt -s nullglob
    local raw_files=("$indir"/*.fq.gz "$indir"/*.fastq.gz "$indir"/*.fq "$indir"/*.fastq)
    shopt -u nullglob
    if [[ ${#raw_files[@]} -eq 0 ]]; then
        echo "[ERROR] ${indir} 下没有找到 .fq/.fastq(.gz) 文件" >&2
        exit 3
    fi
    fastqc -t "$threads" -o "$raw_dir" "${raw_files[@]}"

    # ---- 2. fastp 清洗 ----
    #   不开 --cut_front：5' 端质量通常很高，开了反而误切好碱基（讲义 l0_05 §4 / 错误 10）
    #   单端必须显式给接头：SE 没有双端重叠可借，自动检测常报 No adapter detected
    #   而原样放过接头（UP-030 实测 30% 污染零修剪）。默认 Illumina TruSeq/Nextera 通用前缀，
    #   其他文库用环境变量 ADAPTER_SE 覆盖。
    local adapter_se="${ADAPTER_SE:-AGATCGGAAGAGC}"
    echo "==> [2/4] fastp trimming"
    local f base r2 n_expect=0
    for f in "${raw_files[@]}"; do
        base="$(basename "$f")"
        base="${base%%.*}"          # 去掉 .fq.gz / .fastq.gz 后缀
        base="${base%_R1}"          # 去掉 _R1，否则会拼出 sampleA_R1_R1.clean.fq.gz
        # 双端约定：*_R1* 与 *_R2* 配对；找不到 R2 就按单端处理
        r2="${f/_R1/_R2}"
        if [[ "$f" == *_R1* && -f "$r2" ]]; then
            n_expect=$((n_expect + 2))
            fastp \
                -i "$f" -I "$r2" \
                -o "${clean_dir}/${base}_R1.clean.fq.gz" \
                -O "${clean_dir}/${base}_R2.clean.fq.gz" \
                --detect_adapter_for_pe \
                --cut_tail --cut_window_size 4 --cut_mean_quality 20 \
                --qualified_quality_phred 15 --unqualified_percent_limit 40 \
                --length_required 50 \
                --thread "$threads" \
                --html "${report_dir}/${base}.fastp.html" \
                --json "${report_dir}/${base}.fastp.json"
        elif [[ "$f" != *_R2* ]]; then
            n_expect=$((n_expect + 1))
            fastp \
                -i "$f" -o "${clean_dir}/${base}.clean.fq.gz" \
                --adapter_sequence "$adapter_se" \
                --cut_tail --cut_window_size 4 --cut_mean_quality 20 \
                --qualified_quality_phred 15 --unqualified_percent_limit 40 \
                --length_required 50 \
                --thread "$threads" \
                --html "${report_dir}/${base}.fastp.html" \
                --json "${report_dir}/${base}.fastp.json"
        fi
    done

    # ---- 3. 清洗后 FastQC ----
    # 只认本次运行该产出的文件：按输入逐个推出期望文件名再核对，
    # 不 glob 整个目录——否则旧运行残留的报告会被当成本次结果汇总（UP-030）
    echo "==> [3/4] FastQC on clean data"
    local clean_files=() fastp_json=() raw_zips=() g b
    for f in "${raw_files[@]}"; do
        b="$(basename "$f")"; b="${b%.gz}"; b="${b%.fastq}"; b="${b%.fq}"
        raw_zips+=("${raw_dir}/${b}_fastqc.zip")
        [[ "$f" == *_R2* ]] && continue   # R2 随 R1 计；孤立 R2 与 fastp 分支一致不处理
        base="$(basename "$f")"; base="${base%%.*}"; base="${base%_R1}"
        fastp_json+=("${report_dir}/${base}.fastp.json")
        if [[ "$f" == *_R1* && -f "${f/_R1/_R2}" ]]; then
            clean_files+=("${clean_dir}/${base}_R1.clean.fq.gz" "${clean_dir}/${base}_R2.clean.fq.gz")
        else
            clean_files+=("${clean_dir}/${base}.clean.fq.gz")
        fi
    done
    for g in "${raw_zips[@]}" "${fastp_json[@]}" "${clean_files[@]}"; do
        [[ -s "$g" ]] || { echo "[ERROR] 缺少本次应产出的文件：$g" >&2; exit 4; }
    done
    [[ ${#clean_files[@]} -eq $n_expect ]] || {
        echo "[ERROR] 清洗后文件数 ${#clean_files[@]} ≠ 期望 ${n_expect}" >&2; exit 4; }
    fastqc -t "$threads" -o "$cleanqc_dir" "${clean_files[@]}"
    local clean_zips=()
    for g in "${clean_files[@]}"; do
        b="$(basename "$g" .fq.gz)"; clean_zips+=("${cleanqc_dir}/${b}_fastqc.zip")
        [[ -s "${clean_zips[-1]}" ]] || { echo "[ERROR] 缺少 ${clean_zips[-1]}" >&2; exit 4; }
    done
    echo "[INFO] 产物核对通过：raw FastQC ${#raw_zips[@]}、fastp ${#fastp_json[@]}、clean ${#clean_files[@]}"

    # ---- 4. MultiQC 汇总 ----
    #   --force 覆盖旧报告；不加会生成 multiqc_report_1.html 这类带后缀的副本
    #   只喂本次的报告文件，而不是整个 $outdir（避免汇总进旧样本）
    echo "==> [4/4] MultiQC summary"
    multiqc --force -o "$outdir" -n multiqc_report.html \
        "${raw_zips[@]}" "${clean_zips[@]}" "${fastp_json[@]}"

    echo
    echo "完成。请打开："
    echo "  清洗前后对比 : ${outdir}/multiqc_report.html"
    echo "  单样本细节   : ${report_dir}/*.fastp.html"
}

# ---------------------------------------------------------------
main() {
    if [[ $# -lt 2 ]]; then usage; exit 1; fi
    if [[ "$1" == "--long" ]]; then
        shift
        [[ $# -ge 2 ]] || { usage; exit 1; }
        run_long_mode "$@"
    else
        run_short_mode "$@"
    fi
}

main "$@"
