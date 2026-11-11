#!/bin/bash
#$ -S /bin/bash
#$ -N m02_assembly
#$ -cwd
#$ -j y
#$ -pe smp 16
# ============================================
# 脚本名称：02_assembly_pipeline.sh
# 功能描述：m02 组装侧一条链 —— Jellyfish/GenomeScope2 k-mer 估计 → Flye 组装 → QUAST + BUSCO 评估
# 作者：王运生
# 日期：2026-08-29
# 提交方式：qsub 02_assembly_pipeline.sh      【禁止在登录节点直接 bash 运行】
# 配套讲义：02_lectures/master/topic02_assembly_pangenome/02_assembly_pangenome_lecture.md §5.2-5.4
# ============================================
#
# 说明：
#   -S /bin/bash  必须写。SGE 默认 shell 不是 bash 时，下面的进程替换 <(zcat ...)
#                 会报 "syntax error near unexpected token `('"（讲义 §9-5）
#   -pe smp 16    申请的 slot 数须与下面的 THREADS 一致，两处不一致会挤占别人的核

set -euo pipefail

# ---------------------------------------------------------------- 参数
THREADS=16
KMER=21                       # 细菌常用 21；取奇数以避免 k-mer 与自身反向互补相同
PLOIDY=1                      # 单倍体（细菌）用 1；二倍体真菌/卵菌用 2
HASH_SIZE=2G                  # jellyfish 哈希槽数（非字节）；≤50 Mb 基因组 2G 足够
# 主线 ERR15732374 是 MinION（ENA instrument_model，2026-11-04 核），化学版本未注明 → --nano-raw 最稳妥；
# 换 HiFi 数据用 --pacbio-hifi，确知 R10.4 + Dorado sup 用 --nano-hq（UP-001）
READ_TYPE="${READ_TYPE:---nano-raw}"   # HiFi: --pacbio-hifi | ONT 普通: --nano-raw | ONT R10+sup: --nano-hq
BUSCO_LINEAGE="${BUSCO_LINEAGE:-xanthomonadales_odb10}"  # 与 06_data/master/README 自查判据一致；
                                                          # 报告中必须写明库名与版本
BUSCO_DB=/data/db/busco_downloads          # 预下载目录，见下方 --offline 说明

# 主线数据：CIX2779（PRJEB100987），由 06_data/master/download_master.sh --topic m02 下载
DATA_DIR="${DATA_DIR:-/d3/scratch/${USER}/ngs/data/m02}"
READS="${READS:-${DATA_DIR}/ERR15732374.fastq.gz}"        # ONT 长读长 → Flye 组装
SR1="${SR1:-${DATA_DIR}/ERR15732332_1.fastq.gz}"          # Illumina 短读长 → k-mer survey
SR2="${SR2:-${DATA_DIR}/ERR15732332_2.fastq.gz}"          #   （长读长错误率高，不适合做 k-mer 谱）
# QUAST 参考：CIX2779 已发表完成图 GCA_024981335 = 标准答案。下载脚本不取组装，需在登录节点自取：
#   B=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/024/981/335/GCA_024981335.1_ASM2498133v1/GCA_024981335.1_ASM2498133v1
#   curl -s ${B}_genomic.fna.gz | zcat > ${DATA_DIR}/GCA_024981335.fna
#   curl -s ${B}_genomic.gff.gz | zcat > ${DATA_DIR}/GCA_024981335.gff
REF_FA="${REF_FA:-${DATA_DIR}/GCA_024981335.fna}"
REF_GFF="${REF_GFF:-${DATA_DIR}/GCA_024981335.gff}"      # 可缺省：缺失时 QUAST 不给基因覆盖统计
WORKDIR=/d3/scratch/${USER}/m02/assembly
CKPT=/data/lab/m02/checkpoints             # 预跑结果：跑不完就从这里取（讲义"工程约束②"）

# ---------------------------------------------------------------- 环境
source /opt/miniconda3/bin/activate
conda activate ngs_ms_genome
for tool in jellyfish genomescope2 flye quast.py busco; do
    command -v "${tool}" >/dev/null || { echo "[FATAL] ${tool} 不在 PATH，环境没激活成功"; exit 1; }
done

