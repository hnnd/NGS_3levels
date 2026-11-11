---
title: "实验指导 m04：转录组定量与差异表达"
level: master
topic: m04
textbook: [ch14, ch12]
lecture: ../02_lectures/master/topic04_rnaseq/04_rnaseq_lecture.md
env: ngs_ms_transcriptome
---

# 实验指导 m04：转录组定量与差异表达
> 上机时手边打开的这份文件。每一步都回答四件事：这条命令在做什么、敲什么、
> 看到什么算对、看到什么说明错了。原理与判据在教材第 14 章（§14.4 概念、§14.5 失效条件），
> 统计背景（负二项、FDR、功效）在第 12 章；本指导只放操作与自查入口。检查点数字都带来源：
> 「预期（未实测）」是 README/讲义经验口径，「合成算例」是 demos 固定种子演示；本课没有在
> 课程集群真实跑完过全流程，凡标「集群未实测」的按预期对待。

## 0. 本实验对应什么
- **教材**：第 14 章 转录组定量与差异表达（主），第 12 章 计数数据的统计基础（参照）。
  覆盖硕士层学习目标 LO14-03（定量选型）、LO14-04（设计矩阵与方向）、LO14-05（离散度收缩）、
  LO14-06（结果表与矩阵形态）、LO14-07（富集背景与 2 重复边界）。
- **学时**：m04 共 4 学时（2 h 理论 + 2 h 实践），本实验是实践环节；作业建议上机 4–6 小时（含等待）。
- **环境**：定量与统计用 `ngs_ms_transcriptome`（`07_envs/conda/env_master_transcriptome.yml`），
  质控用 `ngs_ms_base`（`env_master_base.yml`）。m04 与 m05 共用一个转录组环境——
  m05 要把差异 peak 与本实验的差异基因取交集，不要自建分环境。
- **作业**：`08_assessment/master/assignments/m04_rnaseq_assignment.md`，占课程总成绩 5%；
  「方法选择与结果可信度说明」占作业 30%（报告三件事：模型、阈值、背景集与功效边界，教材 14.4.6/14.5.4）。
- **计算纪律**：一切计算一律 `qsub`（登录节点只下载、建环境、编辑；建索引也投递）。
  计算节点不通外网，任何联网步骤只能在登录节点做（根 CLAUDE.md 集群事实）。

## 1. 实验前检查
- **前置模块**（讲义 ②，先确认自测能过）：`l0_02_r` 第 3/4/6/8–10 题（按 `padj` 筛选、
  宽长表转换、上机）、`l0_04_formats` 第 5/6/7 题（reads 与参考序列的条数量级、GFF3 父子
  层级、坐标系）、`l0_05_qc` 第 3(b)/4(a)(c)/8 题（GC 双峰、RNA-seq 不去重、前 12 bp 不处理）、
  `l0_06_stats` Q3/Q5/Q6/Q7/Q9/Q10（均值-方差、BH、批次与混杂、生物学 vs 技术重复、
  为什么不能对 counts 做 t 检验）。
- **激活并核验版本**（版本与 `07_envs/conda/env_master_transcriptome.yml` 的 pin 对齐）：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_transcriptome
  salmon --version          # 期望 salmon 1.10.3（yml pin）
  STAR --version            # 期望 2.7.10b（yml pin）
  Rscript -e 'packageVersion("DESeq2")'        # 期望 1.42.0（yml pin）
  Rscript -e 'packageVersion("tximport")'      # 应打印版本号，不报 there is no package called
  Rscript -e 'packageVersion("apeglm")'        # 同上（脚本 lfcShrink(type="apeglm") 依赖它）
  ```

  这条命令在做什么：课程 yml 已含 tximport/apeglm/enhancedvolcano，但集群已建环境未必按
  新 yml 增量装过——`packageVersion` 是开箱第一闸：报 `there is no package called 'tximport'`
  就按讲义 ⑨-E0 在**登录节点**
  `mamba install -n ngs_ms_transcriptome -c bioconda bioconductor-tximport bioconductor-apeglm`
  补装再继续。
- **质控工具在另一个环境**（不要装错环境）：

  ```bash
  conda activate ngs_ms_base
  fastp --version           # 期望 0.23.4（yml pin）
  multiqc --version         # 期望 1.14（yml pin）
  ```
- **预期**：版本号全部打印且与 pin 一致。**出错信号**：`command not found` / 版本对不上 →
  环境没激活成功或装错环境（讲义 ⑨-E0 的排查思路）；缺 R 包 → 登录节点补装，
  **不要**在计算节点装（无外网）。

## 2. 实验数据
贯穿数据是 `PRJDB36269`（水稻根系复氮时序，与 m05 的 ATAC-seq 出自同一批样本），
取 Z 基因型、对照（K）与复氮（N）都有的配对时间点 30/60/120 分钟，各 2 个生物学重复（A/B），
共 12 个样本（算术；`06_data/master/README.md` m04 节；教材 14.6）。登录号全部已登记
`06_data/accessions.tsv`（项目在册、12 个 run 在册；样本名 ↔ 登录号 ↔ 文件名对照见下方
两份样本表，如 `ZK0030A` = `DRR737490` = 对照 30 min 重复 A）。

- **参考基因组**：`GCA_001433935`（水稻 IRGSP-1.0，总长 373,795,655 bp ≈ 374 Mb；
  教材 14.1 按 NCBI assembly stats 现查口径；数据 README 旧写「约 380 Mb」，以教材为准）。
  参考 FASTA、注释 GTF、转录本 FASTA 与 tx2gene 属课程备料：校内集群路径**由助教公布**
  （数据 README 未登记集群侧路径，勿编造）；校外自学从 NCBI 该装配页面下载 FASTA+GTF，
  转录本 FASTA 与 tx2gene 由 GTF 生成、版本号以课程提供为准。
- **备料到工作目录**（软链接，别拷贝大文件；3.1 与 STAR 选做都读本目录的文件）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m04
  REF_DIR=<助教公布的课程备料路径>      # 校外自学：换成自己下载/生成文件所在目录
  ln -s ${REF_DIR}/genome.fa genome.fa
  ln -s ${REF_DIR}/transcripts.fa transcripts.fa
  ln -s ${REF_DIR}/anno.gtf anno.gtf
  ln -s ${REF_DIR}/tx2gene.tsv tx2gene.tsv
  ls -l genome.fa transcripts.fa anno.gtf tx2gene.tsv   # 四行都指向真实文件（失效链接 ls 标红）
  ```

  检查点：`head -1 genome.fa` 打印 `>` 开头的 FASTA 头；跳过本步，3.1 第一条命令即报
  `grep: genome.fa: No such file or directory`。
