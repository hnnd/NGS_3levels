---
title: "实验指导 u01：Linux 命令行与 Conda 环境"
level: undergraduate
topic: u01
textbook: [ch01, ch02]
lecture: ../02_lectures/undergraduate/unit01_linux_conda/01_linux_conda_lecture.md
env: ngs_ug_base
---

# 实验指导 u01：Linux 命令行与 Conda 环境

> 上机时手边打开的这份文件。每一步回答五件事：目的 / 敲什么 / 产出什么文件 / 看到什么算对
> / 看到什么说明错了。原理与判据在教材第 1 章（§1.4、§1.5）与第 2 章（§2.4、§2.5），这份指导只放操作与自查入口。
> 标「预期（未实测）」的数字是课程登记的下载完整性校验值，不是集群实测结果；
> 标「集群未实测」的步骤按预期对待。本实验引用的脚本名、参数名与输出文件名均按
> `03_code/undergraduate/scripts/` 现版逐个 grep 核对（见任务回执），不复制脚本全文。

## 0. 本实验对应什么

- **教材**：第 1 章 命令行、文本流与集群作业（§1.1–1.4，失效条件 §1.5.1/1.5.2/1.5.4）；
  第 2 章 可复现的软件环境（§2.1–2.4，失效条件 §2.5.1/2.5.3）。覆盖本科学习目标 LO01-01..04
  与 LO02-01..02（路径 / 管道 / 软链接与权限 / 最小 SGE 作业 / 四种名字 / yml 三段与激活验收）。
- **学时与定位**：课堂 Day 0「环境就绪检查」2 学时（本科大纲），当堂验收五项——集群登录、
  conda 环境激活、`qsub` 冒烟测试、数据软链接、目录结构验收。本实验就是这五项的操作手册，
  也是 u08 综合项目第一小时的全部动作（讲义 ③3.4）。
- **环境**：conda 环境 `ngs_ug_base`（`07_envs/conda/env_ug_base.yml`）。
  本实验只建/验这一个环境；其余三个本科环境（assembly / annot / phylo）按需后续再建。
- **计算纪律**：一切计算（包括序列统计，步骤 2）一律 `qsub` 投递计算节点；
  登录节点只做登录、编辑、下载、建环境这类轻量事（教材 §1.5.1）。
- **双轨说明**：实验数据有校内、校外两条轨道，步骤相同、数据源不同（§2）。首课验哪一套
  由授课教师明确（大纲 §9.5）；个人自学、补做走校外轨道。校外个人电脑没有 `/d3/scratch`
  与 SGE：项目根用脚本 `-d` 指个人目录（如 `~/ngs`），下文 `/d3/scratch/${USER}/ngs` 全部
  换成你的项目根；凡 `qsub` 的步骤直接运行作业脚本里的命令（数据量小，本机可承受）。

## 1. 实验前检查

- **前置自测**（讲义 ②，先确认能过再进机房）：
  `l0_01_linux` 自测第 1–6 题、`l0_03_conda` 自测第 1–4 题；上机考核 U01-P1/P2/P3。
- **登录集群**（以下都在【本地电脑】终端执行，切勿登录进服务器后再配置免密；讲义 ⑤步骤 0）：

  ```bash
  # 方式 A：单次密码登录
  ssh 用户名@10.7.254.22        # 首次连接核对指纹后键入完整 yes；密码输入无回显属正常

  # 方式 B：一次性配置免密登录（推荐；教材 §1.8）
  ssh-keygen -t ed25519          # 本地生成现代密钥对（一路回车即可）
  ssh-copy-id 用户名@10.7.254.22 # 最后一次输密码，向服务器植入公钥
  ssh 用户名@10.7.254.22        # 此后登录不再需要输入密码
  ```

  校外自学（个人电脑，无集群可登）：跳过本节；conda 按本机安装路径初始化，
  `hostname` 检查不适用。

