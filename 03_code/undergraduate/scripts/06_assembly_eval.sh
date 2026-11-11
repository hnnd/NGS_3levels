#!/bin/bash
#$ -S /bin/bash
#$ -N u06_eval
#$ -cwd
#$ -j y
#$ -pe smp 4
#$ -hold_jid u06_assem
#
# u06 步骤三：QUAST（连续性）+ BUSCO（完整性）双维度评估
# 提交方式：qsub 06_assembly_eval.sh
# 配套讲义：unit06_assembly_basics/06_assembly_basics_lecture.md §5.6 / §5.7
#
# -hold_jid u06_assem  让 SGE 等组装作业结束后再跑本作业。
#   这比手册里的 `while [ ! -f ... ]; do sleep 300; done` 轮询更可靠：
#   轮询版本在组装失败时会永远等下去，白占一个 slot 直到作业超时。

set -euo pipefail

THREADS=4
LINEAGE=bacteria_odb10        # 细菌用这个。选错 lineage（如给细菌用 eukaryota_odb10）
                              # 会得到接近全 Missing 的结果，那不是组装烂，是库选错了
WORKDIR=/d3/scratch/${USER}/ngs/assem
CANU_FA="${WORKDIR}/canu/test-pacbio/test.contigs.fasta"
FLYE_FA="${WORKDIR}/flye/out_pacbio/assembly.fasta"

source /opt/miniconda3/bin/activate
conda activate ngs_ug_assembly

for f in "${CANU_FA}" "${FLYE_FA}"; do
    [ -s "$f" ] || { echo "[FATAL] 组装结果缺失：$f —— 先确认 06_assemble_compare.sh 真的成功了"; exit 1; }
done

mkdir -p "${WORKDIR}/eval"
cd "${WORKDIR}/eval"

# ---------------------------------------------------------------- QUAST
echo "=== [$(date +%T)] QUAST ==="
# 一次传入两个 fasta，QUAST 会输出并排对比表，比跑两次再手工拼表可靠
# -o     输出目录
# -t     线程数
# -l     给每列起名字，否则表头是一长串路径，没法看
QUAST_BIN=$(command -v quast.py || command -v quast)
"${QUAST_BIN}" "${CANU_FA}" "${FLYE_FA}" \
    -o quast_results -t ${THREADS} \
    -l "Canu,Flye"

echo "--- QUAST 关键指标 ---"
cat quast_results/report.txt

# ---------------------------------------------------------------- BUSCO
echo "=== [$(date +%T)] BUSCO ==="
# -i  输入基因组 fasta
# -o  输出目录名【只能是名字，不能带斜杠路径，否则报 "Please do not provide a path in --out"】
# -m genome  评估模式（基因组/转录组/蛋白）
# -l  谱系数据库
# -c  线程数
# 集群无外网时，先在有网机器上 busco --download bacteria_odb10，
# 再加 --offline --download_path <本地库目录>
busco -i "${CANU_FA}" -o busco_canu -m genome -l ${LINEAGE} -c ${THREADS} -f
busco -i "${FLYE_FA}" -o busco_flye -m genome -l ${LINEAGE} -c ${THREADS} -f

echo "--- BUSCO 摘要 ---"
grep -h "C:" busco_canu/short_summary*.txt busco_flye/short_summary*.txt || true

# ---------------------------------------------------------------- 汇总成报告要填的那张表
echo ""
echo "================ 报告模板用对比表（自行核对后誊写）================"
# transposed_report.tsv 每行一套组装，表头是指标名；下面按列名取值，列序变了也不会错位
awk -F'\t' '
  NR==1 { for (i = 1; i <= NF; i++) col[$i] = i;
          printf "%-8s %-10s %-12s %-12s %-14s\n",
                 "组装", "contig数", "总长(bp)", "N50(bp)", "最长contig"; next }
  { printf "%-8s %-10s %-12s %-12s %-14s\n",
           $1, $(col["# contigs"]), $(col["Total length"]),
           $(col["N50"]), $(col["Largest contig"]) }
' quast_results/transposed_report.tsv
echo "BUSCO 完整性请从上面的 C:xx.x%[S:..,D:..],F:..,M:.. 一行抄写"
echo "=================================================================="