- **下载与降采样**（README m04 节原口径）。在**课程仓库根目录**运行（脚本按相对路径调用；
  先进仓库根，或把命令写成绝对路径 `<课程仓库路径>/06_data/master/download_master.sh`）：

  ```bash
  cd <课程仓库路径>
  bash 06_data/master/download_master.sh --topic m04 --subsample 3000000 --run \
       --outdir /d3/scratch/${USER}/ngs/data
  ```

  产物落在 `/d3/scratch/${USER}/ngs/data/m04/`，命名形如 `DRR737490_1.sub3000000.fastq.gz`
  （`_1`/`_2` 双端；以日志与 `ls` 实名为准）。全集约 32 GB，降采样后 m04 约 2 GB（m04+m05 约 4 GB）。
  **`--subsample` 取每个文件的前 300 万条读段，不是随机抽样**（ENA 字节范围前缀下载 + 截断），
  方法学里必须如实写明（教材 14.6 已知限制第二条）；下载脚本校验 read 数，不足会在日志
  告警——看到告警先重下该 run，不要带着残缺文件往下跑。
- **两份样本表**（在登录节点建；制表符分隔，都必须带表头行——表头 + 12 行 = `wc -l` 为
  13。定量脚本跳过表头行（`04_rnaseq_quant.sh` L26），R 的 `read_tsv` 把第一行当列名：缺表头
  会把第一个样本名当列名、后面全错位）。直接复制下面文本块（heredoc 原样写入制表符，不用
  手敲 Tab；文件名以 `ls /d3/scratch/${USER}/ngs/data/m04/` 实名为准）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m04
  cat > samples.tsv <<EOF
  sample	R1	R2
  ZK0030A	/d3/scratch/${USER}/ngs/data/m04/DRR737490_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737490_2.sub3000000.fastq.gz
  ZK0030B	/d3/scratch/${USER}/ngs/data/m04/DRR737503_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737503_2.sub3000000.fastq.gz
  ZK0060A	/d3/scratch/${USER}/ngs/data/m04/DRR737491_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737491_2.sub3000000.fastq.gz
  ZK0060B	/d3/scratch/${USER}/ngs/data/m04/DRR737504_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737504_2.sub3000000.fastq.gz
  ZK0120A	/d3/scratch/${USER}/ngs/data/m04/DRR737492_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737492_2.sub3000000.fastq.gz
  ZK0120B	/d3/scratch/${USER}/ngs/data/m04/DRR737505_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737505_2.sub3000000.fastq.gz
  ZN0030A	/d3/scratch/${USER}/ngs/data/m04/DRR737499_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737499_2.sub3000000.fastq.gz
  ZN0030B	/d3/scratch/${USER}/ngs/data/m04/DRR737512_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737512_2.sub3000000.fastq.gz
  ZN0060A	/d3/scratch/${USER}/ngs/data/m04/DRR737500_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737500_2.sub3000000.fastq.gz
  ZN0060B	/d3/scratch/${USER}/ngs/data/m04/DRR737513_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737513_2.sub3000000.fastq.gz
  ZN0120A	/d3/scratch/${USER}/ngs/data/m04/DRR737501_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737501_2.sub3000000.fastq.gz
  ZN0120B	/d3/scratch/${USER}/ngs/data/m04/DRR737514_1.sub3000000.fastq.gz	/d3/scratch/${USER}/ngs/data/m04/DRR737514_2.sub3000000.fastq.gz
  EOF
  cat > coldata.tsv <<EOF
  sample	condition	rep	time	treatment
  ZK0030A	K	A	min30	K
  ZK0030B	K	B	min30	K
  ZK0060A	K	A	min60	K
  ZK0060B	K	B	min60	K
  ZK0120A	K	A	min120	K
  ZK0120B	K	B	min120	K
  ZN0030A	N	A	min30	N
  ZN0030B	N	B	min30	N
  ZN0060A	N	A	min60	N
  ZN0060B	N	B	min60	N
  ZN0120A	N	A	min120	N
  ZN0120B	N	B	min120	N
  EOF
  wc -l samples.tsv coldata.tsv        # 都应为 13（表头 + 12 行数据）
  ```

  - `samples.tsv` 三列 `sample R1 R2`，R1/R2 指向**清洗前**原始文件（步骤 3.2 的输入）。
  - `coldata.tsv` 五列 `sample condition rep time treatment`：`treatment` 取 K/N；`rep` 取 A/B；
    `condition` 填 K/N（与 treatment 同值）——脚本 L46 与 PCA 着色（L94）硬引用这一列，
    缺了会在 L46 报 `replacement has 0 rows`（本机现跑复现）。
  - **`time` 必须写成字符串水平 `min30/min60/min120`**——脚本只对 condition 显式转因子
    （L46），time 写成数值会被当连续协变量只占 1 列（本机 DESeq2 1.50.2 现跑
    model.matrix：因子 5 列、数值 4 列，自由度账全变；课程环境未复跑）。副作用：字母序
    会把 `min120` 当参考水平——这不影响 `treatmentN` 的 Wald 对比、也不影响检验 treatment
    的 LRT（教材 14.4.5）；若个人分析要以 30 min 为基线解读时间系数，在副本建对象后加
    `dds$time <- relevel(dds$time, ref = "min30")` 再重拟合。
  - 步骤 3.2 跑完后一键生成 `samples_clean.tsv`（结构同 `samples.tsv`，指向 `clean/` 下
    清洗后文件；作业都 `cd` 到工作目录投递，相对路径可用）：

    ```bash
    awk -F'\t' -v OFS='\t' 'NR==1{print; next} {print $1, "clean/"$1"_R1.fq.gz", "clean/"$1"_R2.fq.gz"}' samples.tsv > samples_clean.tsv
    ```
- **设计公式**：`~ rep + time + treatment`。`rep`（A/B）充当批次项；待估系数 5 个
  （截距 1 + rep 1 + time 2 + treatment 1），残差自由度 `12 − 5 = 7`（手算；教材 14.4.5）。
- **工作目录**：`/d3/scratch/${USER}/ngs/m04/`（下建 `clean/ qc/ quant/ salmon_idx/ star_idx/`）。
  数据放 scratch 不要放家目录；原始数据只软链不拷贝。

## 3. 实验步骤
> 每步五栏：目的 / 命令 / 产出文件 / 检查点 / 出错信号。
> 命令调用 `03_code/master/scripts/` 现有脚本与讲义 ⑤ 命令，不复制脚本全文；
> 脚本名、参数名、输出文件名已逐个与现版源码核对（见任务回执）。
> **在哪敲命令**：SSH 登录后是家目录；先 `cd /d3/scratch/${USER}/ngs/m04` 再投递。
> 凡 `qsub` 的作业日志（`*.o<作业号>`）写在投递时所在目录（脚本头 `#$ -cwd` 的约定），
> 产出写在命令指定的输出目录，两者不是一回事。集群真实运行本课未实测，一切区间按「预期」对待。

