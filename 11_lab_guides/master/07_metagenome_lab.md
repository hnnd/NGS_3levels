---
title: "实验指导 m07：宏基因组分析"
level: master
topic: m07
textbook: [ch19]
lecture: ../02_lectures/master/topic07_metagenome/07_metagenome_lecture.md
env: ngs_ms_microbiome
---

# 实验指导 m07：宏基因组分析

> 上机时手边打开。每步回答四件事：命令在做什么、敲什么、看到什么算对、看到什么说明错了。原理与判据在教材第 19 章（§19.4 概念、§19.5 失效条件），统计背景接第 18 章与第 12 章，设计与
> 混杂在第 13 章。检查点数字都带来源标签：**「ENA 实查」**是教材按 ENA Portal 逐字段核过的口径；**「课程自查线（未实测）」**是数据 README 的练习参照区间，不是合格线；**「合成算例」**
> 只对 demos 各自的生成模型成立；**「手算」** 给出输入与步骤、可计算器复核。真实样本的组装/分箱/分类本课未在集群复跑，标「集群未实测」的步骤按预期对待，结果以你自己的运行日志为入口。

## 0. 本实验对应什么

- **教材**：第 19 章 宏基因组（物种组成、组装分箱与功能），硕士层 LO19-01（两条路线）、LO19-02（去宿主与占比判读）、LO19-03（计数≠丰度）、 LO19-04（分箱双信号、MIMAG、弱阴性证据）；
  步骤 8 的组成性分析另接博士层 LO19-05/06，硕士以会用为度。**学时** 4 h（2 理论 + 2 实践，契约），作业建议上机 8–12 小时（组装与分箱是长作业）。
- **环境**：conda `ngs_ms_microbiome`（`07_envs/conda/env_master_microbiome.yml`）：MEGAHIT 1.2.9、MetaBAT2 2.15、checkm-genome 1.2.2、 eggNOG-mapper 2.1.11、samtools 1.17、R 4.3.1；
  Kraken2、Bracken、seqkit、ALDEx2、ANCOM-BC **未钉版本**——打印实装版本并记录（教材 19.3）。 **三个跨环境事实**：fastp 0.23.4 在 `ngs_ms_base`；Bowtie2 2.5.1 在
  `ngs_ms_transcriptome`、**不在**本环境 yml 里；CheckM2、Prodigal、DAS Tool、GTDB-Tk 全部课程 yml 都没有，用到时写「需自装」，不写成已装能力。
- **数据库不进环境**（讲义 ②）：Kraken2 Standard-8 约 8 GB、eggNOG 约 50 GB、CheckM 库约 1.4 GB（均为讲义 ② 的估计体量，非本机实测）、宿主索引视宿主而定。路径与版本登记在 `06_data/reference/README.md`，那是**登记表、
  不是实装证据**——本指导**未在线核验**集群侧是否已部署，§1 先查可用性，缺库就停下问教师/助教。
- **作业与计算纪律**：`08_assessment/master/assignments/m07_metagenome_assignment.md`，占课程总成绩 5%、「方法选择与结果可信度说明」占 30%。一切计算（fastp、Kraken2、组装、分箱、
  CheckM、eggNOG、seqkit 统计、R 分析与绘图）一律 `qsub` 投计算节点；登录节点只做下载、建环境、编辑、写作业、看日志。计算节点不通外网。

## 1. 实验前检查

- **前置模块**（讲义 ②，自测须能过）：`l0_01_linux`（`qsub -v`、`Eqw` 排查、`-hold_jid`）、`l0_04_formats`（SAM/BAM 与 FLAG：`-f 4` 与 `-f 12` 的口径）、`l0_05_qc`（单端可变长不能
  照抄双端 PE150 修剪参数）、`l0_06_stats`（p 值语义、多重检验）、`l0_03_conda`（数据库为什么不进 yml）。
- **核验工具链与跨环境依赖**（版本以 yml 为准；作业不继承交互 shell 的环境，每个作业脚本开头都要自己激活，主脚本 L16 已内置）：

  ```bash
  source /opt/miniconda3/bin/activate && conda activate ngs_ms_microbiome
  command -v megahit metabat2 checkm emapper.py samtools seqkit Rscript kraken2 bracken   # 九个命令行工具
  megahit --version; metabat2 -h 2>&1 | head -1
  conda list -n ngs_ms_microbiome | grep -iE 'bioconductor-(aldex2|ancombc|treesummarizedexperiment)'
  command -v bowtie2 && bowtie2 --version | head -1 || echo "本环境内没有 bowtie2"
  ```

  九个命令行工具与三个 R 包缺一个就别往下跑（`kraken2`/`bracken` 归步骤 7；`TreeSummarizedExperiment` 是 ANCOM-BC 分支的依赖，缺它时脚本只 warning 跳过、不会生成重叠表）。
  **登录节点只做包名清点（`conda list` 是纯元数据，不加载 R），真正的可加载性由步骤 8 的作业日志证明**——脚本对缺包只 warning 跳过。**主脚本的去宿主与比回两步调用 Bowtie2，而它不在本环境 yml 里**——缺失就停下报教师/助教确认集群实装与依赖裁决，不能声称主脚本能直接跑通，也不要静默混用环境（教材 19.3）；fastp 同理由步骤 1 的作业自己切 `ngs_ms_base`（版本见 §0）。
- **数据库与参考路径核验**（登录节点；`/data/db` 是登记表给的部署根，**以现场为准**）：

  ```bash
  ls -d /data/db/kraken2/Standard-8 /data/db/eggnog /data/db/checkm /data/db/host_bt2
  ls /data/db/kraken2/Standard-8/ | grep kmer_distrib   # 库内可用读长档，Bracken -r 只能取其中之一
  checkm data setRoot /data/db/checkm                   # 未配置时用这条把 CheckM 库指过去
  ls /data/db/host_bt2/*.1.bt2                          # 宿主 Bowtie2 索引（m07 用稻 IRGSP-1.0）
  ```

  四个 `ls -d` 有任何一个报 `No such file` 就是缺库——**路径不同先 `ls /data/db` 看有什么、再问助教，不要自己猜路径也不要自己建库**；缺库的步骤记「未完成、缺库」，不得写成「跑了但没
  结果」。Kraken2 查询把整个哈希表读进内存，`h_vmem` 必须 ≥ 库大小（8 GB 量级）。
- **合成自查预演**（在课程仓库根目录运行）：

  ```bash
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch19_host_depletion_tradeoff.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch19_lca_escalation.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch19_checkm_contamination.py --selftest
  ```

  三个脚本固定种子 20261104、全绿才算环境 OK：去宿主权衡 10/10、LCA 上浮 9/9、CheckM 污染度 8/8（合成算例，下文引用数值时都带这个标签）。 **第一个脚本的输出里现在还写着「必须下采样
  到等通量再比」，那是演示文案的旧说法**：教材 19.4.1 把它写成**可选敏感性分析**，方法学按教材口径写；演示的数值可引用，这句指令不要照抄（演示文本待总编修，冲突处以教材为准）。
- **出错信号**：`command not found` → 环境未激活成功（讲义 ② 的 30 秒自检同口径）；demos 任一 FAIL → 本机 Python 环境异常，先修再上课； `checkm data setRoot` 后仍为空 → 库未部署或
  路径不对，先问助教，否则主脚本 [4/5] 会静默跳过。

## 2. 实验数据

贯穿数据是 `PRJDB12800`「日本农田鸟枪法宏基因组」（水田 paddy vs 旱地 uplandfield）。全研究共 45 个 run，**课程取其中 12 个**：水田 6 个（北海道、爱知各一块田 × 3 重复）、旱地 6 个
（筑波、阿苏各一块田 × 3 重复）；子集边界必须写进报告方法学（教材 19.1）。12 个 run 已登记 `06_data/accessions.tsv`（L98 项目行 + L99–L110 逐个 run）：

