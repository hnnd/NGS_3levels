---
title: "实验指导 u05：序列比对与 BAM 处理"
level: undergraduate
topic: u05
textbook: [ch07]
lecture: ../02_lectures/undergraduate/unit05_alignment_bam/05_alignment_bam_lecture.md
env: ngs_ug_base
---

# 实验指导 u05：序列比对与 BAM 处理

> 上机时手边打开的这份文件。每一步都回答四件事：这条命令在做什么、敲什么、看到什么算对、看到什么说明错了。原理与判据在教材第 7 章（§7.4 概念、§7.5 失效条件），这份指导只放操作与自查入口。**本科课程没有为本实验登记任何比对率、深度、重复率的数值预期区间**（教材 §7.6 边界 3），检查点只写「对得上账」与定性判据；集群上跑真实数据的步骤本课未实测，按「预期」对待，不得把预期写成实测。

## 0. 本实验对应什么

- **教材**：第 7 章 序列比对：读段在参考上找位置；本实验覆盖本科学习目标 LO07-01（索引与查询代价边界）、LO07-02（排序/索引/BAM 统计与坐标契约）、LO07-03（BaseQ 与 MAPQ、重复区两个方向）、LO07-04（完整性验收四件套）。
- **学时**：u05 为 4 学时线上自学单元；本实验是其上机部分，产出的 BAM 与审计日志是 u07（IGV 浏览器加载）与 u08（长读长回贴自己组装的基因组）的输入。
- **环境**：conda 环境 `ngs_ug_base`（`07_envs/conda/env_ug_base.yml`，钉 bwa 0.7.17、bowtie2 2.5.1、samtools 1.17、bedtools 2.31.0、fastp 1.3.6）。
- **计算纪律**：比对、排序、建索引、重复标记、**全文件扫描**（zcat 数行、`samtools view` 全 BAM 统计、合成 demo 复现）一律 `qsub` 投递计算节点；登录节点只做下载、建目录、编辑和 `samtools --version`、`samtools view -H`、按区间 `view -c`（走 `.bai` 索引）这类秒级自检（在登录节点直接跑多线程比对会被 OOM 杀掉，典型指纹是日志里一行 `Killed`）。

## 1. 实验前检查

