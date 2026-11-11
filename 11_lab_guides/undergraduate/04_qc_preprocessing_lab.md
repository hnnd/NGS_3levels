---
title: "实验指导 u04：质量控制与数据预处理"
level: undergraduate
topic: u04
textbook: [ch06]
lecture: ../02_lectures/undergraduate/unit04_qc_preprocessing/04_qc_preprocessing_lecture.md
env: ngs_ug_base
---

# 实验指导 u04：质量控制与数据预处理

> 上机时手边打开的这份文件。每一步回答四件事：这条命令在做什么、敲什么、
> 看到什么算对、看到什么说明错了。原理与判据在教材第 6 章（§6.4 概念、§6.5 失效条件），
> 这份指导只放操作与自查入口。三个合成演示脚本（固定种子）的数可以现跑复核；
> 真实数据的检查点没有预置区间，按本指导 §4 的对账项记录自己跑出的数，不得把任何
> 「预期区间」写成实测。本课未在集群上真实跑完公开数据全流程，标【集群未实测】的
> 步骤按预期对待。

## 0. 本实验对应什么

- **教材**：第 6 章 质量控制与预处理：哪些红灯不必处理；本实验覆盖本科学习目标
  LO06-01（判读 FastQC 模块、区分启发式警报与统计检验）、LO06-02（接头修剪、质量修剪、
  长度过滤的不同作用）、LO06-03（清洗前后对账、诊断过度修剪与旧报告）、LO06-04
  （短读长 / 长读长 / FASTA 的质控策略、名义深度与读段 N50）。
- **学时**：u04 为 4 学时线上自学单元；本实验是其上机部分，产出服务 u08 综合项目报告
  的「数据量和质量评估 / 数据预处理方法」两段（《学生实验操作手册》附报告模板）。
- **环境**：conda 环境 `ngs_ug_base`（`07_envs/conda/env_ug_base.yml`）：FastQC 0.12.1、
  MultiQC 1.14、fastp 1.3.6。
- **计算纪律**：一切计算（FastQC、fastp、MultiQC、--long 统计、合成演示）一律 `qsub`
  投递计算节点；登录节点只做下载数据、建目录、编辑文件（根 CLAUDE.md 集群事实）。

## 1. 实验前检查

- **前置自测**（讲义 ②，先确认能过）：`l0_01_linux` 第 1–5 题（通配符、重定向）、
  `l0_03_conda` 第 1–3 题（激活并验证环境）、`l0_04_formats` 第 1–7 题（FASTQ 四行
  契约、Phred 字符、FASTA 与 FASTQ 差异）。本单元即 L0 模块 `l0_05_qc` 的本科落地版，
  完成本实验加自测即视为掌握。
