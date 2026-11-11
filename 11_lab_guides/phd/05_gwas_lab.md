---
title: "实验指导 p05：GWAS 关联分析与后 GWAS 挖掘"
level: phd
topic: p05
textbook: [ch21]
lecture: ../02_lectures/phd/topic05_gwas/05_gwas_lecture.md
env: ngs_phd_popgen
---

# 实验指导 p05：GWAS 关联分析与后 GWAS 挖掘

> 上机时手边打开的这份文件。每步回答五件事：做什么、敲什么、产出哪个文件、看到什么算对、看到什么说明错了。原理与判据在教材第 21 章（§21.4 概念方法、§21.5 七条失效条件、§21.7 习题、§21.9 答案、§21.10 数字索引）。
>
> **数字标注规则（全篇遵守）**：检查点里的每个数只来自三类合格入口——① `06_data/phd/README.md` p05 节的登记实测（413 份种质、36,901 个 SNP、表型 36 列、`.ped/.map` 8.5 MB、已发表 p 值 23 MB、`.fam` IID ∩ 表型第 2 列 = 413/413 而 ∩ 第 1 列 = 0、`wc -l` = 0、`.ped` 表型列 `-9`）；② 教材正文带复现入口的数（手算法如 `0.05/36901 = 1.35×10⁻⁶`、BED 换算十二位数手例、`1-(1-1/25000)^25000 ≈ 0.6321`；`demos/ch21_*.py` 与 `ch20_hwe_selfing_wahlund.py` 的现跑输出）；③ 教材明确标「设例／经验口径」的量（λ 四态档位 ≥1.20／1.00±0.05／≤0.90／≈1.00、候选区间 100–300 kb 量级、单 SNP 解释 >40% 方差、`n<60` 时 `pve` 预警）。**RDP1 上的真实读数一律不进检查点**：剪枝集行数、质控后个体数、GEMMA 实测 λ、λ–PC 曲线、候选区间宽度、与已发表 p 值的秩相关——教材 §21.10 把这批全部判为 unverified，本指导只给判据形态，数值由你自己的日志填进 §4 记录表。教材已撤下的数字（「峰从 12 降到 3.5」「MLM 2 / FarmCPU 11 / BLINK 19」「MAF 0.02 时 ~8 个次等位纯合」「不平衡二分类 1:20」「517 份地方稻种 / 360 万 SNP」）**本指导一个不用**。本指导**不挂任何图、不提图号**：第 21 章的配图与图注归正文与幻灯片，读图以教材为准。`--hwe 1e-6` 这个口径差**不来自现版讲义**：讲义 ⑤5.3 已写「不加 `--hwe`」、⑤5.8 已用 `$3=="gene"`，两处与课程脚本一致；残留只在教材图 21-7 的图面（教材 §21.6 已写明「照图操作前先读这一句」）与旧版幻灯片里。见 §3.3 检查点第 5 条——**在文字里就地解决**，不靠任何图面文字背书。**禁止写成「逐位点复现」已发表结果**：教材 §21.5.7 只允许秩相关 + 峰区间一致性。
>
> **计算纪律**：两个 shell 脚本都带 SGE 作业头（`05_gwas_gemma.sh` L6–7 为 `-pe smp 8` 与 `h_vmem=16G`，`05_postgwas_interval.sh` L6–7 为 `-pe smp 4` 与 `h_vmem=8G`），脚本头明令 **禁止在登录节点直接 `bash` 运行**（gemma L14、interval L14）。登录节点只做下载、建环境、编辑、实查文件与看日志；一切计算 `qsub`。**投递后无法补参数**，改任何一个值都要重投。`03_code/`、`06_data/`、`07_envs/` 只读：要改值就走「`cp` 个人副本 → 改指定行 → `grep` 确认 → `qsub` 副本」。**路径陷阱（本专题必踩）**：`05_gwas_gemma.sh` L53 是 `mkdir -p "${OUTDIR}"; cd "${OUTDIR}"`，也就是说 `BFILE`、`PRUNED`、`EIGENVEC`、`PHENO` 的相对路径**在 `cd` 之后才解析**。默认值 `./popgen/struct`（L46）、`./popgen/pca.eigenvec`（L48）是 p04 的写法，照抄会指向 `$OUTDIR/popgen/` 这个不存在的目录。本指导统一：**副本里把这四个值改成绝对路径**，`grep` 确认后再 `qsub`。`VAR=value qsub` 那种写法只给 `qsub` 命令本身设了环境变量、不转交作业进程（作业头没有 `-V`），`qsub -v` 在本机无 SGE 环境下**未实测**——所以不推荐，统一走改副本。**本指导新增的四段作业（§3.1 资产重建、§3.4 诊断、§3.6b 局部放大图、§3.7 对答案）都用 `cat > 脚本名 <<EOF` 生成，`EOF` 不加引号**：不带引号的 here-doc 在**登录节点写文件的那一刻**就把 `${P05}` 展开成字面路径，投递到执行节点后脚本里只剩绝对路径。写完一律 `grep -n 'P05' 脚本名` 复核，**期望无输出**；有输出说明作业会读到空变量，路径会变成 `/work/...` 这种根目录下的假路径（§3.3 出错信号同一条）。

## 0. 本实验对应什么

- **教材**：第 21 章。覆盖博士层目标 LO21-01（关联与因果的边界）、LO21-02（表型治理与功效闸门）、LO21-03（Q/K 分工与过度校正、阈值推导）、LO21-04（QQ/λ 判读与候选区间界定）、LO21-05（出版级报告）；失效条件对应 §21.5.1–§21.5.7。硕士选读块（§21.4.1、§21.4.2、§21.4.3、§21.4.5、§21.4.6 的 callout）在本实验只作读图与表述参考，不另设步骤。
- **讲义**：p05 ② 前置表与 30 秒自检、③ 3.1 应用案例、④ 4.1–4.6、⑤ 5.1–5.8、⑥ 6.1–6.2、⑦ 统计插件（7.1–7.4）、⑧ AI 任务、⑨ E1–E10、⑩ 8 题、⑪ 文献。**注意两处编号差**：讲义头注与维护信息（L7/L9）写「输入为 p04 ⑥ 6.3」，而 p04 讲义 ⑥ 只有 6.1 与 6.2，交付清单是 **6.2**；`05_postgwas_interval.sh` L15 的头注同样写 ⑥ 6.3。按 6.2 读。
- **学时**：p05 共 4 学时（2 理论 + 2 实践，`00_design/course_contract.yaml`）；本实验是实践环节，作业另建议上机 5–7 小时（GEMMA 的 5 套 PC 扫描最耗时）、写报告 3 小时（`08_assessment/phd/assignments/p05_gwas_practice.md`）。
- **环境**：`ngs_phd_popgen`（`07_envs/conda/env_phd_popgen.yml`），**与 p04 同一个环境**。pin：`plink=1.90b6.21`、`gemma=0.98.3`、`bedtools=2.31.0`、`r-base=4.3.1`、`r-ggplot2=3.4.2`，`r-qqman` 无版本 pin（所以 qqman 版本必须实查后写进方法节）。**GAPIT 不在 conda 里**（契约 `env_exempt_tools`，yml 头注 L7 明示），要用按讲义 ⑤5.6 自装；课程环境里多模型一步**默认不做**，报告写「以 GLM/MLM 为主，BLINK 为可选扩展」。
- **一处与教材口径不一致的环境事实（按现读文件写）**：`env_phd_popgen.yml` L31–33 现在**真装了** `r-lme4` 与 `r-dplyr=1.1.4`（注释即写「p05 表型 BLUE/BLUP（讲义 ⑤5.2）用 lme4 + dplyr」），而教材 §21.3 L77 仍说「这两个包不在依赖清单里」。**本指导按 yml 现读写**：讲义 ⑤5.2 的 `library(lme4); library(dplyr)` 片段可以照抄运行；教材侧这句已登记为待改事实（§21.9 交总编的问题 5）。报告里要写你实际用的包与版本，不要再照抄「不在依赖清单」这句话。
- **本实验做不了、但能补上的三件事**（教材 §21.1 L14–22、§21.5.6）：① RDP1 的结构资产（`struct.{bed,bim,fam}`、`struct.pruned.*`、`pca.eigenvec`、`prune.prune.in`、`ld_decay.txt`）**在课程仓库没有任何现成脚本**，p04 的交付物是 PRJEB53625 的 40 株稻瘟菌，**不能直接用**——§3.1 给了一条最小重建命令链（`plink` 四步 + 复用 p04 的 LD 衰减脚本），路是通的，但**本指导未在集群实跑过**，剪枝行数与半衰距离仍属待测；② 区间内基因要的 GFF3 注释**课程不提供**——`06_data/reference/README.md` 第 24 行明写「p05 无需另备参考」，而 §3.6 必须要一份与基因型同版本的注释，取不到就停在 §3.6 之前并按 §3.6 的「注释从哪来」那一段写报告；③ GAPIT 的多位点模型默认不跑，与已发表 p 值矩阵的比对只到**秩相关与峰区间一致**，不做逐位点复现（§21.5.7）。

## 1. 实验前检查

- **前置自测**（题号在 `08_assessment/prerequisites/` 逐一存在）：`l0_01_linux` 第 5、9 题（登录节点与计算节点的分工、SGE 作业投递——5 套 PC 扫描在登录节点会被清退）；`l0_03_conda` 第 9、10 题（环境快照、作业里正确激活环境）与**第 6 题**（「不走 conda 的工具」——正是 GAPIT 这一类的豁免口径）；`l0_04_formats` 第 6、7 题（BED/GFF 坐标与半开区间、差一错误——§3.6 的 `parks` 与 `genes.bed` 全用得上）；`l0_06_stats` 第 4、5、6 题（p 值语义、Bonferroni 与 FDR 的适用边界、协变量共线混杂——§3.5 的阈值论证与 §3.3 的 Q 协变量）；`l0_02_r` 第 8、9、10 题（表格合并与排序、出版级图件导出——§3.7 的对答案散点与 §3.4 的图）；以及 `l1_phd` 的 **Q3、Q4**（`l1_p05` 模块：PLINK 四个过滤参数逐条解释、VCF 与 BED 坐标）。补课入口：硕士层 `m03` §6.2「VCF 格式与变异过滤」。
- **建/激活环境并核验工具链**（建环境与下载属允许的 I/O 型任务）。**在课程仓库根目录敲**：

  ```bash
  conda env create -f 07_envs/conda/env_phd_popgen.yml          # 只需一次（与 p04 共用）
  source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_popgen
  #   ↑ 个人电脑上没有该路径时直接 conda activate ngs_phd_popgen
  for t in plink gemma bedtools awk Rscript; do command -v $t; done
  plink --version | head -2 ; gemma -h | head -3 ; bedtools --version
  Rscript -e 'for (p in c("qqman","ggplot2","lme4","dplyr")) cat(p, as.character(packageVersion(p)), "\n")'
  Rscript -e 'cat("GAPIT:", if (requireNamespace("GAPIT", quietly = TRUE)) as.character(packageVersion("GAPIT")) else "无（多模型一步默认不做，见 §0）", "\n")'
  ```

  这条命令在做什么：SGE 作业不继承终端里的 conda 变量，两个 shell 脚本各自在开头激活一次（gemma L40、interval L37）。`05_gwas_gemma.sh` L42–44 逐个 `command -v plink gemma awk`，`05_postgwas_interval.sh` L39–41 检查 `plink bedtools awk sort`——**两份都不检查 `Rscript`**，而 §3.4 与 §3.7 的 R 步骤也要投 qsub，缺 `Rscript` 要到作业日志里才暴露。`command -v` 只对真二进制有意义：GAPIT 是按讲义 ⑤5.6 在 R 里 `library(GAPIT)` 挂载的 R 包，PATH 里没有这个可执行文件，`command -v GAPIT` 恒返回非零、装好了也判成缺失——所以上面用 `requireNamespace()` 查。

- **版本口径**：`plink=1.90b6.21`、`gemma=0.98.3`、`bedtools=2.31.0`、`r-base=4.3.1`、`r-ggplot2=3.4.2` 有 pin（`env_phd_popgen.yml`）；**`qqman` 与 `lme4`、`dplyr` 的版本未 pin**（`r-dplyr=1.1.4` 除外），方法学里只填你激活环境后打印的实际值。
- **脚本静态检查**（课程仓库根目录；应无输出、退出码 0、不产生文件）：

  ```bash
  bash -n 03_code/phd/scripts/05_gwas_gemma.sh
  bash -n 03_code/phd/scripts/05_postgwas_interval.sh
  Rscript -e "invisible(parse('03_code/phd/scripts/05_gwas_diagnostics.R'))"
  Rscript -e "invisible(parse('03_code/phd/scripts/04_ld_decay_plot.R'))"   # §3.1 第 ⑤ 步要复用它
  ```

  **两类命令不能混**：`bash -n` 只对 `.sh` 有意义；对 `.R` 跑它会报 `syntax error near unexpected token`（R 的 `<-` 在 bash 里是另一套语法）——那是用错了检查器。R 脚本的静态检查是 `parse()`：只解析不执行。
