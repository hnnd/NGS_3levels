#!/bin/bash
#$ -S /bin/bash
#$ -N p02_scrnaseq
#$ -cwd
#$ -j y
#$ -pe smp 8
#$ -l h_vmem=64G
# ============================================================
# 脚本名称：02_run_seurat.sh
# 功能描述：p02「单细胞与空间转录组」实践的集群作业入口 ——
#           Seurat 主流程 → pseudobulk 差异表达 → 检出功效估算 →（可选）Visium。
#           SCTransform 与 FindAllMarkers 是内存大户（万级细胞常需 32-64 GB），
#           必须 qsub，不要在登录节点跑（l0_01_linux 自测 L0-1-Q9）。
#           SGE 作业不继承登录终端环境，故显式 source activate
#           （机理见 l0_01_linux，写法见 l0_03_conda 自测 L0-3-Q10）。
# 环境    ：ngs_phd_sc
# 作者    ：王运生
# 日期    ：2026-08-29
#
# 用法：
#   INDIR=data/p02/10x OUTDIR=results/p02 MT_PATTERN='^ATMG' CP_PATTERN='^ATCG' \
#   qsub 02_run_seurat.sh
# ============================================================
set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_sc

echo "[host] $(hostname)"            # 提交成功时这里不应是登录节点
echo "[time] $(date '+%F %T')"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INDIR="${INDIR:?必须指定 INDIR=CellRanger filtered_feature_bc_matrix 目录}"
OUTDIR="${OUTDIR:-results/p02}"
META="${META:-}"                     # 含 sample / condition / batch 三列的样本元数据表
MT_PATTERN="${MT_PATTERN:-^MT-}"     # 【按物种改】人 ^MT- ｜ 鼠 ^mt- ｜ 拟南芥 ^ATMG
CP_PATTERN="${CP_PATTERN:-}"         # 植物必填叶绿体前缀，如 ^ATCG
NPCS="${NPCS:-30}"
RESOLUTION="${RESOLUTION:-0.5}"
BATCH_COL="${BATCH_COL:-batch}"
VISIUM_DIR="${VISIUM_DIR:-}"         # 留空则跳过空间部分
mkdir -p "${OUTDIR}"

# 环境快照：单细胞包版本迭代快，结果必须与版本一起存档（l0_03_conda L0-3-Q9）
conda env export --no-builds > "${OUTDIR}/env_snapshot.yml"

echo "=== [1/4] Seurat 主流程 ==="
META_ARG=()
[[ -n "${META}" ]] && META_ARG=(--meta "${META}")
Rscript "${SCRIPT_DIR}/02_seurat_pipeline.R" \
        --indir "${INDIR}" --outdir "${OUTDIR}" \
        --mt-pattern "${MT_PATTERN}" --cp-pattern "${CP_PATTERN}" \
        --npcs "${NPCS}" --resolution "${RESOLUTION}" --batch-col "${BATCH_COL}" \
        "${META_ARG[@]}"

echo "=== [2/4] pseudobulk 差异表达（与 FindMarkers 对比，§⑦-2）==="
if [[ -f "${OUTDIR}/integrated.rds" ]]; then
    Rscript "${SCRIPT_DIR}/02_pseudobulk_de.R" \
            --rds "${OUTDIR}/integrated.rds" \
            --sample-col sample --celltype-col seurat_clusters --condition-col condition \
            --outdir "${OUTDIR}/de" || \
        echo "[warn] pseudobulk 跳过：元数据缺 sample/condition 列，或每组样本数 < 2"
fi

echo "=== [3/4] 细胞数与检出功效（实验设计用，§⑦-3）==="
Rscript "${SCRIPT_DIR}/02_power_cells.R" --prop 0.01 --k 10 --power 0.95 \
        --out "${OUTDIR}/power_cells.png"

echo "=== [4/4] 空间数据（可选）==="
if [[ -n "${VISIUM_DIR}" ]]; then
    Rscript "${SCRIPT_DIR}/02_spatial_visium.R" \
            --indir "${VISIUM_DIR}" --outdir "${OUTDIR}/spatial" --resolution 0.8
else
    echo "未设置 VISIUM_DIR，跳过空间部分。"
fi

echo "----------------------------------------------"
echo "检查清单（讲义 §6.2）："
echo "  1) percent.mt 是否全为 0（前缀是否匹配本物种）"
echo "  2) 整合前后 UMAP：处理特异的簇整合后还在不在（过度校正）"
echo "  3) de_comparison_summary.tsv：FindMarkers 与 pseudobulk 差几个数量级"
echo "[done] $(date '+%F %T')"