### 3.1 参考与索引准备（Salmon decoy-aware 索引；STAR 索引选做）
- **目的**：建定量要用的转录本索引。课程定量脚本只做 quant 与映射率汇总、**不含索引
  构建**——索引必须本步预先建好、以 `IDX=` 传给脚本（教材 14.4.2）。
- **命令**（讲义 ⑤5.2 原命令，投递计算节点；前置：§2 的四个软链接已建好）：

  ```bash
  cat > 04_salmon_index.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m04_idx
  #$ -cwd
  #$ -j y
  #$ -pe smp 16
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_transcriptome
  cd /d3/scratch/${USER}/ngs/m04
  grep '^>' genome.fa | cut -d ' ' -f1 | sed 's/^>//' > decoys.txt
  cat transcripts.fa genome.fa > gentrome.fa        # 顺序不能反：转录本必须在前
  salmon index -t gentrome.fa -d decoys.txt -i salmon_idx -k 31 -p 16
  EOF
  qsub 04_salmon_index.job
  ```

  这条命令在做什么：把基因组序列接在转录本序列之后建索引（转录本在前），内含子残留、
  gDNA 污染与未注释区读段有个去处（decoy），而不是被强行配给相似转录本（教材 14.4.2）。
  `-k 31` 的官方口径是「31 对 75 bp 及更长的读段表现良好」；讲义「读长 <50 bp 才降到
  21–25」是经验值，不是软件判据（教材 14.4.2）。
- **产出**：`salmon_idx/`（索引目录）、`decoys.txt`、`gentrome.fa`。
- **检查点**：`grep -c '^>' transcripts.fa` 应是**几万条、平均 1–3 kb**——转录本集条数量级
  是索引建错的第一道粗防线（教材 14.4.9）；`wc -l decoys.txt` 应等于
  `grep -c '^>' genome.fa`（基因组序列一条不落全进 decoy）。
- **出错信号**：把 `genome.fa` 当 `transcripts.fa` 建索引不报错，到 3.3 才暴露为映射率极低
  （讲义 ⑨-E8 → 教材 §14.4.9 的排查顺序）。STAR 路线（选做，需坐标 BAM 时才走）：
  `STAR --runMode genomeGenerate --genomeDir star_idx --genomeFastaFiles genome.fa --sjdbGTFfile anno.gtf
  --sjdbOverhang 149 --runThreadN 16`（`--sjdbOverhang` = 读长 − 1，150 bp 即 149，设例；教材 14.4.2），
  大内存作业按讲义 ⑨-E8 申请 `-l h_vmem=40G`（建索引默认内存上限 31 GB 级，教材 14.4.2）。

### 3.2 质控 fastp + MultiQC（环境 `ngs_ms_base`）
- **目的**：清洗接头与低质量区。**RNA-seq 两条纪律**（教材 14.4.1）：常规文库**不做
  PCR 去重**（高表达基因的重复读段大多来自真实分子）；前 ~12 bp 的 per-base sequence
  content 异常**不处理**（随机六聚体引物偏好，讲义经验 10–15 bp 与文献约 12 bp 一致）——
  处理它反而引入偏倚。
- **命令**（讲义 ⑤5.1 参数原样；小计算也走 qsub）：

  ```bash
  cat > 04_fastp.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m04_fastp
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_base
  cd /d3/scratch/${USER}/ngs/m04
  mkdir -p clean qc
  while IFS=$'\t' read -r s r1 r2; do
      [[ -z "${s}" || "${s}" == \#* || "${s}" == "sample" ]] && continue
      fastp -i "${r1}" -I "${r2}" -o "clean/${s}_R1.fq.gz" -O "clean/${s}_R2.fq.gz" \
            --detect_adapter_for_pe --cut_tail --cut_mean_quality 20 --length_required 50 \
            -w 4 -h "qc/${s}.html" -j "qc/${s}.json"
  done < samples.tsv
  multiqc qc/ -o qc/multiqc
  EOF
  qsub 04_fastp.job
  ```

  之后按 §2 说明建 `samples_clean.tsv`（R1/R2 指向 `clean/${s}_R{1,2}.fq.gz`），供 3.3 使用。
- **产出**：`clean/` 下 12 对清洗后 fastq；`qc/` 下每样本 html+json 与 multiqc 汇总目录。
- **检查点**：12 个 fastp json 齐全（`ls qc/*.json | wc -l` = 12）；multiqc 报告存在。保留率
  只作记录不作判据——降采样取文件头部，组成异常先怀疑截断（下载脚本告警优先处理）。
- **出错信号**：见重复率高就加去重参数 → 削掉真信号（只有 UMI 文库、扩增子/靶向、近饱和小
  转录组才按建库类型定，教材 14.4.1）；剪 5′ 端「修」前 12 bp → 引入偏倚（教材 14.4.1）。

### 3.3 定量（`qsub 04_rnaseq_quant.sh`，Salmon 选择性比对）
- **目的**：逐样本 quant 并把映射率汇总成一张表。选型：只要表达量走 Salmon；需要坐标
  BAM（可变剪接、IGV、与 m05 联合）才走 STAR（教材 14.4.2）。
- **命令**：

  ```bash
  cd /d3/scratch/${USER}/ngs/m04
  qsub -v SAMPLES=/d3/scratch/${USER}/ngs/m04/samples_clean.tsv,\
  IDX=/d3/scratch/${USER}/ngs/m04/salmon_idx,\
  OUTDIR=/d3/scratch/${USER}/ngs/m04/quant \
       <课程仓库路径>/03_code/master/scripts/04_rnaseq_quant.sh
  qstat -u ${USER}        # qw 排队 / r 运行 / Eqw 报错
  ```

  这条命令在做什么：脚本逐行读 `samples_clean.tsv` 逐样本跑
  `salmon quant -i ${IDX} -l A -1 R1 -2 R2 -p ${NSLOTS} --validateMappings --gcBias -o ${OUTDIR}/${sample}`
  （脚本 L32–35）。`-l A` 自动侦测文库类型并写进 `lib_format_counts.json`（与映射率一起先看，
  教材 14.4.9）；`--validateMappings` 是选择性比对的显式自证（1.0.0 起即默认）；`--gcBias`
  校正 GC 偏好。讲义 ⑤5.2 另加 `--seqBias --numBootstraps 30`，两套都合法，课程脚本走最小
  差异表达路径。跑完从各样本 `aux_info/meta_info.json` 抽 `percent_mapped` 汇总成
  `mapping_rates.tsv`（L51–57）。`MODE=star` 分支要求 `GTF=` 非空（L20/L37）但只做比对
  定量、不建索引，走 STAR 时照传 `GTF=<注释文件>` 即可（脚本内不使用，待清理的守卫）。