- **自查演示**（不需要集群，四个脚本各自打印 PASS 计数与汇总行）。在课程仓库根目录运行：

  ```bash
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch21_structure_confounding_ols.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch21_lambda_gc_scaling.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch21_thresholds_fwer_fdr.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch20_hwe_selfing_wahlund.py --selftest
  ```

  四组数是 3.3–3.6 的读图标尺，**都是合成算例（固定种子 20261104），只对各自的生成模型成立**：① 结构混杂 `6/6 PASS`——两亚群各半、Δ=2、两万个中性位点时，朴素回归的中性位点`p<0.05` 比例 **0.573**（名义 0.05）、`p<10⁻⁴` 占 **0.2676**、λ_GC **12.149**；加一个亚群指示协变量后回到 **0.051** 与 **1.005**；遗漏变量偏差斜率观测 **0.4791** 对理论 Δ·w_A·w_B = **0.5000**；② λ 标度律 `11/11 PASS`——χ²₁ 中位数 **0.454936**；N=413 → λ 观测 **1.0075** 对理论 **1.0083**，N=3500 → **1.0721 / 1.0700**，N=5000 → **1.1058 / 1.1000**，N=10000 → **1.2152 / 1.2000**；λ₁₀₀₀ 手算锚点 **1.3333**（n=150、λ=1.05）与 **1.0429**（n=3500、λ=1.15）；尾部钝感——注入 5 个强信号前后 λ 都是 **1.0679**，而最小 p 由 **1.71×10⁻⁵** 变 **2.50×10⁻¹²**；③ 阈值与错误率 `13/13 PASS`——设例三条线 **1×10⁻⁷ / 2×10⁻⁶ / 4×10⁻⁵**；80% 功效非中心参数**31.3**（α=2×10⁻⁶）对 **39.6**（α=5×10⁻⁸）、样本量代价 **+27%**、RDP1 规模检出限 **q≈0.076**；25 个连锁 SNP 在 SNP 层 BH 下报成 25 个「发现」而按块归并只有 **1** 个位点；置换成对阈值 **3.79×10⁻⁶**，三个口径的经验 FWER **0.009 / 0.205 / 0.050**；④ 自交与 Wahlund `10/10 PASS`——部分自交率 s=0.95（F = s/(2−s) = **0.9048**）时 **100%** 位点 `p<10⁻⁶`，三亚群等比例合并时 **99.6%**，分群后 `p<0.05` 只占 4.5%。

## 2. 实验数据

- **来源与规模**：Rice Diversity Panel 1（RDP1），`http://ricediversity.org/data/sets/44kgwas`，源自全球 **82 个国家**的 **413 份**代表性水稻种质（教材 §21.10 第 1 行；Zhao 等 2011）。原作者质控（call rate > 70%、MAF > 0.01）后发布 **36,901 个 SNP**，课程 §3.3 再质控后会更少。
- **⚠ 无登录号，且这是刻意登记的**：RDP1 是 ricediversity.org 的**面板名**，不是 INSDC/GEO 登录号。`06_data/accessions.tsv` 里**没有 RDP1 条目**（该表与 p05 相邻的只有 p04 的 `PRJEB53625`），`00_design/course_contract.yaml` 的 p05 数据条把 `accession` 记成 `RDP1` 本身。**报告里不许出现任何自造登录号**（`SRR…`、`PRJNA…` 一律不写）；引用这篇数据时写「RDP1，ricediversity.org」并核验文献元数据。
- **下载**（登录节点做；`--topic p05` 不碰 ENA，全是 HTTP 直取）：

  ```bash
  bash 06_data/phd/download_phd.sh --topic p05                       # 先 dry-run 看命令
  bash 06_data/phd/download_phd.sh --topic p05 --run \
       --outdir /d3/scratch/${USER}/ngs/data                        # 真下：8.5 MB + 23 MB（可选）
  ```

  落盘在 `--outdir` 下的 `p05_gwas/`：`RiceDiversity.44K.MSU6.Genotypes_PLINK.zip` 及其解压出的 `sativas413.ped/.map`（**PLINK 1 的 `.ped/.map`，不是 bed/bim/fam**，要先 `--file … --make-bed` 转换）、`RiceDiversity_44K_Phenotypes_34traits_PLINK.txt`、脚本自动 `tr '\r' '\n'` 后得到的 **`phenotypes_34traits.tsv`**（3.x 全部用它，**不要用原始 `.txt`**）、`RiceDiversity.44K.germplasm.csv`、`RiceDiversity.44K.MSU6.SNP_Information.txt`，以及可选的 `MixedModel_Pval_all.txt`（23 MB，§3.7 对答案用）。
- **先把工作变量定下来**（登录 shell 里敲，之后每一步都靠它；`qsub` 作业**不会**继承它，见 §3.3 与卷首的 here-doc 规则）：

  ```bash
  export P05=/d3/scratch/${USER}/ngs/data/p05_gwas     # 必须与上面 --outdir 拼出的目录完全一致
  ls -lh "$P05"/sativas413.ped "$P05"/phenotypes_34traits.tsv   # 两条都列出来再往下走
  ```

  目录名写错是最常见的「第一步 `No such file or directory`」；`ls` 没列出两个文件，就回上面核 `--outdir`。重开终端要重敲一次 `export`。

- **实测规格**（`06_data/phd/README.md` p05 节，2026-08-30 已真下载核对）：413 行 `.ped`、36,901 行 `.map`、表型文件 **36 列**、`.ped/.map` 合计 **8.5 MB**、已发表 p 值矩阵 **23 MB**。**列数口径要写清**：教材 §21.10 记「文件 36 列 = 34 项性状 + 2 个 FT ratio 派生列」，而 ID 列（HybID、NSFTVID）也占列；两处并存不矛盾（READMET 与教材在「34」归谁身上不同口径，教材 §21.9 末已登记该分歧）。**你只需在报告里写清「目标性状是第几列、列名是什么」**，不抄总结性的『36/34』。
- **三个必踩的坑（README 实测，逐条给了复现命令，见 §3.2）**：1. **表型原始文件是旧 Mac 的纯 CR 行尾**：`wc -l` 返回 **0**（整份文件只算「一行」），`file` 报的是 `CR line terminators` 而**不含 `CRLF`** 字样——只查 CRLF 的守卫会漏。`download_phd.sh` 已用 `tr '\r' '\n'` 清洗成 `phenotypes_34traits.tsv`；**自己另做表型仍须自查这一步**。2. **ID 要按 NSFTVID 匹配**：`.fam` 的 FID 是样本代号（HybID，形如 `081215-A05`），**IID 是纯数值的 NSFTVID**；表型文件第 1 列是 HybID、**第 2 列才是 NSFTVID**。实测 `.fam` IID ∩ 表型**第 2 列** = **413/413**，∩ **第 1 列** = **0**。按第 1 列 merge 会得到空表。3. **`.ped` 的表型列是 `-9`**（缺失占位）：必须用 `--pheno` 单独挂表型，不能指望基因型文件自带；GEMMA 也不读 `--pheno`，只读 `.fam` 第 6 列。
- **前置硬条件：结构资产必须自己在 RDP1 上重算，不能接 p04 的（教材 §21.1 L14–22、§21.5.6）**。本实验要五类资产：`struct.{bed,bim,fam}`（质控后的基因型）、`struct.pruned.*` 与 `prune.prune.in`（LD 剪枝集与其标记清单，K 与 `n_eff` 的来源）、`pca.eigenvec`（Q 协变量）、`ld_decay.txt`（两行半衰距离：`half_decay_bp` 与 `half_decay_baseline_adjusted_bp`，候选区间宽度用）。`03_code/phd/scripts/` 里**没有一条命令直接产出它们**：`04_popgen_*` 那三件是 PRJEB53625 稻瘟菌的（单倍体、40 Mb、无表型），与 RDP1 的二倍体水稻 413 份 36 列表型不可互换。**但零件都在**——`plink` 与你自己的 `ld_decay.txt` 计算链就是 §3.1 给的四步 `plink` 加 p04 的 `04_ld_decay_plot.R`（复用只读脚本，不改它）。§3.1 是**必需步骤**，不是可选的自查；若你确实拿不到资产，报告必须明写「结构资产缺失，Q/K 与区间宽度属假定链」，不得假装跑通。

- **已发表 p 值矩阵是「对答案」的金标准，不是「验收标准」**：`MixedModel_Pval_all.txt` 出自 EMMA 实现，协变量、K 的构造、内建过滤都与 GEMMA 不同（§21.5.7）。判据见 §3.7。

## 3. 实验步骤

> 每步五栏：**目的 / 命令 / 产出文件 / 检查点 / 出错信号（→ 教材节号）**。命令调用
> `03_code/phd/scripts/` 现有脚本，不复制全文；脚本名、参数名、行号、输出文件名已逐个与现版源码核对。
> **RDP1 全链与 `qsub` 各步在本机均未实测**（无 SGE、无 plink/gemma），凡属真实数据读数的检查点一律标「预期（未实测）」或只给定性判据。现跑实测的只有三类：`bash -n`／`parse()`／`--selftest`，外加本指导四段作业脚本的**生成与语法检查**、以及 §3.3 的协变量键连接与 §3.7／§3.6b 的 R 代码在合成输入上的试跑。
> `03_code/`、`06_data/`、`07_envs/` 只读；要改脚本一律「`cp` 个人副本 → 改指定行 → `grep` 确认 → `qsub` 副本」。

### 3.1 重建结构资产（`qsub`，一次性）+ 资产对账（登录节点，10 分钟）

- **目的**：两件事一起做。第一，把「p04 的交付物直接用」这个错误念头在第一条命令之前堵死：§21.5.6 是本章专列的失效，`.fam` 行数刚好凑得上、染色体名又能过 `--allow-extra-chr` 时，程序不报错，但 K 与 PC 描述的是另一批个体（真菌），结果无法解释。第二，手上没有 RDP1 资产的同学，用下面这条**最小重建链**把它造出来——全部是 PLINK 常规操作，没有隐藏步骤；失败点只会在「注释/版本」与「半衰距离」两处，本节的检查点就是为它们设的。
- **命令（a）重建**：生成作业脚本再投递。脚本里一律是字面绝对路径、不出现 `$P05`（见卷首 here-doc 规则）：

```bash
mkdir -p "$P05/popgen" "$P05/work" "$P05/results"
cat > "$P05/work/build_assets.sh" <<EOF
#!/bin/bash
#\$ -S /bin/bash
#\$ -N p05_assets
#\$ -cwd
#\$ -j y
#\$ -pe smp 4
#\$ -l h_vmem=16G
set -euo pipefail
source "\${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_popgen
cd ${P05}/popgen
# ① 文本 ped/map → PLINK 1 二进制（原始 413 份，这一步不做质控）
plink --file ${P05}/sativas413 --allow-extra-chr --make-bed --out sativas413
# ② 质控：四个阈值与 §3.3 完全一致（HWE 关）
plink --bfile sativas413 --allow-extra-chr --maf 0.05 --geno 0.1 --mind 0.1 --make-bed --out struct
# ③ LD 剪枝 → 剪枝集（K 与 n_eff 的来源）
plink --bfile struct --allow-extra-chr --indep-pairwise 50 5 0.2 --out prune
plink --bfile struct --allow-extra-chr --extract prune.prune.in --make-bed --out struct.pruned
# ④ Q 协变量：前 10 个主成分（--out pca 会写出 pca.eigenvec / pca.eigenval）
plink --bfile struct.pruned --allow-extra-chr --pca 10 --out pca
# ⑤ LD 衰减 → ld_decay.txt（复用 p04 的只读脚本；n_ind 传「染色体条数」= 2×个体数）
plink --bfile struct.pruned --allow-extra-chr --r2 --ld-window 99999 --ld-window-kb 1000 --ld-window-r2 0 --out ld
Rscript /课程仓库路径/03_code/phd/scripts/04_ld_decay_plot.R ${P05}/popgen/ld.ld 1000 10000 ${P05}/popgen/ld_decay \$(( 2 * \$(wc -l < ${P05}/popgen/struct.fam) ))
EOF
grep -n 'P05' "$P05/work/build_assets.sh" || echo "无变量残留（通过）"   # 有输出就是变量没展开
bash -n "$P05/work/build_assets.sh"           # 期望无输出、退出码 0
cd "$P05/work" && qsub build_assets.sh && qstat -u "$USER"
```

  三条口径要说清：① 第 ① 步的 `--file` 指向下载目录里的同名文本文件（`$P05/sativas413.ped/.map`），`--out sativas413` 才让后面所有步骤都能用 `sativas413.*` 这个名字；② 第 ⑤ 步的 `--ld-window-r2 0` 不能省，省了曲线尾部会凭空消失且不报错（p04 讲义 ⑤5.5 的同一坑），`n_ind` 必须传**染色体条数**`2×个体数`——`04_ld_decay_plot.R` 用它算 `1/n` 基线，传成个体数会把基线抬高一倍、`half_decay_baseline_adjusted_bp` 跟着变形（二倍体基线是 `1/(2N)`，p04 实验指导 §3.7 检查点⑤ 已写明）；③ `Rscript` 那一行的脚本路径要换成你机器上的仓库绝对路径，`/课程仓库路径/` 是占位。

- **命令（b）对账**（登录节点；资产重建作业跑完之后）：

  ```bash
  cd "$P05/popgen"
  wc -l sativas413.fam sativas413.bim struct.fam struct.bim prune.prune.in 2>/dev/null
  cut -d' ' -f1,2 sativas413.fam | head -3           # FID=HybID、IID=NSFTVID
  head -3 pca.eigenvec                               # 第 1、2 列是 FID/IID；首行可能是 "#FID IID PC1…" 表头，看一行再断言
  # ① eigenvec 的 IID 是否全在 .fam 里（逐个找到才算对）
  awk 'NR==FNR{iid[$2]=1; next} !($2 in iid)' struct.fam pca.eigenvec | wc -l
  # ①' 反向：.fam 的 IID 是否都有 PC（缺一个，§3.3 的键连接就会 FATAL）
  awk 'NR==FNR{pc[$2]=1; next} !($2 in pc)' pca.eigenvec struct.fam | wc -l
  # ② 染色体命名空间：基因型 vs GFF3（§3.6 的 comm 会再查一次）
  cut -d' ' -f1 struct.bim | sort -u | head -5
  awk '!/^#/{print $1}' <你的注释.gff3> | sort -u | head -5
  # ③ 半衰距离两行都在？
  grep -i 'half' ld_decay.txt
  ```

