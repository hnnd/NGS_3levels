---
title: "实验指导 m06：扩增子测序与微生物群落多样性"
level: master
topic: m06
textbook: [ch18]
lecture: ../02_lectures/master/topic06_amplicon/06_amplicon_lecture.md
env: ngs_ms_microbiome
---

# 实验指导 m06：扩增子测序与微生物群落多样性

> 上机时手边打开的这份文件。每一步回答四件事：这条命令在做什么、敲什么、看到什么算对、看到什么说明错了。
> 原理与判据在教材第 18 章（§18.4 概念、§18.5 失效条件），统计背景（置换检验、多重检验）在第 12 章，
> 设计与批次在第 13 章；本指导只放操作与自查入口。检查点数字都带来源：课程自查线是数据 README 为练习
> 设定的参考线（非实测、非通用阈值），手算例给出输入与运算步骤、可计算器复核，合成算例是 demos 固定种子
> 演示（只对各自生成模型成立）。真实数据（PRJDB13364）的全流程本课未在课程集群复跑，标「集群未实测」的
> 步骤按预期对待，真实结果以你自己的运行日志为入口；教材 §18.6 的结果数字全部是设例，不得抄进报告。

## 0. 本实验对应什么

- **教材**：第 18 章 扩增子测序与微生物群落多样性。本实验覆盖硕士层学习目标 LO18-03（区段选择与重叠算式）、LO18-04（DADA2 六步
  与 track 表判读）、LO18-05（α/β 多样性与 PERMANOVA＋betadisper）、LO18-06（抽平决策说明）。
- **学时**：m06 共 4 学时（契约），本实验是实践环节；配套作业建议上机 4–6 小时（作业规格，`learnErrors` 与去噪最耗时）。
- **环境**：conda 环境 `ngs_ms_microbiome`（`07_envs/conda/env_master_microbiome.yml`）。dada2、phyloseq、vegan 在该 yml 里
  **未钉版本**——实装版本由步骤 2 的作业日志打印并写进报告，不要预写版本号（教材 18.3）。DECIPHER 与 phangorn 不在环境里，
  UniFrac 不是已装能力（教材 18.4.7）。QIIME2 **不在本环境**：它绑定了数十个强绑定、版本锁死的 Python 底层依赖，与本环境的 R
  4.3.1/Bioconductor 体系互相冲突，混装轻则 conda 求解失败、重则毁坏现有环境，官方因此要求独立安装（讲义 ②）——**不要**试图把
  QIIME2 装进本环境重建。
- **作业**：`08_assessment/master/assignments/m06_amplicon_assignment.md`，占课程总成绩 5%；「方法选择与结果可信度说明」占作业
  30%。
- **计算纪律**：一切计算（质量图、DADA2、统计、绘图，含看似很小的计算）一律 `qsub`——登录节点只做下载、建环境、编辑、看日志与
  `command -v` 这类秒级路径核对。登录节点有单用户 CPU/内存配额，DADA2 这类内存敏感计算可能因超配额被杀（不保证必现，但会白跑）
  并拖慢大家共用的登录节点（教材 18.3 与集群事实）；计算节点不通外网，联网步骤只能在登录节点做。

## 1. 实验前检查

- **前置模块**（先确认自测能过，讲义 ②）：`l0_01_linux`（qsub、`Eqw` 排查）、`l0_02_r`（读表、ggplot2 出图）、`l0_05_qc`（质量
  图定截断）、`l0_06_stats`（置换检验最小可能 p 值，第 2 题 3v3）、`l0_03_conda`（QIIME2 为什么必须独立建环境）。
- **环境路径核对**（登录节点，秒级、不加载任何包）：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_microbiome
  command -v Rscript; command -v seqkit; conda env list | grep ngs_ms_microbiome
  ```

  这条命令在做什么：作业不继承交互 shell 的环境，每个作业脚本开头都要自己激活环境；这里只确认 Rscript、seqkit
  在 PATH 里、环境确实存在。**版本核验一律进 qsub**：§3 步骤 2 的预检脚本 `m06_qual.R` 开头就打印
  `R.version.string` 与四个包的 `packageVersion()`，作业日志（`m06_qual.o<作业号>`）即版本记录，与正式流程同一
  环境同一口径。版本以 `env_master_microbiome.yml` 为准：R 4.3.1 与 ggplot2 3.4.2 按 yml 核验；dada2/phyloseq/vegan
  **未 pin**，照日志实读数字写进报告方法节。
- **预期**：`command -v` 各打印一条路径；`conda env list` 里有 `ngs_ms_microbiome`；步骤 2 作业日志里有 R 版本与三个未 pin 包
  的实装版本。
- **出错信号**：`command not found` / 包加载失败 → 作业内环境未激活或环境损坏（讲义 ② 的 30 秒自检同口径）；**不要**试图把
  QIIME2 装进本环境重建（机制见 §0）。

## 2. 实验数据

贯穿数据是 `PRJDB13364`（布基纳法索铁毒稻田根际土细菌 16S，V4 区 515F/806R，双端 250 bp）。二十个样本按铁毒
（Fe）与非铁毒（nonFe）分组，**主线是 Fe vs nonFe，不是发病/健康**（教材 18.1）。登录号全部已登记
`06_data/accessions.tsv`（L77 项目号，L78–L97 共 20 个 run），与 `06_data/master/README.md` m06 节一致：

| 年份 | Fe 组 | nonFe 组 |
|---|---|---|
| 2017（2 对 2） | `DRR357521` `DRR357522` | `DRR357523` `DRR357524` |
| 2018（4 对 4） | `DRR357529`–`DRR357532` | `DRR357533`–`DRR357536` |
| 2019（4 对 4） | `DRR357545`–`DRR357548` | `DRR357549`–`DRR357552` |

- **规模**：20 个样本合计 242 MB（README m06 节）；每样本原始读段约 3 万–4 万条，ENA 实查 34 281–42 256 条、中位 37 031 条、合
  计 744 081 条（教材 18.6 记录，课程环境未复跑，unverified）——只用于判断量级，**不能**当抽平深度的依据（去噪去嵌合会先砍掉一
  截，18.4.9）。
- **下载**（登录节点，在课程仓库根目录运行）：

  ```bash
  cd <课程仓库路径>
  bash 06_data/master/download_master.sh --topic m06 --run --outdir /d3/scratch/${USER}/ngs/data
  ```

  产物落在 `/d3/scratch/${USER}/ngs/data/m06/`：每 run 一对 `_1.fastq.gz` / `_2.fastq.gz`（ENA 命名）加
  `SHA256_MANIFEST.tsv`。下载时脚本已按 ENA 公布的 md5 逐文件校验；看到校验告警先重下该 run，不要带残缺文件
  往下跑。若用 `--runs` 分片补下过文件，再跑一次整批下载以重写清单（分片模式不重写清单）。
- **注释训练集**：`assignTaxonomy` 用的 DADA2 格式 SILVA 训练集，**必须与 V4 区段匹配**（教材 18.4.5）；推荐 SILVA v138.2 的
  **toGenus** 训练集（DADA2 官方维护版，Zenodo 记录 14169026，2024-11-15 发布，文件清单与大小以记录页为准）。下载只在登录节点
  做：

  ```bash
  wget -c -O /d3/scratch/${USER}/ngs/m06/db/silva_nr99_v138.2_toGenus_trainset.fa.gz \
    "https://zenodo.org/records/14169026/files/silva_nr99_v138.2_toGenus_trainset.fa.gz?download=1"
  ```

  直链失败就打开该记录页（或 DADA2 官方 training 页面）手动下载同名文件，**不要**改下 assignSpecies/toSpecies
  文件；文件名以下载实名为准，`DB=` 填完整路径，训练集文件名与版本写进报告方法节。
- **工作目录**：分析根目录 `/d3/scratch/${USER}/ngs/m06/`。**先建子目录**——R 脚本向 `results/` 写文件，目录不存在会直接报错退
  出：

  ```bash
  mkdir -p /d3/scratch/${USER}/ngs/m06/{db,results,logs}
  ```

  原始数据放在下载目录直读；`metadata.tsv` 建在 **`FQDIR` 里面**（脚本按 `file.path(fqdir, "metadata.tsv")`
  读取，R L41–42）。数据不要放家目录。

## 3. 实验步骤

> 每步固定五栏：目的 / 命令 / 产出文件 / 检查点 / 出错信号。命令调用 `03_code/master/scripts/` 现有脚本，不复制
> 脚本全文；脚本名、参数名、输出文件名已逐个与现版源码核对。**在哪敲命令**：登录节点只做下载、编辑、看日志与
> `command -v` 秒级路径核对；其余一律 `qsub`（步骤 2/7/8/9 的个人扩展也是 qsub）。需要改脚本时按「cp 个人副本 →
> 改指定行 → grep 确认 → qsub 副本」走，不得「投递后再补参数」。作业日志（`dada2.o<作业号>`）写在投递时所在
> 目录（脚本头 `#$ -cwd`），产出写在 `OUTDIR`，两者不是一回事。