- **初始化 conda 并核验**（登录节点执行；与作业脚本内的写法同源——作业不继承终端环境，
  脚本里必须重写这两行，教材 §1.5.2 / §2.4.3）：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  conda --version && hostname
  command -v samtools    # 检查点核验：打印路径应以 /d3/lab/envs/ngs_ug_base/bin/ 开头
  conda env list         # 检查点核验：查看四个本科环境的真名
  ```

  这条命令在做什么：`source` 在当前 shell 里执行 conda 的初始化脚本，下一行的
  `conda activate` 才成为可用函数；`hostname` 回答「我在哪台机器」，是排查的第一动作。
- **检查点**：终端提示符带 `(ngs_ug_base)`；`command -v samtools` 打印的路径以
  `/d3/lab/envs/ngs_ug_base/bin/` 开头；`conda env list` 里四个本科环境真名是
  `ngs_ug_base / ngs_ug_assembly / ngs_ug_annot / ngs_ug_phylo`（注意是 `ngs_ug_annot`
  不是 `ngs_ug_annotation`；环境名只由 yml 的 `name:` 决定，教材 §2.5.1）。
- **出错信号**：
  - `conda: command not found` → 忘了第一行 `source`，或登录的不是课程集群（讲义 ⑨9.3）。
  - `EnvironmentNameNotFound: Could not find conda environment: …` → 拿文件名当环境名激活
    （教材 §2.5.1）；`conda env list` 看真名再激活。
  - 提示符没有环境名前缀 → 激活没发生，不要靠提示符猜，用 `command -v` 的解析路径说话
    （提示符只是线索，教材 §2.4.3）。

## 2. 实验数据

本实验有校内、校外两条轨道，**步骤相同，数据源不同**，按教师明确的轨道执行，不要混用。

| 轨道 | 数据源 | 形态 |
|---|---|---|
| 校内（实验室集群） | `/data/lab/ngs/reads*`（PacBio 长读长 + 配套数据；脚本默认数据源 `01_setup_project_dirs.sh` L15） | 课程公共只读目录，用软链接接入，**不得复制** |
| 校外（公开数据自学） | ENA 项目 `PRJEB100987`（西非水稻白叶枯病菌 Xoo 群体），下载脚本 `bash 06_data/undergraduate/download_ug.sh --run`（课程仓库根目录运行） | 学生自下载，文件落在 `06_data/raw/undergraduate/` |

校外轨道三个主线数据的检查点数字（精确值入口：**教材第 4 章 §4.1/§4.6**，ENA `read_run`
元数据 2026-11-03 实查、正文列出算式；`06_data/undergraduate/README.md` §2.1 只有约数、
§四为「期望」；均为**预期值，用于下载完整性校验**，集群实跑标「集群未实测」）：

| 登录号 | 平台 | 预期体量 | 本实验用途 |
|---|---|---|---|
| `ERR15732384` | ONT 长读长 | ≈ 38,078 条 / 302,672,631 bp（≈63×，可降采样至 40×） | 步骤 2 序列统计 |
| `ERR15732342` | Illumina 双端短读长 | 双端 `zcat … \| wc -l` 行数相等（`PAIRED_OK`）；合计 228,911,011 bp（≈48×） | 数据完整性自查 |
| `GCA_987216485` | 作者发表完成图（CIX4481） | 4,768,212 bp | 深度估算的基因组大小 `-g` 分母 |

- 登录号均已登记 `06_data/accessions.tsv` L14–17 ✓。
- **手算检查点**（输入全列出，可用计算器复核；教材 §1.4.5 深度口径；精确值见上）：
  ONT 名义深度 = 302,672,631 ÷ 4,768,212 = 63.477… ≈ **63.5 X**；Illumina = 228,911,011 ÷
  4,768,212 = 48.007… ≈ **48.0 X**（与 README「≈63× / ≈48×」约数一致；名义深度 ≠ 有效深度）。
- **合成演示数据**（课程仓库根目录运行，带 `--selftest`，rc=0）：`python3
  textbook/demos/ch01_symlink_checks.py --selftest` 复现断链三件套与字节数
  （活链接 8 B、断链 19 B、真实文件 15 B，教材 §1.4.6 表）。
- 校内轨道无公开检查点数值，用步骤 2 的自洽判据（条数 × 平均 ≈ 总碱基）验收。

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出文件 / 检查点 / 出错信号。
> **在哪敲命令**：SSH 登录后当前目录是家目录；scratch 路径一律以 `/d3/scratch/${USER}/ngs`
> 为根。`<课程仓库路径>` 用课程仓库在本机的实际位置代入：校内集群上用教师公布的共享路径
> （例如 `<课程仓库路径>`，以课堂公布为准）；自行 git clone 的，
> 为你存放仓库的目录（如 `~/NGS_3Levels`）。可先 `cd` 进仓库跑 `pwd` 确认。
> `01_qsub_hello.sh` 带 `#$ -cwd`：日志落在**投递时所在的目录**，先 `cd` 到个人
> `scripts/` 再投递；`${USER}` 不要替换成具体用户名（教材 §1.4.2）。

### 步骤 1：目录树与数据接入（`01_setup_project_dirs.sh`）

- **目的**：一键建立六个分析模块目录 + 五个辅助目录项，并把公共数据用软链接接入 `fq/`
  （零拷贝，不占个人配额；教材 §1.4.6）。
