---
title: "实验指导 m03：重测序与变异检测"
level: master
topic: m03
textbook: [ch10, ch07]
lecture: ../02_lectures/master/topic03_resequencing/03_resequencing_lecture.md
env: ngs_ms_variant
---

# 实验指导 m03：重测序与变异检测

> 上机时手边打开的这份文件。每一步回答四件事：做什么、敲什么、看到什么算对、看到什么
> 说明错了。原理与判据在教材第 10 章（§10.4 概念、§10.5 失效条件）与第 7 章（§7.4、
> §7.5，比对与 `@RG`），这份指导只放操作与自查入口。所有标「预期（未实测）」的数字都是
> 课程写下的自查范围，不是实测结果；本课没有在集群上真实跑完过 12 株全流程，标「集群
> 未实测」的步骤同样按预期对待。

## 0. 本实验对应什么

- **教材**：第 10 章 重测序与变异检测（主）＋第 7 章 比对与 BAM（参照）。覆盖硕士
  学习目标 LO10-04（PCR/光学重复与 BQSR 取舍）、LO10-05（HaplotypeCaller 与倍性）、
  LO10-06（位点级过滤与置缺失设计）、LO10-07（深度模型、阴性对照与阈值敏感性）。
- **学时**：m03 共 4 学时（2 理论＋2 实践，契约口径）；作业卡建议上机 5–7 小时，等待计算期间可写报告。
- **环境**：`ngs_ms_variant`（`07_envs/conda/env_master_variant.yml`：bwa=0.7.17、bwa-mem2=2.2.1、
  samtools=1.17、gatk4=4.4.0.0、bcftools=1.17、snpeff=5.1、picard、vcftools）；作图与报告用 `ngs_ms_base`。
- **计算纪律**：一切计算一律 `qsub` 投递计算节点（包括敏感性分析这种小计算）；
  登录节点只做下载、建环境、编辑。GATK 在登录节点直接跑会被杀（内存故事见步骤 5）。

## 1. 实验前检查

- **前置自测**（讲义 ②，先确认能过；题号在 `08_assessment/prerequisites/`）：
  `l0_01_linux` Q05/Q06/Q09（qsub 与作业脚本）、`l0_04_formats` Q04/Q06/Q09（SAM 与
  FLAG）、`l0_05_qc` Q04/Q05/Q09（输入必须是去接头后的 clean 数据）、`l0_06_stats`
  Q04/Q05/Q07（阈值—错误权衡与功效）。
- **激活环境并核验工具链**（与 `03_gatk_pipeline.sh` L19 同一激活写法）：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_variant
  command -v bwa bwa-mem2 samtools gatk bcftools snpEff picard
  bwa 2>&1 | grep -i version ; bwa-mem2 version ; gatk --version | head -2
  samtools --version | head -1 ; bcftools --version | head -1
  ```

  这条命令在做什么：SGE 作业不继承你终端的 conda 变量，每个作业脚本开头都会自己
  激活环境（脚本 L19）；先跑一遍 `command -v`，缺工具在投递前发现，而不是等作业失败。
  核验 7 个核心可执行文件（vcftools 同在该环境，本实验命令不直接调用，不列入）。
  版本对照 yml 钉版：bwa 0.7.17、bwa-mem2 2.2.1、GATK 4.4.0.0、samtools 1.17、
  bcftools 1.17、SnpEff 5.1（picard 未钉版）。
- **比对器口径（先知道，避免双份索引）**：环境同时装了 bwa 与 bwa-mem2，但课程脚本
  用 **bwa**（L36 守卫认 `.bwt`，L42 用 `bwa mem`）。若按讲义 ⑤5.1 用 bwa-mem2 建
  索引（`.0123` 系），守卫不会认、会再建一份 bwa 索引，两套并存。**本课一律以脚本
  为准用 bwa**；同一流程内不要混用。
- **检查点**：七条路径全部打印，版本与 yml 钉版一致。任一缺失 → 环境没激活成功，别投递。
- **出错信号**：`command not found` → 环境未激活；版本对不上 → 激活错了环境（集群上常有多个同名环境，认准 yml 创建的那个）。

## 2. 实验数据

主线是西非水稻白叶枯病菌 *Xanthomonas oryzae* pv. *oryzae*（Xoo）项目
`PRJEB100987` 中 12 株的 Illumina 双端数据，参考基因组是其中 CIX2779 株的已发表
完成图——**参考来自 12 株之一，这本身就是一个内建阴性对照**（步骤 7）。登录号全部
已登记 `06_data/accessions.tsv`（L14、L34、L39–50），零悬空：

| 登录号 | 菌株 | 数据量（登记值） |
|---|---|---|
| `ERR15732323` `ERR15732331` `ERR15732332` `ERR15732346` | CIX2353 / CIX2725 / CIX2779 / CIX2780 | 各 145–195 MB |
| `ERR15732333` `ERR15732324` `ERR15732325` `ERR15732334` | CIX2785 / CIX2951 / CIX2952 / CIX2974 | 同上 |
| `ERR15732326` `ERR15732303` `ERR15732304` `ERR15732305` | CIX2976 / CIX2983 / CIX3025 / CIX3026 | 同上 |
| `GCA_024981335` | 参考基因组（CIX2779 完成图） | 4.77 Mb |

- **下载 12 个 run**（登录节点；默认 dry-run，加 `--run` 才真下；数据一律进 scratch，
  不入 git）：

  ```bash
  cd <课程仓库路径>
  bash 06_data/master/download_master.sh --list
  bash 06_data/master/download_master.sh --topic m03 --run --outdir /d3/scratch/${USER}/ngs/data
  ls -lh /d3/scratch/${USER}/ngs/data/m03/    # 文件名以实落盘为准（ENA 原始命名）
  ```

  下载脚本自带 md5 校验并写 `SHA256_MANIFEST.tsv`；总量约 4.0 GB（README §m03，登记值）。
- **取参考基因组与注释**（下载脚本不取组装，登录节点自取；GFF 步骤 8 建 SnpEff 库要用，
  与 fna 同目录同基名）：

  ```bash
  B=https://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/024/981/335/GCA_024981335.1_ASM2498133v1/GCA_024981335.1_ASM2498133v1
  mkdir -p /d3/scratch/${USER}/ngs/data/m03
  curl -s ${B}_genomic.fna.gz | zcat > /d3/scratch/${USER}/ngs/data/m03/GCA_024981335.fna
  curl -s ${B}_genomic.gff.gz | zcat > /d3/scratch/${USER}/ngs/data/m03/GCA_024981335.gff
  grep -c '^>' /d3/scratch/${USER}/ngs/data/m03/GCA_024981335.fna   # 单记录（1 条染色体级序列）
  head -1 /d3/scratch/${USER}/ngs/data/m03/GCA_024981335.gff        # ##gff-version 3
  ```
- **数据自查**（README §m03）：12 个 run 齐、每 run 双端两个文件；参考 FASTA 单记录
  4.77 Mb（登记值）；GFF 与 FASTA 同基名就位。课堂时间有限可先跑 3 株（**必须含
  CIX2779/ERR15732332**），作业补齐 12 株。
- **ENA 原始文件必须清洗成 clean 数据再进流程**（脚本头注明的输入就是清洗后 FASTQ）：
  在 scratch 建个人清洗脚本（`#$` 头照抄课程脚本，`fastp` 在 `ngs_ms_base` 环境，
  钉 0.23.4），投递后得到 `*_1/2.clean.fq.gz`——步骤 2 的 R1/R2 指向它们：

  ```bash
  cat > /d3/scratch/${USER}/ngs/clean_fastq.sh <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N fastp_clean
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  #$ -l h_vmem=4G
  source "${CONDA_ROOT:-/opt/miniconda3}/bin/activate" ngs_ms_base
  DATA=/d3/scratch/${USER}/ngs/data/m03
  for r in ERR15732323 ERR15732331 ERR15732332 ERR15732346 ERR15732333 ERR15732324 \
           ERR15732325 ERR15732334 ERR15732326 ERR15732303 ERR15732304 ERR15732305; do
    fastp -i "${DATA}/${r}_1.fastq.gz" -I "${DATA}/${r}_2.fastq.gz" \
          -o "${DATA}/${r}_1.clean.fq.gz" -O "${DATA}/${r}_2.clean.fq.gz" \
          -j "${DATA}/${r}.fastp.json" -h "${DATA}/${r}.fastp.html" -w "${NSLOTS:-4}"
  done
  EOF
  qsub /d3/scratch/${USER}/ngs/clean_fastq.sh
  ls /d3/scratch/${USER}/ngs/data/m03/*.clean.fq.gz | wc -l   # 24（12 run × 双端）
  ```

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出 / 检查点 / 出错信号。
> 命令里的脚本名、参数名、输出文件名与 `03_code/master/scripts/` 现版逐字一致
> （本指导修订时已逐个 grep 核对，见任务回执）。12 株真实流程本课未在集群实测，
> 一切区间写「预期（未实测）」。
>
> **在哪敲命令**：下文 scratch 路径以 `/d3/scratch/${USER}/ngs` 为根；`<课程仓库路径>` 指课程仓库在本机的位置（校内集群由教师公布）。两个脚本都带 `#$ -cwd`：作业日志写在**投递时所在的目录**，产出写在脚本内部 `OUTDIR` 指定的目录，两者不是一回事。`03_code/` 是课程公共目录、只读；凡要改脚本一律「cp 个人副本 → 改指定行 → grep 确认 → qsub 副本」，不改原文件——qsub 按提交时的脚本执行，**投递后无法再补参数**。