- **前置模块**（讲义 ②，先确认自测能过）：`l0_01_linux` Q03/Q07/Q10（管道与重定向、作业提交）、`l0_04_formats` Q04/Q09（SAM 列与 FLAG/CIGAR）、`l0_05_qc` Q05/Q06/Q10（clean 数据是比对输入）。本讲不依赖 `l0_06_stats`。
- **激活环境并核验工具链**（与讲义 ② 同款）：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  bwa 2>&1 | head -3            # 期望版本 0.7.17
  bowtie2 --version | head -1   # 期望版本 2.5.1
  samtools --version | head -1  # 期望版本 1.17
  ```

  这条命令在做什么：SGE 作业不继承你终端里的 conda 变量，每个作业脚本开头都要自己激活环境（u04/u06 实验指导同款写法）。版本以环境 yml 的 pin 为准；讲义 ⑨ 开头的 0.7.19 / 2.5.5 / 1.22 不是课程环境版本，报错指纹可能略有差异，以你环境里实际行为为准（教材 §7.3）。
- **预期**：三个版本号与上面一致。`command not found` 一类报错 → 环境没激活成功（课程脚本的前置检查也会在同一处报错退出，脚本里写了同款提示）。
- **出错信号**：版本对不上 → 先查 `conda env list` 确认激活的是 `ngs_ug_base`，不要带着错误环境往下跑（教材 §7.3）。

## 2. 实验数据

本实验有两条轨道，**步骤相同，数据不同，数字不得互搬**（教材 §7.6 边界 2）。登录号全部已登记 `06_data/accessions.tsv`：

| 轨道 | 读段（clean 输入） | 参考 | 用途 |
|---|---|---|---|
| 练习轨 | `SRR2584863` 双端（E. coli 演示 run，ENA 登记 1,553,259 条读段）——第 6 章没有清洗过它，按步骤 0 自行下载并用第 6 章同款 fastp 参数清洗 | `GCF_000005845.2`（E. coli K-12 MG1655，1 条序列、4,641,652 bp，登记值） | 主练习：本指导步骤的命令都以它为例 |
| 主线轨 | `ERR15732342`（CIX4481 Illumina 双端，1,579,368 条读段、228,911,011 bp，名义深度 48.0×）经第 6 章清洗后的 clean 文件（步骤 0 直接复用） | 同株完成图 `GCA_987216485`（4,768,212 bp，登记值） | 选做：把课程主线数据也走一遍同一流程 |

- **数字口径**：1,579,368 / 228,911,011 / 48.0× 是登录号元数据换算（228,911,011 ÷ 4,768,212，教材 §7.1 列了同一除法）；`06_data/undergraduate/README.md` §2.1 只给约数（229 Mb、约 48×）。`SRR2584863` 的 1,553,259 条读段来自 ENA run 元数据（2026-11-10 实查），两端压缩文件各约 183 / 191 MB（ENA `fastq_bytes` 元数据）。练习轨的参考长度（4,641,652 bp）只属练习轨，不要搬到 Xoo 主线；主线数据也没有登记任何比对率预期。
- **clean 文件从哪来（两轨不同，先对号入座）**：主线轨的输入就是**你在第 6 章（u04）清洗好的产物** `qc/clean/ERR15732342_R*.clean.fq.gz`，步骤 0 软链过来即可；第 6 章**没有**清洗过 `SRR2584863`，它的 clean 文件要按步骤 0 从原始读段现做（讲义 ⑤5.3 说「上一讲清洗产出」，指的是清洗**方法**来自第 6 章，不是文件已备好）。两轨的共同输入形态都是双端 `*.clean.fq.gz`——把带接头的原始数据直接投喂比对器会让末端软剪切激增（讲义 ② 的典型薄弱症状）；还没跑完第 6 章的先回去补。
- **工作目录**（建在 scratch 不建家目录；比第 6 章多一个 `raw/` 放练习轨原始读段）：

  ```bash
  mkdir -p /d3/scratch/${USER}/ngs_u05/{ref,raw,clean,bam,logs} && cd /d3/scratch/${USER}/ngs_u05
  ```

- **数据自查**（往下做之前）：练习轨的双端行数对账放在步骤 0 的清洗作业末尾自动做（`PAIRED_OK` 写进 `logs/clean_lines.txt`）；主线轨的双端行数已在第 6 章查过，这里 `ls -lL clean/` 不爆红即可——真不同步，比对脚本的验收与 bwa 的配对检查还会再抓一次（出错信号 → 教材 §7.5.2 对账前提）。

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出 / 检查点 / 出错信号。命令里的脚本名、参数名、输出文件名与 `03_code/undergraduate/scripts/05_align_and_sort.sh` 现版逐字一致（本指导修订时已逐个核对，见任务回执）。课程没有在集群真实跑完过全流程，本指导不写任何预期数值区间。
>
> **在哪敲命令**：下文所有路径以 `/d3/scratch/${USER}/ngs_u05` 为根。用 `qsub` 投递时先 `cd` 到想放作业日志的目录；课程脚本不带 SGE 作业头，下文给最小作业脚本写法（`-S /bin/bash` + `-pe smp <N>` + `-l h_vmem=<M>G`，与 u04/u06 实验指导已验收写法一致）。
>
> **占位符纪律（复制命令前必读）**：作业脚本里的 `<课程仓库路径>` 是占位符，**不得原样粘贴**——Bash 把 `<` 当输入重定向，作业会秒退（报错形如 `bash: 课程仓库路径: No such file or directory`）。统一处理三步：① 定义 `REPO=<课程仓库路径>`（换成教师公布的真实路径）；② `sed -i "s|<课程仓库路径>|${REPO}|g" <作业脚本>`；③ `grep -n '<课程仓库路径>' <作业脚本>` 必须无输出，才算替换干净、可以投递。

### 步骤 0：数据就位（练习轨下载+清洗；主线轨复用第 6 章产物）

- **目的**：让 clean 双端文件在作业排队之前就位，并把来源和完整性当场核清。
- **命令（主线轨，登录节点）**：

  ```bash
  cd /d3/scratch/${USER}/ngs_u05
  ln -sf /d3/scratch/${USER}/ngs_u04/qc/clean/ERR15732342_R1.clean.fq.gz clean/
  ln -sf /d3/scratch/${USER}/ngs_u04/qc/clean/ERR15732342_R2.clean.fq.gz clean/
  ls -lh clean/        # 两端各一个 .fq.gz，指向真实存在
  ```

- **命令（练习轨 · 登录节点：查地址、下载、校验）**：

  ```bash
  cd /d3/scratch/${USER}/ngs_u05/raw
  # ① 从 ENA 登记入口查这个 run 的官方地址与 md5（m01 讲义同款查询；地址以 fastq_ftp 列为准）
  curl -s "https://www.ebi.ac.uk/ena/portal/api/filereport?accession=SRR2584863&result=read_run&fields=run_accession,read_count,fastq_md5,fastq_ftp&format=tsv" -o runinfo_SRR2584863.tsv
  cat runinfo_SRR2584863.tsv    # read_count 应 1,553,259；fastq_ftp 列是两端文件地址
  # ② 下载两端原始文件（课程修订时已核验以下地址可下；中断用 wget -c 续传，别全量重下）
  wget -c https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR258/003/SRR2584863/SRR2584863_1.fastq.gz
  wget -c https://ftp.sra.ebi.ac.uk/vol1/fastq/SRR258/003/SRR2584863/SRR2584863_2.fastq.gz
  # ③ 按 fastq_md5 列逐一校验（m01 讲义：md5 是唯一能证明下载完整的手段）
  md5sum SRR2584863_1.fastq.gz SRR2584863_2.fastq.gz
  ```

- **命令（练习轨 · 清洗，qsub 最小作业；fastp 参数与第 6 章实验指导步骤 3 逐字相同）**：

  ```bash
  cat > /d3/scratch/${USER}/ngs_u05/u05_clean.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u05_clean
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  #$ -l h_vmem=2G
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  cd /d3/scratch/${USER}/ngs_u05
  fastp -i raw/SRR2584863_1.fastq.gz -I raw/SRR2584863_2.fastq.gz \
      -o clean/sample01_R1.clean.fq.gz -O clean/sample01_R2.clean.fq.gz \
      --detect_adapter_for_pe --cut_tail --cut_window_size 4 --cut_mean_quality 20 \
      --qualified_quality_phred 15 --unqualified_percent_limit 40 --length_required 50 \
      --thread 4 --html logs/fastp_SRR2584863.html --json logs/fastp_SRR2584863.json
  zcat clean/sample01_R1.clean.fq.gz | wc -l > logs/clean_lines.txt
  zcat clean/sample01_R2.clean.fq.gz | wc -l >> logs/clean_lines.txt
  [[ $(sed -n 1p logs/clean_lines.txt) -eq $(sed -n 2p logs/clean_lines.txt) ]] \
      && echo PAIRED_OK >> logs/clean_lines.txt
  EOF
  cd /d3/scratch/${USER}/ngs_u05 && qsub u05_clean.job
  ```

  这条命令在做什么：清洗用第 6 章的同款参数（讲义 ⑤5.5；`--cut_tail` 只剪 3′ 端滑窗、窗口 4 均值 20 是课程起点不是黄金值，教材 §6.4.4），产物按本指导统一命名 `sample01_R*.clean.fq.gz`；作业末尾把 clean 双端行数写进 `logs/clean_lines.txt` 并对账——全文件扫描放计算节点，不占登录节点。等作业结束（`qstat -u ${USER}` 里看不到它、日志 `u05_clean.o*` 无报错）再往下做。
- **产出**：练习轨 `clean/sample01_R{1,2}.clean.fq.gz`、`logs/fastp_SRR2584863.{html,json}`、`logs/clean_lines.txt`；主线轨 `clean/` 下两个软链接。
- **检查点**：`cat logs/clean_lines.txt` 两行数字相等且末行 `PAIRED_OK`；`ls -lh clean/` 两端文件都在；`ls -lL` 不爆红（链接没有指向空处）。
- **出错信号**：md5 与 `fastq_md5` 列对不上 → 下载不完整，`wget -c` 续传重下；反复失败 → 联系助教经集群内网传一份，或用教师公布的课程共享目录预置文件。clean/ 下缺文件 → 课程脚本会以 `[ERROR] 文件不存在或为空` 退出（脚本前置检查，对 `-r/-1/-2` 三个参数都查）；行数不等 → 回第 6 章用双端模式重跑质控（§2 自查）。

### 步骤 1：下载参考（登录节点）

- **目的**：拿到练习轨参考——参考是整条流程的底本，底本错了后面每一步都 silently 错。
- **命令**（讲义 ⑤5.1 原句）：

  ```bash
  cd /d3/scratch/${USER}/ngs_u05/ref
  wget -c https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/005/845/GCF_000005845.2_ASM584v2/GCF_000005845.2_ASM584v2_genomic.fna.gz
  gunzip -c GCF_000005845.2_ASM584v2_genomic.fna.gz > ecoli.fa
  ls -lh ecoli.fa        # 一个约 4.6 MB 的文本文件
  ```

  这条命令在做什么：从 NCBI 下载登记过的参考 `GCF_000005845.2`，解压成 `ecoli.fa`。完整性三项自检（条目数 / 碱基总数 / 头行）安排在步骤 2 的作业开头做——参考只有 4.6 MB，占一个作业槽几秒钟，换来「底本对了才建索引」的顺序保证。
- **产出**：`ref/ecoli.fa`。
- **检查点**：`ls -lh` 文件存在、大小约 4.6 MB；正式对账看步骤 2 作业结束后的 `ref/ref_selfcheck.txt`（登记值：条目数 **1**、总长 **4,641,652 bp**，教材 §7.1/§7.10）。
- **出错信号**：文件缺失或明显偏小 → 下载不完整，`wget -c` 续传重下；反复失败 → 联系助教经集群内网传一份，或用教师公布的课程共享目录预置参考（若已公布）。

> **主线轨参考**（选做主线轨时）：用同株完成图 `GCA_987216485`（登记全长 4,768,212 bp）：`ln -sf <课程仓库路径>/06_data/raw/undergraduate/genomes/CIX4481.fna ref/xoo.fa`（课程仓库若还没下载这份数据，先按 `06_data/undergraduate/README.md` 的下载脚本获取）；后续步骤把命令里的 `ecoli.fa` 换成 `xoo.fa`、索引前缀相应替换，三项自检照做、登记值换成 4,768,212 bp。

### 步骤 2：建索引 + 参考自检（qsub 最小作业）

- **目的**：确认底本正确，并把参考预编译成比对器能查的数据结构。这一步教你认索引文件的件数与命名——索引缺失或换参考不重建，是比对启动即报错与「对着旧参考跑」两类事故的根源。
- **命令**（登录节点写作业脚本并投递）：

  ```bash
  cat > /d3/scratch/${USER}/ngs_u05/u05_index.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u05_index
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  #$ -l h_vmem=2G
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  cd /d3/scratch/${USER}/ngs_u05/ref
  {
    echo "entries=$(grep -c '^>' ecoli.fa)"
    echo "bases=$(grep -v '^>' ecoli.fa | tr -d '\n' | wc -c)"
    echo "header=$(grep '^>' ecoli.fa)"
  } > ref_selfcheck.txt
  grep -q '^entries=1$' ref_selfcheck.txt || { echo '[FATAL] 参考条目数不是 1：下载不完整，删掉重下'; exit 1; }
  bwa index ecoli.fa
  bowtie2-build --threads 4 ecoli.fa ecoli_bt2
  EOF
  cd /d3/scratch/${USER}/ngs_u05 && qsub u05_index.job
  ```

  这条命令在做什么：先做参考三项自检（条目数 / 碱基总数 / 头行名字）写进 `ref/ref_selfcheck.txt`，条目数不是 1 直接退出、不建索引；然后 `bwa index` 产出 `.amb/.ann/.bwt/.pac/.sa` **恰 5 件**；`bowtie2-build --threads 4` 产出 **恰 6 个 `.bt2`**，前缀 `ecoli_bt2`（正向 4 个 + 反向 2 个）。前缀 `ecoli_bt2` 严格遵循课程脚本的推导规则（`05_align_and_sort.sh` 的 `build_index`：去掉 `.fa`/`.fasta` 后缀再加 `_bt2`），步骤 3/7 用 `-a bowtie2` 时脚本按同一规则找到 `ecoli_bt2.1.bt2` 会跳过重建。注意两个工具的要件不同：`bwa mem` 收 FASTA **文件名**，`bowtie2 -x` 收索引**前缀名**、严禁带 `.1.bt2` 后缀（讲义 ⑤5.2 的分水岭）。
- **产出**：`ref/ref_selfcheck.txt`；`ref/ecoli.fa.{amb,ann,bwt,pac,sa}` 5 件；`ref/ecoli_bt2*.bt2` 6 件。
- **检查点**（先等作业结束：`qstat -u ${USER}` 里看不到它、`u05_index.o*` 无 `[FATAL]`）：

  ```bash
  cat ref/ref_selfcheck.txt     # entries=1 / bases=4641652 / header=... 与登记值逐字对账
  ls ref/ecoli.fa.{amb,ann,bwt,pac,sa}   # 5 件齐全（在 ngs_u05 根下看，路径要带 ref/ 前缀）
  ls ref/ecoli_bt2*.bt2                  # 6 件齐全
  ```

- **出错信号**：两个数对不上 → 下载不完整，删掉 `ref/` 里相关文件重下（自检在作业里，结果在 `ref_selfcheck.txt`）；缺任何一件索引 → 比对一个启动就报 `fail to locate the index files`（讲义 ⑨-E1）；**换了参考必须重建索引**，脚本只按「文件在不在」跳过，管不住「索引是不是这个参考的」——旧索引配新参考会把读段对着旧参考比对，后续统计全部静默错误（教材 §7.4.4 换参考契约）。

### 步骤 3：比对 + 排序 + 内置验收（`qsub 05_align_and_sort.sh`）

- **目的**：一条命令完成 比对 → 管道排序成 BAM → 建索引 → 自动验收（quickcheck + 非空 + 记录数对账），并落盘比对日志。验收是教材 §7.5.2 的头号失效（上游比对器中途死亡、管道却返回成功）的第一道防线。
- **命令**（登录节点写作业脚本并投递；【集群未实测】真实数据本课未在课程环境跑通；占位符按 §3 开头「占位符纪律」三步替换）：

  ```bash
  cat > /d3/scratch/${USER}/ngs_u05/u05_align.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u05_align
  #$ -cwd
  #$ -j y
  #$ -pe smp 16
  #$ -l h_vmem=2G
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  cd /d3/scratch/${USER}/ngs_u05
  bash "<课程仓库路径>/03_code/undergraduate/scripts/05_align_and_sort.sh" \
      -r ref/ecoli.fa \
      -1 clean/sample01_R1.clean.fq.gz \
      -2 clean/sample01_R2.clean.fq.gz \
      -s sample01 -o bam -t 8
  EOF
  REPO=<课程仓库路径>    # ← 换成教师公布的真实路径
  sed -i "s|<课程仓库路径>|${REPO}|g" u05_align.job
  grep -n '<课程仓库路径>' u05_align.job   # 必须无输出
  cd /d3/scratch/${USER}/ngs_u05 && qsub u05_align.job
  ```

  这条命令在做什么：脚本默认 `-t 4 -m 2G -a bwa`，这里显式给 `-t 8`。注意资源口径：脚本把 `-t` **同时**传给 `bwa mem -t 8` 和管道里的 `samtools sort -@ 8`，两个进程在管道中**并发**运行，申请核数要按名义线程之和给（`-t 8` → `#$ -pe smp 16`）；「每个工具的参数各自等于申请核数」的旧口径不成立。内存按脚本 `-m 2G` 的名义合计（8 × 2G = 16 GB）再加余量申请（`h_vmem=2G` × 16 = 32 GB）；课程未实测真实峰值，`h_vmem` 的口径（每槽还是每进程）随集群配置而异，报 `vmem exceeded` 或被 OOM 杀时找助教确认本集群口径再上调。队列紧张可改 `-t 4`（脚本默认值）+ `#$ -pe smp 8`。
  脚本内部（与现版源码逐字一致）：`bwa mem -t 8 -M -K 10000000 -R "$rg"`，`-R` 由脚本用双引号变量传入、含 `ID/SM/PL/LB/PU` 五个标签；管道接 `samtools sort -@ 8 -m 2G -T bam/tmp_sample01_<PID> -o bam/sample01.sorted.bam -`，`-T` 前缀带进程号、防同目录并发任务互相覆盖；比对 stderr 落 `bam/logs/bwa_mem.log`。三个参数各一句口径：`-M` 只改分裂比对的标记口径（短段标成次要比对 FLAG 256），不改比对本身；`-K 10000000` 固定批处理大小，**有助**同一版本同一参数下复现，不保证跨版本二进制哈希一致；`-m 2G` 是近似的每线程内存配额，名义合计 `-t × 2G`，实际峰值还含其它开销、以实测为准（教材 §7.4.7）。
