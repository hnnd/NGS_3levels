---
title: "实验指导 u06：基因组组装原理与质量评估"
level: undergraduate
topic: u06
textbook: [ch08]
lecture: ../02_lectures/undergraduate/unit06_assembly_basics/06_assembly_basics_lecture.md
env: ngs_ug_assembly
---

# 实验指导 u06：基因组组装原理与质量评估

> 上机时手边打开的这份文件。每一步都回答四件事：这条命令在做什么、敲什么、
> 看到什么算对、看到什么说明错了。原理与判据在教材第 8 章（§8.4 概念、§8.5 失效条件），
> 这份指导只放操作与自查入口。所有标「预期区间（未实测）」的数字都是课程写下的自查范围，
> 不是实测结果；本课没有在集群上真实跑完过全流程，标「集群未实测」的步骤同样按预期对待。

## 0. 本实验对应什么

- **教材**：第 8 章 基因组组装与质量评估；本实验覆盖本科学习目标 LO08-01（k-mer 频谱）、
  LO08-02（OLC/DBG 与 k−1 边界）、LO08-03（N50/L50 与错接反例）、LO08-04（QUAST/BUSCO/环状标记证据链）。
- **学时**：u06 为 4 学时线上自学单元；本实验是其上机部分，也是 u08 综合项目「模块 1 勘测 +
  模块 2 组装」的完整流程（讲义 ⑫）。
- **环境**：conda 环境 `ngs_ug_assembly`（`07_envs/conda/env_ug_assembly.yml`）。
  注意 Canu、Flye、QUAST、BUSCO 在该 yml 里**未钉版本**，不要声称"某版本行为已实测"（教材 8.4.5）。
- **计算纪律**：一切计算一律 `qsub` 投递计算节点——包括 GenomeScope 拟合（步骤 2）和
  有参考 QUAST（步骤 5），本指导给最小作业脚本写法；只有下载数据、激活环境、
  `wget` 这类轻量操作在登录节点做。在登录节点直接跑组装会被 OOM 杀掉
  （典型指纹 `Killed`，讲义 E1）。

## 1. 实验前检查

- **前置模块**（讲义 ②，先确认自测能过）：
  `l0_01_linux` Q06/Q09（qsub 与软链接）、`l0_03_conda` Q02/Q07（作业内激活环境）、
  `l0_04_formats` Q01/Q03（FASTQ/FASTA 与短/长读长分工）。统计素养依赖 `l0_06_stats`（讲义 ⑦）。