- **产出**：`quant/<样本>/quant.sf`（转录本级 `NumReads/TPM/EffectiveLength`）、
  `aux_info/meta_info.json`（映射率）、`lib_format_counts.json`、`logs/salmon_quant.log`、
  `quant/mapping_rates.tsv`。
- **检查点**：
  1. `mapping_rates.tsv` 有 12 行（产物级自查：计数对得上样本数）。
  2. 映射率**预期（未实测）**：README 水稻口径 >80%，讲义经验 70–90%；诊断量不是判据——
     先看组内比较，同批样本应彼此接近（教材 14.4.9）。
  3. `lib_format_counts.json` 的 `expected_format` **全样本一致**（如 ISR）；个别样本单独
     跑出 IU（非链特异）= 建库可能不同，分析前必须解决（教材 14.4.9）。
- **出错信号**（教材 §14.4.9 分档排查 + 讲义 ⑨-E8）：
  - 所有样本 <30% → 索引建错（genome.fa 当 transcripts.fa）或物种不对，回 3.1 查条数量级；
  - 30–50% → rRNA 未去净 / gDNA 污染 / 注释不全，取未映射读段做 BLAST 定性；
  - 样本间相差 >20 个百分点 → 回 3.2 的 MultiQC 找离群样本；
  - `qstat` 恒 `Eqw` → `qstat -j <ID> | grep -A5 error` 看资源/路径错误。

### 3.4 基因级矩阵（tximport 汇总）
- **目的**：把转录本级估计按 `tx2gene` 汇总到基因级计数矩阵交给 DESeq2。汇总后第一件事是
  **总量级对账**——tximport 只匹配上一小部分转录本时不报错，会成功返回一个大部分为 0 的
  矩阵（教材 14.4.2 的静默防线）。
- **命令**（讲义 ⑤5.4 的 tximport 部分；`readr::write_tsv` 不写行名，必须显式转
  `gene_id` 列——下游脚本把第一列当基因 ID）：

  ```bash
  cat > 04_tximport.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m04_tximport
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_transcriptome
  cd /d3/scratch/${USER}/ngs/m04
  Rscript - <<'RS'
  library(tximport); library(readr)
  samples <- read_tsv("samples_clean.tsv", show_col_types = FALSE)
  files <- file.path("quant", samples$sample, "quant.sf"); names(files) <- samples$sample
  tx2gene <- read_tsv("tx2gene.tsv", show_col_types = FALSE)  # 两列：transcript_id、gene_id（表头以课程备料为准）
  txi <- tximport(files, type = "salmon", tx2gene = tx2gene, ignoreTxVersion = TRUE)
  print(sum(txi$counts))   # 总量级对账：判据见下方检查点 2
  write_tsv(as.data.frame(txi$counts) |> tibble::rownames_to_column("gene_id"), "counts.tsv")
  saveRDS(txi, "txi.rds")  # 完整 txi 落盘：3.5 的教材全口径副本（DESeqDataSetFromTximport）要用
  RS
  EOF
  qsub 04_tximport.job
  ```
- **产出**：`counts.tsv`（第一列 `gene_id` + 12 个样本列）、`tx2gene.tsv`（课程备料）。
- **检查点**：
  1. `head -2 counts.tsv`：13 列，第一列是基因 ID（不是样本计数列——那是行名没转的征兆）。
  2. **量级对账（预期、未实测；手算口径）**：Salmon 的 `NumReads` 按**片段**计（双端一对
     算 1），每样本 300 万片段 × 映射率（讲义经验 70–90%，README 口径 >80%）≈ 每样本
     2.1×10⁶–2.7×10⁶，全样本 `sum(txi$counts)` 应在 2.5×10⁷–3.2×10⁷。汇总表跨 12 个样本、
     「每样本 300 万」是单样本口径，两者不能直接比；要分样本核：`colSums(txi$counts)` 各列
     应 ≈ 3,000,000 × 该样本 `percent_mapped`/100（3.3 的 `mapping_rates.tsv`），对不上的
     样本先回 3.3 查。若总数只有几十万或更少 → tx2gene 版本号不匹配，先别进 3.5。
  3. `tx2gene.tsv` 的转录本 ID 与 `quant.sf` 第一列**逐字比对**（版本号后缀一致；
     不一致时 `ignoreTxVersion = TRUE` 只兜底、仍要弄清来源）。
- **出错信号**：`None of the transcripts in the quantification files are present in the first
  column of tx2gene`（讲义 ⑨-E1）→ 版本号问题；**不报错但矩阵大片为 0** → 检查点 2
  没对账（教材 14.4.2，§14.5.1 的同类「格式正确内容错」）。

### 3.5 DESeq2 差异表达（Wald，`qsub 04_deseq2_analysis.R`）
- **目的**：拟合负二项 GLM 并出结果表与诊断图。本设计问的是**处理主效应的方向与大小**
  （Wald 末位系数 `treatmentN`）；跨时间点的整体处理效应留给 3.6 的 LRT。