| 分组 | 采样点 | 登录号 |
|---|---|---|
| paddy 水田 | 北海道 ×3 ／ 爱知 ×3 | `DRR336839` `DRR336851` `DRR336863` ／ `DRR336843` `DRR336855` `DRR336867` |
| uplandfield 旱地 | 筑波 ×3 ／ 阿苏 ×3 | `DRR336847` `DRR336871` `DRR336859` ／ `DRR336848` `DRR336872` `DRR336860` |

- **形态（决定本实验每一个参数的写法，ENA 实查，教材 19.1）**：12/12 单端（SINGLE）、读长 216–239 bp（可变）、Illumina MiSeq、2011 年采样；合计 1.326 GB（1.24 GiB）、合计 16 137 419
  条读段，单样本 303 063–2 319 023 条。数据 README 旧写法「约 1.1 GB、每样本 50 万–200 万条」与实查不符（低约 17%、两端出界），**本课一律按上面实查值验收**。
  读长那条要有个入口，别只记结论：12 个 run 逐个查 ENA 的 `read_count` 与 `base_count` 两栏、相除即得该 run 的平均读长，用
  `curl -s 'https://www.ebi.ac.uk/ena/portal/api/filereport?accession=DRR336839&result=read_run&fields=run_accession,read_count,base_count,library_layout&format=tsv'`（把登录号换掉即可）；
  逐个 run 算出来是 **204–247 bp**，12 个 run 合并（`Σbase_count ÷ Σread_count`）是 **225.5 bp**、落在教材 216–239 bp 之内。教材那句「216–239 bp」未说明按单 run 还是按合并算（按合并吻合、
  按单 run 略宽），不影响任何参数选择（`bracken -r` 指最接近的库档、不写死 150）；**报告里用你自己 `seqkit stats` 的 `avg_len` 并注明口径**，不要拿其中一套去否定另一套，判定权在你的表。
- **这条数据线的限制必须写进方法学**：它与第 18 章扩增子数据 `PRJDB13364`（布基纳法索铁毒稻田 16S，2017–2019 采样）**不是同一批采样**—— 跨大陆、跨年份、跨方法三重差异完全混杂，任何
  「16S 与鸟枪法导致丰度不同」的比较都不成立，只能作概念性对照（教材 19.5.4）。
- **低深度的预期**：这个深度下可能一个高质量 MAG 都分不出，属数据的真实状态而非流程失败；教学重点放在 read-based 组成与组成性差异分析（课程自查线（未实测），数据 README m07；教材
  19.6）。
- **下载**（登录节点，在课程仓库根目录运行；`~/NGS_3Levels` 换成你自己的仓库根目录）：

  ```bash
  cd ~/NGS_3Levels
  bash 06_data/master/download_master.sh --topic m07 --run --outdir /d3/scratch/${USER}/ngs/data
  ```

  产物落在 `/d3/scratch/${USER}/ngs/data/m07/`，按 ENA 原文件名落盘并写 `SHA256_MANIFEST.tsv`。**这批 run 全是单端，每个 run 一个 FASTQ，文件名以 `ls` 实见为准（不要假定 `_1`/`_2`
  后缀）**；看到校验告警先重下该 run（下载脚本幂等，会跳过完好的）。
- **工作目录**：分析根 `/d3/scratch/${USER}/ngs/m07/`（下建 `raw/ clean/ nohost/ out/ bracken/ results/ logs/`）。原始数据只做软链接，**不要放家目录**。

## 3. 实验步骤

> 每步固定五栏：目的 / 命令 / 产出文件 / 检查点 / 出错信号。主脚本 `03_code/master/scripts/07_metagenome_assembly.sh` 一次投递跑完五步（去宿主 → MEGAHIT → 比回与 MetaBAT2 → CheckM
> 1.x → eggNOG），步骤 3–6 是它五个阶段的逐个检查；fastp、Kraken2/Bracken 是**讲义扩展、没有对应课程脚本**，命令来自讲义 ⑤ 5.1–5.2 的单端改写。脚本名、参数名、输出文件名已逐个与现
> 版源码 grep 核对。**在哪敲**同 §0：登录节点只做下载、编辑、看日志与 `ls`/`head`/`grep` 级检查，其余一律 `qsub`；改脚本走个人副本（`cp → 改指定行 → grep 确认 → qsub`），不得「投递
> 后再补参数」。下文四个作业文件建在 `/d3/scratch/${USER}/ngs/m07/`，头四行（`-S`/`-N`/`-cwd`/`-j y`）相同，`#$ -j y` 把 stderr 并入 `meta_${S}.o<作业号>`。

### 步骤 0：数据就位、文件名归一、读段统计（登录节点 + 1 个统计作业）

- **目的**：确认 12 个单端 FASTQ 完整，按实见文件名生成统一清单与规范软链名，再统计读段数与读长分布。
- **命令**：

  ```bash
  cd /d3/scratch/${USER}/ngs/data/m07
  shopt -s nullglob; FQS=(*.fastq.gz *.fq.gz)              # 后缀以实见为准，两种都收
  echo "${#FQS[@]}"; ls | grep -E '_1|_2' || echo "无 _1/_2 后缀：确认是单端"
  mkdir -p /d3/scratch/${USER}/ngs/m07/{raw,clean,nohost,out,bracken,results,logs}
  : > /d3/scratch/${USER}/ngs/m07/samples.txt              # 重跑时清零，避免清单翻倍
  for f in "${FQS[@]}"; do
    S=$(basename "$f" | sed -E 's/(\.fastq|\.fq)\.gz$//')
    ln -sf "$PWD/$f" /d3/scratch/${USER}/ngs/m07/raw/${S}.fastq.gz
    echo "$S" >> /d3/scratch/${USER}/ngs/m07/samples.txt
    gzip -t "$f" 2>/dev/null && echo "${S} OK" || echo "${S} BROKEN"   # 整文件校验，不用 zcat|head（管道会吞掉解压错误）
  done
  sort -o /d3/scratch/${USER}/ngs/m07/samples.txt /d3/scratch/${USER}/ngs/m07/samples.txt
  cd /d3/scratch/${USER}/ngs/m07        # 同一个统计作业后面再用两次，只换 TARGETS/TAG
  cat > m07_stats.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m07_stats
  #$ -cwd
  #$ -j y
  #$ -pe smp 2
  source /opt/miniconda3/bin/activate ngs_ms_microbiome
  cd /d3/scratch/${USER}/ngs/m07
  seqkit stats -a -T ${TARGETS} > logs/stats_${TAG}.tsv
  EOF
  qsub -v TARGETS="/d3/scratch/${USER}/ngs/m07/raw/*.fastq.gz",TAG=raw m07_stats.job
  wc -l samples.txt; qstat -u ${USER}
  ```

  这条命令在做什么：ENA 原文件名不可假定，所以**先按实见文件名解析出登录号**，再以 `raw/${S}.fastq.gz` 建软链（不拷数据），后续作业只认这个规范名；`samples.txt` 是唯一的样本清单（12 个登录号见 §2 表）。
  `seqkit stats` **默认不输出 N50**，`-a` 才带 N50 与长度分位数；`-T` 输机器可读 TSV（含 `num_seqs`/`min_len`/`max_len`/`avg_len` 等列）。`TARGETS`、`TAG` 经 `qsub -v` 传入（SGE 作业不继承终端变量；通配符在作业内展开）。
  **这一行必须用双引号**：`${USER}` 要在这里就展开成你的用户名，写成单引号会把 `${USER}` 原样带进作业，`seqkit` 按字面找目录直接报 `no such file`。步骤 3、4 复用同一个作业，只换 `TARGETS`/`TAG`（具体值见各步命令）。