- **激活环境并核验工具链**：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  command -v fastqc fastp multiqc
  fastqc --version      # 期望 FastQC v0.12.1
  fastp --version       # 期望 fastp 1.3.6
  multiqc --version     # 期望 multiqc, version 1.14
  ```

  > 注：`/opt/miniconda3` 是课程集群（10.7.254.22）的专用路径；在自己的电脑或虚拟机
  > 上，换成你自己的 conda 安装路径（如 `~/miniconda3/bin/activate`）。

  这条命令在做什么：SGE 作业不继承你终端的 conda 变量，每个作业脚本开头都要自己
  激活环境（步骤 2 的模板已带）；`command -v` 三连确认工具落在
  `…/envs/ngs_ug_base/bin/`——`~/.local` 下可能有一份残缺的 MultiQC，落在那里说明
  环境不对（讲义 ⑨9.3）。
- **版本口径**：版本以 `env_ug_base.yml` 的 pin 为准（fastqc 0.12.1、multiqc 1.14、
  fastp 1.3.6，2026-11-05 起钉到集群实装）。教材 §6.8 写「fastp 未钉」早于这次钉版，
  属教材侧滞后，本指导以 yml 为准。fastp 1.3.6 在「输出目录缺失」等路径上的行为
  课程未实测（教材 §6.4.6 只实测过 1.0.1 与 0.22.0），所以本指导不写 fastp 版本
  特定断言，统一用「先建目录 + 跑完对账」验收。
- **出错信号**：`command not found` → 环境没激活，回 `l0_03_conda` 自测；
  `multiqc` 落在 `~/.local` → 讲义 ⑨9.3，重激活或用环境绝对路径。

## 2. 实验数据

双轨：**步骤相同，数据与参数不同，不要混用**。四个登录号均已登记
`06_data/accessions.tsv` L14–17（项目 `PRJEB100987`，西非 Xoo 群体 CIX4481）。

**重要：步骤 2–5 的短读长质控是实验核心，无论校内校外都用 ERR15732342**——校内轨道
独有的 `/data/lab/ngs/reads.fa` 只在步骤 6 用。上机前所有人必须先拿到这份双端短读长
（校内由教师统一下发；未下发就按校外方式自己下，见下）。

| 轨道 | 输入 | 平台 / 格式 | 登记规模 | 用途 |
|---|---|---|---|---|
| 校内（教师下发） | `/data/lab/ngs/reads.fa` | PacBio 长读长（u08 手册按 PacBio 组织下游），FASTA | 以你自己 `--long` 实测为准 | 步骤 6 长读长统计 |
| 共用（步骤 2–5 核心输入） | `ERR15732342_1/_2.fastq.gz` | Illumina 双端短读长 | 229 Mb 碱基量（双端合计）；压缩下载约 136 MB | 步骤 2–5 三件套 |
| 校外 | `ERR15732384_ont.fastq.gz` | ONT MinION 长读长，FASTQ | ≈38,078 条 / 302 Mb 碱基量；压缩约 282 MB | 步骤 6 长读长统计 |
| 对答案参照 | `genomes/CIX4481.fna`（即 `GCA_987216485`） | 完成图 | 4,768,212 bp | 名义深度分母 |

- **获取短读长（上机前必须完成，登录节点）**：
  - 校内：教师已统一下发到 `06_data/raw/undergraduate/reads/` 的，直接用（此时
    下文 `<数据目录>` = 课程仓库下的 `06_data/raw/undergraduate`）。
  - 校外 / 校内未下发：`bash 06_data/undergraduate/download_ug.sh --run --outdir
    /d3/scratch/${USER}/ngs/u04/data`。**加 `--outdir` 把数据放进自己的 scratch**——
    课程仓库是只读材料，不要往里写数据；此时 `<数据目录>` = `/d3/scratch/${USER}/ngs/u04/data`。
- **下载后自查（登录节点）**，按 README §四 口径（下文 `D=<数据目录>`）：md5 已由
  下载脚本校验；`seqkit stats $D/reads/ERR15732384_ont.fastq.gz` 期望 ≈38,078 条 /
  302 Mb（**碱基量**，不是压缩字节数）；双端 `zcat $D/reads/ERR15732342_1.fastq.gz | wc -l`
  与 `_2` 行数相等（`PAIRED_OK`，不等 = 下载不完整）。注意 `ls -l` 看到的是压缩字节
  （双端合计约 136 MB），与 229 Mb 碱基量是两列数，不要混着对（README §2.1 分开登记）。
- **两个目录约定（步骤 0 必须做，否则脚本行为跑偏）**：
  1. 短读长输入目录里**只放短读长文件**。脚本按扩展名抓输入目录下所有
     `.fq/.fastq(.gz)`（`04_run_fastqc.sh` L110），ONT 文件若混进来会被一起喂给
     FastQC 和 fastp。
  2. 双端文件名必须含 `_R1`/`_R2`。脚本按 `*_R1*` 找配对（L131–132）：**缺 R2 时
     R1 走单端分支**（L145 起，显式 `--adapter_sequence`）；**缺 R1 时孤立的 R2 被
     整个跳过**（L145 条件排除，不产出任何 clean 文件）——不是都按单端处理，运行前
     必须按对校验。下载文件的 `_1`/`_2` 命名会被当成两个单端文件分开清洗，
     `--detect_adapter_for_pe` 不会生效。步骤 0 用软链接改名，不动原始文件。
- **数据纪律**：原始数据只软链接进自己的 scratch，不要拷贝、不要放家目录
  （u08 项目说明：家目录配额小且是规范性扣分项）。

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出文件 / 检查点 / 出错信号。
> 命令里的脚本路径、参数名、输出文件名与 `03_code/undergraduate/scripts/04_run_fastqc.sh`
> 现版逐字一致（本指导修订时已逐个 grep 核对，见任务回执）。`<课程仓库路径>` 指课程
> 仓库在你机器上的位置（校内集群由教师公布），`<数据目录>` 见 §2。合成演示与真实
> 数据的投递口径见步骤 1 与步骤 2，一切计算走 qsub。

### 步骤 0：工作区与输入目录（登录节点）

- **目的**：让作业排队之前，目录、数据、命名都就位。
- **命令**：

  ```bash
  mkdir -p /d3/scratch/${USER}/ngs/u04/{fq,qc,qc_long}
  cd /d3/scratch/${USER}/ngs/u04/fq
  # 软链 + 改成 _R1/_R2 命名（脚本按 *_R1* 配对的依据，见 §2；<数据目录>见 §2 定义）
  ln -sf <数据目录>/reads/ERR15732342_1.fastq.gz ERR15732342_R1.fastq.gz
  ln -sf <数据目录>/reads/ERR15732342_2.fastq.gz ERR15732342_R2.fastq.gz
  ls -lL /d3/scratch/${USER}/ngs/u04/fq     # 链接有效、两个文件都在
  ```

  这条命令在做什么：建自己的工作目录；把双端短读长软链成 `_R1/_R2` 名——只改链接
  名、不动原始文件；`ls -lL` 解引用，确认链接指向的文件真实存在。
  （校内轨道若教师另发短读长数据，同样处理：单独目录 + `_R1/_R2` 命名。）
- **产出文件**：`fq/ERR15732342_R1.fastq.gz`、`fq/ERR15732342_R2.fastq.gz` 两个软链接。
- **检查点**：`ls -lL` 两行都显示、大小非 0。这里看到的是**压缩字节**（双端合计
  约 136 MB，README §2.1）；229 Mb 是碱基量，要用 `seqkit stats` 核（§2 自查）。
- **出错信号**：链接报红（指向不存在）→ 下载没完成或 `<数据目录>` 写错，回 §2 自查；
  只链了 R1 → 按单端处理（双端自动检测不生效，§2 约定 2）；只链了 R2 → 被脚本整个
  跳过、产不出 clean 文件，补链 R1 再跑。

### 步骤 1：判据预演——三个合成演示（登录节点）

- **目的**：不碰真实数据，先把本实验的三组判据用固定种子合成算例现跑一遍：FastQC
  阈值口径、扩增子红灯对照、fastp 阈值四档表。真实数据的检查点就是这些判据的对账项。
- **命令**（三条都在**课程仓库根目录**运行；步骤 0 已 `cd` 到 scratch，先切回来；
  三个脚本均为合成算例、固定种子）：

  ```bash
  cd <课程仓库路径>
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch06_perbase_quality.py --selftest    # 期望 SELFTEST PASS (17/17)
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch06_amplicon_redlight.py --selftest  # 期望 SELFTEST PASS (7/7)
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch06_trim_threshold.py --selftest     # 期望 SELFTEST PASS (21/21)
  ```

  集群纪律：合成演示也算计算，集群上请投递作业（激活段同步骤 2 模板；若计算节点
  缺 numpy，改在 ta / 个人电脑直接跑上面三条）：

  ```bash
  cat > u04_demo.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u04_demo
  #$ -cwd
  #$ -j y
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  cd <课程仓库路径>
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch06_perbase_quality.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch06_amplicon_redlight.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch06_trim_threshold.py --selftest
  EOF
  qsub u04_demo.job
  ```

  这条命令在做什么：`--selftest` 把各脚本与真实工具（FastQC 0.12.1 / fastp 1.0.1）
  的实跑记录逐值对算，全 PASS 说明判据口径可用。三组判据（教材 §6.4.2 / §6.4.3 /
  §6.4.5）：
  1. **per-base 阈值**：官方 WARN = 低四分位 <10 或中位 <25；ERROR = <5 或 <20；
     判定对象是碱基组（100 bp → 55 组），WARN 起于名为 82–83 的组、ERROR 起于
     96–97 的组。
  2. **重复 / 过表达边界**：跟踪上限是 100,000 个**不同序列**（满额冻结、已登记者
     继续计数），不是「文件开头 10 万条」；去重后 <70% WARN、<50% FAIL；扩增子文库
     去重后 4.0855% 判 FAIL 属设计必然（合成对照：随机文库 100.0000% PASS）。
  3. **修剪四档表**：输入 2000 条 / 200000 bp（Q20 95.00%、Q30 64.00%）；阈值 20 档
     保留 172152 bp、平均 86.08 bp、Q30 74.35%、接头 608 条·13848 bp；阈值 30 档
     Q30「变好」到 100% 但只剩 121980 bp（70.9%）、平均 60.99 bp、接头计数掉到
     4 条（顺序效应，不是接头变少）。
- **产出文件**：终端输出（无文件）。
- **检查点**：三个 SELFTEST 全 PASS（本指导修订时 2026-11-10 在 ta 现跑复核一致）。
- **出错信号**：某个 FAIL → 环境（Python / numpy）问题，别带着错误判据跑真实数据。

### 步骤 2：原始数据 FastQC（qsub）

- **目的**：体检原始短读长：每个文件一份 FastQC 报告，记录清洗前的模块状态
  （教材 §6.4.2；重点看 Per base sequence quality 与 Adapter Content）。
- **路径二选一（先读这个，避免重复投递互相冲突）**：
  - **推荐｜一键全流程**：下面作业模板末行调 `04_run_fastqc.sh`，会自动依次跑完
    [1/4] 原始 FastQC（本步）→ [2/4] fastp（步骤 3）→ [3/4] 复检（步骤 4）→
    [4/4] MultiQC（步骤 5），并自带产物对账。**全程只投递这一次**；作业结束后跳到
    步骤 3–5 的「检查点」核验产物、填 §4 表即可，**不要重复投递**。
  - **进阶｜分步投递**：想逐步体会每条命令时，**不要**投递 `04_run_fastqc.sh`；
    把步骤 2、3、4、5「分步手敲」框里的命令分别作为作业末行，依次投递 4 个作业
    （作业开头的环境激活段照抄本步模板），每个作业等前一个跑完再投。
- **命令**（一键路径的作业模板；分步路径见下方「分步手敲」）：

  ```bash
  cd /d3/scratch/${USER}/ngs/u04
  cat > u04_qc.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u04_qc
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  bash <课程仓库路径>/03_code/undergraduate/scripts/04_run_fastqc.sh \
      /d3/scratch/${USER}/ngs/u04/fq /d3/scratch/${USER}/ngs/u04/qc 4
  EOF
  qsub u04_qc.job
  qstat -u ${USER}          # qw 排队 / r 运行 / Eqw 报错
  ```

  分步手敲（讲义 ⑤5.2；把作业模板末行换成下面这条，效果同 [1/4]）：

  ```bash
  mkdir -p qc/fastqc_raw    # FastQC 不自动建目录（教材 §6.4.6 表：rc=2）
  fastqc -t 4 -o qc/fastqc_raw fq/ERR15732342_R1.fastq.gz fq/ERR15732342_R2.fastq.gz
  ```

  这条命令在做什么：`-t 4` 是文件级并行（一个线程处理一个文件），与作业申请的
  4 核对应；脚本版同款命令是 `fastqc -t "$threads" -o "$raw_dir" "${raw_files[@]}"`
  （L116）；提交后它还会继续跑 [2/4]–[4/4]（见上方「路径二选一」）。
- **产出文件**：`qc/fastqc_raw/ERR15732342_R1_fastqc.{html,zip}`、
  `ERR15732342_R2_fastqc.{html,zip}`（每输入 1 html + 1 zip）。
- **检查点**：html/zip 数 = 输入文件数（2 + 2）——先对账再判读：
  `ls qc/fastqc_raw/ | wc -l`；再逐个归档看模块状态。注意：**不能**把多个 zip 用通配符
  直接喂给 `unzip -p`——它会只认第一个 zip、把其余当成压缩包内文件名，报错退出并
  吞掉 R2 的报告（本指导修订时实测 rc=11）；必须用循环逐个解：

  ```bash
  for z in qc/fastqc_raw/*_fastqc.zip; do echo "=== $z ==="; unzip -p "$z" "*/summary.txt"; done | less
  ```

  状态本身不是结论：每个红灯按教材 §6.4.3 鉴别「数据
  的问题 vs 这类数据本来的样子」。【集群未实测：真实文件的模块状态分布】
- **出错信号**：stderr 有 `Skipping '…' which didn't exist, or couldn't be read` 而
  退出码仍是 0 → 有文件被静默跳过，`set -euo pipefail` 拦不住（教材 §6.5.2）；
  FASTA 混入报 `ID line didn't start with '@'`、rc=1（讲义 ⑨9.1）；`-o` 目录不存在
  rc=2（教材 §6.4.6 表）。三者都先停下查输入 / 目录，别往下游跑。

