#!/bin/bash
#$ -S /bin/bash
#$ -N p04_structure
#$ -cwd
#$ -j y
#$ -pe smp 8
#$ -l h_vmem=16G
# ============================================================
# 脚本名称：04_popgen_structure.sh
# 功能描述：p04 群体遗传学基础 —— LD 剪枝 → LD 衰减曲线 → PCA → ADMIXTURE(K 遍历 + CV)
#           → 亲缘/重复样本检查 → TreeMix 输入与迁移边遍历 → 生成交给 p05 的交付清单
# 作者：王运生
# 日期：2026-08-29
# 提交方式：qsub 04_popgen_structure.sh      【禁止在登录节点直接 bash 运行】
# 配套讲义：02_lectures/phd/topic04_popgen/04_popgen_lecture.md §5.5–5.6、⑥ 6.3
# ============================================================
#
# 设计要点（讲义 §4.4、§4.5、⑨）：
#   1) --ld-window-r2 0 必须显式写。PLINK 的默认值是 0.2，不写会让 LD 衰减
#      曲线的尾部凭空消失（⑨ E5），而且**不报错**。
#   2) --ld-window-kb 与 --ld-window 必须同时给。PLINK 1.9 默认并不会全基因组
#      两两计算（默认 --ld-window-kb 1000，且 --ld-window 只看相邻少数几个 SNP），
#      真正的静默问题是三重默认裁剪让 LD 曲线残缺而不报错。本脚本把 --ld-window
#      放到 99999 解除个数上限，此时必须靠 --ld-window-kb 限定物理距离，
#      否则输出量会随 SNP 数急剧膨胀（讲义 ⑨ E6 的「数百 GB」只在这种情形下成立）。
#   3) ADMIXTURE 不使用染色体信息，但读 .bim 时对染色体编码有内建假设：
#      非人类染色体名会让它直接退出（⑨ E3）。把第一列整列置 0 是通行解法，
#      不改变任何基因型。
#   4) CV error 曲线**不是**用来断言"真实亚群数"的（讲义 §4.5、⑦ 7.4）。
#      本脚本用多个随机种子重复，输出均值与波动范围，逼你按范围而非单点判读。
#
# 环境变量：
#   BFILE     PLINK 前缀（04_popgen_qc_diversity.sh 产出的 struct）  默认 ./popgen/struct
#   OUTDIR    输出目录                                              默认 与 BFILE 同目录
#   KMIN/KMAX ADMIXTURE 的 K 范围                                    默认 2 / 8
#   REPS      每个 K 的重复次数（不同随机种子）                      默认 3
#   MAXKB     LD 计算的最大物理距离（kb）                            默认 500
#   BINBP     LD 衰减曲线的分箱宽度（bp）                            默认 1000
#   ROOTPOP   TreeMix 外群名（缺省则不跑 TreeMix）
# ============================================================

set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_popgen

for tool in plink admixture Rscript awk; do
    command -v "${tool}" >/dev/null || { echo "[FATAL] ${tool} 不在 PATH，环境没激活成功"; exit 1; }
done

BFILE="${BFILE:-./popgen/struct}"
OUTDIR="${OUTDIR:-$(dirname "${BFILE}")}"
KMIN="${KMIN:-2}"; KMAX="${KMAX:-8}"; REPS="${REPS:-3}"
MAXKB="${MAXKB:-500}"; BINBP="${BINBP:-1000}"
THREADS="${NSLOTS:-8}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "${OUTDIR}"; cd "${OUTDIR}"
BASE=$(basename "${BFILE}")
NIND=$(wc -l < "${BFILE}.fam")
echo "[INFO] $(date '+%F %T') 个体数 ${NIND}；标记数 $(wc -l < "${BFILE}.bim")"

# ---- 1) LD 剪枝：给 PCA / ADMIXTURE / TreeMix 用的近似独立标记集 ----
plink --bfile "${BFILE}" --allow-extra-chr --indep-pairwise 50 10 0.2 --out prune
plink --bfile "${BFILE}" --allow-extra-chr --extract prune.prune.in --make-bed --out "${BASE}.pruned"
NPRUNE=$(wc -l < prune.prune.in)
echo "[INFO] 剪枝后标记数 ${NPRUNE}（< 1 万时 PCA 不稳；这个数同时是 p05 估 M_eff 的粗略上界）"

# ---- 2) LD 衰减曲线（注意 --ld-window-r2 0）----
plink --bfile "${BFILE}" --allow-extra-chr --r2 \
      --ld-window 99999 --ld-window-kb "${MAXKB}" --ld-window-r2 0 --out ld
Rscript "${SCRIPT_DIR}/04_ld_decay_plot.R" ld.ld "${MAXKB}" "${BINBP}" ld_decay "${NIND}"