- **激活环境并核验工具链**（与 `06_kmer_survey.sh` L29–30 同一写法）：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_assembly
  command -v jellyfish canu flye quast.py busco
  ```

  这条命令在做什么：SGE 作业不继承你终端里的 conda 变量，每个脚本开头都要自己激活环境；
  `command -v` 逐个确认五个工具在 PATH 里，缺一个就别往下跑。
  GenomeScope **不在 conda 环境**里（课程契约列为环境豁免工具；`env_ug_assembly.yml` 注释），
  本课用 `wget` 下载 `genomescope.R` 后以 `Rscript` 运行。
- **预期**：五行路径全部打印。任一缺失 → 讲义 E4（环境没激活成功）。
- **出错信号**：`canu: command not found` 一类 → 作业内环境未激活（讲义 E4 → 教材 §8.5.3 的参数/输入核查思路）。

## 2. 实验数据

本实验有校内、校外两条轨道，**步骤相同，数据与组装器参数不同**。两套都不要混用平台：
k-mer 扫描只用短读长，组装只用长读长（教材 8.5.3）。登录号全部已登记
`06_data/accessions.tsv` L14–17（项目 `PRJEB100987`，西非 Xoo 群体）：

| 登录号 | 平台 | 体量/深度 | 用途 |
|---|---|---|---|
| `ERR15732384` | ONT 长读长 | 302 Mb，≈63×（课程降采样至 40×） | Canu/Flye 组装 |
| `ERR15732342` | Illumina 双端短读长 | 229 Mb，≈48× | k-mer 扫描 |
| `GCA_987216485` | 作者发表完成图 | 4,768,212 bp | 「标准答案」，步骤 5 对答案用 |

两条轨道逐项输入对照：

| 轨道 | k-mer 扫描输入（短读长） | 组装输入（长读长） | 对答案参考序列 |
|---|---|---|---|
| 校内（实验室集群） | `/data/lab/ngs/` 下 `*.fq.gz`（`06_kmer_survey.sh` L24 `RAW_DIR`，作业内自动软链 L37–39） | `/data/lab/ngs/reads.fa`（PacBio，`06_assemble_compare.sh` L23） | 集群路径**由助教公布**（数据 README 未登记集群侧参考路径） |
| 校外（公开数据自学） | `<课程仓库路径>/06_data/raw/undergraduate/reads/ERR15732342_1.fastq.gz` 与 `_2.fastq.gz` | `<课程仓库路径>/06_data/raw/undergraduate/reads/ERR15732384_ont_40x.fastq.gz` | `<课程仓库路径>/06_data/raw/undergraduate/genomes/CIX4481.fna`（即 `GCA_987216485`） |

- **校外下载与降采样**（README §三原句）：
  `bash 06_data/undergraduate/download_ug.sh --run --subsample --depth 40`。
  下载脚本把文件放在 `06_data/raw/undergraduate/reads/` 与 `…/genomes/` 下，文件名以实落盘为准。
- **校外改参数的两条途径**：k-mer 脚本**不用改**——它同时认 `*.fq.gz` 与 `*.fastq.gz`
  （L44），自动软链在校外会静默跳过（L37–39 的 `|| true`），只要步骤 0 手动把短读长
  链进 `fq/` 即可；组装脚本**必须改**（校内路径与 PacBio 参数都写死了），改法见步骤 3
  的「个人副本」流程。
- **工作目录**（三个脚本一致）：`/d3/scratch/${USER}/ngs/{fq,survey,assem}`。
  原始数据几十 GB，只做软链接不拷贝——**不要把数据放家目录**（u08 项目说明，
  家目录配额小且是规范性扣分项）。
- **数据自查**（README §四，先跑通再往下做）：ONT `seqkit stats` 期望 ≈38,078 条 / 302 Mb
  （登记值，63× 全量）；Illumina 双端行数相等（`PAIRED_OK`）；完成图长度量级 4.6–5.1 Mb；
  md5 已由下载脚本校验。

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出 / 检查点 / 出错信号。
> 命令里的脚本名、参数名、输出文件名与 `03_code/undergraduate/scripts/` 现版逐字一致
> （本指导修订时已逐个 grep 核对，见任务回执）。集群真实组装/QUAST/BUSCO 本课未实测，
> 一切区间写「预期区间（未实测）」。
>
> **在哪敲命令（工作目录约定）**：SSH 登录后当前目录是家目录。下文所有 scratch 路径以
> `/d3/scratch/${USER}/ngs` 为根；`<课程仓库路径>` 指课程仓库在你机器上的位置（校内集群上
> 由教师公布）。三个脚本都带 `#$ -cwd`：作业日志（`u06_*.o<作业号>`）写在**投递时所在的
> 目录**，而产出写在脚本内部 `WORKDIR` 指定的目录——两者不是一回事，找不到文件时先想清
> 自己在找哪一类。qsub 用绝对路径投递（下面命令都给了写法），或在放脚本副本的目录里
> 投递相对路径；**不要在家目录里相对路径投递**（会报 `No such file or directory`）。

### 步骤 0：投递前准备（对应三个脚本的头部自检）

- **目的**：让作业排队之前，目录、数据、环境都就位。
- **命令**（在登录节点执行）：

  ```bash
  mkdir -p /d3/scratch/${USER}/ngs/{fq,survey,assem/{canu,flye,eval}}
  # 校内轨道：脚本作业内会自动软链，这里再链一次做肉眼确认
  cd /d3/scratch/${USER}/ngs/fq && ln -sf /data/lab/ngs/reads* ./
  # 校外轨道：手动把下载好的短读长链进 fq/（脚本认 *.fq.gz 与 *.fastq.gz 两种后缀）
  cd /d3/scratch/${USER}/ngs/fq && ln -sf <课程仓库路径>/06_data/raw/undergraduate/reads/ERR15732342_*.fastq.gz ./
  ls -lh /d3/scratch/${USER}/ngs/fq        # 软链接已建好、短读长就位
  ```

  这条命令在做什么：建标准目录（讲义 ⑤5.1 同款），把原始短读长软链进自己的 scratch，
  只链接不拷贝。两条轨道按 §2 对号入座，只做自己那条。
- **产出**：`/d3/scratch/${USER}/ngs/{fq,survey,assem}` 目录就绪；`fq/` 下有短读长文件。
- **检查点**：`ls -lh` 能看到短读长 fastq（规模见 §2 自查数字）；链接指向的文件真实存在
  （`ls -lL` 不报红）。
- **出错信号**：`fq/` 下没有 `*.fq.gz`/`*.fastq.gz` → 脚本会以 `[FATAL]` 退出
  （`06_kmer_survey.sh` L45–49），先查下载/软链接，别急着投作业。
  读数对不上 §2 自查数字 → 停，先查数据完整性。

### 步骤 1：k-mer 扫描（`qsub 06_kmer_survey.sh`）