- **命令**（按「cp 副本 → 改行 → grep → qsub」走；副本同时满足作业 `scripts/` 提交要求与
  res/dds 落盘，PCA/LRT 副本都由它派生）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m04
  cp <课程仓库路径>/03_code/master/scripts/04_deseq2_analysis.R 04_deseq2_mine.R
  # 用编辑器在 res <- results(dds, alpha = 0.05)（L58）之后加两行：
  #   print(sizeFactors(dds)); saveRDS(dds, file.path(outdir, "dds.rds")); saveRDS(res, file.path(outdir, "res.rds"))
  grep -n 'saveRDS\|sizeFactors' 04_deseq2_mine.R      # 确认已加，再进下一步
  cat > 04_deseq2.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m04_deseq2
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_transcriptome
  cd /d3/scratch/${USER}/ngs/m04
  Rscript 04_deseq2_mine.R \
      counts.tsv coldata.tsv out_m04 "~ rep + time + treatment"
  EOF
  qsub 04_deseq2.job
  ```

  这条命令在做什么：第 4 个参数是设计公式（默认 `~condition`，L24），本设计
  `"~ rep + time + treatment"`（引号包住、空格原样传入）。关键机制（行号对现版）：
  L33–45 样本核对（setdiff 双侧报错＋按 coldata 重排＋identical 断言，教材 14.5.2 的
  三行防御已内置）；L46 `condition` 转因子；L49 `round(cts)` 对计数输入合法、对 TPM/FPKM
  即失效条件（教材 14.5.1，口径细节见下「建模口径」）；L50 预过滤
  `rowSums(counts(dds)) >= 10`（总计数口径；讲义 ⑤5.4 逐样本口径亦合法——事先定一种、
  不按结果调参，教材 14.6）；L51 默认 Wald；L58 `results(alpha = 0.05)` 的 alpha 必须与
  筛选阈值一致（教材 14.4.6）；L64–65 `lfcShrink(type = "apeglm")`。`rep/time/treatment`
  自动转因子、按字母序取参考（本数据 A、min120、K；min120 是字母序产物，不影响
  `treatmentN` 与 LRT 的 treatment 检验——本机 DESeq2 1.50.2 现跑 resultsNames 末位
  `treatment_N_vs_K`，课程环境未复跑）。副本只多 print/sizeFactors/saveRDS 两行
  （与可选的 Tximport 替换），其余逐行未动。
- **建模口径（教材全口径的可选副本改法）**：课程脚本 L49 `DESeqDataSetFromMatrix(round(cts))`
  不带长度偏移；教材 14.4.2/14.5.1 的全口径是 `DESeqDataSetFromTximport()` 把平均转录本长度
  留在模型里。两口径的计数基因数、流程与输出文件名一致，差别只在「同一基因跨样本有效长度
  不同（异构体切换）」时影响估计。要用全口径，在 3.4 已存 `txi.rds` 的前提下改副本两处
  （行号对未增行的现版；先做这两处再加 saveRDS 两行，行号就不漂）：L27–28 换成等行数两行
  `txi <- readRDS("txi.rds")` 与 `cts <- txi$counts`（其后 L33–45 样本核对三行原样生效）；
  L49 换成三行（前两行把 txi 三个矩阵同步重排——防御三行只重排了 `cts`，漏了会让长度偏移
  与样本错位）：

  ```r
  for (nm in intersect(c("counts", "abundance", "length"), names(txi)))
      txi[[nm]] <- txi[[nm]][, colnames(cts), drop = FALSE]
  dds <- DESeqDataSetFromTximport(txi, coldata, as.formula(design_str))
  ```

  `grep -n 'DESeqDataSetFromTximport' 04_deseq2_mine.R` 确认后投递。该路径已在本机
  DESeq2 1.50.2 合成数据走通（avgTxLength 进模型、Wald/apeglm 全链可跑），课程环境未复跑；用了哪种口径写进方法学说明。
- **产出**（`out_m04/`）：`deseq2_results.tsv`（六列 + 收缩后 log2FC/lfcSE，按 padj 排序）、
  `dispersion_estimates.png`、`volcano.png`、`vst_matrix.tsv`、`pca.png`。
- **检查点**：
  1. 日志先打印 `样本 12 个，基因 N 个，设计公式 ~ rep + time + treatment`（样本数必须是 12）。
  2. 方向核对：`mcols(res)$description[2]` 应写明 `treatment N vs K`（批处理会话已退出，
     从落盘对象读回再查：`res <- readRDS("out_m04/res.rds")`；本机现跑确认，三道闸见 §5 第 3 条）。
  3. 日志中 `padj 为 NA 的基因：N 个`——**预期构成 = 全零 + 独立过滤**；Cook's 路径在每格
     2 样本的设计里不可触发（教材 14.5.4），出现成批 `pvalue` 为 NA 先查分组与拟合。
  4. `sizeFactors(dds)` 范围抄进 §4 记录表（日志已打印，或
     `sizeFactors(readRDS("out_m04/dds.rds"))`）：跨样本**相差数倍**要先查建库与降采样
     （教材 14.4.9/14.5.4 的口径是「数倍」，不是某个固定倍数）。
  5. 作业 `fig2_pca.png` 要求颜色=condition、**形状=batch**——脚本 pca 只着色 condition。
     `cp 04_deseq2_mine.R 04_deseq2_pca.R`，在 `intgroup =` 加 `"rep"`（现版 L91）、
     `aes(...)` 加 `shape = rep`（现版 L94；若做过 Tximport 替换行号会漂，用
     `grep -n 'plotPCA\|geom_point' 04_deseq2_pca.R` 定位，不信行号信 grep），
     `grep -n 'intgroup\|shape' 04_deseq2_pca.R` 确认后投递副本（产物在 `out_m04_pca/`，
     含副本自己的 dds.rds/res.rds 与 pca.png；fig2 取这里）：

     ```bash
     cp 04_deseq2.job 04_deseq2_pca.job
     sed -i 's|04_deseq2_mine\.R|04_deseq2_pca.R|; s|out_m04|out_m04_pca|' 04_deseq2_pca.job
     grep -n 'Rscript\|out_m04' 04_deseq2_pca.job    # 脚本名与输出目录都指向 pca 副本
     qsub 04_deseq2_pca.job
     ```
- **出错信号**：
  - `counts 与 coldata 样本不一致——仅在 counts: … / 仅在 coldata: …` → 两表集合不同，脚本拦下
    （教材 §14.5.2；比静默贴标签好一万倍）。
  - DEG = 0 而 PCA 上两组分得开 → 先查方向（`resultsNames`/`contrast`/`description[2]`）与列序
    （§14.5.3/§14.5.2）。
  - 差异基因数达到检测基因一半以上 → 先查文库因子是否跨样本相差数倍、组成性偏差
    （教材 14.4.9；量级只决定先查哪项，不能单独断因）。

### 3.6 时序对比 LRT（个人副本）
- **目的**：回答「在配对时间框架下，复氮是否改变表达」——全模型 `~ rep + time + treatment`
  对约化模型 `~ rep + time`，被剔除的是 `treatment`（教材 14.4.6：LRT 检验被剔除的那项，
  不是「时间效应」）。
- **命令**（课程脚本默认 Wald、**不含 LRT 分支**，走个人副本）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m04
  cp 04_deseq2_mine.R 04_deseq2_lrt.R
  # 用编辑器把第 51 行  dds <- DESeq(dds)  改为
  #   dds <- DESeq(dds, test = "LRT", reduced = ~ rep + time)
  grep -n 'DESeq(dds' 04_deseq2_lrt.R          # 应看到新行带 test = "LRT"
  # 投递：复制 3.5 的作业脚本，脚本名换成 04_deseq2_lrt.R、输出目录换成 out_m04_lrt
  cp 04_deseq2.job 04_deseq2_lrt.job
  sed -i 's|04_deseq2_mine\.R|04_deseq2_lrt.R|; s|out_m04|out_m04_lrt|' 04_deseq2_lrt.job
  grep -n 'Rscript\|out_m04' 04_deseq2_lrt.job    # 应指向 lrt 副本与 out_m04_lrt
  qsub 04_deseq2_lrt.job
  ```
