#!/bin/bash
#$ -S /bin/bash
#$ -N m02_ortho_cafe
#$ -cwd
#$ -j y
#$ -pe smp 16
# ============================================
# 脚本名称：02_orthofinder_cafe.sh
# 功能描述：m02 比较/泛基因组一条链 —— OrthoFinder orthogroup → 核心/可变划分输入 → CAFE5 扩张收缩
# 作者：王运生
# 日期：2026-08-29
# 提交方式：qsub 02_orthofinder_cafe.sh      【禁止在登录节点直接 bash 运行】
# 配套讲义：02_lectures/master/topic02_assembly_pangenome/02_assembly_pangenome_lecture.md §5.5-5.7
# ============================================
#
# 输入前提（讲义 §⑤ 案例数据）：
#   PROT_DIR 下每个基因组一个 .faa，文件名（去扩展名）即输出中的物种名；
#   **全部基因组必须用同一注释流程、同一版本、同一参数产生**——否则会得到大批
#   假的"物种特异基因"（讲义 §9-2），这是本流程最常见的翻车点。

set -euo pipefail

# ---------------------------------------------------------------- 参数
THREADS=16
ANALYSIS_THREADS=4            # OrthoFinder 的 -a：树构建等分析步骤的并行度，别设得比 -t 还大
MAX_FAMILY_SIZE=100           # 单物种拷贝数 ≥ 此值的超大家族不进 CAFE5（会把 λ 拉到极端值）；
                              # 100 出自 CAFE 官方教程 clade_and_size_filter.py 的做法，是惯例而非理论阈值

PROT_DIR=/data/lab/m02/proteomes            # 【主线数据待定】8-12 个近缘菌株的统一注释 .faa
TREE_ULTRA=/data/lab/m02/tree_ultrametric.nwk   # 【主线数据待定】超度量物种树（分支长度 = 时间）
WORKDIR=/d3/scratch/${USER}/m02/compgenome
CKPT=/data/lab/m02/checkpoints

# ---------------------------------------------------------------- 环境
source /opt/miniconda3/bin/activate
conda activate ngs_ms_genome
for tool in orthofinder diamond mafft cafe5; do
    command -v "${tool}" >/dev/null || { echo "[FATAL] ${tool} 不在 PATH，环境没激活成功"; exit 1; }
done
# 注：bioconda 包名是 cafe（cafe=5.1.0 即 CAFE5），装出的命令是 cafe5。

mkdir -p "${WORKDIR}"
cd "${WORKDIR}"

# ---------------------------------------------------------------- 1. 输入体检（做在跑之前）
echo "=== [$(date +%T)] 输入体检：各蛋白集的基因数是否可比 ==="
for f in "${PROT_DIR}"/*.faa; do
    printf "%-30s %s\n" "$(basename "$f")" "$(grep -c '^>' "$f")"
done
echo "[提示] 某个基因组的蛋白数明显离群，先查注释流程是否统一，不要直接往下跑。"
echo "       （同种菌株间 >20% 是本课的经验警戒线，不是文献阈值；近缘种间差异可以更大）"

# ---------------------------------------------------------------- 2. OrthoFinder [checkpoint]
echo "=== [$(date +%T)] 步骤一：OrthoFinder（约 20-40 min） ==="
if [ -d "${CKPT}/orthofinder_results" ] && [ "${USE_CKPT:-0}" = "1" ]; then
    echo "[INFO] USE_CKPT=1，使用预跑结果"
    RES="${CKPT}/orthofinder_results"
else
    # -t 全对全搜索线程   -a 分析步骤线程   -M msa 用比对建基因树（比 dendroblast 准但慢）
    # -S diamond 以 DIAMOND 代替 BLAST，10 个细菌基因组规模上快 1-2 个数量级
    orthofinder -f "${PROT_DIR}" -t "${THREADS}" -a "${ANALYSIS_THREADS}" -M msa -S diamond
    RES=$(ls -d "${PROT_DIR}"/OrthoFinder/Results_*/ | tail -1)
fi
echo "[INFO] OrthoFinder 结果目录：${RES}"

# ---------------------------------------------------------------- 3. 输出体检：假物种特异基因的警报
echo "=== [$(date +%T)] 输出体检：Statistics_PerSpecies.tsv ==="
grep -E "Number of genes$|species-specific orthogroups" \
     "${RES}/Comparative_Genomics_Statistics/Statistics_PerSpecies.tsv" || true