- **目的**：用低错误率短读长数三档 k（17/21/25）的 k-mer 频数，产出 GenomeScope 的输入直方图。
  k-mer 频谱只回答"基因组多大、重复多不多、有没有混序列"，是**勘测**不是判决（教材 8.4.3）。
- **命令**（在登录节点执行；先 cd 到要放日志的目录再投递）：

  ```bash
  cd /d3/scratch/${USER}/ngs
  qsub <课程仓库路径>/03_code/undergraduate/scripts/06_kmer_survey.sh   # 脚本头：-N u06_kmer -pe smp 4，【无】h_vmem 行
  qstat -u ${USER}              # 看作业状态：qw 排队 / r 运行 / Eqw 报错
  ```

  这条命令在做什么：脚本对 `fq/` 里的短读长跑 `jellyfish count -C -m {17,21,25}
  -s 1000000000 -t 4`（L60–61），再 `jellyfish histo -t 4` 转成两列文本（L65），
  最后把 k=21 的直方图复制为无 k 标记的 `reads.histo`（L73）。
  `-C` 表示正反链合并计数：DNA 双链，AGCT 与其反向互补是同一段序列。**漏加 `-C` 时
  每个 k-mer 被正反链各计一次，频谱口径改变**，主峰位置与大小估计都可能明显变化——但
  具体方向和幅度取决于数据与拟合，没有"主峰腰斩、估计虚增一倍"之类的固定倍数（教材 8.4.3
  口径；脚本 L55 注释是同向提醒，不是实测证明）。
- **产出**（在 `survey/`）：`reads.k17.histo`、`reads.k21.histo`、`reads.k25.histo`、`reads.histo`；
  作业日志里每个 k 打印 `head -15` 自检（日志 `u06_kmer.o<作业号>` 在本指导 §3 约定目录下）。
- **检查点**：
  1. 脚本自检（L67–69）只打印每个 histo 的**前 15 行**——那是深度 1–15 的低频错误尾，
     数字单调下降是正常现象，**不是**出错信号。想看主峰在哪，二选一：
     - 作业结束后在终端手动找主峰：
       `awk '$1>=10 && $1<=100' /d3/scratch/${USER}/ngs/survey/reads.k21.histo | sort -k2,2nr | head -5`
       （第 1 列=深度，第 2 列=该深度的 k-mer 种类数；排在第一行的深度就是主峰）；
     - 或直接等步骤 2，GenomeScope 拟合摘要里的 `kcov` 就是主峰深度。
     定性判据：主峰**存在且明显高于两侧**——不存在"主峰必须落在某个数值区间"的门槛
     （未实测的固定区间不作判据，教材 8.4.3–8.4.4）。
  2. 原理自查用合成算例（**在课程仓库根目录运行**；课程站暂未发布 textbook/，
     demos 脚本请从课程仓库获取，下文同）：
     `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch08_kmer_spectrum.py --selftest`
     ——场景一主峰 19×、错误尾（深度 1–3）占 81.5%、G=40,976 bp（偏差 2.4%）。
     记住 `D_k`（主峰横坐标）≠ 按碱基的深度 D：30×、L=100、e=0.01 → D_k≈19×
     （教材 8.4.3 换算式），别把主峰读数当测序深度报。
- **出错信号**：
  - 完整直方图从最高点单调滑落、没有主峰 → 深度不足或把高错误率长读长喂了进来
    （讲义 E5 → 教材 §8.5.3）。
  - `std::bad_alloc` / `vmem exceeded` → 哈希槽超内存配额（讲义 E2：`-s` 降至 100000000）。
  - `syntax error near unexpected token '('` → 脚本没用 bash 跑（讲义 E6：头里 `#$ -S /bin/bash`）。
  - `qstat` 恒为 `Eqw` → 资源名不识别（讲义 E10：`qstat -j <ID> | grep -A5 error`）。

### 步骤 2：GenomeScope 拟合（qsub 最小作业，外置 R 脚本）

- **目的**：把直方图拟合成"错误＋杂合＋单拷贝＋重复"混合模型，读出基因组大小、杂合度、
  重复比例三个估计。**模型输出不是标准答案**（教材 8.4.4）。
