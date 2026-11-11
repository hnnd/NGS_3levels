#!/bin/bash
#$ -S /bin/bash
#$ -N filter_sens
#$ -cwd
#$ -j y
#$ -pe smp 4
# ============================================================
# m03 统计插件配套 —— 变异过滤阈值的敏感性分析
# 环境：conda activate ngs_ms_variant
#
# 目的：讲义 ⑦ 要求学生说明"为什么用这个阈值"。
#      光说不够——本脚本把阈值扫一遍，让学生看到结论随阈值怎么变。
#      这正是"方法选择与结果可信度说明"评分项要的证据。
# ============================================================
set -euo pipefail
source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_ms_variant

# 两种调用都支持（讲义写的是 -v/-o，旧版脚本只认位置参数，UP-039）：
#   bash 03_filter_sensitivity.sh -v raw.vcf.gz -o outdir
#   bash 03_filter_sensitivity.sh raw.vcf.gz [outdir]
VCF=""; OUTDIR=""
while getopts "v:o:h" opt; do
  case "${opt}" in
    v) VCF="${OPTARG}" ;;
    o) OUTDIR="${OPTARG}" ;;
    *) echo "用法: $0 -v <raw.vcf.gz> [-o outdir]   或   $0 <raw.vcf.gz> [outdir]" >&2; exit 2 ;;
  esac
done
shift $((OPTIND - 1))
VCF="${VCF:-${1:-}}"; OUTDIR="${OUTDIR:-${2:-./filter_sensitivity}}"
[[ -n "${VCF}" && -s "${VCF}" ]] || { echo "错误：找不到输入 VCF '${VCF}'" >&2; exit 2; }
mkdir -p "${OUTDIR}"
LOG="${OUTDIR}/bcftools.log"; : > "${LOG}"

# 过滤表达式引用的 INFO 标签若在某些记录里缺失，该条件不命中、记录被静默放行（第 10 章失效条件 2）。
# 先数一遍每个标签缺失的记录数，写进报告旁边，别让「放行」被误读成「通过」。
NREC=$(bcftools view -H "${VCF}" | wc -l)
echo "记录总数：${NREC}"
for tag in QD FS MQ SOR; do
  nmiss=$(bcftools query -f "%INFO/${tag}\n" "${VCF}" 2>>"${LOG}" | grep -c '^\.$' || true)
  echo "  INFO/${tag} 缺失的记录：${nmiss}"
  [[ "${nmiss}" -gt 0 ]] && echo "  【警告】${tag} 缺失的记录不会被含 ${tag} 的条件拦下，结果中以 PASS 形式保留"
done

REPORT="${OUTDIR}/sensitivity.tsv"
printf "QD\tFS\tMQ\tSOR\tn_SNP\tn_INDEL\tTi_Tv\tmean_DP\n" > "${REPORT}"

# GATK 硬过滤推荐值附近扫描。QD 是最影响结果的一维，扫得细一些。
for QD in 1.0 2.0 3.0 5.0; do
  for FS in 30.0 60.0; do
    MQ=40.0; SOR=3.0
    expr="QD < ${QD} || FS > ${FS} || MQ < ${MQ} || SOR > ${SOR}"
    tmp="${OUTDIR}/tmp_qd${QD}_fs${FS}.vcf.gz"
    bcftools filter -e "${expr}" -O z -o "${tmp}" "${VCF}" 2>>"${LOG}"
    bcftools index -f "${tmp}" 2>>"${LOG}"
    nsnp=$(bcftools view -v snps   -H "${tmp}" | wc -l)
    nind=$(bcftools view -v indels -H "${tmp}" | wc -l)
    # Ti/Tv（脚本旧表头写 Ts/Tv，同一个比）只作代理指标：人类 WGS 的 2.0–2.1 不适用于细菌，
    # 本课 Xoo 只报告实测值并看它随阈值的变化方向，不设目标值。
    tstv=$(bcftools stats "${tmp}" 2>>"${LOG}" | awk '/^TSTV/{print $5; exit}')
    mdp=$(bcftools query -f '%INFO/DP\n' "${tmp}" 2>>"${LOG}" | awk '$1!="."{s+=$1;n++} END{if(n) printf "%.1f", s/n; else print "NA"}')
    printf "%s\t%s\t%s\t%s\t%d\t%d\t%s\t%s\n" "${QD}" "${FS}" "${MQ}" "${SOR}" \
           "${nsnp}" "${nind}" "${tstv:-NA}" "${mdp}" >> "${REPORT}"
    rm -f "${tmp}" "${tmp}.csi"
  done
done

echo "敏感性表已生成：${REPORT}"
column -t "${REPORT}"
cat <<'NOTE'

怎么读这张表：
  · 网格是 QD 4 档 × FS 2 档 = 8 组（MQ、SOR 固定）；「宽 / 严」是读表口径，不是另跑三组。
  · n_SNP 随阈值放松单调上升是正常的；看 Ti/Tv 是否随之下降——随机错误没有转换偏好，
    放松后 Ti/Tv 明显下滑提示新放进来的位点里错误比例升高。不要套用人类 2.0–2.1 的目标值。
  · bcftools 的报错与警告在 bcftools.log，跑完先看一眼。
  · 报告里要写：我选了哪一组阈值、Ts/Tv 是多少、比相邻档位好在哪。
    只写"按 GATK 推荐值过滤"拿不到"方法选择与结果可信度说明"的分。
NOTE