### 步骤 0：数据获取与配对核对

- **目的**：拿到 20 个已登记 run 的双端 FASTQ，并确认左右两端 basename 一一成对。
- **命令**（登录节点；下载命令见 §2，下载完成后做配对核对）：

  ```bash
  cd /d3/scratch/${USER}/ngs/data/m06
  ls DRR3575*_1.fastq.gz | wc -l            # 期望 20（F 端条数）
  comm -12 <(ls DRR3575*_1.fastq.gz | sed 's/_1\.fastq\.gz//' | sort) \
           <(ls DRR3575*_2.fastq.gz | sed 's/_2\.fastq\.gz//' | sort) | wc -l   # 期望 20（成对 basename 数）
  cat SHA256_MANIFEST.tsv | wc -l           # 期望 40（20 run × 双端 2 个 .gz，逐文件一条记录）
  ```

  这条命令在做什么：主流程脚本只按 `_1`/`_2` 模式数文件条数、**不逐一核对 basename 对应**（现脚本只比条数，
  R L32–33）——左右数量相等而内容错配不会触发任何检查（教材 §18.5.6）。所以下载后先逐 run 比较 `_1`/`_2`
  的 basename 集合，不能只比条数。清单是课程侧对目录下全部 `.gz` 逐一计算的 SHA256（下载脚本 L176–177，只保留
  前 12 位哈希），**40 行才正常**——20 个 run、每个 run 两个端文件；它与下载时脚本按 ENA 公布的 md5 做的逐文件
  校验是两道工序，前 12 位截短值不能代替 md5 校验通过。
- **产出文件**：20 对 FASTQ、`SHA256_MANIFEST.tsv`；随后自建 `metadata.tsv`（步骤 1）。
- **检查点**：两个 `wc -l` 都等于 20；清单 40 行（20 对双端共 40 个 fastq.gz，每文件一条 `sha256sum` 记录）；单文件体量与「合
  计 242 MB」量级相符（README m06 节）。
- **出错信号**：缺文件、md5 校验失败、basename 不成对 → 停止，先修下载；不得进入 DADA2（教材 §18.5.6 的流程最前端配对错位）。

### 步骤 1：环境与元数据预检

- **目的**：环境可用，分组（`group`）与真实测序批次（`batch`）明确——这两列是主流程的强制输入，不是可选项。
- **命令**（登录节点；**逐 run** 抽 FASTQ 头确认实际测序批次，然后生成 metadata）：

  ```bash
  cd /d3/scratch/${USER}/ngs/data/m06
  for f in DRR3575*_1.fastq.gz; do printf '%s\t' "${f%%_1.fastq.gz}"; zcat "${f}" | head -1; done \
    | tee /d3/scratch/${USER}/ngs/m06/logs/fastq_headers.tsv
  ```

  这条命令在做什么：**每个 run 都要看头部**，不能只抽「每年一个」——同一年可能跨多个测序 run，抽样推不出全部
  20 个 run 的批次。FASTQ 头两种常见形状：`@<instrument>:<run>:...`（Illumina 标准头，前两段就是仪器号与 run 号）
  或 `@DRR357521.1 1 length=250` 这类提交格式头（instrument/run 信息已被抹掉）。归批规则：**同一 instrument:run
  同批**；头部不含 instrument/run（或明显被重写）的 run，先查 ENA 该 run 的元数据（run 号、flowcell、平台字段），
  仍无归属就记 `unknown` 并在报告披露——教材 18.4.4：flowcell/run 的归属在 ENA 字段里查不到时只能按 FASTQ 头
  核实，不要把 `unknown` 编成某年。

  `metadata.tsv`（制表符分隔，放在 FQDIR 内）一键生成模板——20 个样本名、分组与年份已按登记信息填好，`batch`
  列按你核到的 FASTQ 头填写：

  ```bash
  cat > /d3/scratch/${USER}/ngs/data/m06/metadata.tsv <<'EOF'
  sample	group	batch	year
  DRR357521	Fe	<按FASTQ头>	2017
  DRR357522	Fe	<按FASTQ头>	2017
  DRR357523	nonFe	<按FASTQ头>	2017
  DRR357524	nonFe	<按FASTQ头>	2017
  DRR357529	Fe	<按FASTQ头>	2018
  DRR357530	Fe	<按FASTQ头>	2018
  DRR357531	Fe	<按FASTQ头>	2018
  DRR357532	Fe	<按FASTQ头>	2018
  DRR357533	nonFe	<按FASTQ头>	2018
  DRR357534	nonFe	<按FASTQ头>	2018
  DRR357535	nonFe	<按FASTQ头>	2018
  DRR357536	nonFe	<按FASTQ头>	2018
  DRR357545	Fe	<按FASTQ头>	2019
  DRR357546	Fe	<按FASTQ头>	2019
  DRR357547	Fe	<按FASTQ头>	2019
  DRR357548	Fe	<按FASTQ头>	2019
  DRR357549	nonFe	<按FASTQ头>	2019
  DRR357550	nonFe	<按FASTQ头>	2019
  DRR357551	nonFe	<按FASTQ头>	2019
  DRR357552	nonFe	<按FASTQ头>	2019
  EOF
  column -t -s$'\t' /d3/scratch/${USER}/ngs/data/m06/metadata.tsv | head -5   # 预览格式
  ```

  另注意 2019 年 Fe 组的 `library_name` 前缀是 `BERS`、其余是 `BFRS`（教材 18.4.4），核实前不要把它当分组信息
  用。最低要求：`group` 列（只写 Fe / nonFe）＋ `batch` 列（覆盖全部 20 个样本；核不出的写 `unknown` 并披露，
  不要把采样年份冒充批次）；`year` 列（2017/2018/2019）供步骤 8 扩展模型用。脚本默认按 `BATCH_COL=batch`
  读批次列（`06_run_dada2.sh` L25 → `06_dada2_pipeline.R` L26）。