- **命令**（登录节点下载脚本，拟合投计算节点；【集群未实测】）：

  ```bash
  cd /d3/scratch/${USER}/ngs/survey
  wget https://raw.githubusercontent.com/schatzlab/genomescope/master/genomescope.R
  cat > u06_gs.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u06_gs
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_assembly
  cd /d3/scratch/${USER}/ngs/survey
  Rscript genomescope.R reads.k21.histo 21 100 gs_k21 1000   # 5 个位置参数，顺序不能换
  Rscript genomescope.R reads.k17.histo 17 100 gs_k17 1000
  Rscript genomescope.R reads.k25.histo 25 100 gs_k25 1000
  EOF
  qsub u06_gs.job
  ```

  这条命令在做什么：`wget` 拉官方 R 脚本（它不进 conda；下载只在登录节点做）；
  最小作业脚本头部（`-S/-N/-cwd/-j y/-pe smp 4`）与资源参数参照 `06_assembly_eval.sh`
  L2–6 的写法，正文只有环境激活 + 三条 `Rscript`。`Rscript` 的 5 个位置参数依次是
  **直方图文件、k 值、读长、输出目录、最大截断深度**——读长 100 与 `06_kmer_survey.sh`
  L23 `READ_LEN=100` 同源，别抄成别的数；校外轨道的实际读长若不同，先查输入再填此参数。
  三档各跑一次。
- **产出**：`gs_k17/`、`gs_k21/`、`gs_k25/`，各含 `summary.txt` 与拟合图。
- **检查点**（判读按教材 8.4.4 **四步读法**，不背阈值）：
  1. 确认输入：用的是哪个 k 的 histo、读长参数是否与实际数据一致；
  2. 看拟合曲线是否贴住主峰、残差有没有系统形状；
  3. 读三个估计及区间——`summary.txt` 全英文，字段对照：**单倍体长度 = Genome Haploid
     Length、杂合度 = Heterozygosity、重复比例 = Genome Repeat Length、模型拟合优度 =
     Model Fit、有效深度 = kcov**。`Model Fit` 只作**诊断量**记录——**不存在
     "低于 90% 三个数全废"的合格线**（该判据已被教材撤下，见教材 8.4.4）；
  4. 外部对账：基因组大小预期 **4.4–4.9 Mb**、杂合度 **≈0%**（README §四，预期区间，未实测）。
  5. 三档 k 的估计做**敏感性比较**：报告三档结果、说明哪一档频谱形状最清楚及为什么选它。
     三档差多少算合格**没有通用阈值**，不存在"差 2 倍/收敛 10% 才可用"的判据（教材 8.4.3–8.4.4）。
  6. 若主峰左侧约一半深度出现半峰：细菌是单倍体，这是混序列警报，但**不是"确诊混菌"**——
     按教材 8.4.3 四条基本检查（换 k 重跑／回贴深度分档／总长对账〔有已知长度才做〕／单菌落纯化重测），
     两条同向才可写成污染证据，只有一条成立时报告写"存在半深度峰，原因待定"。
- **出错信号**：
  - `there is no package called 'minpack.lm'` → 讲义 E8；环境 yml 已含 `r-minpack.lm`，
    确认作业里激活的是 `ngs_ug_assembly`。
  - `Failed to converge` → 有效出错信号：其余数字按诊断量**降级使用**，别直接删数据
    （教材 8.4.4）。
  - `len` 明显偏离预期区间 → 回查 k 值、读长参数、数据深度，而不是编造"错误峰"式判据。

### 步骤 3：双组装（`qsub 06_assemble_compare.sh`）

- **目的**：用同一批长读长分别跑 Canu（OLC）与 Flye（repeat graph）两套独立算法，
  让两套算法假设互相检验（教材 8.4.5、8.6）。
- **命令**：

  ```bash
  cd /d3/scratch/${USER}/ngs
  qsub <课程仓库路径>/03_code/undergraduate/scripts/06_assemble_compare.sh   # 校内轨道
  ```

  **校外轨道（ONT）改用个人副本**——脚本 L23 `READS=` 与 PacBio 参数都写死了校内数据，
  原文件在课程公共目录只读，按「复制 → 改 → 核对 → 投副本」走：

  ```bash
  cp <课程仓库路径>/03_code/undergraduate/scripts/06_assemble_compare.sh \
     /d3/scratch/${USER}/ngs/06_assemble_compare_ont.sh
  cd /d3/scratch/${USER}/ngs
  # 用编辑器改副本三处（行号为现版脚本，改动前先 grep 核对）：
  #   第 23 行  READS=<课程仓库路径>/06_data/raw/undergraduate/reads/ERR15732384_ont_40x.fastq.gz
  #   第 50 行  -pacbio  →  -nanopore          （Canu 换 ONT 错误率模型）
  #   第 63 行  --pacbio-raw  →  --nano-raw     （Flye 换 ONT 错误率模型）
  # 可选：第 20 行 GENOME_SIZE=4m 改 4.7m，与讲义 ONT 口径对齐（不改也能跑）
  grep -n 'READS=\|pacbio\|nano\|GENOME_SIZE' 06_assemble_compare_ont.sh   # 逐条确认改到位
  qsub 06_assemble_compare_ont.sh
  ```

  这条命令在做什么：`GENOME_SIZE=4m`（L20，量纲最易写错：4 Mb 细菌写 `4m`，
  写成 `4g` 按 40 亿 bp 规划资源、写成 `4k` 疯狂丢读段）；Canu
  `-p test -d test-pacbio genomeSize=4m useGrid=false maxThreads=4 maxMemory=28g -pacbio /data/lab/ngs/reads.fa`
  （L46–50；`useGrid=false` 防止 Canu 再往 SGE 投子作业把自己挂死）；
  Flye `--pacbio-raw … --out-dir out_pacbio --genome-size 4m --threads 4`（L63–66）。
  `test` 只是输出前缀名，产物是你自己的组装，不是 Canu 自带测试数据。
  **副本的三处改名有连锁约束**：`#$ -N u06_assem` 不要改（评估脚本的
  `-hold_jid u06_assem` 依赖它，`06_assembly_eval.sh` L7）；输出目录名
  `test-pacbio`/`out_pacbio` 不要改（评估脚本 L23–24 按这个路径找产物）。
