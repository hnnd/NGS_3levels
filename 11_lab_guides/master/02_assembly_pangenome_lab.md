---
title: "实验指导 m02：基因组组装与比较/泛基因组"
level: master
topic: m02
textbook: [ch11, ch08]
lecture: ../02_lectures/master/topic02_assembly_pangenome/02_assembly_pangenome_lecture.md
env: ngs_ms_genome
---

# 实验指导 m02：基因组组装与比较/泛基因组

> 上机时手边打开的这份文件。每一步都回答四件事：这条命令在做什么、敲什么、
> 看到什么算对、看到什么说明错了。原理与判据在教材第 11 章（§11.4 概念、§11.5
> 失效条件）与第 8 章（§8.4、§8.5），这份指导只放操作与自查入口。所有标
> 「预期（未实测）」的数字都是课程写下的自查范围，不是实测结果；本课没有在
> 集群上真实跑完过全流程，标「集群未实测」的步骤同样按预期对待。

## 0. 本实验对应什么

- **教材**：第 11 章 比较基因组与泛基因组（主）＋第 8 章 基因组组装与质量评估（参照）。
  本实验覆盖硕士学习目标 LO11-04（OrthoFinder 输入与输出审查）、LO11-05（统一重注释与
  输入体检）、LO11-06（泛基因组分类规则与曲线）、LO11-07（CAFE5 模型与时间树）。
- **学时**：m02 共 4 学时（2 理论＋2 实践，契约口径）；上机 5–7 小时，等待计算期间可写报告。
- **流程分两阶段**：阶段一（步骤 1–5）勘测、组装与评估，产出 CIX2779 组装序列；
  阶段二（步骤 6–10）统一重注释、聚类、泛基因组划分与 CAFE5，输入是阶段一的组装结果，不要跳步。
- **环境**：组装/评估/比较基因组用 `ngs_ms_genome`（`07_envs/conda/env_master_genome.yml`：
  flye=2.9.2、quast=5.2.0、busco=5.4.7、orthofinder=2.5.5、mafft=7.520、iqtree=2.2.2、
  cafe=5.1.0〔装出的命令名是 `cafe5`〕、r-ape、r-ggplot2=3.4.2；diamond 由 orthofinder
  依赖带入、未单独钉版）；Prokka 用 `ngs_ug_annot`（未钉版）；泛基因组 R 绘图用
  `ngs_ms_base`（r-tidyverse=2.0.0、r-ggplot2=3.4.2）。
- **两个已知环境缺口（先知道，后文有替代写法）**：`genomescope2` 与 `UpSetR` 都不在
  任何课程环境 yml 里——k-mer 拟合改用 wget 下来的 `genomescope.R`（步骤 2），
  UpSet 图给两条路（步骤 9）。本课不声称这两个包「已装好」。
- **工程约束**：作业用长读长数据的基因组 ≤ 50 Mb；组装与 OrthoFinder 两步带
  `[checkpoint]` 预跑结果：计算节点上 `CKPT=/data/lab/m02/checkpoints`，
  跑不完就用 `USE_CKPT=1` 启用预跑输出（组装脚本 L78–80、比较脚本 L55–58）。
- **计算纪律**：一切计算一律 `qsub` 投递计算节点（包括 GenomeScope 拟合、Prokka
  注释、R 绘图这种小计算）；登录节点只做下载、建环境、编辑、取参考组装。

## 1. 实验前检查

- **前置自测**（讲义 ②，先确认能过）：
  `l0_01_linux` Q06/Q09（qsub 与作业脚本）、`l0_03_conda` Q07/Q10（作业里正确激活环境）、
  `l0_05_formats` Q07/Q10、`l0_06_stats` Q04/Q05/Q10（多重检验与 BH，CAFE5 结果判读要用）。