### 步骤 3：fastp 清洗（qsub）

- **目的**：去接头（按内容）+ 3′ 端滑窗质量修剪（按质量）+ 长度过滤
  （教材 §6.4.4 两把剪刀；PE 参数与脚本 L134–142 逐字一致）。
- **命令**（一键 = 脚本 [2/4]；分步 = 讲义 ⑤5.5，按步骤 2「进阶路径」单独投递一个作业）：

  ```bash
  mkdir -p qc/clean qc/fastp_reports    # fastp 不自动建目录；先建再跑
  fastp \
      -i fq/ERR15732342_R1.fastq.gz -I fq/ERR15732342_R2.fastq.gz \
      -o qc/clean/ERR15732342_R1.clean.fq.gz -O qc/clean/ERR15732342_R2.clean.fq.gz \
      --detect_adapter_for_pe \
      --cut_tail --cut_window_size 4 --cut_mean_quality 20 \
      --qualified_quality_phred 15 --unqualified_percent_limit 40 \
      --length_required 50 \
      --thread 4 \
      --html qc/fastp_reports/ERR15732342.fastp.html \
      --json qc/fastp_reports/ERR15732342.fastp.json
  ```

  这条命令在做什么：双端接头有三条通道（教材 §6.4.4），本命令走「额外序列自动
  检测」`--detect_adapter_for_pe`（默认通道按读对重叠剪，不需开关）；`--cut_tail`
  只在 3′ 端滑窗剪——脚本明确**不开** `--cut_front`（L119 注释：5′ 端质量通常高，
  开了误切好碱基）；窗口 4、均值 20 是课程起点不是黄金值；`--length_required 50`
  是配合 100–150 bp 短读长的课程取值（教材 §6.4.4）。若跑单端文件必须显式
  `--adapter_sequence`（脚本单端分支 L149，默认 `AGATCGGAAGAGC`，可用环境变量
  `ADAPTER_SE` 覆盖，L123）；单端不给接头序列，自动检测可能报
  `No adapter detected` 而接头全残留（教材 §6.4.5 的排查句）。