- **产出文件**：`$P05/popgen/` 下 `sativas413.{bed,bim,fam}`、`struct.{bed,bim,fam}`、`prune.prune.in/.out`、`struct.pruned.{bed,bim,fam}`、`pca.eigenvec/.eigenval`、`ld.ld`、`ld_decay.txt/.png/_binned.tsv`；作业日志 `p05_assets.o<作业号>`；`$P05/results/assets_inventory.md`（一张表的首段，进报告方法节与 §4 前四行）。
- **检查点**：
  1. `sativas413.fam` = **413** 行（原始面板；README 实测），`sativas413.bim` = **36,901** 行；`struct.fam` **≤ 413**、`struct.bim` 在 **36,901 的量级**或更少（质控后必然更少，§21.4.3 L158 要求记账）。**两个数要分别记**：413 是原始面板，不是质控后的验收数
  2. 上面 ① 的输出为 **0**（eigenvec 的每个 IID 都能在 `.fam` 里找到），①' 的输出也为 **0**（`.fam` 的每个个体都有 PC）。两条都要，方向不同：只有 ① 能过、①' 不为 0 时，`--pca` 用的是另一批个体（§21.5.6 第三条察觉动作）
  3. 染色体名两侧**同一套**（`Chr01`/`chr01`/`1` 不能混）——§3.6 的 `comm` 若交集为空会 FATAL，与其到那时才发现，不如现在改注释文件的命名（改法见 §3.6）
  4. `ld_decay.txt` 里 **两行半衰都在**（`half_decay_bp` 与 `half_decay_baseline_adjusted_bp`），且 `n_individuals` 那行等于 `2 × struct.fam` 行数；报告要写清 §3.6 用的是哪一行、为什么（p04 实验指导 §3.7 的四要素口径）
- **出错信号**：`sativas413.fam` = 40 行、`.bim` 是 contig 名 → **你接的是 p04 的稻瘟菌资产**（§21.5.6，`--allow-extra-chr` 会让它一路跑到底不报错）；`.fam` 行数与 eigenvec 对不上、① 或 ①' 不为 0 → Q 会错位，回第 ④ 步重算 PCA，不要手工补 IID；`grep -i half` 无输出或两行里有 `NA` → `ld_decay.txt` 没生成好（`NA` 说明分箱不足或 `--ld-window-r2` 漏了），§3.6 的 `HALF` 无从取值（脚本 L46 会以 `${HALF:?…}` 直接失败）；作业日志 `plink: command not found` → L 里的激活没生效（同 §3.3 出错信号第一条）；`04_ld_decay_plot.R` 报「没有落在 0–1000 kb 区间内的位点对」→ `ld.ld` 的窗口参数与脚本第 2 个参数（`max_kb`）不一致。

### 3.2 表型体检与治理（登录节点 + 小 R 脚本）

- **目的**：GWAS 的成败在跑第一条命令之前就定了大半（§21.4.2）。这一步把 36 列文件变成**三列**（FID、IID、value），并把「选的是哪一列、为什么、缺失怎么处置」写成可复核的记录。§21.5.3 的三张「不会报错」的脸全在这里堵：CR 行尾、ID 取错列、按行拼接换主人。
- **命令**：

  ```bash
  cd $P05
  # ① 行尾与列数：先查 \r 本身，不要只查 CRLF
  LC_ALL=C grep -c $'\r' phenotypes_34traits.tsv          # 期望 0（下载脚本已清洗）
  wc -l phenotypes_34traits.tsv                            # 期望 413（+1 若首行是表头）
  head -1 phenotypes_34traits.tsv | cat -A | head -2      # 看分隔符是制表符还是空格、首行是不是表头
  head -1 phenotypes_34traits.tsv | awk '{print NF}'       # 36 列（README 实测）
  # ② ID 列对账：两行分开读。.fam 取自 §3.1 转换出的 sativas413（原始 413 份，未质控）
  cut -d' ' -f2 popgen/sativas413.fam | sort -u > fam.iid
  awk -F'\t' 'NR>1{print $2}' phenotypes_34traits.tsv | sort -u > pheno.col2   # 第 2 列 = NSFTVID
  awk -F'\t' 'NR>1{print $1}' phenotypes_34traits.tsv | sort -u > pheno.col1   # 第 1 列 = HybID
  echo "对第2列 $(comm -12 fam.iid pheno.col2 | wc -l) / 对第1列 $(comm -12 fam.iid pheno.col1 | wc -l)"
  ```

  期望打印 `对第 2 列 413 / 对第 1 列 0`（README 实测）。**这两行要分开读**：对第 2 列得到 0 才是列取错了；对第 1 列得到 0 是正常的，因为它本来就不是 NSFTVID。这条对账必须在**原始** `.fam` 上做（§3.1 的 `sativas413.fam`）；质控后的 `struct.fam`/`gwas.fam` 会因为 `--mind` 少人，交集自然小于 413，用它做这条判据会得出假警报。

  ```r
  # ③ 选目标性状列 → 三列表型文件。列号与列名以 ② 的 head -1 为准，不要按论文顺序猜
  raw <- read.delim("phenotypes_34traits.tsv", check.names = FALSE)
  cat(ncol(raw), "columns\n"); print(colnames(raw)[1:6])       # 确认第 1/2 列是 ID
  trait <- raw[[<目标性状列号>]]                               # 抽穗期一类数量性状
  # 分布体检：偏度/峰度、缺失比例、是否有天花板效应
  cat("n =", length(trait), " NA =", sum(is.na(trait)),
      " range =", range(trait, na.rm = TRUE), "\n")
  # 轻度偏态 → log；极端分布 → RINT（代价：系数失去物理单位，§21.4.2）
  # R 基础包没有 rint()，标准实现就这一行（含 NA 保留）；并列多时先跑最后一行自查
  rint <- function(x) qnorm((rank(x, na.last = "keep") - 0.5) / sum(!is.na(x)))
  y <- if (<你判断偏态> ) log(trait) else trait
  # y <- rint(trait)                                           # 选 RINT 时用这一行替换上一行
  cat("并列比例 =", round(mean(duplicated(trait), na.rm = TRUE), 3),
      " 变换后 mean =", round(mean(y, na.rm = TRUE), 3), " sd =", round(sd(y, na.rm = TRUE), 3), "\n")
  out <- data.frame(FID = raw[[1]], IID = raw[[2]], value = y)  # 列序必须是 FID IID value
  write.table(out, "phenotypes.tsv", sep = "\t", quote = FALSE, row.names = FALSE, na = "-9")
  ```

  `rint()` 的自查口径：连续、无并列的表型做 RINT 后应是均值 ≈ 0、标准差 ≈ 1（纯分位数序列 `sd(qnorm(((1:413)-0.5)/413))` = **0.9996**，用真实表型现跑一般就在 1 附近）；**并列越多，标准差离 1 越远**——`rank()` 对并列取平均秩，同一个值的人会拿到同一个秩分，分布被压扁。用 `duplicated` 的比例先看：计数型/分级型表型（病害分级、分蘖数）并列往往过半，这类性状做 RINT 等于把真实分级抹平，应该换 log 或直接报两个口径的对照（教材 §21.4.2 的两条代价：极端个体离群信息被抹平、系数失去物理单位）。

  末行的 `na = "-9"` 是刻意的：`05_gwas_gemma.sh` L49 的头注说「缺失写 NA」，但脚本**没有传** `--missing-phenotype`（全文件 grep 无此参数），而 PLINK 1.9 的默认缺失表型值就是 **-9**；写 `NA` 会在 `--pheno` 处报 `Invalid phenotype value`。**这条口径差是要在报告里交代的工程细节**，想用 `NA` 就在个人副本的 L75–78 加 `--missing-phenotype NA` 并用 `grep` 确认。
- **产出文件**：`$P05/phenotypes.tsv`（三列，413 行 + 表头）；`$P05/results/qc_thresholds.md` 的表型段（目标性状列号与列名、CR 检查读数、`wc -l`、缺失比例、变换与理由、BLUE/BLUP 选择）。
- **检查点**：
  1. `LC_ALL=C grep -c $'\r'` = **0** 且 `wc -l` = **413**（**不是 0**；0 就说明整份文件只有一个「行」）
  2. 第 2 列交集 **413/413**、第 1 列交集 **0**（README 实测）——这两行必须都在 `qc_thresholds.md` 里
  3. 写清「36 列里我用的是第几列、列名是什么」，以及该列的缺失比例与是否做过变换（§21.4.2 L105–119）
  4. BLUE 还是 BLUP 要**给理由**：缺失多、重复不均衡 → BLUP 更稳但收缩会压低基因型间方差、轻微降功效；要报物理效应量 → BLUE。本数据是**已汇总的单环境表型**（没有 env/rep 列时），`lmer` 那一步**不做**，直接在报告写「本数据无多环境重复，BLUE/BLUP 不适用，改用原值 + 变换」——这比硬跑一个没有随机效应的模型诚实。若你自行补了多环境数据，按讲义 ⑤5.2 的模型做并写清代价
  5. 遗传力闸门：讲义 ④ 把「`H²` 低于 0.2」当闸门口径，教材 §21.4.2 L117 的同一个 0.2 是**设例前提**（效应均匀分摊、`M_eff` = 25000、`N` = 400），结论是功效极低、不是「绝无可能」。达不到这个量级时正确动作是回去改表型测量精度或扩样本，**不是放宽阈值**。本数据没有 `H²` 的现成读数时，用 GEMMA 的 `pve`（§3.3 的日志，属「待测」），并在报告里写清用的是哪一个口径。
- **出错信号**：`wc -l` = 0 → 纯 CR 行尾（§21.5.3 第二条；`file` 报 `CR line terminators`，用 `tr '\r' '\n'` 重做一次）；交集 = 0 而你以为取的第 2 列 → 分隔符不是制表符（用 `cat -A` 看），或首行是表头被算进了数据；**最隐蔽的一种**：413 行对 413 行、`cbind` 或各自 `sort` 后合并、程序全程不报错，表型却换了主人（§21.5.3 末句）——所以不要用行数当验收，要用「合并键唯一的行数 +抽查 3 个 IID 的表型值」；`Invalid phenotype value` → 缺失写成了 `NA` 而没加 `--missing-phenotype`。

### 3.3 质控 → Q/K → GLM 对照 + MLM 与 PC 扫描（`qsub`，最耗时）

- **目的**：一次提交跑完「质控 → 表型写进 fam → 协变量 → 亲缘矩阵 K → 不校正的 GLM 对照 → MLM 主模型 ×5 档 PC」。**GLM 对照一定要跑**：只有把 GLM 与 MLM 的 QQ 并排，才看得出校正做了什么、信号有没有被一起抹平（§21.4.3 L148、§21.5.1）。这一步的目标不是出结果，是出**两个可对照的读数**：λ 与检出位点数。
- **命令**（**改个人副本，不投公共脚本**）：

  ```bash
  cd "$P05/work"                                      # -cwd：作业日志落在投递目录
  cp <课程仓库路径>/03_code/phd/scripts/05_gwas_gemma.sh ./gwas_gemma.sh
  # 编辑器改副本七处（行号为现版）。值一律写字面绝对路径——作业进程没有 $P05：
  #   L46 BFILE     → /d3/scratch/<你的账号>/ngs/data/p05_gwas/popgen/struct
  #   L47 PRUNED    → …/p05_gwas/popgen/struct.pruned
  #   L48 EIGENVEC  → …/p05_gwas/popgen/pca.eigenvec
  #   L49 PHENO     → …/p05_gwas/phenotypes.tsv（必填，不能留空）
  #   L50 OUTDIR    → …/p05_gwas/work/gwas（L53 会 cd 进去，相对路径会失效）
  #   L51 MAF/GENO/MIND/HWE → 0.05 / 0.1 / 0.1 / 0（HWE 默认关，见检查点 5）
  #   L88 算 K 那行 plink 要补 --mind ${MIND}（理由见出错信号最后一条）
  grep -n 'BFILE\|PRUNED\|EIGENVEC\|PHENO\|OUTDIR\|MAF\|GENO\|MIND\|HWE\|PCLIST\|h_vmem\|-pe' gwas_gemma.sh
  grep -nF '$P05' gwas_gemma.sh || echo "无变量残留（通过）：脚本里只剩字面路径"
  ```

  **第八处要改的是 L100–103 的协变量生成**——现版按 eigenvec 的行序输出，与 `.fam` 行序无关；行数断言只查条数，查不出错位。把 `else` 分支那三行 `awk …` 换成按 `.fam` 行序键连接的五行：

  ```bash
      awk -v n="${NPC}" -v tag="covar_pc${NPC}" '
          NR==FNR{for(i=1;i<=n;i++) pc[$2,i]=$(2+i); ok[$2]=1; next}
          { if(!($2 in ok)){ printf "[FATAL] fam 个体 %s 没有 PC\n", $2 > "/dev/stderr"; bad=1; next }
            printf "1"; for(i=1;i<=n;i++) printf "\t%s", pc[$2,i]; print ""
            print $2 > (tag ".iid") }
          END{ if(bad) exit 1 }' "${EIGENVEC}" gwas.fam > "${tag}.txt"
  ```

  投递前先做一次**乱序自测**（只处理 400 行的文本、不涉及关联计算，在登录节点做；真正的 GWAS 一律 `qsub`）：把 eigenvec 的行打乱后重建协变量，输出应当**逐行不变**。

  ```bash
  cd "$P05/popgen"
  { grep '^#' pca.eigenvec; grep -v '^#' pca.eigenvec | shuf; } > pca_shuffled.eigenvec   # 乱序副本
  awk -v n=4 'NR==FNR{for(i=1;i<=n;i++) pc[$2,i]=$(2+i); ok[$2]=1; next}
      { printf "1"; for(i=1;i<=n;i++) printf "\t%s", pc[$2,i]; print "" }' \
      pca_shuffled.eigenvec "$P05/work/gwas/gwas.fam" > covar_pc4_shuffled.txt
  diff "$P05/work/gwas/covar_pc4.txt" covar_pc4_shuffled.txt && echo "顺序无关：通过"
  ```

  现版写法（按 eigenvec 行序）在同一自测下**必然报差异**——这就是要改的原因，不是理论隐患。

  ```bash
  qsub gwas_gemma.sh                                  # 只投副本，不投公共脚本
  qstat -u "$USER"
  ```

  脚本做什么：L40 激活环境；L42–44 查 `plink gemma awk`；L53 建 `OUTDIR` 并 `cd`（**这是路径陷阱的源头**）；L58–65 表型体检（查 `\r` → 拦 0 行 → 拦 <3 列）；L69–73 HWE 开启时打 `[WARN]`；L75–78 `plink --bfile … --allow-extra-chr --maf --geno --mind --pheno --make-bed --out gwas`；L82–84 断言 `.fam` 第 6 列有有效表型（>0）；L88–90 用剪枝集算 `kin_in` 并断言 `output/kin.cXX.txt` 存在；L93 GLM 对照（`-lm 4`，不校正）；L96–109 对 `PCLIST` 里每个 PC 数生成协变量并跑 MLM；**L101–103 是关键**：`awk 'NR==FNR{keep[$2]=1; next} ($2 in keep){…}' gwas.fam "${EIGENVEC}"`——按 IID 键匹配，第一列补 `1` 作截距（GEMMA 不会替你加，⑨ E3）；L105–107 断言行数 = `.fam` 行数；L108 `-lmm 4`；L112–119 打印每个模型的 `pve`/`se(pve)` 并在边界处 `[WARN]`；L121–122 汇总 `number of analyzed SNPs`。