- **激活环境并核验工具链**（两个脚本的守卫同款写法）：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_genome
  command -v jellyfish flye quast.py busco orthofinder diamond mafft cafe5
  ```

  这条命令在做什么：SGE 作业不继承你终端里的 conda 变量，每个作业脚本开头都会自己
  激活环境（脚本 L35–36 / L50–51）；你在登录节点先跑一遍 `command -v`，缺哪个工具
  都能在投递前发现，而不是等作业失败。
- **检查点**：八条路径全部打印。`cafe5` 是包 `cafe=5.1.0` 装出的命令名，找不到
  `cafe5` 不是装错包（比较脚本 L40 注释）。
- **出错信号**：`command not found` → 环境没激活成功；不要在登录节点直接 `bash`
  跑两个主脚本（脚本头明令禁止，会抢登录节点资源被杀）。
- **BUSCO 谱系库预下载**（登录节点，计算节点无外网；组装脚本 L100–101 同款命令）：

  ```bash
  busco --download xanthomonadales_odb10 --download_path /data/db/busco_downloads
  ```

  `/data/db` 是实验室共享目录，无写权限时把下载目录换到自己的 scratch，并同步改
  个人副本（步骤 5 说明改哪行，即脚本 L33 的 `BUSCO_DB`）。
- **r-ape 超度量自检**：`ngs_ms_genome` 的 yml 已声明 `r-ape`，理论上
  `Rscript -e 'library(ape); cat(ape::is.ultrametric(ape::read.tree("tree.nwk")), "\n")'`
  可跑；**集群实测 unverified**，跑不通时按步骤 10 的替代口径办。

## 2. 实验数据

主线是西非水稻白叶枯病菌 *Xanthomonas oryzae* pv. *oryzae*（Xoo）项目 `PRJEB100987`
的一株 CIX2779（组装侧）＋ 3 株已发表参照株（比较侧）。登录号全部已登记
`06_data/accessions.tsv`（L14、L34–38、L41），零悬空：

| 登录号 | 平台/形态 | 体量（登记值） | 用途 |
|---|---|---|---|
| `ERR15732374` | ONT 长读长 | 425 MB | CIX2779，Flye 组装输入 |
| `ERR15732332` | Illumina 双端 | 160 MB | CIX2779 短读长，k-mer 侦察与抛光 |
| `GCA_024981335` | 已发表完整基因组 | 4.77 Mb | CIX2779 的「标准答案」：QUAST 参考 |
| `GCA_004322815` | 已发表完整基因组 | 约 4.7–5.1 Mb | 泛基因组参照株 CIX2374 |
| `GCA_004322835` | 已发表完整基因组 | 约 4.7–5.1 Mb | 泛基因组参照株 CIX298 |
| `GCA_029204245` | 已发表完整基因组 | 约 4.7–5.1 Mb | 泛基因组参照株 CIX4509 |

- **MB 是下载体积，不是碱基数**——不得拿 425 MB 或 160 MB 去除以基因组大小换算深度
  （教材 §8.6 硕士块明文）。深度概念只在 k-mer 频谱与 QUAST 结果里读。
- **下载读长**（登录节点；默认 dry-run，加 `--run` 才真下）：

  ```bash
  cd <课程仓库路径>
  bash 06_data/master/download_master.sh --list                 # 先看清单
  bash 06_data/master/download_master.sh --topic m02 --run --outdir /d3/scratch/${USER}/ngs/data
  ```

  脚本默认把文件下进仓库里的 `06_data/raw/master/`，**数据一律进 scratch**：必须带
  `--outdir /d3/scratch/${USER}/ngs/data`，落盘路径才能对上两个主脚本的
  `DATA_DIR=/d3/scratch/${USER}/ngs/data/m02`（组装脚本 L36）。文件名以实落盘为准，
  与 `READS`/`SR1`/`SR2`（L37–39）默认名不一致时改个人副本对应行。
- **取 4 个参考组装**（下载脚本不取组装，登录节点自取）。NCBI FTP 按登录号分三级
  哈希目录、末级目录与文件名都含程序集版本后缀（`.1_ASM...v1`），**只在 URL 里替换
  GCA 号得不到其余三株的路径**（会 404，`zcat` 报 not in gzip format）。下面 4 条
  完整路径 2026-11-10 逐条实测可下；gff 只有标准答案需要（QUAST `-g`）：

  ```bash
  D=/d3/scratch/${USER}/ngs/data/m02
  B=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/024/981/335/GCA_024981335.1_ASM2498133v1/GCA_024981335.1_ASM2498133v1
  curl -s ${B}_genomic.fna.gz | zcat > ${D}/GCA_024981335.fna
  curl -s ${B}_genomic.gff.gz | zcat > ${D}/GCA_024981335.gff
  B=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/004/322/815/GCA_004322815.1_ASM432281v1/GCA_004322815.1_ASM432281v1
  curl -s ${B}_genomic.fna.gz | zcat > ${D}/GCA_004322815.fna
  B=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/004/322/835/GCA_004322835.1_ASM432283v1/GCA_004322835.1_ASM432283v1
  curl -s ${B}_genomic.fna.gz | zcat > ${D}/GCA_004322835.fna
  B=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/029/204/245/GCA_029204245.1_ASM2920424v1/GCA_029204245.1_ASM2920424v1
  curl -s ${B}_genomic.fna.gz | zcat > ${D}/GCA_029204245.fna
  ```

- **面板构成（设例口径）**：比较侧 = 3 株参照株 ＋ 你自己组装的 CIX2779，共 **n=4**。
  CIX2779 有标准答案 `GCA_024981335`——它的基因数或特异基因数明显离群时，先怀疑
  自己的组装或注释（教材 §11.6 的内建自检点）。
- **项目总株数不写**：公开材料里项目总株数的口径尚未统一，本实验只讲这 4 株，
  不引用任何「总株数」（教材 §11.6 限制）。

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出 / 检查点 / 出错信号。
> 命令里的脚本名、参数名、输出文件名与 `03_code/master/scripts/` 现版逐字一致
> （本指导修订时已逐个 grep 核对，见任务回执）。集群真实组装/OrthoFinder/CAFE5
> 本课未实测，一切区间写「预期（未实测）」。
>
> **在哪敲命令**：下文 scratch 路径以 `/d3/scratch/${USER}` 为根；`<课程仓库路径>`
> 指课程仓库在本机的位置（校内集群由教师公布）。两个主脚本都带 `#$ -cwd`：作业
> 日志写在**投递时所在的目录**，产出写在脚本内部 `WORKDIR` 指定的目录，两者不是
> 一回事。`03_code/` 是课程公共目录、只读；凡要改脚本（路径、缺口替代）一律
> 「cp 个人副本 → 改指定行 → grep 确认 → qsub 副本」，不改原文件——qsub 按提交时
> 的脚本执行，**投递后无法再补参数**。
>
> **个人作业脚本**：步骤 6 的 Prokka 投递脚本与步骤 9 的 R 分析脚本课程仓库里没有，
> 下文给完整文本，存到自己 scratch 再 qsub（与个人副本同一纪律）。

### 阶段一：基因组勘测、组装与评估

#### 步骤 1：数据下载与参考组装自取（登录节点）

- **目的**：把 §2 的读长与 4 个参考组装放到位，并让主脚本默认路径找得到它们。
- **命令**：按 §2 三节命令执行（下载脚本 `--list` → `--run --outdir …` → 4 组 curl）。
- **产出**：`/d3/scratch/${USER}/ngs/data/m02/` 下两个 run 的 fastq（ONT 单端一个文件、
  Illumina 双端 `_1`/`_2` 两个文件，以实落盘为准）＋ `GCA_024981335.fna/.gff` ＋
  3 个参照株 fna。
- **检查点**：`ls -lh` 体量与 §2 表同量级；`md5sum` 与下载脚本输出一致（脚本自带校验）；
  `grep -c '^>' GCA_024981335.fna` 应为 1 条染色体级序列（4.77 Mb 登记值量级）。
- **出错信号**：下载脚本报 md5 不符 → 加 `--runs ERR15732374` 重下该 run，别带病往下跑；
  curl 出来是 0 字节/HTML → FTP 路径不对，回 §2 核对整条 URL，不要换 GCA 号硬凑。

#### 步骤 2：k-mer 特征估计（`qsub` 个人副本）

- **目的**：用低错误率 Illumina 短读长估基因组大小、杂合度、重复比例，给组装立
  预期。k-mer 谱是**勘测不是判决**（教材 §8.4.3）；长读长错误率高，不适合做 k-mer
  谱（脚本 L39 注释），所以 survey 输入是 Illumina 双端。
- **命令**（genomescope2 未进任何课程环境：wget `genomescope.R` 用 Rscript 运行。
  该脚本只依赖 R 基础包、带 5 个位置参数，本机已核用法与源码；先复制个人副本改
  两处，再投递）：

  ```bash
  # ① 登录节点：取 GenomeScope R 脚本（它不进 conda 环境）
  cd /d3/scratch/${USER}/ngs/data/m02
  wget https://raw.githubusercontent.com/schatzlab/genomescope/master/genomescope.R
  # ② 复制个人副本（03_code 只读，不改原文件）
  cp <课程仓库路径>/03_code/master/scripts/02_assembly_pipeline.sh /d3/scratch/${USER}/m02/
  cd /d3/scratch/${USER}/m02
  # ③ 编辑器改副本两处（行号为现版脚本）：
  #    第 52 行  工具守卫删去 genomescope2（它在环境中不存在，留着会让整个作业退出）
  #    第 71 行  genomescope2 -i reads.histo -o genomescope_out -k "${KMER}" -p "${PLOIDY}"
  #             →  Rscript /d3/scratch/${USER}/ngs/data/m02/genomescope.R reads.histo "${KMER}" 150 genomescope_out 1000
  #    为什么绝对路径：作业运行时脚本会 cd 到 WORKDIR=.../m02/assembly（L46、L60–61），
  #    那里没有 genomescope.R；相对路径会在拟合处报 cannot open file，set -e 让整个作业退出。
  #    5 个位置参数：直方图、k 值、读长、输出目录、kmer_max；读长 150 = ERR15732332 实测读长
  #    （ENA FASTQ 头行核，2026-11-10）；想自己核：zcat .../ERR15732332_1.fastq.gz | head -2 | tail -1 | awk '{print length($0)}'
  grep -n 'command -v\|genomescope' 02_assembly_pipeline.sh    # 逐条确认改到位
  # ④ 投递副本（脚本头 -pe smp 16 与 THREADS=16 一致；日志 m02_assembly.o<作业号>）
  qsub 02_assembly_pipeline.sh
  ```

  这条命令在做什么：`jellyfish count -C -m 21 -s 2G -t 16 -o reads.jf <(zcat SR1 SR2)`
  （L67–68；`-C` 正反链合并计数不能省）→ `jellyfish histo` 得两列直方图（L70）→
  GenomeScope 拟合（L71 副本改写处）。作业后续步骤（组装、评估）在同一脚本里，
  本步骤先看 survey 产出，评估步骤的检查点在步骤 4/5。