- **产出**：`samples.txt`（12 行）；`raw/` 下 12 个软链；`logs/stats_raw.tsv`。
- **检查点**：文件数 = `samples.txt` 行数 = `raw/` 软链数 = 12，每行形如 `DRR3368xx` 且与 §2 表逐一相符、每行回显 `OK`；`stats_raw.tsv` 的 `num_seqs` 合计 **16 137 419**、单样本 **303 063–2 319 023**。
  读长看 **`avg_len` 一栏**（第 7 列），**不要拿 `min_len`/`max_len` 对照平均读长**：单条读段从几十 bp 到三四百 bp 都有（可变长文库的常态），这两个数是极端值，永远落不进平均读长区间。教材 19.1 写的
  「216–239 bp」是另一个口径（见 §2 的说明）；**以你 `stats_raw.tsv` 的实测为准**，与教材口径的出入写进方法学，不要为了让数字落进区间去改数据或改参数。`seqkit` 版本未钉，记实装版本。
- **出错信号**：出现 `_1/_2` → 拿错了双端 run，回 §2 表核对登录号；`BROKEN` 或行数不足 → 重下该 run；`sed` 解析出的名字不像登录号 → 先 `ls` 看真实文件名再改正则，不要硬凑；
  `seqkit: command not found` → 作业内没激活环境；`stats_raw.tsv` 为空 → 看 `m07_stats.o*` 里 `TARGETS` 是否被 `qsub -v` 截断。

### 步骤 1：fastp 单端质控（讲义扩展，课程脚本不含此步）

- **目的**：按单端可变长数据修剪（3' 端质量下降是系统性的），不套双端参数。
- **命令**（写作业投 qsub；fastp 0.23.4 在 `ngs_ms_base`，它不在主环境里）：

  ```bash
  cat > /d3/scratch/${USER}/ngs/m07/m07_fastp.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m07_fastp
  #$ -cwd
  #$ -j y
  #$ -pe smp 8
  source /opt/miniconda3/bin/activate ngs_ms_base
  cd /d3/scratch/${USER}/ngs/m07
  set -euo pipefail
  for S in $(cat samples.txt); do
    fastp -i raw/${S}.fastq.gz -o clean/${S}.fq.gz \
          --cut_tail --cut_window_size 4 --cut_mean_quality 20 \
          --length_required 50 -w 8 -h logs/${S}.fastp.html -j logs/${S}.fastp.json
  done
  [[ $(ls clean/*.fq.gz | wc -l) -eq 12 ]] || { echo "[ERROR] clean 下不足 12 个文件，先修再往下"; exit 1; }
  EOF
  cd /d3/scratch/${USER}/ngs/m07 && qsub m07_fastp.job && qstat -u ${USER}
  ```

  讲义 ⑤ 5.1 的单端改写——只给 `-i/-o`，**不给** `-I/-O` 与 `--detect_adapter_for_pe`（那是双端参数）；`--cut_tail` 而非 `--cut_front`（3' 端质量系统性下降，`l0_05_qc` 第 6 题）；
  `--length_required 50` 丢弃短于 50 bp 的读段。这些是课程指定的运行参数，不是结果合格线。
- **产出**：`clean/${S}.fq.gz`（12 个）、`logs/${S}.fastp.html/.json`（12 对）。
- **检查点**：`qstat` 里 `m07_fastp` 消失（`qw`→`r`→无）且 `clean/` 下有 12 个文件，**才允许进步骤 2**；读 JSON 里修剪前后读段数与长度分布，填记录表「原始/修剪读段数」两栏。**没有
  课程实测的修剪保留率门槛**（教材 19.3：单端可变长不照抄 PE150，机制归第 6 章）。
- **出错信号**：过滤后接近空表 → 先查参数与数据布局（是不是把单端文件按双端喂了），对应教材 §19.5.1 的排查思路；`exit 1` 且日志说文件不足 12 → 看哪个样本失败，单独重投；某样本原始
  读段数显著偏离 ENA 实查区间 → 回步骤 0 查完整性。

### 步骤 2：投递主脚本（一次跑 [1/5]→[5/5]）

- **目的**：对 12 个样本各投一个作业，完成去宿主 → 组装 → 分箱 → CheckM → eggNOG。
- **命令**（登录节点；每个样本一条，变量值不含逗号；`-N meta_${S}` 让作业名带样本名）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m07
  HOST_IDX=/data/db/host_bt2/IRGSP-1.0      # 宿主索引前缀，先按 §1 核验；跳过则留空
  EGGNOG_DB=/data/db/eggnog                 # eggNOG 库目录，先按 §1 核验；缺库则留空
  for S in $(cat samples.txt); do
    qsub -N meta_${S} -hold_jid m07_fastp \
         -v R1=/d3/scratch/${USER}/ngs/m07/clean/${S}.fq.gz,R2=,\
  SAMPLE=${S},OUTDIR=/d3/scratch/${USER}/ngs/m07/out/${S},\
  HOST_IDX=${HOST_IDX},EGGNOG_DB=${EGGNOG_DB} \
         ~/NGS_3Levels/03_code/master/scripts/07_metagenome_assembly.sh
  done
  qstat -u ${USER}     # qw 排队 / r 运行 / Eqw 报错
  ```

  `-v` 把变量传进作业，`R1` 必填（脚本 L18，缺了作业直接报 `必须指定 R1`）；**本数据是单端，`R2` 留空**，脚本据此自动走单端分支（L19、L41–43）；`OUTDIR` 显式指到 scratch（默认落在 `-cwd` 下）；
  `-hold_jid m07_fastp` 让这 12 个作业等 fastp 全部跑完才启动（`qsub` 是异步投递，不挂依赖时会在 `clean/` 还没生成时就投出去，12 个作业集体秒退）。`HOST_IDX` 是宿主 Bowtie2 索引前缀（m07 为水稻 IRGSP-1.0），
  教师明确跳过这步则留空并在记录表写「跳过」；`EGGNOG_DB` 是 eggNOG 库目录（**脚本变量名是 `EGGNOG_DB`，不是讲义手动命令里的 `EGGNOG_DATA_DIR`**，两个名字别混，否则 [5/5] 会静默跳过）。脚本头固定 `-pe smp 24`、`h_vmem=10G`（L6–7），线程取 `NSLOTS`——**换更大文库须重估内存与线程，不要照抄**。
- **产出**：每样本 `out/${S}/` 下的五步产物（各步见步骤 3–6）；作业日志 `meta_${S}.o<作业号>`（在投递目录，`#$ -cwd`）。
- **检查点**：`qstat` 12 个作业排队/运行，作业名一眼对得上样本；作业日志逐样本留存（宿主比对率、各步 `[n/5]` 标记、WARN/跳过提示都在里面）。
- **出错信号**：`Eqw` → `qstat -j <ID> | grep -A5 error`（常见：`-v` 行被换行截断、变量含逗号/空格、R1 路径不存在、`-hold_jid` 的作业名写错）；作业秒退且日志报 `必须指定 R1` → 变量
  没传进去；12 个作业同时报「找不到 clean 文件」→ fastp 还没跑完就投了，重投即可。

### 步骤 3：查去宿主（主脚本 [1/5]）

- **目的**：拿到逐样本的非宿主读段数与宿主占比，判断本批离散与组间偏移；为步骤 7 准备输入。
- **命令**（作业结束后，登录节点轻量检查 + 建软链）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m07
  grep -H 'overall alignment rate' meta_*.o*      # 文件名前缀即样本名，一行一对
  for S in $(cat samples.txt); do
    ln -sf /d3/scratch/${USER}/ngs/m07/out/${S}/clean.fq.gz nohost/${S}.fq.gz
  done
  ls nohost/ | wc -l                              # 期望 12
  qsub -v TARGETS='out/*/clean.fq.gz',TAG=nohost m07_stats.job   # 非宿主读段数
  ```

  脚本对单端用 `bowtie2 -U … | samtools view -b -f 4 -F 256`（保留未比对、排除次级比对，L41–43）产出 `clean.fq.gz`；`overall alignment rate` 打到 stderr，`#$ -j y` 把它合进作业日志
  ——**脚本不单独写 host.log，从 `meta_${S}.o*` 里 grep**（讲义 ⑤ 的 `logs/${S}.host.log` 是另一条路线）。脚本保持默认灵敏度、**没有 `--very-sensitive`**（L31–32）：过严会把与宿主局
  部同源的微生物读段删掉。软链到 `nohost/${S}.fq.gz` 是给步骤 7 的**重命名**：12 个 `clean.fq.gz` 同名，直接 `cp` 会互相覆盖。
