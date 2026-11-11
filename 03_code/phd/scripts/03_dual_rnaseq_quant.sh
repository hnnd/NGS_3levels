#!/bin/bash
#$ -S /bin/bash
#$ -N p03_dual_quant
#$ -cwd
#$ -j y
#$ -pe smp 16
#$ -l h_vmem=64G
# ============================================================
# 脚本名称：03_dual_rnaseq_quant.sh
# 功能描述：p03 宿主-病原互作组学 —— 双参考构建 → 竞争性比对 → 按前缀拆分 → 生物量曲线
# 作者：王运生
# 日期：2026-08-29
# 提交方式：qsub 03_dual_rnaseq_quant.sh     【禁止在登录节点直接 bash 运行】
# 配套讲义：02_lectures/phd/topic03_host_pathogen/03_host_pathogen_lecture.md §5.2–5.3
# ============================================================
#
# 设计要点（讲义 §4.2–4.4）：
#   1) 合并参考竞争性比对，而不是"先比宿主、剩下的比病原"——顺序过滤会把同源区
#      read 系统性归给先比的物种，且下游看不出来。
#   2) --outFilterMultimapNmax 1 只保留唯一比对：两侧都命中的 read 在此被剔除。
#      被剔除比例必须随时间点报告（见 qc/biomass.tsv 的 ambiguous 列）。
#   3) 本脚本只出两份**分开的**计数矩阵，绝不合并——合并后算 TPM 是系统性错误。
#   4) 未接种对照样本的"病原占比"即本流程的交叉比对本底，理论值 0，实测值写进方法学。

set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_interaction

for tool in seqkit samtools STAR awk; do
    command -v "${tool}" >/dev/null || { echo "[FATAL] ${tool} 不在 PATH，环境没激活成功"; exit 1; }
done

# ---------------------------------------------------------------- 参数
HOST_FA="${HOST_FA:?必须指定 HOST_FA=宿主基因组 fasta}"            # 【主线数据待定】
HOST_GTF="${HOST_GTF:?必须指定 HOST_GTF=宿主注释 gtf}"
PATH_FA="${PATH_FA:?必须指定 PATH_FA=病原基因组 fasta}"
PATH_GTF="${PATH_GTF:?必须指定 PATH_GTF=病原注释 gtf}"
SAMPLES="${SAMPLES:?必须指定 SAMPLES=samples.tsv（列：sample R1 R2 treatment time；单端 R2 写 -）}"
# 主线 PRJNA661210 是单端数据：R2 列写 - 或 NA 即按单端比对（UP-053）。
# 不能留空：IFS 为制表符时 read 会合并连续空字段，treatment 会错位进 R2 列
OUTDIR="${OUTDIR:-./p03_dual}"
READLEN="${READLEN:-150}"                 # --sjdbOverhang = 读长 - 1
THREADS="${NSLOTS:-16}"
GENOME_RAM="${GENOME_RAM:-60000000000}"   # 必须小于 qsub 的 h_vmem，否则被 SGE 杀掉
HOST_PFX="HOST_"
PATH_PFX="PATH_"
STRAND_COL="${STRAND_COL:-4}"             # ReadsPerGene.out.tab：2=无链 3=正链 4=反链
                                          # 选错会得到一份几乎全是噪声的矩阵（讲义 §5.3）

REF="${OUTDIR}/ref"; IDX="${OUTDIR}/dual_idx"; ALN="${OUTDIR}/star"
CNT_H="${OUTDIR}/counts/host"; CNT_P="${OUTDIR}/counts/path"; QC="${OUTDIR}/qc"
mkdir -p "${REF}" "${ALN}" "${CNT_H}" "${CNT_P}" "${QC}"

# ---------------------------------------------------------------- 步骤一：加前缀的双参考
if [[ ! -s "${REF}/dual.fa.fai" ]]; then
    echo "=== [1/4] 构建加前缀的双参考 ==="
    seqkit replace -p '^' -r "${HOST_PFX}" "${HOST_FA}" > "${REF}/host.pfx.fa"
    seqkit replace -p '^' -r "${PATH_PFX}" "${PATH_FA}" > "${REF}/path.pfx.fa"
    cat "${REF}/host.pfx.fa" "${REF}/path.pfx.fa" > "${REF}/dual.fa"
    # GTF 第 1 列必须与 FASTA 序列名同步改；只改一边是最高频的错（讲义 ⑨-E1）
    awk -v p="${HOST_PFX}" 'BEGIN{OFS="\t"} /^#/{print; next} {$1=p $1; print}' "${HOST_GTF}" \
        >  "${REF}/dual.gtf"
    awk -v p="${PATH_PFX}" 'BEGIN{OFS="\t"} /^#/{next} {$1=p $1; print}' "${PATH_GTF}" \
        >> "${REF}/dual.gtf"
    # 重名必须自己查：samtools faidx 与 STAR 遇重名都不报错（faidx 只警告并取第一条），
    # 结果静默错位（UP-053 / 讲义 ⑨-E1）
    grep '^>' "${REF}/dual.fa" | awk '{print $1}' | sort | uniq -d > "${QC}/dup_seqnames.txt"
    [[ -s "${QC}/dup_seqnames.txt" ]] && {
        echo "[FATAL] 双参考中有重名序列，见 ${QC}/dup_seqnames.txt"; exit 1; }
    samtools faidx "${REF}/dual.fa"
    # 一致性自检：GTF 用到的序列名必须都在 FASTA 里
    comm -23 <(awk '!/^#/{print $1}' "${REF}/dual.gtf" | sort -u) \
             <(cut -f1 "${REF}/dual.fa.fai" | sort -u) > "${QC}/gtf_not_in_fasta.txt"
    [[ -s "${QC}/gtf_not_in_fasta.txt" ]] && {
        echo "[FATAL] GTF 中有 FASTA 里不存在的序列名，见 ${QC}/gtf_not_in_fasta.txt"; exit 1; }