- **命令**（登录节点执行；校内轨道用默认值；校外轨道用 `-d` 指个人项目根、`-s` 指下载目录）：

  ```bash
  # 校内轨道
  bash <课程仓库路径>/03_code/undergraduate/scripts/01_setup_project_dirs.sh
  # 校外轨道（集群上省略 -d；个人电脑把 -d 指到 ~/ngs 等个人目录）
  bash <课程仓库路径>/03_code/undergraduate/scripts/01_setup_project_dirs.sh \
      -s <课程仓库路径>/06_data/raw/undergraduate/reads
  # 已知限制：脚本通配式硬编码 reads*（L16），匹配不到 ERR 开头的下载文件，
  # 校外轨道显示「本次新建软链接 0 个」属预期——补跑这条手动批量链接：
  ln -s <课程仓库路径>/06_data/raw/undergraduate/reads/ERR*.fastq.gz /d3/scratch/${USER}/ngs/fq/
  # 个人电脑把目标目录换成你的 -d 项目根下的 fq/；参数均可查：bash …/01_setup_project_dirs.sh -h
  ```

  这条命令在做什么：`-d` 项目根（默认 `/d3/scratch/${USER}/ngs`，L14）、`-s` 数据源（默认
  `/data/lab/ngs`，L15）、`-h` 帮助（L32–40）；六模块数组 `survey assem anno ident phylo
  pangenome`（L43）与五辅助项 `fq scripts logs results/figures results/tables`（L45）用
  `mkdir -p` 幂等创建——`results/figures`、`results/tables` 共用顶层 `results/`，故
  **顶层 10 个目录**（配置路径 11 条，别按 11 找）；`link_data` 对 `${DATA_SRC}/reads*`
  逐文件 `ln -s`（L65–71，已存在则跳过 L68–70），末尾打印「本次新建软链接 N 个」（L76）。
  磁盘余量按 `df -h` 自查：确认目标盘剩余空间充足（本实验产物为文本与日志、百 MB 量级；
  接近写满时写入会中途失败且不一定报错，教材 §1.5.4）。
- **产出文件**：项目根（默认 `/d3/scratch/${USER}/ngs`）下顶层 10 个目录，`results/` 内含
  `figures/`、`tables/` 两个子目录；`fq/` 下指向数据源的软链接。
- **检查点**：
  1. 脚本末段验收区打印的目录树 `ls -1` 顶层共 **10** 项（6 模块 + fq/scripts/logs/results），
     `ls -1 results` 另见 figures、tables 两个子目录；
  2. 重复执行不报错（`mkdir -p` 幂等，再跑一遍是设计允许的行为）；
  3. 「本次新建软链接 N 个」：第一次 N≥1；**N=0 且 `fq/` 为空** = 数据源缺失或通配未命中——
     校外轨即 ERR 通配未命中，按上面手动 `ln -s` 补链再查；数据源不存在时脚本 L58–61
     打印「跳过」并以 rc=0 继续（设计性跳过不是成功）；
  4. `ls -lh fq` 行首为 `l`（link），`head -n 2 fq/<真实文件名>` 能读出内容、
     `ls -lL` 返回 0（跟随测试通过）。真实文件名校外形如 `ERR15732384_ont.fastq.gz`、
     校内形如 `reads.fa`——先用 `ls -lh fq` 看清再敲。
- **出错信号**：
  - `No such file or directory` 或链接条目显红 → 断链：跑跟随动作三件套定位——
    `cat` 返回 1 并报 `No such file or directory`、`ls -lL` 返回非零、`[[ -f ]]` 为假
    （教材 §1.5.4；本机可复现：`python3 textbook/demos/ch01_symlink_checks.py --selftest`）。
    修复 = 回到数据源重建链接，**不要用 cp 绕过**（把配额问题留给下一次）。
  - `ln: failed to create symbolic link … File exists` → 同名对象已存在（讲义 ⑨9.2）。
    **先 `ls -l` 看清它是旧链接还是真实文件**：确认是废弃旧链接才 `rm` 后重建
    （`ln -s` 本身不覆盖已有对象；不要用 `ln -sf`，`-f` 会静默移除同名真实文件）。
  - `df -h` 显示磁盘接近写满 → 大文件写入可能中途失败且不一定报错；先清理
    （`du -sh /d3/scratch/${USER}/ngs/* | sort -h` 找膨胀源），再开工（教材 §1.5.4）。
- **执行位置**：目录创建与软链接是轻量操作，登录节点执行即可。

### 步骤 2：文本统计（管道与重定向 + `01_seq_stats.sh`）

- **目的**：用一行命令看清「管道把上一段的输出接下一段的输入、重定向把流写进文件」
  （教材 §1.4.4/§1.4.5），再用封装脚本产出可填进报告的两类数字（条数、总碱基、估算深度）。