- **产出文件**：`qc/clean/ERR15732342_R1.clean.fq.gz`、`_R2.clean.fq.gz`；
  `qc/fastp_reports/ERR15732342.fastp.{html,json}`（JSON 是 MultiQC 的输入源）。
- **检查点**（真实数据**无预置区间**，按对账项记录；判据教材 §6.5.3）：
  1. JSON 里 `filtering_result` 三行（low_quality / too_many_N / too_short）一起
     看——先确定失败原因集中在哪一类，再谈参数；
  2. 两个保留率一起算：读段级 `passed_filter_reads ÷ total_reads`、碱基级
     `after_filtering.total_bases ÷ before_filtering.total_bases`；只报读段数会掩盖
     通量损失（教材 §6.4.5）；
  3. `adapter_cutting.adapter_trimmed_reads` 非零（存在接头读穿的文库）；
  4. 合成对照（步骤 1 的固定种子 demo）：阈值 20 档 Q30 74.35% 时碱基还剩
     172152 bp；把阈值抬到 30 追 Q30 的 100%，碱基只剩 70.9%——「变好看」与
     「保住数据」是两件事，别用 Q30 单项宣告成功。
- **出错信号**：接头计数 0 而复检仍报接头 → 回查接头通道（本命令是双端检测；单端
  必须给 `--adapter_sequence`）；Q30 上升但碱基级保留率大减、平均读长缩水 →
  过度修剪（教材 §6.5.3）；clean 文件 0 字节或缺失 → 输出目录问题，行为随版本
  不同（教材 §6.4.6：fastp 1.0.1 报错退出 255、0.22.0 静默 rc=0），不依赖报错——
  跑完 `ls -lh qc/clean/` 对账。