- **产出**（在 `WORKDIR=/d3/scratch/${USER}/m02/assembly`，L46）：`reads.jf`、`reads.histo`、
  `genomescope_out/summary.txt` 与 `genomescope_out/plot.png`（报告 fig1_kmer_histogram.png）。
- **检查点**：
  1. 主峰存在且明显高于两侧；主峰横坐标是 **k-mer 深度 D_k，不等于测序深度 D**
     （换算见教材 §8.4.3：D_k ≈ D×(L−k+1)/L×(1−e)^k；合成算例 30×、L=100、e=0.01
     → D_k≈19×）。半峰（约一半深度处）首先怀疑混序列，但要按教材 §8.4.3 四条检查
     （换 k、回贴分档、总长对账、纯化重测）至少两条同向才可写污染，否则写
     「存在半深度峰，原因待定」。合成参照：
     `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch08_kmer_spectrum.py --selftest`（rc=0）。
  2. 估计大小与登记值 4.77 Mb（`GCA_024981335`）同量级；估计与组装总长偏差
     **>20% 是经验警戒线（非文献阈值）**，触发后先查 k 值/读长参数/深度，不编判据。
  3. `Model Fit` 只作**诊断量**记录，按教材 §8.4.4 四步读法（确认输入→看拟合曲线与
     残差→读估计及区间→外部对账）；**不存在「低于 90% 三个数全废」的合格线**
     （该判据已被教材撤下）。
- **出错信号**：完整直方图从最高点单调滑落、没有主峰 → 先查是不是把长读长喂了进来
  （讲义 ⑨-4 同型 → 教材 §8.5.3）；`syntax error near unexpected token '('` → 作业头
  必须 `#$ -S /bin/bash`（脚本 L2 已带；改副本别删掉）；`[FATAL] genomescope2 不在 PATH`
  → 第 52 行守卫没改干净；`cannot open file 'genomescope.R'` → 第 71 路径没写绝对。

#### 步骤 3：长读长组装 Flye（同一脚本，[checkpoint]）

- **目的**：用 CIX2779 的 ONT 读长跑 Flye 2.9.2，得到染色体级组装。
- **命令**：上一步已投递的同一作业包含本步骤（脚本 L78–86），无需另投。
  跑不完（排队过久/调试期）就用预跑结果：

  ```bash
  # 重新投递时启用预跑组装（脚本 L78–80 的分支；作业不继承登录 shell 的变量，
  # 用 qsub 的 -v 传进去，或改副本里 USE_CKPT 的默认值为 1）：
  qsub -v USE_CKPT=1 02_assembly_pipeline.sh
  # 启用后脚本直接拷贝 checkpoint 的 assembly.{fasta,txt,gfa} 进 asm_flye/
  ```

  这条命令在做什么：`flye ${READ_TYPE} "${READS}" --out-dir asm_flye --threads 16`
  （L84）。`READ_TYPE` 默认 **`--nano-raw`**（L30）——主线 `ERR15732374` 是 MinION
  （ENA instrument_model 实查），与本课数据匹配；换 HiFi 数据才用 `--pacbio-hifi`，
  确知 R10.4+Dorado sup 用 `--nano-hq`。**读长类型参数必须与数据匹配**，选错的后果
  是 contig 数暴涨、总长远超估计（讲义 ⑨-4 → 教材 §8.5.3）。
- **产出**（`WORKDIR/asm_flye/`）：`assembly.fasta`、`assembly_info.txt`（含 `circ.` 列）、
  `assembly_graph.gfa`。
- **检查点**（`06_data/master/README.md` m02 自查判据，预期、未实测）：
  1 条染色体；总长 **4.7–5.2 Mb**；`assembly_info.txt` 的 `circ.`=Y 是**有用的阳性
  信号，不是完成证明**（不能证明无错接、无塌缩，教材 §8.4.6）。contig 数 **>20**
  说明数据量或参数有问题（README 口径，线索非判据）。
- **出错信号**：总长远超 4.77 Mb 量级＋contig 暴涨 → 第一怀疑读长类型参数选错
  （讲义 ⑨-4），改对参数重跑，别指望后处理挽救；`Killed` → 在登录节点跑了，回 qsub。

#### 步骤 4：QUAST 评估（同一脚本；连续性＋正确性）

- **目的**：与标准答案 `GCA_024981335` 比对，同时拿连续性（N50/L50）与正确性
  （misassembly、genome fraction）。**必须给 `-r`/`-g` 才有这两栏**（脚本 L91 注释；
  教材 §8.4.8）。不给参考的 QUAST 报告错接栏是空的，「无参考报告 ≠ 正确性通过」
  （教材 §8.5.2）。
- **命令**：同一作业内自动执行（L88–96：`quast.py asm_flye/assembly.fasta -r "${REF_FA}"
  -g "${REF_GFF}" -o quast_out -t 8`）。`REF_FA`/`REF_GFF` 默认指向
  `${DATA_DIR}/GCA_024981335.fna/.gff`（L44–45）——即步骤 1 curl 的文件；缺失时脚本
  只 WARN 降级、不出基因覆盖统计（L93），那两项要在报告里写「未检查」。
- **产出**：`quast_out/report.{txt,tsv,html}` 等。
- **检查点**（README 自查判据，预期、未实测）：genome fraction **>97%**、misassembly
  **个位数**；N50/L50 手算复核（在课程仓库根目录运行，rc=0）：
  `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch08_n50_vs_completeness.py --example 2`
  ——500/300/200/150/100/50 kb → N50 300、L50 2；错接反例（`--example 3`）：[2.0,2.0] Mb
  错接成 [4.0] Mb，总长不变、N50 2.0→4.0——**N50 对错接是奖励**，必须与 misassembly
  同读（教材 §8.4.7–8.4.8）。
- **出错信号**：misassembly 栏空 → 没给 `-r`，报告写「未检查错接」（教材 §8.5.2）；
  N50 变大同时 misassembly 变多 → 错接被奖励，回到组装参数与证据链（教材 §8.5.2）。

#### 步骤 5：BUSCO 评估（同一脚本；完整性）

- **目的**：用保守基因集查组装的完整性。`BUSCO_LINEAGE` 默认
  **`xanthomonadales_odb10`**（L31），与 README 自查判据同一套口径；报告必须写明
  库名、版本与 `n`（short_summary 里都有）。
- **命令**：同一作业内自动执行（L102–103：`busco -i asm_flye/assembly.fasta -l
  "${BUSCO_LINEAGE}" -m genome -o busco_out -c 8 --offline --download_path "${BUSCO_DB}"`）。
  无 `/data/db` 写权限时改副本 L33 的 `BUSCO_DB` 为自己的预下载目录（§1 已下）。