- **产出**：`assem/canu/test-pacbio/test.contigs.fasta`；
  `assem/flye/out_pacbio/assembly.fasta` 与元数据 `assembly_info.txt`（含 `circ.` 列）。
- **检查点**：
  1. 粗检命令（脚本 L73–77 的同款动作，作业结束后自己跑一遍）：

     ```bash
     grep -c '^>' /d3/scratch/${USER}/ngs/assem/canu/test-pacbio/test.contigs.fasta   # Canu contig 条数
     grep -c '^>' /d3/scratch/${USER}/ngs/assem/flye/out_pacbio/assembly.fasta        # Flye contig 条数
     cat  /d3/scratch/${USER}/ngs/assem/flye/out_pacbio/assembly_info.txt             # Flye：circ. 列
     grep -i "circular" /d3/scratch/${USER}/ngs/assem/canu/test-pacbio/*.report \
          /d3/scratch/${USER}/ngs/assem/canu/test-pacbio/test.contigs.fasta \
          || echo "Canu 未标环状"
     ```

     Flye 的环状标记在 `assembly_info.txt` 的 `circ.` 列；Canu 没有同名文件，在
     `test-pacbio/*.report` 或 fasta 头里找 `circular` 字样，找不到就是未标环状。
     自查基准：contig **1–5 条**、总长 **4.6–4.9 Mb**（README §四，预期区间，未实测；
     讲义"1–3 条"是理想完成图口径，教材 8.4.6 与 README §四 两种口径并存，
     以 1–5 条为自查基准，别拿理想口径当及格线）。
  2. `circ.=Y` 是**有用的阳性信号，不是完成证明**——不能证明染色体完整、无错接、
     无塌缩、质粒齐全（教材 8.4.6）。
- **出错信号**：
  - Canu 日志 `Found … (1.28 times coverage)` 式荒谬深度 → `genomeSize` 量级写错
    （讲义 E3 → 教材 §8.5.3）；改参数后**必须 `rm -rf` 原输出目录**再跑，防旧缓存。
  - `Killed` → 在登录节点跑被 OOM 杀（讲义 E1）；`command not found` → 讲义 E4。
  - 作业几天不结束 → 先查 `genomeSize` 是不是写成了 `4g`（讲义 E3）。

### 步骤 4：双维度评估（`qsub 06_assembly_eval.sh` 的个人副本）

- **目的**：QUAST 并排比连续性，BUSCO 比完整性。脚本头 `#$ -hold_jid u06_assem`（L7）
  让评估等组装结束再启动——事件驱动取代 `sleep` 轮询，组装崩了不会死等（讲义 E9）。
- **命令**（顺序不能乱：**先补离线参数，再投递**）：

  ```bash
  # ① 登录节点预下载谱系库（计算节点无外网，教材 8.5.4；讲义 ⑤5.7）
  busco --download bacteria_odb10 --download_path /d3/scratch/${USER}/ngs/busco_lib
  # ② 复制个人副本（03_code 是课程公共目录，只读，不要改原文件）
  cp <课程仓库路径>/03_code/undergraduate/scripts/06_assembly_eval.sh /d3/scratch/${USER}/ngs/
  cd /d3/scratch/${USER}/ngs
  # ③ 用编辑器打开副本，在第 59、60 行两条 busco 命令末尾（-f 之后）追加：
  #      --offline --download_path /d3/scratch/${USER}/ngs/busco_lib
  #    保存后 grep 确认：
  grep -n -- "--offline" 06_assembly_eval.sh      # 应命中第 59、60 行各一次
  # ④ 投递副本（日志 u06_eval.o<作业号> 落在当前目录，#$ -cwd）
  qsub 06_assembly_eval.sh
  ```

  这条命令在做什么：脚本跑 `quast.py <canu.fa> <flye.fa> -o quast_results -t 4 -l "Canu,Flye"`
  （L42–45），再跑两条 `busco -i … -o busco_{canu,flye} -m genome -l bacteria_odb10 -c 4 -f`
  （L59–60），最后按列名从 `transposed_report.tsv` 取数拼成报告用对比表（L69–76）。
  **为什么必须先改副本**：脚本原版的两条 busco 命令**没有** `--offline --download_path`
  （属课程侧待修，本指导不改脚本），直接投递会在计算节点联网失败退出——`qsub` 提交后
  作业按提交时的脚本执行，**投递后无法再补参数**，所以必须按 ①→④ 的顺序先改好再投。
  【集群未实测】