- **产出**：`bam/sample01.sorted.bam` + `.bai`；`bam/logs/bwa_mem.log`；作业日志 `u05_align.o<作业号>`（`#$ -j y` 合并到当前目录）。
- **检查点**（先等作业结束：`qstat -u ${USER}` 里看不到它、日志里出现 `[DONE]`）：

  ```bash
  cat u05_align.o*                      # 找 [INFO] 验收通过：quickcheck OK；主记录 N = 2 × M 模板
  samtools view -H bam/sample01.sorted.bam | grep '^@RG'   # 五个标签齐全、制表符在位
  ```

  对账的账本是手算算术（教材 §7.4.6）：R1 clean 行数 ÷ 4 = 模板数 M，双端数据期望主记录数 = **2 × M**；脚本用 `samtools view -c -F 0x900` 数主记录（`0x900 = 2048 + 256 = 2304`，排除次要与补充比对），与 2 × M 不等即以 `[FATAL]` 退出并提示「不要用这份 BAM 做下游统计」。
- **出错信号**：
  - 作业日志出现 `Killed` → 内存被 OOM 杀掉（教材 §7.5.2）；调 `-m`/申请内存后重投。
  - `paired reads have different names` → 双端文件不同步，回第 6 章用双端模式重跑质控。
  - `no ID within the read group line` → `-R` 字符串在传到 bwa 之前被某个转义层破坏了（讲义 ⑨-E4）。注意病根**不是**双引号：Bash 单双引号都保留字面的 `\t`，课程脚本正是用双引号变量传 `-R`（教材 §7.4.7 本机实测）；排查时把脚本的 `rg=` 行回显进日志看实参。
  - 比对器中途死亡而管道返回成功（rc=0、0 条记录的 BAM）→ 脚本内置的 quickcheck + 非空 + 对账三件套就是为此准备的（教材 §7.5.2；本机实测记录：截断到 100 字节的 BAM 被 quickcheck 以退出码 56 抓住；上游写出有效头后死亡时 sort 照常 rc=0 产出 0 条记录——两级行为均非课程 pin 版本实测，教材 §7.3 口径）。

