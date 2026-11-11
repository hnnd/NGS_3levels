---
title: "实验指导 m05：转录调控与表观组（ChIP-seq / ATAC-seq / CUT&Tag）"
level: master
topic: m05
textbook: [ch15]
lecture: ../02_lectures/master/topic05_regulome/05_regulome_lecture.md
env: ngs_ms_transcriptome
---

# 实验指导 m05：转录调控与表观组（ChIP-seq / ATAC-seq / CUT&Tag）

> 上机时手边打开的这份文件。每一步回答四件事：这条命令在做什么、敲什么、看到什么算对、
> 看到什么说明错了。原理与判据在教材第 15 章（§15.4 概念、§15.5 失效条件），统计背景
> （泊松、BH、置换检验）在第 12 章；本指导只放操作与自查入口。检查点数字都带来源：
> 「预期（未实测）」是数据 README 或讲义经验口径，「合成算例」是 demos 固定种子演示（只对生成模型成立）。本课没有在课程集群真实跑完过 ATAC 全流程，标「集群未实测」的步骤按预期对待，真实结果以你自己的运行日志为入口。

## 0. 本实验对应什么

- **教材**：第 15 章 转录调控与表观组。本实验覆盖硕士层学习目标 LO15-03（对照、重复与缺对照失效机制）、LO15-04（narrow / broad / ATAC 三套 callpeak 参数）、LO15-05（FRiP 与 IDR 判读）、LO15-06（峰注释、motif 背景与交集置换检验）。
- **学时**：m05 共 4 学时（契约），本实验是实践环节；配套作业建议上机 5–7 小时（作业规格，HOMER 首次预解析很慢，提前起）。
- **环境**：主流程 `ngs_ms_transcriptome`（与 m04 共用），质控清洗 `ngs_ms_base`（fastp / MultiQC）。**两个环境不要叠加使用**——fastp 只在 `ngs_ms_base` 里。
- **作业**：`08_assessment/master/assignments/m05_regulome_assignment.md`，占课程总成绩 5%；「方法选择与结果可信度说明」占作业 30%。
- **计算纪律**：一切计算一律 `qsub`（登录节点只下载、建环境、编辑；建索引这类小计算也投递）。计算节点不通外网，任何联网步骤只能在登录节点做。

## 1. 实验前检查

- **前置模块**（先确认自测能过）：`l0_04_formats`（BED 0-based 半开 / GFF3 1-based 闭区间、FLAG 位）、`l0_05_qc`（fastp 边界）、`l0_06_stats` Q5/Q7/Q10（FDR、生物学 vs 技术重复、多重检验）、第 14 章差异表达（本实验步骤 3.5 的必需输入）。
- **激活并核验版本**（版本以 `07_envs/conda/env_master_transcriptome.yml` 为准）：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_transcriptome
  bowtie2 --version        # 期望 2.5.1（yml pin）
  samtools --version       # 期望 1.17（yml pin）
  bedtools --version       # 期望 2.31.0（yml pin）
  macs2 --version          # yml pin 2.2.9.1
  bamCoverage --version    # yml pin deepTools 3.5.5
  Rscript -e 'packageVersion("ChIPseeker")'   # yml pin 1.38.0
  idr --version            # yml 未 pin：记录实装版本写进报告
  ```

  这条命令在做什么：yml 已 pin bowtie2 / samtools / bedtools / MACS2 / deepTools / HOMER /
  ChIPseeker 的版本，但集群已建环境未必按新 yml 增量安装过——每条都是开箱第一闸，对不上先在
  登录节点补装。IDR 未 pin，把实装版本记进报告的「软件与版本」一节。
- **质控工具在另一个环境**（不要装错环境）：

  ```bash
  conda activate ngs_ms_base
  fastp --version          # 期望 0.23.4（yml pin）
  multiqc --version        # 期望 1.14（yml pin）
  ```
- **m04 差异表确认**：步骤 3.5 需要第 14 章交付的**差异表达结果全表**（`deseq2_results.tsv`，含 `padj` 为 NA 的行）；只留筛过的 `deg_sig.tsv` 不够（原因见步骤 3.5 检查点）。
- **预期**：版本号全部打印且与 yml 一致。
- **出错信号**：`command not found` / 版本对不上 → 环境没激活成功或装错环境；缺工具 → 登录节点补装，**不要**在计算节点装（无外网）。

## 2. 实验数据

贯穿数据是 `PRJDB36269`（水稻根系复氮时序）的 ATAC-seq 部分，与 m04 的 RNA-seq 出自**同一批样本**、一一对应：Z 基因型，对照（K）与复氮（N）各 3 个时间点（30/60/120 分钟），每条件每时间点 2 个生物学重复（A/B），共 12 个样本（算术 `2×3×2=12`；`06_data/master/README.md`，教材 15.1）。登录号全部已登记 `06_data/accessions.tsv`：

| 样本名 | 处理 | 时间 | 重复 | 登录号 |
|---|---|---|---|---|
| ZK0030A / ZK0030B | K 对照 | 30 min | A / B | `DRR737541` / `DRR737554` |
| ZK0060A / ZK0060B | K 对照 | 60 min | A / B | `DRR737542` / `DRR737555` |
| ZK0120A / ZK0120B | K 对照 | 120 min | A / B | `DRR737543` / `DRR737556` |
| ZN0030A / ZN0030B | N 复氮 | 30 min | A / B | `DRR737550` / `DRR737563` |
| ZN0060A / ZN0060B | N 复氮 | 60 min | A / B | `DRR737551` / `DRR737564` |
| ZN0120A / ZN0120B | N 复氮 | 120 min | A / B | `DRR737552` / `DRR737565` |

- **参考基因组**：`GCA_001433935`（水稻 IRGSP-1.0），12 条核染色体合计 373,795,655 bp（ENA assembly 记录；教材 15.1）。**注意：该参考没有线粒体/叶绿体序列**——细胞器读段在比对时以 unmapped 消失，「线粒体比例」在本课程数据上不可计算（教材 15.4.4）。参考 FASTA 与注释 GFF3 属课程备料：校内集群路径**由助教公布**（数据 README 未登记集群侧路径，勿编造）；校外自学从 NCBI 该装配页面下载（登录号在册）。
- **下载与降采样**（在**课程仓库根目录**运行）：

  ```bash
  cd <课程仓库路径>
  bash 06_data/master/download_master.sh --topic m05 --subsample 3000000 --run \
       --outdir /d3/scratch/${USER}/ngs/data
  ```

  产物落在 `/d3/scratch/${USER}/ngs/data/m05/`，命名形如 `DRR737541_1.sub3000000.fastq.gz`（`_1`/`_2` 双端；以下载脚本日志与 `ls` 实名为准）。ATAC 全集约 43 GB，降采样后 m04+m05 合计约 4 GB。**`--subsample 3000000` 取每个文件的前 300 万条读段，不是随机抽样**（ENA 字节范围前缀下载 + 截断），方法学里必须如实写明（教材 15.1）。下载脚本会校验 read 数并写 SHA256 manifest——看到「只取到 N 条 read」告警先重下该 run，不要带着残缺文件往下跑。
- **工作目录**：`/d3/scratch/${USER}/ngs/m05/`（下建 `clean/ ref/ run/ idr/ results/`）。数据放 scratch 不要放家目录；原始数据只软链不拷贝。

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出文件 / 检查点 / 出错信号。命令调用 `03_code/master/scripts/` 现有脚本与讲义 ⑤ 命令，不复制脚本全文；脚本名、参数名、输出文件名已逐个与现版源码核对（括注 Lx–y 为现版源码行号）。**在哪敲命令**：SSH 登录后是家目录；登录节点只做下载、编辑、建环境，其余一律 qsub。作业日志（`*.o<作业号>`）写在投递时所在目录（`#$ -cwd`），产出写在命令指定的输出目录，两者不是一回事。下面每个作业脚本都带 `set -euo pipefail`：任何一步失败作业立即退出，不让后续步骤拿残缺产物硬跑。
>
> **先声明三个不能绕过的缺口**（全程照此执行，不造假补齐）：① 差异峰没有生成脚本（两个课程脚本都不产生差异峰，DiffBind/csaw 不在课程环境），步骤 3.4 显式处理；② 现有步骤没有数值 TSSE、NRF/PBC 的实现（TSS 热图 ≠ TSSE），相应记录栏标「当前流程未产出」；③ 作业要求的「相关矩阵含 input、线粒体百分比」与主线 ATAC 无 input、参考无细胞器序列冲突，相应栏写「不适用 / 不可计算」，不虚构。