- **产出**：`nohost/` 下 12 个软链；每样本 `out/${S}/clean.fq.gz`；宿主占比与非宿主读段数（日志与 `logs/stats_nohost.tsv`）。
- **检查点**：
  1. 逐样本记录原始读段数、`overall alignment rate`（注明参考版本与比对参数）、非宿主读段数，填记录表；先看本批 12 个样本的离散，
     **不存在「保留率必须 > 某值」的合格线**（课程自查线（未实测）：土壤样本保留率 > 90% 仅为参照，数据 README m07；教材 19.4.1）。
  2. 组间对照：paddy 6 vs upland 6 的宿主占比有无系统性偏移。若大到足以改变结论，处置是**先报两组原始/非宿主读段数**，再把等通量下采样作为
     **可选敏感性分析**（报下采样前后两套结果）写进方法学（教材 19.4.1：下采样只对齐通量，不消除参考库差异、选择性误删与批次混杂）。合成算例
     的通量算术：两组原始通量相同时，宿主占比 85% vs 40% → 有效非宿主通量比 `(1−0.85)/(1−0.40) = 0.25`（手算；
     `demos/ch19_host_depletion_tradeoff.py --selftest` 同式断言）。
  3. 严/松权衡的量级感（合成算例，seed 20261104）：阈值从严时宿主残留占原宿主读段 20.05%→1.26%，但微生物误伤占全部微生物读段 0.86%→4.56%，
     且被杀的微生物里保守同源类占 44.16%、典型类仅 0.158%——误伤有选择性，删得越干净越危险（教材 19.5.1）。
- **出错信号**：作业 exit 3（去宿主后没有剩余读段）→ 先查 `HOST_IDX` 是否选对（`ls ${HOST_IDX}*` 看索引在不在）；某样本保留率明显低于本批其余样本 → 先怀疑宿主参考选错或组织裂解异常，**
  不要先调严参数**（教材 §19.5.1）；比对率全样本接近 0 → 索引前缀填错；`nohost/` 只有 1 个文件 → 用了 `cp` 没用按样本名的 `ln -sf`。

### 步骤 4：查组装与分箱（主脚本 [2/5]、[3/5]）

- **目的**：评估单样本组装的规模与连续性，确认深度表列结构，评估 MetaBAT2 分箱结果。
- **命令**（登录节点轻量检查；contig 统计用步骤 0 的同一个作业）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m07
  qsub -v TARGETS='out/*/megahit/final.contigs.fa',TAG=asm m07_stats.job
  head -2 out/DRR336839/depth.txt        # 表头列数应为 5（3+2S，S=1）
  ls out/DRR336839/bins/                 # bin.1.fa bin.2.fa …（可能为空或很少）
  grep -h 'No bins\|metabat' meta_*.o*   # 分箱阶段的真实姿态
  ```

  脚本用 `megahit -r <clean.fq.gz> -t ${THREADS} -o out/${S}/megahit --min-contig-len 1000` 组装（单端参数在 L55，调用在 L56），产物 `megahit/final.contigs.fa`（L57）；脚本**不传 k 参数**，
  走 MEGAHIT 1.2.9 默认 k=21,33,…,141 共 11 个（手算 `(141−21)/12+1=11`，教材 19.4.3），`--min-contig-len 1000` 丢弃短于 1 kb 的重叠群（分箱器用不上，早丢省内存）。之后把本样本读段比回组装
  （`bowtie2-build` → `samtools sort/index` → `jgi_summarize_bam_contig_depths --outputDepth depth.txt asm.bam`，L63–67），再 `metabat2 -i final.contigs.fa -a depth.txt -o out/${S}/bins/bin -t ${THREADS} -m 1500`（L68）。
  深度表头为 contigName、contigLen、totalAvgDepth，**每个参与比回的 BAM 再贡献一对「样本均值/样本方差」列，总列数 3+2S**（手算规则；本脚本 S=1 → 5 列，教材 19.5.7）。**脚本不传 `--unbinned`**，没有 `*.unbinned.*` 产物，不要要求它出现。
- **产出**：`logs/stats_asm.tsv`；每样本 `asm_idx.*`、`asm.bam(.bai)`、`depth.txt`、`bins/bin.*.fa`（若有箱）。
- **检查点**：
  1. `logs/stats_asm.tsv` 记每样本重叠群条数、总长、N50。N50 **只能由长度分布算**（`seqkit stats -a` 给的就是这个口径；总长 ÷ 条数是平均长度，
     两者不能互换，教材 19.6）。判读：宏基因组 N50 小是常态，**不要按单基因组标准判读**；课程自查线（未实测）：土壤样本 N50 1–5 kb 仅为参照
     （数据 README m07、教材 19.4.3），明显离谱时先查深度与株系异质性，不设硬线。
  2. `head -2 depth.txt` 数列应为 5。深度仍在（均值+方差），但**跨样本共变消失**——单样本正是教材 19.5.7 写的退化形态，不是「只剩 TNF」也不是
     「必然失败」。
  3. 箱数记进记录表；课程自查线（未实测）：这个深度下可能一个高质量 MAG 都分不出，箱少或 `No bins` 是可能结果而非流程失败（数据 README m07；
     教材 19.6）。比回率（clean 读段比回组装的 alignment rate）本脚本不产出，属讲义扩展：要算需自建 `bowtie2 -x asm_idx -U clean.fq.gz` 并从日志
     grep，只作参照（教材 19.4.3）。想分箱更好走步骤 9 的跨样本拓展（12 个样本文库共同深度表 3+2×12=27 列），现脚本没做，不能声称已完成
     （教材 19.4.4）。
- **出错信号**：`megahit: … already exists`（讲义 ⑨ 第 1 条）→ 换 `OUTDIR` 或确认断点续跑条件；作业被 SGE 杀、`qacct` 显示 `exit_status 137` → **疑似 OOM**（137 只说明收到 SIGKILL，
  也可能是别的 kill）：对照 `qacct -j <ID>` 的 `maxvmem` 与 `-l h_vmem`、看日志是否停在组装，本脚本未传 `-m`、固定 `h_vmem=10G`，换大数据须同时重估两者（讲义 ⑨ 第 2 条原则）；N50
  极小且重叠群极多 → 低深度碎片化是可能结果，先查输入读段数再下结论（教材 19.4.3）；箱数偏少按顺序查：① depth 列对数（`3+2S`）→ ② BAM 个数 → ③ contig 长度下限与碎片化（教材 §19.5.7）；
  `jgi_summarize_bam_contig_depths` 报 `BAM file is not sorted` → 比回管道里 sort/index 顺序错了（讲义 ⑨ 第 5 条同型问题）。

### 步骤 5：查 CheckM 质量表（主脚本 [4/5]）

- **目的**：按 MIMAG 给每个箱判级，识别混箱。
- **命令**（登录节点轻量检查）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m07
  ls out/DRR336839/checkm_summary.tsv && head -3 out/DRR336839/checkm_summary.tsv
  grep -h 'WARN\|跳过' meta_*.o*          # lineage_wf 失败或缺库跳过
  ```

  脚本先确认 CheckM 1.x 库已配置（`checkm data setRoot` 或作业内 `CHECKM_DATA_PATH`，L72），再跑
  `checkm lineage_wf -x fa -t ${THREADS} out/${S}/bins out/${S}/checkm --tab_table -f out/${S}/checkm_summary.tsv`（L73–75）。**脚本用的是 CheckM 1.x，不是 CheckM2**（L76 自述）；
  两版算法不同、数值不可互换，报告必须写清版本（教材 19.4.5）。脚本对 `lineage_wf` 失败只打印 WARN 并继续——**日志末尾写「完成」不等于质量表已产出**。
