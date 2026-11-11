---
title: "实验指导 m01：高通量测序原理与实验设计"
level: master
topic: m01
textbook: [ch13, ch04]
lecture: ../02_lectures/master/topic01_ngs_design/01_ngs_design_lecture.md
env: ngs_ms_base
---

# 实验指导 m01：高通量测序原理与实验设计

> 上机时手边打开的这份文件。每一步都回答四件事：这条命令在做什么、敲什么、
> 看到什么算对、看到什么说明错了。判据在教材第 13 章（§13.4 概念、§13.5 失效条件），
> 平台与文库选型判据在第 4 章；本指导只放操作与自查入口。
> 检查点里的每个数字都带来源（教材实查、讲义口径或 demos 现跑）；
> 2026-11-11 教师已在课程集群（登录节点 mu01 + 计算节点）按本指导从头到尾彩排一遍，
> 文中标「集群实测」的数字即彩排所得；彩排时的网速等环境数字只代表当时，上课以现场为准。

## 0. 本实验对应什么

- **教材**：第 13 章 实验设计：重复、深度与批次，重点 §13.4.5（批次与区组）、
  §13.4.6（公共数据检索、下载与验收）；对应学习目标 LO13-05（设计矩阵可识别性、
  区组化与随机化）与 LO13-06（层级检索与四步验收）。步骤 6/7 另用 LO13-03/04 的
  固定预算账与深度换算账。平台与文库选型的判据（方案第 2 段要用）在第 4 章。
- **讲义**：m01 ⑤5.1–5.6（操作步骤）、⑥6.1–6.5（读设计表与验收结果）、⑨E1–E8（排错）。
- **学时**：m01 共 4 学时，本实验是其中的上机实践环节；作业规格建议上机 2–3 小时（含下载等待）。
- **环境**：conda 环境 `ngs_ms_base`（`07_envs/conda/env_master_base.yml`）。
  sra-tools / entrez-direct / pysradb / kingfisher 在该 yml 里**未钉版本**。集群实测
  （2026-11-11）：激活 `ngs_ms_base` 后 `prefetch`、`fasterq-dump` 解析到系统的
  `/opt/bio/sratk/bin/`、`esearch` 解析到 `/opt/bio/edirect/`，**`kingfisher`、`pysradb` 不在**——
  上机仍以 `command -v` 实查为准，把实见路径与版本号记进 verify_log.txt（教材 13.4.6 口径：
  只写工具名，版本上机自查）。缺件不阻断本实验：检索与验收只用 curl + awk + md5sum。
- **课程材料在集群上的位置**（下文统称「m01 课程目录」，只读）：`/d3/lab/ngs/master/m01/`
  ——`scripts/`（下载脚本、登录号核验脚本与清单）、`demos/`（步骤 6 的四个演示）、
  `data/`（本实验数据的预置副本与对照练习文件，见 §2）。
- **计算纪律**：两类任务分两处执行（根 CLAUDE.md 集群事实：**计算节点不通外网**）——
  **联网任务**（检索元数据、下载 FASTQ、`prefetch`）只能在**登录节点**做，绝不能 qsub 投递
  （投到计算节点必因断网失败）；**CPU 计算**（全文件解压计数、MD5 计算等）一律 `qsub`
  投递计算节点或进 `qrsh` 交互节点（讲义 ⑨-E4；登录节点只下载、建环境、编辑，
  与本科生 u08 指导书同口径）。下面每步命令都标了执行位置。

## 1. 实验前检查

- **前置模块**（讲义 ②，先确认自测能过，跟不上就回查对应题号）：
  `l0_04_formats` L0-4-Q1/Q2/Q3/Q5（FASTQ 四行结构与计数陷阱、Phred 分数）、
  `l0_06_stats` L0-6-Q6/Q7/Q8（批次混杂、重复与功效、PCA 诊断）、
  `l0_01_linux` L0-1-Q5/Q8/Q10（登录节点 vs qsub vs qrsh、批量文本处理、项目目录）、
  `l0_03_conda` L0-3-Q9/Q10（建环境、SGE 作业内激活环境）。
- **登录号核验**（教材 13.4.6：凡是登录号先核再用，不能凭印象写）：

  ```bash
  bash /d3/lab/ngs/master/m01/scripts/verify_accessions.sh PRJNA295606 SRR2584863
  ```

  这条命令在做什么：向 ENA 与 NCBI 各查一次本实验要用的 BioProject。先确认联网正常
  （代理、时段、HTTP 状态）再判读结果：网络确认无虞仍查不到，才是未公开或登录号写错
  （讲义 ⑨-E1 同型判断；区分流程见步骤 1 出错信号）。
  集群实测（2026-11-11）：两行都是 `[通过]`，`PRJNA295606` 312 条记录、`SRR2584863` 1 条记录，
  物种均为 `Escherichia coli B str. REL606`，末行 `全部通过。`