- **产出文件**：`metadata.tsv`；版本记录（步骤 2 作业日志里的 packageVersion 输出）、`logs/fastq_headers.tsv` （批次判定依
  据）。
- **检查点**：20 个 FASTQ 样本名全部被 metadata 行名覆盖（行名＝run 登录号，与 `_1.fastq.gz` 的 basename 严格一致）；`group`
  非空且只用 Fe/nonFe 两值；`batch` 列无缺失（`unknown` 也是一种值，但必须在报告说明）。年份内 2+2/4+4/4+4 的交叉结构是样本表
  设计（教材 18.1/18.6），不是检验结果，核对时不要把「平衡」写成「已证明可分离」。
- **出错信号**：缺 `batch` 列 → 脚本警告并把全部样本当同一 run 学错误模型，这行警告要当错误处理（R L48–52；教材
  §18.5.2）；metadata 缺某样本 → 脚本在读取批次列时停止（R L44–45，报「metadata.tsv 缺少样本」）。**缺 `group` 列不会被跳过**
  ——脚本只在文件不存在时跳过多样性统计（R L118、L148–150）；文件在而缺 `group`，会在 `plot_richness(..., x = "group")` 等处失
  败（L123）。所以 `group` 是本步骤的强制预检项，缺了先补（教材 §18.4.4）。

### 步骤 2：质量图、引物状态与截断参数（qsub 个人预检）

- **目的**：先定 `truncLen`/`trimLeft` 再投主流程，禁止裸用默认值。现版课程脚本**没有** `plotQualityProfile` 步骤、不产出质量
  图（讲义 ⑤5.1 是扩展示例，不是现成脚本能力）——本步骤在个人预检脚本里补做，产物同时是作业 fig1 的原料。
- **命令**（个人扩展；在 scratch 下新建 `m06_qual.R` 与最小作业，改完 grep 核对再投）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m06
  cat > m06_qual.R <<'EOF'
  library(dada2); library(ggplot2)
  cat(R.version.string, "\n")                                   # 版本记录进作业日志
  for (p in c("dada2","phyloseq","vegan","ggplot2"))
    if (requireNamespace(p, quietly = TRUE)) cat(p, as.character(packageVersion(p)), "|")
  cat("\n")
  fqdir <- "/d3/scratch/USER/ngs/data/m06"          # 改成你的 ${USER}
  fnF <- sort(list.files(fqdir, pattern = "_1\\.fastq(\\.gz)?$", full.names = TRUE))
  fnR <- sort(list.files(fqdir, pattern = "_2\\.fastq(\\.gz)?$", full.names = TRUE))
  stopifnot(length(fnF) == length(fnR), length(fnF) > 0)
  ggsave("results/qual_F.png", plotQualityProfile(fnF[1:4]), width = 8, height = 6, dpi = 150)
  ggsave("results/qual_R.png", plotQualityProfile(fnR[1:4]), width = 8, height = 6, dpi = 150)
  EOF
  sed -i "s|/d3/scratch/USER/|/d3/scratch/${USER}/|" m06_qual.R
  grep -n 'list.files\|plotQualityProfile\|scratch' m06_qual.R     # 模式与路径核对
  cat > m06_qual.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m06_qual
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_microbiome
  cd /d3/scratch/USER/ngs/m06
  Rscript m06_qual.R
  EOF
  sed -i "s|/d3/scratch/USER/|/d3/scratch/${USER}/|" m06_qual.job
  qsub m06_qual.job
  ```

  这条命令在做什么：文件模式 `_1`/`_2` 与主流程脚本现版（`06_dada2_pipeline.R` L30–31）一致——讲义 ⑤5.1 示例的
  `_R1`/`_R2` 在本数据上会配到 0 个文件，不要照抄。第一行打印 R 版本、随后打印四个包的实装版本，都留在作业日志里
  （§1 要求的版本记录即来自这里）。质量图绿线是均值、**橙色实线才是中位数**；教材 18.4.1 的演示策略是以橙线跌破
  Q30 的位置为候选截断点，但 Q30 只是候选参考、不是充分判据：最终值要同时满足 `maxEE` 不过度杀人（过滤保留率
  合理）与重叠减法 ≥12。R2 通常比 R1 差、截断位点更靠前，差多少看你自己的图（教材 18.4.1）。作业 fig1 要求 R1
  与 R2 并标出 `truncLen` 取值位置：定参后用
  `plotQualityProfile(fnF[1:4]) + geom_vline(xintercept = c(<TRUNC_F>), linetype = 2)` 加竖线重存一版（图题/轴一律英文）。
- **引物状态**用数据本身确认（教材 18.4.3）：取一条读段的前 25 bp 与 515F 比对——

  ```bash
  zcat /d3/scratch/${USER}/ngs/data/m06/DRR357521_1.fastq.gz | sed -n '2p' | cut -c 1-25
  ```

  515F 为 Apprill 2015 修订版（教材 18.4.1 所引）：`GTGCCAGCMGCCGCGGTAA`（19 bp；`M` 是简并碱基 A/C）。若多数
  读段前 15–19 bp 与该序列一致（允许简并位差异），说明下机数据**带引物**；若完全对不上，说明建库/下机流程已去
  引物。本数据 V4 515F/806R：带引物写 `TRIM_F=19 TRIM_R=20`，已去引物写 0。多抽几条、两个端都看看再下结论。
- **参数决策（减法）**：过滤后重叠 `O = (F − l_F) + (R − l_R) − L_ins`，其中 `F/R` 是 `truncLen` 坐标（第 1 位仍是引物碱基），
  `l_F/l_R` 是 `trimLeft`，V4 扣引物后插入片段 `L_ins = 253` bp（教材 18.4.1/18.3）。合并要求 `O ≥ 12`（DADA2 `minOverlap` 默
  认）；留到 20 bp 量级是本课的练习余量，不是文献阈值。手算例（教材 18.4.1，可复核）：V4 带引物 `truncLen=c(240,200)`、
  `trimLeft=c(19,20)` → `(240−19)+(200−20)−253 = 148`；已去引物 `trimLeft=c(0,0)` → `240+200−253 = 187`。合成量级演示（课程仓
  库根目录运行，rc=0）：`PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch18_overlap_trunclen.py --selftest`——V4 正常配置合
  并保留 99.0%，过度截尾只剩 5.78%（合成算例）。
- **产出文件**：`results/qual_F.png`、`results/qual_R.png`（定参后加竖线版作 fig1）；参数决策记录（
  `TRUNC_F/TRUNC_R/TRIM_F/TRIM_R` 一组值＋依据，写进报告第 1 节）。
- **检查点**：质量图四线齐全；截断点与质量曲线自洽（橙线跌破 Q30 处是候选点），且减法结果 ≥12、余量口径写明、过滤保留合理（不
  看单一 Q30 线定参）。注意 `TRUNC_F/TRUNC_R` 默认值 240/200 只是占位——`06_run_dada2.sh` L29–32 会打印「truncLen 必须由本批数
  据的质量曲线决定」的提醒。
- **出错信号**：`truncLen ≤ trimLeft` → R 侧启动即停（R L27「truncLen 必须大于 trimLeft」）；照抄超读长的 `truncLen`（PE250 数
  据抄 280）→ 过滤后全 0，走进教材 §18.5.5 的现场；质量图文件名/路径与作业日志对不上 → 先查 `#$ -cwd` 的日志位置。

### 步骤 3：提交 DADA2 主流程（qsub -v 传齐变量）