- **产出**：`busco_out/short_summary*.txt` 及明细目录。
- **检查点**（README 自查判据，预期、未实测）：**C > 97%**；五数加法自检
  **C=S+D、C+F+M=100%** 必须成立（教材 §8.4.8；设例 123/65/58 → C:99.2%[S:52.4%,
  D:46.8%]，n=124 口径）。粒度教学算例：`bacteria_odb10` 的 n=124 时 1 个基因 =
  0.81 个百分点（在课程仓库根目录运行：`python3 textbook/demos/ch08_n50_vs_completeness.py
  --example 4`，rc=0）——C 差不到 1 个百分点不定优劣；本课用的 xanthomonadales 库
  `n` 不同，以你跑出的 short_summary 为准。**不给 D 设百分比红线**（教材 §8.6 硕士块
  明文不采纳）：D 偏高时按 §8.5.5 三步（总长对账→回贴深度→独立证据）区分两套序列/
  真实复制/污染。
- **出错信号**：`Errno -3` / `Temporary failure in name resolution` → 计算节点无外网，
  不是 BUSCO 缺陷（教材 §8.5.4）：回登录节点预下载＋检查 `--offline --download_path`
  是否指向已下载目录；接近全 Missing → lineage 选错。

### 阶段二：比较基因组与泛基因组分析

#### 步骤 6：统一重注释（Prokka，`qsub` 个人作业脚本，4 株同一口径 .faa）

- **目的**：比较基因组的第一前提是输入可比——4 株（含你自己组装的 CIX2779）必须用
  **同一软件、同一版本、同一参数**预测基因，否则会得到大批假的「菌株特异基因」
  （教材 §11.5.1）。公共库完成图的注释来源不一，必须重注释。
- **命令**：先做输入准备（3 株参照株 fna 步骤 1 已取；把自己组装的序列按株名放好），
  再把个人作业脚本存到 scratch、检查、投递：

  ```bash
  # ① 登录节点：自己的组装结果按株名放入数据目录（供脚本循环统一处理）
  cp /d3/scratch/${USER}/m02/assembly/asm_flye/assembly.fasta /d3/scratch/${USER}/ngs/data/m02/CIX2779.fna
  # ② 把下面的「个人作业脚本 02_prokka_job.sh」全文存为 /d3/scratch/${USER}/m02/02_prokka_job.sh
  # ③ 检查并投递（脚本头 -pe smp 8；日志 m02_prokka.o<作业号>）
  grep -n 'conda activate\|for strain\|prokka' /d3/scratch/${USER}/m02/02_prokka_job.sh
  qsub /d3/scratch/${USER}/m02/02_prokka_job.sh
  ```

  **个人作业脚本 02_prokka_job.sh（完整文本，逐字保存）**：

  ```bash
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m02_prokka
  #$ -cwd
  #$ -j y
  #$ -pe smp 8
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_annot
  set -euo pipefail
  DATA=/d3/scratch/${USER}/ngs/data/m02
  OUT=/d3/scratch/${USER}/m02/proteomes
  mkdir -p "${OUT}"
  # 4 株同一软件、同一版本、同一参数（教材 §11.5.1）：3 株参照株 + 自己组装的 CIX2779
  for strain in GCA_004322815 GCA_004322835 GCA_029204245 CIX2779; do
    prokka --prefix "${strain}" --kingdom Bacteria --outdir "prokka_${strain}" "${DATA}/${strain}.fna" --cpus 8
    cp "prokka_${strain}/${strain}.faa" "${OUT}/${strain}.faa"
  done
  ```

- **产出**：`proteomes/` 下 4 个 `.faa`（文件名（去扩展名）即 OrthoFinder 输出中的
  物种名，比较脚本 L17 注释）＋ 每株一个 `prokka_<strain>/` 注释目录。
- **检查点**：4 个 `.faa` 均非空；蛋白数同量级——本课 Prokka 预期每株约
  **4,000–4,600** 个基因（`06_data/undergraduate/README.md` §四，预期、未实测）。
- **出错信号**：某一株 `.faa` 明显偏大/偏小或几乎为空 → 停，先查该株 `prokka_<strain>/`
  日志与参数是否同一套（教材 §11.5.1）；**不要**带着离群输入往下跑 OrthoFinder。

#### 步骤 7：输入体检（蛋白集可比性）

- **目的**：跑聚类之前的最后一道闸——任何一株蛋白数离群都先查注释，不查生物学。
- **命令**（比较脚本 L46–50 同款动作，登录节点即可做）：

  ```bash
  cd /d3/scratch/${USER}/m02/proteomes
  for f in *.faa; do printf "%-30s %s\n" "$f" "$(grep -c '^>' "$f")"; done
  ```
- **产出**：4 行「文件名 蛋白数」。
- **检查点**：4 株同量级（预期 4,000–4,600/株，未实测）；两两差异 **>20% 是课程经验
  警戒线、只是排查线索不是判据**——注释差异不到 20% 也能制造大量假特异（比较脚本
  L51 注释口径；教材 §11.4.2）。合成算例的形态：统一注释 2,088–2,132、混入 1 株
  宽松规则后 9,993/8,150（在课程仓库根目录运行：
  `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch11_annotation_bias.py --selftest`，rc=0）。
- **出错信号**：某株离群 → 回步骤 6 查注释流程，**不要**往下跑（教材 §11.5.1）。

#### 步骤 8：直系同源聚类 OrthoFinder（`qsub` 个人副本，第一投只做聚类；[checkpoint]）

- **目的**：把 4 株统一注释的蛋白集聚成直系同源群，产出存在/缺失矩阵的源头
  `GeneCount.tsv` 与体检表。OrthoFinder 2.5.5 **只对含 ≥4 条序列的 OG 建基因树**，
  `-M msa` 下默认 MAFFT＋FastTree，另加 `-T iqtree` 才是 IQ-TREE（教材 §11.4.3）——
  物种树可作拓扑参考，**枝长是替换数，不能直接喂 CAFE5**。
- **命令**（`PROT_DIR` 现版仍是占位路径，必须改副本。**第一投只做聚类**：CAFE5 要的
  超度量树步骤 10 才造，现在把树自检与 CAFE5 段整段注释掉，否则作业跑完聚类会在
  树自检处 `exit 1`）：

  ```bash
  cp <课程仓库路径>/03_code/master/scripts/02_orthofinder_cafe.sh /d3/scratch/${USER}/m02/
  cd /d3/scratch/${USER}/m02
  # 编辑器改副本（行号为现版脚本）：
  #   第 29 行  PROT_DIR=/d3/scratch/${USER}/m02/proteomes        （你步骤 6 的 4 个 .faa）
  #   第 83–119 行  全部行首加 # 注释掉（自「步骤二：构造 CAFE5 输入」到文件结尾：
  #               第一投不构造 CAFE5 输入、不做树自检、不跑 CAFE5）
  grep -n 'PROT_DIR=\|TREE_ULTRA=' 02_orthofinder_cafe.sh      # 逐条确认改到位
  qsub 02_orthofinder_cafe.sh      # 脚本头 -N m02_ortho_cafe -pe smp 16
  # 跑不完/调试期用预跑结果：qsub -v USE_CKPT=1 02_orthofinder_cafe.sh（脚本 L55–58 分支）
  ```

  这条命令在做什么：`orthofinder -f "${PROT_DIR}" -t 16 -a 4 -M msa -S diamond`
  （L61；`-a` 取 `-t` 的 1/4，脚本注释说明别设得比 `-t` 大）；跑完自动打印体检两行
  （L67–70）。真核数据须先每基因只留最长转录本（讲义 ⑤5.5），本课细菌免此步。