### 步骤 4：统计落盘与读法（脚本自动；讲义 ⑤5.6）

- **目的**：脚本自动落盘 flagstat / idxstats / coverage / 深度摘要四种统计，并读懂每个数的分母与口径——这一步把「命令成功」变成「结果可解释」。
- **命令**：无新命令（步骤 3 的 `run_stats` 已自动完成）；作业结束后在登录节点读数：

  ```bash
  ls bam/logs/     # sample01.flagstat.txt / idxstats.txt / coverage.txt / depth_summary.txt
  cat bam/logs/sample01.flagstat.txt
  cat bam/logs/sample01.depth_summary.txt   # mean_depth / zero_depth_sites / zero_depth_pct
  ```

  这条命令在做什么：flagstat 按**记录与 FLAG** 统计，`in total` 含次要与补充记录、不等于 FASTQ 模板数；`mapped` 是「本条记录自己比对上了」的**记录级**比例，不是「至少一端贴上的模板比例」——要后者须按 QNAME 归成模板另数（教材 §7.4.6 的三条高频误读）。单 contig 参考下 `mate mapped to a different chr` 预期为 0。**深度口径声明**：脚本的深度摘要用 `samtools depth -a`（零深度位点也输出），本指导与脚本报告一律声明为「`-a` 口径」；`-a` 仍**不含完全未被读段使用的 contig**——本实验参考只有 1 条序列，两口径无差别；将来换多 contig 参考做全参考平均深度，必须用 `-aa` 或以参考全长做分母并写明口径（教材 §7.4.6 本机实测的非课程 pin 例：两 contig 各 200 bp、仅其一有 100 bp 覆盖，`-a` 均值 0.5、`-aa` 口径 0.25）。