- **产出**：`out_m04_lrt/`（同 3.5 的一套文件，统计列来自 LRT）。
- **检查点**：
  1. 自由度账：`Λ` 的自由度 = 被剔除的列数 = `5 − 4 = 1`（手算；教材 14.4.6）。
  2. 日志里 `summary(res)` 表头标明 LRT 及两个模型的公式；`stat` 列**非负、无方向**
     （本机 DESeq2 1.50.2 现跑确认，课程环境未复跑）。
  3. 读表分行：`padj` 针对被剔除的 treatment 项；`log2FoldChange` 仍是末位系数（treatmentN）
     的收缩 MLE——`padj` 小而 log2FC 小不矛盾（效应小、标准误更小；教材 14.4.6）。
  4. 「时间整体有没有效应」要换约化模型 `~ rep + treatment`（剔除 time 两列，df=2），
     别把两种问法混着解释（教材 14.4.6）。
- **出错信号**：报 `must be Wald tests` → `lfcThreshold` 只能配 Wald（教材 14.4.6）；
  副本忘改第 51 行就投递 → 跑出来的还是 Wald 表（grep 确认就是防这个）。

### 3.7 诊断判读（先看图，再看表）
- **目的**：把「四图 + 三行数字」先抄进 §4 记录表，再打开结果表——看到很长的显著清单，
  人会不自觉地为异常找解释（教材 14.4.9 的建议流程）。
- **命令**：读图无新计算；作业要的 `fig5_heatmap.png` 在此产出（提交物清单要求，3.1–3.6
  都没画它）。用 vst 矩阵 + 按 padj 排序的前 50 个基因（教材 14.4.7：聚类热图必须用 vst/rlog，
  不用 counts）。pheatmap 不在课程 yml 包清单：先 `Rscript -e 'library(pheatmap)'` 检查，
  缺则按 ⑨-E0 在**登录节点** `mamba install -n ngs_ms_transcriptome -c conda-forge r-pheatmap` 补装：

  ```bash
  cat > 04_fig5_heatmap.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m04_fig5
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_transcriptome
  cd /d3/scratch/${USER}/ngs/m04
  Rscript - <<'RS'
  library(pheatmap); library(readr)
  vst <- read_tsv("out_m04/vst_matrix.tsv", show_col_types = FALSE) |> as.data.frame()
  rownames(vst) <- vst[[1]]; vst <- vst[, -1]
  res <- read_tsv("out_m04/deseq2_results.tsv", show_col_types = FALSE)
  top <- res$gene_id[1:50]     # 结果表已按 padj 排序；取前 50 个基因
  pheatmap(vst[top, ], scale = "row", show_rownames = FALSE,
           filename = "fig5_heatmap.png", width = 6, height = 8)
  RS
  EOF
  qsub 04_fig5_heatmap.job
  ```
- **产出**：填好的 §4 记录表前半；`fig5_heatmap.png`（作业 figs/ 第 5 张，画完复制进 figs/）：
  50 行基因 × 12 列样本，行按基因内 z 分数着色（`scale = "row"`，颜色只表示「该基因跨样本的
  相对高低」），图内文字一律英文。
- **检查点**：
  1. `plotDispEsts()` 四要点（教材 14.4.9）：黑点云状散布；红线自左上向右下单调下降后趋平；
     蓝点明显向红线收拢；红线上方远处带蓝圈的黑点是**故意不收缩**的离群基因
     （「红线近水平且很高，α 约 0.5 以上」的 0.5 是经验值不是判据）。
  2. PCA（vst 矩阵）**预期（README 口径，未实测）**：时间点应比 A/B 重复分得开；
     若 A/B 分得比处理还远 → 批次主导，正好支撑 `~ rep + ...` 的必要性（PCA 不能单独
     识别原因，要结合载荷与实验记录，教材 14.4.9）。
  3. 显著基因数**预期（未实测）**：复氮 30 min 对对照 30 min，README 口径几百到两千
     （教材 14.6 标 unverified）；拿到 0 或远超量级，先按 §14.5.2/§14.5.3 排查分组、
     列序与方向，再谈生物学解释——单一数字不能反推错误类型。
  4. 2 重复的边界：这张图能告诉你趋势线可辨、收缩生效；**不能**按单个基因的离散度
     下结论（黑点云上下界太宽，离线波动与抽样波动分不开；教材 14.5.4）。
- **出错信号**：红线接近 0 且平坦 → 疑似技术重复当生物学重复，下游 p 值严重偏小
  （教材 14.4.9 判读表）；收缩后 log2FC 仍是 ±20 级极值 → 单独核查该基因原始计数
  （教材 14.4.9）；火山图左右严重不对称 → 用 MA 图交叉验证（正常应围绕 y=0 对称）。

### 3.8 功能富集（GO ORA；blocked 声明）
- **目的**：差异基因清单 → 通路层面的候选解释（ORA 超几何检验，教材 14.4.8）。
- **状态声明（先读）**：水稻 OrgDb（`org.Osativa.eg.db`）不在课程任何 conda 环境包清单，
  `enrichGO` 开箱即败；教师裁定补包前本步标 **blocked/未实测**——结果不得写成已跑出。
- **命令**（讲义 ⑤5.4 的 enrichGO 代码，两处按教材口径改）：blocked 期间是**示意代码**
  （OrgDb 缺包整段跑不通）；补包后改掉三处占位（`res` 从磁盘读回、OrgDb 显式给出、结果写出）即可执行：

  ```r
  library(clusterProfiler); library(readr)
  res <- read_tsv("out_m04/deseq2_results.tsv", show_col_types = FALSE) |> as.data.frame()
  rownames(res) <- res$gene_id        # 批处理会话已退出，res 不在内存，必须从结果表读回
  # 占位：水稻 OrgDb 不在课程 yml（见上方状态声明）；补包后改为
  #   library(org.Osativa.eg.db); org.db <- org.Osativa.eg.db
  org.db <- NULL   # 跑到 enrichGO 会在此显式报错，而不是假装出结果
  deg <- subset(res, !is.na(padj) & padj < 0.05 & abs(log2FoldChange) > 1)
  deg_up <- rownames(subset(deg, log2FoldChange > 0)); deg_dn <- rownames(subset(deg, log2FoldChange < 0))
  universe_genes <- rownames(res)[!is.na(res$padj)]  # 背景 = 有资格入选（padj 非 NA）且
                                                     # ID 映射成功（教材 14.4.8）；keyType 与
                                                     # 课程基因 ID 版本先小样本试映射（bitr）核对
  ego <- enrichGO(deg_up, OrgDb = org.db, keyType = "GID", ont = "BP",
                  universe = universe_genes,
                  pAdjustMethod = "BH", minGSSize = 10,
                  qvalueCutoff = 0.05)   # 教材统一口径收紧到 0.05；软件默认是 0.2（14.4.8）
  write_tsv(as.data.frame(ego), "enrich_go.tsv")     # 结果落盘；universe 大小一并写进报告
  ```

  上下调**分开**各跑一次（ORA 本身无方向，混在一起成员互相抵消；教材 14.4.8）。