- **产出**：`Results_*/` 目录群，本实验消费：`Orthogroups/Orthogroups.GeneCount.tsv`、
  `Comparative_Genomics_Statistics/Statistics_PerSpecies.tsv`（体检表）、
  `Orthogroups/Orthogroups_SingleCopyOrthologues.txt` 与 `Single_Copy_Orthologue_Sequences/`
  （步骤 10 建树用）、`Orthogroups/Orthogroups_UnassignedGenes.tsv`（孤儿基因，泛基因组
  总量须声明是否纳入，教材 §11.4.2）、`Species_Tree/SpeciesTree_rooted*.txt`。脚本把
  `GeneCount.tsv` 复制到工作目录 `/d3/scratch/${USER}/m02/compgenome`（L78），步骤 9 的
  R 脚本吃这个文件。
- **检查点**：脚本 L68–70 自动 grep 体检表；**某一列的 species-specific 计数比其他列
  高一个量级 → 注释不统一的警报**（教材 §11.5.1），跑完第一件事就是看它。核心/泛基因组
  计数**本章不预设数值**（unverified，教材 §11.6）；README 旧说明的「Roary 4–5 株 core
  3500–4000 / pan 5000–6500」是另一套小样本预期值，**不套用、不是验收线**。
- **出错信号**：体检表某列离群 → 回步骤 6/7 查注释；某株 `.faa` 为 0 条 → 空输入会让
  共享家族在该列全缺失，「没有报错」不等于输入完整（教材 §11.4.4 图 11-2 导语口径）；
  作业在「树不是超度量」处退出 → 第 83–119 行没注释干净。

#### 步骤 9：泛基因组划分、共享模式图与稀释曲线（R，`ngs_ms_base`，个人作业脚本）

- **目的**：把 `GeneCount.tsv` 折成 0/1 存在矩阵，按出现频率互斥分类，画组成图、
  共享模式图与稀释曲线。**n=4 时 95%/99% 与 100% 三个阈值全部退化为「4 株全有」**
  （⌈0.95×4⌉=4，k=0），softcore 恒为空；允许缺 1 株的真实比例是 3/4=75%（合成算术，
  在课程仓库根目录运行：`PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch11_core_threshold.py
  --strains 4 5 8 12 20 57 100`，rc=0）。报告一律写「允许缺失 k 株（≈ x%）」并同时报
  `n`、`m`、`k`（教材 §11.5.2；术语表口径）。
- **命令**：把下面的 R 脚本与 qsub 小作业存到 `/d3/scratch/${USER}/m02/compgenome/`，
  检查并投递：

  ```bash
  cd /d3/scratch/${USER}/m02/compgenome
  grep -n 'conda activate\|Rscript' 02_pan_job.sh && qsub 02_pan_job.sh   # 日志 m02_pangenome.o<作业号>
  ```

  **qsub 小作业 02_pan_job.sh（完整文本，逐字保存）**：

  ```bash
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m02_pangenome
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_base
  cd /d3/scratch/${USER}/m02/compgenome
  Rscript 02_pangenome_analysis.R Orthogroups.GeneCount.tsv
  ```

  **个人作业脚本 02_pangenome_analysis.R（完整文本，逐字保存）**：

  ```r
  #!/usr/bin/env Rscript
  # m02 泛基因组划分 + 共享模式图 + 稀释曲线（教材 §11.4.4–11.4.5）
  # 输入：OrthoFinder 的 Orthogroups.GeneCount.tsv（比较脚本已拷到本目录）
  # 环境：ngs_ms_base（r-tidyverse；无 UpSetR，共享模式图用 ggplot2 自绘）
  suppressPackageStartupMessages({ library(tidyverse) })
  args <- commandArgs(trailingOnly = TRUE)
  infile <- if (length(args) >= 1) args[1] else "Orthogroups.GeneCount.tsv"
  SEED <- 20261110   # 课程设定：固定并记录随机种子
  REPS <- 100        # 每个 N 无放回抽 100 次（课程设定，非行业标准）
  counts <- read_tsv(infile, show_col_types = FALSE)
  sp <- setdiff(names(counts), c("Orthogroup", "Total"))
  stopifnot("物种列不足 2 列" = length(sp) >= 2)
  pres <- counts %>% select(all_of(sp)) %>% mutate(across(everything(), ~ as.integer(.x > 0)))
  n_sp <- ncol(pres); k <- rowSums(pres)
  # ① 互斥分类（unique 优先，与讲义 ⑤5.6 case_when 同口径；报告必须声明口径，教材 §11.4.4）
  cls <- case_when(k == n_sp ~ "core", k == 1 ~ "unique",
                   k / n_sp >= 0.95 ~ "softcore",
                   k / n_sp >= 0.15 ~ "shell", TRUE ~ "cloud")
  # n=4 时 softcore/cloud 档恒空，m=1 记 unique（教材 §11.5.2：95%/99%≡100%）
  out <- tibble(Orthogroup = counts$Orthogroup, n = n_sp, m = k, k_allowed = n_sp - k, Class = cls)
  write_tsv(out, "orthogroups_class.tsv")
  comp <- out %>% count(Class, name = "n_families")
  write_tsv(comp, "pangenome_composition.tsv")
  p1 <- ggplot(comp, aes(Class, n_families, fill = Class)) + geom_col(width = 0.65) +
    geom_text(aes(label = n_families), vjust = -0.4, size = 3.5) +
    scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
    labs(x = "Class", y = "Number of families", title = "Pan-genome composition") +
    theme_bw(base_size = 12) + theme(legend.position = "none")
  ggsave("fig2_pangenome_pie.png", p1, width = 6, height = 4.5, dpi = 300)
  # ② 共享模式图（路 B：柱 + 点阵保留交集身份；按株数汇总与 UpSet 不等价）
  patterns <- apply(pres, 1, function(r) paste(sp[as.logical(r)], collapse = "+"))
  ct <- tibble(pattern = patterns) %>% count(pattern, name = "n") %>% arrange(desc(n), pattern)
  ct$pid <- factor(ct$pattern, levels = ct$pattern)
  ymax <- max(ct$n); gap <- max(2, ymax / 6)   # 点阵行距随柱高缩放
  mem <- bind_rows(lapply(seq_len(nrow(ct)), function(i) {
    ss <- strsplit(ct$pattern[i], "+", fixed = TRUE)[[1]]
    tibble(pid = ct$pid[i], yv = -match(ss, sp) * gap) }))
  lab <- tibble(strain = sp, yv = -seq_along(sp) * gap)
  p4 <- ggplot() +
    geom_col(data = ct, aes(pid, n), fill = "#3C5488", width = 0.7) +
    geom_hline(yintercept = 0, color = "grey60") +
    geom_point(data = mem, aes(pid, yv), color = "#00A087", size = 3) +
    geom_text(data = lab, aes(x = 0.3, y = yv, label = strain), hjust = 1, size = 3) +
    scale_y_continuous(limits = c(-(n_sp * gap + 0.5 * gap), ymax * 1.15),
                       breaks = function(lims) pretty(c(0, ymax))) +
    scale_x_discrete(expand = expansion(add = c(2.4, 0.4))) +
    labs(x = "Presence pattern", y = "Number of families",
         title = "Sharing patterns (identity preserved)") +
    theme_bw(base_size = 11) + theme(axis.text.x = element_text(angle = 45, hjust = 1))
  ggsave("fig4_shared_patterns.png", p4, width = 7.5, height = 5, dpi = 300)
  # ③ 稀释曲线（中位数 + 四分位区间）与 Heaps 拟合 P(N) ≈ κ·N^γ
  set.seed(SEED)
  pan_med <- pan_lo <- pan_hi <- core_med <- core_lo <- core_hi <- numeric(n_sp)
  for (i in seq_len(n_sp)) {
    pans <- replicate(REPS, { s <- sample(sp, i); sum(rowSums(pres[, s, drop = FALSE]) > 0) })
    cors <- replicate(REPS, { s <- sample(sp, i); sum(rowSums(pres[, s, drop = FALSE]) == i) })
    pan_med[i]  <- median(pans); pan_lo[i]  <- quantile(pans, 0.25); pan_hi[i]  <- quantile(pans, 0.75)
    core_med[i] <- median(cors); core_lo[i] <- quantile(cors, 0.25); core_hi[i] <- quantile(cors, 0.75)
  }
  rf <- tibble(N = seq_len(n_sp), pan = pan_med, pan_lo = pan_lo, pan_hi = pan_hi,
               core = core_med, core_lo = core_lo, core_hi = core_hi)
  write_tsv(rf, "rarefaction_summary.tsv")
  lg <- lm(log(pan) ~ log(N), data = rf)   # n=4 只有 4 个点，γ 只作方法演示（教材 §11.4.5）
  cat(sprintf("Heaps fit on median curve: kappa = %.3f, gamma = %.3f\n",
              exp(unname(coef(lg)[1])), unname(coef(lg)[2])))
  p3 <- ggplot(rf) +
    geom_ribbon(aes(N, ymin = pan_lo, ymax = pan_hi), fill = "#4DBBD5", alpha = 0.3) +
    geom_line(aes(N, pan, color = "Pan-genome")) +
    geom_ribbon(aes(N, ymin = core_lo, ymax = core_hi), fill = "#E64B35", alpha = 0.15) +
    geom_line(aes(N, core, color = "Core")) +
    scale_color_manual(values = c("Pan-genome" = "#3C5488", "Core" = "#E64B35")) +
    scale_x_continuous(breaks = seq_len(n_sp)) +
    labs(x = "N genomes sampled", y = "Number of families", color = NULL,
         title = "Rarefaction curves (median, IQR)") + theme_bw(base_size = 12)
  ggsave("fig3_rarefaction.png", p3, width = 6, height = 4.5, dpi = 300)
  cat("Done: orthogroups_class.tsv / pangenome_composition.tsv / rarefaction_summary.tsv / fig2 / fig3 / fig4\n")  ```