- **产出**：`bam/logs/sample01.{flagstat,idxstats,coverage}.txt`、`bam/logs/sample01.depth_summary.txt`（脚本对 depth 空输出有 `[FATAL]` 防护）。
- **检查点**：四个文件存在非空；flagstat 的 `in total` 与步骤 3 的主记录数 + 次要/补充数对得上；**只记录数值、不判优劣**——本科无比对率/深度/重复率的登记预期区间。
- **出错信号**：contig 名写错时区间查询返回 0 条、退出码 0、stderr 一行 `unknown reference ... Continue anyway`（教材 §7.5.3）。当场演示一次静默形态——区间查询走 `.bai` 索引、只扫指定区间，秒级，登录节点可跑：

  ```bash
  samtools view -H bam/sample01.sorted.bam | grep '^@SQ'     # ① 真实 contig 名在 SN: 后面
  CTG=$(samtools view -H bam/sample01.sorted.bam | awk -F'\t' '/^@SQ/{for(i=1;i<=NF;i++) if($i~/^SN:/) print substr($i,4)}')
  echo "contig=${CTG}"        # ② 核对：只打印一个名字，与 ① 逐字一致
  samtools view -c bam/sample01.sorted.bam "${CTG}:1000000-1010000"   # ③ 用变量构造区间，记下条数
  samtools view -c bam/sample01.sorted.bam chr1:1-100 ; echo "rc=$?"  # ④ 故意写错：0 条、rc=0
  ```

  名字逐字以 ① 的实际输出为准（头行空格前是什么就抄什么，不要凭印象写）；③ 的条数**记下来**：正确名字一般能查到记录，但若查到 0 条——先核对 ② 与 ① 逐字一致；仍 0 条则可能是该区间确实没有读段覆盖（本课未实测该演示数据的覆盖分布，**不算错**），把「确实没有」写进记录表。④ 的「0 条 + rc=0 + 一行警告」就是静默形态，与 ③ 对照着看才分得清「名字错了」和「确实没有」。名字对了还要防坐标基准差一位：命令行区间是 1-based 闭区间，BED 是 0-based 半开区间（教材 §7.4.4）。