- **目的**：按批次完成过滤、错误模型学习、去噪、合并、去嵌合、注释及默认多样性输出。
- **命令**（先设变量再投递；值必须来自步骤 2 的决定）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m06
  FQDIR=/d3/scratch/${USER}/ngs/data/m06
  OUTDIR=/d3/scratch/${USER}/ngs/m06/amplicon
  DB=/d3/scratch/${USER}/ngs/m06/db/silva_nr99_v138.2_toGenus_trainset.fa.gz   # 以下载实名为准
  TRUNC_F=<步骤2 的 F 端截断值>   TRUNC_R=<步骤2 的 R 端截断值>
  TRIM_F=<步骤2 的引物状态：带引物 19，已去引物 0>   TRIM_R=<20 或 0>
  qsub -v FQDIR="${FQDIR}",OUTDIR="${OUTDIR}",TRUNC_F="${TRUNC_F}",TRUNC_R="${TRUNC_R}",TRIM_F="${TRIM_F}",TRIM_R="${TRIM_R}",DB="${DB}",BATCH_COL=batch,MINBOOT=80 <课程仓库路径>/03_code/master/scripts/06_run_dada2.sh
  qstat -u ${USER}        # qw 排队 / r 运行 / Eqw 报错
  ```

  注意：`qsub -v` 的变量列表用逗号分隔、**绝对不能含空格或换行**——上面这条必须保持单行复制粘贴；若终端里总被
  折断，改用 `export FQDIR OUTDIR TRUNC_F TRUNC_R TRIM_F TRIM_R DB BATCH_COL MINBOOT`（逐个赋值后）再
  `qsub -V <脚本>` 继承环境。

  这条命令在做什么：`06_run_dada2.sh` 是 SGE 封装（`#$ -pe smp 8`，L6），R 侧线程取 `NSLOTS` 默认 8（L22），
  激活 `ngs_ms_microbiome` 后调同目录 `06_dada2_pipeline.R`（L34–35）。逐项参数口径（已对现版源码核对）：
  `FQDIR`（必填，L17）、`OUTDIR`（默认 `./amplicon`，L18）、`TRUNC_F/TRUNC_R`（默认 240/200 仅占位，L19–20）、
  `DB`（必填，L21）、`TRIM_F/TRIM_R`（引物长度，默认 0，L23–24）、`BATCH_COL`（默认 `batch`，L25）、`MINBOOT`
  （默认 80，L26）。R 侧固定参数：`maxEE=c(2,2)`、`truncQ=2`、`maxN=0`、`rm.phix=TRUE`（L55–57，**没有对应
  环境变量**）；`pool="pseudo"`（L79–80）；按 `BATCH_COL` 分批 `learnErrors`→`dada`→`mergePairs` 各建序列表再
  `mergeSequenceTables`（L73–90）；合并用 DADA2 默认 `minOverlap=12/maxMismatch=0`（教材 18.4.3）。要放宽
  `maxEE`（如 R2 差时 `c(2,5)`）只能改个人 R 副本并记录，不能伪称有环境变量。
- **产出文件**（在 `OUTDIR`）：`filter_stats.csv`（L58）、按批次的 `error_model_F_<batch>.png`（L77–78）、`track.csv`（完整形
  态：样本、batch、input、filtered、denoisedF、denoisedR、merged、merged_frac、nonchim；L94–110）、`seqtab_nochim.rds`
  （L111）、`taxonomy.csv`（L114–115）；metadata 合格时另有 `alpha_diversity.png`、`beta_stats.txt`、`pcoa.png`（L126–147）。
- **检查点**：先查日志再查产物，不以 `rc=0` 代替产物检查；上列文件逐个存在且非空（`ls -lh ${OUTDIR}`）。
- **出错信号**：`qstat` 恒 `Eqw` → `qstat -j <ID> | grep -A5 error`（资源/路径，`l0_01_linux` 口径）；环境未激活进作业 →
  `command not found`；`FQDIR`/`DB` 未传 → 脚本启动即停（L17/L21「必须指定」）；双端配不上 → R L32–33「双端文件配不上」；批次
  缺样本 → R L44–45「metadata.tsv 缺少样本」。过滤全 0 / 合并 0 / merged 塌 → 按教材 §18.5.5、§18.5.1 分流（步骤 4）。

### 步骤 4：track 表与错误模型诊断（先看表，再看任何图）

- **目的**：`track.csv` 是本章第一诊断依据（教材 18.4.3）：先按样本记录每步剩余读段，再逐批看错误模型图，最后才看多样性图。
- **命令**：

  ```bash
  column -t -s, /d3/scratch/${USER}/ngs/m06/amplicon/track.csv | less
  ls /d3/scratch/${USER}/ngs/m06/amplicon/error_model_F_*.png
  ```

- **产出文件**：读表无新产物；诊断记录写进 §4 结果记录表。
- **检查点**：
  1. 按样本抄录 `input/filtered/denoisedF/denoisedR/merged/merged_frac/nonchim`，比较同批样本间的一致性：同批次
     同参数，各步保留率应彼此接近；某一步只在部分样本断崖下跌比整体偏低更值得追（教材 18.4.3）。
  2. 课程自查线（README m06 节，**非实测、非通用阈值**）：过滤保留 `filtered/input > 70%`、合并保留 `merged/filtered > 60%`、
     去嵌合保留 `nonchim/merged > 55%`，三个数的分母依次是 input/filtered/merged。脚本对 `merged_frac < 0.5` 的样本发警告（R
     L99–101）是软件行为，不是生物学合格线。旧口径的 70–90%、≥70%、≥60%（土壤 50%）、总保留 50–80% 与 <40%/<30% 硬线已被教材撤
     下，**不要**写进判据（教材 18.4.3）。
  3. 错误模型图（`error_model_F_<batch>.png`）：灰点（观测错误率）随 Q 升高下降、黑线（拟合）贴灰点、红线（名义 Q 期望）趋势一
     致为正常（教材 18.4.3）。逐批都过一遍；量级直觉用合成演示（课程仓库根目录，rc=0）：
     `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch18_error_model_mixrun.py --selftest`——混学对脏 run 低估 0.60–0.65、对
     干净 run 高估 2.39–2.57，错误变异误判 0 → 24 113 个（合成算例，证明的是「双向失真」机制）。
- **出错信号**：`merged` 单列塌（`merged_frac` 低）→ 重叠不足，回步骤 2 做减法（教材 §18.5.1）；`filtered` 为 0 或 `NA`、track
  只剩精简列 → `truncLen` 超读长（§18.5.5 的三种现场：部分样本为 0 下游 NA／全部为 0 精简表后停／合并总数为 0 完整 track 后
  停）；缺批次列警告或某批曲线异常 → 混学（§18.5.2）。不要把旧百分比硬线当判据。

### 步骤 5：分类注释检查

- **目的**：确认 `taxonomy.csv` 的注释质量配得上后续结论——短读长 V4 的可靠分辨率常止于属，种名不是物种鉴定（教材 18.4.5）。
- **命令**（读表无新计算；用 R 或文本工具统计 NA 比例与最低阶元）：

  ```bash
  head -3 /d3/scratch/${USER}/ngs/m06/amplicon/taxonomy.csv
  ```

- **产出文件**：`taxonomy.csv`（ASV × 各阶元）；注释检查记录。
- **检查点**：报告四件事并写进方法节——训练集文件名（与 `DB` 一致）、区段（V4）、`minBoot`（本次 80，R L25/L114）、`NA` 比例与
  最低注释阶元。定性判据：以属水平为主属正常；「大片 `NA` 或只到门」是定性警报（不存在「NA 超过某百分比即不合格」的通用线，教
  材 §18.5.3）。出现种名时同时给置信度与区段信息，给不出就降级为属。