- **命令**（先看头部：登录节点秒级；一切计数与完整统计走 `qsub`，见下方作业模板）：

  ```bash
  cd /d3/scratch/${USER}/ngs/fq
  ls -lh                                     # 先看清真实文件名；.gz 用 zcat，取够行数即停
  head -n 8 reads.fa                         # 校内轨道（文件名通常为 reads.fa）
  zcat ERR15732384_ont.fastq.gz | head -n 8  # 校外轨道：'>'=FASTA，'@'=FASTQ（脚本判据同源）
  # 管道一行（只对前 400 行演示，登录节点秒级）：数出前 100 条的序列行
  zcat ERR15732384_ont.fastq.gz | head -n 400 | awk 'NR % 4 == 2' | wc -l
  ```

  这条命令在做什么：`01_seq_stats.sh`（下方 qsub 里调用）用 `-g` 指定基因组大小 bp
  （默认 4,000,000，L14；`getopts :g:h` 在 L29–31），按扩展名选读取方式（`.gz` 用
  `zcat`，L53），按首字符分 FASTA/FASTQ 分支：FASTQ 只认行号 `NR % 4 == 2` 的序列行
  （L103），不检查 `+` 行与质量行；估算深度按 `%.1f` 一位小数格式化（L97/L113）。
  **它不计算 N50**（N50 在 u06 由 QUAST 给出，讲义 ⑤步骤 3）。

- **大文件统计与计数走 qsub**（ONT 压缩包 282 MB；一切计算投递计算节点，登录节点只编辑/下载）：

  ```bash
  cd /d3/scratch/${USER}/ngs/scripts
  cat > u01_stats.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u01_stats
  #$ -cwd
  #$ -j y
  #$ -pe smp 1
  # —— 校外轨道（-g 用完成图 GCA_987216485 的长度 4,768,212）：
  bash <课程仓库路径>/03_code/undergraduate/scripts/01_seq_stats.sh \
      -g 4768212 /d3/scratch/${USER}/ngs/fq/ERR15732384_ont.fastq.gz
  # —— 校内轨道（-g 按教师/手册指定值；未指定用默认 4000000 并注明）：
  # bash <课程仓库路径>/03_code/undergraduate/scripts/01_seq_stats.sh -g 4000000 /d3/scratch/${USER}/ngs/fq/reads.fa
  # —— 校外完整性自查（README §四）：zcat fq/ERR15732342_1.fastq.gz | wc -l 与 _2 行数相等
  EOF
  qsub u01_stats.job
  ```

- **产出文件**：屏幕/日志输出一份统计块（格式 / 条数 / 总碱基 / 平均 / 最长最短 / 估算深度）；
  作业日志 `u01_stats.o<作业号>`（落在 `scripts/`）。
- **检查点**（校外轨道 ONT 文件，预期值用于校验，集群未实测）：
  1. read 数 ≈ 38,078、总碱基 ≈ 302,672,631 bp、估算深度 ≈ 63.5 X
     （精确值入口：教材 ch04 §4.1，ENA 元数据实查；与 §2 对账）；
  2. **自洽判据**（不依赖任何外部数字，校内轨道也适用）：条数 × 平均读长 ≈ 总碱基数；
     最长 ≥ 平均（教材 §1.4.5）；
  3. `-g` 必须给对：漏写 `-g` 会用默认 4,000,000，同一文件深度显示 ≈ 75.7 X
     （302,672,631 ÷ 4,000,000 = 75.668…，手算可复核）——分母错了结果照样打印，
     这就是「跑完 ≠ 做对」的实例。
- **出错信号**：
  - `错误：文件不存在或是断链的软链接` + rc=1 → 脚本的 `[[ -f ]]` 守门拦下了断链
    （L44–48；教材 §1.5.4）。回步骤 1 修链接。
  - `无法识别格式：首字符既不是 '>' 也不是 '@'` + rc=1 → 先看 `head -n 4` 文件长什么样。
  - **静默家族（不报错但结果不可信，教材 §1.4.5 设例）**：FASTQ 截断到 14 行仍得
    「4 条 40 bp」（第 14 行被当序列行）、截断到 13 行得「3 条 30 bp」，rc=0 都不
    报错——首字符判断只查首行，中途截断查不出来。最终判据是产物自洽 + 下载完整性
    自查（§2 的 `PAIRED_OK` 与登记值对账）。
  - 深度显示 `0.0 X` → 真实值未必是零，只是按一位小数舍入（教材 §1.4.5 设例：
    40 ÷ 4,000,000 = 1×10⁻⁵ 显示 `0.0 X`）；判断是否「无数据」要回原始计数。
- **执行位置**：`ls`/`head`/`less` 这类秒级查看与「前 400 行」管道演示可在登录节点；
  对整套数据的计数（`grep -c`、`zcat … | wc -l`、awk 统计）与 `01_seq_stats.sh`
  一律 `qsub`（上面模板）——不要在登录节点对 282 MB 的 ONT 文件跑完整统计。

### 步骤 3：环境创建与四步验收（`ngs_ug_base`）