- **产出文件**（都在 `$P05/work/gwas/`）：`gwas.{bed,bim,fam}`、`kin_in.*`、`output/kin.cXX.txt`、`covar_pc{0,2,4,6,10}.txt`、`output/glm_raw.assoc.txt`、`output/mlm_pc{0,2,4,6,10}.assoc.txt`（**六套 assoc**：1 个 GLM + 5 个 MLM）、对应的 `.log.txt`，以及作业日志 `p05_gwas.o<作业号>`。
- **检查点**：
  1. 日志里 `[INFO] 质控后：X 个标记 / Y 个个体`（L79）。**Y 不能预设是 413**：`--mind 0.1` 会剔个体，质控后个体数按实际保留的 IID 集报（§21.5.3 第四条察觉动作）
  2. **行数与行序都要查**：`covar_pc*.txt` 每份行数 = `gwas.fam` 行数（脚本 L105–107 的断言），并且配套的 `covar_pc*.iid` 与 `.fam` 第 2 列**逐行相同**。行数相等不代表对齐——按现版写法，两份文件同集不同序时行数断言照样通过（§21.4.3 L154 要求「行序必须与 `.fam` 一致，不能按特征向量文件的行序想当然」）。作业结束后在 `$P05/work/gwas/` 里核一遍：

  ```bash
  for NPC in 2 4 6 10; do
    paste -d'\t' <(cut -d' ' -f2 gwas.fam) "covar_pc${NPC}.iid" \
      | awk -v t="pc${NPC}" -F'\t' '$1!=$2{bad++} END{print t, "错位行数", bad+0}'
  done
  diff <(cut -d' ' -f2 gwas.fam | sort) <(cut -d' ' -f2 kin_in.fam | sort) && echo "K 的个体集与 gwas.fam 一致"
  ```

  3. `output/kin.cXX.txt` 非空（L90 的断言；缺失时按 ⑨ E5 去查 **GEMMA 默认写 `./output/`**）
  4. 六套 `.assoc.txt` 齐全（GLM 1 + MLM 5）。`grep -h 'number of analyzed SNPs' output/mlm_pc*.log.txt`那一行（L121–122）**就是方法学要报的数**：不是 `gwas.bim` 的行数——GEMMA 在 PLINK 过滤之上还有自己的内建过滤（⑨ E6、§21.4.3 L158）
  5. `HWE=0` 是默认（L51）。**若你改成了非 0**：日志会出现 `[WARN] 已开启 --hwe …`（L72），并且质控后位点数会**塌掉大半甚至只剩零头**——RDP1 是高自交二倍体群体，自交使杂合子系统性缺失，合成量级：部分自交率 s=0.95（F=0.9048）时 **100%** 位点 `p<10⁻⁶`，三亚群合并（Wahlund）时 **99.6%**（`demos/ch20_hwe_selfing_wahlund.py --selftest`）。方法学里写「因自交/克隆繁殖，未做 HWE 过滤」及替代防线（缺失率、等位深度平衡比、重复区掩码）（§21.4.4 L206、§21.5.5）
  6. `pve` 与 `se(pve)` 表（L112–119）：`pve = 1` 或 `se(pve) = nan` 是方差组分跑到边界的预警（⑨ E10），**不是可以忽略的警告**——样本量相对标记数太小，处置是减协变量或改 `GLM + 少量 PC`，并如实说明。
- **出错信号**：日志首行 `gemma: command not found` → 作业没继承环境，L40 没生效（⑨ E1 同族，属环境层）；`[FATAL] … 没有换行符（0 行）`（L63）→ 表型仍是纯 CR（§21.5.3）；`[FATAL] … 只有 N 列`（L65）→ 只给了性状没给 FID/IID；`[FATAL] gwas.fam 第 6 列没有有效表型`（L83）→ `--pheno` 没挂上或 IID 对不上（GEMMA 随后会报 `analyzed individuals = 0`，⑨ E4）；`[FATAL] fam 个体 … 没有 PC`（改过的协变量那行）→ eigenvec 比 fam 少人，回 §3.1 第 ①' 步；`[FATAL] covar_pcN.txt 行数 … 与 gwas.fam 不一致`（L105–107）→ eigenvec 与 fam 不是同一批个体。**一类不报错的错**：行数断言过了，但协变量行序跟着 `${EIGENVEC}` 走（现版 L101–103 的第二文件就是 eigenvec）——两份文件取自不同个体集或不排序时才会错位，而行数断言查不出它。处置就是上面那两处改动（按 `.fam` 行序键连接 + 乱序自测），改完不再依赖「两个文件恰好同序」这个假设。另有一类**跑通了但结论不成立**：K 用剪枝集算出来，但算 K 的那次 `plink`（L88）**没带 `--mind`**，质控却带了（L76）。按 §3.1 自建的资产通常不会触发（剪枝集是从质控后的 `struct` 派生的，个体集本来就同源）；但若剪枝集是别人给的、或你后来又改过 `--mind`，K 的个体集就与 `gwas.fam` 不同源——轻则 GEMMA 报个体数不匹配，重则顺序错位、结果无效（§21.4.3 L166）。处置：在副本 L88 补 `--mind ${MIND}`，并用上面那条 `diff` 断言两侧个体集相同。教材把这条要求写成「同源过滤」：两端用同一份个体清单。

### 3.4 诊断：先 QQ、再 λ、最后曼哈顿（`qsub`，约几分钟）

- **目的**：把「这张曼哈顿图可不可信」这个判断前移到看曼哈顿之前（§21.4.5 L210）。顺序不是习惯而是逻辑必需：**整体抬升**与**尾部离群**在曼哈顿图上肉眼无法区分，都是「很多超线的点」。本步同时产出定 PC 数的直接依据——λ–PC 曲线（双轴：λ 与检出位点数）。
- **命令**（先算 `n_eff`，否则两条阈值线没有意义；诊断要读六套 assoc 并出十来个图件，按计算纪律投 `qsub`，不在登录节点跑）：

```bash
cd "$P05/work"
N_EFF=$(wc -l < "$P05/popgen/prune.prune.in")   # 剪枝标记数，起点估计（不是严格上界）
N_IND=<质控后实际个体数>                          # 取 §3.3 日志 L79 的 Y；不传则不算 λ₁₀₀₀
echo "n_eff = $N_EFF   N_IND = $N_IND"
cat > run_diag.sh <<EOF
#!/bin/bash
#\$ -S /bin/bash
#\$ -N p05_diag
#\$ -cwd
#\$ -j y
#\$ -pe smp 1
#\$ -l h_vmem=8G
set -euo pipefail
source "\${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_popgen
export N_IND=${N_IND}
Rscript /课程仓库路径/03_code/phd/scripts/05_gwas_diagnostics.R ${P05}/work/gwas/output ${N_EFF} ${P05}/work/gwas/output/diagnostics
EOF
grep -n 'P05' run_diag.sh || echo "无变量残留（通过）：脚本里只剩字面路径"
qsub run_diag.sh && qstat -u "$USER"
```

  脚本做什么：L34 固定 `P_COL <- "p_wald"`（`-lmm 4` 同时给 `p_wald`/`p_lrt`/`p_score`，**固定报一个并写明是哪个**）；L36–39 `lambda_gc <- median(qchisq(1-p,1))/qchisq(0.5,1)`，分母 `qchisq(0.5,1) = 0.4549`；L41–44 找不到 `*.assoc.txt` 直接 `stop`（指向 ⑨ E5 的 `./output/`）；L57–58 用环境变量 `N_IND`换算 `lambda_1000 = 1 + (λ-1)·1000/N`；L64–65 两条线 `thr_gw = 0.05/n_eff` 与 `thr_sug = 1/n_eff`；L66–74 把字符型 `chr` 映射成数值 `CHR_num` 再画曼哈顿（⑨ E7 的处置已内置）；L76–83 超阈位点写 `hits_<tag>.tsv`（列 `chr rs ps allele1 allele0 af beta se p_wald`，**按 p 升序**）；L84–94 汇总 `model_summary.tsv`（`model, n_snp, lambda, lambda_1000, thr_genomewide, n_hits, min_p`）；L97–115 `lambda_vs_npc.png`——**双轴**，左轴 λ、右轴检出位点数；L117–121 四态判读提示。
- **产出文件**（默认落在 `<res_dir>/diagnostics/`）：`qq_{glm_raw,mlm_pc0,2,4,6,10}.png`（六张）、`manhattan_*.png`（六张）、`chr_map_*.tsv`、`hits_*.tsv`（有超阈位点时才写）、`model_summary.tsv`、`lambda_vs_npc.png`。
- **检查点**：
  1. **QQ 按顺序读，并把「应该看到什么」写成可证伪的诊断假设**：若结构混杂是主因，未校正的 GLM 那张会从最小 p 值处整体抬升，MLM 各档逐步贴回对角线（§21.5.1 的现场判据）；若 GLM 与 MLM 都贴对角线，说明这份数据在无校正模型上也没有结构信号——这条失效在你手上没有发生，报告要如实写，不要为了「跑出对照」硬解读；若 MLM 反而整体沉陷（λ<1），走第三态（过度校正）。合成标尺：加结构校正前 λ_GC **12.149**、`p<0.05` 比例 **0.573**，加一个亚群指示协变量后 **1.005 / 0.051**（`demos/ch21_structure_confounding_ols.py --selftest`）。**RDP1 上的实际读数待测**，本节只判形态与方向。

  2. λ 判读用**四态 + 经验口径**：≥1.20 整体抬升／1.00±0.05 仅尾部翘起／≤0.90 整体沉陷（过度校正）／≈1.00 全程贴合。**档位是经验口径，不许单独当通过标准**，必须与 QQ 形态、λ–PC 曲线一起读；第三态与第四态的分辨要点是「尾部有没有东西」，不是 λ 的小数（§21.4.5 L236–245）
  3. **λ–PC 曲线要双轴一起读，它是诊断线索而不是判决**：只按 λ 最小选，会选到信号全灭的过度校正档；常见的折中口径是「λ 接近 1 且信号未被抹平的最小 PC 数」——两条线一起看，λ 收敛到 1 附近、`n_hits` 没有同步归零。但这一条**不能单独定案**：λ≈1 不排除仍留着结构造成的假阳性（λ 只对整体抬升敏感），位点数不归零也不排除把真信号一起洗掉。定 PC 数要联读四样东西：QQ 形态、群体结构（前几个 PC 的散点或你的分群定义）、关键位点效应量在相邻 PC 档之间是否稳定、以及设计上已知的强效应位点还在不在。把「为什么是这一档」写成一句话，比写「λ 最接近 1」经得起追问（§21.4.5 L240–245、§21.5.2）。

  4. `model_summary.tsv` 六行齐全，`n_snp` 与 §3.3 日志的 `number of analyzed SNPs` 对得上；报告里写清 p 值列名是 `p_wald`（L34），不是笼统的「p 值」
  5. 传了 `N_IND` 才有 `lambda_1000` 一列。跨研究比较只能用它：手算锚点 λ₁₀₀₀(n=150, λ=1.05) = **1.3333**、λ₁₀₀₀(n=3500, λ=1.15) = **1.0429**（`demos/ch21_lambda_gc_scaling.py --selftest` 部分 2 同值）。λ 本身随样本量与多基因性上升：N=413 时理论 **1.0083**、N=10000 时 **1.2000**（同脚本部分 1）。所以「λ<1.05 才算干净」这条在大样本多基因性状上是错的；RDP1 的 413 份属小样本，λ 更贴近 1 是**预期**，不是功劳。
- **出错信号**：`在 … 下没找到 *.assoc.txt`（L43 的 `stop`）→ 路径指错，GEMMA 默认写 `./output/`（⑨ E5）；`qqman::manhattan` 崩在 `CHR column should be numeric` → 你绕开了脚本自己画图（脚本 L66 已用`as.integer(factor(chr))` 处理，⑨ E7）；六张 QQ 都贴对角线但 `n_hits = 0` → 可能是真没信号（第四态），回查 `pve` 与样本量，**不许放宽阈值编结果**（§21.4.5 第四态）；**λ 对尾部钝感要记住**：注入 5 个强信号前后 λ 都是 **1.0679** 一动不动，而最小 p 从 **1.71×10⁻⁵** 变成 **2.50×10⁻¹²**（`ch21_lambda_gc_scaling.py --selftest` 部分 3）——所以 λ 正常不等于没有真信号，λ 异常也不等于没有结果，两者都要看。这一栏正对 §21.5.1 的现场判据（GLM 与 MLM 两张 QQ 并排）与 §21.5.2 的第二条察觉（审阅顺序里必须有 QQ、λ、λ–PC 曲线三项）。