### 步骤 0：工作目录与投递前检查（登录节点）

- **目的**：让作业排队之前，目录、数据、环境都就位。
- **命令**：

  ```bash
  mkdir -p /d3/scratch/${USER}/ngs/{data/m03,variant,joint,sens,results}
  ls -lh /d3/scratch/${USER}/ngs/data/m03/    # 12 run × 双端 raw + .clean.fq.gz + GCA_024981335.fna/.gff
  source /opt/miniconda3/bin/activate && conda activate ngs_ms_variant
  command -v bwa samtools gatk bcftools       # 见 §1
  ```

- **产出**：`/d3/scratch/${USER}/ngs/{data/m03,variant,joint,sens,results}` 目录就绪。
- **检查点**：§2 自查数字全部对得上（12 run、参考单记录、GFF 就位）；24 个 clean
  文件已生成；`command -v` 四件套齐全。
- **出错信号**：数据不全就投递 → 作业集体失败还占排队资源；先停，补数据。

### 步骤 1：参考三套索引（脚本 step 0 的守卫，L36–38）

- **目的**：bwa 索引（`.bwt/.amb/.ann/.pac/.sa`）、samtools 索引（`.fai`）、GATK
  字典（`.dict`）三套先生成、先验收，再批量投递样本作业（讲义 ⑨-E1/E3）。
- **为什么先做**：12 个作业同时起跑会**抢建同一套索引**——脚本的守卫只查文件存在、
  不加锁，两个作业同时发现缺 `.bwt` 就会各建一遍，甚至读到建了一半的索引。
  顺序固定：先投 1 株 → 等三套索引落盘并验收 → 再投其余 11 株。
- **命令**（先投 CIX2779 一株，它的 step 0 守卫会自动建缺的三套索引）：

  ```bash
  cd /d3/scratch/${USER}/ngs
  DATA=/d3/scratch/${USER}/ngs/data/m03
  qsub -v SAMPLE=CIX2779,R1=${DATA}/ERR15732332_1.clean.fq.gz,R2=${DATA}/ERR15732332_2.clean.fq.gz,REF=${DATA}/GCA_024981335.fna \
       <课程仓库路径>/03_code/master/scripts/03_gatk_pipeline.sh
  qstat -u ${USER}     # 等它从 qw 变 r（开始运行后守卫才会建索引）
  ls -l ${DATA}/GCA_024981335.fna*          # 多出 .bwt/.amb/.ann/.pac/.sa .fai .dict
  cut -f1 ${DATA}/GCA_024981335.fna.fai     # contig 名记录在案（只有 1 行）
  ```

  守卫行为（grep 脚本可见，不用手动建）：`[[ -e "${REF}.bwt" ]] || bwa index`
  （L36）、`[[ -e "${REF}.fai" ]] || samtools faidx`（L37）、`[[ -e "${REF%.*}.dict" ]]
  || gatk CreateSequenceDictionary`（L38）——缺哪套建哪套。**守卫只查存在、不查
  版本**：换参考而旧索引同名残留时，流程对着旧参考静默跑歪（教材 §10.5.3 排查
  第②步），换参考必须连同旧索引一起清掉重建。
- **产出**：参考旁多出 `.bwt .amb .ann .pac .sa .fai .dict`；后续 11 株作业直接复用。
- **检查点**：三套文件时间戳一致；`.fai` 的 contig 名记下来——后续所有 `-L` 与联合
  调用都按它写，**不要写死 `chr01`**（写死名字不匹配会得到空结果且可能不报错，教材
  §10.6、ch07 §7.5.3）。
- **出错信号**：`Fasta dict file … does not exist` → 缺 `.dict`（⑨-E1）；
  `incompatible contigs` → 参考与 BAM 不同源（⑨-E3）：全流程锁定同一份 FASTA。

### 步骤 2：比对与前处理（`qsub 03_gatk_pipeline.sh`，SGE 头 L3–7）

- **目的**：bwa 比对 → 排序建索引 →（脚本后续步骤 3–5）一条龙。`@RG` 的 `SM`
  决定 VCF 样本列名，写错下游全歪（教材 §10.6 表）。