- **激活环境并核验工具链**（版本不写死，看到什么记什么）：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_base
  command -v prefetch fasterq-dump kingfisher pysradb esearch || true
  ```

  这条命令在做什么：SGE 作业不继承你终端里的 conda 变量，每个作业脚本开头都要自己激活环境
  （讲义 ⑨-E5 的写法）；`command -v` 逐个确认工具在 PATH 里，缺哪个就在 verify_log.txt
  里记一行，本实验的验收流程不依赖它们。
- **检查点**：核验脚本两行 `[通过]` 并以 `全部通过。` 结尾；`command -v` 每个工具打印一行路径或静默缺失。
- **出错信号**：`conda activate` 报 `Could not find conda environment: ngs_ms_base` →
  环境没建或没配 envs_dirs（讲义 l0_03 对应自测；根 CLAUDE.md：课程环境在 `/d3/lab/envs`，
  两套 conda 都要 append envs_dirs）｜工具缺失 → 按讲义 ⑨-E6 降级（ENA 直链 curl 永远可用），
  不要为此在登录节点重装环境耽误实验。

## 2. 实验数据

本实验只用一套公共数据——Lenski 大肠杆菌长期演化实验（LTEE）——练「检索 → 下载 →
验收 → 整理 → 写方案」。两个登录号都已登记 `06_data/accessions.tsv`
（`PRJNA295606` 第 8 行、`SRR2584863` 第 9 行）：

| 登录号 | 层级 | 内容与体量 | 来源 |
|---|---|---|---|
| `PRJNA295606` | BioProject | LTEE 项目；ENA Portal API 实查返回 312 个 Run（2026-11-04 实查，2026-11-10 复查一致；**以现场 API 返回为准**） | 教材 13.4.6/13.6 |
| `SRR2584863` | Run | 双端 WGS，Illumina HiSeq 2500；`read_count` 计 **1 553 259 个片段**、`base_count` **465 977 700 bp**（算术核对：`1 553 259 × 2 × 150 = 465 977 700`） | 教材 13.4.6/13.6，ENA 实查 |

- 本实验只下载 **1–2 个 Run**（讲义 ⑤5.3：全部下完既没必要也占配额）。
- 工作目录：`/d3/scratch/${USER}/ngs/m01`。原始与下载数据一律进 scratch，**不要放家目录**
  （家目录配额小，prefetch 默认落 `~/ncbi/public` 会写爆，讲义 ⑨-E2）。
- **课上用预置副本，课后再自己下**：集群出口带宽很窄。彩排实测（2026-11-11，登录节点单人）
  从 ENA 取这个 Run：FTP 约 50 KB/s（下载脚本默认走 FTP，两文件共约 374 MB，
  单人约 2 小时）、HTTPS 约 0.37 MB/s（单人约 17 分钟）；全班同时下载只会更慢。所以课上把
  `SRR2584863` 的两个原始文件预置在 m01 课程目录，步骤 2 先把它们拷进你的下载目录，
  脚本见到文件「已存在」就跳过下载——**这正好让你亲眼看到「非空即跳过」**（步骤 2 重跑注意），
  于是步骤 4 的四步验收一步都不能省。预置副本是从 ENA 直链原样取回的 gzip，MD5 应与
  `fastq_md5` 逐位一致；**不信它，就用步骤 4 证明它**。

  | 文件（m01 课程目录 `data/` 下） | 用途 | 大小（ENA `fastq_bytes`） |
  |---|---|---|
  | `SRR2584863_1.fastq.gz`、`SRR2584863_2.fastq.gz` | 预置副本，步骤 2–4 用 | 183 292 913 / 191 090 316 bytes |
  | `MD5SUMS` | 教师侧核对记录（**作业的 MD5 判据仍取你自己检索的 runinfo_ena.tsv**） | — |
  | `practice/SRR2584863_1.truncated.fastq.gz` | 步骤 4 对照练习：模拟下载被掐断的半截文件，**不是**数据 | 120 000 000 bytes |
- 数据自查入口：硕士层 README 只登记 m02–m07 主线数据，m01 数据来自公共库——
  所以四步验收（步骤 4）就是你唯一的对错判据。
- 贯穿说明：本实验的四个合成演示（步骤 6）是固定种子的合成算例，数字只对各自生成模型
  成立（教材 13.1 末段的数字口径：合成算例不能当实测）；检索与验收的数字则来自
  ENA 实查，入口随数字标注。

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出文件 / 检查点 / 出错信号。
> 命令里的脚本名、参数名、输出文件名与 `03_code/master/scripts/01_fetch_sra.sh`
> 现版逐字核对过（本指导修订时已逐个 grep 源码，证据见任务回执）。步骤 1–6 已于
> 2026-11-11 在集群按原文彩排（预置副本路线）；prefetch 备用路线未彩排，其耗时与临时空间不写预期值。
>
> **在哪敲命令（工作目录约定）**：SSH 登录后当前目录是家目录。下文所有路径以
> `/d3/scratch/${USER}/ngs/m01` 为工作根；课程提供的脚本、演示与预置数据都在只读的
> m01 课程目录 `/d3/lab/ngs/master/m01/`（§0）。联网步骤（步骤 1、2、3 主体）在登录节点用
> `bash`/裸命令执行，输出直接打在终端，没有作业日志；`qsub` 投递的计算作业（步骤 4 的
> `verify_fastq.sh`）用绝对路径投递，或在放作业脚本的目录里投递相对路径——作业日志
> （`verify_fastq.o<作业号>`，作业头 `#$ -j y` `#$ -cwd`）写在**投递时所在的目录**，
> 与产出文件（写在 scratch 工作根下）不是一回事，找不到文件时先分清自己在找哪一类。

### 步骤 1：检索元数据（ENA Portal API，登录节点）

- **目的**：先看清项目里有什么，再决定下什么。平台、文库类型、声明的 read 数——
  四步验收的全部对照基准都来自这一步（教材 13.4.6：先看清楚再下载，避免下错几十 GB）。
- **命令**（讲义 ⑤5.2 方案 A；10 个字段**含 `fastq_md5`**，该字段只有 ENA 路线拿得到）：

  ```bash
  mkdir -p /d3/scratch/${USER}/ngs/m01 && cd /d3/scratch/${USER}/ngs/m01
  curl -fsS -w '\nHTTP %{http_code}\n' "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=SRR2584863&result=read_run&fields=run_accession,sample_accession,sample_title,instrument_model,library_strategy,library_layout,read_count,base_count,fastq_md5,fastq_ftp&format=tsv" \
      -o runinfo_ena.tsv
  head -2 runinfo_ena.tsv
  ```

  这条命令在做什么：ENA Portal API 无需 API key，`result=read_run` 表示一行一个 Run；
  字段顺序就是表列顺序，第 9 列是 `fastq_md5`、第 10 列是 `fastq_ftp`。
  ENA 默认返回表头行——第 1 行是字段名，第 2 行起才是数据（2026-11-10 实查口径）。
- **产出文件**：`runinfo_ena.tsv`（10 列；作业提交物之一，**原样保留**不要手改）。
- **检查点**（数字全部带入口）：
  1. 第 1 行为 10 列表头，第 2 行为 `SRR2584863` 数据行；
  2. `read_count=1 553 259`、`base_count=465 977 700`，与 §2 表一致（教材 13.4.6/13.6，ENA 实查）；
  3. `instrument_model=Illumina HiSeq 2500`、`library_layout=PAIRED`、`library_strategy=WGS`；
  4. `fastq_md5` 与 `fastq_ftp` 各是分号分隔的**两个值**（双端两文件各一枚，ENA 实查口径）——
     第 4 步验收要从这里拆出两枚 MD5。