- **出错信号**：大片 `NA`／只到门按概率排三病因依次核对——① 训练集与区段不匹配（查 `DB` 是否 V4 区段训练集）；② 引物残留（查
  `TRIM_F/TRIM_R` 是否与数据引物状态一致）；③ 序列方向反（`tryRC=TRUE`，**不是现脚本的显式参数**——要用须改个人 R 副本并记录）
  （教材 §18.5.3）。

### 步骤 6：默认 α/β 产物与统计核对

- **目的**：核对脚本默认多样性产物，并把统计口径记全（现脚本行为：α 用**未抽平原始计数**的
  `plot_richness(ps, x="group", measures=c("Observed","Shannon"))`（L123–126），β 用**相对丰度表**的 Bray–Curtis
  （L130–131），`adonis2(..., 999)` ＋ `permutest(betadisper(...), 999)`（L133–137）——**不抽平**，教材 18.4.9）。
- **命令**：

  ```bash
  cat /d3/scratch/${USER}/ngs/m06/amplicon/beta_stats.txt
  ```

- **产出文件**：`alpha_diversity.png`、`beta_stats.txt`、`pcoa.png`。
- **检查点**：
  1. `beta_stats.txt` 两段齐全：PERMANOVA 的 R² 与 p、betadisper 的置换检验结果；记录距离（Bray–Curtis）、R²、p、
     置换数（999）、`packageVersion("vegan")`。任何 PERMANOVA 必须附 betadisper，缺一即不完整（教材 18.4.8）。
  2. 行序对齐显式检查（教材 §18.5.6；在步骤 8 的 R 会话里执行并留存）：`all(rownames(meta) == rownames(as.matrix(d)))`——手工取
     子集后必须重做。
  3. α 图注明「当前默认脚本未抽平」、β 图注明「当前默认脚本用相对丰度」；不预设「Fe 应显著」或任何 R² 区间；真实数据的
     α/β、R²、p 本课未实测，以你的运行结果为准（unverified）。
- **出错信号**：metadata.tsv 不存在时脚本只打印「跳过多样性统计」就继续（R L148–150）——不报错但交付缺三大件（回看步骤 1 的强制
  预检）；PCoA 与统计不一致 → 先查行序对齐再怀疑方法（§18.5.6）；betadisper 显著 → 不能直接断言中心移动，按教材 18.4.8 的四行
  表降级解释。

### 步骤 7：抽平与敏感性分析（个人扩展，qsub；非现脚本默认步骤）

- **目的**：完成作业的抽平决策（深度、种子、被剔除样本）与「抽平表 vs 相对丰度表」强制对照。现脚本**无** `rarefy_even_depth`——
  本步骤在个人扩展脚本里完成。