### 3.5 阈值论证（不新增计算，只做手算对账）

- **目的**：把「用 5e-8」这类习惯说法换成一条**可复核的推导链**：每条阈值的性质（严格界／近似口径／线索线）、分母从哪来、估计方法有没有校准证据。§21.4.4 L202 明文要求**不得只报一个数**；§21.5.2 的第一处察觉就是「报的是位点数而阈值来自未聚类的 SNP 层 BH」。
- **命令**（全部是手算，**用计算器或 R 复核一遍**，把算式贴进 `qc_thresholds.md`）：

  ```bash
  # 三条线（M = GEMMA 日志的 number of analyzed SNPs；n_eff = 剪枝集行数）
  #   朴素 Bonferroni   α = 0.05 / M            （严格界，通常过严）
  #   按 M_eff 的 FWER   α = 0.05 / n_eff        （近似口径，取决于 n_eff 估得准不准）
  #   suggestive 线      α = 1 / n_eff           （线索线：控制的是每次扫描的平均假阳性数）
  awk -v m=<M> -v n=<n_eff> 'BEGIN{printf "0.05/M=%.3g  0.05/n_eff=%.3g  1/n_eff=%.3g\n", 0.05/m, 0.05/n, 1/n}'
  # 发布位点数口径（教材 §21.4.4 手算锚点，用来对齐量级）
  awk 'BEGIN{printf "0.05/36901 = %.3g\n", 0.05/36901}'        # 1.35e-06
  # suggestive 线的两个不同量（次数期望 ≠ 事件概率）
  awk 'BEGIN{m=25000; printf "期望次数=%.0f  至少一次的概率=%.4f\n", m*(1/m), 1-(1-1/m)^m}'
  ```

  第二条打印 **1.35×10⁻⁶**（教材 §21.4.4 与 §21.10 的手算锚点）；第三条打印 `期望次数=1` 与`至少一次的概率=0.6321`——「期望 1 个」不等于「最多 1 个」，更不等于「出现一个就算发现」（§21.4.4 末段给了 `1-(1-1/25000)^25000 ≈ 0.6321` 的手算步骤）。
- **产出文件**：`$P05/results/qc_thresholds.md` 的阈值段；报告「阈值与候选区间」一节。
- **检查点**：
  1. **三个数都在，且每个都写了性质**：严格界（`0.05/M`，不需要任何依赖结构假设，代价是保守）／近似口径（`0.05/n_eff`，依赖 `n_eff` 估得准，偏小则实际 FWER 高于名义值）／线索线（`1/n_eff`）。只报一个数按 §21.4.4 L202 判不合格
  2. **剪枝行数只能当起点估计**：它不是有效检验数的严格上界——剪枝只按成对 r² 删标记，留下的仍可能相关，删掉的信息也可能仍有贡献，落在真实 `M_eff` 的哪一侧取决于标记集与阈值（§21.4.4 L188）。方法学里要写成「起点估计，须与 simpleM 或置换交叉核对」，**不许写「稳健上界」**
  3. `M` 取自 GEMMA 日志的 `number of analyzed SNPs`（不是 `.bim` 行数），`n_eff` 取自`wc -l < prune.prune.in`，两个分母各自的来源都要写在表里
  4. 人类 `5×10⁻⁸ = 0.05/10⁶` **只能作对照，不许当默认**（§21.4.4 L192）：它等于假定全基因组约一百万个独立常见单倍型块，搬到长 LD 自交作物上没有任何根据。若要做比较，必须连同「哪个设例口径」一起写（设例：剪枝集 25000 当 `M_eff` 时严 40 倍；比朴素 `0.05/500000 = 1×10⁻⁷` 严 2 倍——后者只依赖两个分母）。代价可算：80% 功效所需非中心参数 **31.3**（α=2×10⁻⁶）对 **39.6**（α=5×10⁻⁸），样本量约多 **27%**；RDP1 规模上 α=2×10⁻⁶ 的检出限已是解释 **7.6%** 方差的位点（`ch21_thresholds_fwer_fdr.py --selftest` 部分 B）
  5. 报告里要明写**发现单位**：若报「显著 SNP 数」而阈值来自未聚类的 SNP 层 BH，就已经错了。合成标尺：25 个连锁 SNP（块内等效相关 0.95）在 SNP 层 BH（q=0.05）下报成 **25 个发现**，按块归并后只有**1 个**独立位点（同脚本部分 C）。要报位点数就走两条合法路线之一：预定义区域（组内校准 p 值 +Bonferroni／BH／BY），或数据驱动 clumping **加另行校准**（不能把簇内最小 p 当位点 p）（§21.4.4 L180–182）。
- **出错信号**：报「n_eff 是上界」→ 与 §21.4.4 L188 冲突；把 SNP 层 BH 的显著数当位点数 → §21.5.2；只报一个数、或只写「按多重检验校正后 α=…」→ §21.4.4 L202 判不合格；把置换成对阈值当「独立校准」→ 置换的 0.050 是**构造内结果**（阈值与回算同一批最小 p 值，必然贴合），要另起独立重复（不同种子、独立模拟或独立样本）才算校准（§21.4.4 L200）；顺带记住置换的**有效性依赖交换性**：群体分层、家系亲缘、批次存在时全样本无条件重排不满足，受限置换或残差置换都只是近似（§21.4.4 L196、§21.5.2）。

### 3.6 后 GWAS：clump → 区间 → 基因（`qsub`）

- **目的**：把峰变成**区间**而不是一个 SNP，并把区间内的基因整理成可排序的候选表。§21.4.6 的四步：取先导 SNP（前提是过了 QQ 关）→ `--clump` 归并成独立位点 → 按 LD 半衰距离扩成候选区间 →提取区间内基因并排序四类证据。§21.5.4 明写：峰内最近或最显著的基因都只是候选，不是因果基因。
- **命令**：

  ```bash
  cd "$P05/work"      # -cwd；相对路径按投递目录解析（本脚本不像 gemma 那样 cd 进 OUTDIR）
  cp <课程仓库路径>/03_code/phd/scripts/05_postgwas_interval.sh ./postgwas_interval.sh
  # 编辑器改副本五处（行号为现版；同样写字面绝对路径，不留 $P05）：
  #   L43 BFILE  → /d3/scratch/<你的账号>/…/p05_gwas/work/gwas/gwas
  #   L44 ASSOC  → …/p05_gwas/work/gwas/output/mlm_pc4.assoc.txt（换成你在 §3.4 选定 PC 数的那一份）
  #   L45 GFF    → …/p05_gwas/ref/<你的注释>.gff3（必填，与基因型同版本，见下方「注释从哪来」）
  #   L46 HALF   → <ld_decay.txt 里的半衰距离，单位 bp>（必填）
  #   L47 P1/P2/R2/KB → 1e-5 / 1e-3 / 0.2 / 500（显式给定，不是 PLINK 默认）
  grep -n 'BFILE\|ASSOC\|GFF\|HALF\|P1\|P2\|R2\|KB\|OUTDIR\|h_vmem\|-pe' postgwas_interval.sh
  qsub postgwas_interval.sh
  qstat -u "$USER"
  ```

**注释从哪来（本实验的一处硬缺口，必须先解决再投这一步）**：`06_data/phd/download_phd.sh` 的 `fetch_p05` 只下基因型、表型、种质清单、SNP 信息四个文件，**没有 GFF3**；`06_data/reference/README.md` 第 24 行也明写「p05 无需另备参考」。而这一步没有注释就出不了基因表。做法：自备一份**与基因型同版本**的注释——RDP1 的 44K 芯片按 MSU6 坐标设计（下载文件名里就写着 `MSU6`），所以注释的坐标版本与染色体命名都要与 `sativas413.map` 对得上；校内集群的共享备料路径由助教公布（数据 README 未登记集群侧路径，勿编造），校外可从 MSU/RAP-DB 或 Ensembl Plants 取对应装配的 GFF3。拿到手先做两件事：① 看染色体名与基因条数量级（下一段的命令）；② 在报告方法节写清注释版本、来源与获取日期——**换一份注释，区间内的基因表就换一套**。确实拿不到时，§3.6 只做到 `peaks.bed`，报告写「区间已界定，基因列因注释不可得留空」，不许凭文献猜区间内有哪些基因。

染色体命名不一致时只改**注释的第一列前缀**，注释行与列顺序都不动（对数万行的 GFF3 直接全局替换会改坏 `ID=` 里的内容）：

```bash
awk 'BEGIN{FS=OFS="\t"} /^#/{print; next} {sub(/^Chr/, "", $1); print}' "$P05/ref/<你的注释>.gff3" > "$P05/ref/anno_num.gff3"
# 反向（注释纯数字、关联结果带前缀）就改 assoc 的第一列，或用 sed 's/^/>Chr&/' 的另一套写法
cut -f1 "$P05/ref/anno_num.gff3" | grep -v '^#' | sort -u | head -5   # 与 §3.1 ② 的输出逐行对照
```

  脚本做什么：L37 激活环境；L39–41 查 `plink bedtools awk sort`；L51–59 **先核染色体命名交集**（`comm -12` 两侧染色体名，为空就 FATAL 并打印示例——⑨ E9 的「不报错的错误」被提前拦下）；L62–65 `plink --clump`，**`--clump-field p_wald --clump-snp-field rs` 显式写**（PLINK 默认找 `P` 与`SNP`，⑨ E8）；L66–73 `clump.clumped` 为空时 WARN 后 **`exit 0`**——所以**必须看日志**；L78–82 区间：`s = $4 - H; if (s < 1) s = 1`，输出 `$1, s-1, $4+H, $3, $5`（**1-based → 0-based 半开**，起点减 1、终点不减，且先钳位再减）；L85–86 `awk '!/^#/ && $3=="gene" {print $1,$4-1,$5,$9,".",$7}'` 转`genes.bed`（**按 GFF 第 3 列取 gene**，不是 `$6`）；L87–88 `bedtools intersect -wa -wb`；L95–103 候选表骨架（四列 `evid_*` 留空 + `priority`）。
- **产出文件**（`$P05/work/postgwas/`）：`chr_shared.txt`、`clump.clumped`、`peaks.bed`、`genes.bed`、`candidate_genes_raw.tsv`、`candidate_genes_table.tsv`，加作业日志。
- **检查点**（**BED 换算可以完全手算复核，这是本步最硬的自查**）：1. `clump.clumped` 非空、日志有 `[INFO] clump 得到 N 个独立位点`（L75）。**空的 `clump.clumped` 不等于没有信号**：L66–73 会 WARN 后 `exit 0`，且**不要在此时调大 `--clump-p1`**——教材 §21.4.6 与 ⑥ 6.2 都说，该做的是回 §3.4 看 QQ（尾部也贴对角线 → 本来就没有可检出信号）；2. 四个 clump 参数写进报告：`p1=1e-5`、`p2=1e-3`、`r²=0.2`、窗口 500 kb。它们**不是 PLINK 默认**（默认 1e-4 / 1e-2 / 0.5 / 250 kb），是显式选择，必须交代。`r²=0.2` 的含义：与先导 SNP 相关度高于 0.2 的标记算同一个位点；500 kb 是上限，防止长 LD 区间无限外延；3. **BED 是 0-based 半开**，手算一遍：设先导 SNP 的 `ps` = 12,345,678（1-based）、`HALF` = 150,000 bp，则左端 `s = 12,345,678 − 150,000 = 12,195,678`，BED 起点取 `s − 1 = 12,195,677`；右端 `12,345,678 + 150,000 = 12,495,678`；记录是 `chr 12195677 12495678`，长度 **300,001 bp**（教材 §21.4.6 L281–283 的同一手例）。**终点为什么不减 1**：BED 的 `end` 指向区间之后第一个碱基，1-based 闭区间终点可直接当半开区间终点。**宽度要用 BED 两列现算，不要背公式**：`end − start`，只有没被钳位时才等于 `2×HALF + 1`——`HALF` 是**单侧**半衰距离，全宽是两侧之和再加先导 SNP 本身那 1 bp。若先导 SNP 在 120,000 处，左端为负 → 脚本钳位到 1、BED 起点为 0，区间从染色体第一个碱基开始，**实际宽度因此短于 `2×HALF+1`**：设 `HALF=150000`、`ps=120000`，则 `s = 120000−150000 < 1` 被钳到 1、`start = 0`、`end = 120000+150000 = 270000`，`end − start = 270,000`（不是 300,001；四则运算可手算复核）。报告里写实际宽度并说明是否钳位，不要写「宽度应等于半衰距离」。**用自己的 `clump.clumped` 与 `HALF` 复算一条，与 `peaks.bed` 逐字段对上**：
4. 基因数取 `candidate_genes_raw.tsv` 的行数（每个峰×基因一行，同一个基因跨多个峰会出现多次，去重后才是个数）。区间宽度异常（比如只有 1 bp 或上万 kb）→ 查 `HALF` 单位（bp 还是 kb）与坐标系；5. **`strand` 列不要引用**：`05_postgwas_interval.sh` L99–102 取的是 `$10`，而 `candidate_genes_raw.tsv` 里第 10 列是 `genes.bed` 的 score 占位 `.`、第 11 列才是 strand——该列输出恒为 `.`。教材 §21.4.6 L302 已声明**不引用该列**，属脚本缺陷，修正另行登记；你的候选表也照此处理，在报告里注一句。判句要能自己数出来：`head -1 candidate_genes_raw.tsv | awk '{print NF}'` 得 11 列。
- **出错信号**：`[FATAL] GFF3 与关联结果的染色体名没有任何交集`（L55）→ 命名空间不一致（⑨ E9）；`Error: No significant --clump results` 或日志提示缺 P/SNP 列 → `--clump-field`/`--clump-snp-field` 没写对（⑨ E8）；`[WARN] 区间内一个基因都没有`（L90）→ 先排除染色体命名（第 0 步已过则排除），再查**GFF 第 3 列是不是真的用 `gene` 这个词**（有些注释用 `mRNA`/`transcript`）；若你照抄讲义 ⑤5.8 的旧写法 `bedtools intersect … | awk '$6=="gene"'`，候选表会**恒空**——4 列 BED 前缀 + 9 列 GFF 之后 `$6` 是 source 列，type 在第 7 列（§21.4.6 L285）。**本栏对应 §21.5.4**：这一条失效不是「跑失败」，而是「跑通了却把最近或最显著的基因当因果基因」，所以区间宽度、四列证据与共定位检查要在报告里逐条交代。教材 §21.5.4 给的写作口径是「四条里缺两条以上，结论只能写到『区间内候选基因包括……』这一级」，§21.4.6 的硕士选读块同款写「四列里至少两列独立指向同一基因」——照抄时标明节号即可，它是**写作规范**，不是可以算出来的统计阈值，别写成自己的硬门槛。