- **命令**（登录节点投递；入口变量 `SAMPLE/R1/R2/REF` 必填，脚本 L21–24；CIX2779
  已在步骤 1 投过，这里投其余 11 株）：

  ```bash
  cd /d3/scratch/${USER}/ngs
  DATA=/d3/scratch/${USER}/ngs/data/m03
  REF=${DATA}/GCA_024981335.fna
  # 其余 11 株循环投递（课堂可先只投 2 株打通链路；OUTDIR 默认 ./variant/${SAMPLE}）：
  while read -r sample run; do
    qsub -v SAMPLE=${sample},R1=${DATA}/${run}_1.clean.fq.gz,R2=${DATA}/${run}_2.clean.fq.gz,REF=${REF} \
         <课程仓库路径>/03_code/master/scripts/03_gatk_pipeline.sh
  done <<'EOF'
  CIX2353 ERR15732323
  CIX2725 ERR15732331
  CIX2780 ERR15732346
  CIX2785 ERR15732333
  CIX2951 ERR15732324
  CIX2952 ERR15732325
  CIX2974 ERR15732334
  CIX2976 ERR15732326
  CIX2983 ERR15732303
  CIX3025 ERR15732304
  CIX3026 ERR15732305
  EOF
  qstat -u ${USER}     # qw 排队 / r 运行 / Eqw 报错
  ```

  这条命令在做什么：脚本头 `-N gatk_pipeline -pe smp 16 -l h_vmem=8G`（L3–7）；
  `THREADS=${NSLOTS:-16}`（L26）；比对 `bwa mem -t "${THREADS}" -M
  -R "@RG\tID:${SAMPLE}\tSM:${SAMPLE}\tPL:ILLUMINA\tLB:lib1"`（L42–44）｜
  `samtools sort -@ 4 -o …sorted.bam -`（L45）｜ `samtools index`（L46）。
  脚本用**双引号**插值写 `@RG`——Bash 单双引号都保留字面 `\t`，危险的是多层转义
  丢分隔符，不是引号本身；纪律是传参后核对头行（检查点 3，ch07 §7.4.7/§7.5.4）。
  `-M` 把 split 次要比对标为 secondary（Picard/GATK 传统要求）。
- **产出**：`variant/<SAMPLE>/<SAMPLE>.sorted.bam(.bai)`；作业日志 `gatk_pipeline.o<作业号>`（投在本目录，`#$ -cwd -j y`）。
- **检查点**（README §m03 自查判据，**预期、未实测**）：
  1. `samtools flagstat variant/<SAMPLE>/<SAMPLE>.sorted.bam`——比对率 **>95%**（同物种
     不同株）；**<85% 先查是不是选错参考**。这是本项目预期区间，不是跨数据健康线
     （ch07 §7.6 边界 3）。
  2. 手动验收四件套（ch07 §7.5.2，脚本无此防护，自己补）：`samtools quickcheck`；
     FASTQ 读段总数（R1+R2）与 `samtools view -c -F 0x900 …sorted.bam` 对账（应相等）；
     `samtools idxstats … | head` 分 contig 无异常空缺。
  3. `samtools view -H variant/<SAMPLE>/<SAMPLE>.sorted.bam | grep '^@RG'`——
     一行 `@RG`，`ID/SM/PL/LB` 齐全、`SM` 等于你的 `SAMPLE`、字段间是制表符。
- **出错信号**：
  - 下游 `missing the read group (RG) tag`（⑨-E2）→ 比对时 `@RG` 没注进去，
    回查头行；重新比对，不要用 `AddOrReplaceReadGroups` 硬补（丢 lane 级信息，
    BQSR 分组失真，讲义 ⑨-E2）。
  - `no ID within the read group line`（rc≠0）→ `@RG` 行里 `\t` 真丢了（多层
    转义），检查你改过的副本里 `-R` 写法，回 ch07 §7.5.4。
  - 比对率 <85% → 参考选错 / 污染 / 接头未去（README 判据 + ch07 §7.5.5），不要盲目
    调高允许错配数硬贴。

### 步骤 3：标记重复（脚本 step 2，L49–53）

- **目的**：MarkDuplicates 按两端 5' 坐标、方向与插入片段长度判重，保留质量最高
  一对、其余打 `0x400`——只标记不删除（教材 §10.4.2、§10.5.1）。
- **命令**：随步骤 2 的同一作业自动执行。核对参数：

  ```bash
  grep -n 'MarkDuplicates\|dedup.bam\|dup_metrics' <课程仓库路径>/03_code/master/scripts/03_gatk_pipeline.sh
  grep '^## METRICS CLASS' -A2 variant/<SAMPLE>/<SAMPLE>.dup_metrics.txt   # PERCENT_DUPLICATION 所在表
  ```

  脚本为 `gatk MarkDuplicates -I sorted.bam -O dedup.bam -M dup_metrics.txt`
  （L49–52）＋ `samtools index dedup.bam`（L53）。**未启用**
  `--OPTICAL_DUPLICATE_PIXEL_DISTANCE`：默认 100；只有图案化流动槽（如 NovaSeq）才
  需要 2500，且前提是读段名能解析出 tile/x/y 坐标——本课 Xoo 数据不是该场景，不要加
  （教材 §10.4.2）。
- **产出**：`variant/<SAMPLE>/<SAMPLE>.dedup.bam(.bai)`、
  `variant/<SAMPLE>/<SAMPLE>.dup_metrics.txt`。
- **检查点**（教材 §10.5.1 口径，**不设通用红线，不设数字经验区间**）：
  1. `PERCENT_DUPLICATION` 进报告，与建库方式、基因组大小、深度一起读，并与同批
     样本横向比——明显偏离同批样本才需要解释，不凭绝对数值下结论。
  2. 统计口径写清：samtools 1.17 的 `depth` 默认排除 `0x400`，同一份 BAM 去重前后
     用默认参数统计深度会下降；报告写明工具、参数与排除规则（教材 §10.4.2）。
  3. 去重前后对照（合成算例，rc=0，在课程仓库根目录运行）：
     `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch10_pcr_duplicate_support.py --selftest`
     ——24 分子、一个错误分子扩增 8 份，表观重复率 7/31≈22.6%，去重前 `AD=23,8`
     质量代理 91.9 → 去重后 `AD=23,1`、代理 6.7；批对照判变异 4.9%→0.0%。真实数据
     不会这么整齐，读法是「去重前后对照」不是套这两个数。
- **出错信号**：
  - `Value was put into PairInfoMap more than once` → 同一读段名出现多次：
    多 lane 用 `cat` 合并了（⑨-E6），改用 `samtools merge`/`MergeSamFiles` 且
    各 lane `@RG ID` 唯一。
  - 去重后有效深度骤降 → 10.4.6 的 `d` 变小、功效重估（教材 §10.5.1），
    不是「数据不可用」的结论。