- **出错信号**（按序排查：先网络，后登录号）：curl 报错、非 200 状态码或超时 →
  网络/服务问题（代理、限流、时段），换时段重试或走教师提供的代理——此时还轮不到判
  登录号｜HTTP 200 但只有表头、没有数据行 → 登录号错或未公开（教材 §13.4.6 登录号实查；
  讲义 ⑨-E1 同型判断）——带着错的对照基准往下走，四步验收全部作废（教材 §13.5.4）｜
  网络确认无虞仍查不到，不要改用 NCBI 路线（它的 runinfo 没有 `fastq_md5`，第 4 步
  MD5 做不了）。

### 步骤 2：脚本化拉元数据并看分布（登录节点，个人副本）

- **目的**：体验课程脚本的「先元数据、后下载」流程；脚本自动去重表头并打印
  平台/文库/类型分布，分布表是批次线索的第一来源（教材 13.4.6）。
- **命令**（先复制个人副本再在**登录节点**用 bash 直接跑——`03_code` 是课程公共目录，
  只读，不要改原文件；本脚本的主体是联网 I/O，按 §0 计算纪律**不能** qsub 投递）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m01
  echo "SRR2584863" > acc_list.txt
  cp /d3/lab/ngs/master/m01/scripts/01_fetch_sra.sh ./fetch_sra.sh
  grep -n 'ACC_LIST=\|OUTDIR=\|ena_report\|CONDA_ROOT' fetch_sra.sh   # 跑前核对参数与输出名
  # 课上：先放入预置副本，脚本的下载步会跳过（§2「课上用预置副本」）；课后自己下载时省掉这两行
  mkdir -p sra_data/fastq
  cp /d3/lab/ngs/master/m01/data/SRR2584863_?.fastq.gz sra_data/fastq/
  bash ./fetch_sra.sh acc_list.txt /d3/scratch/${USER}/ngs/m01/sra_data
  ```

  这条命令在做什么：`01_fetch_sra.sh <accession_list.txt> [outdir]`（脚本 L20–21 的用法行；
  列表里每行一个 SRR/ERR/DRR，`#` 开头与空行跳过，L29）。**acc_list.txt 只放 1 个 Run**——
  放 BioProject 号会让脚本的下载步拉全项目几百个 Run。脚本内自己激活 `ngs_ms_base`
  （L18：`source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate"`，登录节点同样适用）。
  它一次跑完三步（L27–37 逐号 curl 元数据并去重表头、打印 `instrument_platform
  library_strategy library_layout` 分布计数；L41–47 按 `fastq_ftp` 下载；L51–55 逐文件
  `zcat | wc -l` 打印实际 read 数）——前两步是联网任务，在登录节点跑；第三步的解压计数
  只是**初步打印**，正式的验收计数按计算纪律在步骤 4 用 qsub 重做。
- **产出文件**：`sra_data/meta/ena_report.tsv`、`sra_data/meta/ena_report.clean.tsv`
  （去重表头后每 Run 一行）、终端上的分布计数与 read 数打印。
- **重跑注意（脚本的两个可靠性缺口）**：下载步只「跳过非空文件」，**不验证完整性**
  （被截断的半截文件也会被跳过）；元数据用 `>>` 追加写，**重跑会在 `ena_report.tsv`
  里叠出重复行**。所以不要把「重跑」当纠错手段：发现文件损坏或元数据重复时，先删掉
  损坏的 FASTQ 和整个 `meta/` 旧表，再从本步骤开头重跑，对错最终以步骤 4 的
  MD5 与计数为准——脚本当前版本行为如此，不要按「幂等，重跑即可」理解它。
- **检查点**（集群实测 2026-11-11：终端依次打印 `1 ILLUMINA WGS PAIRED`、两行 `已存在，跳过 …`、
  两行 `… 1553259 reads`，登录节点全程约 18 秒）：
  1. `ena_report.clean.tsv` 行数 = Run 数 + 1（表头；本例应为 2 行——手算核对）；
  2. 分布计数里 `library_strategy` 应为 WGS——出现 AMPLICON/RNA-Seq 混进来说明检索式
     没限定策略（教材 13.4.6 元数据判读第一件：`library_strategy` 读错，后面全错）；
  3. 对照步骤 1 的 `runinfo_ena.tsv`：同一 Run 的 `read_count`/`base_count` 两表一致
     （ENA 同一接口，理应逐位相同；不一致说明有一步拿到了截断响应，先按重跑注意
     清旧表重检索，仍不一致再按教材 §13.5.4 处置）。
- **出错信号**：clean 表只有表头（0 数据行）→ 先查网络与 HTTP 状态，再判登录号
  （处置同步骤 1）｜把本脚本 qsub 到计算节点 → 必因计算节点不通外网而失败
  （§0 计算纪律），回登录节点用 bash 重跑｜
  分布全是同一平台 → 批次线索为零：唯一机型当 `batch` 列是常数列，下游设计矩阵秩亏
  （教材 §13.4.6 第三误用；代数后果见 §13.5.2）｜终端报 `conda activate` 失败 →
  环境没建或没配 envs_dirs（§1 出错信号；脚本 L18 依赖 `${CONDA_ROOT}` 或
  `/opt/miniconda3` 存在）。

### 步骤 3：下载 1–2 个 Run（登录节点；脚本第 2 步已随步骤 2 跑完）

- **目的**：把 FASTQ 拿到 scratch。脚本的下载步（L41–47）从 `fastq_ftp` 列展开 URL、
  逐文件 `curl`，已存在则跳过——注意「非空就跳过」不等于「完整」（重跑可靠性见
  步骤 2 的「重跑注意」）。