- **产出**：`enrich_go.tsv`（结果表 + universe 大小写进报告，作业要求；blocked 期间
  该文件不存在，不得提交）。
- **检查点**：
  1. `length(universe_genes)` 与 `sum(!is.na(res$padj))` **对账一致**，写进方法学——
     `rownames(res)` 不能直接当背景：它含全零行与被独立过滤（padj=NA）的基因
     （教材 14.4.8/14.5.3）。
  2. ID 映射警告（`xx.x% of input gene IDs are fail to map...`）：「多高算高」**没有统一
     百分比判据**，先查 keyType 与 ID 版本（教材 14.4.8 拒绝硬阈值的理由）。
  3. `minGSSize` 默认 10（小 term 显著性不稳，教材 14.4.8）。
- **出错信号**：不传 `universe` → p 值系统性偏小、纯零假设下也能富集出一堆 term
  （合成算例：正确背景 0 个显著 term、全基因组背景 22 个，`demos/ch14_ora_background.py --selftest`，
  教材 §14.5.3）；结果全是「cellular process」「metabolic process」这类最顶层 term →
  背景错或名单太杂（讲义 ⑥6.4 的判读）。

### 3.9 课堂演示（四条失效条件的合成证据，无集群依赖）
- **目的**：3.3–3.8 的四类事故共同特征是「不报错、结果表看起来正常」；
  四个固定种子的合成演示给出可复现的量化证据（数字只对各自生成模型成立）。
- **命令**（在课程仓库根目录运行；课程站暂未发布 textbook/，demos 从课程仓库获取）：

  ```bash
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch14_tpm_rounding.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch14_sample_mismatch.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch14_reversed_reflevel.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch14_ora_background.py --selftest
  ```
- **产出**：四组 `SELFTEST PASS`（2026-11-10 现跑通过）。
- **检查点（数字对照表）**：

  | 失效条件 | 关键数字（合成算例，来源 = 对应 demos --selftest） |
  |---|---|
  | 14.5.1 TPM 取整喂 DESeq2 | 假阳性率 0.038（raw）vs 0.288（round TPM，7.6 倍）；检出率 0.978 vs 0.744；真实文库因子 0.38–2.89 而对 round(TPM) 估出 0.93–1.14 |
  | 14.5.2 列序/标签错配 | 两组标签整体对调：检出率 0.990 不变、符号正确率 0%；随机重贴（10 次均值）：检出率 0.308、差异基因 665→67 |
  | 14.5.3 方向设反 | 显著基因 1257 两组相同、p 值最大差 5.8×10⁻¹⁵，只有符号翻转（100%→0%）；「N 上调」清单 343 vs 322（两条尾巴不等长） |
  | 14.5.3 背景用错 | BgRatio 0.3746 vs 0.2331；显著 term 0 vs 22；p 中位数 0.639 vs 0.206；超几何手算 40/120=0.3333 与 scipy 一致 |

- **出错信号**：四个脚本任一 `FAIL` → 环境或文件被改动，STOP 并核对
  （四个脚本只依赖 numpy/scipy，rc=0 即通过）。

## 4. 结果记录表（学生填写，不预填；「自查判据」列给来源口径）
| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 3.3 | 每样本映射率 / `expected_format` | % / 代码 | | 映射率：组内接近优先，README 口径 >80%、讲义经验 70–90%（均预期未实测；教材 14.4.9：诊断量非判据）；expected_format 全样本一致，个别 IU = 分析前必须解决 |
| 3.4 | `sum(txi$counts)` 总量级与 `colSums` 分样本值 | 计数总和 | | 总量 2.5×10⁷–3.2×10⁷、每样本 2.1×10⁶–2.7×10⁶（预期未实测，手算：300 万片段 × 映射率 70–90%）；分样本与 3.3 的 percent_mapped 对账（教材 14.4.2） |
| 3.5 | `sizeFactors` 范围 | 倍 | | 相差数倍要先查建库/降采样（教材 14.4.9，无固定倍数判据） |
| 3.5 | `padj` NA 三档计数：全零 / 独立过滤 / 其他 | 基因数 | | 预期只有前两档（Cook's 路径本设计不可触发；教材 14.5.4）；「其他」非零 → 先查拟合与分组 |
| 3.5 | 显著基因数（写明你的阈值） | 个 | | 预期（未实测）几百到两千（README 口径，教材 14.6） |
| 3.5 | PCA percentVar（PC1/PC2） | % | | 记录并判读批次还是处理主导（教材 14.4.9：PCA 不能单独识别原因） |
| 3.6 | LRT 显著基因数（写明阈值） | 个 | | 与 Wald 表分行解读（教材 14.4.6） |
| 3.8 | universe 大小 | 个基因 | | 与 `sum(!is.na(res$padj))` 对账一致（教材 14.4.8） |

## 5. 失效条件对照（教材 §14.5，本实验里在哪一步、看什么能察觉）
1. **TPM/FPKM 取整喂 DESeq2：不报错，方差模型已失效**（§14.5.1）｜3.4→3.5：
   输入只走 `txi$counts` 计数通路（3.4 对账）；3.5 日志 `converting counts to integer mode`
   正常（估计计数取整）；上游错传 TPM 则事后查 `sizeFactors(dds)` 是否全趋近 1。合成证据见 3.9。
2. **计数矩阵列序与样本表行序不一致：三档行为，最危险档不报错**（§14.5.2）｜3.5：
   集合不同 → 脚本 `setdiff` 双侧报错拦下（好失败）；顺序不同 → 重排+断言；
   无列名 → 静默贴标签（所以 `head counts.tsv` 必须是基因 ID）。
   「DEG≈0 而 PCA 分开」是第一察觉信号。
3. **对照水平设反与富集背景用错：两个对称的参照系事故**（§14.5.3）｜3.5/3.8：
   方向 = 三道闸（relevel 显式意识 + `contrast` 显式写出 + 读 `mcols(res)$description[2]`；
   本数据 K/N 字母序碰巧正确，是巧合不是规则）；背景 = universe 与
   `sum(!is.na(res$padj))` 对账（3.8 检查点 1）。
4. **只有 2 个生物学重复：能做什么与不能做什么**（§14.5.4）｜3.5/3.7/3.8：
   能 = 估趋势离散度、逐基因 Wald/LRT、给候选清单；不能 = 估单基因方差、用 Cook's 识别
   离群（每格 2 样本不计算、替换需某格 ≥7）、把「不显著」读成「没有差异」。察觉 = 蓝点收拢
   （收缩生效）+ NA 构成只有全零与独立过滤两档；报告三件事写齐（模型、阈值、背景集），
   结论限定为候选清单 + 需独立验证。