### 步骤 4：清洗后复检 FastQC（qsub）

- **目的**：验证「该消的红灯」消除，并正确看待「必然变差」的模块（教材 §6.4.3
  第五例）。
- **命令**（一键 = 脚本 [3/4]，且只核对本次应产出的文件（L160–187）；分步 = 讲义
  ⑤6）：

  ```bash
  mkdir -p qc/fastqc_clean
  fastqc -t 4 -o qc/fastqc_clean qc/clean/*.clean.fq.gz
  ```

- **产出文件**：`qc/fastqc_clean/ERR15732342_R1.clean_fastqc.{html,zip}`、
  `_R2.clean_fastqc.{html,zip}`。
- **检查点**：
  0. 终端快速查看模块状态（集群无桌面、打不开 HTML，用循环逐个解，只看本步关心的
     三行）：
     `for z in qc/fastqc_clean/*_fastqc.zip; do echo "=== $z ==="; unzip -p "$z" "*/summary.txt"; done | grep -E "Adapter|Sequence Length|Per base sequence quality"`；
  1. Adapter Content 明显下降 / 压平（前提是步骤 3 有接头修剪计数；接头残留会在
     比对时表现为软剪切，教材 §6.4.4）；
  2. Sequence Length Distribution 从 PASS 变 WARN 属**修剪预期**——「自己做出来的
     红灯」：要写进报告的是分布形状与平均读长掉了多少，不是模块颜色（教材
     §6.4.3 / §6.4.5；合成对照 l0_05 步骤 4 的 diff 四行 2c2/4c4/7c7/10c10 可复现）；
  3. Per base sequence quality 可能仍 WARN：末端质量沿位置衰减是物理事实，修剪只是
     把恶化起点挪后（步骤 1 的 demo 口径）。【集群未实测：真实文件的变化幅度】
- **出错信号**：Adapter 仍 FAIL 而命令「成功」→ 回步骤 3 查接头通道，不要开始调
  阈值；某模块从 PASS 变 WARN，先问「这是不是修剪的必然结果」再决定动不动手
  （教材 §6.5.1）。

### 步骤 5：MultiQC 汇总（qsub）

- **目的**：把 raw / clean 报告与 fastp JSON 汇成一张网页，做清洗前后对照与跨文件
  检查（MultiQC 聚合既有报告、不重新分析，教材 §6.4.6）。
- **命令**（一键 = 脚本 [4/4]；分步 = 讲义 ⑤6）：

  ```bash
  multiqc --force -o qc -n multiqc_report.html qc/fastqc_raw qc/fastqc_clean qc/fastp_reports
  ```

  脚本版只喂本次运行的 zip / json（L193–194，注释说明防旧样本混入；不加 `--force`
  会生成 `multiqc_report_1.html` 后缀副本，L190）。分步手敲版喂的是三个目录：若里面有
  旧运行的残留报告会被一起汇总——分步路径请用独立目录或先清空，别往用过的目录里重跑。
- **产出文件**：`qc/multiqc_report.html`（MultiQC 同时生成同名 `_data` 数据目录，
  正常）。
- **查看网页**：集群是纯字符终端，把 HTML 拷回本机再用浏览器打开：
  `scp <用户名>@<集群IP>:/d3/scratch/${USER}/ngs/u04/qc/multiqc_report.html ./`。
- **检查点**：报告生成且**没有** `multiqc_report_1.html` 这类带后缀副本（`--force`
  生效）；打开报告先核对里面出现的**样本名**与本次输入清单一致、时间戳是本次
  （FastQC 按文件、fastp 按样本归一化，General Statistics 行数不必等于输入文件数，
  以样本名为准，不按固定行数验收）。
- **出错信号**：`No analysis results found` → 上游其实没产出（讲义 ⑨9.3），回
  步骤 2–4 对账；发现 `_1` 副本 → 打开的是旧报告，换独立目录或先清空重跑
  （教材 §6.5.2）；`which multiqc` 落在 `~/.local` → 环境不对（讲义 ⑨9.3）。
  【集群未实测】

### 步骤 6：长读长统计 `--long`（qsub）

- **目的**：长读长 / FASTA 不跑 FastQC（按位置统计的模块对变长读段解释力有限、
  FASTA 没有质量行），改看读长分布、总产出、读段 N50、名义深度
  （教材 §6.4.7 / §6.5.4）。
