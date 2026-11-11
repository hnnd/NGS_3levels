---
title: "实验指导 p04：群体结构推断与 LD 衰减，并交付 p05 输入"
level: phd
topic: p04
textbook: [ch20]
lecture: ../02_lectures/phd/topic04_popgen/04_popgen_lecture.md
env: ngs_phd_popgen
---

# 实验指导 p04：群体结构推断与 LD 衰减，并交付 p05 输入

> 上机时手边打开的这份文件：每步回答做什么、敲什么、产出哪个文件、看到什么算对、看到什么说明错了。
> 原理与判据在教材第 20 章（§20.4 概念方法、§20.5 四条失效条件、§20.6 边界与交付、§20.7 习题、§20.9 答案解析）。
>
> **数字标注规则（全篇遵守）**：检查点里的数只来自四类合格入口——① `06_data/phd/README.md` p04 节登记值与 `06_data/phd/manifests/p04_runs.tsv` 实测（40 行 40 唯一分离株、`base_count` 合计 18 441 762 641、`fastq_bytes` 合计 11.95 GB）；② 教材正文带复现入口的数（手算式 `a_40 = 4.2535`、`1/40 = 0.025`、`18.44 Gb / (40 Mb × 40) = 11.5 ×`、`50 × 0.05² = 0.125`；`demos/ch20_*.py --selftest` 现跑输出；作业与脚本口径）；③ 教材明确标「设例／经验档位」的量（`D_T = −1.8`、全基因组 D 中位数 `+0.5`、半衰距离的百 kb / kb 量级、`AD` 比 0.25–0.75）；④ ENA 元数据现查值（每个 run 的 `library_layout` 与 `fastq_ftp` 文件数，查询命令给在 §2，属于你自己就能复核的外部事实）。真实 40 株全流程**集群未复跑**（教材 §20.6 开篇明写），故真实数据读数一律标「预期（未实测）」或只给定性判据。教材已撤下的数字（`4N_eμ` 作通用 θ、`F ≈ 1`、「两个数量级 = 100 倍」、「读数可差 2–3 倍」、「下载 12.5 GB」、「≥30 个体 / ≥10 万 SNP」）本指导一个不用。
>
> **计算纪律**：两个 shell 脚本都带 SGE 作业头（qc L6–7 `-pe smp 8` / `h_vmem=8G`，structure L6–7 `-pe smp 8` / `h_vmem=16G`），脚本头明令**禁止在登录节点直接 `bash` 运行**。登录节点只做下载、建环境、编辑、实查文件与看日志；一切计算 `qsub`。投递后无法补参数，改任何一个值都要重投。`03_code/`、`06_data/`、`07_envs/` 只读：要改值就走「`cp` 个人副本 → 改指定行 → `grep` 确认 → `qsub` 副本」。

## 0. 本实验对应什么

- **教材**：第 20 章。覆盖博士层 LO20-01（频谱三个读数与经验分位数）、LO20-02（HWE 两类偏离与倍性）、LO20-03（F_ST 估计量/求平均、结构与迁移边的解释边界）、LO20-04（LD 衰减倒推窗宽与标记密度、两套产物、最低证据标准）；硕士层 LO20-05 作选读（§20.4 开头、§20.4.2 末、§20.4.3 末三个选读块）。失效条件对应 §20.5.1–§20.5.4。
- **讲义**：p04 ② 前置表、③ 3.1、④ 4.1–4.9、⑤ 5.1–5.6、⑥ 6.1–6.2、⑦ 统计插件、⑧ AI 任务、⑨ E1–E10、⑩ 8 题、⑪ 文献。**两处编号差**：讲义 ⑤5.4 注说窗宽「依据 5.5 确立」，实际 5.5 在其后（循环依赖见 3.5 末）；交付清单在讲义是 ⑥6.2，而 `04_popgen_structure.sh` 的头注（L15）与收尾行（L123）写成「⑥ 6.3」，作业 L17/L37 同写 6.3，一律按 6.2 读。
- **学时与环境**：p04 共 4 学时（2 理论 + 2 实践，`00_design/course_contract.yaml`）；作业建议上机 5–7 小时（ADMIXTURE 多 K 多种子最耗时）、写报告 3 小时（`08_assessment/phd/assignments/p04_popgen_practice.md`）。环境 `ngs_phd_popgen`（`07_envs/conda/env_phd_popgen.yml`），**与 p05 同一个环境**，pin 情况见 §1「版本口径」。
- **三个脚本的顺序不能颠倒**：`04_popgen_qc_diversity.sh`（质控两套产物 → 缺失率 → π/Tajima's D → F_ST → HWE）必须先跑，它产出 `struct.bed/.bim/.fam`，而 `04_popgen_structure.sh` 的输入 `BFILE` 默认就是 `./popgen/struct`（L49）；`04_ld_decay_plot.R` 由结构脚本第 2 段内部调用（L69），不单独投递，但可以单独重跑某一条曲线。
- **本实验做不了的两件事**（教材 §20.1 末、§20.6）：① 40 个 run 的 fastq 到群体 VCF 的比对与变异检测**没有课程脚本**，`03_code/phd/scripts/` 里找不到 calling 脚本，本章按第 10 章的变异检测概念接住 `raw.pop.vcf.gz` 这个外部输入；② `pop.treemix.frq.gz` 与候选区间的 `top1pct.bed` **都没有生成步骤**（教材 §20.3 L92），前者只在文件存在时才跑（脚本 L114）。
- **主线是单倍体**：稻瘟菌在营养生长与侵染阶段每个位点只带一个等位基因，`--hwe` 在数学上没有对象，其输出不作技术诊断（教材 §20.4.3 选读块、§20.5.2）；θ 与 N_e 的关系一律用 `2N_eμ`。
- **交给 p05 的是格式与口径，不是这批基因型**（教材 §20.6 末）：p04 是 40 株稻瘟菌（单倍体），p05 是水稻多样性面板（二倍体），两套样本毫无重叠。`deliverables_for_p05/` 能被 p05 直接读，是因为它符合 p05 的**文件结构、字段口径与方法规格**（PLINK 三件套、`pca.eigenvec` 的 Q 协变量格式、`ld_decay.txt` 的半衰与四要素、分群定义与 `cv_error.tsv`），**不是因为真菌基因型能拿去关联水稻表型**。搬得走的是规范，搬不走的是数值。

## 1. 实验前检查

- **前置自测**（题号在 `08_assessment/prerequisites/` 逐一存在）：`l0_01_linux` 第 5、9 题（登录节点与计算节点的分工、SGE 作业投递——ADMIXTURE 多 K 循环在登录节点必被清退）；`l0_03_conda` 第 9、10 题（环境快照、批处理作业里正确激活环境）；`l0_04_formats` 第 6、7 题（BED/GFF3/GTF/VCF 的用途分工、0-based 与 1-based 的坐标偏移）；`l0_06_stats` 第 4、5、6 题（p 值语义、Bonferroni 与 FDR、批次与分层混杂）；`l0_02_r` 第 9、10 题（ggplot2 分组映射与出版级导出）；以及 `l1_phd` 第 Q1、Q2 题（群体 VCF 列解析与 `GT`/`DP`/`GQ`/`AD` 语义、基因型频数分布；`l1_p04` 的最短补课路径写「约 45 分钟」，材料为 m03 的 VCF 格式与变异过滤两节）。
- **建/激活环境并核验工具链**（建环境与下载属允许的 I/O 型任务，在登录节点做）。**在课程仓库根目录敲**：

  ```bash
  conda env create -f 07_envs/conda/env_phd_popgen.yml          # 只需一次
  source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_popgen
  for t in bcftools vcftools plink tabix bgzip awk admixture Rscript; do command -v $t; done
  command -v treemix || echo "缺 treemix：TreeMix 段会失败，见 3.11"
  plink --version | head -2 && bcftools --version | head -1
  ```

  SGE 作业不继承终端里的 conda 变量，两个脚本各自在开头激活一次（qc L37、structure L43）。`04_popgen_qc_diversity.sh` L39–41 逐个 `command -v` 检查 `bcftools vcftools plink tabix bgzip awk`；`04_popgen_structure.sh` L45–47 检查 `plink admixture Rscript awk`——**这一份没有检查 `treemix`**，TreeMix 缺不缺必须自己先查，否则作业跑到第 6 段才失败，前五段的产物才刚落盘。
- **版本口径**：`plink=1.90b6.21`、`bcftools=1.17`、`bedtools=2.31.0`、`r-base=4.3.1`、`r-ggplot2=3.4.2` 有 pin（`07_envs/conda/env_phd_popgen.yml`）；**`vcftools`、`admixture`、`treemix` 未 pin**，教材 §20.3 因此不写这三个工具的版本号，方法学里只填你激活环境后打印的实际值。参考基因组与注释的部署见 `06_data/phd/README.md` p03 节，本实验只在 `bedtools intersect` 那一步（讲义 ⑤5.6 末，本指导未展开）用 GFF3，主流程不需要。
- **脚本静态检查**（课程仓库根目录；应无输出、退出码 0、不产生文件）：

  ```bash
  bash -n 03_code/phd/scripts/04_popgen_qc_diversity.sh
  bash -n 03_code/phd/scripts/04_popgen_structure.sh
  Rscript -e "invisible(parse('03_code/phd/scripts/04_ld_decay_plot.R'))"
  ```

  **两类命令不能混**：`bash -n` 只对 `.sh` 有意义；对 `.R` 跑它会报 `syntax error near unexpected token`（R 的 `<-` 在 bash 里是另一套语法）——那是用错了检查器。R 脚本的静态检查是 `parse()`：只解析不执行。
- **自查演示**（不需要集群，四个脚本各自打印 PASS 计数与汇总行）。课程仓库根目录运行：

  ```bash
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch20_tajima_d_maf_bias.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch20_fst_average_trap.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch20_hwe_selfing_wahlund.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch20_ld_r2_baseline.py --selftest
  ```

  四组数是 3.5、3.6、3.7 的读图标尺，**都是合成算例（固定种子 20261104），只对各自的生成模型成立**：
  ① MAF 扭曲频谱 `7/7 PASS`——`S` 20000→15187（−24.1%）、`θ_W` 4701.96→3570.44（−24.1%）、`π` 4587.10→4351.03（−5.1%）、Tajima's D −0.092→+0.825（整段总量口径、π 未乘 `n/(n−1)`）；
  ② F_ST 两种平均 `7/7 PASS`——分量和之比 0.0723 对比值平均 0.0455、窗口偏差中位数 0.0279 对 0.0067、剔稀有变异后 0.0757→0.0841（1.11 倍）、按观测频率过滤反降到 0.0634，手算锚点 `N = 0.01895 / D = 0.44 / F_ST = 0.04306`；
  ③ Wahlund 与自交 `10/10 PASS`——`H_exp − H_obs = 0.1200 = 2Var(p)`、合并样本 99.6% 位点 `p < 10⁻⁶`、正确分群后 `p < 0.05` 占 4.5%、自交 `s = 0.95` 时 `F = 0.9048`（教材手算写 0.905）、`H_obs/H_exp = 0.0985`；
  ④ LD 基线 `8/8 PASS`——`n = 30` 实测 0.0347（`1/30 = 0.0333`）、`n = 200` 实测 0.0050，半衰 54.0 / 48.0 kb 与 51.0 / 50.0 kb，`r² = 0.2` 距离 111.0 / 99.0 kb 与 102.0 / 101.0 kb（真实 50 kb）。