echo "[提示] 某一列的 species-specific 计数比其他列高一个量级 → 注释流程不统一（讲义 §9-2）。"

# 单拷贝直系同源（建树用）与物种特异基因（候选毒力因子）分别在哪
echo "--- 单拷贝直系同源 OG 数：$(wc -l < "${RES}/Orthogroups/Orthogroups_SingleCopyOrthologues.txt")"
echo "--- 单拷贝序列目录：${RES}/Single_Copy_Orthologue_Sequences/（→ MAFFT + IQ-TREE 建物种树）"
echo "--- 孤儿基因表：${RES}/Orthogroups/Orthogroups_UnassignedGenes.tsv"

# ---------------------------------------------------------------- 4. 泛基因组划分的输入
cp "${RES}/Orthogroups/Orthogroups.GeneCount.tsv" ./
echo "[INFO] Orthogroups.GeneCount.tsv 已就位 —— 用 ngs_ms_base 环境跑 R 做 core/shell/cloud"
echo "       划分、UpSet 图与稀释曲线（讲义 §5.6）。"

# ---------------------------------------------------------------- 5. CAFE5 输入准备与过滤
echo "=== [$(date +%T)] 步骤二：构造 CAFE5 输入 ==="
NSP=$(head -1 Orthogroups.GeneCount.tsv | awk -F'\t' '{print NF-2}')   # 减去 Orthogroup 与 Total 两列
# CAFE5 输入：第 1 列描述、第 2 列家族 ID、其后每物种一列计数；物种列顺序须与树叶名对应
awk -v n="${NSP}" -v maxf="${MAX_FAMILY_SIZE}" 'BEGIN{FS=OFS="\t"}
    NR==1 { printf "Desc\tFamily_ID"; for(i=2;i<=n+1;i++) printf "\t%s", $i; print ""; next }
    {
        sum=0; mx=0
        for(i=2;i<=n+1;i++){ sum+=$i; if($i>mx) mx=$i }
        if (sum==0)    next          # 全 0 家族会让似然无定义（讲义 §9-6）
        if (mx>=maxf)  next          # 超大家族把 λ 拉到极端值，单独做描述性分析
        printf "(null)\t%s", $1; for(i=2;i<=n+1;i++) printf "\t%s", $i; print ""
    }' Orthogroups.GeneCount.tsv > cafe_input.tsv
echo "[INFO] 过滤后家族数：$(( $(wc -l < cafe_input.tsv) - 1 ))"

# 树的自检：非超度量树 CAFE5 会拒绝（讲义 §9-3）
# 超度量是 CAFE5 的必要条件而非充分条件：分支长度还须与时间成比例（讲义 §9-3）
if Rscript -e 'quit(status = !requireNamespace("ape", quietly = TRUE))' 2>/dev/null; then
    Rscript -e 'tr <- ape::read.tree(commandArgs(TRUE)[1]); u <- ape::is.ultrametric(tr);
                cat("is.ultrametric:", u, "\n"); quit(status = !u)' "${TREE_ULTRA}" \
        || { echo "[FATAL] 树不是超度量的，CAFE5 会拒绝；先用 r8s/treePL/chronos 定年"; exit 1; }
else
    echo "[WARN] 当前环境无 R 包 ape，跳过超度量自检（CAFE5 遇非超度量树会自行报错）"
fi

# ---------------------------------------------------------------- 6. CAFE5
echo "=== [$(date +%T)] 步骤三：CAFE5 ==="
# -t 必须是超度量树（分支长度 = 时间）
# -p 是 --poisson：根节点家族大小取 Poisson 分布（CAFE5 文档），**不是**「输出 p 值」开关——
#    家族级 p 值默认就写在 Base_family_results.txt 里（UP-042）
cafe5 -i cafe_input.tsv -t "${TREE_ULTRA}" -p -o cafe_out

echo "--- 家族级结果：cafe_out/Base_family_results.txt（p 值）"
echo "--- 分支级结果：cafe_out/Base_branch_probabilities.tab"
echo "[提示] 家族级 p 值必须再做 BH 校正后按 FDR 报告；显著家族占比异常高（本课经验线 >20%，"
echo "       非文献阈值）时先查输入过滤与 λ 估计是否合理"
echo "       （讲义 §⑦-1、§⑦-3、§6.5）。"
echo "[$(date +%T)] 比较/泛基因组侧完成。"
