#!/bin/bash
#$ -S /bin/bash
#$ -N metagenome
#$ -cwd
#$ -j y
#$ -pe smp 24
#$ -l h_vmem=10G
# ============================================================
# m07 宏基因组分析 —— 组装 → 分箱 → 质量评估 → 功能注释
# 环境：conda activate ngs_ms_microbiome
#
# 注意：eggNOG-mapper 的数据库约 50 GB，需集群侧单独部署。
#      未部署时本脚本跳过该步并给出提示，不会中断整个流程。
# ============================================================
set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_ms_microbiome

R1="${R1:?必须指定 R1}"
R2="${R2:-}"                      # 留空 = 单端数据（课程 m07 的 12 个 run 在 ENA 均为 SINGLE）
SAMPLE="${SAMPLE:-meta}"
OUTDIR="${OUTDIR:-./metagenome/${SAMPLE}}"
THREADS="${NSLOTS:-24}"
HOST_IDX="${HOST_IDX:-}"          # 宿主基因组 bowtie2 索引前缀，宿主相关样本必填
EGGNOG_DB="${EGGNOG_DB:-}"        # eggNOG 数据库目录

mkdir -p "${OUTDIR}"

# ---- 1) 去宿主（植物/昆虫样本不做这步，宿主序列会淹没微生物信号）----
if [[ -n "${HOST_IDX}" ]]; then
    echo "[1/5] 去宿主 ..."
    # 保持 bowtie2 默认灵敏度，不加 --very-sensitive：过严会把与宿主局部同源的
    # 微生物 reads 一并删掉（讲义 ④4.1）。保留口径：双端都未比对（-f 12）/ 单端未比对（-f 4）。
    if [[ -n "${R2}" ]]; then
        bowtie2 -x "${HOST_IDX}" -1 "${R1}" -2 "${R2}" -p "${THREADS}" \
          | samtools view -b -f 12 -F 256 - \
          | samtools sort -n -@ 4 -o "${OUTDIR}/unmapped.bam" -
        samtools fastq -1 "${OUTDIR}/clean_1.fq.gz" -2 "${OUTDIR}/clean_2.fq.gz" \
            -0 /dev/null -s /dev/null -n "${OUTDIR}/unmapped.bam"
        R1="${OUTDIR}/clean_1.fq.gz"; R2="${OUTDIR}/clean_2.fq.gz"
    else
        bowtie2 -x "${HOST_IDX}" -U "${R1}" -p "${THREADS}" \
          | samtools view -b -f 4 -F 256 - \
          | samtools fastq - | gzip > "${OUTDIR}/clean.fq.gz"
        R1="${OUTDIR}/clean.fq.gz"
    fi
    # gzip 空流也会生成约 20 字节的文件，所以不能用 -s 判空，要真读一个字节
    [[ -n "$({ zcat "${R1}" 2>/dev/null || true; } | head -c 1)" ]] || { echo "[ERROR] 去宿主后没有剩余 reads：检查 HOST_IDX 是否选对" >&2; exit 3; }
else
    echo "[1/5] 跳过去宿主（未提供 HOST_IDX）。宿主相关样本请务必做这步。"
fi

# ---- 2) 组装 ----
echo "[2/5] MEGAHIT 组装 ..."
if [[ -n "${R2}" ]]; then READS_ARGS=(-1 "${R1}" -2 "${R2}"); MAP_ARGS=(-1 "${R1}" -2 "${R2}")
else                      READS_ARGS=(-r "${R1}");            MAP_ARGS=(-U "${R1}"); fi
megahit "${READS_ARGS[@]}" -t "${THREADS}" -o "${OUTDIR}/megahit" --min-contig-len 1000
ASM="${OUTDIR}/megahit/final.contigs.fa"

# ---- 3) 分箱：需要覆盖度信息，所以要把 reads 比回组装 ----
#     注意：这里是单样本组装 + 单样本覆盖度的简化形态。分箱主要靠「跨样本覆盖度共变」，
#     单样本时这一信号退化，低深度样本可能一个高质量 MAG 都分不出（讲义 ⑨-4）。
echo "[3/5] MetaBAT2 分箱 ..."
bowtie2-build --threads "${THREADS}" "${ASM}" "${OUTDIR}/asm_idx" > /dev/null
bowtie2 -x "${OUTDIR}/asm_idx" "${MAP_ARGS[@]}" -p "${THREADS}" \
  | samtools sort -@ 4 -o "${OUTDIR}/asm.bam" -
samtools index "${OUTDIR}/asm.bam"
jgi_summarize_bam_contig_depths --outputDepth "${OUTDIR}/depth.txt" "${OUTDIR}/asm.bam"
metabat2 -i "${ASM}" -a "${OUTDIR}/depth.txt" -o "${OUTDIR}/bins/bin" -t "${THREADS}" -m 1500

# ---- 4) 分箱质量：完整度与污染度决定这个 MAG 能不能用 ----
echo "[4/5] CheckM 评估 ..."
if checkm data setRoot 2>/dev/null >/dev/null || [[ -n "${CHECKM_DATA_PATH:-}" ]]; then
    checkm lineage_wf -x fa -t "${THREADS}" "${OUTDIR}/bins" "${OUTDIR}/checkm" \
        --tab_table -f "${OUTDIR}/checkm_summary.tsv" \
        || echo "  [WARN] checkm lineage_wf 失败，见上方日志；checkm_summary.tsv 不可用" >&2
    echo "  注意：本脚本调用的是 CheckM 1.x（checkm lineage_wf），不是讲义 ⑤5.5 的 CheckM2；两者数值口径不可互换。"
    echo "  MIMAG：completeness >90% 且 contamination <5% 只是 High-quality 的一部分，"
    echo "         还要求 23S/16S/5S rRNA 齐全且 tRNA ≥18 种；只满足前两项的短读长 MAG 应报 Medium-quality（≥50% / <10%）以上。"
else
    echo "  [跳过] CheckM 参考数据库未配置：checkm data setRoot <目录>"
fi

# ---- 5) 功能注释 ----
echo "[5/5] 功能注释 ..."
if [[ -n "${EGGNOG_DB}" && -d "${EGGNOG_DB}" ]]; then
    emapper.py -i "${ASM}" --itype metagenome -o "${OUTDIR}/eggnog" \
        --data_dir "${EGGNOG_DB}" --cpu "${THREADS}"
else
    echo "  [跳过] eggNOG 数据库未部署（约 50 GB）。设置 EGGNOG_DB=<目录> 后重跑此步。"
    echo "         报告中若要求 COG 分类图，需先与教师确认数据库可用性。"
fi

echo "完成。产出在 ${OUTDIR}/"
