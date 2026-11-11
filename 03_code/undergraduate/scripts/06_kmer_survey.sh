#!/bin/bash
#$ -S /bin/bash
#$ -N u06_kmer
#$ -cwd
#$ -j y
#$ -pe smp 4
#
# u06 步骤一：k-mer 基因组扫描（Jellyfish count + histo，k=17/21/25）
# 提交方式：qsub 06_kmer_survey.sh        【禁止在登录节点直接 bash 运行】
# 配套讲义：02_lectures/undergraduate/unit06_assembly_basics/06_assembly_basics_lecture.md §5.2
#
# 说明：
#   -S /bin/bash  必须写。默认 shell 不是 bash 时，下面的进程替换 <(zcat ...) 会报
#                 "syntax error near unexpected token `('"
#   -pe smp 4     申请 4 个 slot，与 jellyfish 的 -t 4 保持一致；两处不一致会挤占别人的核

set -euo pipefail

# ---------------------------------------------------------------- 参数
THREADS=4
HASH_SIZE=1000000000          # jellyfish 哈希槽数，非字节数；细菌 1e9 足够（约占 4-8 GB）
KVALUES=(17 21 25)            # 手册要求三档对比，主用 21
READ_LEN=100                  # Illumina 读长，GenomeScope 需要这个数
RAW_DIR=/data/lab/ngs
WORKDIR=/d3/scratch/${USER}/ngs/survey
FQDIR=/d3/scratch/${USER}/ngs/fq

# ---------------------------------------------------------------- 环境
source /opt/miniconda3/bin/activate
conda activate ngs_ug_assembly       # 项目集群上的既有环境名为 ngs，按实际情况改
command -v jellyfish >/dev/null || { echo "[FATAL] jellyfish 不在 PATH，环境没激活成功"; exit 1; }

mkdir -p "${WORKDIR}" "${FQDIR}"

# ---------------------------------------------------------------- 数据软链接
# 只建链接、不拷贝：原始数据几十 GB，每人拷一份会撑爆配额
cd "${FQDIR}"
ln -sf "${RAW_DIR}"/reads* ./ 2>/dev/null || true
ls -lh "${FQDIR}"

# k-mer 扫描要用短读长（低错误率）。PacBio 原始 reads 错误率高，
# 直接拿来数 k-mer 得不到干净的主峰——见讲义 §9 第 5 条。
shopt -s nullglob
FQ_FILES=("${FQDIR}"/*.fq.gz "${FQDIR}"/*.fastq.gz)
if [ ${#FQ_FILES[@]} -eq 0 ]; then
    echo "[FATAL] ${FQDIR} 下没有 *.fq.gz，无法做 k-mer 扫描。"
    echo "        若本项目只有 PacBio reads.fa，请先与教师确认扫描用哪份数据。"
    exit 1
fi

# ---------------------------------------------------------------- 计数
cd "${WORKDIR}"
for K in "${KVALUES[@]}"; do
    echo "=== [$(date +%T)] jellyfish count, k=${K} ==="
    # -C  正反链合并计数：DNA 双链，AGCT 与其反向互补是同一段序列，不合并会把每个 k-mer 数成两半
    # -m  k 值
    # -s  哈希大小
    # -t  线程数
    # -o  输出的二进制计数文件
    jellyfish count -C -m "${K}" -s "${HASH_SIZE}" -t "${THREADS}" \
        -o "reads.k${K}.jf" <(zcat "${FQ_FILES[@]}")

    echo "=== [$(date +%T)] jellyfish histo, k=${K} ==="
    # histo 把"出现 n 次的 k-mer 有多少种"输出成两列文本，这就是 GenomeScope 的输入
    jellyfish histo -t "${THREADS}" "reads.k${K}.jf" > "reads.k${K}.histo"

    # 立刻做一次自检：主峰位置应落在 20-100 之间且明显高于两侧
    echo "--- k=${K} 前 15 行（第 1 列 = 深度，第 2 列 = 该深度的 k-mer 种类数）---"
    head -15 "reads.k${K}.histo"
done

# 与手册命名保持一致：主用 k=21 的 histo 另存一份无 k 标记的名字
cp "reads.k21.histo" reads.histo

echo "[$(date +%T)] k-mer 计数完成。下一步：Rscript genomescope.R reads.histo 21 ${READ_LEN} gs_k21 1000"