for f in "${READS}" "${SR1}" "${SR2}" "${REF_FA}"; do
    [ -s "${f}" ] || { echo "[FATAL] 输入缺失：${f}（先跑 download_master.sh --topic m02，参考组装见上方注释）"; exit 1; }
done

mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

# ---------------------------------------------------------------- 1. k-mer 特征估计
echo "=== [$(date +%T)] 步骤一：k-mer 特征估计 ==="
# -C  正反链合并计数（DNA 双链，不合并等于把每个 k-mer 数成两半）
# -m  k 值    -s 哈希槽数    -t 线程    -o 二进制计数文件
jellyfish count -C -m "${KMER}" -s "${HASH_SIZE}" -t "${THREADS}" \
    -o reads.jf <(zcat "${SR1}" "${SR2}")
# histo 输出两列：深度 / 该深度的 k-mer 种类数 —— 这就是 GenomeScope 的输入
jellyfish histo -t "${THREADS}" reads.jf > reads.histo
genomescope2 -i reads.histo -o genomescope_out -k "${KMER}" -p "${PLOIDY}"

# 自检：Model Fit < 90% 时后面三个数全部无意义（讲义 §6.1）
grep -E "Model Fit|Genome Haploid Length|Heterozygosity" genomescope_out/summary.txt || true

# ---------------------------------------------------------------- 2. 长读长组装 [checkpoint]
echo "=== [$(date +%T)] 步骤二：Flye 组装（约 20-40 min） ==="
if [ -s "${CKPT}/asm_flye/assembly.fasta" ] && [ "${USE_CKPT:-0}" = "1" ]; then
    echo "[INFO] USE_CKPT=1，直接使用预跑结果，跳过组装"
    mkdir -p asm_flye && cp "${CKPT}"/asm_flye/assembly*.{fasta,txt,gfa} asm_flye/ 2>/dev/null || true
else
    # 读长类型参数必须与数据匹配，选错的后果见讲义 §9-4（contig 数暴涨、总长远超估计）
    # --genome-size 自 Flye 2.8 起为可选项，不写则自行估计
    flye ${READ_TYPE} "${READS}" --out-dir asm_flye --threads "${THREADS}"
fi
echo "--- assembly_info.txt（看 circ. 列：细菌染色体应为 Y）---"
head -5 asm_flye/assembly_info.txt

# ---------------------------------------------------------------- 3. 组装评估
echo "=== [$(date +%T)] 步骤三：QUAST（连续性 + 正确性） ==="
# 必须给 -r/-g 才有 misassembly 与基因覆盖统计；不给就只有连续性指标（讲义 §6.2）
QUAST_GFF=()
if [ -s "${REF_GFF}" ]; then QUAST_GFF=(-g "${REF_GFF}"); else echo "[WARN] 无 ${REF_GFF}，QUAST 不出基因覆盖统计"; fi
# ${arr[@]+...} 写法：集群 bash 4.2 下空数组配 set -u 会报 unbound variable
quast.py asm_flye/assembly.fasta -r "${REF_FA}" ${QUAST_GFF[@]+"${QUAST_GFF[@]}"} \
    -o quast_out -t 8

echo "=== [$(date +%T)] 步骤四：BUSCO（完整性） ==="
# --offline + --download_path 用登录节点预下载的库：计算节点通常不通外网（讲义 §9-1）
# 若未预下载，先在登录节点执行：
#   busco --download ${BUSCO_LINEAGE} --download_path ${BUSCO_DB}
busco -i asm_flye/assembly.fasta -l "${BUSCO_LINEAGE}" -m genome -o busco_out -c 8 \
      --offline --download_path "${BUSCO_DB}"

# ---------------------------------------------------------------- 4. 汇总自检
echo "=== [$(date +%T)] 三把尺汇总（连续性 / 正确性 / 完整性）==="
grep -E "^# contigs|^Total length|^N50|^L50|^# misassemblies" quast_out/report.txt || true
grep -E "C:[0-9]" busco_out/short_summary*.txt || true
echo "[提示] C 高但 D 高 ≠ 组装好；N50 大但 misassembly 多 ≠ 组装好。判据见讲义 §4.4 与 §⑦。"
echo "[$(date +%T)] 组装侧完成。下一步：qsub 02_orthofinder_cafe.sh"