- **产出**：`eval/quast_results/{report.txt,transposed_report.tsv,report.html}`、
  `eval/busco_canu/short_summary*.txt`、`eval/busco_flye/short_summary*.txt`；
  awk 汇总表**不写屏幕**——qsub 只回显一行 "Your job … has been submitted"，
  汇总表在作业日志 `u06_eval.o<作业号>` 里，作业结束后 `cat u06_eval.o*` 查看。
- **检查点**：
  1. N50/L50 手算复核（在课程仓库根目录运行，rc=0）：
     `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch08_n50_vs_completeness.py --example 1`
     ——100/80/50/40/30 kb → N50 80、L50 2。会手算才看得懂 QUAST 的数。
  2. BUSCO 加法自检：`C=S+D`、`C+F+M=100%` 必须成立（教材 8.4.8）；粒度：`n=124` 时
     1 个基因 = 0.81 个百分点（`--example 4`），**C 差不到 1 个百分点不定优劣**
     （教材撤下"一票否决"判据）。
  3. **lineage 两把尺**：脚本用 `bacteria_odb10`，而 README 预期
     （C>97%）按 `xanthomonadales_odb10` 写，两库 `n` 与基因集合不同、**分数不可比**——
     本步检查点只写"两套组装用同一库自比 + 报告必须写清库名与 `n`"，
     不得把脚本跑出的 C 直接对照 README 的 97%（教材 8.4.8/8.5.4 口径）。
  4. 本步 QUAST 不带参考：错接一栏是空的（教材 8.4.8）。**无参考报告 ≠ 正确性通过**，
     记录表里正确性一栏写"未检查错接（见步骤 5）"（教材 §8.5.2）。
- **出错信号**：
  - `Errno -3` / `Temporary failure in name resolution` → 计算节点无外网，不是 BUSCO 缺陷
    （教材 §8.5.4）：回登录节点预下载 + 检查副本里 `--offline --download_path` 是否真加上了。
  - 接近全 Missing → lineage 选错（如给细菌用真核库），不是组装烂（脚本 L20–21 注释）。
  - `Please do not provide a full path in --out` → 讲义 E7：`-o` 只接名字不接路径。

### 步骤 5：对答案——有参考 QUAST（主线数据自带标准答案）

- **目的**：把组装与作者发表的完成图 `GCA_987216485`（4,768,212 bp，登记值）比对，
  拿到错接数与基因组覆盖比例——**有参考才有这两栏**（教材 8.4.8）。
- **命令**（拟合同款的最小作业投递；【集群未实测】本科评估脚本暂无此步，属课程侧待补，
  以下为手动补跑的作业脚本）：

  ```bash
  cat > /d3/scratch/${USER}/ngs/u06_qref.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u06_qref
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_assembly
  cd /d3/scratch/${USER}/ngs/assem/eval
  REF=<参考序列路径>
  quast.py ../flye/out_pacbio/assembly.fasta      -r ${REF} -o quast_vs_ref_flye -t 4
  quast.py ../canu/test-pacbio/test.contigs.fasta -r ${REF} -o quast_vs_ref_canu -t 4
  EOF
  cd /d3/scratch/${USER}/ngs && qsub u06_qref.job
  ```

  这条命令在做什么：`-r` 指向标准答案 fasta（用法与硕士脚本 `02_assembly_pipeline.sh`
  L95–97 同源），QUAST 额外报告 `# misassemblies` 与 `Genome fraction`。
  `<参考序列路径>` 按轨道填（§2 表）：校外轨道填
  `<课程仓库路径>/06_data/raw/undergraduate/genomes/CIX4481.fna`；校内集群轨道
  **由助教公布**（数据 README 未登记集群侧路径），上机按教师指认路径替换，勿编造。