- **产出**：成功时每样本 `checkm_summary.tsv`（每箱一行：完整度、污染度等）；失败时只有 WARN。
- **检查点**：
  1. 先查文件存在、表头与箱数，再读数值；无表即未完成本步（缺库会跳过、失败只 WARN，两者都不报错退出）。
  2. **若步骤 4 分箱数为 0（`bins/` 为空），CheckM 无输入、报 WARN 且不出表，这是正常的级联现象**——记录表填「箱数 0、质量表免评」，在报告里写明
     原因，**不算流程失败、也不扣你自己的分**；它证明的是「这份数据分不出 MAG」，不是「CheckM 装坏了」（教材 19.6）。
  3. 判级按 MIMAG（Bowers 2017，教材 19.4.5）：High-quality 要完整度 >90% 且污染度 <5% **且**检出全长 23S/16S/5S rRNA 与 ≥18 种 tRNA；Medium-quality
     为完整度 ≥50% 且污染度 <10%；Low-quality（完整度 <50%）一般不单独用于结论。Medium 的边界是 **≥50**，恰好 50.0% 算 Medium。
  4. 污染度口径：CheckM 1.x 污染度 = 各单拷贝标记座位超出 1 份的副本数之和 ÷ 座位总数 `Σmax(份数−1,0)/M`，不是「出现重复的座位比例」；完整揉进 k 个
     基因组约 `(k−1)×100%`，**可超过 100%，是结果不是报错**（教材 19.4.5）。合成算例（`demos/ch19_checkm_contamination.py --selftest`，M=100，
     seed 20261104）：干净箱 94.9%/0.0%，两基因组全合并 100.0%/100.0%、三基因组 100.0%/200.0%、部分合并 99.5%/148.0%——「完整度很高、污染度爆表」
     是几个残缺基因组各交出不重叠片段的典型形态。另：**「完整度 95% 却没有 16S」是二代短读的常态**（rRNA 操纵子约 4.5–5.2 kb 高度重复、短读跨不过、
     组装必断），不是失败数据（手算：16S≈1.5 kb + 23S≈2.9 kb + 5S≈0.12 kb；教材 19.4.5）。
- **出错信号**：污染度 >100% → 先算箱体量与标记基因拷贝数判断揉进几个基因组；处置是第二个分箱器 / DAS Tool 精化（DAS Tool 未装，属另装扩展）或丢弃， **严禁手动删 contig 把数字调下
  来**（教材 §19.5.3）；质量表缺失却报「完成」→ 回作业日志查 WARN/跳过原因；「高完整度、零污染」也不等于干净——分类学嵌合要 GUNC 补检（未装，属另装扩展）。

### 步骤 6：查 eggNOG 注释（主脚本 [5/5]）

- **目的**：拿到整份组装的功能注释，界定结论只到遗传潜力。
- **命令**（登录节点轻量检查）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m07
  ls -lh out/DRR336839/eggnog.emapper.annotations
  wc -l out/DRR336839/eggnog.emapper.annotations
  head -2 out/DRR336839/eggnog.emapper.annotations
  ```

  仅当 `EGGNOG_DB` 非空且目录存在才执行（L85）：`emapper.py -i final.contigs.fa --itype metagenome -o out/${S}/eggnog --data_dir ${EGGNOG_DB} --cpu ${THREADS}`（L86–87）——**直接对
  整份重叠群注释，不先经 Prodigal 翻译**（Prodigal 未装；讲义 ⑤ 5.5 的「MAG→蛋白→注释」路线是另装扩展）。脚本读的就是 `EGGNOG_DB`。
- **产出**：`eggnog.emapper.annotations` 等以 `eggnog` 为前缀的 emapper 输出。
- **检查点**：文件存在、行数、KO/COG 字段；统计 COG 大类分布填记录表。环境样本注释率低属真实状态（未培养微生物的未知基因家族），**没有课程实测的注释率阈值**，不得给注释率设「正常/
  异常」的数值判据（教材 19.4.6）；结论只到「遗传层面具备……的潜力」，不写到表达或活性（教材 19.4.6）。
- **出错信号**：日志出现「[跳过] eggNOG 数据库未部署」而报告又要求 COG/KO 图 → 缺输出即未完成本步，先去确认库路径，**不要**把跳过写成「注释率为零」；注释几乎全空且样本近缘（非本数
  据形态）→ 先查库路径与基因预测参数（教材 19.4.6）。

### 步骤 7：Kraken2/Bracken 物种组成（讲义扩展，课程脚本不含此步）

- **目的**：read-based 路线出属/种两层组成，与 assembly-based 互相印证。
- **命令**（先按步骤 0 的统计与 §1 的库清单选定读长档，再写作业投 qsub）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m07
  cut -f1,7 logs/stats_raw.tsv | column -t            # 第 1 列文件名、第 7 列 avg_len（216–239 bp）
  ls /data/db/kraken2/Standard-8/ | grep kmer_distrib  # 只有清单里的档能用
  cat > m07_kraken.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m07_kraken
  #$ -cwd
  #$ -j y
  #$ -pe smp 16
  #$ -l h_vmem=12G
  source /opt/miniconda3/bin/activate ngs_ms_microbiome
  cd /d3/scratch/${USER}/ngs/m07
  KRAKEN2_DB=/data/db/kraken2/Standard-8
  RL=250          # ← 换成 ls 实见清单里与 216–239 bp 最接近的那档；下一行是防错闸门
  ls ${KRAKEN2_DB}/database${RL}mers.kmer_distrib >/dev/null 2>&1 \
    || { echo "[ERROR] 库里没有 ${RL} 档：按上一条 ls 的实见改 RL 再重投"; exit 1; }
  for S in $(cat samples.txt); do
    kraken2 --db ${KRAKEN2_DB} --threads 16 --confidence 0.1 \
            nohost/${S}.fq.gz --report bracken/${S}.kreport --output bracken/${S}.kout
    bracken -d ${KRAKEN2_DB} -i bracken/${S}.kreport -o bracken/${S}.bracken -r ${RL} -l S -t 10
  done
  EOF
  qsub m07_kraken.job && qstat -u ${USER}
  ```

  输入是步骤 3 建好重命名软链的 `nohost/${S}.fq.gz`（不是同名 `clean.fq.gz`）。作业里的 `RL=250` 只是**占位示例**，不是本库的答案：必须按上一条 `ls` 的实见改成清单里与 216–239 bp 最接近的那档，
  第二行的 `ls … || exit 1` 会在投递后就拦下错档（Bracken 自己报错前你可能已等了一晚上）。`--confidence 0.1` 要求至少 10% 的 k-mer 支持同一谱系路径，从源头压随机假阳性（教材 19.4.2 的 C/Q 语义）；
  `bracken -l S` 重估到种，`-t 10` 少于此数的物种不再分配。**`-r` 必须同时满足两件事**：① 与实际读长（216–239 bp）最接近；② 在库内 `kmer_distrib` 清单里确有其档。清单里只有 100/150 这类档时，
  就选最接近的并在方法学写明「库档与实测读长的错配」，**不要照抄 150**（那是双端 PE150 时代的值）。Bracken 校正的是 LCA 上浮造成的分配损失，**不校正基因组大小**——大基因组物种的读段份额仍高于细胞份额（教材 19.4.2）。
  `new_est_reads` 是**重分配后的估计值**（`kraken_assigned_reads` + `added_reads`），不是观测计数：报告须注明「估计」，并在方法学声明本课是把估计值当计数做组成性分析（教材 19.4.8）；估计值被当作整数计数喂给 ALDEx2/ANCOM-BC 的可接受性由教师裁决。
- **产出**：每样本 `bracken/${S}.kreport`（六列：累计相对丰度、子树读段数、直接读段数、等级代码、Taxonomy ID、学名）、`${S}.kout`、`${S}.bracken` （7 列，含 `taxonomy_id`、
  `new_est_reads`）。