### 步骤 3.0：参考准备、数据验收与清洗（qsub）

- **目的**：把参考（FASTA+`.fai`+bowtie2 索引+GFF3）和 12 个样本的 clean reads 备齐，避免把 dry-run 输出或旧版本当成已执行。
- **命令**（前两条在登录节点；索引构建与 fastp 投递计算节点）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m05
  mkdir -p ref clean run idr results
  # ① 备料软链（路径由助教公布；校外换成自己下载的文件）
  #    校内上机：备料位置以助教现场公布/投屏为准（数据 README 未登记集群侧路径，勿编造）——
  #    找不到就问助教或看课程群公告，不要自己猜路径
  ln -s <助教公布的课程备料>/genome.fa ref/genome.fa
  ln -s <助教公布的课程备料>/annotation.gff3 ref/annotation.gff3
  ls -lL ref/                                  # 链接指向真实文件（失效链接 ls 标红）
  # ② 建 .fai + bowtie2 索引（小计算也投递；计算节点无外网）
  cat > 05_ref_index.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m05_refidx
  #$ -cwd
  #$ -j y
  #$ -pe smp 8
  set -euo pipefail
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_transcriptome
  cd /d3/scratch/${USER}/ngs/m05
  samtools faidx ref/genome.fa
  bowtie2-build --threads ${NSLOTS} ref/genome.fa ref/genome_idx   # 申请的 8 核全用上；不加 --threads 只跑 1 核
  EOF
  qsub 05_ref_index.job
  ```

  这条命令在做什么：`.fai` 是下游按染色体名过滤的依据；`bowtie2-build` 生成索引前缀 `ref/genome_idx`。**索引、比对、过滤、注释必须用同一套 FASTA/GFF3**（教材 15.5.6）。
- **fastp 清洗**（`ngs_ms_base` 环境；下载产物名与脚本期望的 clean 名不同，本步统一命名；清洗不在 m05 主脚本内，脚本从 clean reads 接手）。先建样本表（制表符分隔；样本名↔登录号对照见 §2，文件名以 `ls /d3/scratch/${USER}/ngs/data/m05/` 实名为准）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m05
  printf 'sample\tR1\tR2\n' > samples_raw.tsv
  for P in ZK0030A:DRR737541 ZK0030B:DRR737554 ZK0060A:DRR737542 ZK0060B:DRR737555 \
           ZK0120A:DRR737543 ZK0120B:DRR737556 ZN0030A:DRR737550 ZN0030B:DRR737563 \
           ZN0060A:DRR737551 ZN0060B:DRR737564 ZN0120A:DRR737552 ZN0120B:DRR737565; do
      S=${P%%:*}; D=${P##*:}
      printf '%s\t/d3/scratch/%s/ngs/data/m05/%s_1.sub3000000.fastq.gz\t/d3/scratch/%s/ngs/data/m05/%s_2.sub3000000.fastq.gz\n' \
          "${S}" "${USER}" "${D}" "${USER}" "${D}" >> samples_raw.tsv
  done
  wc -l samples_raw.tsv        # 13（表头 + 12 行）
  cat > 05_fastp.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m05_fastp
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  set -euo pipefail
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_base
  cd /d3/scratch/${USER}/ngs/m05
  while IFS=$'\t' read -r s r1 r2; do
      [[ -z "${s}" || "${s}" == "sample" ]] && continue
      fastp -i "${r1}" -I "${r2}" -o "clean/${s}_R1.clean.fq.gz" -O "clean/${s}_R2.clean.fq.gz" \
            --detect_adapter_for_pe --cut_tail --cut_mean_quality 20 --length_required 50 \
            -w 4 -h "qc/${s}.html" -j "qc/${s}.json"
  done < samples_raw.tsv
  # 逐样本对账：fastp 任一样本失败会由 set -e 立即退出；这里再数一遍成对产物，
  # 缺一个都不让 MultiQC 拿缺样本的结果兜底
  n_clean=$(find clean -name '*.clean.fq.gz' | wc -l)
  [[ "${n_clean}" -eq 24 ]] || { echo "clean 文件 ${n_clean}/24，有样本清洗失败或产出缺失，先修再跑"; exit 1; }
  multiqc qc/ -o qc/multiqc
  EOF
  mkdir -p qc && qsub 05_fastp.job
  ```

  这条命令在做什么：fastp 去接头与低质量区，产物命名成 `clean/<样本>_R1.clean.fq.gz`——正是 `05_peak_calling.sh` 的默认输入名（L44–45），步骤 3.1 用 `-v` 传 `FQ_DIR` 后脚本按默认命名自取，不需要也不应该再传原始 fastq 路径。
- **产出**：`ref/genome.fa.fai`、`ref/genome_idx.*`；`clean/` 下 12 对清洗后 fastq；`qc/` 下每样本 html+json 与 multiqc 汇总。
- **检查点**：
  1. `wc -l ref/genome.fa.fai` = 12（12 条核染色体；ENA 记录，教材 15.4.4）；`ls ref/genome_idx.*` 索引文件齐全。
  2. `ls clean/*.clean.fq.gz | wc -l` = 24（12 样本 × 双端）；`zcat clean/ZK0030A_R1.clean.fq.gz | wc -l` ÷4 = 清洗后读段数，**只作记录不作判据**：它一定 ≤ 下载目标 300 万/端（fastp 过滤会丢读段，「对不上 300 万」不是错误）；组成异常先怀疑下载截断（下载脚本告警优先处理）。
  3. 12 个样本与 §2 登记册一一对应（对账用样本数，不是 QC 实测）。
- **出错信号**：只有 dry-run 输出而没有 FASTQ（忘了 `--run`）；下载脚本告警 read 数不足 → 重下该 run，不进分析（教材 15.6；前缀截断的教训）；`fastp: command not found` → 你在 `ngs_ms_transcriptome` 里，切回 `ngs_ms_base`。

### 步骤 3.1：比对 → 清洗 → call peak → FRiP → bigwig（`qsub 05_peak_calling.sh`）