### 步骤 4：BQSR 决策（脚本 step 3，L55–67）

- **目的**：决定做不做碱基质量重校准，并把理由写进方法学。本课默认**跳过**。
- **命令**：无新命令。脚本默认 `SKIP_BQSR=1`（L27），命中 else 分支打印跳过提示
  （L64–67）；仅当显式 `SKIP_BQSR=0` 且提供 `KNOWN_SITES`（L28、L57）才跑
  `BaseRecalibrator`＋`ApplyBQSR`（L58–63）。
- **产出**：本课无新文件；作业日志里有跳过提示行。
- **检查点**：方法学按教材 §10.4.3 的口径写——「没有可用的独立 known-sites，
  因此未做 BQSR，用 FS/SOR/ReadPosRankSum/MQ 的位点级过滤补偿残余偏差」。
  两个不要：不要写「因为是非模式物种所以不做」（有没有可信屏蔽集才是理由）；
  不要照抄脚本注释当方法学句子。若真跑了 BQSR：报告写 known-sites 来源与版本、
  校正前后质量分布（`AnalyzeCovariates`），并交代自举的循环依赖风险——轮次没有
  通用标准，不写「跑一两轮就收敛」（教材 §10.4.3）。
- **出错信号**：跳过提示没出现、也没有 recal 表 → 副本分支逻辑动过了，回 grep
  `SKIP_BQSR` 核对；报告出现「固定轮数收敛」类句子 → 按 §10.4.3 改写。

### 步骤 5：变异检出 gVCF（脚本 step 4，L70–73）

- **目的**：HaplotypeCaller 以 gVCF 模式输出每株的变异证据（含 `<NON_REF>` 参考块），
  区分「未变异」与「未测到」（教材 §10.4.5）。
- **命令**：同一作业自动执行：

  ```bash
  grep -n 'HaplotypeCaller\|ERC GVCF\|ploidy\|native-pair-hmm' \
       <课程仓库路径>/03_code/master/scripts/03_gatk_pipeline.sh
  ```

  `gatk HaplotypeCaller -R "${REF}" -I "${BAM_FOR_CALL}" -O "${SAMPLE}.g.vcf.gz"
  -ERC GVCF -ploidy "${PLOIDY}" --native-pair-hmm-threads "${THREADS}"`（L70–73）。
  脚本现版默认 `PLOIDY=1`（L31，注释写明 Xoo 单倍体→1、自交纯系二倍体植物→2、GATK
  默认 2）。**Xoo 是单倍体，保持默认 1 即可**；换二倍体数据要显式改回 2（改副本默认值
  或 `qsub -v PLOIDY=2`）。脚本**没有 `-L`**：单 contig 小参考无需切区间；若自行加
  `-L`，contig 名必须取自 `.fai`（步骤 1 已记录），写死名字会返回空结果且可能不报错
  （教材 §10.6、ch07 §7.5.3）。
- **产出**：`variant/<SAMPLE>/<SAMPLE>.g.vcf.gz(.tbi)`。
- **检查点**：
  1. `bcftools view variant/<SAMPLE>/<SAMPLE>.g.vcf.gz | grep -m1 NON_REF` 能命中
     参考块——gVCF 的标志。
  2. `bcftools query -f '%GT\n' variant/<SAMPLE>/<SAMPLE>.g.vcf.gz | sort | uniq -c | head`
     ——单倍体输出 `GT` 是**单个数字**（0/1）或缺失 `.`；出现 `0/1`、`1/1`、`./.`
     说明按二倍体分型了：`PLOIDY` 被改回 2 或用了旧版脚本（教材 §10.4.1/§10.4.8）。
  3. 关注区抽查 `bcftools view variant/<SAMPLE>/<SAMPLE>.g.vcf.gz | grep -m3 'END='`：
     `MIN_DP` 是块内最小值，=0 只说明块内至少一处深度为 0，推不出整块未覆盖
     （教材 §10.4.5、§10.5.4）。
- **出错信号**：
  - `OutOfMemoryError: Java heap space`（⑨-E5）→ 脚本**没有**设 `-Xmx`、
    SGE 头 `h_vmem=8G`（L7）：4.77 Mb 参考下默认堆够用；若自己加
    `--java-options "-Xmx16g"`，qsub 内存必须大于 `-Xmx`（JVM 另有开销）。
  - 关注基因没有参考块 / `MIN_DP` 极低 → 可能真没测到，先回深度统计，别急着下
    「无变异」结论（§10.5.4）。

### 步骤 6：验收统计与可判定区域（脚本 step 5，L76–77 ＋ 手动补）

- **目的**：拿报告必填的比对/深度数字，补脚本不做的可判定区域（callable）统计——
  **没有它，「某基因无变异」不成立**（教材 §10.4.8、§10.5.4）。
- **命令**（脚本部分自动；callable 与三张汇总表手动补，计算走 qsub 或并入你的
  作业脚本；门槛自定并写进报告）：

  ```bash
  grep -n 'flagstat\|coverage' <课程仓库路径>/03_code/master/scripts/03_gatk_pipeline.sh
  # 可判定区域（教材 10.4.8 三道门槛：深度、比对质量、不在已知不可判定区。
  # 本课数据只做前两道——DP≥5、MAPQ≥20；第三道没有已知的不可判定区清单，报告里
  # 如实写明「近似口径」。分母=参考全长；单 contig 参考 depth -a 即全量，多 contig
  # 参考的 -a/-aa 口径见 ch07 §7.4.6；samtools 1.17 depth 的 -Q 是 MAPQ）：
  cd /d3/scratch/${USER}/ngs
  REF=/d3/scratch/${USER}/ngs/data/m03/GCA_024981335.fna
  awk '{t+=$2}END{print "ref_len="t}' "${REF}.fai"   # 分母核对：应等于深度行数
  SAMPLES="CIX2353 CIX2725 CIX2779 CIX2780 CIX2785 CIX2951 CIX2952 CIX2974 CIX2976 CIX2983 CIX3025 CIX3026"
  printf "sample\tcovered_dp5_mapq20_fraction\n" > results/callable_summary.tsv
  for s in ${SAMPLES}; do
    samtools depth -a -Q 20 "variant/${s}/${s}.dedup.bam" \
      | awk -v s="${s}" '$3>=5{n++} END{ if(NR==0){printf "%s\tNA\n", s; exit}
          printf "%s\t%.4f\n", s, n/NR }' >> results/callable_summary.tsv
  done
  # 也可用 gatk CallableLoci 交叉核对（第三道门槛它替你管）
  ```

  脚本输出 `flagstat.txt`（L76）与 `coverage.txt`（L77）进 `variant/<SAMPLE>/`。