- **命令**（两条轨道二选一；本步不在步骤 2 一键作业内，单独写一个作业投递——把
  选中那条作为作业末行，激活段照抄步骤 2 模板；建议与短读长作业分开投便于对账）：

  ```bash
  # 校内（FASTA；讲义 ⑤5.8 模板口径）：
  bash <课程仓库路径>/03_code/undergraduate/scripts/04_run_fastqc.sh --long /data/lab/ngs/reads.fa qc_long 4m
  # 校外（ONT FASTQ；分母必须显式给完成图全长）：
  bash <课程仓库路径>/03_code/undergraduate/scripts/04_run_fastqc.sh --long \
      <数据目录>/reads/ERR15732384_ont.fastq.gz qc_long 4768212
  ```

  这条命令在做什么：`--long` 调 `03_parse_fastq_stats.sh <文件> <gsize> 0`
  （L47–51）输出七项统计（条数 / 碱基总量 / 最短最长 / 平均 / 中位 / N50 / 估算
  深度），再画纯文本读长直方图（L63–75）。**gsize 必须显式给**：缺省 `4m`
  （= 4,000,000）会把校外数据算成 ≈75.7×（302,672,631 ÷ 4,000,000），按完成图全长
  4,768,212 bp 才是 ≈63.5×（教材 §6.4.7 算术）——分母写错深度就错。校内轨道的
  `4m` 是讲义模板设例分母；若教师公布目标基因组大小，用公布值替换并写进 §4 表。
- **产出文件**：`qc_long/longread_stats.txt`、`qc_long/read_length_hist.txt`。
  **已知限制（2026-11-10 实测复现）**：直方图由内联 `awk '/^>/ …'`（脚本 L64）生成，
  只认**未压缩 FASTA**；对 `.fastq.gz` 的 FASTQ 恒产出 **0 字节** `read_length_hist.txt`
  （`longread_stats.txt` 不受影响，校内 FASTA 轨道直方图正常）。脚本修复已报总编；
  修复前对校外 FASTQ 轨道，跑完用下面这条等价命令自己重画（写回同一文件名，再进
  步骤 7 对账）：

  ```bash
  zcat <数据目录>/reads/ERR15732384_ont.fastq.gz | awk 'NR%4==2{b=int(length($0)/1000);
      cnt[b]++; if(b>maxbin)maxbin=b} END{for(x=0;x<=maxbin;x++) if(cnt[x]>0)
      printf "%5d-%5d kb : %8d\n", x, x+1, cnt[x]}' > qc_long/read_length_hist.txt
  ```
- **检查点**：
  1. 校外轨道条数 / 总碱基 ≈38,078 / 302,672,631（ENA 门户元数据实查，README §四
     自查口径）；名义深度 ≈63.5×（按 G = 4,768,212；这是元数据换算值，不是课程
     环境实跑）；
  2. 读段 N50 与名义深度只说明「输入特征」：不保证覆盖均匀、不保证跨重复、不承诺
     闭合——闭合与错接归第 8 章组装评估（教材 §6.4.7）；
  3. 形状参照（合成、固定种子、非主线数字）：l0_05 步骤 5 的 demo 1200 条 /
     9.41 Mb / N50 10 254 bp / 最长 94 597 bp / 按 100 kb 目标 94.1×，用来看输出
     长什么样。
- **出错信号**：把 FASTA 直接喂 FastQC 报 `ID line didn't start with '@'`、rc=1
  （讲义 ⑨9.1）→ 换 `--long`；**不要**把 FASTA 转 FASTQ 绕过——转换伪造质量值，
  之后所有质量统计失义（教材 §6.5.4）；文件不存在脚本 rc=2（L42）。
- **脚本 NOTE 的处置**：脚本跑完会打印一段「长读长判读要点」。其中「长读长的错误
  是随机分布的」一句与教材口径不一致——纳米孔在同聚物与低复杂度区段有系统性偏差
  （教材 §6.4.7，第 4 章已展开），以教材为准，不要抄进报告；NOTE 里「深度一般要求
  ≥50X」「read N50 常见 10–20 kb」「rRNA 操纵子约 5 kb」等经验数没有课程复现入口，
  不是本实验检查点，判据按上面三条与本指导 §4。

### 步骤 7：产物总对账（贯穿纪律）

- **目的**：退出码只区分「显式失败」与「没被判为失败」，不能证明「做成了」
  （教材 §6.4.6）——跑完用清单对账代替信任退出码。
- **命令**（作业结束后，登录节点查看即可；每件预期产物一行，一眼数出 11 行：
  raw zip×2、clean×2、复检 zip×2、fastp html+json×2、MultiQC×1、--long×2）：

  ```bash
  ls -lh qc/fastqc_raw/*.zip qc/clean/*.fq.gz qc/fastqc_clean/*.zip \
         qc/fastp_reports/*.html qc/fastp_reports/*.json \
         qc/multiqc_report.html qc_long/longread_stats.txt qc_long/read_length_hist.txt 2>/dev/null
  ```