- **目的**：每个 ATAC 样本得到可追踪的 BAM、峰表、FRiP 和信号轨道（教材 15.6 前五个环节）。
- **命令**（每样本一个作业；**必须显式 `MODE=atac`**，脚本默认是 narrow，L48）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m05
  # 只从样本表取样本名；R1/R2 一律不传——脚本默认从 FQ_DIR 取 clean reads（L44–45）。
  # 若把 samples_raw.tsv 里的原始 fastq 路径传进去，fastp 清洗就白跑了。
  tail -n +2 samples_raw.tsv | cut -f1 | while read -r S; do
      VARS="SAMPLE=${S},MODE=atac,FQ_DIR=/d3/scratch/${USER}/ngs/m05/clean,PROJ_DIR=/d3/scratch/${USER}/ngs/m05/run/${S},GENOME_FA=/d3/scratch/${USER}/ngs/m05/ref/genome.fa,BT2_IDX=/d3/scratch/${USER}/ngs/m05/ref/genome_idx"
      qsub -v "${VARS}" <课程仓库路径>/03_code/master/scripts/05_peak_calling.sh
  done
  qstat -u ${USER}          # qw 排队 / r 运行 / Eqw 报错
  ```

  这条命令在做什么（参数逐个与现版源码核对，行号对现版）：**SGE 作业默认不继承提交终端的环境变量**——`SAMPLE=... qsub` 在 qsub 前赋值是传不进作业的（作业里 SAMPLE 未设，脚本 L43 的 `:?` 直接退出；MODE 缺省回落 narrow，L48）。必须用 `qsub -v 变量=值,...` 白名单显式传进作业（不要用 `-V` 全传，会把登录节点的杂散变量带进作业）。`bowtie2 --very-sensitive -X 2000`（L80）；`samtools markdup -r -s`（L94）去 PCR 重复；`samtools view -q 30 -F 1804`（L110，1804 = 4+8+256+512+1024，教材 15.3 手算）；`MT_PATTERN` 过滤（L61、L108）在本课程参考上是空操作，脚本会打印提示（L103–106）；ATAC 分支 `-f BAMPE -q 0.05 --keep-dup all`（L156–159，BAMPE 强制 nomodel，双端不需要也不应用 `--shift/--extsize`，那是单端口径）；FRiP 并追加 `qc/frip_summary.tsv`（L171–176）；`bamCoverage --binSize 10 --normalizeUsing RPGC --effectiveGenomeSize ${EGS}`（L184–186）。`GSIZE=3.0e8` / `EGS=300000000` 为现脚本默认（L55–56）并有同数校验（L57–60，不同数即退出）。**每样本独立 `PROJ_DIR`** 是故意的：脚本在 L176 追加共享 `frip_summary.tsv`，12 个作业并发写同一文件会互相踩踏。跑完后合并对账：

  ```bash
  # frip_summary.tsv 无表头、每文件只有一行：直接拼接。绝不能用「跳过重文件表头」的
  # awk（FNR==1 && NR!=1{next}）——它没有表头可跳，会把第 2–12 个文件唯一的行全删光
  cat run/*/qc/frip_summary.tsv > qc/frip_summary_all.tsv
  wc -l qc/frip_summary_all.tsv        # 应为 12（每样本一行：SAMPLE/MODE/TOTAL/NPEAK/FRiP）
  cut -f1 qc/frip_summary_all.tsv | sort | uniq -c   # 12 个样本各出现 1 次——对账，不许丢行
  ```
- **产出**（每样本在 `run/<S>/` 下）：`align/<S>.{raw,dedup,clean}.bam`（+`.bai`）；`logs/<S>.{bowtie2,macs2}.log`；`qc/<S>.{markdup,idxstats,fraglen}.txt`；`peaks/<S>_peaks.narrowPeak`（10 列，含 summit）与 `peaks/<S>_peaks.xls`；`bigwig/<S>.bw`；合并后 `qc/frip_summary_all.tsv`。
- **检查点**：
  1. clean BAM 非空、染色体名与 `.fai` / `@SQ` 逐字一致（`samtools view -H run/<S>/align/<S>.clean.bam | grep '^@SQ'` 对 `cut -f1 ref/genome.fa.fai`）。
  2. FRiP 记录实测值；外部参考线：ENCODE4 的 ATAC **>0.2 可接受、>0.3 为优**（教材 15.4.4），**只作参考，不单独判样本通过**。
  3. 片段长度看 `<100 / ~200 / ~400 bp` 阶梯。作业全部结束后在登录节点画直方图（提交物 fig1 的来源，先 `mkdir -p figs`）：`Rscript -e 'd <- read.table("run/ZK0030A/qc/ZK0030A.fraglen.txt"); png("figs/fig1_fraglen.png", width=800, height=600); hist(d$V1, breaks=100, xlim=c(0,800), main="Fragment Length", xlab="Fragment Length (bp)"); dev.off()'`（把 ZK0030A 换成你的样本名；图题/坐标轴按课程图表规则用英文，中文解释写在报告正文）。合成对照：在课程仓库根目录运行 `PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch15_atac_fragment_model.py --selftest`（阶梯 603/310/151 vs 消化过度单峰 931；数字只对生成模型成立）。
  4. 峰数与中位宽**只记录本样本值与分布，不设合格线**（数据 README 与讲义的经验区间都未经课程集群实测，一律不作判据）；异常多/异常窄按下面的出错信号走 IGV 检查（§15.5.1）。
  5. `-g` / `EGS` 抄进 §4：3.0e8 落在教材手算区间 `2.6×10⁸–3.4×10⁸` 内（`0.7/0.9 × 373,795,655`，教材 15.4.3）；真实可比对比例未实测（unverified）。
  6. `BLACKLIST` 默认空（L41）、留空即跳过过滤（L112–116）：课程仓库没有现成水稻清单，报告写「未过滤」，不得声称已过滤（教材 15.5.2）。
- **出错信号**：
  - MACS2 日志出现建模警告 / `No enough pairs to build model`（措辞随版本变）→ ATAC 模型口径错了，检查是否显式 `MODE=atac` → 教材 §15.5.1。
  - clean BAM 为空或缺染色体 → 参考名不匹配，§15.5.6。
  - `GSIZE` 与 `EGS` 不同数 → 脚本在 L57–60 直接退出，按报错改成同数。
  - `qstat` 恒 `Eqw` → `qstat -j <ID> | grep -A5 error` 看资源/路径错误。

### 步骤 3.2：TSS 热图与重复相关（脚本外手工步骤，无对应 03_code 实现）

- **目的**：从 bigwig 观察 TSS 结构和重复间秩相关（教材 15.6「TSS 富集与重复相关」一行，标注**脚本未内置**，脚本收尾只 echo 提示，L190–191）。
- **命令**（讲义 ⑤ 步骤 3 参数，个人 qsub 包装；**主线 ATAC 删除 `input.bw`**，不得为交作业虚构 input）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m05
  cat > 05_tss_cor.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m05_tss
  #$ -cwd
  #$ -j y
  #$ -pe smp 8
  set -euo pipefail
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_transcriptome
  cd /d3/scratch/${USER}/ngs/m05
  # genes.bed：GFF3 是 1-based 闭区间，转 BED 时 start 必须减 1（教材 15.3）；也是计算，放进作业做
  awk 'BEGIN{OFS="\t"} $3=="gene" {print $1, $4-1, $5, $9, ".", $7}' ref/annotation.gff3 \
    | sort -k1,1 -k2,2n > ref/genes.bed
  BWS=$(ls run/*/bigwig/*.bw | tr '\n' ' ')
  computeMatrix reference-point -S ${BWS} -R ref/genes.bed --referencePoint TSS \
      -b 3000 -a 3000 --skipZeros -o results/matrix.gz -p ${NSLOTS}
  plotHeatmap -m results/matrix.gz -o results/tss_heatmap.png --colorMap Blues --refPointLabel TSS
  multiBigwigSummary bins -b ${BWS} -o results/summary.npz -p ${NSLOTS}
  plotCorrelation -in results/summary.npz -c spearman -p heatmap --plotNumbers \
      -o results/cor_heatmap.png
  EOF
  qsub 05_tss_cor.job
  ```

  用 Spearman 而非 Pearson：分箱信号右偏且有极端值，秩相关更稳健（教材 15.4.2）。deepTools 按扩展名出图：`-o` 直接给 `.png` 就是 PNG（fig2/fig3 的来源），不用事后转换。
- **产出**：`results/{matrix.gz, tss_heatmap.png, summary.npz, cor_heatmap.png}`。
- **检查点**：
  1. 热图有 TSS 中心深色纵带、两侧衰减为**定性**判据；整张图均匀无结构 → 先查参考注释、bigwig 与样本质量，再谈生物学（教材 15.4.4 的合读顺序）。
  2. Spearman 只看**组内 vs 组间和异常样本的相对关系**（同条件重复应相对更近），不设 0.8/0.6 通用线（教材 15.4.2：它是补充诊断，不替代四项 QC 或 IDR）。
  3. 若某样本与所有其他样本都远 → 按 15.4.4 固定顺序回查该样本的比对率/重复率/FRiP。
- **阻塞（写在报告里，不预填）**：这些命令**不输出数值 TSSE**；TSS 热图不能写成 TSSE 分数。NRF/PBC 也未由现脚本计算（教材 15.4.4 的定义与阈值适用域先写明，课程 3M 降采样数据不直接套深度依赖阈值）。
- **出错信号**：深色带偏离 TSS 中心 → 先查 bigwig 与注释坐标系，不要把 SE 的 shift/extsize 机制套到 PE（教材 15.4.3/15.5.6）。

### 步骤 3.3：两个生物学重复的 IDR 与 ENCODE 两比率（脚本外手工步骤）

- **目的**：评价可重复性，不以单样本峰数替代（教材 15.4.2）。设计是 6 个「条件×时间点」对，每对 A/B 两个生物学重复各跑一次 IDR，并补池化伪重复与各自拆半自跑，算 rescue ratio 与 self-consistency ratio（教材 15.4.2 口径，报告写清用的是哪一版定义）。
- **命令**（讲义 ⑤ 步骤 4 参数；**ATAC 不传 `-c input.bam`**——主线无 input；ChIP/CUT&Tag 才传对应 input）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m05
  cat > 05_idr.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m05_idr
  #$ -cwd
  #$ -j y
  #$ -pe smp 8
  set -euo pipefail
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_transcriptome
  cd /d3/scratch/${USER}/ngs/m05
  # 拆半伪重复通用流程：$1=clean BAM，$2=标签；按 qname 交替拆两个不相交半库
  # （同一对读段同一 qname，一定进同一半），各自宽松 call peak 后互跑 IDR，
  # stdout 打印第 5 列 ≥540 的通过数
  pseudo_idr() {
      local BAM=$1 TAG=$2 D=idr/${PAIR}
      samtools sort -n -o ${D}/${TAG}.ns.bam "${BAM}"
      samtools view ${D}/${TAG}.ns.bam | awk -v d="${D}/${TAG}" '
          $1 != prev { flip = 1 - flip; prev = $1 }
          { print > (flip ? d ".h1.sam" : d ".h2.sam") }'
      samtools view -H ${D}/${TAG}.ns.bam > ${D}/${TAG}.hdr
      for H in h1 h2; do
          cat ${D}/${TAG}.hdr ${D}/${TAG}.${H}.sam | samtools sort -o ${D}/${TAG}.${H}.bam -
          macs2 callpeak -t ${D}/${TAG}.${H}.bam -f BAMPE -g 3.0e8 \
              -n ${TAG}_${H} --outdir ${D} -p 1e-3 --keep-dup all
          sort -k8,8nr ${D}/${TAG}_${H}_peaks.narrowPeak \
              > ${D}/${TAG}_${H}.sorted.narrowPeak
      done
      idr --samples ${D}/${TAG}_h1.sorted.narrowPeak ${D}/${TAG}_h2.sorted.narrowPeak \
          --input-file-type narrowPeak --rank p.value \
          --output-file ${D}/idr_${TAG}_out.txt --plot --idr-threshold 0.05
      awk '$5 >= 540{c++} END{print c+0}' ${D}/idr_${TAG}_out.txt
  }
  for PAIR in ZK0030 ZK0060 ZK0120 ZN0030 ZN0060 ZN0120; do
      A=${PAIR}A; B=${PAIR}B
      mkdir -p idr/${PAIR}
      for S in ${A} ${B}; do
          macs2 callpeak -t run/${S}/align/${S}.clean.bam -f BAMPE -g 3.0e8 \
              -n ${S}_loose --outdir idr/${PAIR} -p 1e-3 --keep-dup all
          sort -k8,8nr idr/${PAIR}/${S}_loose_peaks.narrowPeak \
              > idr/${PAIR}/${S}.sorted.narrowPeak
      done
      idr --samples idr/${PAIR}/${A}.sorted.narrowPeak idr/${PAIR}/${B}.sorted.narrowPeak \
          --input-file-type narrowPeak --rank p.value \
          --output-file idr/${PAIR}/idr_out.txt --plot --idr-threshold 0.05
      awk '$5 >= 540' idr/${PAIR}/idr_out.txt > idr/${PAIR}/reproducible_peaks.bed
      NT=$(wc -l < idr/${PAIR}/reproducible_peaks.bed)
      # ---- ENCODE 两比率（教材 15.4.2 完整口径）----
      # rescue：真实重复通过数 NT 与池化伪重复通过数 Np 的大者÷小者；
      # self-consistency：两个真实重复各自拆半自跑的通过数 N1、N2 的大者÷小者；均要求 < 2
      samtools merge -f idr/${PAIR}/pooled.bam \
          run/${A}/align/${A}.clean.bam run/${B}/align/${B}.clean.bam
      NP=$(pseudo_idr idr/${PAIR}/pooled.bam ${PAIR}_pooled)
      N1=$(pseudo_idr run/${A}/align/${A}.clean.bam ${A}_self)
      N2=$(pseudo_idr run/${B}/align/${B}.clean.bam ${B}_self)
      RESCUE=$(awk -v a="${NT}" -v b="${NP}" 'BEGIN{m=(a>b)?a:b; n=(a>b)?b:a; printf "%.3f", m/n}')
      SELFCON=$(awk -v a="${N1}" -v b="${N2}" 'BEGIN{m=(a>b)?a:b; n=(a>b)?b:a; printf "%.3f", m/n}')
      echo "${PAIR} Nt=${NT} Np=${NP} N1=${N1} N2=${N2} rescue_ratio=${RESCUE} self_consistency=${SELFCON}"
  done
  EOF
  qsub 05_idr.job
  ```

  这条命令在做什么：每重复单独以宽松阈值 `-p 1e-3` call peak（IDR 靠排名靠后的噪声估计混合模型的噪声成分，只喂高置信峰会让估计不稳，教材 15.4.2）；`sort -k8,8nr` 按第 8 列 `−log10(p)` 降序排名；`idr` 用 `--rank p.value`；第 5 列是 scaled IDR，`$5 >= 540` 对应 IDR 0.05（`int(−125·log₂(0.05)) = 540`，教材 15.4.2 手算）。`--plot` 生成的 png 就是作业 fig4 的来源。**IDR 输入必须是未压缩的 narrowPeak**：若你中途把文件压成 `.gz`，先 `gunzip -c` 再跑（讲义 ⑨ 错误 5 的 `UnicodeDecodeError: ... 0x8b`）。注意 idr 默认只输出两个输入都支持的合并峰（源码 iter_merge_grpd_intervals：任一侧无峰即整区跳过），所以**两半各自的真实通过数不能用输出列拆开数**——N1/N2 必须像上面这样对 A、B 各自再拆半自跑一次 IDR。池化（merge）保证伪重复来自同一批读段，按 qname 交替拆分保证读段对不被拆开。【集群未实测】与全流程一致，跑不通先看作业日志，不要拿单样本峰数顶替。
- **产出**：每对 `idr/<条件时间>/` 下：`*_loose_peaks.narrowPeak`、`*.sorted.narrowPeak`、`idr_out.txt`、`idr_out.txt.png`（idr --plot 输出）、`reproducible_peaks.bed`；比率侧 `pooled.bam`、`*.ns.bam`、`*.h1/h2.*`、`idr_<标签>_out.txt(.png)`；作业日志每对打印一行 `Nt=… Np=… N1=… N2=… rescue_ratio=… self_consistency=…`。
- **检查点**：
  1. 每对 `reproducible_peaks.bed` 行数 > 0；第 5 列 ≥540 为筛选口径（手算来源如上）。
  2. 一致性判据按教材 15.4.2 的完整口径报 **rescue ratio（max(真实重复通过数, 池化伪重复通过数) ÷ min，即 NT 与 Np 之比）与 self-consistency ratio（两个重复各自拆半自跑通过数 N1、N2 之比）均 <2**（ENCODE 框架），不写旧式「各自峰数/可重复峰数 > 2」简化式；作业日志里每对打印的 Nt/Np/N1/N2 与两个比率抄进 §4 记录表，比率由你的运行产生、不预填。
  3. `--plot` 的 rank–rank 图：高显著区两重复排名一致、低显著区散开为正常；整面均匀弥散 → 先查哪个重复失败（回 3.1 对该样本的 QC），**不换取交集凑数**。
- **出错信号**：散点弥散换交集 → 教材 §15.5.2 口径错误；用技术重复冒充生物学重复会让不可重复发现率偏低、scaled IDR 偏高，「通过得漂亮」检验的是同一管测两次（教材 15.4.2）。

### 步骤 3.4：差异峰上游闸门（当前无实现，必须显式报告）

- **目的**：若报告声称「差异峰 ∩ 差异基因」，先确认差异峰确实由条件比较模型产生。
- **现状**：`05_peak_calling.sh` 只按样本 call peak；`05_peak_annotation.R` 只注释输入峰并与差异基因求交；二者都不生成差异峰表。DiffBind / csaw 不在课程环境（教材 15.4.5）。
- **本指导的可写流程**：有教师提供的差异峰表时，记录一致峰集、区间计数、设计式、样本分组、大小因子与 FDR 后才进入联合分析；没有时只能把产物准确命名为**「可重复峰关联基因 ∩ 差异基因」**，不得改称差异峰（教材 15.4.5/15.4.7）。
- **检查点**：方法、输入矩阵、分组与结果文件可互相追溯；不得仅检查文件名叫 `diff_peaks`。
- **出错信号**：把单样本可重复峰直接当差异峰 → 结论层级错误（§15.4.5/15.4.7）。此项是课程侧待裁决缺口，不由学生自行缩小需求或用假文件补齐。

### 步骤 3.5：ChIPseeker 注释与交集置换（`qsub 05_peak_annotation.R` 个人副本）

- **目的**：得到「最近基因」候选清单、与 m04 差异基因的交集及其基因标签置换零分布（教材 15.4.5、15.4.7）。
- **命令**（按「cp 个人副本 → 改指定行 → grep 确认 → qsub 副本」走）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m05
  # ① 个人副本：把读入函数改成 read.delim（m04 交付是制表符分隔的 .tsv，
  #    脚本默认 read.csv 读 .tsv 会读成一整列、随后在基因列检查处 stop）
  cp <课程仓库路径>/03_code/master/scripts/05_peak_annotation.R 05_peak_annotation_mine.R
  #   用编辑器把 L108   deg_raw <- read.csv(opt$deg, stringsAsFactors = FALSE)
  #            改为      deg_raw <- read.delim(opt$deg, stringsAsFactors = FALSE)
  grep -n 'read.delim' 05_peak_annotation_mine.R     # 确认改到位再投递
  # ② 投递（--deg 传 m04 的差异表达结果全表，不要只传筛过的 deg_sig.tsv）
  #    合并 6 对可重复峰也是计算，一并放进作业里做
  cat > 05_anno.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m05_anno
  #$ -cwd
  #$ -j y
  #$ -pe smp 4
  set -euo pipefail
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_transcriptome
  cd /d3/scratch/${USER}/ngs/m05
  # 合并 6 对可重复峰为一份输入（注明合并方式；这是对 IDR 产物的整理，不是差异峰）
  cat idr/*/reproducible_peaks.bed | sort -k1,1 -k2,2n | bedtools merge \
      > results/reproducible_peaks_all.bed
  echo "reproducible_peaks_all.bed 行数: $(wc -l < results/reproducible_peaks_all.bed)"
  Rscript 05_peak_annotation_mine.R \
      --peak=results/reproducible_peaks_all.bed \
      --gff=ref/annotation.gff3 \
      --deg=<m04 工作目录>/deseq2_results.tsv \
      --outdir=results/anno --tss_up=-3000 --tss_down=3000 \
      --padj=0.05 --lfc=1 --nperm=1000
  EOF
  qsub 05_anno.job
  ```

  这条命令在做什么（行号对现版源码）：TxDb 必须由自己的 GFF3 现场构建（L59）；染色体命名自动统一与共同染色体检查（L62–72），共同染色体为 0 直接 `stop`；`annotatePeak(tssRegion=c(-3000,3000))`（L78–80）只定义「TSS 上下游 3 kb 算不算启动子」，不定义任何调控关系；intergenic > 0.95 红灯自检（L84–90）；可检测基因全集取 `padj` 非 NA 的行（L113–114），交集与置换都在全集内进行（L120–122）；置换 `nperm` 次抽样求交（L134–138），经验 p = `(1 + #{null≥obs}) / (n_perm+1)`（L140，分母 1001）；`set.seed(20260829)` 可复现（L26）。**为什么必须传全表**：只传 `deg_sig.tsv`（只有显著行）时，`padj` 非 NA 的行就是差异基因本身——可检测基因全集退化成差异基因集，置换零分布失效（经验 p 恒偏大）。全表 = m04 的 `results()` 输出（含 `padj` 为 NA 的行）；脚本 L109 自动找基因 ID 列（`gene_id`/`gene`/`GeneID`/`X` 之一），另需 `log2FoldChange`、`padj` 两列。备选改法：不动脚本，把 m04 的 tsv 在 R 里读入后 `write.csv()` 另存真 CSV 再传默认脚本。
- **产出**（`results/anno/`）：`peak_annotation.csv`（注释全表）、`peak_annotation_plots.pdf`（饼图 + TSS 距离图）、`peak_nearest_genes.txt`（最近基因清单）、`overlap_permutation_test.csv`（`observed`/`null_median`/`null_mean`/`null_q95`/`fold_over_median`/`n_permutations`/`empirical_p`）、`diffpeak_x_deg.csv`（交集基因 + `log2FoldChange`/`padj`/`rna_direction`）、`overlap_permutation.pdf`。两个 CSV 分工不同：前者是「交集是否大于随机」的计算结果，后者是拿去对读方向表的名单，名字别写反（教材 15.4.7）。
- **检查点**：
  1. 日志先打印 `peak 数 = N；共同染色体 = M`——M 是**峰表与注释共有的染色体数**（脚本自动计算，不是参考的染色体总数）：M = 0 脚本直接 stop（→ §15.5.6）；M 与 12 条核染色体明显对不上时，先查染色体命名（`chr1` vs `1`）与物种注释，再谈生物学。
  2. intergenic 比例记录；>95% 是命名/物种不匹配的红灯，不是生物学发现（§15.5.6）。
  3. 置换结果的 `null_median` 与你自己的手算设例对照：教材设例 `512×1843/12400=76.10`、SD 7.88、观察 137 的 z=7.73（**设例**；脚本在真实表上产生它自己的零分布中位数，`set.seed(20260829)`、`nperm=1000`，不要拿手算中位数对脚本输出）。
  4. 真实 `observed`/`null_median`/`empirical_p` 由运行产生，不预填。
- **出错信号**：共同染色体为 0 → stop，查染色体命名（`chr1` vs `1`）与物种注释，§15.5.6；`差异表达表里找不到基因 ID 列` → 传成了错误文件或分隔符不对；把输出表的最近基因写成靶基因 → §15.5.3（注释表是「几何关联，未经互作验证」的候选清单）。

### 步骤 3.6：HOMER motif（脚本外手工步骤）

- **目的**：在序列层检查候选 motif，并验证背景而非只读极小 p 值（教材 15.4.6）。
- **命令**（用 MACS2 已产出的 `_summits.bed`，取可重复峰内的 summit；个人 qsub 包装。**依赖步骤 3.5 的作业**：要用它合并出的 `results/reproducible_peaks_all.bed`，等 3.5 跑完再投）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m05
  mkdir -p /d3/scratch/${USER}/homer_preparsed     # 个人可写目录，先建（公共参考目录只读）
  cat > 05_homer.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m05_homer
  #$ -cwd
  #$ -j y
  #$ -pe smp 16
  set -euo pipefail
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_transcriptome
  cd /d3/scratch/${USER}/ngs/m05
  # 汇总全部 12 个样本的 summit 再与可重复峰求交——只取单个样本的 summit 会把
  # 只在其他条件/重复里开放的可重复峰的峰顶整个丢掉
  cat idr/*/*_loose_summits.bed | sort -k1,1 -k2,2n > results/all_loose_summits.bed
  bedtools intersect -a results/all_loose_summits.bed -b results/reproducible_peaks_all.bed -u \
      > results/reproducible_summits.bed
  echo "reproducible_summits.bed 行数: $(wc -l < results/reproducible_summits.bed)"
  findMotifsGenome.pl results/reproducible_summits.bed ref/genome.fa results/homer_out \
      -size 200 -p ${NSLOTS} -mask -preparsedDir /d3/scratch/${USER}/homer_preparsed
  EOF
  qsub 05_homer.job
  ```

  这条命令在做什么：`-size 200` 取 summit ±100 bp（转录因子结合位点集中在峰顶附近，不要用整个峰）；`-mask` 屏蔽重复序列；`-preparsedDir` 指向自己的可写目录；直接把 FASTA 路径传给程序现场预解析（conda 装的 HOMER 不带基因组数据，本课程是非模式物种，**不要下载 HOMER 预置基因组**）。首次预解析耗时几十分钟量级，作业时限留够（作业规格原话）。
- **产出**：`results/all_loose_summits.bed`、`results/reproducible_summits.bed`、`results/homer_out/` 下 `knownResults.html`（读 `P-value`、`% of Targets`、`% of Background` 三列）、`knownMotifs.html`、`homerMotifs.all.motifs`（de novo）、预解析目录。
- **检查点**：
  1. 报告写明背景生成方式（HOMER 默认生成 GC 与长度匹配背景）、`-mask`、summit 取窗与重复间一致性（教材 15.4.6 的三问）。要比较重复间一致性，可对各重复的 summits 分别跑 HOMER 再对比 Top 家族是否一致（本课不强制，属加分项）。
  2. Top motif 的 Targets 与 Background 只差 1–2 倍时**不能单独判真假**：换一套 GC/长度匹配背景重跑，看富集还在不在。合成对照见 3.7 表最后一行（同一 GC-rich 诱饵序列，换背景后从假富集 5.83× 变成被正确放过的 0.93×；数字只对生成模型成立）。
  3. de novo 的极小 p 值不按常规显著性水平读（搜索空间未校正，量级不可跨运行比较）。
- **出错信号**：`Genome hg38 not found ...` → 直接传 FASTA，别装预置基因组；`Could not open .../preparsed/ for writing` → `-preparsedDir` 指个人目录；Top 全是 GC-rich 低复杂度序列 → §15.5.4 的三问核查，不凭「GC-rich」本身判真假。

### 步骤 3.7：合成演示四连（无集群依赖，课堂现跑）

- **目的**：3.1–3.6 的四类事故都有「不报错、结果看起来正常」的共同特征；四个固定种子的合成演示给出可复现的量化证据（数字只对各自生成模型成立，不得当 PRJDB36269 的结果）。
- **命令**（在**课程仓库根目录**运行；课程站暂未发布 textbook/，demos 从课程仓库获取）：

  ```bash
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch15_local_lambda.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch15_atac_fragment_model.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch15_motif_gc_background.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch15_nearest_gene_mismatch.py --selftest
  ```
- **产出**：四个 `SELFTEST PASS`（rc=0；以你自己的运行为准——FAIL 说明环境或文件被改动，停下核对）。
- **检查点（关键数字对照，来源 = 对应 demos --selftest，合成算例）**：

  | 机制 | 关键数字 |
  |---|---|
  | 局部 λ 取 max 的意义（§15.4.3） | 共享宽偏差域内 λBG-only 假阳性 255 → 三尺度 max 为 0 |
  | 无对照自估失效（§15.5.2） | 假阳性 2→218、宽域召回 0.871→0.003、伪 FRiP 0.0665→0.0160；`--nolambda` 管线 288 个假峰伪 FRiP 反而最高 0.0789 |
  | ATAC 无双峰结构（§15.5.1） | 互相关峰 ChIP 208 bp vs ATAC 9 bp；强按 d=200 峰中心偏 100 bp（设例） |
  | 最近基因错配（§15.5.3） | 总错配 66.5%；60–150 kb 分层 92.1%；紧凑基因组 95.5%；≤10 kb 截断压不下错配 |
  | motif 背景失配（§15.5.4） | 同一 GC-rich 诱饵：随机背景假富集 5.83×（p=4.12×10⁻³³）→ 匹配背景被正确放过 0.93×（p=0.806） |
- **出错信号**：任一脚本 `FAIL` → 环境或文件被改动，STOP 并核对（四个脚本只依赖 numpy/scipy，rc=0 即通过）。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果；「自查判据」列给来源口径，填表时对照。线粒体%、input 相关、数值 TSSE/NRF/PBC 三栏的口径见 §3 开头「三个不能绕过的缺口」。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 3.0 | 每样本清洗后读段数 | 条 | | 3,000,000 条/端是**下载目标**（前缀非随机；下载脚本校验）；清洗后因 fastp 过滤只会更少，只记录实际值、不作判据 |
| 3.0 | `.fai` 染色体数 | 条 | | 12（ENA 记录，教材 15.4.4） |
| 3.1 | 每样本比对率 / 重复率 | % | | 只记录 + 组内互查；不设合格线（讲义经验阈值未实测，教材 15.4.4） |
| 3.1 | clean BAM 读段数 | 条 | | 非空；染色体名与 `.fai`/`@SQ` 一致（§15.5.6） |
| 3.1 | FRiP | 0–1 | | ENCODE4 参考 >0.2 可接受、>0.3 为优（教材 15.4.4，非单独通过线） |
| 3.1 | 峰数 / 峰宽中位数 | 个 / bp | | 只记录本样本值与分布，不设合格线（README 与讲义的经验区间均未实测，不作判据；算法见 §7 peaks_summary.tsv） |
| 3.1 | blacklist 状态 | 文字 | | 本课留空 = 「未过滤」，照实写（§15.5.2） |
| 3.2 | TSS 热图结构 | 定性 | | 有/无 TSS 富集纵带；**数值 TSSE 本流程未产出**，不得从热图反推 |
| 3.2 | Spearman 组内 vs 组间 | 图 | | 组内相对更近即可；不设 0.8/0.6（教材 15.4.2） |
| 3.3 | 每对 IDR 通过峰数 / loose 峰数；rescue_ratio；self_consistency | 个 / 比率 | | 第 5 列 ≥540（教材手算）；rescue = max(Nt,Np)÷min(Nt,Np)、self-consistency = max(N1,N2)÷min(N1,N2)，均 <2（教材 15.4.2；定义与算法见步骤 3.3，比率由运行产生、不预填） |
| 3.5 | intergenic 比例 | % | | >95% 先查命名/物种（§15.5.6） |
| 3.5 | 置换 observed / null_median / empirical_p | 个/个/p | | p 由运行产生；手算设例 E=76.10、SD=7.88（设例，教材 15.4.7） |
| 3.6 | Top motif Targets vs Background | % / % | | 差 1–2 倍 → 三问核查：背景生成、`-mask`、换匹配背景重跑（§15.5.4） |
| 3.x | 线粒体% | — | | 本课程参考无细胞器序列：**不可计算**（教材 15.4.4） |
| 3.x | input 相关矩阵列 | — | | ATAC 无 input：**不适用**，不得虚构 input.bw（教材 15.4.2） |
| 3.x | NRF / PBC1 / PBC2 | — | | 当前流程未产出；阈值须先写明定义与深度（教材 15.4.4） |

## 5. 失效条件对照（教材 §15.5，本实验里在哪一步、看什么能察觉）

1. **ATAC 用默认双峰模型，峰被切碎**（§15.5.1）｜本实验 3.1：察觉 = MACS2 建模警告/失败（措辞随版本变，以日志与产物计数为准）；峰数异常多、中位宽异常小；IGV 上连续开放区被切碎。合成证据见 3.7（互相关峰 9 bp vs 208 bp）。双端确认 `-f BAMPE`。
2. **缺 input 对照的假峰与 FRiP 风险**（§15.5.2）｜本实验 3.1/3.3：ATAC 无 input 属正常，不误判为实验缺项；查 MACS2 日志是否真有 control 行（ATAC 没有是正常的）；联查 blacklist 是否实际执行（本课「未过滤」照写）、峰落重复区与 FRiP；用 IDR 而非单样本峰数作主要证据，并知道 IDR 排除不了可重复的系统偏差。
3. **最近基因被当成靶基因**（§15.5.3）｜本实验 3.5：察觉 = 查峰到 TSS 的距离分布、是否隔着其他基因、真实调控距离/基因间距的比值；表头措辞写「最近基因」，需互作或功能证据才升级为靶基因。合成证据见 3.7（错配 66.5%/95.5%）。
4. **motif 背景 GC/长度失配**（§15.5.4）｜本实验 3.6：察觉 = 核对 Targets/Background 三列、背景生成方式、`-mask`、summit 取窗与重复可重现性；换匹配背景重跑。不能凭「GC-rich」本身判真或判假。
5. **有效基因组大小与参考不匹配**（§15.5.5）｜本实验 3.1：把 `GSIZE`/`EGS` 抄出来与「0.7–0.9 × 373,795,655 = 2.6×10⁸–3.4×10⁸」对账（教材手算），核对两处同数（L57–60 内置校验）与 `*_peaks.xls` 头注释记录的值；本课 3.0e8 在区间内。
6. **染色体命名不匹配，流程跑完但结果为空**（§15.5.6）｜本实验 3.0/3.1/3.5：察觉 = `samtools view -H ... | grep '^@SQ'` 与 `head ref/genome.fa.fai` 逐字对照；R 日志「共同染色体 = 0」脚本直接 stop（不再只是 warning）；注释 intergenic >95% 红灯。从头统一到同一份 FASTA/GFF3。

## 6. 思考题（教材 §15.7，习题的上机版，不给答案）

1. 你的注释表里某个可重复峰的最近基因距离是 47 kb（设例）。什么条件下愿意把它写进候选靶基因表、什么条件下不愿意？需要什么额外数据才能把「愿意」变成「确定」？（§15.7 习题 3 → 15.4.5 的比值判据与 15.5.3）
2. HOMER 的 known motif 结果中 Top 1 是 SP1（GC-box），`% of Targets = 41%`、`% of Background = 33%`、`P-value = 1e-18`（设例）。这是不是可信的生物学发现？给出依据和你会做的一次验证操作。（§15.7 习题 4 → 15.4.6 与 15.5.4）
3. 同学报告：处理组 ATAC 有 68 000 个峰、对照组 41 000 个，说明处理让染色质整体变开放；测序量分别是 52 M 与 31 M 读段（设例）。指出问题，写出你会要求他补做的三件事。（§15.7 习题 5 → 15.4.3/15.4.4）
4. 你的 ATAC 实验没有 input。报告方法学必须写清哪三件事？若改成 TF ChIP-seq，对照怎么配，input 与 IgG 各负责校正什么？（§15.7 习题 6 → 15.5.2）
5. 两个样本的 FRiP 分别是 0.31 与 0.06、TSSE 分别是 8.4 与 2.1（设例）。能不能直接说「前者调控更强、后者调控更弱」？这两个数各自在说什么，下一步查什么？（§15.7 习题 8 → 15.4.4）
6. 差异峰关联基因 512 个、差异基因 1 843 个、可检测基因全集 12 400 个、观察交集 137 个（设例）。手算独立时的交集期望、标准差与 z 值。若有人报告的置换零分布中位数明显低于理论值（例如低出近两个标准差），怎样判断这个数有问题、可能错在哪？（§15.7 习题 7 → 15.4.7；手算中位数与脚本零分布不完全同义，不要拿 76 去对脚本输出）

课堂讨论（讲义 ⑩）：选型三维度论证、47 kb 判据、SP1 验证操作、400 字课题迁移方案。

## 7. 提交物

- **对应作业**：`08_assessment/master/assignments/m05_regulome_assignment.md`（占课程总成绩 5%）。打包为 `学号_姓名_m05.zip`（≤200 MB，不要把 BAM 与 bigwig 打进包），解压后：

  ```
  学号_姓名_m05/
  ├── report.pdf                # 主报告 ≤9 页，六节按作业规格
  ├── scripts/
  │   ├── peak_calling.sh       # 你实际投递用的上游脚本（未改就复制课程脚本，改了交个人副本）
  │   └── peak_annotation.R     # 05_peak_annotation_mine.R（read.delim 副本）
  ├── results/
  │   ├── qc_table.tsv          # 每样本：比对率/重复率/线粒体%（写「不可计算」）/NRF（写「未产出」）/FRiP/TSS enrich（写「见热图，数值未产出」）/判定
  │   ├── peaks_summary.tsv     # 各样本 peak 数与宽度中位数（narrowPeak 第 3 列减第 2 列）
  │   ├── reproducible_peaks.bed# 3.3 产物（合并版注明合并方式：cat|sort|bedtools merge）
  │   ├── peak_annotation.csv   # 3.5 产物
  │   ├── homer_known_top.tsv   # knownResults.html 的 Top 行：P-value / % Targets / % Background
  │   └── peak_gene_overlap.tsv # 交集名单 + 置换统计的固定格式合并（格式与生成命令见下）
  ├── figs/                     # 标题/轴/图例一律英文
  │   ├── fig1_fraglen.png      # fraglen.txt 直方图（核小体阶梯；画法见步骤 3.1 检查点 3）
  │   ├── fig2_tss_heatmap.png  # 3.2 tss_heatmap.png
  │   ├── fig3_cor_heatmap.png  # 3.2 cor_heatmap.png（无 input 列，方法学写明原因）
  │   ├── fig4_idr_plot.png     # 3.3 idr --plot 的 png
  │   ├── fig5_anno_pie.png     # 3.5 peak_annotation_plots.pdf 转 PNG（见下）
  │   └── fig6_permutation.png  # 3.5 overlap_permutation.pdf 转 PNG（见下）
  └── env_snapshot.yml          # conda env export --no-builds
  ```
- **文件来源对照**（命名不一致处在此闭环，保留生成过程，不把手工表说成脚本原生文件）：
  - `peaks_summary.tsv` 各样本「peak 数 / 峰宽中位数」按下式现算（narrowPeak 无表头，第 3 列减第 2 列 = BED 0-based 半开区间宽度；awk 没有内置中位数，用 R）：
    ```bash
    cd /d3/scratch/${USER}/ngs/m05
    tail -n +2 samples_raw.tsv | cut -f1 | while read -r S; do
        Rscript -e 'p <- read.table(commandArgs(TRUE)[1]); cat(commandArgs(TRUE)[2], nrow(p), median(p$V3 - p$V2), "\n")' \
            run/${S}/peaks/${S}_peaks.narrowPeak ${S}
    done > results/peaks_summary.tsv
    ```
  - `peak_gene_overlap.tsv` 有**固定格式**：前两行是 `#` 开头的置换统计量（表头一行 + 数值一行，来自 `overlap_permutation_test.csv`），第三行起是交集基因名单（TSV 表头 + 数据行，来自 `diffpeak_x_deg.csv`）。按下式生成，两个源文件一并保留：
    ```bash
    cd /d3/scratch/${USER}/ngs/m05/results/anno
    { head -1 overlap_permutation_test.csv | tr ',' '\t' | sed 's/^/# permutation: /'
      sed -n '2p' overlap_permutation_test.csv | tr ',' '\t' | sed 's/^/# permutation: /'
      head -1 diffpeak_x_deg.csv | tr ',' '\t'
      tail -n +2 diffpeak_x_deg.csv | tr ',' '\t' ; } > peak_gene_overlap.tsv
    ```
  - `fig5_anno_pie.png` / `fig6_permutation.png` 的源文件是 R 脚本出的 PDF，转 PNG 用 poppler 工具（`pdftoppm -png -r 150 results/anno/peak_annotation_plots.pdf fig5_anno_pie`，输出名带页码后缀，取对应页重命名；或任何等价的 PDF→PNG 工具）。
  - `reproducible_peaks.bed` 不是 shell 脚本自动产出，是 3.3 手工 IDR 步骤的产物；`qc_table.tsv` 各列必须从实际产出填：线粒体%写「不可计算（本课程参考无细胞器序列）」、NRF 与数值 TSSE 写「当前流程未产出」——**不得编造或从热图/重复率反推**。
- **诚实红线**（本指导与作业规格的差距如实写，等课程侧裁决，不由你造假补齐）：① 差异峰无生成脚本——产物命名「可重复峰关联基因 ∩ 差异基因」，不称差异峰；② 数值 TSSE/NRF/PBC 未产出——相应栏写「未产出」，方法学写明热图 ≠ TSSE；③ 相关矩阵含 input、线粒体百分比与主线 ATAC 数据冲突——写「不适用 / 不可计算」并各附一句原因。报告「方法选择与结果可信度说明」四问按教材 15.4/15.5 写实；黑名单状态、`-g`/`EGS`、IDR 输入阈值必须写清（教材 15.6 的八项验收记录）。
- **提交方式**：课程 LMS「专题作业 m05」；截止 m05 课后第 10 天 23:59；迟交/重交规则以作业规格为准。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念/失效条件/贯穿案例/习题） | `textbook/chapters/ch15/manuscript.qmd` §15.4 / §15.5 / §15.6 / §15.7 |
| 统计背景（泊松、BH、置换检验） | `textbook/chapters/ch12/manuscript.qmd` §12.4 |
| 本专题讲义（⑤ 操作、⑥ 解读、⑦ 统计插件、⑨ 排错） | `02_lectures/master/topic05_regulome/05_regulome_lecture.md` |
| 上游脚本（含 SGE 作业头） | `03_code/master/scripts/05_peak_calling.sh`（MODE 分派 L137–166、FRiP L171–176、bigwig L184–186） |
| 下游注释与置换脚本 | `03_code/master/scripts/05_peak_annotation.R`（TxDb L59、stop L67–72、红灯 L84–90、置换 L134–152） |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch15_local_lambda.py`、`ch15_atac_fragment_model.py`、`ch15_motif_gc_background.py`、`ch15_nearest_gene_mismatch.py` |
| 数据说明、登录号与下载 | `06_data/master/README.md` m04/m05 节；`06_data/accessions.tsv`；`06_data/master/download_master.sh` |
| 环境定义 | `07_envs/conda/env_master_transcriptome.yml`（`ngs_ms_transcriptome`）、`env_master_base.yml`（`ngs_ms_base`） |
| 作业规格 | `08_assessment/master/assignments/m05_regulome_assignment.md` |
| 上游衔接 | m04（差异表达结果全表 `deseq2_results.tsv` 是 3.5 的必需输入；同批样本） |