### 3.6b 峰的局部放大图（`qsub`，作业交付物里的 `fig4_locus_zoom`）

- **目的**：区间定下来之后，用一张「先导 SNP ±200 kb」的局部图看清峰形：连片峰的先导 SNP 最显著、两侧邻居随 LD 衰减回落；孤峰则是单点跳出、侧翼毫无起色（§21.4.5 的峰形判读、§21.5.4 第一个检查）。这张图是作业 ② 里的 `figs/fig4_locus_zoom.png`，三个核心脚本都不产出它，所以单列一步。
- **命令**（先算先导 SNP 与邻居的 r²，再画图；两步都在同一个作业里）：

```bash
cd "$P05/work"
mkdir -p "$P05/results/figs"
LEAD=$(head -2 gwas/output/diagnostics/hits_mlm_pc4.tsv | tail -1 | cut -f2)   # hits 按 p 升序，第一行就是先导 SNP
echo "lead = $LEAD"
cat > locus_zoom.sh <<EOF
#!/bin/bash
#\$ -S /bin/bash
#\$ -N p05_locus
#\$ -cwd
#\$ -j y
#\$ -pe smp 2
#\$ -l h_vmem=8G
set -euo pipefail
source "\${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_popgen
plink --bfile ${P05}/work/gwas/gwas --allow-extra-chr --r2 --ld-snp ${LEAD} \\
      --ld-window 99999 --ld-window-kb 200 --ld-window-r2 0 --out ${P05}/work/locus_ld
cat > ${P05}/work/locus_zoom.R <<'RSCRIPT'
assoc <- "${P05}/work/gwas/output/mlm_pc4.assoc.txt"
ld    <- "${P05}/work/locus_ld.ld"
out   <- "${P05}/results/figs/fig4_locus_zoom.png"
d <- read.table(assoc, header = TRUE, stringsAsFactors = FALSE)
d\$p_wald[d\$p_wald <= 0] <- .Machine\$double.xmin
d\$neglogp <- -log10(d\$p_wald)
hits <- "${P05}/work/gwas/output/diagnostics/hits_mlm_pc4.tsv"
# 先导 SNP 的定义与 plink 那一侧一致：都取 hits 表第一行（按 p 升序），并列时不至于两边各挑一个
ln   <- if (file.exists(hits)) read.table(hits, header = TRUE, stringsAsFactors = FALSE)[1, "rs"] else d\$rs[which.min(d\$p_wald)]
lead <- d[d\$rs == ln, ][1, ]
W <- 200000L
w <- d[d\$chr == lead\$chr & abs(d\$ps - lead\$ps) <= W, ]
if (file.exists(ld)) {
  l <- read.table(ld, header = TRUE, stringsAsFactors = FALSE)
  l\$rs <- ifelse(l\$SNP_A == lead\$rs, l\$SNP_B, l\$SNP_A)
  w <- merge(w, unique(l[, c("rs", "R2")]), by = "rs", all.x = TRUE)
} else { w\$R2 <- NA_real_ }
ramp <- colorRampPalette(c("#2166AC", "#B2182B"))(100)
w\$col <- ifelse(is.na(w\$R2), "grey65", ramp[pmax(1, pmin(100, ceiling(w\$R2 * 100)))])
png(out, width = 1600, height = 1000, res = 200)
plot(w\$ps / 1e6, w\$neglogp, pch = 19, cex = .7, col = w\$col,
     xlab = "Position (Mb)", ylab = "-log10(p)",
     main = sprintf("Locus zoom: %s (chr %s, +/- %d kb, n = %d)", lead\$rs, lead\$chr, W %/% 1000L, nrow(w)))
abline(v = lead\$ps / 1e6, lty = 2)
points(lead\$ps / 1e6, lead\$neglogp, pch = 18, cex = 1.6, col = "#B2182B")
legend("topright", legend = c("r2 > 0.5", "r2 <= 0.5", "no r2"), pch = 19,
       col = c(ramp[100], ramp[20], "grey65"), bty = "n", cex = .8)
dev.off()
cat("lead:", lead\$rs, "chr", lead\$chr, "ps", lead\$ps, "p", signif(lead\$p_wald, 3), "\n")
RSCRIPT
Rscript ${P05}/work/locus_zoom.R
EOF
grep -n 'P05' locus_zoom.sh || echo "无变量残留（通过）"
qsub locus_zoom.sh && qstat -u "$USER"
```

  三处口径：① `--ld-snp` 只在部分 PLINK 1.9 版本可用（本指导无 plink，未实测）：如果你的版本报未知参数，就去掉它跑整个窗口的 `--r2`，R 脚本里的 `ifelse(SNP_A == lead, SNP_B, SNP_A)` 这一行本来就是为这种输出写的；② `hits_*.tsv` 只有「通过 genomewide 阈值的位点」时才存在，全空说明没有可选峰——此时这张图**不做**，报告写「未检出超阈位点，局部放大图缺项」并解释，不要拿 suggestive 线的位点充数；③ 先导 SNP 是区间锚点不是答案，图上标它只是为了说明峰形，图注必须写「先导 SNP + 窗口半宽 + 颜色代表 r²」，不能写「候选基因所在位点」。

### 3.7 对答案：秩相关 + 峰区间，不追逐位相等（`qsub`）

- **目的**：用已发表的 p 值矩阵判断「流程通没通」，并把这个判断的判据写对。§21.5.7 是本专题最容易被误读成「流程失败」的一条：两套数字在实现层面不可逐位对齐（EMMA vs GEMMA、协变量、K 的构造、内建过滤都不同），要求逐位点相等会导致无休止调参，还可能把真实的工程错误掩盖过去。
- **命令**（一个 R 作业；`MixedModel_Pval_all.txt` 23 MB，读入与两万行 merge 都算计算，投 `qsub`）：

```bash
cd "$P05/work"
cat > answer_check.sh <<EOF
#!/bin/bash
#\$ -S /bin/bash
#\$ -N p05_answer
#\$ -cwd
#\$ -j y
#\$ -pe smp 1
#\$ -l h_vmem=8G
set -euo pipefail
source "\${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_phd_popgen
cat > ${P05}/work/answer_check.R <<'RSCRIPT'
p05  <- Sys.getenv("DATADIR")            # R 不会替你展开字符串里的变量，路径从环境变量取
stopifnot(nzchar(p05))
pub  <- read.delim(file.path(p05, "MixedModel_Pval_all.txt"), check.names = FALSE)
mine <- read.delim(file.path(p05, "work/gwas/output/mlm_pc4.assoc.txt"))
str(pub, list.len = 8)                   # 先看列名：rs 列叫 SNP 还是 Marker？目标性状列叫什么？
TRAIT <- "<目标性状的 p 列名>"
stopifnot(!anyDuplicated(mine\$rs))      # 两侧都必须键唯一，缺一侧的检查会漏
stopifnot(!anyDuplicated(pub[["<rs列名>"]]))
m <- merge(mine[, c("rs", "chr", "ps", "p_wald")],
           pub[, c("<rs列名>", TRAIT)], by.x = "rs", by.y = "<rs列名>")
m\$neglog_mine <- -log10(m\$p_wald)
m\$neglog_pub  <- -log10(m[[TRAIT]])
cat("n_matched =", nrow(m), " n_NA_pub =", sum(!is.finite(m\$neglog_pub)), "\n")
cat("spearman =", cor(m\$neglog_mine, m\$neglog_pub, use = "complete.obs", method = "spearman"), "\n")
NTOP <- 20L
top_mine <- head(m[order(m\$p_wald), c("rs", "chr", "ps", "p_wald")], NTOP)
top_pub  <- head(m[order(m[[TRAIT]]), c("rs", "chr", "ps", TRAIT)], NTOP)
cat("你的前 5 个峰：\n");     print(head(top_mine, 5))
cat("已发表的前 5 个峰：\n"); print(head(top_pub, 5))
cat("两侧峰是否落在同一区间：逐行对照上面两张表，同一染色体且距离 < 一个 HALF 才算一致\n")
png(file.path(p05, "results/fig_answer_check.png"), width = 1200, height = 1200, res = 200)
plot(m\$neglog_pub, m\$neglog_mine, pch = 16, cex = .4,
     xlab = "Published -log10(p)", ylab = "Your -log10(p)", main = "Answer-key check")
abline(0, 1, lty = 2); dev.off()
write.table(m, file.path(p05, "results/answer_check.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
RSCRIPT
DATADIR=${P05} Rscript ${P05}/work/answer_check.R
EOF
grep -n 'P05' answer_check.sh || echo "无变量残留（通过）"   # 有输出说明变量没展开，作业里会读到空路径
qsub answer_check.sh && qstat -u "$USER"
```

  两处容易翻车的写法：① **路径不要写进 R 的字符串字面量**——`"$P05/xxx"` 在 R 里是一个叫 `$P05/xxx` 的目录名，直接 `cannot open file`；用 `Sys.getenv()` 或 `file.path()` 拼。② `cor()` 的 `use` 默认值是 `"everything"`：已发表矩阵各性状的缺失位点不同，一列里有 `NA` 就整个返回 `NA`，看起来像 merge 失败，所以显式写 `use = "complete.obs"`。先看 `n_NA_pub` 那一行，再判秩相关。

- **产出文件**：`$P05/results/answer_check.tsv`（`rs` / `chr` / `ps` / 自己 `-log10 p` / 已发表 `-log10 p`）＋ `$P05/results/fig_answer_check.png`。
- **检查点**：
  1. 判据只有两条：**整体秩相关高** + **主要峰落在同一物理区间**。都有就说明流程通了，**不要求逐位相等**（§21.5.7 L376、§21.6 L386）。数值本身**待测**，不进检查点
  2. 秩相关低时按同一张清单排查**工程问题**，顺序不能反：① ID 列是不是取错（§3.2 的第 2 列对账）；② 表型文件是不是旧 Mac CR（`wc -l` = 0）；③ 有没有用 `--pheno` 把表型挂上（§3.3 的 `.fam` 第 6 列）；④ **36 列里选的是不是目标性状列**——秩相关低时先怀疑列选错，这是最常见的一种（§21.5.7、`06_data/phd/README.md` 自查判据）。地图问题排完，再谈模型差异
  3. 方法学里写「与已发表结果做**秩相关与峰区间一致性**比对」，**不写「逐位点复现」**
  4. 峰顶位点的 p 值量级要抽查（同量级即可，不看小数）。若某个峰在你的结果里有、已发表里没有，记录它并回到 §3.6 查区间与基因，不要为对齐而改模型。
- **出错信号**：要求「两表 p 值完全一致」→ 会陷入换 PC 数、换 K 的构造、换表型变换的无休止调参（§21.5.7）；秩相关低却先去调 PC 数 → 排查顺序反了；`merge` 出来 0 行 → 键取错（`rs` 与行号、或两边 marker ID 命名空间不同）；两表都有 413 行就以为对上了 → §21.5.3 末句的「表型换主人」正是这种脸。

### 3.8 AI 任务与提交物收尾（讲义 ⑧、作业 ⑨）

- **目的**：把「模型跑完了图挺好看」变成一次可复核的**外部质疑**：让 AI 读 QQ 与 λ，然后按五条核查逐条判它说得对不对，并**按它的建议真的重跑 ≥2 组参数**。评分口径在作业 ⑨：只考可复核性，「AI 输出全部正确且无验证过程」本栏不得分，未用 AI 但写明原因不扣分。
- **命令**（提示词与日志都留档；**第一轮故意不说模型、PC 数、样本量**）：

  ```bash
  mkdir -p "$P05/ai_logs"
  # ① 第一轮提示词（原文保存，别改写）：只给 QQ 图（或分位数数据）与 λ，不给模型/PC 数/N
  #     「这是我 GWAS 后的 QQ 图与 lambda_GC=…，请评估结果是否合格、是否需要调整协变量重跑」
  # ② 记下 AI 回答 → 按作业 ⑨ 的五条核查逐条填 ai_audit.tsv
  # ③ 「按建议重跑至少两组参数」**不需要再排队**：§3.3 已一次跑完 PCLIST=0 2 4 6 10 五档，
  #    §3.4 的 model_summary.tsv 与六张 QQ 都在手上，直接取对应两档并排即可。
  #    只有当你改了 MAF/缺失率、换了 K 或换了表型时才要重投作业（那时改副本再 qsub）。
  awk 'NR==1||$1=="mlm_pc2"||$1=="mlm_pc10"' "$P05/work/gwas/output/diagnostics/model_summary.tsv" \
      | column -t                                        # 这三行就是「改了之后到底改动了什么」
  ```