- **UpSet 图的两条路**：`UpSetR` 不在任何课程环境 yml——路 A：课程环境补包后
  `library(UpSetR); upset(as.data.frame(pres), nsets = n_sp, order.by = "freq")`，
  存 `fig4_upset.png`；路 B（包未补时的默认路）：上面的脚本已用 ggplot2 自绘**共享
  模式图**——柱＋点阵保留交集身份（A+B 与 A+C 可区分），而「按出现株数汇总」的
  堆叠柱会丢掉交集身份，**两者不等价**（教材 §11.4.4 边界）。作业卡当前写死
  `fig4_upset.png`，环境缺包时交哪个名字的口径冲突已上报总编；未裁定前按教师
  当堂口径命名，并在报告方法节写明本次用哪条路、为什么。
- **产出**：`orthogroups_class.tsv`（每 OG 的 n、m、k_allowed、Class）、
  `pangenome_composition.tsv`、`rarefaction_summary.tsv`、`fig2_pangenome_pie.png`、
  `fig3_rarefaction.png`、路 B 的 `fig4_shared_patterns.png`（路 A 时为你自画的 fig4）。
- **检查点**：报告核心数必须同时给 `n`、`m`、`k` 并声明 unique 口径；core 占比 30–60%
  是讲义经验区间（非本数据实测、非判据）；曲线末端仍在变（pan 上升/core 下降）→ 不报
  确定核心数，只报趋势（教材 §11.4.5）。「开放/封闭」只是观测窗口内的趋势描述：同一
  生成过程，选近缘 12 株 γ=0.253、混簇 12 株 γ=0.317（合成算例，`python3 textbook/demos/
  ch11_pan_rarefaction.py --selftest`，rc=0）——换选株策略结论就变，不得写成物种属性（§11.5.3）。
- **出错信号**：阈值写「95% 核心」而不给 n/k → 回到 §11.5.2 改写；`library(UpSetR)`
  报 `there is no package called 'UpSetR'` → 走路 B，不算流程失败。

#### 步骤 10：CAFE5 基因家族扩张收缩（比较脚本的第二、三投；本课为方法演示）

- **目的**：演示「把家族拷贝数变化放回超度量时间树」的完整统计链。先讲死边界：
  **课程没有可靠校准的超度量时间树**，脚本里的 `TREE_ULTRA` 路径是占位——你自己
  造树（下述），并在方法里写明「相对时间近似、绝对速率无意义」（教材 §11.4.6）。
  本课 CAFE5 结果**不可解释为生物学结论**，只验收流程与判读。