- **产出**：`eval/quast_vs_ref_{flye,canu}/report.txt`（含错接数、Genome fraction、总长差异）。
- **检查点**（README §四，预期区间，未实测）：与 `GCA_987216485` 的总长差异 **<1%**。
  差异大 → 按差异形态定位：总长偏短先查塌缩（回贴深度是否约 2×）、偏长先查冗余/污染
  （GC 第二峰、D 升高）（教材 8.6）。
- **出错信号**：没带 `-r` 的报告错接栏为空，报告只能写"**未检查错接**"，
  不得写成"正确性通过"（教材 §8.5.2）。

### 步骤 6：证据链选型与记录（对齐教材 8.4.9 与报告模板）

- **目的**：从两套组装里选一套交给下一章，选型顺序固定为证据链，不是"谁 N50 大选谁"。
- **命令**：无新命令；把步骤 3–5 的产出按顺序读一遍，填 §4 结果记录表。
- **产出**：填好的结果记录表（§4）＋ 报告模板 §3.1/§3.2 的文字。
- **检查点**（顺序即教材 8.4.9）：
  1. **总长对账**：与勘测估计并排，明显偏离先查塌缩/丢段（偏短）或冗余/污染（偏长）；
  2. **结构证据**：有参考看 QUAST 错接数与 Genome fraction（步骤 5），无参考看回贴深度
     （断点常见骤降＋跨越读段缺失；塌缩处约为拷贝数倍，约 2×；低深度/过滤时信号可能不出现）；
  3. **同库 BUSCO**：C/S/D/F/M＋`n` 五项同报，C 明显偏低先查 lineage 与深度，
     **不设"差 2% 一票否决"**（`n=124` 时两三个基因就是 2 个点）；
  4. **连续性与 circ.**：排最后。`circ.=Y` 只是阳性信号（见步骤 3 检查点）。
  5. 两套一致 ≠ 结论稳健：两套可能错得一样，交叉互证不能替代标准答案或正交数据
     （教材 8.6）。若只有无参考证据，结论必须带"结构未验证"的不确定声明。
- **出错信号**：发现自己只填了 N50 和 C 两行 → 回 §4 把三维证据补全再写结论（教材 §8.5.2）。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果。表头口径：QUAST 指标注明过滤阈值（默认最短 contig 500 bp，
> 以所用版本为准，教材 8.4.7）；BUSCO 一栏必须写库名与 `n`。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 1 k-mer | 三档主峰 D_k（k=17/21/25） | × | | 定性：主峰存在且明显高于两侧；以步骤 2 拟合 kcov 为准，无固定数值门槛（教材 8.4.3–8.4.4） |
| 2 GenomeScope | 基因组大小估计（三档） | bp | | 预期 4.4–4.9 Mb（README §四，未实测） |
| 2 GenomeScope | 杂合度 | % | | 预期 ≈0%；显著非零→查混序列（README §四） |
| 2 GenomeScope | Model Fit（仅诊断量） | % | | 记录并看拟合曲线贴不贴主峰（教材 8.4.4） |
| 3 组装 | Canu contig 数 / 总长 / N50 | 条 / bp / bp | | 预期 1–5 条、4.6–4.9 Mb（README §四，未实测） |
| 3 组装 | Flye contig 数 / 总长 / N50 / circ. | 条 / bp / bp / Y-N | | 同上；circ.=Y 是阳性信号不是完成证明（8.4.6） |
| 4 评估 | BUSCO（同库）C/S/D/F/M，n= | %，注明库名 | | 加法自检 C=S+D、C+F+M=100%（8.4.8）；`bacteria_odb10` 分数不得对照 xanthomonadales 的 97% |
| 5 对答案 | 与 GCA_987216485 总长差异 / # misassemblies / Genome fraction | % / 个 / % | | 总长差异预期 <1%（README §四，未实测） |
| 6 选型 | 最终选择 + 证据链顺序（总长→结构→完整性→连续性） | 文字 | | 按教材 8.4.9；无参考时写"结构未验证" |

## 5. 失效条件对照（教材 §8.5，本实验里在哪一步察觉）

1. **重复长于读长（DBG：k−1）→ 断开或塌缩**（§8.5.1）｜察觉：步骤 3 的 contig 数明显多于
   1–5 条先别怪算法；步骤 5/回贴看塌缩处深度约 2×、断点处骤降＋跨越读段缺失；
   总长与勘测估计对账，偏短先查塌缩。单看 N50 分不清"拼得更好"与"连得更错"。