- **产出文件**：`$P05/ai_logs/prompt_and_reply.md`（原文往返，含模型名与日期）、`$P05/results/ai_audit.tsv`（五条逐条判定）、`figs/fig_ai_before_after.png`（前后 QQ + λ 并排）。
- **检查点**（五条核查，逐条要有「哪里错了／我怎么发现的」）：1. 它有没有**区分整体抬升与尾部抬升**（笼统说「偏离说明有关联信号」即不合格）；2. 它有没有**追问模型与校正**（不问 GLM/MLM、几个 PC、K 怎么算、样本量多大即不合格）；3. 它有没有把 **λ 的经验区间当绝对标准**（「λ=1.15 属正常，不用处理」是越界）；4. 它的**建议在你的数据上是否有效**——按它说的重跑，前后 QQ 与 λ 并排；5. 它有没有提示**过度校正的风险**（一味建议「多加几个 PC」是隐患）。**必须给判定**：它的建议是「改善了模型」还是「只是把信号一起抹平了」，**用 λ 与显著位点数两个指标同时说明**；它在追问后改口，就记录改口前后的差异。
- **出错信号**：只有一段 AI 原文、没有重跑 → 该栏不得分（作业 ⑨）；按 AI 建议加到 PC 全灭还写「改善了模型」→ 与 §21.4.5 L240 的过度校正判读相反；把 AI 说的「λ 正常」直接抄进报告 →漏了标度律（λ 随 N 与多基因性上升，§21.4.5）。**本栏对应 §21.5.2 第三条察觉**：「λ 一路降到 1 以下而位点数同步归零」就是过度校正，此时无论 AI 怎么说都不能写「改善了模型」。

## 4. 结果记录表（学生填写，不预填；「自查判据」列给来源口径）

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 1 | 实查版本：plink / gemma / bedtools / R / qqman / lme4 / dplyr | 版本号 | | 应为 1.90b6.21 / 0.98.3 / 2.31.0 / 4.3.1 / 未 pin / 未 pin / 1.1.4（`env_phd_popgen.yml`），以激活环境实查为准 |
| 1 | 四个 `--selftest` 的 PASS 计数 | 条 | | 6/6、11/11、13/13、10/10（本指导现跑，2026-11-11） |
| 2 | 下载体积：基因型 + 已发表 p 值 | MB | | 8.5 / 23（`06_data/phd/README.md` p05 节实测） |
| 2 | 表型文件行数 / 列数 / 目标性状列名与列号 | 行 / 列 / 文本 | | 413 行、36 列（README 实测）；**列名与列号必须自己写**，不抄『36/34』口径 |
| 2 | `LC_ALL=C grep -c $'\r'` | 个 | | **必须 0**；>0 说明未清洗（§21.5.3） |
| 2 | `.fam` IID ∩ 表型**第 2 列** / ∩ **第 1 列** | 个 | | **413 / 0**（README 实测）；两行分开读（§21.5.3 第一条） |
| 2 | 目标性状缺失比例 / 变换方式 / BLUE 或 BLUP 及理由 | % / 文本 | | 变换与选择要给理由（§21.4.2 L109）；本数据无多环境重复时写明「不适用」 |
| 3.1 | 资产对账：`sativas413.fam` / `sativas413.bim` / `struct.fam` / `struct.bim` / `prune.prune.in` 行 | 行 | | 原始面板 **413** 与 **36,901**（README 实测）；质控后 `.fam ≤ 413`、`.bim` 在 36,901 量级或更少；剪枝行数**待测**（教材判 unverified） |
| 3.1 | `pca.eigenvec` IID 不在 `.fam` 里的条数 / `.fam` 里没有 PC 的个体数 | 条 | | 两个方向都**必须 0**（§21.5.6 第三条察觉动作） |
| 3.1 | `ld_decay.txt` 两行半衰是否都在 / 你用哪一行 / `n_individuals` | bp / 文本 / 个 | | `half_decay_bp` 与 `half_decay_baseline_adjusted_bp` 都在，`n_individuals` = 2×个体数；**数值待测**（unverified） |
| 3.3 | 质控后标记数 / 个体数 | 个 | | 取日志 L79 的「X 个标记 / Y 个个体」；**Y 不预设 413**（§21.5.3 第四条） |
| 3.3 | GEMMA `number of analyzed SNPs`（六套是否一致） | 个 | | 取 L121–122 抓出的那行；**这是方法学要报的数**，不是 `.bim` 行数（⑨ E6） |
| 3.3 | 各模型 `pve` / `se(pve)` | 无量纲 | | `pve=1` 或 `se(pve)=nan` 属边界预警（⑨ E10），处置写进报告 |
| 3.3 | 协变量行数 = `.fam` 行数？行序逐行相同？（五个 PC 档逐个） | 是/否 | | 行数由脚本断言（L105–107）；行序查 `covar_pc*.iid` 与 `.fam` 第 2 列逐行比对（改过的协变量那步会写这个文件），错位行数必须 0 |
| 3.4 | 六套 λ / `n_hits` / `min_p`（`model_summary.tsv`） | 无量纲 / 个 | | 数值**待测**；判据形态：若结构混杂是主因，GLM 的 λ 高于 MLM（§21.5.1），但这是诊断假设，两行都贴近 1 也算一种真实结果 |
| 3.4 | λ 四态判读（整体抬升 / 仅尾部 / 沉陷 / 无信号） | 定性 | | 档位 ≥1.20 / 1.00±0.05 / ≤0.90 / ≈1.00 是**经验口径**，须与 QQ 形态联读（§21.4.5 L236–245） |
| 3.4 | 选定的 PC 数 + 理由（λ、位点数、QQ、效应稳定性一起） | 个 / 文本 | | 「λ 接近 1 且信号未被抹平的最小 PC 数」是常用口径，不能单独定案（§21.4.5 L240–245、§21.5.2） |
| 3.4 | `lambda_1000`（传了 `N_IND` 才有） | 无量纲 | | 手算锚点 1.3333（n=150, λ=1.05）与 1.0429（n=3500, λ=1.15） |
| 3.4 | `n_eff` 取值 + 来源 + 是否与 simpleM 或置换交叉核对 | 个 / 文本 | | 起点估计只能写「起点估计」；**不许写「稳健上界」**（§21.4.4 L188） |
| 3.4 | 显著位点表的必备列与 p 值列名 | 列 / 文本 | | 必备列见作业 ⑥ #7；p 值列写 `p_wald`（脚本 L34 固定），换列就改说明 |
| 3.5 | 三条阈值 + 各自性质 + 分母来源 | 数值 / 文本 | | `0.05/36901 = 1.35×10⁻⁶`；(0.05/M)、(0.05/n_eff)、(1/n_eff) 三个数都要有（§21.4.4 L202） |
| 3.5 | suggestive 线的两个量：期望次数 / 至少一次的概率 | 个 / 概率 | | 1 / 0.6321（手算，§21.4.4） |
| 3.6 | clump 四参数 / `clump.clumped` 位点数 / `peaks.bed` 行数 | 参数 / 个 / 行 | | p1=1e-5、p2=1e-3、r²=0.2、500 kb；**空表要回 §3.4 看 QQ，不调阈值** |
| 3.6 | `HALF` 取值、来源、区间**实际宽度**（`end − start`）、是否钳位 | bp / 文本 | | 手算锚点 12,345,678 ± 150,000 → `chr 12195677 12495678`、300,001 bp；`HALF` 是单侧距离，钳位后宽度更短（`ps`=120,000 时为 270,000），照实写 |
| 3.6 | 区间内基因数（去重后）/ 四列证据各几条 | 个 | | 计数取 `candidate_genes_raw.tsv`；`strand` 列**不引用**（脚本取列缺陷，教材 §21.4.6 L302） |
| 3.6b | 先导 SNP 的 rs / chr / ps / 窗口内位点数 / 邻居 r² 是否随距离衰减 | 文本 / 个 | | 图注写「先导 SNP + 窗口半宽 + 颜色 = r²」；无超阈位点时本图缺项要写理由 |
| 3.7 | 匹配位点数 / 秩相关 / 峰区间是否一致 | 个 / 无量纲 / 定性 | | 判据是秩相关 + 峰区间一致，**不要求逐位相等**（§21.5.7）；数值**待测** |
| 3.8 | AI 五条核查逐条判定 / 重跑前后 λ 与位点数 | 是·否 / 数值 | | 五条见作业 ⑨；判定必须用 λ 与位点数两个指标（§21.4.5 L240） |

## 5. 失效条件对照（教材 §21.5，本实验里在哪一步、看什么能察觉）

1. **〔博〕群体结构未校正，全基因组假阳性**（§21.5.1）｜3.3 与 3.4。**察觉**：①先看 QQ，不看曼哈顿；②把不校正的 GLM 与校正后的 MLM 两张 QQ 并排——**若结构是主因**，会看到 λ 压回 1 附近而峰仍在；③调阈值无效，因为抬升是整体的。**峰消失不是「过度校正」的自动证据**：它有两种互斥解释——结构假阳性被清掉，或真信号与结构共线被一起吸收；区分靠三项正交检查（亚群内单独扫描峰还在不在、λ–PC 上 λ 是否一路下穿 1 且位点数同步归零、有没有共定位或单倍型等独立证据），教材 §21.7 第 8 题就考这一步。量级标尺：`ch21_structure_confounding_ols.py --selftest` 的 0.573 / 12.149（朴素）对 0.051 / 1.005（加 Q 后），OVB 斜率 0.4791 对理论 0.5000。**RDP1 上的实际 λ 待测**。
2. **〔博〕照搬转录组 FDR，且诊断顺序颠倒**（§21.5.2）｜3.4、3.5。**察觉**三处：①阈值属于哪一类、分母或零分布从哪来、有没有校准证据——报「位点数」而阈值来自未聚类的 SNP 层 BH 就已经错了；②审阅顺序里有没有 QQ、λ、**λ–PC 曲线**，只有曼哈顿图的报告不合格；③PC 数 0/2/4/6/10 下 λ 与位点数的走向是判断「校正」与「抹平」的主要线索，λ 一路降到 1 以下而位点数同步归零即过度校正；**但走向只是线索，定案要联读 QQ 形态、群体结构与效应稳定性**（3.4 检查点 3）。另有一条**经验红线**：单个 SNP 解释 >40% 表型方差在自然群体极罕见，优先怀疑表型录入或样本标签颠倒（不是判据）。量级标尺：`ch21_thresholds_fwer_fdr.py --selftest` 的 25 SNP→1 位点、置换成对阈值 3.79×10⁻⁶、三口径 FWER 0.009 / 0.205 / 0.050（后者是构造内结果）。
3. **〔硕〕样本 ID 按错列匹配，或表型文件带旧 Mac 回车**（§21.5.3）｜3.2 与 3.3。**察觉**四条对账：① `.fam` IID ∩ 表型第 2 列 = 413/413、∩ 第 1 列 = 0（两行要分开读）；② `wc -l` = 样本数，返回 0 说明整份文件只有一个「行」（`file` 报 `CR line terminators`，只查 CRLF 会漏）；③ 表型必须用 `--pheno` 显式挂上（`.ped` 末列是 `-9`）；④ 合并后不能用行数当验收，要用「合并键唯一的行数 + 抽查几个 IID」，且质控后行数按实际保留 IID 集报（`--mind` 会改变个体数）。入口：README p05 节实测；脚本 L58–65、L82–84。
4. **〔博〕峰内最近或最显著的基因不一定是因果基因**（§21.5.4）｜3.6。**察觉**四个检查：①峰形是连片还是孤峰，孤峰先查数据质量（查该位点 HWE p、缺失率、等位深度平衡比，必要时 IGV 看比对）；②区间**实际宽度**（`peaks.bed` 的 `end − start`）与 `HALF` 的来源是否写明、有没有被染色体起点钳位；③候选表有没有四列证据、是否**至少两列独立指向同一基因**；④有没有做共定位——只有「表达峰与表型峰在同一区间」这一条，不能写成共享因果变异。教材 §21.5.4 的写作口径是「四条里缺两条以上，结论只能写到『区间内候选基因包括……』这一级」，它属写作规范而非统计阈值。另：区间宽度是**全基因组平均量**，局部 LD 明显更长时应放宽并说明，但不得窄到只包住先导 SNP（否则区间退化成位点）。
5. **〔博〕在高自交群体上照搬 HWE 过滤**（§21.5.5）｜3.3 的 `HWE=0`。**察觉**：①质控前后位点数对账，塌掉先看繁育系统而不是先怀疑数据质量；②分群后重算——Wahlund 造成的偏离在亚群内部大幅减弱，自交造成的不会；③课程脚本 `HWE=0`，开启时打印警告并要求确认随机交配（L69–73），方法学里写「因自交/克隆繁殖，未做 HWE 过滤」及替代防线（缺失率、等位深度平衡比、重复区掩码）。量级标尺：`ch20_hwe_selfing_wahlund.py --selftest` 的 100%（s=0.95、F=0.9048）与 99.6%（三亚群合并）。
6. **〔博〕拿 p04 的真菌交付物跑水稻关联**（§21.5.6）｜3.1。**察觉**三条：① `.fam` 行数是否为 413、`.bim` 是否为 36,901 的量级（质控后更少）；②染色体名是否与注释同一套；③ `pca.eigenvec` 的 IID 是否能在 `.fam` 里逐个找到。三条任一不成立，就回 RDP1 重新生成资产。**最轻是维度不匹配、GEMMA 报错；更隐蔽的是个体数刚好凑上、染色体名又能过 `--allow-extra-chr`——程序不报错，但 K 与 PC 描述的是另一批个体**。实质是「同一条管线换数据必须重算中间产物」，而非文件路径问题。
7. **〔硕〕要求与黄金答案逐位点相等**（§21.5.7）｜3.7。**察觉**：先看整体秩相关与峰所在区间，两者都对得上就说明流程通了，再抽查峰顶位点的 p 值量级。秩相关很低时按 §3.7 的四条工程清单排查（ID 列、CR 行尾、`--pheno`、36 列里选错性状），**不是先去调 PC 数**。方法学写「秩相关与峰区间一致性比对」，不写「逐位点复现」。这条最容易被误读成「流程失败」，进而无休止调参。