- **目的**：拿到一个「定位、版本、导入、最小真实命令」四层证据齐全的环境（教材 §2.4.8），
  并导出 `--no-builds` 的 `environment.yml` 作为可复现凭证（教材 §2.4.7）。
- **命令**（建环境是联网操作，只在登录节点做；集群 `/d3/lab/envs` 已实装四个本科环境，
  课程记录——先核验，确实缺了再自建）：

  ```bash
  # ① 核验已有环境（课程集群应为已实装）
  conda env list | grep ngs_ug
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  # ② 自建（校外/本机练习时才需要；集群上缺环境找教师，不要在登录节点重复建）
  conda env create -f <课程仓库路径>/07_envs/conda/env_ug_base.yml
  ```

  这条命令在做什么：`conda env create -f` 读 yml 的 `name:` 段命名（默认入口不从文件名
  推导，教材 §2.4.2）；课程四份本科 yml 渠道顺序一致（conda-forge → bioconda → defaults，
  历史配置保留）且未 pin Python 版本——**不要声称本科环境是某个 Python 版本**
  （四份 yml 均无 `python=` 行，同节）。
- **四步验收**（每步都要过；只查 `command -v` 不算验收，「找得到」≠「跑得起来」，教材 §2.4.8）：

  ```bash
  # ① 定位：解析路径以环境前缀开头（which 与 command -v 只回答这一个问题）
  command -v samtools
  # ② 版本：能启动并打印（入口：env_ug_base.yml 的 pin）
  fastqc --version      # 期望 0.12.1
  multiqc --version     # 期望 1.14
  samtools --version    # 期望 1.17（头一行）
  # ③ 启动期自检：perl/Python 工具能越过启动阶段（两类典型启动期失败见出错信号）
  fastqc --help >/dev/null && echo FASTQC_START_OK
  # ④ 最小真实命令 + 产物校验：真跑一个小任务，看退出状态与产物
  # 先截取微型测试文件（只取前 400 行 = 100 条，登录节点秒级；校内轨道若只有
  # FASTA 文件，向教师索取小样本或用校外 ERR 短读长文件代替）：
  cd /d3/scratch/${USER}/ngs/logs
  zcat /d3/scratch/${USER}/ngs/fq/ERR15732342_1.fastq.gz | head -n 400 > mini_test.fq
  # 真跑 FastQC 仍走 qsub（一切计算投递计算节点；微型文件秒级跑完）：
  cd /d3/scratch/${USER}/ngs/scripts
  cat > u01_fastqc.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u01_fastqc
  #$ -cwd
  #$ -j y
  #$ -pe smp 1
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  cd /d3/scratch/${USER}/ngs/logs
  fastqc --extract -o . mini_test.fq
  EOF
  qsub u01_fastqc.job
  ls -l /d3/scratch/${USER}/ngs/logs/mini_test_fastqc.html   # 日志在 scripts/，产物在 logs/
  ```

  四步缺一则环境不算就绪——课程的环境准备脚本只对每个工具做 `conda run -n 环境 which 工具`，
  缺工具时脚本末尾的 `echo` 照样让整体 rc=0（「打印了失败，脚本却成功」，教材 §2.4.8
  三行 Shell 可现场核对），所以冒烟脚本的通过**不能替代**上面四步。
- **产出文件**：激活成功的会话；`fastqc` 产出 `*_fastqc.html`（+ `--extract` 时的
  `*_fastqc/` 目录）；下面导出的 `environment.yml`。
- **检查点**：
  1. ①打印 `/d3/lab/envs/ngs_ug_base/bin/samtools`（校内集群实装路径，课程记录；
     自建环境则为你的 conda envs 目录）；
  2. ②三个版本号与 yml pin 一致（0.12.1 / 1.14 / 1.17；版本以 yml 为准，教材 §2.3）；
  3. ④产物文件存在、非零字节、能用浏览器/编辑器打开（本步即 logs/ 下
     `mini_test_fastqc.html`）。