- **产出**：`variant/<SAMPLE>/<SAMPLE>.flagstat.txt`、`.coverage.txt`；
  `results/callable_summary.tsv`（两列：样本名、达标位点占参考全长比例；作业必交）。
  同目录再汇总两张（作业必交；awk 以 samtools 1.17 / GATK 4.4.0.0 输出格式为准；
  `${SAMPLES}` 沿用上面 callable 块的定义）：

  ```bash
  printf "sample\tmapped_pct\tproperly_paired_pct\tsingletons_pct\n" > results/flagstat_all.tsv
  printf "sample\tPERCENT_DUPLICATION\n" > results/dup_metrics_all.tsv
  for s in ${SAMPLES}; do
    awk -v s="${s}" '
      $4=="mapped"                   { match($0, /\([0-9.]+%/); M=substr($0,RSTART+1,RLENGTH-2) }
      $4=="properly" && $5=="paired" { match($0, /\([0-9.]+%/); P=substr($0,RSTART+1,RLENGTH-2) }
      $4=="singletons"               { match($0, /\([0-9.]+%/); G=substr($0,RSTART+1,RLENGTH-2) }
      END{ printf "%s\t%s\t%s\t%s\n", s, M, P, G }' "variant/${s}/${s}.flagstat.txt" >> results/flagstat_all.tsv
    awk -v s="${s}" -F'\t' '/^## METRICS CLASS/{f=1;next} f&&/^LIBRARY/{d=1;next} \
        d&&NF>1{printf "%s\t%s\n", s, $(NF-1); exit}' "variant/${s}/${s}.dup_metrics.txt" >> results/dup_metrics_all.tsv
  done
  ```

  flagstat 某行是 `-nan%`（如无双端记录）属正常，照实抄并在报告注明口径。
- **检查点**：比对率 >95%（预期，判据同步骤 2）；**callable 近似比例必须进报告**（作业
  「结果正确性」硬项；阴性结论写法是「在可判定区域内未检出变异」，教材 §10.5.4）。
- **出错信号**：covered 比例高但 callable 低 → 大量位点深度/MAPQ 不达标，报告深度
  分布与可判定区域比例；覆盖度 ≠ 可判定区域（教材 §10.4.8），不得混用。

### 步骤 7：阴性对照——CIX2779 自比（教材 §10.5.3；README「务必跑一遍」）

- **目的**：CIX2779 的读段（ERR15732332）比对自己的完成图（GCA_024981335），变异数
  应**接近 0**——这是整条流程的内建标准答案，跑完主线先看这一眼。
- **命令**：步骤 1 已对 `SAMPLE=CIX2779` 投过作业，gVCF 在 `variant/CIX2779/` 下。
  **不要把它混进 12 株联合 VCF 当第 13 个样本**：自比必须单独分型、单独过滤、
  单独数（教材 §10.6）。①③ 直接照敲；②是过滤链，不在这里重复抄一遍——把步骤 8
  的第 2) 块原样复制一份，只改复制出来的那份，做三处全局替换（都在 `joint/` 之后）：
  `raw`→`self_raw`、`filt`→`self_filt`、`pass.vcf.gz`→`self_pass.vcf.gz`。
  ①–③ 和步骤 8 的联合命令一起放进你的个人作业副本（怎么建副本、怎么投递见
  步骤 8），在计算节点跑，不要在登录节点直接 gatk：

  ```bash
  # ① 单独分型（同一参考、同一索引）
  gatk GenotypeGVCFs -R "${REF}" \
      -V /d3/scratch/${USER}/ngs/variant/CIX2779/CIX2779.g.vcf.gz \
      -O joint/self_raw.vcf.gz
  # ② 见上：复制步骤 8 第 2) 块 + 三处替换，产出 joint/self_pass.vcf.gz
  # ③ 计数（进报告的阴性对照一栏）
  bcftools view -H joint/self_raw.vcf.gz | wc -l            # 原始变异数
  bcftools view -f PASS -H joint/self_pass.vcf.gz | wc -l   # PASS 变异数
  ```
- **产出**：CIX2779 的原始/PASS 变异计数（进报告的阴性对照一栏）。
- **检查点**（README §m03，**设计预期、未实测**）：变异数**接近 0**；「接近 0」是设计
  预期不是恒等式——结果为 0 也只覆盖可判定区域（重复区、低覆盖区、参考缺口不在
  检验内，教材 §10.5.3）。
- **出错信号**：明显不为 0 → 按教材 §10.5.3 四步查，**顺序不颠倒**：
  ① 倍性（是否 `-ploidy 1`）→ ② 参考版本与 `.fai/.dict/.bwt` 是否同源
  （守卫只查存在不查版本）→ ③ `@RG` 的 `SM` 与比对参数（是否混样）→
  ④ 非零位点是否集中在重复/低 MAPQ/高深度异常区（看 `AD`、`MAPQ` 形态）。
  四步走完再谈「这株是否真的与参考不同」。

### 步骤 8：联合分型、过滤与注释（个人副本封装后 qsub；集群未实测）

- **目的**：课程脚本只到单样本 gVCF（脚本 L70–73；分工见教材 §10.6）；联合分型、
  SNP/InDel 分开硬过滤、注释要你自己封装——这正是作业要求提交「改版脚本」的原因。