- **检查点**：
  1. 先看每份报告首行 `unclassified`：课程自查线（未实测）Kraken2 分类率 30–60%、未分类 40–70% 是环境样本的常态（数据 README m07；教材 19.4.2）——只作
     「是否离谱」参照，不作合格线；明显异常先查库版本与构建日期。
  2. 属/种两层同看：属层稳定而种层名单骤缩 → 优先怀疑库缺近缘种（LCA 上浮），不是样本问题（教材 19.5.2）。合成算例
     （`demos/ch19_lca_escalation.py --selftest`，每库状态 20 万条合成读段，seed 20261104）：目标种在库时种水平 34.9%、停在属 65.1%；删掉后种水平
     0.0%、未分类 35.0%；只剩一个姐妹种时 64.8% 被错误种接管——种层「恢复」可能是假精确。
  3. 末尾只有 1–3 条读段支持的长尾「物种」：先列为候选，用阈值前后名单对比、mock/独立证据复核后再决定截断，**不一概判假、也不直接当发现**（教材
     19.4.2、19.5.2）；你自己设的最小读段数/相对丰度阈值必须写进方法学，并报告阈值前后的物种数之差。
- **出错信号**：`unable to allocate memory for hash table` → `h_vmem` 小于库大小（Standard-8 约 8 GB，作业给 12G；讲义 ⑨ 第 3 条）；`bracken` 报找不到
  `database${RL}mers.kmer_distrib` → `RL` 与清单不符，按 `ls` 实见改 `RL` 再重投（**不要**新建分布文件）；六列结构读不懂 → 回教材 19.4.2 报告列义； `unable to open file` →
  `nohost/` 里没有 `${S}.fq.gz`，回步骤 3 的重命名软链。

### 步骤 8：组成性分析与两法差异丰度（`07_compositional_analysis.R`）

- **目的**：亲眼见伪相关 → 对真实丰度表做 CLR/零值敏感性 → ALDEx2 与 ANCOM-BC 两法取共识。
- **命令**（三步按序，全部计算都在作业里跑；登录节点只写文件）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m07
  # (1) metadata：两列、制表符分隔，sample 名与 abundance 表列名必须完全一致
  printf 'sample\tgroup\n' > results/metadata.tsv
  for S in DRR336839 DRR336851 DRR336863 DRR336843 DRR336855 DRR336867; do echo -e "${S}\tpaddy"  >> results/metadata.tsv; done
  for S in DRR336847 DRR336871 DRR336859 DRR336848 DRR336872 DRR336860; do echo -e "${S}\tupland" >> results/metadata.tsv; done
  wc -l results/metadata.tsv                              # 期望 13（1 表头 + 12 样本）
  cut -f2 results/metadata.tsv | sort | uniq -c          # 期望 paddy 6、upland 6（表头 group 另计 1 行）
  ```

  ```bash
  # (2) 存成 merge_bracken.R：12 个 .bracken 合并成行=类群、列=样本的整数计数表
  cat > /d3/scratch/${USER}/ngs/m07/merge_bracken.R <<'EOF'
  fs <- list.files("bracken", pattern = "\\.bracken$", full.names = TRUE)
  long <- do.call(rbind, lapply(fs, function(f) {   # 摊成长表，按 taxonomy_id 汇总就不怕同名
    b <- read.delim(f); sp <- b[b$taxonomy_lvl == "S", c("taxonomy_id", "name", "new_est_reads")]
    sp$sample <- sub("\\.bracken$", "", basename(f)); sp
  }))
  if (is.null(long) || !nrow(long)) stop("bracken/ 里没有种水平行，先确认步骤 7 跑完")
  mat <- as.data.frame.matrix(xtabs(new_est_reads ~ taxonomy_id + sample, data = long))   # 缺格记 0
  ids <- rownames(mat); mat[] <- lapply(mat, as.integer)
  nm <- unique(long[, c("taxonomy_id", "name")]); nm <- nm[match(ids, nm$taxonomy_id), ]
  write.table(nm, "results/taxon_names.tsv", sep = "\t", quote = FALSE, row.names = FALSE)
  write.table(data.frame(taxon_id = ids, mat, check.names = FALSE),
              "results/abundance.tsv", sep = "\t", quote = FALSE, row.names = FALSE)
  EOF
  ```

  ```bash
  # (3) 一个作业跑完：伪相关演示 + 合并 + 两法对比
  cat > /d3/scratch/${USER}/ngs/m07/m07_da.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m07_da
  #$ -cwd
  #$ -j y
  #$ -pe smp 8
  source /opt/miniconda3/bin/activate ngs_ms_microbiome
  cd /d3/scratch/${USER}/ngs/m07
  Rscript ~/NGS_3Levels/03_code/master/scripts/07_compositional_analysis.R results/demo_part1
  Rscript merge_bracken.R
  Rscript ~/NGS_3Levels/03_code/master/scripts/07_compositional_analysis.R \
      results results/abundance.tsv results/metadata.tsv
  EOF
  cd /d3/scratch/${USER}/ngs/m07 && qsub m07_da.job && qstat -u ${USER}
  ```

  `metadata.tsv` 必须是**制表符**两列（`read.delim` 默认 tab；写逗号会解析成单列然后 `stop`）；脚本读入时强制列名与 `metadata$sample` 集合相等、按 metadata 排序，只处理**两组**比较（L80–90），
  预过滤保留在 ≥ `max(2, floor(0.1×样本数))` 个样本中出现的类群（L96–99，12 样本即 ≥2）。第 2 部分对比伪计数 0.5 与 1.0 的 CLR 位移；第 3 部分 ALDEx2（`mc.samples=128, test="t", denom="all"`，显著 = `wi.eBH<0.05` 且 `|effect|>1`，L146–153）
  与 ANCOM-BC（`p_adj_method="BH", prv_cut=0, struc_zero=TRUE, alpha=0.05`，找 `q_group*` 列，L163–171）各跑一次。**这些都是课程选定的运行参数，不是实测生物判据**；合并键取 `taxonomy_id` 而非学名（同名不同 taxid 会让按名字合并出错）。
- **产出**：`results/demo_part1/` 下 `fig_spurious_correlation.png`、`spurious_correlation.tsv`；`results/` 下 `abundance.tsv`、`taxon_names.tsv`、`clr_zero_sensitivity.tsv`、
  `fig_clr_zero_sensitivity.png`、`clr_matrix.tsv`、`aldex2_results.tsv`、`ancombc_results.tsv`；**两法都成功**才有 `overlap_summary.tsv` （aldex2_sig/ancombc_sig/both/union/jaccard
  五行）与 `consensus_taxa.tsv`。
- **检查点**：
  1. 第 1 部分现跑记录值（R 4.5.2，脚本内 seed 20260829、n=200）：绝对丰度 `r=+0.007`、相对丰度 `r=-0.241`（教材 19.4.8 同口径；你的环境版本不同，
     末位可能略有差异，以实跑为准）——负相关完全由「总和为 1」造出来。
  2. 喂表前必查两件事：全表最大值是否 ≤1；每列之和是否接近 1。两条同时成立就是相对丰度表，**ALDEx2/ANCOM-BC 要整数计数**；比例表喂进去不报错、照常
     出 p 值，是静默错误（教材 §19.5.6）。脚本的 `max(cts) <= 1` 警告出现时不要忽略（脚本 L90）。
  3. 报告口径固定四行（教材 19.4.8）：两法各自的显著类群数与名单、交集、Jaccard、单法独有候选降级为探索性假说。Jaccard 手算练习：`8/6/2 →
     2/(8+6−2) = 0.167`（教材 19.9 第 9 题同式）；脚本在 Jaccard < 0.5 时会警示——重叠度低本身就是要报告的发现，说明结论对方法选择敏感；记录表里
     只填你跑出的数。课程环境真实数据的第 2/3 部分未预跑（集群未实测），不预填任何显著类群数。
- **出错信号**：列名不一致/组数不是两组/`metadata` 用了逗号 → 脚本明确 `stop`（防样本错配）；缺包 → 脚本 warning 跳过且**不会**生成重叠表——「没有重叠表」不能用空表冒充「无共识」，
  先补装包重跑（作业要求两法都跑）；只跑出一种方法的显著名单 → 同上，重叠度是评分点；`abundance.tsv` 首列不是 `taxon_id` → 合并脚本最后一行写错了列顺序。

### 步骤 9（选做拓展）：个人副本改造

- **目的**：把单样本流程扩成讲义 ⑤ 5.3–5.4 的跨样本形态，或把 Kraken2 并入主流程。
- **命令**（一律个人副本，不改课程公共脚本）：

  ```bash
  cp ~/NGS_3Levels/03_code/master/scripts/07_metagenome_assembly.sh \
     /d3/scratch/${USER}/ngs/m07/07_meta_coassembly.sh
  # 用编辑器改副本（改动前先 grep 核对行号）：
  #   混合组装：READS_ARGS 改为 -r "$(ls clean/*.fq.gz | paste -sd,)"（gzip 是二进制，绝不能 cat）
  #   跨样本 depth：把全部样本的 BAM 传给 jgi_summarize_bam_contig_depths（总列数 3+2S）
  grep -n 'READS_ARGS\|jgi_summarize\|kraken' 07_meta_coassembly.sh
  # 投副本。变量照步骤 2 写全（R1 只是必填项，混合组装真正吃的是 READS_ARGS）；示例用第一个样本：
  qsub -N m07_coasm -v R1=/d3/scratch/${USER}/ngs/m07/clean/DRR336839.fq.gz,R2=,\