- **命令**：步骤 2 的一次运行已跑完三步（元数据 → 下载 → 打印 read 数），下载不用
  单独执行。**课上**下载步因预置副本而跳过（终端两行 `已存在，跳过`）；**课后**想体验真实下载，
  另建一个空目录（如 `sra_data_self/`）、不拷预置副本再跑一遍步骤 2，放进 `screen`/`tmux`
  里等（登录节点 FTP 实测约 50 KB/s，见 §2），下完同样走步骤 4。若改走讲义 ⑤5.3 的 prefetch 路线，按 §0 计算纪律拆开：**联网的 prefetch
  在登录节点跑；耗 CPU 的转换与压缩写进 qsub 作业脚本**：

  ```bash
  # ① prefetch：联网任务，登录节点执行
  prefetch SRR2584863 -O /d3/scratch/${USER}/ngs/m01/sra --max-size 100G
  # ② fasterq-dump + pigz：CPU 计算，写进作业脚本（verify 之外的第二个作业）再 qsub
  cat > convert_fastq.sh <<'EOF'
  #$ -S /bin/bash
  #$ -N convert_fastq
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_ms_base
  fasterq-dump /d3/scratch/${USER}/ngs/m01/sra/SRR2584863 --split-3 -e 8 \
      -O /d3/scratch/${USER}/ngs/m01/fastq -t /d3/scratch/${USER}/tmp
  pigz -p 8 /d3/scratch/${USER}/ngs/m01/fastq/*.fastq
  EOF
  qsub convert_fastq.sh
  ```

  这条命令在做什么：`-O` 不给会落到 `~/ncbi/public` 把家目录配额写爆（讲义 ⑨-E2）；
  `--max-size` 默认 20G，大 Run 必须放大，否则**静默跳过**（讲义 ⑤5.3 注释）；
  `--split-3` 保留配对判断，写 `--split-files` 会丢（讲义 ⑨-E7）；`-t` 指向 scratch 大分区，
  临时空间需求取决于工具版本与数据量（本课未实测，不给固定倍数）——投作业前先
  `df -h` 确认 scratch 余量再跑；fasterq-dump 不压缩，务必自行 `pigz`。
  ⚠ 备用路线的 FASTQ 是 sra-toolkit 从 SRA 记录**转换重压缩**的产物，字节与 ENA 直链的
  原始 gzip 不同——步骤 4 的 ① MD5（对 `fastq_md5`）只适用于 ENA 直链文件；走备用路线
  时用 ② read 数与 ③ 双端行数做验收，不要拿 ENA 的 MD5 对转换产物。
- **产出文件**：`sra_data/fastq/SRR2584863_1.fastq.gz` 与 `SRR2584863_2.fastq.gz`（成对）。
- **检查点**：两个文件都存在且非空（`ls -lh`）；文件名 `_1`/`_2` 成对、属于同一 Run
  （非空只是入场券，完整性唯一判据是步骤 4 的 MD5）。
- **出错信号**：`Disk quota exceeded` / `can't open '/home/user/ncbi/public/sra'` →
  讲义 ⑨-E2（没给 `-O` 或给了家目录）｜`storage exhausted while writing file` →
  讲义 ⑨-E3（`-t` 临时空间不足，先 `df -h`）｜fasterq-dump/pigz 直接在登录节点跑
  被管理终止 → 计算纪律（§0），必须放进作业投计算节点（讲义 ⑨-E4 同型）｜
  只产出一个 `.fastq` 没有 `_1`/`_2` →
  先查元数据 `library_layout`（讲义 ⑥6.4：该 Run 可能本就单端，不要靠猜）｜
  下载步 exit 0 只说明「跑完了」，不说明「下全了」——跳过本步直接做分析就是
  教材 §13.5.4 的静默截断现场。

### 步骤 4：四步验收（核心步骤，一步都不能省）

- **目的**：确认拿到的字节与声明一致。课程真实案例：29 个下载文件里 14 个被静默截断、
  脚本不报错不校验、退出码 0（教材 §13.5.4 引课程数据准备记录；根 CLAUDE.md 同源实测）。
  四步的顺序不建议换：MD5 不解析 FASTQ、最先做；read 数与行数依赖文件能正常解压；
  读长自洽同时用元数据与文件内容，放最后（教材 13.4.6）。