### 步骤 5：MAPQ 分布自检与重复区已知答案（全文件扫描，qsub）

- **目的**：把「比对率」与「MAPQ 分布」放在一起看——只看前者会发现不了重复区，只看后者会发现不了塌缩参考（教材 §7.5.1 的两个方向）。
- **命令**（登录节点写作业脚本并投递；占位符按 §3 开头三步替换）：

  ```bash
  cat > /d3/scratch/${USER}/ngs_u05/u05_mapq.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u05_mapq
  #$ -cwd
  #$ -j y
  #$ -pe smp 2
  #$ -l h_vmem=2G
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  cd /d3/scratch/${USER}/ngs_u05
  samtools view bam/sample01.sorted.bam | awk '{print $5}' | sort -n | uniq -c > bam/logs/mapq_hist.txt
  samtools view bam/sample01.sorted.bam | awk '$5==0' | wc -l > bam/logs/mapq0_n.txt
  samtools view -c -q 30 bam/sample01.sorted.bam > bam/logs/q30_n.txt
  cd "<课程仓库路径>" && PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch07_mapq_multimapping.py \
      --selftest > /d3/scratch/${USER}/ngs_u05/bam/logs/mapq_demo_selftest.txt 2>&1
  EOF
  REPO=<课程仓库路径>    # ← 换成教师公布的真实路径
  sed -i "s|<课程仓库路径>|${REPO}|g" u05_mapq.job
  grep -n '<课程仓库路径>' u05_mapq.job   # 必须无输出
  cd /d3/scratch/${USER}/ngs_u05 && qsub u05_mapq.job
  ```

  作业结束后在登录节点读数：

  ```bash
  cat bam/logs/mapq_hist.txt                 # MAPQ 各分值档的记录数（0 档在最前）
  cat bam/logs/mapq0_n.txt bam/logs/q30_n.txt
  tail -3 bam/logs/mapq_demo_selftest.txt    # 末行应 SELFTEST PASS
  ```

  这条命令在做什么：前两条 `samtools view | awk` 是教材 §7.4.6 的原句（数第 5 列各分值档、数 MAPQ=0 的记录），第三条看 `-q 30` 过滤后还剩多少——三条都是全文件扫描，放计算节点、结果写文件，登录节点只读文件。demo 在作业内 cd 到课程仓库根目录运行（合成算例、固定种子，不访问你的数据）。
- **已知答案练习（合成、可复跑）**：demo 复现两个锚点——扩展参考（5 个拷贝都保留）上三类读段全部比上、MAPQ=0 占 **33.3%**（600/1800，这是**全部记录中** MAPQ=0 的比例）；`-q 30` 过滤后重复区读段**保留 0 条**——两个数分开记：33.3% 是过滤前的占比，「归零」的是过滤后重复区的保留数；塌缩参考（只留 1 个代表拷贝）上背景深度 10.0×、代表拷贝区 55.0×（比值 5.50）、家族读段 MAPQ 全 60。**对照结论**：只看比对率，两例都「完美」；只查 MAPQ，塌缩参考的方向完全漏网。demo 输出不得写成真实样本实测（2026-11-10 现跑 PASS）。
- **产出**：`bam/logs/{mapq_hist.txt, mapq0_n.txt, q30_n.txt, mapq_demo_selftest.txt}`。
- **检查点**：MAPQ 分布打印成功，能指出 0 档占比并写下你对「这些读段落在哪里」的判断（定性）；demo 复现 33.3% 与 5.50 两个锚点。真实数据的 MAPQ=0 占比**没有登记预期**，只记录。
- **出错信号**：`-q 30` 后某区深度归零、不过滤时正常 → 该区读段集中在低 MAPQ，按教材 §7.5.1 的察觉清单继续查（过滤前后深度对比、次要与补充计数、重复注释叠合）。

### 步骤 6：PCR 重复标记与对账（脚本自动；讲义 ⑤5.8、⑩-1）

- **目的**：标记 PCR 重复（**只标记不删除**：标记可逆，下游用 `-F 1024` 过滤即可），并完成对账黑客任务——三个计数加得了账、并与 markdup 统计互证。
- **命令**：无新命令（脚本的 `mark_duplicates` 自动完成）；作业结束后核对：

  ```bash
  cat bam/logs/dup_counts.txt        # total / after_dedup(-F 1024) / duplicates(-f 1024) / duplicate_rate
  grep -i "DUPLICATE TOTAL" bam/logs/markdup.stats
  ```

  这条命令在做什么：脚本按工业标准链 `collate → fixmate -m → sort → markdup -s` 执行（`-m` 不能省，否则 markdup 报 `no ms score tag`）；`markdup` 不带 `-r`，重复记录保留、FLAG 打 1024。随后用三条 `samtools view -c` 分别数全量、`-F 1024`（剔除重复）、`-f 1024`（只要重复），写入 `dup_counts.txt`。
- **产出**：`bam/sample01.markdup.bam` + `.bai`；`bam/logs/markdup.stats`；`bam/logs/dup_counts.txt`；另有 `bam/logs/sample01.markdup.*` 四个统计文件。
- **检查点**（对得上账，无数值预期）：
  1. `duplicates(-f 1024)` 与 `markdup.stats` 的 `DUPLICATE TOTAL` 一致（脚本 HINT 同款提示）；
  2. 恒等式 total = (total − duplicates) + duplicates 成立——注意按教材口径（案例衔接）：恒等式是**同一 BAM 数两遍**，不是独立证据；独立核对回到步骤 3 的 FASTQ 模板数对账；
  3. 重复率只记录、不判优劣——本科无登记预期区间。