- **命令**（造树 → 改副本 → 两次投递，全程计算节点）：

  ```bash
  # ① 建树拓扑：最低门槛路径——直接用步骤 8 产物 Results_*/Species_Tree/SpeciesTree_rooted.txt
  #    （脚本带 -M msa，OrthoFinder 已用单拷贝基因拼接建树，教材 §11.4.3；枝长是
  #    替换数，不能直接喂 CAFE5）。自己重建可用 mafft=7.520/iqtree=2.2.2 对
  #    Single_Copy_Orthologue_Sequences/ 比对拼接（讲义建议，本课未实跑），不作要求。
  # ② 转超度量时间树（r-ape 已在 ngs_ms_genome 声明；集群实测 unverified）：
  #    cd /d3/scratch/${USER}/m02 && Rscript -e 'tr <- ape::read.tree("SpeciesTree_rooted.txt");
  #      c <- ape::chronos(tr); ape::write.tree(c, "tree_ultrametric_1.nwk")'
  #    两棵不同标定各跑一次（如 chronos 不同 lambda），产 tree_ultrametric_1/2.nwk。
  # ③ 第二投（第一棵树）：编辑器改副本（行号为现版脚本）：
  #    L55–63（OrthoFinder 的 if/else 整块）→ 换成一句（聚类已完成，沿用不重跑）：
  #        RES=$(ls -d "${PROT_DIR}"/OrthoFinder/Results_*/ | tail -1)
  #      （若第一投用了 USE_CKPT=1 预跑结果，换成 RES="${CKPT}/orthofinder_results"）
  #    取消 L83–119 的注释（恢复 CAFE5 段）
  #    第 30 行  TREE_ULTRA=/d3/scratch/${USER}/m02/tree_ultrametric_1.nwk
  #    第 112 行 -o cafe_out  →  -o cafe_out_tree1    （两次运行输出目录必须分开，否则互相覆盖）
  #    grep -n 'RES=\|TREE_ULTRA=\|cafe5 -i' 02_orthofinder_cafe.sh   # 逐条确认
  #    qsub 02_orthofinder_cafe.sh
  # ④ 第三投（第二棵树）：把第 30 行 TREE_ULTRA 改为 tree_ultrametric_2.nwk、
  #    第 112 行 -o cafe_out_tree2，再次 qsub（qsub 按提交时脚本执行，改完再投才生效）。
  ```

  这条命令在做什么：脚本先构造 `cafe_input.tsv`（L84–94：剔除行和为 0 的家族、剔除
  单物种拷贝数 **≥100** 的超大家族——课程设定非官方阈值），打印过滤后家族数（L95）；
  再用 `ape::is.ultrametric` 自检树（L99–105，非超度量即 `exit 1`）；然后
  `cafe5 -i cafe_input.tsv -t "${TREE_ULTRA}" -p -o cafe_out_treeN`（L112）。`-p` 是
  `--poisson`（根频率分布），**不是**输出 p 值的开关；家族级 p 默认就写在
  `Base_family_results.txt`（v5.1 源码口径）。
- **产出**：`cafe_input.tsv`；`cafe_out_tree1/` 与 `cafe_out_tree2/` 下的
  `Base_family_results.txt`（家族级 p）、`Base_branch_probabilities.tab`（分支级，
  v5.1 源码为 `.tab` 后缀）、`Base_asr.tre`（祖先状态重建）。
- **检查点**：过滤后家族数与 L95 打印一致；家族级 p **必须 BH 校正后按 q 报告**
  （教材 §11.4.6：1,000 个家族、阈值 0.05 时全零假设期望 1,000×0.05=50 个原始阳性，
  设例算术）；显著家族占比异常高（课程经验线 >20%，**非文献阈值、只是排查线索**）时
  先查输入过滤与 λ，不写「整张表不可信」（脚本 L116–117 提示口径）；两树 Top 20
  重叠率对照是作业硬要求。
- **出错信号**：`Tree is not ultrametric` → 喂了替换数树或定标不对（教材 §11.5.4：
  五查＝二叉/有根/超度量/枝长单位/校准来源；强制超度量≠定年）；`Failed to initialize
  any models!` → 输入未过滤（全 0 家族/超大家族）或物种列序与树叶名不对应（讲义 ⑨-6）。
  `there is no package called 'ape'` → 环境没激活到 `ngs_ms_genome`。
- **交付物 `cafe_significant.tsv` 与 fig5（两投跑完，登录节点即可）**：CAFE5 不直接
  产出这两个交付物；家族级结果在 `Base_family_results.txt`（v5.1 源码 `write_results`
  口径，首行 `#FamilyID<TAB>pvalue<TAB>Significant at 0.05`）。在结果目录跑：

  ```bash
  # cafe_significant.tsv：BH 校正后按 q<0.05 筛选（base R 自带 p.adjust，无需装包）
  Rscript -e 'd <- read.table("Base_family_results.txt", header=FALSE, sep="\t", comment.char="#", col.names=c("FamilyID","p","sig")); d$q <- round(p.adjust(d$p,"BH"),6); write.table(subset(d,q<0.05)[,c("FamilyID","p","q")], "cafe_significant.tsv", sep="\t", quote=FALSE, row.names=FALSE)'
  # fig5_cafe_top.png：按 q 排序取 Top 10（方向判定见 Base_change.tab，本课按方法演示定位）
  Rscript -e 'suppressPackageStartupMessages(library(ggplot2)); d <- read.table("cafe_out_tree1/Base_family_results.txt", header=FALSE, sep="\t", comment.char="#", col.names=c("FamilyID","p","sig")); d$q <- p.adjust(d$p,"BH"); d <- head(d[order(d$q),],10); d$FamilyID <- factor(d$FamilyID, levels=rev(d$FamilyID)); g <- ggplot(d, aes(FamilyID, -log10(p), fill=q<0.05)) + geom_col() + coord_flip() + labs(x=NULL, y="-log10(p)", fill="q<0.05", title="Top 10 families (tree1)") + theme_bw(); ggsave("fig5_cafe_top.png", g, width=6, height=4, dpi=300)'
  ```

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果；「预期」列全部标「预期、未实测」。BUSCO 一栏必须写
> 库名与 `n`；泛基因组一栏必须写 `n`、`m`、`k` 与 unique 口径。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 2 k-mer | 主峰 D_k / 基因组大小估计 / 杂合度 / 重复比例 / Model Fit（仅诊断量） | × / bp / % / % / % | | 估计与 4.77 Mb 同量级（README 登记值）；偏差 >20% 为经验警戒线（讲义 ⑥6.1 带标）；无 90% 合格线（教材 8.4.4） |
| 3 组装 | contig 数 / 总长 / circ. | 条 / bp / Y-N | | 预期 1 条、4.7–5.2 Mb（README 判据，未实测）；circ.=Y 是阳性信号非完成证明（8.4.6）；contig >20 为线索 |
| 4 QUAST | N50 / L50 / misassembly / genome fraction | bp / 个 / % | | genome fraction >97%、misassembly 个位数（README 判据，未实测）；N50 与 misassembly 同读（8.4.7–8.4.8） |
| 5 BUSCO | C/S/D/F/M（同库同 n） | % | | C>97%（README 判据，未实测）；加法自检 C=S+D、C+F+M=100%（8.4.8）；不设 D 红线（8.6） |
| 6/7 注释 | 各株蛋白数 | 个 | | 预期 4,000–4,600/株（ug README §四，未实测）；>20% 离群＝排查线索（脚本 L51） |
| 8 体检 | Statistics_PerSpecies 各列基因数 / species-specific 计数 | 个 | | 各列同量级；某列高一个量级＝警报（11.5.1） |
| 9 划分 | core/softcore/shell/cloud/unique 计数 | 个，须报 n、m、k | | n=4 时 95%/99%≡100%（demo `--strains 4`，合成算术）；core 30–60% 仅经验参考 |
| 9 曲线 | 末端 pan 增量 / core 变化 / γ 与拟合窗口 | 个家族/株 / 趋势 / — | | 末端仍在变→不报确定核心数（11.4.5）；开放/封闭是趋势非物种属性（11.5.3） |
| 10 CAFE5 | 过滤后家族数 / 显著家族数（p 与 q）/ Top20 两树重叠率 | 个 / % | | p 必须 BH 校正后报 q（11.4.6）；重叠率两树对照是作业硬要求 |

## 5. 失效条件对照（教材 §11.5 / §8.5，本实验里在哪一步、看什么察觉）