## 6. 思考题（指向教材 §21.7 博士层，不给答案）

1. 你在 3.4 拿到了 GLM 与五档 MLM 的 λ 与位点数。用这两组读数说明「λ 接近 1」为什么**不能单独作为通过标准**，并给出你会同时并列报告的三个量；若某一档 λ 收敛而位点数归零，你的结论该怎么写？（§21.7 第 7 题（λ 标度律）＋第 8 题（加 PC 后峰消失的两难）→ §21.4.5、§21.5.2）
2. 3.5 的三个阈值里，哪一个你**敢用来指导后续基因编辑验证**，哪一个只配作线索？把「原理由」写成一句话并附上分母来源与校准证据；若审稿人问「为什么不用 5e-8」，你的回应是什么？（§21.7 第 6 题 → §21.4.4）
3. 你的表型若来自三地两年、缺失率 15%，写出从原始记录到关联输入的清洗路径，并说明 BLUE 与 BLUP 的取舍代价。**本数据有没有这一步？** 如果没有，报告该怎样诚实地交代，而不是假装做了多环境建模？（§21.7 第 5 题 → §21.4.2）
4. 3.6 的某个峰在曼哈顿图上是一个孤峰：该点极显著，侧翼数十个标记毫无起色。列出你**必须做的排查动作**，并说明「排查全部通过」时这句话该怎么写才不越界。（§21.7 第 9 题 → §21.4.5、§21.5.4）
5. 围绕你自己的课题写 350 字左右的 GWAS 方案：群体与样本量、表型与环境设计、协变量与 PC 策略、阈值推导路线、从峰到候选基因的区间标准与四类证据链。要求每条都能对应到本实验的某一步或某个读数。（§21.7 第 11 题 → §21.4.2 至 §21.4.6）

## 7. 提交物

- **对应作业**：`08_assessment/phd/assignments/p05_gwas_practice.md`（占课程总成绩 **4.5%**，是专题实践 27% 的一份），打包 `学号_姓名_p05.zip`（**≤ 200 MB**，按作业 ⑤；去掉 `.bed` 大文件，保留文本结果与图）。解压后：

  ```
  学号_姓名_p05/
  ├── report.pdf                      # 正文 ≤ 8 页；五节：表型与质控 / QQ 与 λ 诊断 /
  │                                   # 曼哈顿与显著位点 / 阈值与候选区间 / 方法选择与可信度（≤1 页）
  ├── scripts/
  │   ├── gwas_gemma.sh               # 你实际投递的那份（改过就标注改了哪几行）
  │   ├── gwas_diagnostics.R           # 同上
  │   └── postgwas_interval.sh         # 同上
  ├── results/
  │   ├── qc_thresholds.md            # 四个质控阈值 + 三条显著阈值的理由与性质
  │   ├── lambda_by_pc.tsv            # λ 与位点数随 PC 数（0/2/4/6/10）
  │   ├── assoc_mlm.tsv               # 主线 MLM 结果（写明用的是 p_wald 还是别的）
  │   ├── sig_loci.tsv                # 显著位点表，必备列见作业 ⑥ #7
  │   ├── clump.clumped
  │   └── candidate_genes.tsv         # 区间内基因 + 四列证据 + 优先级
  ├── figs/                           # 标题/轴/图例一律英文（集群 R 下中文渲染成方块）
  │   ├── fig1_qq_panel.png           # GLM 与各 PC 数的 QQ 拼图（**必须在曼哈顿图之前**）
  │   ├── fig2_lambda_vs_pc.png       # 双轴：λ 与检出位点数
  │   ├── fig3_manhattan.png          # 标出 genomewide 与 suggestive 两条线
  │   └── fig4_locus_zoom.png         # 至少一个峰的局部放大，展示邻居 p 随 r² 递减
  ├── ai_logs/prompt_and_reply.md     # ⑧ 的原文往返（第一轮不说模型/PC 数/样本量）
  ├── results/ai_audit.tsv            # ⑧ 的五条逐条判定
  └── env_snapshot.yml                # conda env export --no-builds
  ```

- **打包时的「改名对照表」**（作业要的文件名与脚本产出的文件名不是一套，这是历史口径差，不是你的错；但交上来必须用作业的名字）：

  ```bash
  cd "$P05/results"
  mkdir -p figs
  cp ../work/gwas/output/diagnostics/model_summary.tsv lambda_by_pc.tsv   # 六行：glm_raw + 5 档 MLM
  cp ../work/gwas/output/mlm_pc4.assoc.txt            assoc_mlm.tsv       # 换成你选定的那份
  cp ../work/postgwas/candidate_genes_table.tsv       candidate_genes.tsv
  cp ../work/postgwas/clump.clumped                   clump.clumped
  cp ../work/gwas/output/diagnostics/hits_mlm_pc4.tsv sig_loci.tsv        # 空表情形见下
  cp ../work/gwas/output/diagnostics/lambda_vs_npc.png figs/fig2_lambda_vs_pc.png
  cp ../work/gwas/output/diagnostics/manhattan_mlm_pc4.png figs/fig3_manhattan.png
  ls figs                                                                    # 对照作业 ② 的清单数一遍
  ```

  QQ 拼图要用六张 `qq_*.png` 合成一张 `figs/fig1_qq_panel.png`：有 ImageMagick 时 `montage ../work/gwas/output/diagnostics/qq_*.png -tile 3x2 -geometry +4+4 figs/fig1_qq_panel.png`；集群上没有 `montage` 就在 R 里 `png(); par(mfrow=c(3,2))` 逐张重画（`qqman::qq()` 可连续调用，顺序固定为 GLM→PC0→PC2→PC4→PC6→PC10）。

  两处要自己补：① **`sig_loci.tsv` 的 MAF 列**——`hits_*.tsv` 里只有 `af`，作业 ⑥ #7 要 MAF：在 `$P05/work` 里跑 `plink --bfile gwas --allow-extra-chr --freq --out gwas_freq`，再按 `SNP` ↔ `rs` 把 `gwas_freq.frq` 的 `MAF` 列并进去；② `fig3_manhattan.png` 的图注要写清两条线各自的口径（`0.05/n_eff` 与 `1/n_eff`）。`hits_*.tsv` 不存在（没有位点过 genomewide 线）时，`sig_loci.tsv` 交一张只含表头的空表并在报告里说明，**不要拿 suggestive 位点填进去**。

- **报告五节顺序即评分顺序，不得调换**：先 QQ/λ，后曼哈顿。报告里若先出现曼哈顿解读而没有 QQ 诊断，作业 ⑥ #1 的「完成度与结果正确性」直接按缺项计。
- **必须自己对齐的三处规格**：① `n_eff` 的来源写成「剪枝集行数（起点估计）」或「置换/ simpleM」，不许写「稳健上界」；② `HALF` 写清取自 `ld_decay.txt` 的哪一行、单位 bp、怎么算出来的；③ 显著位点表的 p 值类型要写 `p_wald`（若换列就改说明）。
- **评分口径**（作业 ④，满分 100）：完成度与结果正确性 **48**、方法选择与结果可信度说明 **30**、AI 使用与验证记录 **10**、报告质量 **12**。30 分那一项考四问：为什么用这个检验/模型、为什么用这个阈值、假阳性风险在哪（含**过度校正的假阴性风险**）、什么证据能推翻你的结论；**不看结论对不对，看推理链闭不闭合**。
- **截止与迟交**：p05 课后**第 10 天 23:59**；迟交 3 天内按 90%、超 3 天按 70%、超 7 天不计分（可在截止前申请一次不扣分延期）；允许截止前重复提交，以最后一次为准。
- **十二个失分点**逐条见作业 ⑥，其中与本指导步骤直接对应的六个：先看曼哈顿（#1）、表型三列格式（#2）、协变量缺截距（#3）、`--clump` 缺列名参数（#8）、`intersect` 空表（#9）、孤峰当发现（#10）。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材（概念、失效条件、习题、数字索引） | `textbook/chapters/ch21/manuscript.qmd`：§21.1（数据链缺口）、§21.3（环境与符号表）、§21.4.1（GWAS 在问什么）、§21.4.2（表型与功效闸门）、§21.4.3（Q/K、近邻污染、LOCO）、§21.4.4（阈值、`M_eff`、置换与交换性）、§21.4.5（QQ/λ/曼哈顿与四态档位）、§21.4.6（clump、区间、四类证据、共定位）、§21.4.7（边界与方向）、§21.5.1–§21.5.7、§21.6、§21.7（博士层 4–11 题）、§21.9（答案）、§21.10（数字索引与失效落点） |
| 本专题讲义 | `02_lectures/phd/topic05_gwas/05_gwas_lecture.md`：② 前置表与 30 秒自检、③ 3.1 应用案例、④ 4.1–4.6、⑤ 5.1–5.8（5.2 BLUE 片段、5.3 质控、5.4 Q/K、5.5 GLM/MLM+PC 扫描、5.7 诊断、5.8 区间）、⑥ 6.1（λ 四态）、6.2（异常排查）、⑦ 7.1–7.4（统计插件）、⑧ AI 任务、⑨ E1–E10、⑩ 8 题、⑪ 文献 |
| 质控 / Q / K / GLM / PC 扫描（只读；改参数走个人副本） | `03_code/phd/scripts/05_gwas_gemma.sh`：作业头 L2–7、设计要点 L18–27、变量注释 L29–37、激活 L40、工具守卫 L42–44、参数 L46–52、`cd` L53、表型体检 L58–65、HWE 警告 L69–73、质控 L75–79、fam 第 6 列断言 L82–84、K（剪枝集）L88–90（**L88 未带 `--mind`**，见 §3.3）、GLM 对照 L93、PC 循环与协变量生成 L96–107（**L101–103 按 eigenvec 行序输出**，见 §3.3 的替换写法）、MLM L108、`pve` 预警 L112–119、analysed SNPs L121–122、收尾提醒 L124–131 |
| LD 衰减（p04 的只读脚本，§3.1 第 ⑤ 步复用） | `03_code/phd/scripts/04_ld_decay_plot.R`：用法 L8（`<plink.ld> <max_kb> <bin_bp> <out_prefix> [n_ind]`）、读入与裁剪 L32–40、分箱 L42–50、Hill–Weir 与指数回退 L52–66、读数 L67–76（写 `half_decay_bp`、`half_decay_baseline_adjusted_bp`、`dist_at_r2_0.2_bp`）、输出 L78–96 |
| 诊断（QQ/λ/λ–PC/曼哈顿/显著表） | `05_gwas_diagnostics.R`：用法 L7–9、`P_COL` L34、λ 函数 L36–39、assoc 空则 stop L41–44、`N_IND` 与 λ₁₀₀₀ L57–58、两条阈值线 L64–65、`CHR_num` L66、QQ L60–62、曼哈顿 L70–74、`hits_*.tsv` L76–83、`model_summary.tsv` L84–94、λ–PC 双轴 L97–115、判读提示 L117–121 |
| 后 GWAS（clump/区间/基因/证据表） | `05_postgwas_interval.sh`：作业头 L2–7、设计要点 L18–25、变量注释 L27–33、激活 L37、工具守卫 L39–41、参数 L43–48、染色体名交集 L51–59、clump L62–65、空结果 WARN+exit 0 L66–73、位点数 L74–75、`peaks.bed` 钳位与 0-based L78–82、`genes.bed`（`$3=="gene"`）L85–86、`intersect` L87–88、空表提示 L89–92、候选表骨架 L95–103、四类证据说明 L105–116 |
| SGE 提交 | 两个 `.sh` 各自带作业头（gemma L2–7、interval L2–7），**禁止登录节点直接 `bash`**（gemma L14、interval L14） |
| 合成自查演示 | `textbook/demos/ch21_structure_confounding_ols.py`、`ch21_lambda_gc_scaling.py`、`ch21_thresholds_fwer_fdr.py`、`ch20_hwe_selfing_wahlund.py`（均带 `--selftest`；在课程仓库根目录运行 `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/<名>.py --selftest`） |
| 数据说明与下载 | `06_data/phd/README.md` p05 节（413 / 36,901 / 36 列 / 8.5 MB / 23 MB、三个必踩的坑、自查判据）；`06_data/phd/download_phd.sh` 的 `fetch_p05`（L159–176：四个文件 + `tr '\r' '\n'` + 可选 p 值矩阵 + `unzip`，**不含 GFF3**）；`06_data/accessions.tsv`（**无 RDP1 条目**）；`06_data/reference/README.md` 第 24 行（p05 参考备料的口径，§3.6 的注释缺口以它为准） |
| 环境定义 | `07_envs/conda/env_phd_popgen.yml`（`ngs_phd_popgen`，与 p04 共用；pin 见 §1，L31–33 含 `r-lme4` 与 `r-dplyr=1.1.4`） |
| 作业规格 | `08_assessment/phd/assignments/p05_gwas_practice.md`（① 背景 ② 交付物 ③ 完成步骤 ④ 评分（48/30/10/12）⑤ 提交 ⑥ 12 个失分点，⑨ AI 五条核查） |
| 上游资产（RDP1 需重算） | p04 实验指导 `../11_lab_guides/phd/04_popgen_lab.md` 的 §3.7（LD 衰减与两行半衰）与 §7（`deliverables_for_p05/` 七项）；p04 讲义 ⑥ 6.2 是交付清单（头注写的「⑥ 6.3」不存在） |
| 下游衔接 | p06 多组学（GWAS 峰与 eQTL 共定位）、p08 课题设计（开题里的阈值与区间论证复用本指导 §3.5、§3.6） |