## 2. 实验数据

- **来源与规模**：`PRJEB53625`，稻瘟病菌（*Pyricularia oryzae*）全球分离株群体重测序集合，登录号已在 `06_data/accessions.tsv` L13 登记。全研究含 257 个 run，课程按 `base_count` 落在 **0.4–1.5 Gb** 筛出候选，取 **40 个分离株**。这个区间是**筛选条件、不是实测跨度**（教材 §20.1）。
- **这 40 个 run 全部是双端（PAIRED）**（2026-11-11 按 ENA filereport 逐条核对 manifest 的 40 个 run 号）：每个 run 有 2 个 `fastq.gz`（R1 + R2），所以落盘是 **80 个文件对应 40 个分离株**。这不是下载重复，也不是你的命令写错了。自己复核一条即可（登录节点）：`curl -s "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=RRRRRRRR&result=read_run&fields=run_accession,library_layout,fastq_ftp&format=tsv"`，把 `RRRRRRRR` 换成 manifest 里任一个 run 号，看 `library_layout` 是不是 `PAIRED`、`fastq_ftp` 是不是两个分号分隔的 URL。**判断样本量永远按分离株数（R1 文件数）算，不按文件总数算。**
- **`fastq_bytes` 这一列不能用来核对落盘字节数**：40 行里有 3 行（`ERR9860934`、`ERR9860956`、`ERR9861104`）只记了 R1 的大小，其余 37 行是两文件之和。所以拿 `ls -l` 去逐行对 `fastq_bytes` 会有 3 行「对不上」，那不是你下载错了；完整性核对只认 3.1 的文件计数、`md5` 校验与 `sha256.txt`。
- **manifest 实查（2026-11-05，`06_data/phd/manifests/p04_runs.tsv`）**：4 列 `run_accession / isolate / base_count / fastq_bytes`；**40 行 = 表头 + 40 个唯一分离株**（`cut -f2 | sort | uniq -d` 为空）；`base_count` 403 747 920–510 291 172（**0.404–0.510 Gb**）、中位 464 865 681（0.465 Gb）、合计 18 441 762 641（**18.44 Gb**）；`fastq_bytes` 合计 11 954 035 620（**11.95 GB**，这是该列原样求和，其中 3 行只记了 R1 故略低于实际字节数）。名义深度 `18.44 Gb / (40 Mb × 40) = 11.5×`（手算，只用到 `base_count`）。**名义深度不是覆盖度**（`TERMINOLOGY.md` §2：覆盖度指被至少一条读段覆盖的基因组比例，本讲不报这个数）。README p04 与作业写的「12.5 GB」与 manifest 求和差约 4%，一律按 manifest 的 11.95 GB 记，**不要拿它当下载量承诺或完整性判据**。
- **下载**（登录节点做）：

  ```bash
  bash 06_data/phd/download_phd.sh --topic p04                   # 先 dry-run 看命令
  bash 06_data/phd/download_phd.sh --topic p04 --run \
       --outdir /d3/scratch/${USER}/ngs/data                      # 真下：manifest 求和 11.95 GB（实际略高，见上条）
  ```

  落盘在 `--outdir` 下的 `p04_popgen/`，每株每个 run 出 `<isolate>_<序号>.fastq.gz`（`i` 从 1 起，双端就是 `_1` 与 `_2`；下载循环见 `download_phd.sh` 的 `fetch_p04`，L124–157），另写 `sha256.txt`（L153）。脚本 L131–135 已内建**重复检测告警**（`cut -f2 | sort | uniq -d` 非空即打印），L144 对 ENA 返回空 body 有守卫，L151 做 md5 校验。
- **开工前先把两个工作变量定下来**（在你自己的登录 shell 里敲，之后每一步都靠它们；`qsub` 作业**不会**继承，见 3.2）：

  ```bash
  export P04=/d3/scratch/${USER}/ngs/data/p04_popgen   # 原始 fastq 所在目录
  export Q=$P04/work/popgen                            # 所有产物的目录
  mkdir -p "$Q" "$P04/work/pops"
  ls "$P04"/*.fastq.gz | wc -l                         # 应为 80（40 株 × 双端两文件）
  ```

- **为什么必须先查唯一性**：产物按样本名落盘，同一分离株出现多次时后一个 run **静默覆盖**前一个，产物数减少而退出码仍是 0（教材 §20.5.4 后半记录了真实发生过的一次：`p04_runs.tsv` 40 行、`O23` 出现 3 次、`i76a` 出现 2 次，实际只落地 37 株，2026-08-30 去重并补入 `i77a`、`i57a`、`d54a` 后恢复 40/40）。所以**完成判据用产物计数对 manifest 行数，不用退出码**。
- **入口数据缺口：课程没有给你 VCF**。`VCF=raw.pop.vcf.gz` 是**外部输入**，`03_code/phd/scripts/` 里没有 fastq→群体 VCF 的比对与变异检测脚本（教材 §20.1 L36、§20.6 L418），`06_data/` 也不发布成品群体 VCF——所以本指导**给不出一个「公共路径」**，给的是两条可选来源与一道入口检查：
  1. 按第 10 章的概念自己做比对与 calling（不在本讲学时内，工作量远大于其余全部步骤）；
  2. 用你课题组已有的、同一物种的群体 VCF（注意：单倍体、双等位 SNP、样本名可与 manifest 对上）。

  来源定了之后，投递前先过这道检查（把 `VCF=` 换成你自己的绝对路径）：

  ```bash
  VCF=$P04/work/raw.pop.vcf.gz          # 换成你实际的路径
  ls -lh "$VCF"                                        # 必须存在且非空
  bcftools view -h "$VCF" | tail -1 | cut -f1-3        # 看表头样本名从哪一列开始
  bcftools query -l "$VCF" | wc -l                     # 样本数：后面的 1/n 基线、n(n−1)/2 群对都从这里算
  bcftools index -n "$VCF" 2>/dev/null || { tabix -f -p vcf "$VCF"; bcftools index -n "$VCF"; }   # 位点数；没索引现建
  ```

- **README 的自查判据只能当预期形态读**（unverified，不是实测）：40 株、单倍体、40 Mb 基因组，「过滤后 SNP 在十万量级」；PCA 前几个主成分应能分出可辨认的几群；若 PC1 只把一两个样本甩出去而其余挤成一团，优先怀疑深度或污染。本指导把这三条写成定性判据，不给合格数字。

## 3. 实验步骤

> 每步五栏：**目的 / 命令 / 产出文件 / 检查点 / 出错信号（→ 教材节号）**。命令调用 `03_code/phd/scripts/` 现有脚本，不复制全文；脚本名、参数名、输出文件名已逐个与现版源码核对（行号对现版）。真实数据全流程**集群未复跑**：真实样本结果的检查点一律标「预期（未实测）」或定性。原始数据目录 `P04=/d3/scratch/${USER}/ngs/data/p04_popgen`，产物目录 `Q=$P04/work/popgen`（两个变量在 §2 末尾 export；重开终端要重敲一次）。**`qsub` 作业不继承你终端里的变量**：两个脚本的作业头都没有 `-V`，所以脚本里的路径必须写成字面绝对路径（3.2 详述）。**脚本是幂等的**：qc 脚本在 `gtmask.vcf.gz` 非空时跳过第 0 段（L56）；structure 脚本每段都会覆盖重写。想重算必须先删对应产物并清空输出目录，否则旧文件会掩盖新缺失。

### 3.1 落盘、manifest 唯一性校验与样本账

- **目的**：把 40 个 run 落到本地，并在开工前用独立计数确认「manifest 40 行 = 40 个唯一分离株 = 40 个 R1 文件 = 80 个 fastq.gz」。这是全篇最容易「跑成功却少样本」的一步，错的时候不报错。
- **命令**（登录节点；`$M` 指向 manifest）：

  ```bash
  M=06_data/phd/manifests/p04_runs.tsv
  tail -n +2 "$M" | cut -f2 | sort | uniq -d          # ① 必须无输出
  tail -n +2 "$M" | cut -f2 | sort -u | wc -l        # ② 必须 40（唯一分离株）
  ls "$P04"/*.fastq.gz   | wc -l                     # ③ 必须 80（40 株 × 双端两文件）
  ls "$P04"/*_1.fastq.gz | wc -l                     # ④ 必须 40（按 R1 数株）
  comm -3 <(tail -n +2 "$M" | cut -f2 | sort -u) \
          <(ls "$P04"/*_1.fastq.gz | sed 's#.*/##; s#_1\.fastq\.gz$##' | sort -u)   # ⑤ 必须无输出
  awk -F'\t' 'NR>1{b+=$3; if(min==""||$3<min)min=$3; if($3>max)max=$3}
              END{printf "total=%.2fGb min=%.3f max=%.3f\n", b/1e9, min/1e9, max/1e9}' "$M"
  ```

- **产出文件**：`$P04/<isolate>_<i>.fastq.gz`（双端每株 `_1` 与 `_2` 两个文件，`i` 从 1 起）、`$P04/sha256.txt`。
- **检查点**：① ①–⑤ 五个数必须齐——① 无输出、② 40、③ 80、④ 40、⑤ 无输出（**名字**也对上，不只是数量），**不看退出码**；② `awk` 打印 `total=18.44Gb min=0.404 max=0.510`，与 manifest 实测一致（0.404–0.510 Gb、中位 0.465 Gb、合计 18.44 Gb、`fastq_bytes` 合计 11.95 GB）；③ 名义深度自己算一遍：`18.44 / (0.04 × 40) = 11.5×`，并写明这是名义深度不是覆盖度；④ 每株的 run 数与 `base_count` 抄进 §4——方法学里的样本量与名义深度都从这张表算，**不从 README 抄**。
- **出错信号**：③ 是 80 而你以为「多了 40 个」→ 双端就是这样，按 ④ 的数记样本量；④ 少于 ② 而 rc=0 → 同名覆盖（教材 §20.5.4 后半，这就是那次「40 行落地 37 株」的形态）；⑤ 有输出 → 数量对得上但名字对不上（改名、补下、漏下都会被它抓出来），逐行看 `comm` 左列（manifest 有、磁盘无）与右列（磁盘有、manifest 无）；日志里 `ENA 无 fastq 或响应为空（可重跑续传）` → ENA 在高并发下返回空 body 而 curl 仍 rc=0，重跑续传即可；`md5 不符` → 续传残片或文件被截断，删掉重下；① 有输出而继续往下做 → 你已经接受了「样本量悄悄变小」，后面的 1/40 基线、F_ST 抽样方差全部要按实际株数重算（教材 §20.5.4）。