- **出错信号**：两计数不一致 → 中间步骤看错文件或 BAM 被截断；`no ms score tag` → 手工改脚本时漏了 `fixmate -m`（脚本内置，正常投递不会触发）。

### 步骤 7（可选）：bowtie2 对照（`-a bowtie2`）

- **目的**：用默认端到端范式的 Bowtie2 跑同一批数据，体会两种范式对同一批带末端异常读段的记分会记在不同地方（教材 §7.4.3），而不是比谁「更准」。
- **命令**（复制步骤 3 的作业脚本改三处再投递；**切勿在登录节点直接敲** `bash … -a bowtie2`——那是多线程比对，违背 §0 计算纪律）：

  ```bash
  cd /d3/scratch/${USER}/ngs_u05
  cp u05_align.job u05_align_bt2.job
  # 用编辑器（nano/vim）改三处：① #$ -N u05_align → #$ -N u05_bt2；
  #   ② -o bam → -o bam_bt2；③ 参数行末尾追加 -a bowtie2
  grep -n 'u05_bt2\|bam_bt2\|bowtie2' u05_align_bt2.job   # 应命中 #$ -N 行与参数行（两处三改）才算改对
  qsub u05_align_bt2.job
  ```

  这条命令在做什么：脚本自动按同一推导规则建/找 `ecoli_bt2` 前缀索引，用 `--very-sensitive -X 800 --rg-id/--rg` 传元数据，stderr 落 `bam_bt2/logs/bowtie2.log`；比对与排序仍在同一管道里并发，作业头沿用步骤 3 的 16 slots 申请口径。
- **产出**：`bam_bt2/sample01.sorted.bam`（+ markdup 链全套，因为没加 `--no-markdup`）。
- **检查点**：`bowtie2.log` 摘要的分类计数总和 = 总对数（讲义 ⑥6.1 的读法）；`aligned concordantly exactly 1 time` 是最健康类别。**关键口径：不要比较两个工具的 MAPQ 均值**——BWA 0.7.17 封顶 60、Bowtie2 端到端唯一锚点 42（`--local` 44），两套标度不可横比（合成锚点来自 demo `--selftest`；教材 §7.4.5/§7.4.8）。Bowtie2 分支的 `@RG` 只有 `ID/SM/PL` 三个标签，是脚本现行为，不是漏了。
- **出错信号**：`(ERR): "ecoli.fa" does not exist or is not a Bowtie 2 index` → 把 FASTA 文件名当成了 `-x` 前缀（讲义 ⑨-E9）；`-x` 只收前缀名 `ecoli_bt2`。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果。所有栏目「自查判据」一列只写对账关系与定性判据——本科无比对率/深度/重复率的登记数值预期。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 0 数据准备 | 练习轨 clean 双端行数对账 | 行 | | `logs/clean_lines.txt` 两行相等且 PAIRED_OK（第 6 章同款对账） |
| 1 参考自检 | 条目数 / 总长 | 条 / bp | | 1 条、4,641,652 bp（登记值，教材 §7.1/§7.10；读 `ref/ref_selfcheck.txt`） |
| 2 索引 | BWA 件数 / Bowtie2 件数 | 件 | | 恰 5 件 .amb/.ann/.bwt/.pac/.sa；恰 6 个 .bt2（脚本注释与手册） |
| 3 比对验收 | 主记录数 vs 2 × R1 模板数 | 条 | | 对账相等（手算：R1 行数 ÷ 4 = 模板数；教材 §7.4.6） |
| 3 元数据 | @RG 行 | 文字 | | ID/SM/PL/LB/PU 齐全、制表符在位（教材 §7.4.7） |
| 4 统计 | flagstat `in total` 与主记录数+次要/补充数 | 条 | | 对得上账；`mapped` 按记录级口径读（教材 §7.4.6） |
| 4 深度 | depth_summary 口径声明 | 文字 | | 写明「-a 口径」；将来多 contig 参考须 -aa 或全长分母（教材 §7.4.6） |
| 5 MAPQ | 0 档占比 / -q 30 后计数 | % / 条 | | 读 `bam/logs/mapq_hist.txt` 等；只记录不判优劣；合成参照 33.3%（demo 现跑，非真实数据预期） |
| 6 重复标记 | duplicates 与 DUPLICATE TOTAL | 条 | | 两数一致；total = (total−dup) + dup 成立（对账非独立证据） |
| 7 对照（可选） | bowtie2 分类计数和 | 对 | | 分类和 = 总对数；不比两工具 MAPQ 均值（标度不同） |

## 5. 失效条件对照（教材 §7.5，本实验里在哪一步察觉）