- **命令**（个人扩展；`m06_rarefy.R` 骨架如下，`<...>` 处按你的数据填，改完 grep 再投）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m06
  cat > m06_rarefy.R <<'EOF'
  suppressPackageStartupMessages({library(phyloseq); library(vegan)})
  fqdir  <- "/d3/scratch/USER/ngs/data/m06"; outdir <- "/d3/scratch/USER/ngs/m06/amplicon"
  seqtab <- readRDS(file.path(outdir, "seqtab_nochim.rds"))
  meta   <- read.delim(file.path(fqdir, "metadata.tsv"), row.names = 1, check.names = FALSE)
  common <- intersect(rownames(seqtab), rownames(meta))
  ps <- phyloseq(otu_table(seqtab[common, ], taxa_are_rows = FALSE),
                 sample_data(meta[common, , drop = FALSE]))
  # 1) 稀释曲线定深度（教材 18.4.6：平台期起点附近选深度）
  png("results/rarecurve.png", width = 800, height = 600, res = 120)
  rarecurve(seqtab[common, ], step = 500, cex = 0.4)
  abline(v = <深度>, lty = 2)   # 作业 fig3 要的抽平深度竖线
  dev.off()
  # 2) 抽平（replace=FALSE；深度与种子按你的 nonchim 与曲线定，示例值见教材 18.4.9）
  set.seed(<种子>)
  ps_rare <- rarefy_even_depth(ps, sample.size = <深度>, rngseed = <种子>, replace = FALSE)
  writeLines(setdiff(sample_names(ps), sample_names(ps_rare)), "results/removed_samples.csv")
  # 2b) 抽平后的 α 表（作业 alpha_diversity.tsv 的直接来源）
  meta_rare <- as(sample_data(ps_rare), "data.frame")
  alpha_df <- estimate_richness(ps_rare, measures = c("Observed", "Shannon", "Simpson"))
  alpha_df$group <- meta_rare[rownames(alpha_df), "group"]
  write.table(alpha_df, "results/alpha_diversity.tsv", sep = "\t", quote = FALSE, col.names = NA)
  # 3) 强制对照：抽平表与相对丰度表各算一次 Bray-Curtis + PERMANOVA（教材 18.4.9）。
  #    两路都是组成性口径，本对照只回答「深度处理敏不敏感」，
  #    不能用来诊断或排除相对丰度闭合伪影（§5 第 4 条）。
  ps_rel  <- transform_sample_counts(ps, function(x) x / sum(x))
  meta_rel <- as(sample_data(ps_rel), "data.frame")
  sink("results/permanova_two_way.txt")
  cat("=== 抽平表（样本数 ", nsamples(ps_rare), "）===\n", sep = "")
  print(adonis2(phyloseq::distance(ps_rare, method = "bray") ~ group, data = meta_rare, permutations = 999))
  cat("\n=== 相对丰度表（全样本，n = ", nsamples(ps_rel), "）===\n", sep = "")
  print(adonis2(phyloseq::distance(ps_rel, method = "bray") ~ group, data = meta_rel, permutations = 999))
  # 3b) 敏感性：相对丰度表只用抽平保留的样本再算一次——剔除样本是否推动结论
  ps_rel_sub <- prune_samples(sample_names(ps_rare), ps_rel)
  meta_sub <- as(sample_data(ps_rel_sub), "data.frame")
  cat("\n=== 相对丰度表（仅抽平保留样本，n = ", nsamples(ps_rel_sub), "）===\n", sep = "")
  print(adonis2(phyloseq::distance(ps_rel_sub, method = "bray") ~ group, data = meta_sub, permutations = 999))
  sink()
  EOF
  sed -i "s|/d3/scratch/USER/|/d3/scratch/${USER}/|" m06_rarefy.R
  grep -n 'rarefy_even_depth\|sample.size\|rngseed\|adonis2\|estimate_richness\|alpha_diversity' m06_rarefy.R
  # 作业投递：由 m06_qual.job 改名复制（-pe smp 4、激活同环境，Rscript 行同步改）
  sed 's/m06_qual/m06_rarefy/g' m06_qual.job > m06_rarefy.job
  grep -n 'Rscript\|m06_rarefy' m06_rarefy.job
  qsub m06_rarefy.job
  ```

  这条命令在做什么：抽平深度由 `track.csv` 的 `nonchim` 列＋稀释曲线平台期决定；设例量级：若取 10 000 条而原始
  读段中位 37 031 条，只用掉原始的约 27.0%（`10 000/37 031 ≈ 27.0%`，教材 18.4.9 手算）——分母是**原始**读段，
  去噪去嵌合先砍一截，能不能抽到要看 `nonchim` 列，不能拿 37 031 推断「不会被剔除样本」。教材的
  `sample.size=10000, rngseed=20260829` 只是示例参数，不得照抄为本批结果。
- **产出文件**：`results/rarecurve.png`（fig3 原料）、`results/removed_samples.csv`（被剔除样本名）、
  `results/alpha_diversity.tsv`（作业交付物）、`results/permanova_two_way.txt`（三段结果：抽平表／相对丰度全样本／仅保留样
  本）。以上全部不是现脚本默认产物，报告写明「个人扩展」。
- **检查点**：报告抽平深度、随机种子、被剔除样本数与样本名（不静默丢弃，教材 18.4.9；抽平提示消息里的 `N` 由本次运行决定，具体
  文本随版本，读含义不抄字面）；抽平表与相对丰度表各用**各自对齐的样本集**（`ps_rare` 配 `meta_rare`，`ps_rel` 配
  `meta_rel`），剔除样本只进全样本一侧；第三段（仅保留样本）与第一、二段并排读——剔除样本若翻转了前两段的对比结论，必须在报告写
  明这是样本集差异而非归一化方法差异。两种口径的 R²/p 并排记录，**结论翻转必须写进报告**，不许挑好看的报（教材 18.4.9）。
- **出错信号**：出现 `N samples removed...` 式提示 → 这是决策信号不是错误：降深度保样本，或保深度并把被剔除样本名与深度写进报
  告（教材 18.4.9：不允许静默丢弃）；若 `adonis2` 报 `'qr' and 'y' must have the same number of rows` → 你大概率用了未对齐的元
  数据表（本骨架已按各自样本集对齐，改过代码的按上面口径自查）。

### 步骤 8：年份协变量与扩展统计（个人扩展，qsub）

- **目的**：区分未调整关联与控制年份后的偏关联（教材 18.4.8 博士块、18.6）。现脚本只跑 `d ~ group`（R L133），年份模型要手动扩
  展。
- **命令**（个人扩展；以下 R 代码进 `m06_year.R`，投递方式同步骤 7）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m06
  cat > m06_year.R <<'EOF'
  suppressPackageStartupMessages({library(phyloseq); library(vegan)})
  fqdir  <- "/d3/scratch/USER/ngs/data/m06"; outdir <- "/d3/scratch/USER/ngs/m06/amplicon"
  seqtab <- readRDS(file.path(outdir, "seqtab_nochim.rds"))
  meta   <- read.delim(file.path(fqdir, "metadata.tsv"), row.names = 1, check.names = FALSE)
  common <- intersect(rownames(seqtab), rownames(meta))
  ps_rel <- transform_sample_counts(
    phyloseq(otu_table(seqtab[common, ], taxa_are_rows = FALSE),
             sample_data(meta[common, , drop = FALSE])), function(x) x / sum(x))
  meta_df <- as(sample_data(ps_rel), "data.frame")
  d <- phyloseq::distance(ps_rel, method = "bray")
  stopifnot(all(rownames(meta_df) == rownames(as.matrix(d))))   # 行序对齐，教材 §18.5.6
  meta_df$year <- factor(meta_df$year)
  sink("results/permanova_year.txt")   # 结果落盘，不被屏幕刷掉
  adonis2(d ~ group, data = meta_df, permutations = 999)
  adonis2(d ~ year + group, data = meta_df, by = "margin", permutations = 999)  # group 行=控制年份后的偏效应
  bd <- betadisper(d, meta_df$group); permutest(bd, permutations = 999)
  sink()
  # 若按年份分块限制置换：permutations = how(blocks = meta_df$year, nperm = 999)
  # 两张 PCoA：分别按 group 与按 year 着色（教材 18.6 的肉眼检查）
  ord <- ordinate(ps_rel, method = "PCoA", distance = "bray")
  g1 <- plot_ordination(ps_rel, ord, color = "group") + geom_point(size = 3) +
    labs(title = "PCoA (Bray-Curtis)", color = "Group") + theme_bw(base_size = 12)
  ggsave("results/pcoa_group.png", g1, width = 6, height = 5, dpi = 150)
  g2 <- plot_ordination(ps_rel, ord, color = "year") + geom_point(size = 3) +
    labs(title = "PCoA (Bray-Curtis)", color = "Year") + theme_bw(base_size = 12)
  ggsave("results/pcoa_year.png", g2, width = 6, height = 5, dpi = 150)
  EOF
  sed -i "s|/d3/scratch/USER/|/d3/scratch/${USER}/|" m06_year.R
  grep -n 'adonis2\|betadisper\|sink\|ggsave' m06_year.R
  sed 's/m06_qual/m06_year/g' m06_qual.job > m06_year.job
  qsub m06_year.job
  ```

  多因子模型必须显式 `by`（`"terms"` 顺序检验／`"margin"` 边际检验），读 `group` 行；不写 `by` 在新版 vegan 上
  只给整体模型 p。分层/配对设计须把置换限制在可交换层内；限制后可达排列数减少，教材 18.4.8 的 `2/C(2n,n)`
  设计天花板表不再适用。作业 fig5 要求置信椭圆与 R²/p 标注：在 `g1` 上加 `stat_ellipse()` 与
  `annotate("text", ..., label = paste0("R2 = ..., p = ..."))`（数值取自 `beta_stats.txt`）。
- **产出文件**：`results/permanova_year.txt`（两个模型＋betadisper 完整输出）、`results/pcoa_group.png`、
  `results/pcoa_year.png`（fig5 原料）。以上均为个人扩展产物。
- **检查点**：年份内 2+2/4+4/4+4 是**交叉平衡**设计（教材 18.1/18.6）——平衡交叉下 `group` 项自己的 R² 不因加入年份而下降（变大
  的是总模型 R²），所以「加年份 R² 一定下降」不是规律；读两个模型 `group` 行的边际 R² 与 F 并排看，不比较两个 p 值的大小。「效
  应消失」不能直接判混杂：可能是确实无独立关联，也可能是功效不够（教材 18.4.8）。设计天花板手算（教材 18.4.8）：本设计每组 10
  个，`2/C(20,10) ≈ 1.08×10⁻⁵`，远低于 0.05；999 次随机置换的最小可报非零 p 是 `1/(999+1) = 0.001`（分辨率，与天花板分开）。
- **出错信号**：完全混杂（某年只有一组）→ 两个效应不可分别辨识，结论改写为不可归因（教材 18.4.8；第 13 章设计面）；betadisper
  显著或行序断言失败 → 先停止「中心移动」的解释。

### 步骤 9：按作业规格整理提交物