- **产出文件**：对账记录（写进 §4 表）。
- **检查点**（四查，教材 §6.4.6 / §6.5.2）：数量（每输入 1 份 raw 报告；每端 1 个
  clean 文件 + 1 份复检报告；每样本 1 份 fastp JSON + HTML；1 份 MultiQC；2 份
  --long 输出——直方图 0 字节的已知限制与重画命令见步骤 6，重画后再对）；非空；
  时间戳晚于输入；MultiQC 里出现的样本名与本次输入一致。脚本已替你做的：输入目录
  无可识别测序文件 rc=3（L113–114）、应产出缺失或非空校验失败 rc=4（L176–187）、
  跑完打印 `[INFO] 产物核对通过`（L187）——它不查时间戳，这条要人看；ls 列出的
  件数以本次输入清单为准，旧目录里数出来的不算。
- **出错信号**：任何一项对不上 → 停下来查，不要往下游（u05 比对）跑；数量少 → 回
  步骤 2 查 `Skipping`；时间戳旧 → 换独立目录或先清空再跑（教材 §6.5.2）。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果；「自查判据」一栏给来源。真实数据栏目填自己跑出的数，
> 不得抄讲义设例。

| 环节 | 栏目 | 单位 / 口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 0 数据自查 | md5 复核 / ONT 条数·碱基 / 双端行数相等 | — / 条·bp / — | | ONT ≈38,078 条 / 302 Mb；`PAIRED_OK`（README §四 期望值） |
| 2 raw FastQC | 各模块 PASS/WARN/FAIL（清洗前） | 状态 | | 状态不是结论，按教材 §6.4.3 鉴别（步骤 2 检查点） |
| 3 fastp | 读段数 before/after；碱基数 before/after | 条 / bp | | 两个保留率一起算（教材 §6.4.5） |
| 3 fastp | 读段级保留率 / 碱基级保留率 | % | | 合成对照（固定种子）：阈值 20 档碱基 172152/200000（demo，步骤 1） |
| 3 fastp | Q20% / Q30% before/after；平均读长 | % / bp | | 别用 Q30 单项宣告成功（教材 §6.5.3；demo 四档表） |
| 3 fastp | adapter trimmed 条数·bp；failed due to 三行 | 条·bp / 行 | | 三行先看分类，再谈参数（教材 §6.5.3）；三行分别记：low_quality=__ 条 / too_many_N=__ 条 / too_short=__ 条 |
| 4 复检 | FastQC 各模块变化（Adapter / SLD / 质量） | 状态变化 | | Adapter 应降；SLD PASS→WARN 属修剪预期（教材 §6.4.3） |
| 5 MultiQC | 样本名；有无 `_1` 后缀副本 | — / — | | 报告内样本名与本次输入一致、时间戳为本次；无 `_1`（`--force`，教材 §6.4.6；不按固定行数验收） |
| 6 --long | 条数 / 总碱基 / 读段 N50 / 名义深度（写明 gsize） | 条 / bp / bp / × | | 校外 ≈38,078 / 302,672,631（ENA 登记）；63.5× 按 G=4,768,212（教材 §6.4.7） |

## 5. 失效条件对照（教材 §6.5，本实验里在哪一步、看什么能察觉）

1. **启发式阈值把数据本来的样子判成缺陷**（§6.5.1）｜全流程，尤其步骤 4 复检读
   模块时：每个红灯先问「这是数据的问题，还是这类数据本来的样子」（教材 §6.4.3
   的五个例子）。为变绿而剪（如切转录组开头、按序列去重）会削掉真实信号；把所有
   红灯当正常会漏掉接头与污染。察觉：先识别文库类型与下游任务，再决定动不动手。
2. **输入不存在时 FastQC 跳过并返回成功**（§6.5.2）｜步骤 2 与步骤 7：stderr 找
   `Skipping`；产物数对不上输入数；MultiQC 里是旧样本 / 旧时间戳。`set -e` 拦不住
   rc=0 的跳过——对账（数量、非空、时间戳、报告记录的输入）是唯一兜底。
3. **过度修剪造成长度偏倚；别把低保留率一律归因参数**（§6.5.3）｜步骤 3 与步骤 4：
   Q30「变好看」而碱基级保留率大减、平均读长缩水；合成对照（demo 四档表）显示
   阈值 20→30 时 Q30 74.35%→100% 但碱基只剩 70.9%。先看三行 failed due to 分类，
   两个保留率一起报；低保留率也可能是真实差文库、污染或配对错误。
4. **用短读长范式做长读长或 FASTA 质控**（§6.5.4）｜步骤 6：FASTA 喂 FastQC rc=1；
   按位置质量曲线对变长读段解释力有限；名义深度 / 读段 N50 是输入特征，不承诺
   闭合（第 8 章）。FASTA 转 FASTQ「绕过」= 伪造质量值，禁止。

## 6. 思考题（指向教材 §6.7 习题，不给答案；做完回查教材 §6.9 对应题号的答案要点）

1. 一条文库分子插入片段 120 bp、读长 150 bp：R1 与 R2 各自末端读进多少 bp 接头？
   插入片段变 110 bp 呢？「接头含量 5%」为什么不能直接推出「必须修剪」？
   （§6.7 习题 2 → §6.4.4）