1. **重复区读段定位置信度低、被伪随机落位，按位置计数会把重复区算错**（§7.5.1）｜察觉：步骤 5——MAPQ 分布里 0 档占比、`-q 30` 前后计数对比；用 demo 的合成已知答案练过两个方向（扩展参考上 MAPQ=0 占全部记录 33.3%（600/1800），`-q 30` 过滤后重复区读段保留 0 条——33.3% 是过滤前的占比、保留 0 是过滤后的结果，两个数分开记；塌缩参考方向是 5.50 倍高深度 + MAPQ 全满分，`-q 30` 保留 100%）再看真实数据。两个方向都不报错，只看一个信号必漏一个方向。
2. **比对器中途退出而管道返回成功，得到截断或空 BAM**（§7.5.2）｜察觉：步骤 3——作业日志先查有没有 `Killed`，再看脚本内置验收三件套（quickcheck + 非空 + 主记录 = 2 × 模板数）有没有打 `[FATAL]`。rc=0 不算数，对得上账才算数。
3. **contig 名不一致：区间提取返回空而不报错**（§7.5.3）｜察觉：步骤 4 末尾的负例演示——`chr1:1-100` 返回 0 条、rc=0、只有一行警告；区间查询先分清「名字错了」与「确实没有」：名字逐字以 `grep '^@SQ'` 与 `grep '^>'` 的实际输出为准，正确名字查到 0 条要记录、不直接判错。任何区间查询把条数与口径写进记录表。
4. **`@RG` 元数据写错：有的当场报错，有的静默误归属**（§7.5.4，本科层只要求「跑完核对头行」这一动作，字段职责属硕士层）｜察觉：步骤 3——跑完立刻 `samtools view -H bam/sample01.sorted.bam | grep '^@RG'` 核对五个标签与制表符；报错形态（`no ID within the read group line`）不可怕，可怕的是不报错的那种，所以核对动作必须做。

## 6. 思考题（指向教材 §7.7 习题与讲义 ⑩，不给答案）

1. 你的 BAM 里 `flagstat` 的 `mapped` 是记录级还是模板级口径？想回答「多少模板至少一端贴上了」该怎么数？（教材 §7.7 习题 6 → §7.4.6）
2. 取一条你的 CIGAR 含 `S` 的记录，说明读段消耗与参考跨度的账各是多少；软剪切集中在 3' 端、长度集中，与固定坐标聚集，分别提示什么、怎样鉴别？（教材 §7.7 习题 4、讲义 ⑩-3 → §7.4.3）
3. 用步骤 5 的两条 awk 命令解释：为什么一条碱基全 Q40 的读段 MAPQ 可以是 0？为什么「BaseQ 高」推不出「MAPQ 高」？（教材 §7.7 习题 5 → §7.4.5）
4. 如果只看比对率，本实验合成批的「高比对率陷阱」为什么发现不了？把 MAPQ 分布叠上之后结论怎样变？（教材 §7.7 习题 5、讲义 ⑩-5 → §7.4.5/§7.5.1）
5. 有同学用同一批数据跑 BWA 与 Bowtie2，拿平均 MAPQ 60 对 42 断言「BWA 更准」。写出这段批判（提示：两个 42/44 锚点、两套标度、该怎么真正比较）。讲义 ⑩-7。

## 7. 提交物

- **对应作业**：u05 没有独立登记作业——`08_assessment/undergraduate/project/` 的综合项目 6 个模块与报告模板均不含比对环节（逐字核查零命中）；u05 的能力在 u06/u08 以「读段回贴自己组装的基因组」复用（讲义 ③3.3）。
- **课堂提交物**（对应讲义 ⑩-1 黑客任务 + 本章审计链）：
  1. `bam/logs/dup_counts.txt` 四个数 + total = (total−dup) + dup 恒等式说明 + 与 `markdup.stats` 的 `DUPLICATE TOTAL` 对账结果；
  2. `bam/logs/` 审计链目录打包（flagstat / idxstats / coverage / depth_summary / markdup.stats / 比对日志）；比对日志默认是 `bwa_mem.log`，做了步骤 7 的 Bowtie2 对照就打包 `bam_bt2/logs/` 的对应文件、日志为 `bowtie2.log`；
  3. 练习轨另附 `logs/fastp_SRR2584863.json` 与 `logs/clean_lines.txt`（clean 数据来源与对账证明）；
  4. 本指导 §4 结果记录表（填好「你的结果」与「自查判据」两列）。
- **打包**：按课程统一命名 `学号_姓名_<作业号>.zip`（作业号以教师课堂公布为准）。
- **诚实红线**：本科无比对率/深度/重复率的登记预期，记录表里只写实测数与对账结论，不得编造「健康阈值」；集群未实测的步骤按预期口径写，不得写成实测。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念/失效条件/习题） | `textbook/chapters/ch07/manuscript.qmd` §7.4 / §7.5 / §7.7 |
| 本单元讲义（原理细节、⑨ 错误排查 E1–E11、⑩ 思考练习） | `02_lectures/undergraduate/unit05_alignment_bam/05_alignment_bam_lecture.md` |
| 配套脚本 | `03_code/undergraduate/scripts/05_align_and_sort.sh`（参数：`-r -1 -2 -s -o -t -m -a --no-markdup`） |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`；本指导放进 qsub 作业内运行） | `textbook/demos/ch07_seed_extend.py`、`textbook/demos/ch07_mapq_multimapping.py` |
| 练习轨数据下载与四步验收（m01 讲义同款 ENA 入口） | 步骤 0 的 filereport 查询；`06_data/accessions.tsv`（`SRR2584863` / `ERR15732342` / `GCF_000005845.2` / `GCA_987216485` 均已登记） |
| 数据说明与登录号登记 | `06_data/undergraduate/README.md` §2.1；`06_data/accessions.tsv` |
| 环境定义 | `07_envs/conda/env_ug_base.yml`（`ngs_ug_base`，bwa 0.7.17 / bowtie2 2.5.1 / samtools 1.17 / fastp 1.3.6） |
| 后续单元 | u07 用本实验 BAM 做 IGV 浏览器核查；u08 用 minimap2 回贴自己组装的基因组（环境 `ngs_ug_assembly`） |