# ---- 3) PCA + 伪影排查（PC 是否与缺失率相关 → 技术批次伪装成结构）----
plink --bfile "${BASE}.pruned" --allow-extra-chr --pca 10 --out pca
if [[ -s qc.imiss ]]; then
    awk 'NR>1{m[$1]=$5} END{}' qc.imiss > /dev/null
    awk 'NR==FNR{if(FNR>1) m[$1]=$5; next} {print $2"\t"$3"\t"$4"\t"(($2 in m)?m[$2]:"NA")}' \
        qc.imiss pca.eigenvec > pc_vs_missing.tsv
    echo "[INFO] pc_vs_missing.tsv：PC1/PC2 与个体缺失率并表，请自行算相关（讲义 6.1）"
fi

# ---- 4) 亲缘关系与重复样本（p05 要用来剔重复）----
plink --bfile "${BASE}.pruned" --allow-extra-chr --genome --out relatedness
awk 'NR>1 && $10>0.9 {print $1"\t"$2"\t"$3"\t"$4"\t"$10}' relatedness.genome > duplicate_pairs.tsv
echo "[INFO] PI_HAT > 0.9 的疑似重复样本对：$(wc -l < duplicate_pairs.tsv) 对"

# ---- 5) ADMIXTURE：K 遍历 × 多种子重复 ----
# 染色体列置 0（⑨ E3）。备份原 .bim 以便回查。
cp "${BASE}.pruned.bim" "${BASE}.pruned.bim.orig"
awk 'BEGIN{OFS="\t"}{$1="0"; print}' "${BASE}.pruned.bim.orig" > "${BASE}.pruned.bim"

: > cv_error_raw.tsv
for K in $(seq "${KMIN}" "${KMAX}"); do
    for R in $(seq 1 "${REPS}"); do
        SEED=$((1000 + R))
        admixture --cv=5 -s "${SEED}" -j"${THREADS}" "${BASE}.pruned.bed" "${K}" \
            > "log_K${K}_r${R}.out" 2>&1
        mv "${BASE}.pruned.${K}.Q" "${BASE}.K${K}.r${R}.Q"
        mv "${BASE}.pruned.${K}.P" "${BASE}.K${K}.r${R}.P"
        CV=$(grep -o 'CV error.*: [0-9.]*' "log_K${K}_r${R}.out" | awk '{print $NF}')
        printf '%s\t%s\t%s\n' "${K}" "${R}" "${CV:-NA}" >> cv_error_raw.tsv
    done
done
awk '{s[$1]+=$3; ss[$1]+=$3*$3; n[$1]++} END{
       print "K\tCV_mean\tCV_sd\tn_reps";
       for(k in n){m=s[k]/n[k]; v=(n[k]>1)?(ss[k]/n[k]-m*m):0; printf "%s\t%.5f\t%.5f\t%d\n", k, m, (v>0?sqrt(v):0), n[k]}}' \
    cv_error_raw.tsv | sort -n > cv_error.tsv
echo "[INFO] CV error（均值 ± sd）："; cat cv_error.tsv
cat <<'EOF'
[提醒] CV error 最小的 K **不是**"真实亚群数"（讲义 §4.5、⑦ 7.4）。
       曲线单调下降 / 长平台是常态；重复间 sd 大于相邻 K 的差值时，这两个 K 不可比。
       报告时并排展示 K = KMIN..KMAX，并用独立证据（地理、寄主、抗性）解释每个成分。
EOF

# ---- 6) TreeMix（可选）----
if [[ -n "${ROOTPOP:-}" && -s pop.treemix.frq.gz ]]; then
    for M in 0 1 2 3 4 5; do
        treemix -i pop.treemix.frq.gz -m "${M}" -k 500 -root "${ROOTPOP}" -o "tm_m${M}"
    done   # -k 500：把相邻 500 个 SNP 打包成块以抵消 LD，不设会严重低估标准误
    echo "[INFO] TreeMix 完成。加几条边看残差矩阵 + 似然增量 + 解释力（讲义 §4.5 末段）"
else
    echo "[WARN] 未设 ROOTPOP 或缺 pop.treemix.frq.gz，跳过 TreeMix"
fi

# ---- 7) 交付清单（p05 的输入，讲义 ⑥ 6.3）----
{
  echo "# p04 → p05 交付清单  生成于 $(date '+%F %T')"
  echo "genotype_gwas       ${OUTDIR}/${BASE}.{bed,bim,fam}      # 已滤 MAF，GWAS 输入"
  echo "genotype_pruned     ${OUTDIR}/${BASE}.pruned.*           # LD 剪枝集，算 PCA 与 K 用"
  echo "pca                 ${OUTDIR}/pca.eigenvec / .eigenval   # Q 协变量"
  echo "relatedness         ${OUTDIR}/relatedness.genome, duplicate_pairs.tsv"
  echo "drop_individuals    ${OUTDIR}/drop_indv.txt"
  echo "ld_decay            ${OUTDIR}/ld_decay.txt               # 半衰距离 → p05 的候选区间宽度"
  echo "n_eff_upper_bound   ${NPRUNE}                            # 估 M_eff 的粗略上界"
  echo "admixture_Q         ${OUTDIR}/${BASE}.K*.r*.Q, cv_error.tsv"
} > deliverables_to_p05.txt
cat deliverables_to_p05.txt
echo "[INFO] $(date '+%F %T') 完成"