- **命令**（①的拆分是几行文本操作，登录节点即可；MD5 计算与②③④的全文件解压计数
  是 CPU 任务，按 §0 计算纪律写成 `verify_fastq.sh` 投计算节点）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m01
  # ① 拆出期望值（登录节点）：fastq_md5 是分号分隔双值，拆分后逐文件比对
  awk -F'\t' 'NR>1{print $9}' runinfo_ena.tsv | tr ';' '\n' > expected_md5.txt
  cat expected_md5.txt
  # ①②③④ 的核验计算写进作业脚本，投递计算节点
  cat > verify_fastq.sh <<'EOF'
  #$ -S /bin/bash
  #$ -N verify_fastq
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  cd /d3/scratch/${USER}/ngs/m01
  md5sum sra_data/fastq/SRR2584863_1.fastq.gz sra_data/fastq/SRR2584863_2.fastq.gz
  # ② read 数：每个文件各应等于 read_count（ENA 对双端计的是片段数，每文件各含一遍）
  echo $(( $(zcat sra_data/fastq/SRR2584863_1.fastq.gz | wc -l) / 4 ))
  echo $(( $(zcat sra_data/fastq/SRR2584863_2.fastq.gz | wc -l) / 4 ))
  # ③ 双端行数必须相等
  [[ $(zcat sra_data/fastq/SRR2584863_1.fastq.gz|wc -l) -eq $(zcat sra_data/fastq/SRR2584863_2.fastq.gz|wc -l) ]] && echo PAIRED_OK
  # ④ 读长自洽：三来源对账——wc -c 字符数、base_count÷(2×read_count) 反算、机型标称
  zcat sra_data/fastq/SRR2584863_1.fastq.gz | head -2 | tail -1 | wc -c
  EOF
  qsub verify_fastq.sh
  ```

  这条命令在做什么：①的 `tr ';' '\n'` 把双值拆成两行，第一行对应 `_1`、第二行对应 `_2`
  （与 `fastq_ftp` 的文件顺序一致）；作业里 `md5sum` 一次算两个文件、与 `expected_md5.txt`
  逐位比对，②③④随后在同一作业里解压计数。④取**第 1 条读段的序列行**（FASTQ 每个读段
  占 4 行，第 2 行是序列；`head -2 | tail -1` 取的就是它）量字符数。注意口径：`read_count=1 553 259` 计的是**片段数**，`_1`、`_2` 每个文件
  各含 1 553 259 条读段、各 4 条一行——按单端口径去对会得到「少一半」的假警报
  （教材 13.4.6）。④的判据是三个来源对得上：`wc -c` 输出 151（150 bp + 换行）、
  `465 977 700 ÷ (2 × 1 553 259) = 150`、HiSeq 2500 标称读长——不是背「151」这个数
  （教材 13.4.6：讲义那句「PE150 应为 151」只是口算版本，具体数据以反算值为准）。
- **产出文件**：`verify_log.txt` 的素材——①的终端输出与作业输出日志
  （`verify_fastq.o<作业号>`，在投递时所在目录）的**原样内容**（作业只交这个，
  不交 FASTQ；手抄的数字不算证据）。
- **检查点**（数字全部带入口）：
  1. ① 两枚拆分 MD5 与 `md5sum` 两文件输出逐位一致（字节级唯一判据；`gzip -t` 通过、
     文件大小接近都不算数，教材 13.4.6）；
  2. ② 两文件各数出 **1 553 259**（ENA 实查，教材 13.4.6/13.6）；
  3. ③ 输出 `PAIRED_OK`；两文件行数各 **6 213 036**（= 4 × 1 553 259，手算）；
  4. ④ `wc -c` 输出 **151**，与反算 150 bp、机型标称三者自洽。

  集群实测（2026-11-11，预置副本，计算节点 cu06）：作业日志依次是两行 MD5
  （`4a1529a4…` / `33492a66…`，与 `expected_md5.txt` 逐位一致）、`1553259`、`1553259`、
  `PAIRED_OK`、`151`，作业约 20 秒跑完。**作业投出后超过 2 分钟仍是 `qw`**，
  不要反复重投——`qstat -u $USER` 截图给助教（调度器故障时所有作业都会卡在 qw）。
- **出错信号**：MD5 不符但大小接近 → 断点续传拼接错/传输截断：**删掉重下，不要接着用**
  （重跑前按步骤 2「重跑注意」同时删掉损坏文件与 `meta/` 旧表；讲义 ⑥6.4；
  教材 §13.5.4）｜read 数少于声明值 → 静默截断（完成判据是产物计数对得上
  声明值，不是退出码，教材 §13.5.4）｜`_1`/`_2` 行数不等 → 配对关系已破坏，后续比对会
  出现大量孤读段（教材 13.4.6 第三步）｜④与反算值对不上 → 下错了 Run 或文件混杂，
  回步骤 2 查映射｜四步全过也只说明「这份数据与元数据一致」，不说明「适合你的问题」——
  后者看文库类型、分组与批次（教材 13.4.6）。
- **对照练习（课上必做，5 分钟）**：看「坏文件」在四步验收里长什么样。m01 课程目录的
  `data/practice/SRR2584863_1.truncated.fastq.gz` 是把 `_1` 只保留前 120 000 000 字节
  做成的半截文件，模拟 `curl` 下到一半被掐断——**大小有 1.2 亿字节、看起来一切正常**。

  ```bash
  cd /d3/scratch/${USER}/ngs/m01 && mkdir -p practice
  cp /d3/lab/ngs/master/m01/data/practice/SRR2584863_1.truncated.fastq.gz practice/
  cat > verify_practice.sh <<'EOF'
  #$ -S /bin/bash
  #$ -N verify_practice
  #$ -cwd
  #$ -j y
  cd /d3/scratch/${USER}/ngs/m01
  md5sum practice/SRR2584863_1.truncated.fastq.gz
  gzip -t practice/SRR2584863_1.truncated.fastq.gz; echo "gzip -t rc=$?"
  echo $(( $(zcat practice/SRR2584863_1.truncated.fastq.gz | wc -l) / 4 ))
  EOF
  qsub verify_practice.sh
  ```

  集群实测（2026-11-11）：MD5 为 `f59290df…`，与 `fastq_md5` 第一枚 `4a1529a4…` 不符；
  `gzip -t` 报 `unexpected end of file`、`rc=1`；read 数打印 **1009467**——只有声明值
  1 553 259 的约 65%，**而计数这一行照样打印出一个像样的整数**。要回答的问题：四步里哪一步最先
  拦住它？如果你只看「作业跑完了、打印了一个数」会怎样？（对应教材 §13.5.4：
  29 个文件 14 个截断、rc=0。）练习文件**不是数据**，只用于本练习，不要拿去做任何分析。

### 步骤 5：整理 sample sheet 并画组 × 批次交叉表

- **目的**：把元数据整理成 `m02`–`m08` 全部复用的标准 8 列表，并人工回填分组——
  公共数据的分组信息经常只写在论文正文里，元数据字段是空的（讲义 ⑤5.5；
  教材 13.4.6）；交叉表是你方案第 5 段的批次设计证据（教材 13.4.5）。
- **命令**（讲义 ⑤5.5 原式）：

  ```bash
  awk -F'\t' 'BEGIN{OFS="\t"; print "sample_id","group","replicate","batch","platform","layout","run_accession","depth_gb"}
       NR>1{print $3, "TBD", "TBD", $4, $4, $6, $1, $8/1e9}' runinfo_ena.tsv > sample_sheet.tsv
  column -t -s $'\t' sample_sheet.tsv   # 只按 Tab 对齐；不加 -s 时 sample_title 里的空格会把一列拆成多列
  ```

  这条命令在做什么：自动填 `sample_id`（`sample_title`）、`platform`（`instrument_model`）、
  `layout`、`run_accession`、`depth_gb`（`base_count ÷ 10⁹`，即碱基 Gb）；
  `group`、`replicate`、`batch` 先填 TBD/占位，**必须人工回填**。
  ⚠ `batch` 列的初值是 `instrument_model`——那只是**占位种子**：同一项目出现两种机型
  是潜在批次的第一条线索，但真正的批次还可能来自送样时间、建库人员、测序中心；
  只有一种机型时该列是常数，直接当 batch 送进下游公式会秩亏（讲义 ⑤5.5 ⚠ 注；
  教材 §13.4.6 第三误用）。确认后改写成真实批次标签。
  本实验只下载 1 个 Run，这份 `sample_sheet.tsv` 只有 1 行——它是**格式与回填方法的
  练习**，不是能画交叉表的设计表。回填的文献入口：本 Run 的 `sample_title` 为
  `Microbe sample from Escherichia coli B str. REL606`（ENA 实查，即步骤 1 表的第 3 列；
  2026-11-10 实查），REL606 是 LTEE 的祖先对照株（教材 13.1 与 13.8 文献表
  `tenaillon2016ltee`，Tenaillon et al. 2016, Nature；LTEE 设计另见 `lenski1991ltee`）——
  据此可回填 `group=ancestor`；`batch`/`replicate` 回论文正文与 ENA 描述确认，写不出
  出处就按出错信号处置，不许留 TBD、也不许填无出处的猜测值。
  ⚠ 组 × 批次交叉表自查的对象是**步骤 7 你自己课题的方案表**（作业 ③ 要求 ≥6 样本、
  分组可查的项目，课上不替你选）：把方案的样本按 批次 × 处理组 列联画表再判区组化。
  课内这 1 行数据画不出交叉表，检查点 3 对它是「不适用」，不是「填 N」。
- **产出文件**：`sample_sheet.tsv`（8 列；作业提交物之一）。
- **检查点**：
  1. 8 列齐全、数据行数 = 你下载的 Run 数；
  2. `group`/`replicate`/`batch` 无 TBD，且每个值能说出出处（论文正文/补充表/ENA 描述；
     教材 13.4.6：元数据的值要可追溯，否则只是格式正确的空字段）；
  3. 组 × 批次交叉表画出来（行 = 批次，列 = 处理组，格 = 样本数）：**每批含全部处理组**
     即区组化（教材 13.4.5）；只有一行/对角矩阵就是混杂警报。自查对象是步骤 7 方案表，
     课内 1 行数据不适用（见上）。
- **出错信号**：`group` 在元数据里是 `sample 1`…或空 → 回论文正文与补充材料手工映射；
  **映射不出来就换数据集，不要用**（讲义 ⑨-E8；教材 §13.4.6、§13.5.4）｜
  `batch` 与 `group` 完全一一对应 → 设计本身就是混杂的，该改设计或换数据集，
  不是换分析方法（讲义 ⑥6.4；教材 §13.5.2）｜回填时发现同一 BioSample 挂多个 Run →
  先查 BioSample → Experiment → Run 映射再决定合并还是并列，别把 Run 数当样本量
  （教材 §13.5.1）。

### 步骤 6：设计自检（四个合成演示，m01 课程目录现跑）

- **目的**：把方案里要写的四笔账变成你能当场辩护的数——预算功效账、秩/可识别性账、
  静默截断账、批次 PCA 诊断账。四个脚本都是固定种子的**合成算例**，数字只对生成模型
  成立，引用时写明口径（教材 13.1 末段）。
- **命令**（四个脚本都只打印、不写文件，几秒跑完；先激活 `ngs_ms_base`——两个 Python 演示要
  scipy，集群环境 2026-11-11 已补装；m01 课程目录只读，日志用 `tee -a` 追加到 scratch 的
  `verify_log.txt`）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m01
  source /opt/miniconda3/bin/activate && conda activate ngs_ms_base
  D=/d3/lab/ngs/master/m01/demos
  PYTHONDONTWRITEBYTECODE=1 python3 $D/ch13_variance_partition.py --selftest 2>&1 | tee -a verify_log.txt
  PYTHONDONTWRITEBYTECODE=1 python3 $D/ch13_design_matrix_rank.py --selftest 2>&1 | tee -a verify_log.txt
  PYTHONDONTWRITEBYTECODE=1 python3 $D/ch13_truncation_confounding.py --selftest 2>&1 | tee -a verify_log.txt
  Rscript $D/ch13_batch_pca.R --selftest 2>&1 | tee -a verify_log.txt
  ```