2. 用步骤 1 的四档表回答：阈值 20→30，读段级保留率、碱基级保留率、平均读长、
   Q30、接头修剪计数各怎么变？哪一项最容易被误读成「清洗成功」？
   （§6.7 习题 4 → §6.4.5；可重跑 demo 核对）
3. 批处理结束 MultiQC 能打开、但样本数比预期少、FastQC 网页数也比输入少：依次查
   哪三件事？为什么 `set -e` 没拦住？（§6.7 习题 5 → §6.4.6 / §6.5.2）
4. 五条长读长 10/8/6/4/2 kb：算总碱基、读段 N50、按 4 Mb 参考的名义深度；这两个
   指标为什么不能保证组装闭合？（§6.7 习题 3 → §6.4.7）
5. 一批 RNA-seq 的 Duplication Levels 报红：写两种竞争解释与各自需要的证据；为什么
   不能仅凭 FASTQ 序列判定为 PCR 重复？（§6.7 习题 6 → §6.4.3）
6. （上机面，对照讲义 ⑩ 第 3 题）在 MultiQC 总表里，你依据哪一个统计特征列裁决
   「最离群样本」？裁决后下一步是定性还是直接剔除？（→ 教材 §6.4.3 的 GC 排查
   次序：先定性，再决策）

## 7. 提交物

- **对应作业**：u04 无独立作业文件；本实验产出是 u08 综合实践项目报告的素材——
  《学生实验操作手册》附报告模板的「§2.3 数据量和质量评估」与「§2.4 数据预处理
  方法」两段草稿（仓库内 `undergrad_report_template.md` 只有 2.1/2.2，与手册附模板
  编号不一致：以手册模板为准；若按仓库模板练写，直接新建「### 2.3 数据量和质量
  评估」「### 2.4 数据预处理方法」两节即可，小节名与手册一致）。评分维度见
  `08_assessment/undergraduate/project/undergrad_project.md`。
- **两段草稿的写法**：按讲义 ⑥6.3 的句式「数据 → 数字 → 判据 → 结论 → 预处理
  决定」；每个数字带复现入口（本指导 §4 表 + fastp JSON 字段 + `--long` 输出）。
  注意：讲义 ⑥6.3 示范段的四个数字（58,432 条 / 412.66 Mb / N50 11,840 /
  103.2×）是设例，且与 ENA 登记的元数据不符，不得写进你的报告——你的数字以自己
  实测为准。§2.4 的「预处理决定」写明做了什么、没做什么、为什么（长读长不做外部
  修剪的理由按教材 §6.4.7，不写「错误随机分布所以不用管」）。
- **过程归档（本实验自己的打包，供教师检查与 u08 取材）**：按课程统一命名
  `学号_姓名_<作业号>.zip`（作业号以教师公布为准），内含：本指导 §4 结果记录表、
  `qc/` 目录（fastqc_raw、clean、fastqc_clean、fastp_reports、multiqc_report.html）、
  `qc_long/` 两份输出。这份压缩包是过程证据，**不是** u08 的正式提交物。
- **u08 正式提交物（与 `undergrad_project.md` §3 一致，另有要求）**：LMS 上传
  ① PDF 报告 `学号_姓名_NGS综合项目报告.pdf`；② 含组装基因组 `genome.fasta` 与
  注释 `.gff` 的关键结果数据包 zip。本实验的 QC 数字作为 PDF 报告 §2.3/§2.4 的
  素材进入，qc/qc_long 产物本身不进 u08 结果包。
- **诚实红线**：预期区间与合成算例不得写成实测；名义深度写明分母并标注「名义」；
  「命令成功 / 报告能打开」不得写成「质控通过」——以对账结果为准。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念 / 失效条件 / 习题） | `textbook/chapters/ch06/manuscript.qmd` §6.4 / §6.5 / §6.7 |
| 本单元讲义（⑤ 操作、⑥ 结果解读、⑨ 常见错误、⑩ 思考练习） | `02_lectures/undergraduate/unit04_qc_preprocessing/04_qc_preprocessing_lecture.md` |
| 主脚本（短读长四步 + `--long`）与被调统计脚本 | `03_code/undergraduate/scripts/04_run_fastqc.sh`、`03_parse_fastq_stats.sh`（逐步解读见 u03 实验指导） |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch06_perbase_quality.py`、`ch06_amplicon_redlight.py`、`ch06_trim_threshold.py` |
| 数据说明、下载与自查 | `06_data/undergraduate/README.md` §2.1（登记值）、§三（降采样）、§四（自查）；`06_data/undergraduate/download_ug.sh`；`06_data/accessions.tsv` L14–17 |
| 环境定义 | `07_envs/conda/env_ug_base.yml`（`ngs_ug_base`；fastqc 0.12.1、multiqc 1.14、fastp 1.3.6） |
| 作业与报告模板 | `08_assessment/undergraduate/project/undergrad_project.md`、`undergrad_report_template.md`；§2.3 / §2.4 以《学生实验操作手册》附模板为准 |