### 3.2 作业目录与参数落位

- **目的**：把两个脚本各抄一份个人副本、把必填变量写进副本并 `grep` 确认，然后才投递。脚本用 `${VCF:?…}` 这类空值即退出的写法（qc L43），变量必须真的进到脚本里。
- **命令**（`$P04`、`$Q` 用 §2 末尾 export 的值；`<课程仓库路径>` 换成你机器上 `NGS_3Levels` 的实际路径）：

  ```bash
  cd $P04/work
  cp <课程仓库路径>/03_code/phd/scripts/04_popgen_qc_diversity.sh ./qc_diversity.sh
  cp <课程仓库路径>/03_code/phd/scripts/04_popgen_structure.sh     ./structure.sh
  cp <课程仓库路径>/03_code/phd/scripts/04_ld_decay_plot.R         ./04_ld_decay_plot.R
  # 用编辑器在 qc 副本 L43 之前插入三行（写**字面绝对路径**，不要写 $P04 / $Q）：
  #   VCF=/d3/scratch/<你的用户名>/ngs/data/p04_popgen/work/raw.pop.vcf.gz
  #   OUTDIR=/d3/scratch/<你的用户名>/ngs/data/p04_popgen/work/popgen
  #   POPS=/d3/scratch/<你的用户名>/ngs/data/p04_popgen/work/pops
  # 在 structure 副本 L49 之前插入两行（同样写字面绝对路径）：
  #   BFILE=/d3/scratch/<你的用户名>/ngs/data/p04_popgen/work/popgen/struct
  #   OUTDIR=/d3/scratch/<你的用户名>/ngs/data/p04_popgen/work/popgen
  grep -n 'VCF=\|OUTDIR=\|POPS=\|WIN=\|STEP=\|MINDP=\|MINGQ=\|h_vmem\|-pe' qc_diversity.sh
  grep -n 'BFILE=\|OUTDIR=\|KMIN=\|KMAX=\|REPS=\|MAXKB=\|BINBP=\|ROOTPOP\|h_vmem\|-pe' structure.sh
  ```

  三条必须遵守的理由，每条都来自脚本本身的写法：

  1. **为什么写字面路径**：`qsub` 只把作业脚本交给调度器，**不传递你当前 shell 的环境变量**（作业头没有 `-V`）。而两个脚本都 `set -euo pipefail`，`${VCF:?}`、`${BFILE:-…}` 之外任何未定义变量都会让作业立刻退出。写 `$P04/work/...` 在脚本里等于引用一个作业进程中不存在的变量。
  2. **为什么把 R 脚本一起拷到 `work/`**：`structure.sh` 第 69 行用 `${SCRIPT_DIR}/04_ld_decay_plot.R` 调用拟合脚本，而 `SCRIPT_DIR`（L54）是**当前脚本所在目录**，不是课程仓库。只拷两个 `.sh` 会在 LD 衰减那一段报 `No such file`。
  3. **为什么不写 `VCF=… qsub script.sh`**：那个前缀只给 `qsub` 命令自身设环境变量，不转交给作业进程。`qsub -v` 是另一种可行写法，但本机无 SGE、集群未实测，统一走「改副本 + `grep` 确认」。

- **产出文件**：`$P04/work/qc_diversity.sh`、`$P04/work/structure.sh`、`$P04/work/04_ld_decay_plot.R`（个人副本三件套）。
- **检查点**：两条 `grep` 各能看到你写的赋值行与作业头；qc 副本里 `OUTDIR`、`POPS`、`VCF` 三个都在，structure 副本里 `BFILE` 与 `OUTDIR` 都在，且写进去的是 `/d3/scratch/…` 开头的绝对路径（不是 `$P04`、不是 `/abs/`）；除 3.10 要你改的 `REPS` 外，脚本默认值保持不变（`WIN=50000`、`STEP=10000`、`MINDP=5`、`MINGQ=20` 见 qc L46–49；`KMIN=2`、`KMAX=8`、`MAXKB=500`、`BINBP=1000` 见 structure L51–52，`REPS` 默认 3）。
- **出错信号**：`必须指定 VCF=群体 VCF（bgzip 压缩且已建 tabix 索引）`（qc L43 原文）→ 赋值行没进副本，或写在 `${VCF:?}` 之后；`[FATAL] plink 不在 PATH，环境没激活成功`（structure L46 原文）→ 见 1 的环境自检；作业日志里出现 `unbound variable` 并秒退 → 你把 `$P04` / `$Q` 写进了脚本，改成字面绝对路径；`04_ld_decay_plot.R: No such file or directory` → R 脚本没拷到 `work/`；两个副本的同名产物落进同一目录导致互相覆盖 → 从现在起就把 `OUTDIR` 固定成一个目录。

### 3.3 群体层质控与两套产物

- **目的**：从外部 VCF 起步，先取双等位 SNP、把低质量基因型**置缺失而不删位点**，再由同一个 `gtmask` 分出两套产物：`popgen.vcf.gz` **不滤 MAF**（供 π、θ_W、Tajima's D、SFS），`struct.vcf.gz` **滤 MAF**（供 LD、PCA、ADMIXTURE、TreeMix，也是按 p05 的 GWAS 输入规范交付的那套基因型）。只产出一套就交，是本讲最常见的系统性错误。
- **命令**（`qsub`；同一作业的第 0、1 段）：

  ```bash
  cd $P04/work && qsub qc_diversity.sh && qstat -u "$USER"
  ```

  脚本这一段做什么：L56 判 `gtmask.vcf.gz` 非空则**跳过**第 0 段；L57 `bcftools view -m2 -M2 -v snps`；L58–59 `bcftools filter -S . -e 'FMT/DP<5 | FMT/GQ<20'`（**置缺失，不删位点**）；L60 `tabix -f -p vcf`；L65–67 `vcftools --max-missing 0.8 --min-alleles 2 --max-alleles 2`（不滤 MAF）；L69–71 `--max-missing 0.9 --maf 0.05`；两套都用 `--recode --recode-INFO-all --stdout | bgzip -c` 并各跟一次 `tabix -f -p vcf`；L73–76 打印三套位点数。
- **产出文件**：`$Q/biallelic.vcf.gz`、`$Q/gtmask.vcf.gz`、`$Q/popgen.vcf.gz`、`$Q/struct.vcf.gz` 及三份 `.tbi` 索引。
- **检查点**：① **四个 VCF 与三份索引都在**（`ls $Q/*.vcf.gz* | wc -l` 应为 **7**：`biallelic`/`gtmask`/`popgen`/`struct` 四个 VCF ＋ 后三个的 `.tbi`；`biallelic.vcf.gz` **没有**索引，脚本 L57 生成它时不建，别去数第 8 个文件）。索引不可缺——缺了 `bcftools view -r` 一类命令会整片失败；② 把 L73–76 打印的三个位点数抄进 `qc_summary.tsv`（输入 / `popgen` / `struct`），**没有合格阈值**：教材与 README 都没给「过滤后应剩多少」，README 的「十万量级」是未实测预期，你只能写「本次实测 X 个，与预期量级是否相符」；③ 两套产物位点数**关系要看方向**：`struct` 比 `popgen` 少是正常的（MAF 0.05 与更严的 `--max-missing` 都在起作用），`struct` 暴跌到接近零则先查 `--max-missing` 方向（vcftools 的 `--max-missing` 是**保留**比例，PLINK 的 `--geno` 是剔除阈值）。**两者接近或相等时不要下「MAF 没生效」的结论**——输入里本来就没有低于 0.05 的位点时，结果也会相等。按下面两条去查，把它当**待复查项**：

  ```bash
  grep -n -- '--maf 0.05' qc_diversity.sh                       # 参数真的在副本里
  vcftools --gzvcf $Q/struct.vcf.gz --freq --stdout \
    | awk 'NR>1{for(i=5;i<=NF;i++){split($i,a,":"); f=a[2]+0; if(f>0){m=(f<1-f)?f:1-f; if(min==""||m<min)min=m}}} END{print "min MAF =", min}'   # 应为 0.05 附近或更高
  ```

  第一条查到参数、第二条查到 MAF 分布的最低端，两条都过才叫「MAF 生效了」；只看「位点数没怎么变」既可能是参数没执行，也可能是没有低频位点可滤，单看计数分不开。

  ④ `gtmask` 的位点数应比 `biallelic` **少或相等而不该大幅减少**——置缺失不删位点，位点数只因全样本缺失而减少。
- **出错信号**：只出现一套 `popgen`/`struct` → 照抄了单过滤脚本；`[E::bgzf_read] … not compressed with bgzip` 或下游 `bcftools: index file not found` → 少了 `tabix -f -p vcf`（漏索引与漏 `--recode-INFO-all` 都是「命令里少写一个参数」，不会在跑的时候报错，只会在下游暴露）；`gtmask.vcf.gz` 已存在而位点数和上次一模一样 → 第 0 段被跳过（L56），改 `MINDP`/`MINGQ` 后必须删掉它再投递（→ 教材 §20.4.7）。

### 3.4 个体缺失率清单（并说明清单不等于已剔除）

- **目的**：先算每个个体的缺失率分布，再决定剔除谁。这一步产出的是**名单**，不是过滤动作。
- **命令**：同一作业第 2 段（L79–81）：

  ```bash
  # 脚本已执行：vcftools --gzvcf popgen.vcf.gz --missing-indv --out qc
  #             awk 'NR>1 && $5>0.2 {print $1}' qc.imiss > drop_indv.txt
  awk 'NR>1{print $5}' $Q/qc.imiss | sort -g | awk '{a[NR]=$1} END{printf "P10=%.4f P50=%.4f P90=%.4f max=%.4f\n", a[int(NR*0.1)+1], a[int(NR*0.5)+1], a[int(NR*0.9)+1], a[NR]}'
  ```

  阈值 0.2 是**脚本设定**（L80），不是数据分位——所以上面这条分位数命令是必做的：你要在报告里说清 0.2 落在你的分布哪个位置。