- **出错信号**：
  - `EnvironmentNameNotFound: Could not find conda environment: ngs_ug_base` → 环境没建或
    名字不对；`conda env list` 看真名（教材 §2.5.1）。
  - `Solving environment` 长时间不出结果 → 先读冲突输出：报出具体包名+版本对才是真互斥
    （按冲突对处置）；没有互斥条目只是不收敛，先试有依据的 pin（如 `python=`），拆环境是
    最后手段（教材 §2.4.6/§2.5.4）。课程集群 `/opt/miniconda3` 为 23.3.1（早于 23.10
    libmamba 默认切换），求解慢属正常，别拿新版本的默认行为套它。
  - `ModuleNotFoundError: No module named 'pkg_resources'`（multiqc 等 2023–2024 年的
    Python 工具）→ setuptools 82.0.0（2026-02-08）删除了该模块；课程 yml 统一钉
    `setuptools<81`（教材 §2.4.8）。你新建环境时若复现此错，先核对自己手里的 yml 是不是课程版。
  - `Can't locate warnings.pm: /root/perl5/lib/perl5/warnings.pm: Permission denied` →
    外部 `PERL5LIB` 抢在环境内 perl 之前找模块；课程 16 个环境已装进入隔离/退出还原的
    激活钩子（课程记录），自建环境遇到就 `unset PERL5LIB PERL_LOCAL_LIB_ROOT
    PERL_MB_OPT PERL_MM_OPT` 再跑（教材 §2.5.3）。
  - `command -v samtools` 指向 `/usr/bin/samtools` 而提示符显示已激活 → 「伪激活」三因：
    环境没装该包 / PATH 更前面有别的来源 / 激活脚本被后续 PATH 赋值盖掉（教材 §2.4.3）；
    用 `conda list samtools` 与打印 `PATH` 逐段核对缩小到一条。
- **收尾导出**（作业与报告附录用这份，教材 §2.4.7）：

  ```bash
  conda env export --no-builds > /d3/scratch/${USER}/ngs/environment.yml
  grep -m1 '^name:' /d3/scratch/${USER}/ngs/environment.yml   # 期望 name: ngs_ug_base
  ```

- **执行位置**：全部在登录节点（建环境/导出不占计算资源）。

### 步骤 4：SGE 冒烟作业（`01_qsub_hello.sh`）

- **目的**：提交一个最小作业，验证「登录 → 排队 → 计算节点运行 → 日志落盘」全链路，
  并拿到四件证据：运行节点、分配核数、工具清单、结束时间（教材 §1.4.8）。
- **命令**（先 cd 到个人 scripts/ 再投递，`#$ -cwd` 让日志落在投递目录）：

  ```bash
  cd /d3/scratch/${USER}/ngs/scripts
  qsub <课程仓库路径>/03_code/undergraduate/scripts/01_qsub_hello.sh
  # 屏幕应立即返回：Your job <作业号> ("qsub_hello") has been submitted
  qstat -u ${USER}          # qw=排队 r=运行；跑完即从列表消失
  # 作业结束后看日志（作业号以屏幕回显为准）
  less qsub_hello.o<作业号>   # 查看后按键盘 q 键退出，回到命令行
  ```

  这条命令在做什么：脚本头五行 `#$` 指令（`-S /bin/bash`、`-N qsub_hello`、`-cwd`、
  `-j y`、`-pe smp 1`，L13–17）由调度器按行首解析；正文先打印作业身份（L27–32），再显式
  `source` + `conda activate` 重建环境（默认目标 `ngs_ug_base`，可第一参数覆盖，
  L22/L37–42），再对 `samtools fastqc R jellyfish flye prokka` 逐个 `command -v`
  清单检查（L49–56），末尾打印「结束时间」（L63）与磁盘余量。
- **产出文件**：`qsub_hello.o<作业号>`（在 `scripts/` 下，`#$ -j y` 合并 stderr）。
- **检查点**（逐条对应脚本的打印行）：
  1. **「运行节点」那一行**（L29）是计算节点名——它不是日志物理第一行（前面还有标题、
     作业号、作业名三行，L24–28）；要拿它当证据，须与作业号、`qstat` 记录交叉核对
     （教材 §1.4.8 证据 1）；
  2. 「分配核数」= 1（来自 `-pe smp 1`，即槽位 `NSLOTS`；槽位≠内存，教材 §1.3）；
  3. 工具清单里 `samtools / fastqc / R` 显示 OK，且 OK 行的路径以
     `/d3/lab/envs/ngs_ug_base/` 开头——`command -v` 只回答「找得到」，
     路径不对也可能是 PATH 里别的来源（教材 §2.4.3）；`jellyfish / flye / prokka`
     显示「不在当前环境」**属正常**——那是跨环境清单，它们分属 assembly / annot 环境
     （脚本 L49–56）；
  4. 日志存在「结束时间」行（L63）= 作业完整走到脚本末尾（证据 2；该行后面脚本
     还有一行说明文字，它不是日志物理末行）。
