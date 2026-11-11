#!/bin/bash
#$ -S /bin/bash
#$ -N p03_effector
#$ -cwd
#$ -j y
#$ -pe smp 16
#$ -l h_vmem=16G
# ============================================================
# 脚本名称：03_effector_screen.sh
# 功能描述：p03 宿主-病原互作组学 —— OrthoFinder 物种特异基因 + 效应子三步 + 宿主 NLR 扫描
# 作者：王运生
# 日期：2026-08-29
# 提交方式：qsub 03_effector_screen.sh       【禁止在登录节点直接 bash 运行】
# 配套讲义：02_lectures/phd/topic03_host_pathogen/03_host_pathogen_lecture.md §5.5、§4.6–4.8
# ============================================================
#
# 【必读·两个工具不在 conda 环境里】（契约 env_exempt_tools）
#   SignalP 6.0 : DTU 学术许可，需在
#                 https://services.healthtech.dtu.dk/services/SignalP-6.0/ 申请下载后
#                 pip install signalp-6-package/  装进 ngs_phd_interaction
#   EffectorP 3.0: git clone https://github.com/JanaSperschneider/EffectorP-3.0
#                 用 EFFECTORP_PY 指向其 EffectorP.py
#   不要 conda install signalp / effectorp（讲义 ⑨-E6）。
#
# 【必读·输入前提】（讲义 §4.6-2）
#   PROT_DIR 下每菌株一个 .faa，**全部菌株必须用同一注释流程、同一版本、同一参数产生**，
#   否则得到的"物种特异基因"是注释伪影而非生物学差异。
#
# 【必读·适用边界】（讲义 §4.7 红线）
#   本流水线仅适用于真菌 / 卵菌病原。细菌 III 型分泌效应子无经典信号肽，
#   SignalP 这一步就已把它们排除，EffectorP 的训练集也不含它们——细菌体系请另择方案。

set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_interaction

# ---------------------------------------------------------------- 参数
PROT_DIR="${PROT_DIR:?必须指定 PROT_DIR=各菌株统一注释的 .faa 目录}"   # 【主线数据待定】
FOCAL="${FOCAL:?必须指定 FOCAL=目标（强致病）菌株名，即其 faa 的文件名主干}"
HOST_PROT="${HOST_PROT:?必须指定 HOST_PROT=宿主蛋白 fasta（NLR 扫描用）}"
PFAM_HMM="${PFAM_HMM:?必须指定 PFAM_HMM=Pfam-A.hmm 路径}"
EFFECTORP_PY="${EFFECTORP_PY:?必须指定 EFFECTORP_PY=EffectorP-3.0/EffectorP.py 路径}"
ORGANISM="${ORGANISM:-eukarya}"          # signalp6 --organism；真菌/卵菌用 eukarya
OUTDIR="${OUTDIR:-./p03_screen}"
THREADS="${NSLOTS:-16}"
NLR_PFAM="${NLR_PFAM:-PF00931 PF00560 PF07723 PF01582}"   # NB-ARC / LRR×2 / TIR

ORTHO="${OUTDIR}/ortho"; SEC="${OUTDIR}/secretome"; NLR="${OUTDIR}/nlr"
mkdir -p "${ORTHO}" "${SEC}" "${NLR}"

for tool in orthofinder diamond seqkit hmmscan hmmpress; do
    command -v "${tool}" >/dev/null || { echo "[FATAL] ${tool} 不在 PATH，环境没激活成功"; exit 1; }
done
command -v signalp6 >/dev/null || {
    echo "[FATAL] 找不到 signalp6。它不随 bioconda 分发，见本脚本头部说明"; exit 1; }
[[ -f "${EFFECTORP_PY}" ]] || { echo "[FATAL] EFFECTORP_PY 路径无效：${EFFECTORP_PY}"; exit 1; }