- **产出文件**：`$Q/qc.imiss`、`$Q/drop_indv.txt`（**只有这两个**：这一段跑的是 `--missing-indv`，个体层面；位点层面的 `lmiss` 在 3.6 由 PLINK `--missing` 产出，文件名是 `miss.lmiss`，别去找 `qc.lmiss`）。
- **检查点**：① `qc.imiss` 有 41 行（表头 + 40 个体；做了剔除就是表头 + 剩下的个体数），`drop_indv.txt` 行数等于脚本 L81 打印的数；② 分位数写进 §4，并回答一句：0.2 是远离群体的离群值，还是切在分布中间；③ **`drop_indv.txt` 只是名单**：qc 脚本**没有** `--remove` 重建 `popgen.vcf.gz`（教材 §20.4.1 末、§20.4.7、§20.6），所以高缺失个体仍在所有统计量里——**包括 `struct.vcf.gz`，而 PCA、ADMIXTURE 和交给 p05 的基因型用的正是它**。只重建 `popgen.clean.vcf.gz` 而不接回流程，等于让名单与数据继续错位（下游没有任何脚本读 `popgen.clean.vcf.gz` 这个名字）。要真剔除，走这条**一次做到下游**的路径：

  ```bash
  # ① 冻结名单并转成两列（vcftools 的 --remove 示例是「FID IID」两列；单列名单在不同版本上行为不一致，统一转两列）
  awk '{print $1"\t"$1}' $Q/drop_indv.txt > $Q/drop_indv.2col.txt && wc -l $Q/drop_indv.2col.txt
  # ② 在 qc 副本的两条 vcftools 过滤命令（原 L65、L69）各加一段 --remove 你的绝对路径/drop_indv.2col.txt
  grep -n -- '--remove' qc_diversity.sh          # 两条命令都要看到；只改一条 = 两套产物不同个体集
  # ③ 删掉受影响的旧产物再重跑（gtmask 与个体剔除无关，可以留着复用；**别删 drop_indv.2col.txt**）
  qstat -u "$USER"                               # 必须为空：上一个作业没跑完就重投，两个作业会同时写 $Q
  rm -f $Q/popgen.vcf.gz* $Q/struct.vcf.gz* $Q/qc.imiss $Q/drop_indv.txt \
        $Q/div.* $Q/fst_* $Q/hwe_* $Q/miss.* $Q/*.bed $Q/*.bim $Q/*.fam
  qsub qc_diversity.sh
  # ④ 等它结束后，结构脚本的产物全部作废，一起清掉再重投
  rm -f $Q/prune.* $Q/struct.pruned.* $Q/ld.ld $Q/ld_decay.* $Q/pca.* $Q/relatedness.genome \
        $Q/duplicate_pairs.tsv $Q/struct.K*.Q $Q/struct.K*.P $Q/cv_error*.tsv $Q/log_K*.out \
        $Q/pc_vs_missing.tsv $Q/deliverables_to_p05.txt
  qsub structure.sh
  ```

  清单一旦冻结（`drop_indv.2col.txt`）就不要再被第二趟重算的 `qc.imiss` 覆盖——否则「剔除谁」在两次运行之间会漂移，方法学就写不清了。**不打算剔除**也是合法选择：那就别加 `--remove`，并在方法学里明写「未执行样本剔除，`drop_indv.txt` 只作 p05 的参考名单」，而不是交一个没人读的 `popgen.clean.vcf.gz`。

- **出错信号**：`drop_indv.txt` 非空而下游位点数与 π 读数一字未变 → 名单没被真正执行（教材 §20.6 表里这一行就是「什么结果说明流程错了」）；`--remove` 之后个体数没变 → 名单是单列或名字与 VCF 表头不符，用 `bcftools query -l` 取名后核对；`drop_indv.txt` 有 40 行 → `--remove` 会删光所有样本，说明 0.2 阈值与这批数据的量级不匹配，回看分布再定阈值（→ §20.4.1 末段）。

### 3.5 多样性、Tajima's D 与分群 F_ST

- **目的**：在不滤 MAF 的 `popgen.vcf.gz` 上算滑窗 π、全基因组 Tajima's D 与分群 F_ST，并**先认列名**。
- **命令**：

  ```bash
  # 分群清单：每行一个样本名，名字必须与 bcftools query -l 的输出逐字一致
  bcftools query -l $Q/popgen.vcf.gz > $P04/work/vcf_samples.txt && wc -l $P04/work/vcf_samples.txt
  ls $P04/work/pops/*.txt                      # 第一趟这里没有文件，属正常（第二趟才有）
  qstat -u "$USER"                             # 先确认没有在跑的作业，再投递
  cd $P04/work && qsub qc_diversity.sh         # 第 3、4 段（重跑前两段是幂等的）
  ```

  这一段做什么：L84 `--window-pi 50000 --window-pi-step 10000`；L85 `--TajimaD 50000`（**`--TajimaD` 只接受窗口大小，没有 step**）；L90–103 两两遍历 `POPS/*.txt` 用 `--weir-fst-pop A --weir-fst-pop B --fst-window-size … --fst-window-step …`。

- **分群目录从哪来：这个流程必须走两趟**。`pops/<群名>.txt` 是**你**根据 3.8 的 PCA 与 3.10 的 ADMIXTURE 结果写的（每行一个样本名，与 `bcftools query -l` 逐字一致），课程不会预先给、manifest 里也没有分群标签：

  1. **第一趟**（3.3 投的那次）：`pops/` 是空的 → F_ST 与分群 HWE **都不运行**。这是预期行为，不是报错。
  2. 拿到 PCA/ADMIXTURE 结果后写 `pops/<群名>.txt`：至少两群、每群 ≥ 2 个样本（某群只有 1 个个体时 F_ST 全 `-nan`），所有样本名都要能在 `vcf_samples.txt` 里查到。
  3. **第二趟**：`qstat -u "$USER"` 确认第一趟已结束，再 `qsub qc_diversity.sh`。脚本没有锁，两个作业同时写 `$Q` 会互相覆盖。

  **一个必须知道的静默行为**：`POPS` 目录**不存在**时才打印 `[WARN] 未找到分群目录`（L102）；目录存在但**是空的**时，`find` 返回空列表、两重循环一次都不进，**一条 WARN 都不打**，日志看起来像正常完成。所以第二趟的判据不是「日志里有没有 WARN」，而是 `$Q` 里有没有 `fst_*.weir.fst`，且群对数等于 `n(n−1)/2`（`n` 是群数，不是样本数）。
- **产出文件**：`$Q/div.windowed.pi`、`$Q/div.Tajima.D`、`$Q/fst_<A>_<B>.weir.fst`、`$Q/fst_<A>_<B>.windowed.weir.fst`（群对数为 `n(n−1)/2`）。
- **检查点**：① **全基因组 Tajima's D 中位数**（L86–87 直接打印，含 `n_windows`）：中性期望近 0；系统性偏正时把「误滤 MAF」列为**第一个待查项但不是唯一解释**——群体收缩同向，而 `+0.5` 只是**经验档位、不是精确阈值**，还必须配一套「同缺失阈值的对照产物」才能归因（教材 §20.5.3）；两套 VCF 的 `--max-missing` 也不同（0.8 与 0.9），**不能拿 `struct` 与 `popgen` 的 D 相减当对照**；② **`WEIGHTED_FST` 列是主结果**（分量和之比 ΣN/ΣD），`MEAN_FST` 是比值平均、不得单独汇报（教材 §20.5.1、§20.6），同时抄窗口内 SNP 数与 MAF 分布；③ **没有合格来源的读数**：π 的绝对水平、F_ST 的「高/低」档位——README 与教材都是 unverified 预期，只给形态与量级描述。
- **出错信号**：`F_ST` 列全 `-nan` → 群体清单样本名与 VCF 表头失配（含回车、前缀不符、某群只有 1 个体），先 `bcftools query -l` 取纯净名再用 `grep -x -f` 核对（教材 §20.6、讲义 ⑨E8）；**`$Q` 里没有 `fst_*.weir.fst` 而日志无任何 WARN** → `pops/` 是空目录（见上条的静默行为），不是脚本坏了；`[WARN] 未找到分群目录`（L102 原文）→ `POPS` 指错或目录不存在，分群定义本身是交付物之一。**循环依赖必须自己闭合**：先跑 3.7 拿到 LD 半衰距离，再把 `WIN` 设成半衰距离的 **2–5 倍**重投本步的第 3、4 段（脚本 L121–126 的收尾提醒是**写给人看的**，脚本不会自己迭代；窗宽小于半衰距离时窗口读数会被单个单倍型块主导，教材 §20.4.7）。

### 3.6 HWE 只算不滤（单倍体上不作诊断）

- **目的**：与课程脚本口径一致地跑一次 `--hardy`，**并明确它在本数据上不产生可解释的读数**；技术诊断改用与倍性相容的量。二倍体体系的判读（方向 + 拓扑 + 分群 + `F_IS`）在这里只作训练。
- **命令**：同一作业第 5 段（L106–118）：

  ```bash
  # plink --vcf struct.vcf.gz --allow-extra-chr --double-id --set-missing-var-ids '@:#' --make-bed --out struct
  # plink --bfile struct --allow-extra-chr --hardy --out hwe_all
  # 分群：awk '{print $1"\t"$1}' pops/<P>.txt > keep_<P>.txt，再 --keep 后 --hardy
  awk 'NR>1 && $9!="NA" && $9<1e-6 {if($7>$8) ex++; else de++} END{printf "  p<1e-6 位点中：杂合过量 %d，杂合缺失 %d\n", ex+0, de+0}' $Q/hwe_all.hwe
  ```

- **产出文件**：`$Q/struct.bed/.bim/.fam`、`$Q/hwe_all.hwe`、`$Q/miss.imiss`、`$Q/miss.lmiss`、`$Q/hwe_<P>.hwe`、`$Q/keep_<P>.txt`（每个分群一份）。
- **检查点**：① 脚本 L117–118 已打印「`p<1e-6` 位点中 杂合过量 N、杂合缺失 M」——这是**方向速览**，不是判据；② **单倍体声明**：稻瘟菌每个位点只有一个等位基因，`p² + 2pq + q²` 这个三分模型在数据上不存在，HWE 的期望杂合度无从定义，输出**不作诊断**，方法学里要写一句「该物种为单倍体，HWE 不适用，未施加 HWE 过滤」，也不得反过来拿这份输出当质量判据（教材 §20.4.3 选读块、§20.5.2、§20.6）；技术诊断改用每位点深度、缺失率、`AD` 中支持非参考等位的读段比例、比对质量；③ **合格数字只有合成算例**：合并三亚群 99.6% 位点 `p < 10⁻⁶`、正确分群后 `p < 0.05` 占 4.5%、自交 `s = 0.95` 时 `F = 0.905` 与 `H/H_exp = 0.0985`、100% 位点 `p < 10⁻⁶`（`ch20_hwe_selfing_wahlund.py --selftest`）。真实 `hwe_all.hwe` 里的任何比例都是**本批实测**，不得拿讲义或教材的数去「对照」；④ 阈值算术自己复核：`50 × 0.05² = 0.125`（期望格计数不足 5，卡方失效）、`10⁶ × 0.05 = 50000`、`0.05/(5×10⁴) = 10⁻⁶`（依赖 `M_eff` 的估计，是经验约定不是常数）。
- **出错信号**：`Error: Invalid chromosome code 'chr01'` → 漏 `--allow-extra-chr`（非模式物种每条 PLINK 命令都要带）；`Error: Duplicate ID '.'` → 漏 `--set-missing-var-ids '@:#'`；把 `p < 10⁻⁶` 占比当成质量分并据此过滤 → 删的是「一个不适用的模型判为异常」的位点（→ 教材 §20.5.2）。

### 3.7 LD 剪枝与衰减曲线（先测衰减，再回头定窗宽）