fi

# ---------------------------------------------------------------- 步骤二：建索引
if [[ ! -s "${IDX}/SA" ]]; then
    echo "=== [2/4] STAR 建双参考索引（内存需求远高于单物种）==="
    mkdir -p "${IDX}"
    STAR --runMode genomeGenerate --genomeDir "${IDX}" \
         --genomeFastaFiles "${REF}/dual.fa" --sjdbGTFfile "${REF}/dual.gtf" \
         --sjdbOverhang $((READLEN - 1)) --runThreadN "${THREADS}" \
         --limitGenomeGenerateRAM "${GENOME_RAM}" \
         --outFileNamePrefix "${IDX}/"
fi

# ---------------------------------------------------------------- 步骤三：竞争性比对 + 拆分
echo "=== [3/4] 竞争性比对与按前缀拆分 ==="
while IFS=$'\t' read -r sample r1 r2 _rest; do
    [[ -z "${sample}" || "${sample}" == \#* || "${sample}" == "sample" ]] && continue
    tab="${ALN}/${sample}_ReadsPerGene.out.tab"
    if [[ ! -s "${tab}" ]]; then
        reads=("${r1}")
        [[ -n "${r2}" && "${r2}" != "-" && "${r2}" != "NA" ]] && reads+=("${r2}")
        for f in "${reads[@]}"; do
            [[ -s "${f}" ]] || { echo "[FATAL] ${sample}: 找不到读段文件（FASTQ） ${f}"; exit 1; }
        done
        echo "[INFO] ${sample}: $([[ ${#reads[@]} -eq 2 ]] && echo 双端 || echo 单端)"
        STAR --genomeDir "${IDX}" --readFilesIn "${reads[@]}" --readFilesCommand zcat \
             --runThreadN "${THREADS}" --outSAMtype BAM SortedByCoordinate \
             --quantMode GeneCounts \
             --outFilterMultimapNmax 1 \
             --outFileNamePrefix "${ALN}/${sample}_"
        samtools index "${ALN}/${sample}_Aligned.sortedByCoord.out.bam"
    fi
    awk -v p="^${HOST_PFX}" -v c="${STRAND_COL}" \
        'NR>4 && $1 ~ p {print $1"\t"$c}' "${tab}" > "${CNT_H}/${sample}.tsv"
    awk -v p="^${PATH_PFX}" -v c="${STRAND_COL}" \
        'NR>4 && $1 ~ p {print $1"\t"$c}' "${tab}" > "${CNT_P}/${sample}.tsv"
done < "${SAMPLES}"

# ---------------------------------------------------------------- 步骤四：生物量曲线
echo "=== [4/4] 生物量曲线与交叉比对本底 ==="
{
printf "sample\ttreatment\ttime\thost_reads\tpath_reads\tpath_pct\tmultimap_pct\n"
while IFS=$'\t' read -r sample r1 r2 treatment time; do
    [[ -z "${sample}" || "${sample}" == \#* || "${sample}" == "sample" ]] && continue
    tab="${ALN}/${sample}_ReadsPerGene.out.tab"
    log="${ALN}/${sample}_Log.final.out"
    h=$(awk -v p="^${HOST_PFX}" -v c="${STRAND_COL}" 'NR>4 && $1 ~ p {s+=$c} END{print s+0}' "${tab}")
    p=$(awk -v p="^${PATH_PFX}" -v c="${STRAND_COL}" 'NR>4 && $1 ~ p {s+=$c} END{print s+0}' "${tab}")
    # 多重比对率 = 被 --outFilterMultimapNmax 1 剔除的比例，其中含同源区的两侧共命中 read
    mm=$(awk -F'|' '/multiple loci/ && /%/ {gsub(/[ \t%]/,"",$2); s+=$2} END{printf "%.3f", s}' "${log}")
    printf "%s\t%s\t%s\t%d\t%d\t%.4f\t%s\n" \
           "${sample}" "${treatment:-NA}" "${time:-NA}" "${h}" "${p}" \
           "$(awk -v a="${p}" -v b="${h}" 'BEGIN{t=a+b; print (t>0)? a/t*100 : 0}')" "${mm}"
done < "${SAMPLES}"
} > "${QC}/biomass.tsv"

echo "完成。请先看 ${QC}/biomass.tsv："
echo "  · 未接种对照行的 path_pct 就是交叉比对本底，应接近 0（讲义 §6.1）"
echo "  · 同一时间点重复间相差一个数量级 = 接种不均，建模前必须处理"
echo "两份分开的计数矩阵：${CNT_H}/ 与 ${CNT_P}/ —— 绝不要合并（讲义 §4.4）"
