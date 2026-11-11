#!/bin/bash
#$ -S /bin/bash
#$ -N u06_assem
#$ -cwd
#$ -j y
#$ -pe smp 4
#$ -l h_vmem=8G
#
# u06 步骤二：Canu 与 Flye 双组装对比
# 提交方式：qsub 06_assemble_compare.sh   【禁止在登录节点直接 bash 运行——必被 kill】
# 配套讲义：unit06_assembly_basics/06_assembly_basics_lecture.md §5.4 / §5.5
#
# 注意 h_vmem 是"每 slot"的内存上限，4 slot × 8G = 32G。
# 集群若不识别 h_vmem（用 mem_free / vf 等名字），请按本地 qconf -sc 的资源名改。

set -euo pipefail

# ---------------------------------------------------------------- 参数
THREADS=4
GENOME_SIZE=4m                # 【最容易写错的一处】4 Mb 细菌 → 4m。
                              # 写成 4g 会让 Canu 按 40 亿 bp 规划资源，作业几天不结束；
                              # 写成 4k 会让它认为覆盖度高到离谱，疯狂丢弃 read。
READS=/data/lab/ngs/reads.fa  # PacBio 长读长，FASTA
WORKDIR=/d3/scratch/${USER}/ngs/assem

source /opt/miniconda3/bin/activate
conda activate ngs_ug_assembly
command -v canu >/dev/null || { echo "[FATAL] canu 不在 PATH"; exit 1; }
command -v flye >/dev/null || { echo "[FATAL] flye 不在 PATH"; exit 1; }
[ -s "${READS}" ] || { echo "[FATAL] 找不到输入 ${READS}"; exit 1; }

mkdir -p "${WORKDIR}"/{canu,flye}

# ---------------------------------------------------------------- Canu（OLC）
echo "=== [$(date +%T)] Canu 开始 ==="
cd "${WORKDIR}/canu"
# -p            输出文件前缀（test.contigs.fasta 等）。注意："test" 只是前缀名，
#               产物是你自己的 CIX4481 组装，不是 Canu 自带测试数据（UP-033）；
#               讲义多处引用该路径，故不改名
# -d            输出目录
# genomeSize=   必填。Canu 用它换算测序覆盖度，决定纠错时保留多少 read
# -pacbio       PacBio 原始/未纠错读长。Canu 1.x 的写法是 -pacbio-raw，2.0 起改为 -pacbio
# useGrid=false 关键：本脚本已经在一个 qsub 作业里，Canu 若再自行向 SGE 投递子作业，
#               常见结果是子作业排不上队、或与本作业互相等待而挂死。
# maxThreads/maxMemory 让 Canu 老实待在 SGE 给的资源里，别超额被调度器杀掉
canu -p test -d test-pacbio \
     genomeSize=${GENOME_SIZE} \
     useGrid=false \
     maxThreads=${THREADS} maxMemory=28g \
     -pacbio "${READS}"

CANU_FA="${WORKDIR}/canu/test-pacbio/test.contigs.fasta"
[ -s "${CANU_FA}" ] || { echo "[FATAL] Canu 未产出 contigs，检查 test-pacbio/*.report"; exit 1; }
echo "=== [$(date +%T)] Canu 完成：${CANU_FA} ==="

# ---------------------------------------------------------------- Flye（repeat graph）
echo "=== [$(date +%T)] Flye 开始 ==="
cd "${WORKDIR}/flye"
# --pacbio-raw   PacBio 未纠错读长（HiFi 数据应改用 --pacbio-hifi，两者不能混用）
# --out-dir      输出目录，assembly.fasta 在里面
# --genome-size  预期大小；Flye 2.8 起可省略，写上便于与 Canu 对齐口径
# --threads      线程数
flye --pacbio-raw "${READS}" \
     --out-dir out_pacbio \
     --genome-size ${GENOME_SIZE} \
     --threads ${THREADS}

FLYE_FA="${WORKDIR}/flye/out_pacbio/assembly.fasta"
[ -s "${FLYE_FA}" ] || { echo "[FATAL] Flye 未产出 assembly.fasta，检查 out_pacbio/flye.log"; exit 1; }
echo "=== [$(date +%T)] Flye 完成：${FLYE_FA} ==="

# ---------------------------------------------------------------- 粗看一眼
echo "--- contig 条数 ---"
echo "Canu: $(grep -c '^>' "${CANU_FA}")"
echo "Flye: $(grep -c '^>' "${FLYE_FA}")"
echo "--- Flye 的每条 contig 信息（含环状标记 circular）---"
cat "${WORKDIR}/flye/out_pacbio/assembly_info.txt" || true

echo "[$(date +%T)] 双组装完成。下一步：qsub 06_assembly_eval.sh"