- **目的**：得到近似独立的标记集（供 PCA / ADMIXTURE / TreeMix），并把 `--r2` 输出按物理距离分箱、拟合衰减，报出**两行半衰**与 `r² = 0.2` 的距离。这一段的读数直接决定 3.5 的窗宽与 p05 的候选区间宽度。
- **命令**（`qsub`；同一作业第 1、2 段）：

  ```bash
  cd $P04/work && qsub structure.sh && qstat -u "$USER"
  # 第 1–2 段在 ADMIXTURE 之前，可以先看产物：
  ls -l $Q/prune.prune.in $Q/ld.ld $Q/ld_decay.txt
  ```

  这一段做什么：L61 `--indep-pairwise 50 10 0.2`（**按变异个数计**：50 个变异的窗口、10 个变异的步长、`r²` 阈值 0.2，不是 50 kb）；L62 `--extract prune.prune.in --make-bed`；L67–68 `--r2 --ld-window 99999 --ld-window-kb 500 --ld-window-r2 0`；L69 调 R 脚本，第 5 个参数是 `NIND=$(wc -l < ${BFILE}.fam)`（L57）。
- **产出文件**：`$Q/prune.prune.in`、`$Q/prune.prune.out`、`$Q/struct.pruned.{bed,bim,fam}`、`$Q/ld.ld`、`$Q/ld_decay.txt`、`$Q/ld_decay.png`、`$Q/ld_decay_binned.tsv`。
- **检查点**：① **`NPRUNE`**（L63 打印，或 `wc -l prune.prune.in`）；脚本 L64 明写「< 1 万时 PCA 不稳」，并说明这个数同时是 p05 估 `M_eff` 的**粗略上界**；② **`ld.ld` 的最小 `r²` 不应恰好是 0.2**——是 0.2 就说明漏了 `--ld-window-r2 0`，曲线尾部凭空消失且不报错；③ **`ld_decay.txt` 两行半衰都在**：`half_decay_bp`（峰值减半）与 `half_decay_baseline_adjusted_bp`（扣掉 `1/n` 基线后再减半），出现 `NA` 说明拟合或分箱不足；另有一行 `dist_at_r2_0.2_bp`，**只有未扣基线一版**（教材 §20.4.4 已标）；④ **披露四要素齐全**：样本染色体数 `n`（并写明是染色体数）、MAF 阈值、分箱宽度与最大距离、半衰判定标准，再加拟合模型——脚本文件头写了 `n_individuals`、`baseline_1_over_n`、`max_distance_kb`、`bin_width_bp`、`n_pairs_used`、`fit_model`、`r2_max_fitted`，但 **MAF 阈值读不到**，文件里只留一行「请手工记录」，必须自己补进方法学；⑤ `baseline_1_over_n` 应为 **0.025**（手算 `1/40`）——只有单倍体下 `NIND` 才等于染色体数，二倍体 30 个个体是 60 条染色体，基线是 `1/60 = 0.0167`；⑥ R 脚本行为对账（L43–L76）：分箱 `floor(dist/bin_bp)*bin_bp + bin_bp/2`，每箱 `n_pairs >= 50` 才进拟合，Hill–Weir 主模型 `R2 ~ 1/(1+rho*bin)`，不收敛退回指数 `a*exp(-b*bin)+cc`，`baseline = 1/n_ind`；⑦ **量级标尺（合成算例，不得当真实数据预期）**：`n = 30` 基线 0.0347（`1/30 = 0.0333`）、半衰 54.0 / 48.0 kb、`r² = 0.2` 距离 111.0 / 99.0 kb；`n = 200` 基线 0.0050、半衰 51.0 / 50.0 kb、0.2 距离 102.0 / 101.0 kb（真实 50 kb）。同一段生物学、不同样本量读出不同的半衰，所以**样本量不等的两条曲线不能直接比高度**。
- **出错信号**：曲线在 0.2 处平直截断 → 漏 `--ld-window-r2 0`（讲义 ⑨E5）；`Killed` → 先看 `h_vmem=16G`（L7）与是否在登录节点跑（登录节点跑 ADMIXTURE 多 K 与 PLINK LD 会被清退）；输出量随 SNP 数急剧膨胀 → 放开了 `--ld-window 99999` 却**没有同步收紧** `--ld-window-kb`（教材 §20.4.4：PLINK 1.9 默认三重裁剪本身不会爆盘，是本脚本放开个数上限才需要收紧 kb）；`没有落在 0–500 kb 区间内的位点对`（R 脚本 L39 原文）→ 检查是否忘了 `--ld-window-kb`（→ 教材 §20.4.4、§20.6）。

### 3.8 PCA 与缺失率对照

- **目的**：把结构分解成连续坐标，同时立刻排查「主成分是不是技术批次」。PCA 不假设群体模型，也不会告诉你「有几个群体」。
- **命令**：同一作业第 3 段（L72–77）：

  ```bash
  # plink --bfile struct.pruned --allow-extra-chr --pca 10 --out pca
  # 脚本在 qc.imiss 存在时把 PC1/PC2 与个体缺失率并成 pc_vs_missing.tsv，并提示「请自行算相关」
  head -3 $Q/pca.eigenvec && cat $Q/pca.eigenval
  # 并表前先确认两边的 ID 是同一套名字（脚本按 qc.imiss 第 1 列去对 eigenvec 第 2 列）：
  comm -3 <(tail -n +2 $Q/qc.imiss | cut -f1 | sort) <(cut -f2 $Q/pca.eigenvec | sort)   # 必须无输出
  awk 'NR>1 && $4=="NA"' $Q/pc_vs_missing.tsv | wc -l                                    # 必须 0
  ```

  两个 ID 列能对上的原因：`plink --vcf` 用了 `--double-id`（qc 脚本 L106），`.fam` 里 FID 与 IID 都等于 VCF 的样本名，所以 `pca.eigenvec` 的第 2 列（IID）就是 `qc.imiss` 第 1 列（INDV）。**如果你自己改过 PLINK 命令、去掉了 `--double-id`，这个对应关系就断了**：`pc_vs_missing.tsv` 会照样生成，缺失率列全是 `NA`，看起来像「没有相关性」——这是静默错，不是数据问题。两个文件都必须落在 `$Q` 下，脚本第 3 段用的是相对路径 `qc.imiss`，不再需要把文件复制到别处。

- **产出文件**：`$Q/pca.eigenvec`、`$Q/pca.eigenval`、`$Q/pc_vs_missing.tsv`。
- **检查点**：① 碎石图（`pca.eigenval` 直接画）前几个特征值应陡降，取多少个主成分进下游要有依据；② **PC 坐标与缺失率（以及个体平均深度）的相关系数自己算**——脚本只并表不算相关（L77 明写）；③ **定性判据**（教材 §20.6）：PC1 只甩出一两个样本而其余挤成一团 → 优先怀疑深度或污染，不是「发现了新群体」；未剪枝时大 LD 区段（倒位、着丝粒）会让数百个共分离标记在同一主成分上同步极化，从而掩盖全基因组结构（教材 §20.4.5）；④ 前几个主成分的方差解释比例抄进 §4，PCA 散点另出一版**按平均深度上色**。
- **出错信号**：`pc_vs_missing.tsv` 没生成 → `qc.imiss` 不在工作目录（脚本用相对路径 `qc.imiss`）；把 PCA 坐标当成分组标签硬切 → 连续渐变被当成离散边界，下游假阳性反而升高（教材 §20.4.5）；PC1 与深度强相关却继续往下做 → 后面的 `Q` 协变量会把技术噪声带进关联模型（→ §20.5.4 前半）。

### 3.9 亲缘与重复样本

- **目的**：给 p05 提供重复样本清单与成对亲缘读数。这一步产出的**不是**现成的亲缘矩阵。
- **命令**：同一作业第 4 段（L81–83）：

  ```bash
  # plink --bfile struct.pruned --allow-extra-chr --genome --out relatedness
  # awk 'NR>1 && $10>0.9 {print $1"\t"$2"\t"$3"\t"$4"\t"$10}' relatedness.genome > duplicate_pairs.tsv   (L82)
  wc -l $Q/duplicate_pairs.tsv && head $Q/duplicate_pairs.tsv
  ```

- **产出文件**：`$Q/relatedness.genome`、`$Q/duplicate_pairs.tsv`。
- **检查点**：① `PI_HAT` 的语义：估计的成对 IBD 共享比例，通常约为亲缘系数的两倍；**大于 0.9 当作可能的重复样本**（教材 §20.6）；② `duplicate_pairs.tsv` 的行数抄进 §4；每出现一对重复，先回查是不是同一 biosample 的多个 run 未去重（教材 §20.5.4 后半）——这条与 3.1 的唯一性校验互为印证；③ **`relatedness.genome` 是样本对表，不是现成的亲缘矩阵 `K`**（教材 §20.6）：要进关联模型须按目标样本重建，报告里要写明这一点，否则 p05 会把它当 `K` 直接用。
- **出错信号**：重复对指向的样本在 manifest 里是不同分离株 → 先查 BAM/VCF 层面是否混样，不要先报「发现克隆系」；把 `relatedness.genome` 直接交给 p05 当 `K` → 矩阵维度与样本对不上（→ §20.6）。

### 3.10 ADMIXTURE 多 K 多种子

- **目的**：在显式生成模型下给出 K = 2…8 的混合比例与交叉验证误差，并按**均值 ± 标准差**判读，而不是报一个「最优 K」。
- **命令**：同一作业第 5 段（L86–106）：

  ```bash
  # cp ${BASE}.pruned.bim ${BASE}.pruned.bim.orig            （L87，原件保留）
  # awk 'BEGIN{OFS="\t"}{$1="0"; print}' .bim.orig > .bim     （L88，染色体列置 0）
  # for K in 2..8; for R in 1..REPS; SEED=1000+R; admixture --cv=5 -s $SEED -j8 ...
  cat $Q/cv_error.tsv
  ```

  **种子数：把 `REPS` 设成 5**（脚本默认 3，作业要求 5–10）。`REPS` 在结构副本 L51，改完 `grep -n 'REPS=' structure.sh` 确认；种子由脚本算成 `1000+R`，即 1001–1005。

  - 工作量自己核一遍：`K = 2…8` 是 7 个 K，×5 个种子 = **35 次 ADMIXTURE**。设成 10 就是 70 次，单次上机的机时更紧。
  - **5 是作业允许区间的下界，不是「折中」**：作业写「换 5–10 个随机种子检查 Q 的一致性」，5 个已满足要求，报告里就写「采用 5 个随机种子（1001–1005）评估收敛性」。
  - **不要保持默认 3 又在方法学里写 5–10**：两处口径必须一致，否则「方法选择」那一栏直接失分。