- **出错信号**：
  - `qstat` 恒为 `Eqw` → 作业初始化即失败且不会自愈：`qstat -j <作业号>` 读 error reason
    （常见：`#$ -cwd` 目录不可达、脚本带 Windows 行尾 `$'\r'`），改完 `qdel <作业号>`
    删掉重提（教材 §1.4.8；行尾问题用 `dos2unix` 或 `sed -i 's/\r$//'` 修）。
  - 日志只有一行 `command not found`、作业秒退 → 作业里环境没激活或拿错环境
    （教材 §1.5.2）：脚本内的两行 `source` + `conda activate` 缺一不可。
  - 「运行节点」是登录节点名 → 你用 `bash` 直接跑了脚本、根本没提交；改 `qsub`
    （教材 §1.5.1）。screen/tmux 里跑也一样在登录节点，会话保活不换机器。
  - 日志只有一行 `Killed` → 进程被不可捕获信号终止，来源至少三种（节点物理内存+
    swap 耗尽、突破作业内存限额、跑在登录节点被管理终止）；第一动作是核对内存申请、
    数据规模、运行节点与调度记账，**槽位≠内存，不要盲目加槽位**（教材 §1.5.5，硕士层）。
  - 有开始时间无结束时间 → 作业没走到脚本末尾：先查磁盘空间（`df -h`）与 `qstat -j`，
    再怀疑参数（教材 §1.4.8 证据 2）。
- **集群实测状态**：`01_qsub_hello.sh` 有课程记录（计算节点 cu02 实测 rc=0，根集群记录）；
  本指导编写未复跑，标「集群未实测」。`01_setup_project_dirs.sh` / `01_seq_stats.sh`
  无集群实测记录，相关检查点按「预期 + 自洽判据」对待。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果。就绪检查五项当堂验收时向教师出示本表。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 1 前检查 | conda 版本 / 主机名 | 文本 | | 激活成功；`command -v samtools` 以环境前缀开头（教材 §2.4.3） |
| 1 目录树 | 顶层目录项数 / 新建软链接 N | 个 | | 顶层 10 项，results/ 下另有 figures、tables 2 项（脚本 L43/L45）；首次 N≥1，N=0 且 fq/ 空 = 数据源未命中，校外轨补手动 ln -s ERR*.fastq.gz（脚本 L76） |
| 1 数据接入 | 链接跟随测试 `ls -lL` | rc | | 0 = 活链接（教材 §1.4.6） |
| 2 统计 | 条数 / 总碱基 / 平均 / 最长 / 深度 | 条 / bp / bp / bp / X | | 条数×平均≈总碱基；最长≥平均（教材 §1.4.5）；校外 ONT 预期 ≈38,078 条 / 302,672,631 bp / 63.5 X（精确值入口：教材 ch04 §4.1 ENA 实查；集群未实测） |
| 2 统计 | `-g` 取值 | bp | | 校外：完成图 4,768,212（GCA_987216485，教材 ch04 §4.1）；校内：按教师/手册指定值填，未指定按默认 4,000,000 并注明；漏给会算出 ≈75.7 X（手算） |
| 3 环境 | fastqc / multiqc / samtools 版本 | x.y.z | | 0.12.1 / 1.14 / 1.17（env_ug_base.yml pin） |
| 3 环境 | 最小真实命令产物 | 存在+非空 | | `*_fastqc.html` 存在、非零字节（教材 §2.4.8 四层判据） |
| 3 环境 | 导出文件 `name:` | 文本 | | `ngs_ug_base`（--no-builds 导出，教材 §2.4.7） |
| 4 冒烟 | 运行节点 / 分配核数 / 结束时间行 | 文本 / 个 / 有·无 | | 计算节点名（非物理首行，交叉核对）；1；有（脚本 L29/L33/L63） |
| 4 冒烟 | 工具清单 samtools/fastqc/R | OK 计数 | | 3 项 OK 且路径以 /d3/lab/envs/ngs_ug_base/ 开头；jellyfish/flye/prokka 不在 base 属正常 |

## 5. 失效条件对照（教材 §1.5 / §2.5，本实验里在哪一步察觉）

1. **在登录节点跑计算（§1.5.1）**｜察觉：步骤 4——日志「运行节点」是登录节点名 = 你
   `bash` 直跑了脚本；步骤 2——对大文件直跑统计而不用 `qsub`，全班终端变卡是线索。
   三线索互核：运行节点行、日志有无结束行、`qstat` 记录。
2. **作业环境与交互终端不同（§1.5.2）**｜察觉：步骤 4——作业秒退、日志一行
   `command not found`，或更隐蔽地命中系统旧版工具跑出「能看但不对」的结果。看日志
   打印的环境名与工具绝对路径，修复 = 脚本内显式两行 `source` + `conda activate`。
3. **复制代替软链接、源移动后断链（§1.5.4）**｜察觉：步骤 1——`fq/` 链接 `ls` 看得见、
   `cat` 报 `No such file or directory`、`ls -lL` 非零；复制路线则先撞 `Disk quota exceeded`。
   空间用 `du`/`df` 查（配额上限以集群说明为准，教材未实测）；修复 = 回数据源重建链接，不要用 cp 绕过。
4. **环境名只由 yml `name:` 决定（§2.5.1）**｜察觉：步骤 1/3——按文件名激活报
   `EnvironmentNameNotFound: Could not find conda environment: ngs_ug_annotation`；
   `conda env list` 对真名 `ngs_ug_annot`。