2. **只报连续性不报正确性**（§8.5.2）｜察觉：步骤 4 的 QUAST 无参考版错接栏为空——
   报告写"未检查错接"；若只按 N50 选型，用合成反例自查（在课程仓库根目录运行，rc=0）：
   `python3 textbook/demos/ch08_n50_vs_completeness.py --example 3`（正确 [2.0,2.0] Mb N50=2.0，
   嵌合 [4.0] Mb N50=4.0，BUSCO C 不变）。
3. **高错误率长读长做 k-mer 勘测；genomeSize 量级写错**（§8.5.3）｜察觉：步骤 1 完整直方图
   单调滑落无主峰 → 查是否误用长读长（合成复现：
   `python3 textbook/demos/ch08_kmer_spectrum.py --error-rate 0.10` → 主峰塌到 4×、G 偏差 67.3%，rc=0）；
   步骤 3 Canu 报 `(1.28 times coverage)` 式荒谬深度 → `genomeSize` 量纲，手算
   "读段总碱基 ÷ genomeSize" 与日志对照（教材算例：1.6×10⁸ bp 按 4 Mb→40×、4 Gb→0.04×）。
4. **BUSCO 谱系库需联网 / 库名不一致**（§8.5.4）｜察觉：步骤 4 报 `Errno -3` → 节点无外网，
   登录节点预下载＋副本补 `--offline --download_path`，不是 BUSCO 缺陷；跑通了分数对不上 →
   查库名与 `n` 是否写进报告（本课脚本 `bacteria_odb10` 与 README 预期
   `xanthomonadales_odb10` 两把尺不可比——本课脚本与预期恰存此口径差，教材 8.5.4 要求库名与 n 写进报告）。

## 6. 思考题（教材 §8.7，习题 1–5，不给答案）

1. 一条 150 bp 读段在 k=21 与 k=31 时各产生多少个 k-mer？1% 错误率下两种 k-mer
   至少含一个错误的概率各是多少？（§8.7 习题 1 → 8.4.3）
2. 频谱深度 5/20/40 处各有 200/400/100 种 k-mer、主峰 20：按 i_min=1 与 i_min=6 两种口径
   各估 G，差别来自哪个假设？（§8.7 习题 2 → 8.4.3 的 i_min 口径）
3. 六条 contig 500/300/200/150/100/50 kb 求 N50/L50；前两条错接成 800 kb 后呢？（§8.7 习题 3，
   可用 `--example 2` 核对）
4. 你的选型证据链里，哪一条证据能排除哪一类错误？哪一类错误所有本科流程都看不见？（§8.7 习题 8 的本科版 → 8.4.9）
5. Canu 与 Flye 结果不一致时，为什么"取平均/取交集"不是解法？先确认哪两件事？（→ 8.6）

## 7. 提交物

- **对应作业**：u08 综合项目的「模块 1 基因组勘测 + 模块 2 基因组组装」（评分维度
  技术准确性 30 分、分析深度 20 分，见 `08_assessment/undergraduate/project/undergrad_project.md`）。
- **报告内容**：实践报告模板（`undergrad_report_template.md`）§2（GenomeScope 图 +
  大小/杂合度/重复比例）与 §3.1 对比表四行（Contig 数量/N50/总长度/BUSCO 完整性）＋ §3.2 选型论证。
  表格列以《学生实验操作手册》§5.1 为准（anchored）。
- **打包**：按课程统一命名 `学号_姓名_<作业号>.zip`；u06 阶段包含：三档 `summary.txt`、
  本指导 §4 结果记录表、QUAST `report.txt`（步骤 4＋5）、`short_summary*.txt`、
  选型后的一个 FASTA。
- **诚实红线**：无参考步骤 5 时，报告正确性一栏写"未检查错接"；一切预期区间不得写成实测。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念/失效条件/习题） | `textbook/chapters/ch08/manuscript.qmd` §8.4 / §8.5 / §8.7 |
| 本单元讲义（原理细节、⑨ 错误排查 E1–E10） | `02_lectures/undergraduate/unit06_assembly_basics/06_assembly_basics_lecture.md` |
| 三个作业脚本 | `03_code/undergraduate/scripts/06_kmer_survey.sh`、`06_assemble_compare.sh`、`06_assembly_eval.sh`（校外轨道按步骤 3/4 复制个人副本修改） |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch08_kmer_spectrum.py`、`ch08_debruijn_repeat.py`、`ch08_n50_vs_completeness.py` |
| 数据说明、下载与预期区间 | `06_data/undergraduate/README.md` §2.1（登记值）、§三（降采样）、§四（自查区间）；`06_data/undergraduate/download_ug.sh` |
| 环境定义 | `07_envs/conda/env_ug_assembly.yml`（`ngs_ug_assembly`） |
| 作业与报告模板 | `08_assessment/undergraduate/project/undergrad_project.md`、`undergrad_report_template.md` |