- **产出文件**：`$Q/struct.pruned.bim.orig`、`$Q/struct.K<K>.r<R>.Q/.P`（每个 K 每个种子一份）、`$Q/log_K<K>_r<R>.out`、`$Q/cv_error_raw.tsv`、`$Q/cv_error.tsv`（列 `K / CV_mean / CV_sd / n_reps`）。
- **检查点**：① `grep 'CV error' $Q/log_K*.out` **不能为空**——为空就是漏了 `--cv`；② **`cv_error.tsv` 的 `n_reps` 应等于你设定的 `REPS`**（本指导取 5；改了 `REPS` 而 `n_reps` 仍是 3，说明投的还是改前那份副本）；报 `K = 2…8` 的并列描述 + 均值 ± sd，**相邻 K 的 CV 差小于重复间 sd 时这两个 K 不可比**；CV 随 K 单调下滑而无极小值时，报一个「最优 K」就是过度解释（教材 §20.4.5、脚本 L107–111）；③ **CV 最小的 K 不是真实亚群数**：CV 误差只度量模型对掩码基因型的预测精度，能做的展示是并列 K 的演进图谱 + 地理/寄主/表型/系统发育的独立证据；④ `.Q/.P` 每个 K×种子都在，`.bim.orig` 还在（回退路径）。
- **出错信号**：无 `.Q/.P`、日志里没有 `Cross-validation` 行 → `.bim` 第一列没置 0（ADMIXTURE 读非数字染色体名会直接退出，教材 §20.4 与讲义 ⑨E3），或者漏了 `--cv`；报告里写「该群体有 4 个遗传谱系」→ 把模型参数当本体论断言（讲义 ⑨E6、⑩Q4）；只跑一个种子 → 似然面多峰时你根本看不见不一致（→ 教材 §20.4.5）。

### 3.11 TreeMix（条件执行的残缺段）

- **目的**：在带漂移的分支树上贪心加迁移边、吸收协方差矩阵里树解释不掉的部分。**迁移边只能当工作假说**，要由四群检验或单倍型溯祖独立证实。
- **命令**：同一作业第 6 段（L114–121），但有三个前置条件，缺一个整段只打印 `[WARN]` 跳过：

  ```bash
  ls -l $Q/pop.treemix.frq.gz            # 必须在 $Q 下：脚本 L55 先 cd 到 OUTDIR，再按相对路径找它
  zcat $Q/pop.treemix.frq.gz | head -3   # 前两行是两个整数（位点数与群体数），第 3 行起是位点行
  grep -n 'ROOTPOP' structure.sh         # 必须看到你写的那一行
  cd $P04/work && qstat -u "$USER"       # 先确认没有在跑的作业
  qsub structure.sh
  ```

  `ROOTPOP` **不用 `qsub -v` 传**，和 `BFILE`、`OUTDIR` 一样写进结构副本（3.2 已留出这行）：`ROOTPOP=<群体标签>`。理由同 3.2——作业进程拿不到你终端里的变量，写进脚本才是可 `grep` 核对的。

  这一段做什么：`if [[ -n ${ROOTPOP:-} && -s pop.treemix.frq.gz ]]` → `for M in 0 1 2 3 4 5`，`treemix -i pop.treemix.frq.gz -m $M -k 500 -root $ROOTPOP -o tm_m$M`；否则打印 `[WARN] 未设 ROOTPOP 或缺 pop.treemix.frq.gz，跳过 TreeMix`。

- **`ROOTPOP` 填的是频率表里的「群体标签」，不是分离株名**：`-root` 取的是 `pop.treemix.frq.gz` 表头那一行的群体名，也就是你 `pops/<群名>.txt` 的**文件名**（不是 `i56a` 这类样本名，也不是 `struct`、`pca` 这类输出前缀）。先列出能用的取值再填：

  ```bash
  zcat $Q/pop.treemix.frq.gz | head -1 | cut -f2-    # 这一行就是 -root 能接受的全部取值
  ```

  课程数据没有先验外群：分群是 PCA 与 ADMIXTURE 之后才定的，哪个群适合作根必须有独立证据（地理、寄主、已发表的系统发育）。**没有可信外群就不要设 `ROOTPOP`**，让这一段按设计跳过，并在报告里写「TreeMix 未执行及理由」——这比硬指一个群当根合规得多。

- **`pop.treemix.frq.gz` 的格式转换课程没有提供**（教材 §20.3 L92、§20.6）。TreeMix 要的是它自己的频率表（gzip 压缩；头两行是两个整数——位点数与群体数；之后每个位点一行，含位点标识、染色体、位置、两个等位、以及各群体的等位频率。**字段顺序与分隔以 TreeMix 官方文档的 Input format 一节为准，本课程不给可抄的一行命令**）。`plink --freq` 的输出不是这个格式，中间需要你自己写一段转换脚本，并把它当作**你方法学的一部分**：放进 `scripts/`、在报告里写明用了哪个位点集（`struct.pruned` 还是 `struct`）与哪种等位编码，并抽两三个位点与 `plink --freq` 的输出手工对账。做不到就跳过本段——**本段是选做**，跳过不扣完成度那一栏的分（作业的七项交付里没有 TreeMix 产物）。
- **产出文件**：成功时 `$Q/tm_m0…tm_m5` 系列（`*.llik`、`*.edges.gz`、`*.cov.gz`、`*.treeout.gz` 等）；跳过时**没有产物**。
- **检查点**：① **`pop.treemix.frq.gz` 的存在性先确认**——讲义与脚本**都没有生成它的步骤**（教材 §20.3 L92）。没有它就不是「TreeMix 结果不好」，而是「TreeMix 根本没跑」；② `-k 500` 把相邻 500 个 SNP 打包成块以抵消 LD，不设会严重低估标准误；③ 加几条边看残差矩阵 + 似然增量 + 解释力（教材 §20.4.5），`M` 取到几要写进方法学；④ 讲义 ⑤5.6 里的 `top1pct.bed` 同样**没有生成命令**，需自己按窗口统计量的分位数提取（教材 §20.3）。
- **出错信号**：脚本最终「完成」不等于 TreeMix 跑过（L120 的 WARN 是唯一线索，只看 rc=0 会漏）；`treemix: command not found` → 结构脚本的 `command -v` 循环里**没有 treemix**（L45–47），`set -euo pipefail` 会让作业在第 6 段失败，日志里最后一个成功段是 ADMIXTURE；`-root` 用了分离株名（如 `i56a`）→ TreeMix 报群体标签找不到，回上一条命令看表头；把迁移边写进结论 → 那是残差吸收器，不是基因流证明（→ §20.4.5）。

### 3.12 交付清单与结果回填

- **目的**：把 p05 要的资产点名点清，并核对「清单上的名字」与「目录里的实名」是否一致。
- **命令**：同一作业第 7 段（L123–134），以及作业额外要求的合并清单：

  ```bash
  cat $Q/deliverables_to_p05.txt                 # 脚本写的书面清单（8 行）
  D=$P04/work/deliverables_for_p05; mkdir -p $D/groups
  cp $Q/struct.bed $Q/struct.bim $Q/struct.fam $Q/struct.pruned.* $Q/prune.prune.in \
     $Q/pca.eigenvec $Q/pca.eigenval $Q/ld_decay.txt $D/
  cp $Q/struct.K*.r*.Q $D/groups/ 2>/dev/null || true   # 每个 K×种子一个 Q 矩阵
  cp $P04/work/pops/*.txt $D/groups/                    # 分群定义，每行一个样本名
  { printf 'type\tid1\tid2\tvalue\n'
    awk 'NR>1 && $10>0.9 {print "dup_pair\t"$1"\t"$2"\t"$10}' $Q/relatedness.genome
    awk '{print "drop_indv\t"$1"\tNA\tNA"}' $Q/drop_indv.txt
  } > $D/related_or_dup.txt
  ls -R $D | head -30 && ls $D/groups | wc -l
  ```

  `related_or_dup.txt` 里有**两类语义完全不同的记录**（成对样本 vs 单个样本），作业只要求一个文件，所以这里用 `type` 列 + 表头把它们分开：`dup_pair` 行是 `PI_HAT > 0.9` 的样本对（`id1 / id2 / PI_HAT`），`drop_indv` 行是缺失率超阈值的单个样本（`id2` 与 `value` 填 `NA`）。不加这一列，下游按 `$3` 当缺失率或按两列当样本对去解析都会错位。`cv_error.tsv` **不在**上面这个拷贝列表里：作业树把它放在 `results/`，交付目录里不需要它。

- **产出文件**：`$Q/deliverables_to_p05.txt`（脚本写的 8 行书面清单）、`$D/`（你按作业七项组装的目录，含 `groups/`）。
- **检查点**：① 脚本清单的 8 项：`genotype_gwas`、`genotype_pruned`、`pca`、`relatedness`、`drop_individuals`、`ld_decay`、`n_eff_upper_bound`、`admixture_Q`；其中 `n_eff_upper_bound` 就是 `NPRUNE`，脚本 L132 明写它是 `M_eff` 的**粗略上界**；② **两处规格与脚本不一致，必须自己选一套并写进报告**：项数——作业评分表写「`deliverables_for_p05/` 七项齐全」，脚本书面清单是 8 行（`admixture_Q` 一行里同时含 `.Q` 与 `cv_error.tsv`），本指导按**作业的七项交付、另附 `cv_error.tsv`**（后者按作业树放进 `results/`，不进 `deliverables_for_p05/`）；文件名——作业要 `related_or_dup.txt`，脚本落的是 `relatedness.genome` 与 `duplicate_pairs.tsv`，用上面那段合成。**这两处不一致属于课程侧的规格差异，不是你的错**，报告里写清「我按七项 + `cv_error.tsv` 提交」即可；③ `groups/` 必须**非空且两类文件都在**：分群定义（`pops/*.txt`）与各 K×种子的 Q 矩阵（`struct.K*.r*.Q`）——作业的七项里这一项目前最容易漏，漏了「七项齐全」直接扣分；④ 清单里的 `${OUTDIR}/${BASE}.{bed,bim,fam}` 是**花括号字面量**（脚本没展开），不要照抄成文件名，按实到目录里数文件；⑤ `ld_decay.txt` 与 `pca.eigenvec` 必须在交付目录里（作业规定超限也不许省）；⑥ 回填 §4：位点数（过滤前 / biallelic / gtmask / popgen / struct）、缺失率分位数、`drop_indv.txt` 行数、Tajima's D 中位数与窗口数、`WEIGHTED_FST` 全基因组值、HWE 方向计数、`NPRUNE`、`ld_decay.txt` 两行半衰与 0.2 距离、PC1–PC4 方差解释、`duplicate_pairs.tsv` 行数、`cv_error.tsv` 的 K×CV 表、TreeMix 是否执行。
- **出错信号**：交付目录里有 `drop_indv.txt` 却没有重建过的 VCF → 名单与数据语义错位（回 3.4）；`groups/` 是空目录或只有 Q 没有 `pops/*.txt` → 七项缺一，p05 无法复现你的分群；`struct.pruned.*` 里缺 `.bim.orig` → 无法回退到 ADMIXTURE 之前的文件；清单里写着 `relatedness.genome` 而目录里只有 `related_or_dup.txt` → 下游找不到（→ §20.6）。