- **命令**（建副本 → 改指定行 → grep 确认 → qsub；以下即作业脚本正文要点）：

  ```bash
  cp <课程仓库路径>/03_code/master/scripts/03_gatk_pipeline.sh /d3/scratch/${USER}/ngs/joint/gatk_pipeline.sh
  ```

  改副本：**保留**顶部 `#$` 开头的 SGE 头（`-pe smp 16`、`-l h_vmem=8G` 等）与
  conda 激活行（L19）；把 L21–77（单样本入口变量与步骤 0–5）整段替换为
  `REF="${REF:?必须指定 REF=参考 fasta}"` ＋ 步骤 7 的自比块 ①–③ ＋ 下面 0)–4)。
  副本直接命名 `gatk_pipeline.sh`——与 §7 提交物 `scripts/gatk_pipeline.sh` 同名。

  ```bash
  cd /d3/scratch/${USER}/ngs
  # 0) 样本对照表：两列制表符（样本名 ↔ gVCF 路径），样本名 = @RG 的 SM
  for s in CIX2353 CIX2725 CIX2779 CIX2780 CIX2785 CIX2951 CIX2952 CIX2974 CIX2976 CIX2983 CIX3025 CIX3026; do
    printf "%s\t%s\n" "${s}" "/d3/scratch/${USER}/ngs/variant/${s}/${s}.g.vcf.gz"
  done > joint/samples.map
  cat -A joint/samples.map | head -3          # 两列、中间是 ^I（制表符）
  # 1) 联合分型（workspace 必须不存在，重跑先 rm -rf；-L 是 GenomicsDBImport 的必需
  #    参数，contig 名取自 .fai——步骤 1 已记录，不要写死 chr01）
  CONTIG=$(cut -f1 /d3/scratch/${USER}/ngs/data/m03/GCA_024981335.fna.fai | head -1)
  gatk GenomicsDBImport --sample-name-map joint/samples.map \
      --genomicsdb-workspace-path joint/gvcf_db \
      -L "${CONTIG}"
  gatk GenotypeGVCFs -R "${REF}" -V gendb://joint/gvcf_db -O joint/raw.vcf.gz
  # 2) SNP 与 InDel 分开过滤（六条 SNP 起点 = GATK 文档起点，教材 §10.4.7；逐条分开写，
  #    不用 || 串联——否则静默放行无法按条计数）
  gatk SelectVariants -V joint/raw.vcf.gz -select-type SNP -O joint/raw_snp.vcf.gz
  gatk VariantFiltration -V joint/raw_snp.vcf.gz -O joint/filt_snp.vcf.gz \
      --filter-name "QD2"  --filter-expression "QD < 2.0" \
      --filter-name "FS60" --filter-expression "FS > 60.0" \
      --filter-name "MQ40" --filter-expression "MQ < 40.0" \
      --filter-name "SOR3" --filter-expression "SOR > 3.0" \
      --filter-name "MQRS" --filter-expression "MQRankSum < -12.5" \
      --filter-name "RPRS" --filter-expression "ReadPosRankSum < -8.0"
  gatk SelectVariants -V joint/raw.vcf.gz -select-type INDEL -O joint/raw_indel.vcf.gz
  gatk VariantFiltration -V joint/raw_indel.vcf.gz -O joint/filt_indel.vcf.gz \
      --filter-name "QD2"   --filter-expression "QD < 2.0" \
      --filter-name "FS200" --filter-expression "FS > 200.0" \
      --filter-name "RPRS20" --filter-expression "ReadPosRankSum < -20.0"
  gatk MergeVcfs -I joint/filt_snp.vcf.gz -I joint/filt_indel.vcf.gz -O joint/filt_all.vcf.gz
  bcftools view -f PASS joint/filt_all.vcf.gz -Oz -o joint/pass.vcf.gz && bcftools index joint/pass.vcf.gz
  # 3) 逐条拦截计数（作业 filter_counts.tsv 的来源；计数 0 要解释，见检查点）
  #    按整条 FILTER 字符串计数（看组合形态）：
  bcftools query -f '%FILTER\n' joint/filt_snp.vcf.gz   | sort | uniq -c | sort -rn > joint/filter_counts_snp.tsv
  bcftools query -f '%FILTER\n' joint/filt_indel.vcf.gz | sort | uniq -c | sort -rn > joint/filter_counts_indel.tsv
  #    按标签拆分计数——一条记录带 QD2;FS60 时两条规则各计一次，这才是「每条规则拦了多少」：
  bcftools query -f '%FILTER\n' joint/filt_snp.vcf.gz   | tr ';' '\n' | grep -vx PASS | sort | uniq -c | sort -rn > joint/filter_tag_counts_snp.tsv
  bcftools query -f '%FILTER\n' joint/filt_indel.vcf.gz | tr ';' '\n' | grep -vx PASS | sort | uniq -c | sort -rn > joint/filter_tag_counts_indel.tsv
  # 4) 注释（非模式物种自建 SnpEff 库：不碰 conda 安装目录的全局配置，全部放在
  #    joint/snpeff/ 下；输入就是 §2 下载的 GFF）
  mkdir -p joint/snpeff/data/CIX2779
  ln -sf /d3/scratch/${USER}/ngs/data/m03/GCA_024981335.fna joint/snpeff/data/CIX2779/sequences.fa
  ln -sf /d3/scratch/${USER}/ngs/data/m03/GCA_024981335.gff joint/snpeff/data/CIX2779/genes.gff
  printf 'CIX2779.genome : CIX2779\n' > joint/snpeff/snpEff.config
  snpEff build -c joint/snpeff/snpEff.config -dataDir joint/snpeff/data -gff3 -v CIX2779
  # 建完核对日志里的基因数与 CDS 数，与 GFF 一致（讲义 ⑨-E8、教材 §10.4.10）
  snpEff -c joint/snpeff/snpEff.config -dataDir joint/snpeff/data -v CIX2779 joint/pass.vcf.gz > joint/annotated.vcf
  bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%INFO/ANN\n' joint/annotated.vcf \
    | grep -w HIGH | awk '!seen[$1,$2]++' > joint/high_impact.tsv
  ```

  InDel 只放宽 FS（200）与 ReadPosRankSum（−20）两项，其余阈值不要按倍数类推放宽
  （教材 §10.4.7）；`--filter-name` 与 `--filter-expression` 成对且顺序对应；
  `bcftools view -f PASS` 提取前确认 FILTER 列不是 `.`（没跑过 VariantFiltration 时
  PASS 为空，讲义 ⑥6.4）。HIGH 清单按位点去重——一个变异可能有多条 `ANN`（不同
  转录本），不去重会重复计数（教材 §10.4.10、作业失分点 8）。
- **提交前核对与投递**（改了副本必须 grep，别凭记忆）：

  ```bash
  grep -n 'GenomicsDBImport\|GenotypeGVCFs\|filter-expression\|snpEff build\|ploidy' \
       /d3/scratch/${USER}/ngs/joint/gatk_pipeline.sh
  cd /d3/scratch/${USER}/ngs && qsub -v REF=${REF} joint/gatk_pipeline.sh   # 只传 REF
  ```
- **产出**：`joint/self_*`（自比，步骤 7）、`raw.vcf.gz`、`filt_snp/indel.vcf.gz`、
  `filt_all.vcf.gz`、`pass.vcf.gz`、`annotated.vcf`、`high_impact.tsv`、
  `filter_counts_snp/indel.tsv` 与 `filter_tag_counts_snp/indel.tsv`
  （作业 `filter_counts.tsv` 由它们整理，建议交拆标签版并说明口径）。
- **检查点**（README §m03，**预期、未实测**）：
  1. 原始变异数**数万级**；硬过滤后保留 **60–80%**（两者都是课程预期，写成「预期」）。
  2. **Ti/Tv 只报告实测值**：细菌没有人类 2.0–2.1 的基线，不设目标值；随机期望 0.5
     （12 类替换等可能，算术）只用于方向判读（教材 §10.4.9）。
  3. 每条 filter 的拦截计数：**>0，或解释为 0**（这条规则确无位点命中 vs 表达式
     引用缺失标签静默放行——两种情形必须在报告里区分，教材 §10.5.2、作业失分点 1）。
     验证动作：`bcftools view -h … | grep INFO=` 只是初筛（头里有声明≠每条有值）；
     `bcftools query -f '%INFO/MQRankSum\n' joint/raw_snp.vcf.gz | head` 把标签逐条
     打印看缺失发生在哪些记录；再构造一个缺标签的小 VCF 复跑一次过滤确认行为。
  4. 联合 VCF 样本列数=12、列名=samples.map 第一列；出现 `sample1` 或塌成一列
     → 回查 `@RG SM`（教材 §10.6 表）。