- **产出文件**：无新文件；四个 `SELFTEST PASS` 行连同关键输出经 `tee -a`
  追加进 `/d3/scratch/${USER}/ngs/m01/verify_log.txt`。若终端不方便用管道，等价做法是
  鼠标选中每次运行的 PASS 行与关键数字，粘贴到该文件尾部——原样粘贴，手抄不算证据。
- **检查点**（rc=0，且关键输出与教材一致）：
  1. 固定预算功效表：每组 90 M 时 3×30 M → **0.152**、6×15 M → **0.313**、
     9×10 M → **0.444**、18×5 M → **0.693**（教材 13.4.3，合成模型）；
     附加对照 6×20 M = **0.321** vs 3×40 M = **0.154** 是**合成设例**（每组 120 M），
     方向演示，不能挂到 Schurch 2016 名下（教材 13.4.3 原话）；
  2. 设计矩阵秩：平衡区组 **3**、完全混杂 **2**（最小范数解 1.606、等价解族
     (γ̂+t, γ̂−t) 的 RSS 恒 1.3879）、lane 与处理共线 **2**/lane 正交 **3**、
     2 组 × 3 批交叉表 **4**（教材 13.4.5）；
  3. 批次 PCA：平衡 **70.8%/13.8%** vs 完全混杂 **82.0%/3.3%**（`set.seed(1234)` 合成数据）——
     这两个数只对这一套数据成立，不能当「混杂的 PC1 一定更高」的判据；PCA 只提示结构
     不裁决（教材 13.4.5）；
  4. 静默截断：不校正假阳性率 **60.7%**（高表达层 87.6%）、CPM 归一后 **4.7%**、
     更深截断（13%–45%）下低表达层归一后仍 **7.6%**；真实锚点 29 文件 14 截断、
     最少 399 491/3 000 000 = **13.3%**、rc=0（教材 §13.5.4；根 CLAUDE.md 同源记录）。
- **出错信号**：某条 PASS 变 FAIL → 先查 Python/numpy/scipy 与 R 版本（集群实测 2026-11-11：
  `ngs_ms_base` 的 Python 3.12.3 / numpy 2.5.2 / scipy 1.18.0 / R 4.3.1 下四条全部 PASS，
  PCA 两组数与 R 4.5.2 逐位一致），**不要改脚本里的数来「修」测试**｜
  `ModuleNotFoundError: No module named 'scipy'` → 没激活 `ngs_ms_base`（系统 python3 没有 scipy）｜
  `No such file` → `$D` 没设或拼错，`ls $D` 应列出 4 个文件。