## 4. 结果记录表（学生填写，不预填；「自查判据」列给来源口径）

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 1 | 实查版本：plink / bcftools / vcftools / admixture / R / treemix | 版本号 | | plink 1.90b6.21、bcftools 1.17、r-base 4.3.1 为 yml pin；**vcftools/admixture/treemix 未 pin，填打印值**（§20.3） |
| 3.1 | manifest 行数 / 唯一分离株数 / 落盘 fastq 文件数 / R1 文件数 | 个 | | 40 / 40 / 80（双端）/ 40；`uniq -d` 无输出、名称清单 `comm` 无输出（§20.5.4 后半） |
| 3.1 | `base_count` 合计 / 跨度 / 中位 | Gb | | 18.44 / 0.404–0.510 / 0.465（manifest 实测，§20.1） |
| 3.1 | `fastq_bytes` 合计 | GB | | 11.95（manifest 该列原样求和；3 行只记了 R1，别用它验完整性，§20.6） |
| 3.1 | 名义深度 `总碱基 / (40 Mb × n)` | × | | 11.5×（手算，§20.1）；**不是覆盖度**（TERMINOLOGY §2） |
| 3.3 | 位点数：输入 / biallelic / gtmask / popgen / struct | 个 | | 看方向不看阈值：`struct` < `popgen` 正常；两者接近/相等是**待复查项**（核 `--maf` 与 MAF 分布），不等于「MAF 没生效」（§20.4.7） |
| 3.3 | 两套过滤参数（`--max-missing` / `--maf`） | 数值 | | 0.8 不滤 MAF；0.9 + 0.05（§20.4.7 表） |
| 3.4 | `qc.imiss` 行数 / 缺失率 P10·P50·P90·max | 行 / % | | 41 行＝表头+40（剔除后为表头+剩余个体）；0.2 是脚本设定不是分位（§20.4.1 末） |
| 3.4 | `drop_indv.txt` 行数 / 是否执行过 `--remove` 重建两套 VCF | 个 / 是·否 | | 名单≠已剔除；做了重建要连 `struct` 与下游一起重做并写明（§20.4.7、§20.6） |
| 3.5 | 全基因组 Tajima's D 中位数 / 窗口数 | 无量纲 / 个 | | 中性近 0；偏正先查误滤 MAF，`+0.5` 只是经验档位（§20.5.3） |
| 3.5 | `WEIGHTED_FST` 全基因组值 / 窗口内 SNP 中位数 | 无量纲 / 个 | | 主结果只用 `WEIGHTED_FST`；`MEAN_FST` 不单独汇报（§20.5.1） |
| 3.5 | 窗口大小的两次取值（默认 50 kb、按半衰 2–5 倍重设） | bp | | 循环依赖：先测半衰再定窗（§20.4.7） |
| 3.6 | `p<1e-6` 位点中 杂合过量 / 缺失 计数 | 个 | | 仅作方向速览；单倍体上不作诊断（§20.4.3、§20.5.2） |
| 3.6 | 方法学是否写明「单倍体，HWE 不适用，未施加 HWE 过滤」 | 是·否 | | 必须写（§20.6 三条特有声明） |
| 3.7 | `NPRUNE`（剪枝后标记数） | 个 | | < 1 万时 PCA 不稳；同时是 `M_eff` 粗略上界（脚本 L64） |
| 3.7 | `ld.ld` 最小 `r²` | 无量纲 | | 不应恰为 0.2；是则漏 `--ld-window-r2 0`（§20.4.4） |
| 3.7 | `half_decay_bp` / `half_decay_baseline_adjusted_bp` | bp | | 两行都要在；`NA`＝拟合或分箱不足（§20.4.4） |
| 3.7 | `dist_at_r2_0.2_bp` / `baseline_1_over_n` | bp / 无量纲 | | 基线应为 1/40＝0.025（手算）；0.2 距离只有未扣基线一版 |
| 3.7 | 披露四要素 + 拟合模型（n、MAF、分箱与最大距离、半衰定义、模型） | 文本 | | 缺一项则半衰不可比（§20.4.4） |
| 3.8 | PC1–PC4 方差解释比例 / 与缺失率的相关系数 | % / 无量纲 | | 强相关＝技术批次伪装成结构（§20.4.5、§20.6）；并表前先过 ID 对齐两条检查（`comm` 无输出、`NA` 计数 0） |
| 3.9 | `duplicate_pairs.tsv` 行数 / 是否回查同一 biosample | 对 / 是·否 | | `PI_HAT > 0.9` 当作可能的重复（§20.6） |
| 3.10 | `REPS` 取值 / `cv_error.tsv` 的 K×CV_mean±sd | 次 / 无量纲 | | 脚本默认 3；作业要 5–10，本指导取 5（35 次运行），两处口径须一致（§20.4.5） |
| 3.10 | 相邻 K 的 CV 差是否小于重复间 sd | 是·否 | | 小于则该两 K 不可比（§20.4.5） |
| 3.11 | `pop.treemix.frq.gz` 是否存在 / TreeMix 是否执行 | 是·否 | | 缺文件则只打 WARN 跳过（§20.3） |
| 3.12 | 交付项数（七项 / 8 行）、`groups/` 是否有两类文件、`ld_decay.txt` 与 `pca.eigenvec` 是否在 | 项 / 是·否 | | 按作业七项 + `cv_error.tsv`；`groups/`（分群定义 + Q）与两项必备文件缺一扣分（§20.6） |

## 5. 失效条件对照（教材 §20.5，本实验里在哪一步、看什么能察觉）

1. **〔博〕F_ST 有多个估计量与两种求平均方式，混用使数值不可比**（§20.5.1）｜3.5。**察觉**：先认列名——`WEIGHTED_FST` 是分量和之比（ΣN/ΣD，主结果）、`MEAN_FST` 是比值平均；再看窗口内 SNP 数与 MAF 分布（低频位点为主的窗口一定把均值口径拉偏）；跨文献比较前把「估计量 / MAF 阈值 / 窗口宽度 / 求平均方式」四项抄进方法学表，缺一项不做数值比较；单 SNP 的 F_ST 不单独汇报。量级标尺：`ch20_fst_average_trap.py --selftest` 的 0.0723 对 0.0455、窗口偏差中位数 0.0279 对 0.0067、剔稀有变异后 0.0757 → 0.0841（1.11 倍）、按观测频率过滤反降到 0.0634，手算锚点 `N = 0.01895 / D = 0.44 / F_ST = 0.04306`。**偏差方向不定**，所以「偏低就说明算错」不成立。
2. **〔博〕把 HWE 当过滤器，删掉的是真实的选择或结构信号**（§20.5.2）｜3.6。**察觉**：**先问倍性**——本讲主线是单倍体，该项没有对象，直接删掉过滤项并写进方法学，也**不把它的输出当质量判据**；二倍体体系再看偏离方向与分布（全基因组平坦缺失 + `F_IS` 正移＝自交/克隆；分群后消失＝Wahlund；与深度、缺失率强相关＝allelic dropout；聚集在重复区与低 MAPQ 的过量＝比对坍缩），**只有最后一类允许单向剔除**。`−log10 p` 对深度/缺失率的回归斜率显著时，「技术驱动」是**待检假设而不是判决**。量级标尺：合并三亚群 99.6% 位点 `p<10⁻⁶`、正确分群后 `p<0.05` 占 4.5%；自交 `s=0.95` 时 `F = 0.905`、`H/H_exp = 0.0985`、100% 位点 `p<10⁻⁶`；`H_exp − H_obs = 0.1200 = 2Var(p)`。
3. **〔硕〕MAF 过滤扭曲频谱，让 Tajima's D 系统性偏正**（§20.5.3）｜3.3、3.5。**察觉**：先看全基因组 D 中位数是否接近 0；偏正时把「误滤 MAF」列为**第一待查项但不是唯一解释**（群体收缩同向）；`+0.5` 是经验档位不是精确阈值。可控对照是只改一个条件：同一份 `gtmask.vcf.gz`、同一 `--max-missing`、同一批个体，另出一套只去掉 MAF 的产物比 D；若差别主要来自 MAF，`θ_W` 降幅应约等于被剔位点比例，而 `π` 降幅远小于它。**不能**拿 `struct` 与 `popgen` 的 D 相减——两者 `--max-missing` 也不同。量级标尺：`S` 20000→15187（−24.1%）、`θ_W` 4701.96→3570.44（−24.1%）、`π` 4587.10→4351.03（−5.1%）、D −0.092→+0.825；手算入口 `1/40 = 0.025 < 0.05` 必剔、`2/40 = 0.05` 在阈值线上保留、`1/a_40 = 23.5%` 与 `(1+1/39)/a_40 = 24.1%` 的区别。偏差单向，多做几次只会更稳定地偏。
4. **〔博〕群体结构与人口历史伪装成选择清除；manifest 同名样本静默覆盖让样本量变小**（§20.5.4）｜3.1、3.8、3.10。**察觉（前半）**：先做结构推断，在明确定义的分群内部扫描；只用全基因组经验分位数（top 1%，严格时 0.5%），不用绝对阈值；每个候选窗口回查 `d_XY`——「`d_XY` 高、π 正常」是老分歧，「π 塌、`d_XY` 不动」才是局域事件；低重组区按重组率分层或单独标注；「两个以上统计量」要落实为**真正不同的机理**（π 比值与 F_ST 由 `F_ST ≈ 1 − π̄/d_XY` 连动，不是两项独立证据）。**察觉（后半）**：按样本名落盘的脚本，开工前校验唯一性；**完成判据用产物计数对 manifest 行数，不用退出码**；重跑先清空输出目录；每株 run 数与 `base_count` 记进方法学表。量级标尺：`1/37 = 0.027` 与 `1/40 = 0.025`（手算）；真实案例 40 行 40 唯一、`O23`×3 与 `i76a`×2 同一 biosample、修复后补入 `i77a`/`i57a`/`d54a`（教材 §20.5.4，不是本任务实测）。
5. **不在四条失效内、但必须写进限制的三条**（§20.6）：① 上游 fastq→群体 VCF 的比对与变异检测**没有课程脚本**，本章从 `raw.pop.vcf.gz` 起步；② `pop.treemix.frq.gz` 与 `top1pct.bed` **没有生成步骤**，TreeMix 段只是条件执行；③ 40 株是 257 个 run 的子集，`base_count` 0.4–1.5 Gb 是筛选条件、实测只落在 0.404–0.510 Gb，分群后每群十几条序列，窗口噪声会盖过真实群体差异——任何「群体层面」的结论都要带上这个 `n`。

## 6. 思考题（指向教材 §20.7 博士层，不给答案）