- **出错信号**：
  - 日志 `WARN … undefined variable <tag>`、退出码 0、某条规则计数 0 → 失效条件 2
    （教材 §10.5.2）：**不要**拿 `--missing-values-evaluate-as-failing=true` 当
    万能修复——它会把低深度下天然算不出秩和的位点整体判不合格（过度过滤一侧）。
  - `A USER ERROR has occurred: No intervals specified` → GenomicsDBImport 缺 `-L`，
    补上并从 `.fai` 取 contig 名（步骤 1）。
  - `bcftools view -f PASS` 为空 → FILTER 列是 `.`，VariantFiltration 没跑过（讲义 ⑥6.4）。
  - `Cannot read file '.../snpEffectPredictor.bin'` → SnpEff 库没建或 `-c/-dataDir`
    没配对（⑨-E8），回建库步骤核对基因数/CDS 数。
  - 样本列对不上 → samples.map 两列顺序（样本名、gVCF 路径）与 `@RG SM` 一致性。

### 步骤 9：阈值敏感性（`qsub 03_filter_sensitivity.sh`，作业必跑）

- **目的**：把 QD/FS 阈值扫一遍，看到保留数与 Ti/Tv 随阈值怎么变——作业「方法选择
  与结果可信度说明」（占 30%）的直接证据。
- **命令**（脚本带 SGE 头 `-N filter_sens -pe smp 4`；现版支持 `-v/-o` 与
  位置参数两种调用，L22–30）：

  ```bash
  cd /d3/scratch/${USER}/ngs
  qsub <课程仓库路径>/03_code/master/scripts/03_filter_sensitivity.sh \
       -v joint/raw_snp.vcf.gz -o sens/snp
  cat sens/snp/sensitivity.tsv      # 8 行网格 + 表头
  ```

  网格 **QD 1/2/3/5 × FS 30/60 共 8 组**（L49–51），MQ 40、SOR 3 固定；输出表头
  `QD FS MQ SOR n_SNP n_INDEL Ti_Tv mean_DP`（L46）。运行前脚本自动清点 QD/FS/MQ/SOR
  缺失记录数并警告（L37–43），与步骤 8 的逐条计数互相印证；`bcftools.log` 在输出
  目录里，跑完先看一眼。
- **产出**：`sens/snp/sensitivity.tsv`、`sens/snp/bcftools.log`；作业的
  `sensitivity_table.tsv` 即取此表（8 行全附，或按读表口径选代表行，见检查点 3）。
- **检查点**：
  1. 方向判据只 borrowed 自合成模型（教材 §10.4.7 带 demo 入口）：在那份固定分布的
     合成数据上阈值放松 → 保留数单调升、Ti/Tv 单调降。合成量级（rc=0，在课程仓库
     根目录运行）：
     `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch10_filter_thresholds.py --selftest`
     ——8 格保留 3994→5339、Ti/Tv 1.896→1.339。**单调性由合成分布保证，不是真实
     数据的判据**：Xoo 上报告实测变化即可；若不单调（某档新放进来的位点恰好转换
     偏多），如实描述并讨论，不硬套 demo 方向。
  2. **不套人类 2.0–2.1**：脚本 NOTE 与教材 §10.4.9 同口径；Xoo 报告实测值并
     解释（脚本 L58–59 注释）。
  3. 作业卡「宽/默认/严三组」是**读表口径**，不是脚本分组：8 行网格里按读法选
     代表行（如 宽≈QD1/FS60、默认≈QD2/FS60、严≈QD5/FS30），报告写明你选了哪组、
     依据是什么、与相邻档位差多少（教材 §10.4.9 参数敏感性）。
  4. `mean_DP` 列（各组平均深度）进 `sensitivity_table.tsv`——作业卡三对照列
     （变异数、Ti/Tv、平均深度）与脚本输出一一对应。
- **出错信号**：`错误：找不到输入 VCF`（rc=2）→ 路径/文件名，回步骤 8 确认
  `raw_snp.vcf.gz` 已产出；预清点钱某标签缺失 >0 → 与步骤 8 检查点 3 同款处理。
  脚本只对 bcftools 负责：复合表达式演示「阈值怎么扫」，**不具备** GATK 缺失值
  语义，不能替代步骤 8 的逐条计数核查（教材 §10.4.7 末段）。

## 4. 结果记录表（学生填写）

只列栏目与单位，不预填结果；「预期」列全部标「预期、未实测」。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 2 比对 | 比对率（各样本） | %（flagstat mapped） | | >95%；<85% 查参考（README §m03，预期）；四件套对账（ch07 §7.5.2） |
| 2 比对 | `@RG` 头行 | 文字 | | ID/SM/PL/LB 齐全，SM=SAMPLE（ch07 §7.5.4） |
| 3 去重 | PERCENT_DUPLICATION（各样本） | % | | 不设红线；与建库方式/基因组大小/深度同读＋横向比（§10.5.1）；注明 depth 的 FLAG 口径 |
| 5 gVCF | 参考块 `NON_REF`/`END`/`MIN_DP` | 行/区间/× | | 有参考块；GT 单数字形态，无二倍体 `0/1`（§10.4.1） |
| 6 callable | 达标位点比例（DP≥5/MAPQ≥20 近似口径） | % | | 必报；阴性结论绑定它；完整 callable 还有第三道门槛，未做须写明（§10.4.8、§10.5.4） |
| 7 自比 | CIX2779 原始/PASS 变异数 | 个 | | 接近 0（设计预期、未实测）；不为 0 走四步排查（§10.5.3） |
| 8 联合 | 原始变异数 / 保留比例 | 个 / % | | 数万级 / 60–80%（README §m03，预期） |
| 8 过滤 | 每条 filter 拦截计数 | 个 | | 全 >0 或解释为 0（区分「无命中」与「静默放行」，§10.5.2） |
| 8 过滤 | Ti/Tv 实测值 | — | | 只报实测不设基线；随机期望 0.5（§10.4.9） |
| 8 注释 | HIGH 影响变异（去重后） | 个 | | 按位点去重；核对自建库基因数/CDS 数（§10.4.10） |
| 9 敏感性 | 8 组网格（n_SNP/Ti_Tv/mean_DP） | 个/—/× | | demo 方向：放松→保留升、Ti/Tv 降（合成算例）；真实数据报告实测、不硬套单调 |

## 5. 失效条件对照（教材 §10.5，本实验里在哪一步、看什么察觉）

1. **PCR 重复伪造等位支持度**（§10.5.1）｜步骤 3：`PERCENT_DUPLICATION` 进报告，与
   建库方式、基因组大小、深度一起读（不设通用红线）；候选变异做去重前后
   `AD/DP/QUAL` 对照；统计深度写明工具与 FLAG 口径（samtools 1.17 `depth` 默认
   排除 `0x400`）。合成量级见步骤 3 检查点 3。