### 步骤 7：写你自己课题的六段式方案

- **目的**：作业的第二产出。注意练习归练习、方案归方案——`design_proposal.pdf` 写的是
  **你自己**的课题，不是 LTEE（作业 ③-7；讲义 ⑤5.6 六段式、教材 13.4.1 六段表）。
- **命令**：无新命令。按教材 13.4.1 六段逐段写，写完用讲义 ⑥6.5 七条逐项自查：
  ① 科学问题可证伪（不接受「研究 X 的机制」）；② 平台选型至少两维判据并写明放弃了什么
  （判据细节在第 4 章）；③ 明确区分生物学重复与技术重复、说清独立性来源；
  ④ 重复数给依据来源（预实验离散度 / 同类文献 / 功效计算，三选一，不接受「一般用 3」）；
  ⑤ 深度写 `基因组大小 × 目标深度 ÷ 有效比例` 的换算式、有效比例注明来源；
  ⑥ 组 × 批次交叉表、每批含全部处理组，或写明随机化方案；⑦ 元数据 ≥ 6 项
  （建库日期、操作人、试剂批号、仪器与 lane、RNA 完整性、提取批次）+ 预算含失败重测预留。
- **产出文件**：`design_proposal.pdf`（正文 ≤ 4 页）。
- **检查点**：七条每一条都能在文档里找到对应句子（教材 13.4.1：只能勾出前两条的
  还是采购申请，不是实验设计）。
- **出错信号**：第 3 段写不出依据 → 回步骤 6 的功效表与教材 13.4.3 的三步反推
  （技术重复估 σ²_shot → 定最小效应 δ → 由目标功效反解 n）｜第 5 段交叉表是对角矩阵 →
  设计即混杂，回到步骤 5 的出错信号（教材 §13.5.2）｜第 4 段只写整数不写换算式与
  分母来源 → 正是教材 §13.5.3 的失效写法。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果。判据列的来源写在括号里；「你的结果」一栏填实测，
> 与判据不符先按对应步骤的出错信号处置，不要改数字凑判据。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 1 检索 | runinfo_ena.tsv 列数 / 数据行数 | 列 / 行 | | 10 列；数据行 = 检索的 Run 数（ENA 默认带表头，2026-11-10 实查） |
| 2 元数据 | ena_report.clean.tsv 行数 | 行 | | = Run 数 + 1（去重表头，手算） |
| 2 元数据 | library_strategy / library_layout | 文本 | | WGS / PAIRED（ENA 实查；读错后果见教材 13.4.6） |
| 3 下载 | `_1`/`_2` 文件大小 | bytes | | 183 292 913 / 191 090 316（ENA `fastq_bytes`，2026-11-11 实查；大小相同也不代替 MD5） |
| 4 对照练习 | 截断文件的 MD5 / `gzip -t` / read 数 | — / rc / 条 | | MD5 不符；rc=1；1 009 467（集群实测，约为声明值 65%） |
| 4 验收 | `_1` / `_2` 各文件 read 数 | 条 | | 各 = 1 553 259（ENA 实查，教材 13.4.6/13.6） |
| 4 验收 | `_1` / `_2` 各文件行数 | 行 | | 各 = 6 213 036（4 × 1 553 259，手算） |
| 4 验收 | MD5 匹配（`_1` / `_2`） | Y/N | | 与 runinfo_ena.tsv 第 9 列拆分值逐位一致（字节级唯一判据） |
| 4 验收 | `wc -c` 序列行 / 反算读长 | 字符 / bp | | 151（含换行）与 465 977 700 ÷ (2 × 1 553 259) = 150 及机型标称三来源自洽 |
| 4 验收 | instrument_model | 文本 | | Illumina HiSeq 2500（ENA 实查） |
| 5 sheet | 8 列 / group·replicate·batch 回填 | 列 / 定性 | | 8 列齐全；无 TBD；batch 非机型常数列（教材 13.4.6） |
| 5 交叉表 | 每批含全部处理组 | Y/N | | 每行同时出现全部处理组（区组化，教材 13.4.5）；对象为步骤 7 方案表，课内单 Run 填「不适用」 |
| 6 演示 | 四个 `--selftest` | PASS/FAIL | | 全部 PASS（关键数对照 §3 步骤 6 检查点） |

## 5. 失效条件对照（教材 §13.5，本实验里在哪一步、看什么能察觉）

1. **同一份 RNA 的多个文库不是重复，n 不是文库数**（§13.5.1）｜察觉：步骤 2/5——
   一个 BioSample 挂多个 Run 时，先查 BioSample → Experiment → Run 映射与文库描述，
   确认可合并再聚合；把 Run 数当样本量、或把元数据里的多行当成多个独立个体，
   是这条失效在本实验的入口。软件不报错，样本表看着就是「好几个样本」。
2. **批次与处理完全混杂，事后无法分离**（§13.5.2）｜察觉：步骤 5 的交叉表——
   有整行只出现一种处理组即警报；代数确认用 `demos/ch13_design_matrix_rank.py`
   （完全混杂秩 2、最小范数解 1.606、等价解族 RSS 恒 1.3879）；PCA 只提示结构不裁决
   （70.8%/13.8% 与 82.0%/3.3% 只是固定种子合成数据的实现值）。
3. **深度换不来重复：饱和后加深度几乎不提升功效**（§13.5.3）｜察觉：步骤 6 的两笔账——
   目标所需绝对读段数（k/f 下限，教材 13.4.4）+ 固定预算功效对照（0.152 → 0.693 的
   预算表；固定 n=6 时深度 20→120 M 功效仅 +6.7%）。方案第 4 段只写整数、不写换算式
   与分母来源，就是这条失效的标准写法。
4. **数据准备静默截断 + 元数据分组字段为空**（§13.5.4）｜察觉：步骤 4 就是本失效的
   验收现场——真实案例 29 文件 14 截断、最少 399 491/3 000 000 = 13.3%、rc=0；
   完成判据是「产物计数对得上声明值」，不是退出码。步骤 5 的 group 回填是后半句：
   映射不出分组就换数据集，并把映射来源写进 sample sheet。