SAMPLE=coasm,OUTDIR=/d3/scratch/${USER}/ngs/m07/out/coasm 07_meta_coassembly.sh
  ```

- **产出**：改造后的个人作业脚本与它的产物。
- **检查点**：跨样本分箱必须先把多个样本**分别比回同一套组装**再合并 BAM——深度不会「天然跨样本」（教材 19.4.3）；改完用 `grep` 逐条确认改到位再投递。
- **出错信号**：分箱更差 → 跨样本株系多态性加剧气泡与嵌合是混合组装的固有代价（教材 19.4.3），不是改错了；内存暴涨 → 输入与图规模同步放大，`h_vmem` 与 `megahit -m` 要配对重估；读段
  文件打不开 → 逗号列表里混进了不存在的路径。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果。标「本批实测」的栏填你自己跑出的数；标「未实测参照」的判据只用来判断结果是否离谱，不得写成合格线。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 0 数据 | 每样本读段数 / 长度范围 | 条 / bp | | ENA 实查：单样本 303 063–2 319 023、合计 16 137 419、216–239 bp（教材 19.1） |
| 1 fastp | 每样本原始/修剪后读段数 | 条 | | 本批实测；无课程阈值（教材 19.3） |
| 3 去宿主 | 每样本 overall alignment rate（注明参考版本与参数）/ 非宿主读段数 | % / 条 | | 本批离散对照；>90% 仅未实测参照（README m07）；组间偏移处置见教材 19.4.1 |
| 4 组装 | 每样本重叠群条数 / 总长 / N50 | 条 / bp / bp | | N50 由长度分布算（`seqkit stats -a`），不由总长÷条数反推（教材 19.6）；1–5 kb 仅未实测参照 |
| 4 分箱 | depth.txt 列数 / 箱数 | 列 / 个 | | 列数 = 3+2S（本脚本 S=1 → 5，手算）；箱少非必然失败（教材 19.5.7） |
| 5 质量 | 每箱完整度 / 污染度 / rRNA / tRNA / MIMAG 级别 | % / % / 有无 / 种 / 级 | | High >90/<5 且 rRNA+tRNA 齐全；Medium ≥50/<10（Bowers 2017，教材 19.4.5）；无 bin 填「免评」 |
| 6 注释 | 注释行数 / COG 大类分布 / 目标基因完整性 | 行 / 分布 / 文字 | | 无课程阈值；结论只到遗传潜力（教材 19.4.6） |
| 7 分类 | 每样本 unclassified 比例 / 分类率 / Bracken `-r` 用的库档 | % / % / bp | | 30–60% 仅未实测参照（README m07、教材 19.4.2）；库档错配写进方法学 |
| 7 分类 | 属/种两层候选数、阈值前后物种数之差 | 个 | | 阈值写进方法学（教材 19.4.2） |
| 8 差异丰度 | ALDEx2 显著数 / ANCOM-BC 显著数 / 交集 / 并集 / Jaccard | 个 / 个 / 个 / 个 / 0–1 | | 本批实测；Jaccard 公式 \|A∩B\|/\|A∪B\|（教材 19.4.8）；零占比只记录实际 `zero_frac` |

## 5. 失效条件对照（教材 §19.5，本实验里在哪一步察觉）

1. **去宿主同源误伤（§19.5.1）**｜察觉：步骤 3。逐样本 grep `overall alignment rate` 看本批离散，保留率偏低的样本先查宿主参考再谈参数；组间占比有系统差时先报两组原始/非宿主通量，等通量下采样只作可选敏感性分析（严参数代价见合成算例：误伤 0.86%→4.56% 且高度选择性）。
2. **LCA 上浮与假精确（§19.5.2）**｜察觉：步骤 7。属/种两层同看：属稳种缩查库缺近缘种；种层「恢复」但只剩一个姐妹种时是假精确（合成算例 64.8%）；查库版本、构建日期、`unclassified`、
   mock 校准，以及 `-r` 用的库档。
3. **CheckM 污染度 >100% 是结果不是报错（§19.5.3）**｜察觉：步骤 5。完整度与污染度同时高 = 部分嵌合；先算箱体量与拷贝数，用第二分箱器/DAS Tool 精化或丢弃，不手动删 contig；合成算例 S2/S3/S4 给量级（100%/200%/148%）。
4. **m06/m07 非同批采样（§19.5.4）**｜察觉：写方法学时。与第 18 章扩增子数据只作概念性对照，丰度差异不可归因于测序方法（教材 19.9 第 10 题：完全混杂）。
5. **MAG 缺基因不等于无功能（§19.5.5）**｜察觉：步骤 5/6 写结论时。合规写法是「在该 MAG 的当前组装中未检出」，不写「不具备」；补证据可把基因探针比回原始读段深度图（命中还须证明归属）
   或用长读长闭合染色体。
6. **相对丰度喂 ALDEx2/ANCOM-BC 不报错（§19.5.6）**｜察觉：步骤 8 喂表前。查全表最大值是否 ≤1、每列之和是否约 1；看脚本的 `max(cts)<=1` 警告；确认行=类群、列=样本、首列 `taxon_id`。
7. **单样本深度失去跨样本共变（§19.5.7）**｜察觉：步骤 4。`head -2 depth.txt` 数列（应 5 列）；箱少依次查列对数、BAM 数、contig 长度与组装碎片化；要共变就做步骤 9 的跨样本拓展。

## 6. 思考题（教材 §19.7 习题 1–6，不给答案）

> 下面每题的数字都给了复现入口：合成算例跑 `textbook/demos/ch19_*.py --selftest`，手算写在题内；标「设例」的是教材题面的假设值，判读只用题内给出的判据（教材 19.4.5 的 MIMAG 阈值）。

1. 用本数据回答：200 份样品（教材题面设例）的「哪些属与抑病相关」与单个富集物的「拿完整基因组读基因簇」分别该走哪条路线、放弃什么？（§19.7 习题 1 → 19.4.1）
2. 若 12 个样本的宿主占比出现一个明显离群值，你的排查顺序是什么？两组均值差多少时你会考虑等通量敏感性分析、方法学要写哪三项？用题给的两个宿主占比算一次交比值：
   `(1−0.85)/(1−0.40) = 0.25`（手算，与合成算例同式）。（§19.7 习题 2 → 19.4.1、19.5.1）
3. 一个库缺目标种的环境样本，报告给出未分类 35.0%、属层合计 65.0%、种层 0.0%，末尾还有一批 1–3 条读段的「物种」——逐条判读，并说明 `--confidence` 与最小读段阈值各压什么。（数值取自
   `demos/ch19_lca_escalation.py --selftest` 的 D1 状态；§19.7 习题 3）
4. 某样本组装 N50 3 kb、只分出 2 个箱、`depth.txt` 只有一对样本均值/方差列——按可能性排三个病因并各给一个检查动作；哪些属数据限制、哪些属流程配置？（N50 与列数是设例；§19.7 习题 4 →
   19.4.4、19.5.7）
5. 五行 CheckM 结果：`94.9%/0.0%`、`100%/100%`、`100%/200%`、`99.5%/148.0%`、`61.5%/13.5%`——按 MIMAG 判级；148.0% 那行怎么处置、为什么不能手动删 contig；`94.9%/0.0%` 那行能否直接申
   报 High？（全部取自 `demos/ch19_checkm_contamination.py --selftest` 的 S1–S5；§19.7 习题 5）
6. 某 MAG（设例）完整度 91%、污染度 2%、未检出 *nifH*——按 MIMAG 能判到哪一级、证据能写到什么程度？给两条补证据路径及各自剩余的不确定性。（91%/2% 为教材题面设例，判读入口教材 19.4.5；§19.7 习题 6 → 19.4.6、19.5.5）

## 7. 提交物

- **对应作业**：`08_assessment/master/assignments/m07_metagenome_assignment.md`。打包 `学号_姓名_m07.zip`（≤ 200 MB，**不打包 BAM、 contigs、bins**），内含 `report.pdf`（正文 ≤ 10
  页、六节齐全）、`scripts/`（你实际用的作业脚本，含本指导里的四个 `.job` 与 `merge_bracken.R`）、 `results/`（各 TSV）、`figs/`（图内标题/轴/图例一律英文）、`env_snapshot.yml`（`conda env export --no-builds`）。
  截止 m07 课后第 12 天 23:59。六节标题、最小读段数阈值要求与评分 40/30/30 见作业 ④。
- **交付文件名映射（照抄作业要求的名字，内容对应清楚写进报告）**：

  | 作业要的文件 | 本课实际产出 | 怎么得到 |
  |---|---|---|
  | `results/assembly_stats.txt` | `logs/stats_asm.tsv` | `cp logs/stats_asm.tsv results/assembly_stats.txt`（同一份 `seqkit stats -a -T` 结果；作业那一栏还要求「reads 比回率」，本脚本不产出，按步骤 4 的说明自建或写明未做） |
  | `results/host_removal.tsv` | `meta_*.o*` 里的比对率 + `logs/stats_raw.tsv` + `logs/stats_nohost.tsv` | 汇总成 `sample/raw_reads/nonhost_reads/nonhost_Gb/align_rate` 五列 TSV（`nonhost_Gb = sum_len ÷ 1e9`，取自 `stats_nohost.tsv`） |
  | `results/bracken_species.tsv` | `results/abundance.tsv` + `results/taxon_names.tsv` | 种水平估计读段数矩阵（按 `taxonomy_id` 合并） |
  | `results/da_overlap.tsv` | `results/overlap_summary.tsv` | `cp results/overlap_summary.tsv results/da_overlap.tsv`（内容一致，报告注明来源） |
  | `results/checkm2_quality.tsv` | 只有 `checkm_summary.tsv`（CheckM 1.x） | 见下「不得改名冒充」 |
  | `results/eggnog_summary.tsv` | `out/${S}/eggnog.emapper.annotations` | 从注释表的 `COG_category` 列按类计数汇总成 `sample/COG/genes` 三列；缺库跳过则按「未完成」写明 |
  | `results/gtdbtk_taxonomy.tsv` | **无**（GTDB-Tk 未装） | 报告注明「未做及原因」，不得留空文件、不得用 Kraken2 的种名冒充 MAG 分类 |
  | `scripts/metagenome_pipeline.sh`、`scripts/compositional_analysis.R` | 主脚本副本 + 本指导步骤 8 的 R 调用 | 交**你实际投递的**脚本（个人副本与 `merge_bracken.R` 一并交），不是课程原版 |
  | `figs/fig1_taxa_composition.png`、`fig2_mag_quality.png`、`fig3_spurious_corr.png`、`fig4_da_venn.png` | fig3 有现成产物（`results/demo_part1/fig_spurious_correlation.png`），fig1/2/4 需自己画 | fig3 用 `cp` 改名（图题已英文）；fig1/2/4 见下「三张图的画法」 |

- **不得改名冒充**：作业要求 `checkm2_quality.tsv`，而课程环境是 CheckM 1.2.2、脚本产出 `checkm_summary.tsv`，CheckM2 与 GTDB-Tk 均未安装。**不得把 CheckM 1.x 的表改名冒充
  CheckM2**（两版数值口径不可互换）：提交 `checkm_summary.tsv` 原名文件，在报告第 4 节写「质量评估用 CheckM 1.x `<实装版本>`； CheckM2/GTDB-Tk 未装，故未提供 `checkm2_quality.tsv`
  与分类学归属」。作业规格/课程现状的冲突已上报总编；学生按上面处理并写明，不要自行变通成「改名交付」。
- **三张图的画法**（一律写成作业投 qsub，登录节点只查看；图内文字用英文）：
  - **fig1 物种组成**：读 `results/abundance.tsv` + `results/taxon_names.tsv`，按列求相对丰度后取每样本 top-N 属/种（其余并为 `Others`），`barplot(..., beside = FALSE)` 堆叠，横轴样本、纵轴相对丰度、按 group 上色——让 paddy/upland 的组间差异一眼可见，**不要把全部类群堆上去**。
  - **fig2 MAG 质量**：读 `checkm_summary.tsv`，横轴 Complete、纵轴 Contamination 画散点，加 MIMAG 两条参考线（90% 与 5%）；无箱的样本图上注明「No bins」，不要留空图。
  - **fig4 两法重叠**：从 `aldex2_results.tsv` 与 `ancombc_results.tsv` 各取显著名单画两圆韦恩（有 `eulerr` 用 `venn()`，没有就用 `plot.new()` + 两圆 + 交并集数字）；**圆心面积与数字必须成正比**，图题写清两条判据（`wi.eBH<0.05 且 |effect|>1` / `q<0.05`）。
- **诚实红线**：报告里每个数字来自你自己的运行日志；本指导中所有「未实测参照」「课程自查线（未实测）」与合成算例数字不得写成你的实测结果；跳过某步（如不做去宿主、缺库跳过
  CheckM/eggNOG）要在记录表与报告中写明，不得只在报告里写「已完成」。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念/失效条件/习题/写法模板） | `textbook/chapters/ch19/manuscript.qmd` §19.4 / §19.5 / §19.7 / §19.6 |
| 本讲讲义（原理细节、② 数据库说明、⑤ 操作命令、⑥ 结果解读、⑨ 排查） | `02_lectures/master/topic07_metagenome/07_metagenome_lecture.md` |
| 主脚本（去宿主→组装→分箱→CheckM 1.x→eggNOG，单/双端自适应） | `03_code/master/scripts/07_metagenome_assembly.sh` |
| 组成性分析脚本（伪相关/CLR/两法对比） | `03_code/master/scripts/07_compositional_analysis.R` |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch19_host_depletion_tradeoff.py`、`ch19_lca_escalation.py`、`ch19_checkm_contamination.py` |
| 数据、登录号、下载与数据库登记 | `06_data/master/README.md` m07 节；`06_data/accessions.tsv` L98–L110（项目行 + 12 run）；`06_data/master/download_master.sh`；`06_data/reference/README.md`（Kraken2 Standard-8、eggNOG、CheckM 库、宿主索引；**登记表，实装以集群现场为准**） |
| 环境定义 | `07_envs/conda/env_master_microbiome.yml`（`ngs_ms_microbiome`）、`env_master_base.yml`（fastp）、`env_master_transcriptome.yml`（Bowtie2） |
| 作业与评分 | `08_assessment/master/assignments/m07_metagenome_assignment.md` |
