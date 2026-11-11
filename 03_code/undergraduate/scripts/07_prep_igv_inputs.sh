#!/bin/bash
# ============================================
# 脚本名称：07_prep_igv_inputs.sh
# 功能描述：准备 IGV 三样输入并做一致性检查（单元 u07 ⑤5.5）
#           ① genome.fasta + .fai  ② 已排序并索引的 BAM  ③ 去掉 ##FASTA 段的 GFF
#           并核对 GFF 的 contig 名与 FASTA 头行是否一致（IGV 空白的头号原因）
# 运行方式：bash 07_prep_igv_inputs.sh [genome.fasta] [reads.bam] [prokka_out/mygenome.gff]
# 作者：王运生
# 日期：2026-08-29
# ============================================

set -euo pipefail

GENOME="${1:-genome.fasta}"
BAM="${2:-reads.bam}"
GFF="${3:-prokka_out/mygenome.gff}"
IGV_GFF="mygenome.igv.gff"
SORTED_BAM="reads.sorted.bam"
THREADS="${NSLOTS:-4}"
CONDA_ROOT="/opt/miniconda3"
CONDA_ENV="ngs_ug_base"     # IGV 与 samtools 都在 base 环境，不在 ngs_ug_annot

main() {
    # shellcheck disable=SC1091
    source "${CONDA_ROOT}/bin/activate"
    conda activate "${CONDA_ENV}"

    # ---- ① 基因组索引 ----
    [[ -s "${GENOME}" ]] || { echo "[ERROR] 找不到 ${GENOME}" >&2; exit 1; }
    [[ -s "${GENOME}.fai" ]] || samtools faidx "${GENOME}"
    echo "[INFO] FASTA 索引就绪：${GENOME}.fai"

    # ---- ② BAM 排序与索引（IGV 加载 BAM 的硬前提）----
    if [[ -s "${BAM}" ]]; then
        # 先把表头存进变量再判断：`samtools view -H | grep -q` 在 pipefail 下
        # grep 提前退出会让 samtools 收到 SIGPIPE，整条管道判失败（UP-036）
        local bam_hdr
        bam_hdr="$(samtools view -H "${BAM}")"
        if [[ "${bam_hdr}" == *"SO:coordinate"* ]]; then
            SORTED_BAM="${BAM}"
            echo "[INFO] BAM 已按坐标排序，跳过 sort"
        else
            echo "[INFO] BAM 未排序，执行 samtools sort"
            samtools sort -@ "${THREADS}" -o "${SORTED_BAM}" "${BAM}"
        fi
        [[ -s "${SORTED_BAM}.bai" ]] || samtools index "${SORTED_BAM}"
        echo "[INFO] BAM 索引就绪：${SORTED_BAM}.bai"

        # BAM 的 @SQ（名称+长度）必须与这份 FASTA 完全一致，否则 IGV 轨道错位或空白：
        # 典型错误是 reads 比对到了另一版组装（Canu vs Flye）或参考基因组
        samtools view -H "${SORTED_BAM}" \
            | awk -F'\t' '$1=="@SQ"{n="";l=""; for(i=2;i<=NF;i++){if($i~/^SN:/)n=substr($i,4); if($i~/^LN:/)l=substr($i,4)} print n"\t"l}' \
            | sort > .bam_sq.tmp
        cut -f1,2 "${GENOME}.fai" | sort > .fasta_sq.tmp
        if ! cmp -s .bam_sq.tmp .fasta_sq.tmp; then
            echo "[ERROR] BAM 的 @SQ 与 ${GENOME} 的序列名/长度不一致（< BAM，> FASTA）：" >&2
            diff .bam_sq.tmp .fasta_sq.tmp | head -20 >&2 || true
            echo "        reads 必须比对到这同一份 FASTA，例如（minimap2 在 ngs_ug_assembly 环境）：" >&2
            echo "        minimap2 -ax map-pb ${GENOME} reads.fa | samtools sort -o reads.bam" >&2
            rm -f .bam_sq.tmp .fasta_sq.tmp
            exit 1
        fi
        rm -f .bam_sq.tmp .fasta_sq.tmp
        echo "[INFO] BAM @SQ 与 FASTA 名称/长度一致"
    else
        echo "[WARN] 未提供 BAM（${BAM} 不存在），跳过比对轨道准备" >&2
        echo "       生成方法（reads 比对到同一份组装；minimap2 在 ngs_ug_assembly 环境）：" >&2
        echo "       minimap2 -ax map-pb ${GENOME} reads.fa | samtools sort -o reads.bam" >&2
    fi

    # ---- ③ 切出 IGV 版 GFF ----
    # Prokka 的 GFF 末尾附有 ##FASTA + 完整序列：Roary 依赖它，IGV 不需要且可能被它搞晕
    [[ -s "${GFF}" ]] || { echo "[ERROR] 找不到 ${GFF}" >&2; exit 1; }
    awk '/^##FASTA/{exit} {print}' "${GFF}" > "${IGV_GFF}"
    echo "[INFO] IGV 版注释就绪：${IGV_GFF}"
    echo "[警告] ${IGV_GFF} 只能给 IGV 用；Roary 必须用原件 ${GFF}，否则核心基因数接近 0"

    # ---- ④ contig 名一致性检查（IGV 一片空白的头号原因）----
    cut -f1 "${IGV_GFF}" | grep -v "^#" | sort -u > .gff_ids.tmp
    cut -f1 "${GENOME}.fai" | sort -u > .fasta_ids.tmp
    if [[ -n "$(comm -23 .gff_ids.tmp .fasta_ids.tmp)" ]]; then
        echo "[ERROR] GFF 中存在 FASTA 里没有的 contig 名，IGV 将无法显示注释：" >&2
        comm -23 .gff_ids.tmp .fasta_ids.tmp >&2
        rm -f .gff_ids.tmp .fasta_ids.tmp
        exit 1
    fi
    rm -f .gff_ids.tmp .fasta_ids.tmp
    echo "[INFO] contig 名一致性检查通过"

    echo
    echo "把下列文件拉回本机同一目录后按顺序加载（Genomes → Load Genome from File 先加载基因组）："
    if [[ -s "${BAM}" ]]; then
        echo "  ${GENOME}  ${GENOME}.fai  ${IGV_GFF}  ${SORTED_BAM}  ${SORTED_BAM}.bai"
    else
        echo "  ${GENOME}  ${GENOME}.fai  ${IGV_GFF}  （无 BAM 轨道）"
    fi
}

main "$@"