2. **过滤表达式引用不存在的 INFO 标签**（§10.5.2）｜步骤 8/9：逐条分开写表达式；
   过滤后 `bcftools query -f '%FILTER\n' | sort | uniq -c` 按标签计数，0 就查；把
   标签逐条打印看缺失发生在哪些记录；构造缺失 fixture 复跑验证。默认
   `--missing-values-evaluate-as-failing=false` 下求值失败按整条表达式不命中处理、
   左侧为真则短路；不要用 `true` 开关当万能修复。步骤 9 脚本的预清点行（L37–43）
   是第一道免费警报。
3. **参考株自比变异数应接近 0**（§10.5.3）｜步骤 7：单独跑、同参考同索引同参数，
   数原始与 PASS；不为 0 按四步查（倍性 → 参考版本与三套索引 → `@RG`/比对参数 →
   重复区形态），顺序不颠倒。
4. **无覆盖与无变异在单样本 VCF 中不可区分**（§10.5.4）｜步骤 5/6：gVCF 参考块的
   `END`/`MIN_DP`/`GQ`（`MIN_DP` 是块内最小值）；callable 比例进报告；阴性结论写
   「在可判定区域内未检出变异」。

（§10.5.5 短读长 SV 盲区属博士层内容，本实验不做 SV，知道「未检出 ≠ 没有」即可。）

## 6. 思考题（指向教材 §10.7 习题，不给答案）

1. 合成布局：24 个独立分子、一个早期错误分子扩增成 8 份。写出总深度、表观重复率、
   去重前后 ALT 支持与质量代理的变化；某样本 `PERCENT_DUPLICATION` 明显高于同批时
   先查什么、为什么不能直接判「数据不可用」？（习题 4 → §10.4.2、§10.5.1）
2. 过滤命令写成 `"MQRankSum < -12.5"` 而低深度位点没有该标签：默认参数下这条规则的
   命运？给两条一分钟内判断它是否生效的命令。`QD < 2.0 || MQRankSum < -12.5` 哪种
   顺序会放走本应被拦下的位点，为什么？（习题 5 → §10.4.7、§10.5.2）
3. 单倍体细菌、自交纯系二倍体植物、同源四倍体作物的 `-ploidy` 各取多少？把单倍体
   样本按默认值跑，`GT/GQ/PL` 各会发生什么？（习题 6 → §10.4.4）
4. 用 §10.4.6 的表写出 `d=8` 与 `d=15` 时 `P(X≤2)`；为什么 `d=10` 的 5.469% 不能
   写成「真实漏检率」？携带 ALT 的读段更容易被丢弃时概率朝哪个方向变？（习题 7 →
   §10.4.6；模型只对二倍体杂合成立，Xoo 是单倍体）
5. CIX2779 自比明显不为 0：按 §10.5.3 顺序写出依次检查的四件事，每步看哪个文件
   或字段。（习题 9）

## 7. 提交物

与 `08_assessment/master/assignments/m03_resequencing_assignment.md` 规格一致：

- **打包**：`学号_姓名_m03.zip`（≤200 MB，**不打入 BAM 与原始 VCF**），解压后：

  ```
  学号_姓名_m03/
  ├── report.pdf                # 正文 ≤9 页（不含附图），六节齐全
  ├── scripts/{gatk_pipeline.sh, filter_sensitivity.sh}   # 你实际用的改后脚本
  ├── results/
  │   ├── flagstat_all.tsv      # 各样本比对率 / properly paired / singletons 汇总
  │   ├── dup_metrics_all.tsv   # 各样本 PERCENT_DUPLICATION 汇总
  │   ├── callable_summary.tsv  # 达标位点比例（无此表「无变异」不成立）
  │   ├── filter_counts.tsv     # 每条 filter 拦截计数（步骤 8 两个计数表合并整理）
  │   ├── sensitivity_table.tsv # 取步骤 9 sensitivity.tsv（8 行；宽/默认/严为读表口径）
  │   └── high_impact.tsv       # HIGH 影响清单（按位点去重）
  ├── figs/                     # 标题/轴/图例一律英文：fig1_qc_summary.png（比对率/
  │                             # 重复率/callable）、fig2_qd_mq_hist.png（QD/MQ 分布）、
  │                             # fig3_sensitivity.png（8 组对照）、fig4_allele_balance.png
  │                             # （单倍体无杂合位点：改画全部变异位点 ALT 深度占比直方图，
  │                             #  两峰贴 0 与 1；或出带文字标注的占位图。硬凑杂合位点才是错）
  └── env_snapshot.yml          # conda env export --no-builds
  ```

  `scripts/gatk_pipeline.sh` 即步骤 8 的个人副本（已同名，打包直接放入）。

- **报告六节**：① 比对与前处理（四数字全报，含 callable）② 调用策略（`-ploidy` 取值
  与理由、gVCF 联合、BQSR 交代）③ 过滤阈值与生效验证（六条逐条说拦什么＋拦截计数）
  ④ 阈值敏感性（选组与依据）⑤ 下游交付与注释（讲义 ⑥6.2.6 四步做了哪几步、哪几步
  刻意没做）⑥ 方法选择与结果可信度说明（≤1 页，四问，占 30%）。
- **评分口径**：流程完整性 40 / 结果正确性 30 / 方法说明 30；截止 m03 课后第 10 天 23:59，迟交与重交规则按作业卡 ⑤。
- **诚实红线**：报告里每个数字必须是自己跑出来的；预期区间不得写成实测；降级或
  未做的检查写明「未检查」及原因；fig4 一类对单倍体数据不适用的图，写清口径而不
  是硬凑杂合位点。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材（ch10 §10.4/§10.5/§10.7；ch07 §7.4/§7.5） | `textbook/chapters/ch10/manuscript.qmd`、`chapters/ch07/manuscript.qmd` |
| 讲义（⑤ 操作、⑥ 解读、⑦ 统计、⑨ 常见错误） | `02_lectures/master/topic03_resequencing/03_resequencing_lecture.md` |
| 课程脚本（只读；改动走个人副本）与合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `03_code/master/scripts/03_gatk_pipeline.sh`、`03_filter_sensitivity.sh`；`textbook/demos/ch10_pcr_duplicate_support.py`、`ch10_filter_thresholds.py`、`ch10_depth_het_dropout.py` |
| 数据说明与下载、登录号登记 | `06_data/master/README.md` §m03；`06_data/master/download_master.sh`；`06_data/accessions.tsv` L14/L34/L39–50 |
| 环境定义 | `07_envs/conda/env_master_variant.yml`（`ngs_ms_variant`）、`env_master_base.yml`（`ngs_ms_base`，fastp 0.23.4） |
| 作业规格 | `08_assessment/master/assignments/m03_resequencing_assignment.md` |