1. 用你自己 3.5 的 `div.Tajima.D` 说明：全基因组 D 中位数若明显为正，你要依次排除哪三个可能，为什么「多做几次取平均」不能修掉它？并给出一个只改一个条件的对照设计。（§20.7 第 9 题 → §20.5.3）
2. 你的 `cv_error.tsv` 里 CV 随 K 单调下滑而没有极小值。写一段 150 字左右的学术回应，既承认模型表现、又守住解释边界，并列出你会补的三项证据。（§20.7 第 6 题 → §20.4.5）
3. 3.7 的 `NPRUNE` 与 3.10 的 K 是两套彼此独立的口径。用它们说明为什么 `M_eff` 只能给「上界」，以及报 `10⁻⁶` 这类阈值时必须一起写出的三项参数。（§20.7 第 10 题 → §20.4.3、§20.4.4）
4. 假设你的 3.1 落盘只得到 37 个文件而退出码为 0。写出两条能在开工前发现它的检查、两个会被改变的读数（各给方向）、以及修复与复跑的最小步骤，并指出 LD 基线从 1/40 变 1/37 的具体算式。（§20.7 第 11 题 → §20.5.4）
5. 你的 3.8 散点里 PC1 与个体缺失率高度相关。列出三项判别动作、两项补救，并说明为什么此时「先剔除劣质样本再谈结构」比「加更多主成分」优先。（§20.7 第 8 题的延伸 → §20.4.5、§20.5.4）
6. 设例：某区间 π 比值与 F_ST 同时达到全基因组前 0.1%。用 `F_ST ≈ 1 − π̄/d_XY` 说明这两个读数为什么不是两项独立证据，并设计三种非选择成因各自的可执行排除计算。（§20.7 第 8 题 → §20.4.8、§20.4.6）

## 7. 提交物

- **对应作业**：`08_assessment/phd/assignments/p04_popgen_practice.md`（占课程总成绩 **4.5%**），打包 `学号_姓名_p04.zip`（≤ 200 MB）。解压后：

  ```
  学号_姓名_p04/
  ├── report.pdf                      # 正文 ≤ 8 页；五节：两套过滤与理由 / LD 衰减与本底判断 /
  │                                   # 群体结构与批次 / HWE 与多样性 / 方法选择与结果可信度说明（≤ 1 页）
  ├── scripts/
  │   ├── qc_diversity.sh             # 你实际投递的 SGE 脚本（改自 04_popgen_qc_diversity.sh）
  │   ├── structure.sh                # 你实际投递的那份（改过就标注改了哪几行）
  │   └── 04_ld_decay_plot.R          # structure.sh 第 69 行按同目录找它，不给就无法原样重跑
  ├── deliverables_for_p05/
  │   ├── struct.{bed,bim,fam}        # 3.3 与 3.6 产出，已滤 MAF
  │   ├── struct.pruned.*             # 3.7 的 LD 剪枝集
  │   ├── prune.prune.in              # 剪枝标记清单（NPRUNE 的来源）
  │   ├── pca.eigenvec, pca.eigenval  # 3.8，可作 p05 的 Q 协变量
  │   ├── related_or_dup.txt          # 3.12 合成：type 列区分 dup_pair（PI_HAT>0.9）与 drop_indv
  │   ├── ld_decay.txt                # 3.7，含四要素与两行半衰
  │   └── groups/                     # pops/*.txt 与 struct.K*.r*.Q（七项里的这一项目前最易漏）
  ├── results/
  │   ├── qc_summary.tsv              # 3.3 的三套位点数 + 3.4 的缺失率分位数
  │   ├── hwe_diagnosis.tsv           # 全样本 vs 分群后 HWE；方向计数（并注明单倍体不作诊断）
  │   ├── diversity_windows.tsv       # π / Tajima's D / WEIGHTED_FST 窗口结果
  │   ├── cv_error.tsv                # 3.10 的 K×重复 均值与 sd（脚本原样）
  │   └── ai_audit.tsv                # ⑧ 的五条逐条判定表
  ├── figs/                           # 标题/轴/图例一律英文（集群 R 下中文会变方块）
  │   ├── fig1_ld_decay.png           # 图注必须写全样本量、分箱宽度、MAF 阈值、半衰定义
  │   ├── fig2_pca_scree.png          ├── fig3_pca_scatter.png   # 另出一版按平均深度上色
  │   ├── fig4_cv_error.png           └── fig5_admixture_Q.png
  ├── ai_logs/prompt_and_reply.md     # ⑧ 的原文往返（提示词原样，第一轮不许预先提示）
  └── env_snapshot.yml                # conda env export --no-builds
  ```

- **五节报告各自要对上一个文件**：第 1 节 ↔ `qc_summary.tsv` 的两套产物位点数；第 2 节 ↔ `ld_decay.txt` 与 `fig1`；第 3 节 ↔ `fig2`/`fig3` 与 `pc_vs_missing.tsv`；第 4 节 ↔ `hwe_diagnosis.tsv` 与 `diversity_windows.tsv`；第 5 节 ↔ 四问逐条作答。
- **两处规格要你自己对齐并在报告里说明**（课程脚本与作业规格不一致，本指导按作业执行）：① 交付项数——作业写「七项齐全」，脚本书面清单是 8 行（`admixture_Q` 那一行同时含 `.Q` 与 `cv_error.tsv`），按七项 + `cv_error.tsv` 交；② 种子数——脚本默认 `REPS=3`，作业要 5–10 个种子，**本指导取 5**（35 次运行），改完 `grep` 确认并在方法学里写清。这两处是课程侧待统一的口径，不是你的操作错误；报告里写明「我按七项 + `cv_error.tsv`、5 个种子提交」即可。
- **四个薄弱处要单独交代**（作业 ④ 的失分点同源）：`--max-missing` 是保留比例的方向；`drop_indv.txt` 是名单、有没有真的 `--remove` 重建（重建就必须连 `struct` 与全部下游产物一起重做，见 3.4）；半衰距离的四要素与定义；`relatedness.genome` 是样本对表、不是亲缘矩阵 `K`。
- **别把交付对象说错**：本层的交付是**规范**——p05 读得懂你的 `struct.*`、`pca.eigenvec`、`ld_decay.txt`、`groups/` 与 `cv_error.tsv` 的**格式与口径**。p05 的主线数据是水稻（二倍体 413 份种质），和这里 40 株稻瘟菌（单倍体）不是同一套样本，**它的表型不可能与你的基因型关联**。报告里若写「p05 直接用这批基因型做 GWAS」，那是概念错误（教材 §20.6 末）。
- **评分口径**（作业 ④，满分 100）：完成度与结果正确性 48、方法选择与结果可信度说明 30、AI 使用与验证记录 10、报告质量 12。**「AI 使用与验证记录」只考可复核性**：提示词原文、模型与日期、AI 给了什么（原样）、哪里错了、你怎么发现的；通篇「AI 输出全部正确」且无验证过程的，本栏不得分；未用 AI 的写明原因即可，不扣分。
- **截止与迟交**：p04 课后**第 7 天 23:59**（p05 上课前 3 天——p05 的实践用的是同一套交付规范，你要在 p05 里复用这套文件组织）；迟交 3 天内按 90%、超 3 天按 70%、超 7 天不计分（可在截止前申请一次不扣分延期）；允许截止前重复提交，以最后一次为准。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材（概念、失效条件、习题、数字索引） | `textbook/chapters/ch20/manuscript.qmd`：§20.1（数据与四处口径）、§20.3（脚本覆盖与两处缺口）、§20.4.1（π/θ_W/D）、§20.4.2（F_ST 三内核两种平均）、§20.4.3（HWE 与倍性选读块）、§20.4.4（LD 三度量、4 要素、PLINK 默认值）、§20.4.5（PCA/ADMIXTURE/TreeMix 边界）、§20.4.6（三联与伪装者）、§20.4.7（两套产物、置缺失、窗口循环依赖）、§20.4.8（`F_ST ≈ 1 − π̄/d_XY`）、§20.4.9（前沿）、§20.5.1–§20.5.4、§20.6、§20.7（博士层 3–13 题）、§20.9、§20.10 |
| 本专题讲义 | `02_lectures/phd/topic04_popgen/04_popgen_lecture.md`：② 前置表与 30 秒自检、③ 3.1、④ 4.1–4.9、⑤ 5.1–5.6、⑥ 6.1–6.2（交付清单；脚本头写的「6.3」按 6.2 读）、⑦ 7.1–7.4、⑧ AI 任务、⑨ E1–E10、⑩ 8 题、⑪ 文献 |
| 质控 / 多样性 / F_ST / HWE（只读；改参数走个人副本） | `03_code/phd/scripts/04_popgen_qc_diversity.sh`：作业头 L2–7、设计要点 L18–26、变量 L28–34、守卫 L36–41、参数 L43–49、第 0 段 L55–61、两套产物 L63–71、位点数 L73–76、缺失率 L78–81、多样性 L83–87、F_ST L89–103、HWE L105–118、收尾提醒 L120–128 |
| LD / PCA / 亲缘 / ADMIXTURE / TreeMix / 清单（只读） | `03_code/phd/scripts/04_popgen_structure.sh`：作业头 L2–7、设计要点 L18–30、变量 L32–39、守卫 L42–47、参数 L49–53、剪枝 L60–64、LD 与调用 R L66–69、PCA L71–78、亲缘 L80–83、ADMIXTURE L85–111、TreeMix L113–121、交付清单 L123–135 |
| LD 衰减拟合（只读） | `03_code/phd/scripts/04_ld_decay_plot.R`：用法 L8、参数 L22–30、读入与距离裁剪 L32–40、分箱 L42–50、Hill–Weir 与指数回退 L52–66、读数 L67–76、输出文件 L78–96、绘图 L98–111、分箱表 L112 |
| 合成自查演示 | `textbook/demos/ch20_tajima_d_maf_bias.py`、`ch20_fst_average_trap.py`、`ch20_hwe_selfing_wahlund.py`、`ch20_ld_r2_baseline.py`（均带 `--selftest`，课程仓库根目录运行 `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/<名>.py --selftest`） |
| 数据说明与下载 | `06_data/phd/README.md` p04 节（筛选条件 0.4–1.5 Gb、40 株、单倍体、自查判据）；`06_data/phd/download_phd.sh --topic p04`（`fetch_p04` L124–157：唯一性告警 L131–135、空 body 守卫 L144、md5 L151、sha256 L153）；`06_data/phd/manifests/p04_runs.tsv`（41 行＝表头+40）；`06_data/accessions.tsv` L13 |
| 元数据自查（双端/文件数） | ENA portal API：`https://www.ebi.ac.uk/ena/portal/api/filereport?accession=<RUN>&result=read_run&fields=run_accession,library_layout,fastq_ftp&format=tsv`（命令与用法见 §2） |
| 环境定义 | `07_envs/conda/env_phd_popgen.yml`（`ngs_phd_popgen`，pin 见 §1「版本口径」） |
| 作业规格 | `08_assessment/phd/assignments/p04_popgen_practice.md`（① 背景 ② 交付物 ③ 完成步骤 ④ 评分 ⑤ 提交 ⑥ 常见失分点） |
| 前置自测 | `08_assessment/prerequisites/l0_01_linux_selftest.md`、`l0_02_r_selftest.md`、`l0_03_conda_selftest.md`、`l0_04_formats_selftest.md`、`l0_06_stats_selftest.md`；`l1_phd_selftest.md`（Q1、Q2）；补课材料见 `02_lectures/prerequisites/l1_phd/l1_phd.md` 的 `l1_p04` 一条 |