## 6. 思考题（教材 §14.7，习题 4/5/6/8/9 的上机版，不给答案）
1. 本实验只要基因水平表达量、不做可变剪接，所以走 Salmon；若课题要画基因组读段覆盖图并与
   ChIP-seq 的 peak 联合，该换什么、选错时流程会怎样错？（§14.7 习题 4 → 教材 14.4.2）
2. 写出 `~ rep + time + treatment` 的设计矩阵维数与残差自由度；若把 rep 换成三水平
   batch 呢？「加批次不花自由度」错在哪？（§14.7 习题 5 → 教材 14.4.5）
3. 结果表里三种 `padj = NA` 各对应哪一步处理？本数据预期能观察到几种、为什么？
   哪一种「补救」动作是错的？（§14.7 习题 6 → 教材 14.4.6）
4. 你 3.8 的 universe 是怎么定义的、大小多少？换成全基因组当背景，BgRatio 与 p 值
   往哪个方向偏、为什么「富集出更多通路」不等于「更多生物学」？（§14.7 习题 8 → 教材 14.4.8）
5. 写一段 150 字方法学说明，必须含：设计公式、`padj` 与 `|log2FC|` 阈值、
   富集背景集、2 重复的功效边界。（§14.7 习题 9 → 教材 14.5.4，即作业 30% 四问的底稿）

课堂讨论（讲义 ⑩ Q3/Q5/Q6/Q7）：NA 三行计数代码、LRT 表的读法、两种筛选法的零假设、富集对照实验。

## 7. 提交物
- **对应作业**：`08_assessment/master/assignments/m04_rnaseq_assignment.md`（占课程总成绩 5%），
  打包为 `学号_姓名_m04.zip`，解压后：

  ```
  学号_姓名_m04/
  ├── report.pdf        # 主报告 ≤8 页（不含附图），六节：QC 与定量汇总 / 实验设计与设计公式 /
  │                     # 离散度与模型诊断 / 差异基因结果 / 功能富集 / 方法选择与结果可信度说明（30%，≤1 页）
  ├── scripts/          # run_quant.sh（改自 04_rnaseq_quant.sh）、deseq2_analysis.R（即 04_deseq2_mine.R，改自 04_deseq2_analysis.R）、04_deseq2_pca.R、04_deseq2_lrt.R（两个副本）
  ├── results/          # deg_all.tsv（results() 全表）、deg_sig.tsv（你声明的阈值）、enrich_go.tsv（含 universe 大小）
  ├── figs/             # fig1_qc_summary.png / fig2_pca.png（颜色=condition、形状=batch）/ fig3_dispersion.png /
  │                     # fig4_volcano.png / fig5_heatmap.png（用 vst/rlog，不用 counts，教材 14.4.7）/ fig6_enrichment.png；图内一律英文
  └── env_snapshot.yml  # conda env export --no-builds
  ```

- **文件来源对照**（提交物从哪来，命名不一致处在此闭环）：
  - `results/deg_all.tsv` = `out_m04/deseq2_results.tsv` 直接复制改名（results() 全表）；
  - `results/deg_sig.tsv` = 按你在报告里**声明的阈值**筛出的子集，示例（阈值换成你自己的）：

    ```r
    library(dplyr); library(readr)
    read_tsv("out_m04/deseq2_results.tsv", show_col_types = FALSE) |>
      filter(!is.na(padj), padj < 0.05, abs(log2FoldChange) > 1) |>
      write_tsv("results/deg_sig.tsv")
    ```

  - `figs/` 六张图：fig1 截 3.2 的 multiqc 报告；fig2 = `out_m04_pca/pca.png`；fig3 =
    `out_m04/dispersion_estimates.png`；fig4 = `out_m04/volcano.png`；fig5 = 3.7 的
    `fig5_heatmap.png`；fig6 由 3.8 的 `enrich_go.tsv` 自行绘制（blocked 期间不提交 fig6）。
- **硬要求提醒**：报告每个数字必须是自己跑出来的；「方法选择与结果可信度说明」按作业四问
  （检验/模型选择、阈值来历、假阳性风险、可推翻证据）写实，2 重复功效边界必须写进第 6 节；
  `fig2` 双标注缺一即触发作业「常见失分点」第 7 条。
- **提交方式**：课程 LMS「专题作业 m04」；≤200 MB（超出删 BAM/quant 中间件）；
  截止 m04 课后第 10 天 23:59（m05 要用你这次的差异基因表做交集）；
  迟交 3 天内按 90%、超 3 天按 70%、超 7 天不计分（可申请一次不扣分延期）；以最后一次提交为准。
- **诚实红线**：3.8 在课程环境 blocked 期间，不得提交「已跑出」的富集结果；
  一切「预期（未实测）」区间不得写成实测；剔除样本须在报告里写明独立于结论的理由。

## 8. 附：教材/讲义/脚本指针
| 内容 | 位置 |
|---|---|
| 教材（概念/失效条件/贯穿案例/习题）＋统计背景（负二项、FDR、功效） | `textbook/chapters/ch14/manuscript.qmd` §14.4–§14.7；`textbook/chapters/ch12/manuscript.qmd` §12.4.4–§12.5 |
| 本专题讲义（⑤ 操作、⑥ 解读、⑨ 排错 E0–E8、⑩ 练习） | `02_lectures/master/topic04_rnaseq/04_rnaseq_lecture.md` |
| 课程脚本（quant 含 SGE 作业头；统计脚本） | `03_code/master/scripts/04_rnaseq_quant.sh`（Salmon L32–35、映射率汇总 L51–57）；`03_code/master/scripts/04_deseq2_analysis.R`（样本核对 L33–45、预过滤 L50、Wald L51、收缩 L64–65、PCA L91–97） |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch14_tpm_rounding.py`、`ch14_sample_mismatch.py`、`ch14_reversed_reflevel.py`、`ch14_ora_background.py` |
| 数据说明、登录号与下载 | `06_data/master/README.md` m04 节；`06_data/accessions.tsv`；`06_data/master/download_master.sh` |
| 环境定义与作业规格 | `07_envs/conda/env_master_transcriptome.yml`（`ngs_ms_transcriptome`）、`env_master_base.yml`（`ngs_ms_base`）；`08_assessment/master/assignments/m04_rnaseq_assignment.md` |
| 下游衔接 | m05（差异 peak ∩ 差异基因，同批样本）；第 22 章（vst 矩阵进 WGCNA/多组学） |