# ---------------------------------------------------------------- 步骤一：清洗蛋白 header
# OrthoFinder 只取第一个空格前的 accession，带描述的 header 极易跨文件撞名（讲义 ⑨-E5）
echo "=== [1/5] 清洗蛋白 FASTA header ==="
CLEAN="${ORTHO}/proteomes_clean"; mkdir -p "${CLEAN}"
for faa in "${PROT_DIR}"/*.faa; do
    sp=$(basename "${faa}" .faa)
    seqkit replace -p '\s.*' -r '' -w 0 "${faa}" \
      | seqkit replace -p '^' -r "${sp}|" -w 0 > "${CLEAN}/${sp}.faa"
done

# ---------------------------------------------------------------- 步骤二：OrthoFinder
echo "=== [2/5] OrthoFinder 直系同源聚类 ==="
[[ -d "${ORTHO}/out" ]] || orthofinder -f "${CLEAN}" -t "${THREADS}" -a 4 -S diamond \
                                       -o "${ORTHO}/out"
RES=$(find "${ORTHO}/out" -maxdepth 2 -type d -name 'Results_*' | head -1)
[[ -n "${RES}" ]] || { echo "[FATAL] 找不到 OrthoFinder 结果目录"; exit 1; }

# 物种特异基因的两个来源必须都取（硕 m02 §4.5.3）：
#   ① Orthogroups_UnassignedGenes.tsv 里的孤儿基因
#   ② GeneCount.tsv 中只有 FOCAL 计数 > 0 的 orthogroup（该株内扩张的特异家族）
echo "=== [3/5] 提取 ${FOCAL} 的物种特异基因（两个来源）==="
GC="${RES}/Orthogroups/Orthogroups.GeneCount.tsv"
UA="${RES}/Orthogroups/Orthogroups_UnassignedGenes.tsv"
OG="${RES}/Orthogroups/Orthogroups.tsv"
# GeneCount.tsv 末列是 Total，故内层循环到 NF-1
awk -v f="${FOCAL}" 'BEGIN{FS="\t"} NR==1{for(i=2;i<=NF;i++) if($i==f) k=i; next}
     {n=0; for(i=2;i<NF;i++) if(i!=k && $i>0) n++; if(k && $k>0 && n==0) print $1}' \
    "${GC}" > "${ORTHO}/specific_OGs.txt"
# ① 孤儿基因：FOCAL 列在 UnassignedGenes 表里的全部条目
awk -v f="${FOCAL}" 'BEGIN{FS="\t"} NR==1{for(i=2;i<=NF;i++) if($i==f) k=i; next}
     k && $k!="" {m=split($k,a,", "); for(j=1;j<=m;j++) print a[j]}' \
    "${UA}" > "${ORTHO}/specific_genes.txt"
# ② 特异 orthogroup 内 FOCAL 的成员基因（该株内扩张的特异家族，只取 ① 会系统性漏掉）
awk -v f="${FOCAL}" 'BEGIN{FS="\t"}
     NR==FNR {want[$1]=1; next}
     FNR==1  {for(i=2;i<=NF;i++) if($i==f) k=i; next}
     k && ($1 in want) && $k!="" {m=split($k,a,", "); for(j=1;j<=m;j++) print a[j]}' \
    "${ORTHO}/specific_OGs.txt" "${OG}" >> "${ORTHO}/specific_genes.txt"
sort -u -o "${ORTHO}/specific_genes.txt" "${ORTHO}/specific_genes.txt"
echo "  物种特异基因 $(wc -l < "${ORTHO}/specific_genes.txt") 条"
echo "  ⚠ 讲义 §4.6-2：每条候选都必须用 tblastn 回查其他菌株的**基因组**复核，"
echo "    蛋白集里的缺失可能只是漏注释。本脚本不代做这一步。"

# ---------------------------------------------------------------- 步骤三：效应子三步
echo "=== [4/5] 效应子预测三步：SignalP → 跨膜排除 → EffectorP ==="
FOCAL_FAA="${CLEAN}/${FOCAL}.faa"
signalp6 --fastafile "${FOCAL_FAA}" --organism "${ORGANISM}" --format none \
         --output_dir "${SEC}/signalp" --mode fast
# prediction_results.txt：列含 ID / Prediction / 各类型概率 / CS Position
awk -F'\t' '!/^#/ && $2 != "OTHER" {print $1}' \
    "${SEC}/signalp/prediction_results.txt" > "${SEC}/secreted_ids.txt"
# 按预测切割位点切出**成熟肽**：跨膜判定必须在成熟肽上做，否则信号肽的疏水 h 区
# 会被 TMHMM 当成跨膜螺旋，把大量真效应子扔掉（讲义 §4.7）
awk -F'\t' '!/^#/ && $2 != "OTHER" {
      if (match($0, /CS pos: [0-9]+-[0-9]+/)) {
          s = substr($0, RSTART, RLENGTH); split(s, a, /[ -]/); print $1"\t"a[3]+1
      } else { print $1"\t1" } }' \
    "${SEC}/signalp/prediction_results.txt" > "${SEC}/cs_pos.tsv"
seqkit grep -f "${SEC}/secreted_ids.txt" "${FOCAL_FAA}" -w 0 > "${SEC}/secreted_full.faa"
python - "${SEC}/secreted_full.faa" "${SEC}/cs_pos.tsv" "${SEC}/mature.faa" <<'PY'
import sys
fa, cs, out = sys.argv[1], sys.argv[2], sys.argv[3]
start = {}
for line in open(cs):
    i, p = line.rstrip("\n").split("\t")
    start[i] = int(p)
name, seq = None, []
with open(out, "w") as fh:
    def flush():
        if name is not None:
            s = "".join(seq)[start.get(name, 1) - 1:]
            if s:
                fh.write(f">{name}\n{s}\n")
    for line in open(fa):
        if line.startswith(">"):
            flush(); name = line[1:].split()[0]; seq = []
        else:
            seq.append(line.strip())
    flush()
PY
# 跨膜排除：环境里的 tmhmm2 可能解不出来（DTU 许可，讲义 ⑨-E6）。
# 有则跑，无则跳过并在日志中要求手工用 DeepTMHMM 在线服务补做——不要静默略过。
if command -v tmhmm >/dev/null; then
    tmhmm "${SEC}/mature.faa" > "${SEC}/tmhmm.out"
    awk '/Number of predicted TMHs:/ {split($0,a,":"); if (a[2]+0 == 0) print $2}' \
        "${SEC}/tmhmm.out" > "${SEC}/no_tm_ids.txt"
    seqkit grep -f "${SEC}/no_tm_ids.txt" "${SEC}/mature.faa" -w 0 > "${SEC}/mature_noTM.faa"
else
    echo "  [WARN] 未找到 tmhmm：跳过跨膜排除。请用 https://dtu.biolib.com/DeepTMHMM"
    echo "         对 ${SEC}/mature.faa 补做，并在方法学中写明用的是哪个工具。"
    cp "${SEC}/mature.faa" "${SEC}/mature_noTM.faa"
fi
python "${EFFECTORP_PY}" -i "${SEC}/mature_noTM.faa" -o "${SEC}/effectorp.tsv"
echo "  ⚠ EffectorP 给的是分类器后验概率，不是 p 值；调阈值不等于控制 FDR（讲义 §4.7）"

# ---------------------------------------------------------------- 步骤四：宿主 NLR 扫描
echo "=== [5/5] 宿主 NLR 结构域扫描 ==="
[[ -f "${PFAM_HMM}.h3i" ]] || hmmpress "${PFAM_HMM}"          # 讲义 ⑨-E7
hmmscan --cpu "${THREADS}" -E 1e-5 --domtblout "${NLR}/host_pfam.domtbl" \
        -o /dev/null "${PFAM_HMM}" "${HOST_PROT}"
for acc in ${NLR_PFAM}; do
    awk -v a="${acc}" '!/^#/ && $2 ~ a {print $4}' "${NLR}/host_pfam.domtbl" | sort -u \
        > "${NLR}/hit_${acc}.txt"
done
# NLR 判据：必须有 NB-ARC，且伴随 LRR 或 TIR——只有 LRR 命中的不算（讲义 §4.8-2）
comm -12 <(sort -u "${NLR}/hit_PF00931.txt") \
         <(cat "${NLR}"/hit_PF00560.txt "${NLR}"/hit_PF07723.txt "${NLR}"/hit_PF01582.txt \
           | sort -u) > "${NLR}/nlr_candidates.txt"
echo "  NLR 候选 $(wc -l < "${NLR}/nlr_candidates.txt") 条"
echo "  ⚠ 讲义 §4.8-3：参考注释会漏 NLR，正式分析需用 NLR-Annotator 在基因组上回补。"

cat <<MSG

完成。下一步交给 03_dual_deseq2_lrt.R 做交集与排序：
  Rscript 03_dual_deseq2_lrt.R <counts/host> <counts/path> <samples.tsv> \\
          ${SEC}/effectorp.tsv ${SEC}/signalp/prediction_results.txt \\
          ${ORTHO}/specific_genes.txt <outdir>
提醒（讲义 §4.7）：本脚本产出的是**候选**，不是鉴定结果。写作时只能说"预测了 N 个候选效应子"。
MSG