1. **注释流程不统一制造假「菌株特异基因」**（§11.5.1）｜察觉：步骤 7 的蛋白数、
   步骤 8 的体检表——OrthoFinder 无任何报错，但某一列 gene 数/species-specific 计数
   比其他列高一个量级。合成形态：2,088–2,132 → 混入 1 株后 9,993/8,150、假特异 99.9%
   （`demos/ch11_annotation_bias.py --selftest`）。
2. **小样本上「95% 核心」与 100% 等价**（§11.5.2）｜察觉：步骤 9——n=4 时写「95%
   阈值」实际一株都不能缺；允许缺 1 株=3/4=75%。任何核心数同时报 n、m、k
   （`demos/ch11_core_threshold.py --strains 4 5 8 12 20 57 100`）。
3. **「开放/封闭」依赖采样与选株**（§11.5.3）｜察觉：步骤 9 稀释曲线——只取近缘株
   曲线更早变平；末端仍在变就不报确定核心数；报告 n、选株方式、抽样次数与种子、
   γ 与拟合窗口（`demos/ch11_pan_rarefaction.py --selftest`）。
4. **CAFE5 要求超度量时间树，替换数树不能用**（§11.5.4）｜察觉：步骤 10——
   `Tree is not ultrametric` 是响亮失败；更隐蔽的是强制超度量后通过格式检查、
   枝长语义仍是替换数，显著性系统性偏移。五查＋换一棵标定不同的树报 Top20 重叠率。
5. **只报连续性不报正确性**（§8.5.2）｜察觉：步骤 4——misassembly 栏空＝没给 `-r`；
   N50 变大同时 misassembly 变多＝错接被奖励（`demos/ch08_n50_vs_completeness.py
   --example 3`）。
6. **长读长做 k-mer 勘测 / 读长类型参数选错**（§8.5.3 精神）｜察觉：步骤 2 无主峰
   先查输入；步骤 3 总长暴涨＋contig 数暴涨＝`READ_TYPE` 选错（讲义 ⑨-4）。
7. **BUSCO 库联网失败**（§8.5.4）｜察觉：步骤 5 `Errno -3`＝节点无外网，登录节点
   预下载＋`--offline --download_path`；库名/n 写进报告，两套库的分数不可比。

## 6. 思考题（指向教材习题，不给答案）

1. 本课面板 n=4：按「存在比例至少 95%」「至少 99%」「100%」三种写法各需几株全有？
   允许缺 1 株对应的存在比例是多少？（教材 §11.7 习题 1 的 n=4 版 → §11.4.4、§11.5.2；
   可用 `demos/ch11_core_threshold.py --strains 4` 核对）
2. 某次聚类后的体检表（构造设例）显示三株基因数 5,124、5,098、7,642，species-specific
   群数 31、27、1,188。算第三株相对前两株的增幅与倍数，列三条竞争解释，并说明先做
   哪项检查、为什么不能把这 1,188 个群直接当候选毒力基因。（§11.7 习题 5 → §11.4.2、
   §11.5.1）
3. 一次 CAFE 分析检验 1,000 个家族（设例），原始 p<0.05 的有 60 个。全零假设、检验
   独立时期望阳性数是多少？为什么不能直接报这 60 个？BH 调整后的 q 是什么、不是
   什么？q 小能支持什么、不能支持什么？（§11.7 习题 7 → §11.4.6）
4. 有人把枝长为「每位点替换数」的树强制成超度量树喂给 CAFE5，程序没有报错。这棵树
   还缺什么？枝长语义错会怎样影响显著家族名单？给出三项核查动作。（§11.7 习题 8 →
   §11.4.6、§11.5.4）
5. 六条 contig 500/300/200/150/100/50 kb 求 N50/L50；前两条错接成 800 kb 后呢？
   这个反例说明 N50 与 misassembly 该是什么关系？（教材 §8.7 习题 3 → §8.4.7；
   可用 `demos/ch08_n50_vs_completeness.py --example 2` 核对）

## 7. 提交物

与 `08_assessment/master/assignments/m02_assembly_pangenome_assignment.md` 规格一致：

- **打包**：`学号_姓名_m02.zip`（≤200 MB，超出则去掉组装中间文件与 OrthoFinder 的
  `WorkingDirectory/`），解压后目录结构按作业卡：报告 `report.pdf`（正文 ≤10 页）＋
  `scripts/`（你的两个改后副本 + 两个个人作业脚本）＋ `results/`（genomescope_summary.txt、
  quast_report.tsv、busco_short_summary.txt〔含库名与版本〕、orthogroups_class.tsv、
  stats_per_species.tsv、cafe_significant.tsv〔p 与 BH 校正后的 q，生成见步骤 10〕）＋
  `figs/`（五张：fig1_kmer_histogram、fig2_pangenome_pie、fig3_rarefaction、fig4_upset〔路 A〕
  或 fig4_shared_patterns〔路 B，口径见步骤 9〕、fig5_cafe_top；标题/轴/图例英文）＋
  `env_snapshot.yml`（`conda env export --no-builds`）。
- **报告七节**：K-mer 特征估计／组装与连续性／完整性评估／k-mer 估计 vs 组装长度差异
  ＋三种成因取舍／泛基因组组成（计数须带 n、m、k 与选样方式）／基因家族扩张收缩
  （Top 10、p 与 q、**两棵不同标定树各跑一次、报 Top 20 重叠率——硬要求**）／
  「方法选择与结果可信度说明」一页四问（占 30%）。
- **时间**：m02 课后第 10 天 23:59 截止；迟交与重交规则按作业卡 ⑤。
- **诚实红线**：无参考或降级运行的检查，报告写明「未检查」；一切预期区间不得写成
  实测；CAFE5 结论按方法演示定位，不写适应性结论。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念/失效条件/习题） | `textbook/chapters/ch11/manuscript.qmd` §11.4 / §11.5 / §11.7 |
| 教材参照章（组装评估/失效条件） | `textbook/chapters/ch08/manuscript.qmd` §8.4 / §8.5 / §8.7 |
| 本专题讲义（原理细节、⑨ 常见错误） | `02_lectures/master/topic02_assembly_pangenome/02_assembly_pangenome_lecture.md` ⑤5.2–5.7／⑥／⑦／⑨ |
| 两个作业脚本（本指导按现版行号引用） | `03_code/master/scripts/02_assembly_pipeline.sh`、`02_orthofinder_cafe.sh`（均只读；改动走个人副本） |
| 两个个人作业脚本（本指导步骤 6/9 给全文） | 存到自己 scratch 后 qsub：Prokka 投递脚本、泛基因组 R 脚本 + qsub 小作业 |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch11_core_threshold.py`、`ch11_annotation_bias.py`、`ch11_pan_rarefaction.py`、`ch08_n50_vs_completeness.py`、`ch08_kmer_spectrum.py` |
| 数据说明、下载与预期判据 | `06_data/master/README.md` m02 块；`06_data/master/download_master.sh`；`06_data/undergraduate/README.md` §四（Prokka 预期） |
| 环境定义 | `07_envs/conda/env_master_genome.yml`（`ngs_ms_genome`）、`env_master_base.yml`（`ngs_ms_base`）、`env_ug_annotation.yml`（`ngs_ug_annot`，Prokka） |
| 作业规格 | `08_assessment/master/assignments/m02_assembly_pangenome_assignment.md` |