## 6. 思考题（教材 §13.7，习题 1、2、9、10 的上机版，不给答案）

1. 四个情境里 `n` 各是多少、为什么：① 一株植物的叶片 RNA 分装三管、分别建库测序；
   ② 一个文库分两个 lane 上机；③ 三株独立种植的植株、各取一片叶；
   ④ 公共数据里一个 BioSample 对应三个 Run。（→ 教材 §13.7 习题 1，概念在 13.4.2）
2. 一张设计表：批次 1 有 3 个对照 1 个处理、批次 2 有 1 个对照 3 个处理。批次与处理
   是否完全共线？能否同时估出两个效应？改成「每批 2 对照 + 2 处理」后结论怎么变？
   （→ 教材 §13.7 习题 2，概念在 13.4.5；可用 `demos/ch13_design_matrix_rank.py` 的
   交叉表情形验证你的判断）
3. 审查这份方案、至少找出五处问题并各给一条改法：三组、每组 3 个重复、每样本 20 M reads；
   对照组 1 月建库、处理组 3 月建库；sample sheet 的 `batch` 列直接填 `instrument_model`；
   没有写深度换算的分母来源。（→ 教材 §13.7 习题 9，覆盖 13.4.1–13.4.6）
4. 某双端 Run（**设例**：1 400 000 是教学构造的数字，不是实测记录）的
   `read_count=1 553 259`（ENA 实查声明值）、`base_count=465 977 700`；实测 `_1` 文件
   1 400 000 条、`_2` 文件 1 553 259 条。四步验收里哪一步先失败、哪一步跟着失败？
   可能原因是什么？接下来该做什么、不该做什么？比较与算术入口：1 400 000 与声明值
   1 553 259 比大小、行数 = 4 × 条数（→ 教材 §13.7 习题 10，概念在
   13.4.6 与 13.5.4）

## 7. 提交物

- **对应作业**：`08_assessment/master/assignments/m01_ngs_design_assignment.md` ②，
  打包为 `学号_姓名_m01.zip`（≤ 100 MB，**不要**把下载的 FASTQ 打进包，只交 verify_log）。
- **解压后目录结构**（文件名按此命名，助教按名清点）：

  ```
  学号_姓名_m01/
  ├── design_proposal.pdf      # 六段式方案，正文 ≤ 4 页（步骤 7）
  ├── sample_sheet.tsv         # 标准 8 列，group/replicate/batch 已人工回填（步骤 5）
  ├── runinfo_ena.tsv          # 步骤 1 检索原始返回，原样保留
  ├── verify_log.txt           # 步骤 4 四步验收（含 verify_fastq 作业日志原样内容）+ 步骤 6 四个 SELFTEST 输出
  ├── scripts/
  │   └── fetch_sra.sh         # 你实际用的脚本（步骤 2 复制到个人目录的 01_fetch_sra.sh 副本，未改代码）
  └── figs/                    # 可选：fig1_batch_design.png（组 × 批次交叉表可视化，也可用表格代替）
  ```

- **评分口径**（作业 ④，总分 100 折算课程总成绩 3.5%）：完整性 50（文件齐全、六段一段不缺、
  sample sheet 八列且已回填、verify_log 四步都有原始输出）；规范性 30（平台选型两维判据 +
  放弃项；重复数依据**来源**；换算式 + 有效比例来源；交叉表每批含全部处理组或写明随机化）；
  报告质量 20（问题可证伪、元数据 ≥ 6 项、预算含失败重测预留、图表标签英文）。
- **常见失分点自查**（作业 ⑥，按出现频率排序的前几条）：把多个 Run 当多个生物学重复；
  验收没走完就当下载成功；prefetch 写爆家目录；把耗 CPU 的计算放登录节点跑（下载恰恰应在登录节点，见 §0）；`group` 留 TBD；
  重复数写「一般用 3」；深度只给数字不给换算；交叉表是对角矩阵；忽略机型混用。
- **诚实红线**：verify_log 手抄不算证据，必须原样粘贴；预期区间（未实测）不得写成实测；
  允许 AI 辅助，但方案里每个判据必须是你能当场辩护的——AI 编造 accession 或深度经验值
  按规范性扣分（作业 ③）。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章：四步验收判读 §13.4.6、失效条件 §13.5.1–13.5.4（每条「机制 → 后果 → 怎样察觉」）、习题 §13.7、四类数字口径 13.1 末段 | `textbook/chapters/ch13/manuscript.qmd` |
| 教材参照章：平台与文库选型判据（方案第 2 段）、HiFi/同聚物等错误模式口径 | `textbook/chapters/ch04/manuscript.qmd` |
| 讲义：⑤5.1–5.6 操作、⑥6.1–6.5 读设计表与验收、⑨E1–E8 排错与决策树、⑩ 练习 | `02_lectures/master/topic01_ngs_design/01_ngs_design_lecture.md` |
| 下载脚本（集群副本 `/d3/lab/ngs/master/m01/scripts/01_fetch_sra.sh`；三步：元数据 → 下载 → 打印 read 数；**第三步只打印不比对、自拉字段不含 fastq_md5**——MD5 一环用步骤 1 的 runinfo_ena.tsv 补；作业要求交它的个人副本） | `03_code/master/scripts/01_fetch_sra.sh` |
| 合成自查演示（均带 `--selftest`；集群副本在 `/d3/lab/ngs/master/m01/demos/`） | `textbook/demos/ch13_variance_partition.py`、`ch13_design_matrix_rank.py`、`ch13_truncation_confounding.py`、`ch13_batch_pca.R` |
| 预置数据与对照练习文件：`/d3/lab/ngs/master/m01/data/`（见 §2）；数据说明与登录号：LTEE 项目口径 `06_data/master/README.md`；登记 `06_data/accessions.tsv`（`PRJNA295606` L8、`SRR2584863` L9）；核验 `06_data/verify_accessions.sh` | `06_data/` |
| 环境定义（`ngs_ms_base`；sra-tools 族未钉版本） | `07_envs/conda/env_master_base.yml` |
| 作业规格（交付物、评分、失分点、提交方式） | `08_assessment/master/assignments/m01_ngs_design_assignment.md` |