- **目的**：把现脚本产物与个人扩展产物按作业清单归位，文件名与作业规格逐字一致。
- **命令**（整理与打包；zip 在登录节点做）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m06
  # 1) 格式转换：.rds 是 R 专有二进制、.csv 是逗号分隔——都不能靠 cp 或改后缀变成
  #    TSV（那样交上去的是损坏/错格式的文件）。用 R 正经转：
  Rscript -e '
  seqtab <- readRDS("amplicon/seqtab_nochim.rds")
  write.table(seqtab, "results/asv_table.tsv", sep = "\t", quote = FALSE, col.names = NA)
  tax <- read.csv("amplicon/taxonomy.csv", row.names = 1, check.names = FALSE)
  write.table(tax, "results/taxonomy.tsv", sep = "\t", quote = FALSE, col.names = NA)
  '
  head -2 results/asv_table.tsv results/taxonomy.tsv    # 目检：制表符分隔、首行是列名
  # 2) 图与表按作业文件名归位（PNG 已由个人扩展脚本直接产出，不做 PDF 转换）
  mkdir -p figs
  cp results/qual_F.png figs/fig1_quality_profile.png   # 定稿版=加 truncLen 竖线后重存的那张
  cp results/rarecurve.png figs/fig3_rarecurve.png
  # fig2：每批次一张 error_model_F_<batch>.png，选主批次；要合并多批次就拼图后另存同名
  cp amplicon/error_model_F_<你的主批次>.png figs/fig2_error_model.png
  ls -lh figs results                        # 命名核对：六个 fig 文件名逐字对齐作业 ②
  conda env export --no-builds > env_snapshot.yml
  ```

- **fig6 属水平堆叠图**（作业六图之一；现脚本与本指导前述扩展都不产出它，完整代码如下，在个人扩展脚本里 qsub 跑）：

  ```bash
  cat > m06_fig6.R <<'EOF'
  suppressPackageStartupMessages({library(phyloseq); library(ggplot2)})
  fqdir  <- "/d3/scratch/USER/ngs/data/m06"; outdir <- "/d3/scratch/USER/ngs/m06/amplicon"
  seqtab <- readRDS(file.path(outdir, "seqtab_nochim.rds"))
  meta   <- read.delim(file.path(fqdir, "metadata.tsv"), row.names = 1, check.names = FALSE)
  common <- intersect(rownames(seqtab), rownames(meta))
  ps <- phyloseq(otu_table(seqtab[common, ], taxa_are_rows = FALSE),
                 sample_data(meta[common, , drop = FALSE]))
  psg <- tax_glom(ps, taxrank = "Genus")                       # ASV 聚合到属
  psg <- transform_sample_counts(psg, function(x) x / sum(x))  # 相对丰度
  tt <- tax_table(psg)
  gen <- tt[, "Genus"]; gen[is.na(gen) | gen == ""] <- "unclassified"
  tt[, "Genus"] <- gen; tax_table(psg) <- tt
  s <- sort(taxa_sums(psg), decreasing = TRUE)
  N <- min(10, ntaxa(psg))   # 作业 ② 写 Top 10–15；教材不设固定数量——报告写明你取的 N 与理由
  keep <- names(s)[1:N]
  tt <- tax_table(psg)
  tt[, "Genus"][!(taxa_names(psg) %in% keep)] <- "Others"      # 长尾归并 Others
  tax_table(psg) <- tt
  df <- psmelt(psg)
  df <- aggregate(df$Abundance, by = list(Sample = df$Sample, Genus = df$Genus), FUN = sum)
  names(df)[3] <- "Abundance"
  df$Genus <- factor(df$Genus, levels = c(names(s)[1:N], "Others", "unclassified"))
  p <- ggplot(df, aes(x = Sample, y = Abundance, fill = Genus)) +
    geom_bar(stat = "identity") +
    labs(x = "Sample", y = "Relative abundance", title = "Genus-level composition (Top N + Others)") +
    theme_bw(base_size = 11) + theme(axis.text.x = element_text(angle = 90, hjust = 1))
  ggsave("results/fig6_taxa_barplot.png", p, width = 9, height = 6, dpi = 150)
  EOF
  sed -i "s|/d3/scratch/USER/|/d3/scratch/${USER}/|" m06_fig6.R
  grep -n 'tax_glom\|psmelt\|ggsave' m06_fig6.R
  sed 's/m06_qual/m06_fig6/g' m06_qual.job > m06_fig6.job
  qsub m06_fig6.job
  ```

- **fig4 α 多样性箱线图**（作业 fig4 要箱线图＋检验 p 值；`plot_richness` 默认是散点）：以步骤 7 的 `alpha_diversity.tsv` 为
  底，`ggplot(alpha_df, aes(x = group, y = Shannon, fill = group)) + geom_boxplot(alpha = 0.4) + geom_jitter(width = 0.15)` 出
  箱线图；p 值用 `wilcox.test(Shannon ~ group, data = alpha_df)`（两组）或 `kruskal.test(...)`（多组）算出后 `annotate()` 标在
  图上（图题/轴/图例一律英文）。
- **产出文件**：`学号_姓名_m06/` 全套（见 §7）。
- **检查点**（最终自检清单）：先 track 后图；抽平深度/种子/剔除名单齐；两种深度校正结果与敏感性段齐；R²/p/betadisper 成对；相
  对丰度措辞（全文不写「含量」）；文件名与作业规格一致（`ls figs` 六个 PNG 逐字对上）；TSV 是真制表符分隔（head 目检），不是改
  后缀的 CSV/二进制；脚本可原样重跑（`scripts/` 里是你实际用的副本）。
- **出错信号**：发现自己是按「图好看」挑结论 → 回步骤 7 的强制对照，两种口径都报（教材 18.4.9）。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果；「自查口径」注明来源，不预填数字。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查口径（来源） |
|---|---|---|---|---|
| 0 下载 | run 数 / 成对 basename 数 / 校验行数 | 个 | | run 数与成对数 = 20；校验行数 = 40（每 `.gz` 一条，§2 数据规模口径） |
| 2 截断 | `TRUNC_F/TRUNC_R/TRIM_F/TRIM_R` 决策值 | bp | | 减法 `(F−l_F)+(R−l_R)−253 ≥ 12`，余量口径写明（教材 18.4.1） |
| 2 截断 | 减法结果 O | bp | | 手算例：带引物 148、已去引物 187（教材 18.4.1） |
| 3 主流程 | 作业状态 / 日志错误 | 文字 | | `qstat` 无 Eqw；产物逐个非空 |
| 4 track | 每样本 filtered/input | % | | 课程自查线 >70%（README m06，非实测非阈值） |
| 4 track | 每样本 merged/filtered | % | | 课程自查线 >60%（同上）；`merged_frac<0.5` 为脚本警告 |
| 4 track | 每样本 nonchim/merged | % | | 课程自查线 >55%（同上） |
| 4 错误模型 | 各批曲线是否正常 | 定性 | | 灰点随 Q 降、黑线贴灰点（教材 18.4.3） |
| 5 注释 | minBoot / NA 比例 / 最低阶元 | — / % / 阶元 | | 属水平为主正常；大片 NA 或只到门为警报（§18.5.3） |
| 6 统计 | 距离 / R² / p / 置换数 | — | | Bray–Curtis；999 次；betadisper 成对（教材 18.4.8） |
| 6 统计 | vegan 版本 | 文字 | | `packageVersion("vegan")` 实读 |
| 6 统计 | 行序对齐检查 | TRUE/FALSE | | `all(rownames(meta)==rownames(as.matrix(d)))`（§18.5.6） |
| 7 抽平 | 深度 / 种子 / 被剔除样本数与名 | 条 / — / 个 | | 由 nonchim＋稀释曲线定（教材 18.4.9；10 000/20260829 仅为示例） |
| 7 抽平 | 抽平表 vs 相对丰度表 vs 仅保留样本 R²/p | — | | 三段各自样本集对齐、并排记录；翻转必须报告（教材 18.4.9） |
| 8 协变量 | 两模型 group 行 R²/F/p | — | | `by="margin"` 读 group 行；不比 p 大小（教材 18.4.8） |

## 5. 失效条件对照（教材 §18.5，本实验里在哪一步、看什么能察觉）

1. **双端重叠不足：五列全绿只有 merged 塌**（§18.5.1）｜察觉：步骤 4 的 `track.csv` `merged/merged_frac` 列（脚本 <0.5 警
   告）；回步骤 2 做减法。量级直觉（合成算例，课程仓库根目录运行）：
   `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch18_overlap_trunclen.py --selftest`（正常 V4 合并 99.0% vs 过度截尾
   5.78%）。
2. **不同 run 混学错误模型**（§18.5.2）｜察觉：步骤 1 按 FASTQ 头核实批次（年份≠run）；步骤 4 逐批
   `error_model_F_<batch>.png`；把「缺批次列」警告当错误。量级直觉（合成）：
   `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch18_error_model_mixrun.py --selftest`（双向失真，净效应不定）。
3. **分类注释分辨率天花板：种名不是鉴定**（§18.5.3）｜察觉：步骤 5 的 `taxonomy.csv` NA 比例与最低阶元；大片 NA/只到门按三病因
   依次核对（训练集区段、`TRIM_F/R`、方向）。
4. **相对丰度闭合造成成片假下降**（§18.5.4）｜察觉：**先查有没有绝对锚**（spike-in/qPCR/总细胞计数）——没有就只写相对丰度；大量
   类群同向变化时优先怀疑闭合。步骤 7 的「抽平表 vs 相对丰度表」对照只回答深度处理敏感性，**不能**用来诊断或排除闭合（两路都是
   组成性口径，结果一致也无法排除闭合）。步骤 9 措辞全文用「相对丰度」。量级直觉（合成）：
   `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch18_compositional_closure.py --selftest` （一个类群翻倍、其余绝对量未变
   → 7/7 被判显著下降）。
5. **`truncLen` 超过实际读长：filtered=0，三种现场**（§18.5.5）｜察觉：步骤 2 的减法与读长核对（`seqkit stats` 看实际读长）；
   步骤 4 看 `filtered` 列与 track 列数——部分样本为 0 下游 NA／全部为 0 精简表后停／合并总数为 0 完整 track 后停。
6. **距离矩阵与元数据行序错位**（§18.5.6）｜察觉：步骤 0 的 basename 成对核对（脚本只比条数）；步骤 6/8 的
   `all(rownames(meta)==rownames(as.matrix(d)))` 断言；图与统计不一致时先查对齐。

## 6. 思考题（教材 §18.7 习题的上机版；答案要点在 §18.9，本指导不给答案）

1. V4 数据、PE250、下机带引物：`truncLen=c(240,200)` 时的有效重叠是多少？把算式写全（§18.7 习题 4 → 18.4.1）。
2. （设例数字，出自教材 §18.7 习题 5，非实测）某样本 track 表 input 38 200、filtered 35 900、denoisedF 35 420、denoisedR 35
   310、merged 9 800、nonchim 9 100：读段掉在哪一步？给两个相容病因假设与先查的三样东西（§18.7 习题 5 → 18.5.1）。
3. （设例数字，出自教材 §18.7 习题 6，非实测）同一份数据，Jaccard 的 PERMANOVA 显著（R²=0.09，p=0.002）而 Bray–Curtis 不显著
   （R²=0.03，p=0.21）：两个距离下各能下什么结论、还要补报什么？写一句可直接进论文的陈述（§18.7 习题 6 → 18.4.7）。
4. 写一段 150 字以内的抽平决策说明，必须含深度、随机种子、被剔除样本处理、哪些分析抽平哪些不抽平（§18.7 习题 8 → 18.4.9）。
5. 二十个样本跨三年且年份内两组数量相同：写出放与不放年份的两个模型（含 `by` 取值），说明各自回答什么；若改成「2017 年只有
   Fe、2018 年只有 nonFe」会怎样（§18.7 习题 11 → 18.4.8）。

## 7. 提交物

- **对应作业**：`08_assessment/master/assignments/m06_amplicon_assignment.md`，打包为 `学号_姓名_m06.zip` （≤ 200 MB），解压后
  目录与文件名单字按作业 ②：`report.pdf`（正文 ≤ 8 页，六节：1 数据与截断决策／2 去噪追踪表判读／3 抽平决策说明／4 α 多样性／5
  β 多样性／6 方法选择与结果可信度说明 ≤ 1 页）、`scripts/{run_dada2.sh, dada2_pipeline.R}`（你实际用的副本）、
  `results/{dada2_track.csv, asv_table.tsv, taxonomy.tsv, alpha_diversity.tsv, permanova.txt}`、
  `figs/` 下六个 PNG——`fig1_quality_profile.png`、`fig2_error_model.png`、`fig3_rarecurve.png`、
  `fig4_alpha_boxplot.png`、`fig5_pcoa.png`、`fig6_taxa_barplot.png`（图题/轴/图例一律英文）、`env_snapshot.yml`。
- **现脚本到作业的映射**（区分「已生成」与「待你生成」）：
  - 现脚本直接产出、改名归位：`track.csv`→`dada2_track.csv`（保留 batch/merged_frac）；
    `beta_stats.txt`→`permanova.txt`（adonis2 与 betadisper 完整两段）。
  - 步骤 9 格式转换生成：`seqtab_nochim.rds`→`asv_table.tsv`（未抽平原始计数）；`taxonomy.csv`→`taxonomy.tsv` （记 minBoot）。
  - 个人扩展生成：步骤 2 质量图（fig1 原料，加竖线后定稿）、步骤 4 `error_model_F_<batch>.png`（fig2）、步骤 7 `rarecurve.png`
    （fig3）与 `alpha_diversity.tsv`、步骤 8 `pcoa_*.png`（fig5 原料，加椭圆与 R²/p 标注后定稿）、步骤 9
    `fig6_taxa_barplot.png` 与 fig4 箱线图。以上报告均写明「个人扩展」；`ls -lh figs` 逐名核对，缺哪个补哪个。
- **评分权重**：流程完整性 40／结果正确性 30／方法选择与结果可信度说明 30（四问：为什么这个检验与距离、为什么这个阈值与深度、
  假阳性风险在哪、什么证据能推翻结论）。
- **诚实红线**：真实数据的 track 比例、ASV 数、注释率、α/β、R² 与 p 全是**你自己跑出来的**才能进报告；教材 §18.6 的整段结果数
  字是设例，不得照抄；一切「预期区间（未实测）」不得写成实测；抽平被剔除样本必须具名。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念/失效条件/习题/结果设例） | `textbook/chapters/ch18/manuscript.qmd` §18.4 / §18.5 / §18.7 习题（答案要点 §18.9）/ §18.6 |
| 本专题讲义（⑤5.1–5.4 操作、⑥ 结果解读、⑦ 统计插件、⑨ 常见错误） | `02_lectures/master/topic06_amplicon/06_amplicon_lecture.md` |
| 作业脚本 | `03_code/master/scripts/06_run_dada2.sh`、`06_dada2_pipeline.R`（个人扩展按「副本→改→grep→qsub」） |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch18_overlap_trunclen.py`、`ch18_error_model_mixrun.py`、`ch18_compositional_closure.py` |
| 数据说明、下载与课程自查线 | `06_data/master/README.md` m06 节；`06_data/master/download_master.sh`；登录号 `06_data/accessions.tsv` L77–L97 |
| SILVA v138.2 训练集（DADA2 格式） | Zenodo 记录 14169026，文件 `silva_nr99_v138.2_toGenus_trainset.fa.gz`（2024-11-15 发布） |
| 环境定义 | `07_envs/conda/env_master_microbiome.yml`（`ngs_ms_microbiome`） |
| 作业规格 | `08_assessment/master/assignments/m06_amplicon_assignment.md` |