5. **装上了却一跑就炸：`PERL5LIB` / `pkg_resources`（§2.5.3）**｜察觉：步骤 3 四步验收的
   第②③步——`command -v` 与 `conda list` 全过，启动即报 `Can't locate warnings.pm …
   Permission denied` 或 `ModuleNotFoundError: No module named 'pkg_resources'`。验收必须推到
   版本、导入、最小真实命令与退出状态；作业脚本显式 `exit 1`，别让末尾 `echo` 兜住失败。
6. **看到 `Killed` 就加槽位（§1.5.5，硕士层备查）**｜察觉：步骤 4——日志只有一行
   `Killed`。先核对内存申请 / 数据规模 / 运行节点与调度记账，区分三种来源后再处置；
   课程组装脚本的内存按槽位计量（`h_vmem` 每 slot 上限），加槽位可能更早撞限。
   证据指向缺 CPU 时才加槽位，并让线程数与槽位数一致。

## 6. 思考题（指向教材习题，不给答案）

1. 当前目录在 `…/ngs/survey`，要读 `…/ngs/fq/reads.fa`：写出两种相对路径与一种绝对路径；
   把写死用户名的脚本发给同学，哪种会失败、为什么？（教材 §1.7 习题 1）
2. 一个 FASTQ 16 行、每条四行、序列行 10 bp：读段数、总碱基、默认 `-g` 下的深度各是多少？
   只剩 13 行 / 14 行时哪项变、脚本报不报错？（§1.7 习题 2 → §1.4.5 设例）
3. `ln -s` 接入的链接自身「大小」由什么决定？源被改名后 `cat` / `ls -lL` / `[[ -f ]]`
   各给出什么？（§1.7 习题 3 → §1.4.6）
4. 作业 `qstat` 显示 `Eqw`，与日志「运行节点」是登录节点名，各是什么问题、下一步查什么？
   （§1.7 习题 5 → §1.4.8 / §1.5.1）
5. `env_ug_annotation.yml` 的环境名是什么？按文件名激活会发生什么、哪条命令立刻给出真名？
   （教材 §2.7 习题 1 → §2.4.1 / §2.5.1）
6. 激活后 `command -v samtools` 指向 `/usr/bin/samtools`，提示符却显示已在目标环境：
   列出三种可能原因与对应的缩小范围的命令。（§2.7 习题 3 → §2.4.3）

## 7. 提交物

- **对应作业**：u01 无独立作业文件（`08_assessment/undergraduate` 下无 u01 条目），按
  本科大纲「环境就绪检查」五项当堂验收：集群登录、conda 环境激活、`qsub` 冒烟测试、
  数据软链接、目录结构验收。
- **当堂出示**：§4 结果记录表（填好检查点列）+ 冒烟日志 `qsub_hello.o<作业号>`。
- **课后保留**（讲义 ②：作为后续单元的检查材料；u08 报告模板届时复用）：个人目录树
  `/d3/scratch/${USER}/ngs/`、`environment.yml`（`--no-builds` 导出）、冒烟日志、排错记录
  （每个出错信号一行：现象 → 你的处置 → 结果）。**打包约定**：后续单元有独立作业时，统一按
  `学号_姓名_<作业号>.zip` 命名（课程作业规格既定格式）；u01 本身只留档不上传。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念 / 失效条件 / 习题） | `textbook/chapters/ch01/manuscript.qmd` §1.4 / §1.5 / §1.7；`textbook/chapters/ch02/manuscript.qmd` §2.4 / §2.5 / §2.7 |
| 本单元讲义（原理细节、⑥ 正常/异常态、⑨ 错误排查） | `02_lectures/undergraduate/unit01_linux_conda/01_linux_conda_lecture.md` |
| 本实验三个脚本 | `03_code/undergraduate/scripts/01_setup_project_dirs.sh`、`01_seq_stats.sh`、`01_qsub_hello.sh`（只读引用，不改原文件） |
| 合成自查演示（课程仓库根目录运行，带 `--selftest`） | `textbook/demos/ch01_symlink_checks.py`、`textbook/demos/ch01_pipe_exit_codes.py`（后者为硕士层管道状态对照，本科了解结论即可） |
| 数据说明、下载与预期区间 | `06_data/undergraduate/README.md` §2.1（登记值）、§三（降采样）、§四（自查）；`06_data/undergraduate/download_ug.sh`；登录号登记 `06_data/accessions.tsv` |
| 环境定义 | `07_envs/conda/env_ug_base.yml`（`ngs_ug_base`）；四环境分工见讲义 ⑤5.2 |
| 作业与报告模板（u08 复用） | `08_assessment/undergraduate/project/undergrad_project.md`、`undergrad_report_template.md` |
