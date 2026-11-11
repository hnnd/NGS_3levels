---
title: "实验指导 u02：R 与数据可视化——把上游表变成可信的图"
level: undergraduate
topic: u02
textbook: [ch03]
lecture: ../02_lectures/undergraduate/unit02_r_visualization/02_r_visualization_lecture.md
env: ngs_ug_base
---

# 实验指导 u02：R 与数据可视化

> 上机时手边打开的这份文件。每一步回答四件事：做什么、敲什么、看到什么算对、
> 看到什么说明错了。原理与判据在教材第 3 章（§3.4 概念、§3.5 失效条件、§3.7 习题），
> 这份指导只放操作与自查入口。所有标「预期区间（未实测）」的数字是课程写下的自查范围，
> 不是实测结果；三个绘图脚本本课未在集群真实跑完，相关步骤按「集群未实测」对待。

## 0. 本实验对应什么

- **教材**：第 3 章 用 R 把表格变成可信的图；本科路径 §3.4.1–3.4.7 与 §3.4.11，
  失效条件 §3.5 四条。学习目标 LO03-01（读表与类型检查）、LO03-02（长宽转换与行数核对）、
  LO03-03（五要素构图）、LO03-04（四条失效的诊断与导出验收）。
- **学时**：u02 为 4 学时异步自学单元；本实验是其上机部分。
- **产出去向**：本实验的图是 u08 综合项目报告的核心图版——按四个专题组织、共
  **5 个 PDF 文件**：k-mer 频谱（模板 §2.2）、QUAST 对比与 BUSCO 堆叠（§3.1，两张
  分开出）、进化树与泛基因组组成（§6、§7，两张分开出）。
- **环境**：conda 环境 `ngs_ug_base`（画树步骤另需 `ngs_ug_phylo`）。R 4.3.1、ggplot2
  3.4.2 已钉版本；tidyverse、readr、dplyr、tidyr、ggtree 未钉版本，不要声称「某包某版本
  的行为已实测」（教材 §3.3）。
- **计算纪律**：一切计算一律 `qsub` 投递计算节点——三个绘图脚本与步骤 3.1 的 demos
  自测都算计算；登录节点只做激活环境、编辑作业脚本、下载（本课规则，同 u06 实验指导）。

## 1. 实验前检查

- **前置模块**（讲义 ②）：`l0_01_linux` Q06/Q09（qsub 与相对路径）、`l0_03_conda`
  Q02/Q07（作业内激活环境）、`l0_02_r` 全部 10 题——其中上机题第 8–10 题（筛选汇总 +
  出图 + ggsave 导出）就是本实验步骤 3.1 的前身。
- **激活并核验**（登录节点允许）：

  ```bash
  source /opt/miniconda3/bin/activate && conda activate ngs_ug_base
  Rscript -e 'cat(R.version.string, as.character(packageVersion("ggplot2")), "\n")'
  command -v Rscript
  ```

  这条命令在做什么：确认你拿到的是课程环境而不是系统 R；本课所有绘图走 `Rscript`
  非交互运行、结果存文件不弹窗（讲义 ⑨ 9.1）。
- **检查点**：打印 **R 4.3.1** 与 **ggplot2 3.4.2**（`07_envs/conda/env_ug_base.yml` 钉值）。
  若打印 4.5.x 或缺包报错，说明你拿到的是系统 R（本课核验机的系统 R 4.5.2 实测缺
  readr、跑不了这三个脚本）——不要硬跑，回去检查环境激活，正式跑走 qsub。
- **出错信号**：`there is no package called 'readr'` → 用的是系统 R 或环境没激活
  （教材 §3.4.6「装了不等于加载了」；环境归属另见第 2 章 §2.5.3、讲义 ⑨ 9.1）。

## 2. 实验数据

本章没有新的测序数据、**没有新登录号**；输入是上游模块已经算好的**表**。
两条轨道数据不同、步骤相同：

| 轨道 | k-mer 频谱输入 | QUAST / BUSCO 输入 | 树与泛基因组输入 |
|---|---|---|---|
| 校内（u08 手册产物） | `survey/reads.histo`、`reads.k17.histo`、`reads.k25.histo`（u06 模块 1 产物） | `quast_out/{canu,flye}/report.tsv`、`busco_{canu,flye}/short_summary*.txt` | `ident/core_gene_alignment.treefile`、`pangenome/gene_presence_absence.csv` |
| 校外（公开数据自学） | u06 实验指导已下载并跑出的三档 `*.histo`（`ERR15732342`，Illumina ≈48×，已登记 `06_data/accessions.tsv`） | 自己组装的 CIX4481 经 QUAST / BUSCO 的产物（对答案完成图 `GCA_987216485`，4,768,212 bp，登记值） | 12 株完成图的 IQ-TREE / Roary 产物（清单见 `06_data/undergraduate/README.md` §2.2） |

- 校外轨道若还没跑出上游产物：先按 u06 实验指导完成模块 1（k-mer 扫描）与模块 2（组装
  + QUAST/BUSCO）；建树与泛基因组属 u08 模块 5/6，按 u08 手册跑 IQ-TREE / Roary 后再回本章出图。
- 没有真实表时的退路：三个脚本都支持 `--demo`，用内置设例跑通代码路径（设例数值只
  证明代码路径通，**不进报告**——教材 §3.4.1 的三种证据状态；每步命令下方给了 `--demo` 的替换写法）。
- 工作目录沿用课程约定：`/d3/scratch/${USER}/ngs`，图统一放 `results/figures/`。
  上游产物大，只做软链接不拷贝，不要放家目录（u08 项目说明）。**目录不会自动出现**：
  先按步骤 0 建好再写作业脚本，否则重定向写文件会报 `No such file or directory`。

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出 / 检查点 / 出错信号。命令里的脚本名、参数名、输出文件名
> 与 `03_code/undergraduate/scripts/` 现版逐字一致（本指导修订时已逐个 grep 核对，见
> 任务回执）。三个脚本只出 **PDF**（`ggsave()` 未写 dpi，不产出同名 PNG，教材 §3.4.9）；
> 要 PNG 时另加一次 `ggsave(..., dpi=300)`，不属于课程脚本的产出。集群实跑本课无记录，
> 一切区间写「预期区间（未实测）」。
>
> **在哪敲命令**：SSH 登录后当前目录是家目录。下文 scratch 路径以 `/d3/scratch/${USER}/ngs`
> 为根；`${REPO}` 代表课程仓库在集群上的绝对路径（由教师公布；课程站暂未发布 textbook/，
> demos 与脚本都从课程仓库获取）——**写进每个作业脚本正文**加一行 `REPO='<课程仓库路径>'`
> 换成真实路径；作业在计算节点是全新 shell，不继承终端变量。作业都带 `#$ -cwd`：用
> `cd /d3/scratch/${USER}/ngs && qsub <作业名>` 投递，日志（`u02_*.o<作业号>`）落在步骤 0 的目录里。

### 步骤 0：准备工作目录（登录节点执行，第一次上机必做）

- **目的**：课程约定的 scratch 目录没人替你建；目录不在，写作业脚本的重定向一敲就崩。
- **命令**：

  ```bash
  mkdir -p /d3/scratch/${USER}/ngs/results/figures
  cd /d3/scratch/${USER}/ngs
  ls -ld /d3/scratch/${USER}/ngs/results /d3/scratch/${USER}/ngs/results/figures
  ```

- **产出**：`/d3/scratch/${USER}/ngs/`（作业脚本与日志放这里）与 `results/figures/`（图放这里）。
- **检查点**：两行 `ls -ld` 都打印出目录信息；写作业脚本时 `No such file or directory`
  → 你跳过了本步骤，回来补 `mkdir -p`。

### 步骤 3.1：语言机制热身（demos，qsub 最小作业）

- **目的**：先亲眼看见教材 §3.5 前两条失效（因子顺序、NA 静默）的机制，再进绘图——
  图出问题时你才知道往哪查。
- **命令**（登录节点写作业脚本、投递计算节点；两条 demos 只用 R base，仍按计算纪律走 qsub）：

  ```bash
  cat > /d3/scratch/${USER}/ngs/u02_warmup.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u02_warmup
  #$ -cwd
  #$ -j y
  #$ -pe smp 1
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  REPO='<课程仓库路径>'   # 换成教师公布的课程仓库绝对路径
  cd ${REPO}
  Rscript textbook/demos/ch03_factor_levels.R --selftest
  Rscript textbook/demos/ch03_na_propagation.R --selftest
  EOF
  cd /d3/scratch/${USER}/ngs && qsub u02_warmup.job
  ```

- **产出**：作业日志（`u02_warmup.o<作业号>`）里两段 `SELFTEST PASS` 与算例打印（无文件产出）。
- **检查点**（数字为 2026-11-10 本机现跑 rc=0，与教材 §3.10 登记一致）：
  1. 算例 A：默认 levels 打印 `Duplicated → Fragmented → Missing → Single-copy`，
     显式绑定后 `Single-copy` 出场位置 4→1；
  2. 算例 B（顺序案例，本科层要求）：同一组数据，标签命名一换、参照组跟着换人——
     本科只要求看到「顺序决定谁被当基准」；系数反转的模型侧解读属硕士层（§3.4.8、
     §3.5.1 末段），看一眼即可，不作要求；
  3. 算例 C：`levels(f) <-` 按位置改名后 `ctrl` 标签均值 10.0→13.0，数据一个数没变；
  4. 算例 D：筛掉 `ctrl` 后 `nlevels` 仍 2、`ctrl` 计数 0，`droplevels()` 后 1；
  5. na_propagation 算例 B：`subset()` 后 6 行剩 3 行、`ctrl` 组 0 行且**无任何警告**；
     算例 E：`ctrl` 默认汇总 `NA`、`na.rm` 后 11.75（n=2），`trt` 15.3（n=3）。
- **出错信号**：任一算例打印 `FAIL` 或数值与上面不符 → R 版本异常或脚本被改动，
  停止实验并报告教师；日志报 `cannot open file '...textbook/demos/...'` → 作业里
  `REPO=` 的路径不对，改对后重投。

### 步骤 3.2：k-mer 频谱图（qsub + `02_plot_kmer_histogram.R`）

- **目的**：把 Jellyfish 直方图画成对数频谱、标出主峰——报告模板 §2.2 的图。
- **命令**（登录节点写作业脚本，投递计算节点；【集群未实测】）：

  ```bash
  cat > /d3/scratch/${USER}/ngs/u02_kmer.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u02_kmer
  #$ -cwd
  #$ -j y
  #$ -pe smp 1
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  REPO='<课程仓库路径>'
  cd /d3/scratch/${USER}/ngs
  Rscript ${REPO}/03_code/undergraduate/scripts/02_plot_kmer_histogram.R \
          results/figures/kmer.pdf \
          21:survey/reads.histo 17:survey/reads.k17.histo 25:survey/reads.k25.histo
  EOF
  cd /d3/scratch/${USER}/ngs && qsub u02_kmer.job
  ```

  还没有 histo 文件时，先用 `--demo` 通路径（内置设例只有 k=21 一档、主峰 45 /
  重复峰 90 / 共 300 行，脚本声明值，未实测，不进报告）：

  ```bash
  Rscript ${REPO}/03_code/undergraduate/scripts/02_plot_kmer_histogram.R \
          results/figures/kmer.pdf --demo
  ```

  这条命令在做什么：参数格式 `<输出.pdf> <k>:<histo 路径>`，一对一档，多档写多对；
  脚本把无表头两列直方图读成数值（depth / n_kmers），纵轴取 log10，横轴用
  `coord_cartesian(xlim=c(0,150))` 只截显示不删数据，跳过深度 ≤5 的错误峰区搜主峰
  （`ERROR_PEAK_CUTOFF = 5`、`XLIM_MAX = 150` 为现行显示配置，非通用判据，教材
  §3.4.7），最后存 7 × 4.5 英寸 PDF 并打印各档主峰表；输出目录不存在脚本自己建。
- **产出**：`results/figures/kmer.pdf` + 作业日志里的主峰表。
- **检查点**：
  1. 日志打印 `Saved: results/figures/kmer.pdf`，且所给的每一档 k 各有一行主峰深度
     （`--demo` 只有内置 k=21 一行）；
  2. 主线数据主峰深度在**几十的量级**——`ERR15732342` 为 Illumina ≈48×
     （`06_data/undergraduate/README.md` §2.1 登记值，预期区间，未实测）；
  3. 图面「两必有 + 一可选」：低深度区贴地的错误峰、主峰处虚线 + 数值标注必有；
     约 2× 深度处的重复峰**取决于基因组重复内容，真实数据没有不代表错**（副标题
     是通用说明文字，不证明每个样本都有重复峰）；
  4. 三档主峰并排比较——档间差异本身正常（k 越大每条读段贡献的 k-mer 越少、
     峰位漂移，手算 `100−17+1=84`、`100−25+1=76`，教材 §3.4.7），报告三档并引。
- **出错信号**：
  - 整张图灰白空、无曲线 → 表读错（分隔符/路径），n_kmers 全 NA：静默类
    （教材 §3.5.3），先对输入 `summary()` 再重画；
  - `main peak = NA`、无主峰虚线 → 搜索窗口内候选行数为 0：输入全 NA，或可用深度
    全部落在窗口外（脚本现行口径：跳过深度 ≤5 后只在 ≤150 内取最大，教材 §3.4.7）；
  - 主峰数值顶在 150、完整频谱右侧还有更高的峰 → 真峰在窗口外，脚本打印的是
    窗口内最大值，虚线标错位置但不报错：在未截断的直方图里另找真主峰（第 1 列=
    深度、第 2 列=该深度的 distinct k-mer 数）：
    `awk '$1>=10 && $1<=100' survey/reads.k21.histo | sort -k2,2nr | head -5`；
  - `文件不存在: …` 停止 → histo 路径写错（教材 §3.4.2 读表五问）；
  - `参数格式应为 <k>:<histo 路径>` 停止 → 冒号写法错，对照上面命令检查。

### 步骤 3.3：QUAST 对比 + BUSCO 堆叠（qsub + `02_plot_assembly_metrics.R`）

- **目的**：Canu/Flye 并排对比图——报告模板 §3.1 的表与图。**本步只呈现对比关系，
  优劣裁决是 u08 选型论证的事**（第 8 章四步证据链；N50 单指标会选错，
  错误连接同样抬高 N50）。
- **真实数据的前置确认**（两条，不满足照抄命令必失败）：
  1. **QUAST 报告必须一套组装一份**。u06 的评估脚本把两套组装放进同一张 `quast_results`
     并排对比表（u06 实验指导步骤 4 的产物），而本步脚本按「第 1 列指标名、第 2 列
     数值」的**单组装两列表**解析——并排表直接喂进来会静默只读到其中一列。先补一个
     小作业按组装器各跑一次 QUAST（登录节点写作业、投递计算节点）：

     ```bash
     cat > /d3/scratch/${USER}/ngs/u02_qprep.job <<'EOF'
     #!/bin/bash
     #$ -S /bin/bash
     #$ -N u02_qprep
     #$ -cwd
     #$ -j y
     #$ -pe smp 4
     source /opt/miniconda3/bin/activate
     conda activate ngs_ug_assembly
     cd /d3/scratch/${USER}/ngs/assem/eval
     quast.py ../canu/test-pacbio/test.contigs.fasta -o quast_canu -t 4
     quast.py ../flye/out_pacbio/assembly.fasta      -o quast_flye -t 4
     EOF
     cd /d3/scratch/${USER}/ngs && qsub u02_qprep.job
     ```

     产出 `assem/eval/quast_canu/report.tsv` 与 `assem/eval/quast_flye/report.tsv`。
     校内轨道若手册已按组装器分开产出 `report.tsv`，可跳过本小作业。
  2. **BUSCO summary 的真实文件名不是 `short_summary.txt`**：BUSCO 5 落盘名形如
     `short_summary.specific.bacteria_odb10.busco_canu.txt`（以 `ls` 实见为准），参数里要写文件本身。
- **命令**（qsub，作业头同 3.2；【集群未实测】）：

  ```bash
  cat > /d3/scratch/${USER}/ngs/u02_quast.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u02_quast
  #$ -cwd
  #$ -j y
  #$ -pe smp 1
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_base
  REPO='<课程仓库路径>'
  cd /d3/scratch/${USER}/ngs
  Rscript ${REPO}/03_code/undergraduate/scripts/02_plot_assembly_metrics.R results/figures \
          quast_canu:assem/eval/quast_canu/report.tsv quast_flye:assem/eval/quast_flye/report.tsv \
          busco_canu:$(ls assem/eval/busco_canu/short_summary*.txt) \
          busco_flye:$(ls assem/eval/busco_flye/short_summary*.txt)
  EOF
  cd /d3/scratch/${USER}/ngs && qsub u02_quast.job
  ```

  还没有真实产物时，先用 `--demo` 通路径（QUAST Canu 3/2.10/2.30/4.12、Flye
  5/1.70/1.95/4.05，BUSCO 97.2/0.8/0.6/1.4 与 95.1/2.3/1.0/1.6，均为脚本内置设例，未实测，不进报告）：

  ```bash
  Rscript ${REPO}/03_code/undergraduate/scripts/02_plot_assembly_metrics.R \
          results/figures --demo
  ```

  这条命令在做什么：第一个参数是**输出目录**（不是文件），后面是 `key:路径` 对，
  key 只认 `quast_canu / quast_flye / busco_canu / busco_flye`（脚本 usage 行）。
  QUAST 侧从单组装两列式 `report.tsv` 正则取四个指标（contigs、N50、最长 contig、
  总长，后三者 ÷1e6 换 Mb）画一行四格分面柱状图（9 × 3.6 英寸）；BUSCO 侧从
  `short_summary*.txt` 抓 `C:..%[S:..%,D:..%],F:..%,M:..%` 汇总行拆 S/D/F/M 四档堆叠
  （5.5 × 4 英寸）。分面各用各的 y 轴是因为**单位不同**（条 vs Mb）——换算成 Mb 后
  量级已接近（教材 §3.4.7）；脚本纵轴笼统写 `Value` 属不合格示例，你的报告图注必须
  逐分面带单位。若目录里有多份 `short_summary*.txt`，把 `$(ls …)` 换成具体文件名。
- **产出**：`results/figures/quast_compare.pdf` + `results/figures/busco_stacked.pdf`
  + 作业日志里两张 stdout 表（每图关键数值，报告引数从这里抄）。
- **同库前置（先于一切分数对照）**：凡对照 README §四「BUSCO Complete >97%」这类预期
  区间，前置条件是「**同一评估库** `xanthomonadales_odb10` + 预期区间（未实测）」。
  先确认实际库名：看 `short_summary*.txt` 文件名里的库名段与文件头说明行，或回查 u06
  评估作业命令里的 `-l` 参数——**不要拿脚本图题的 `bacteria_odb10` 当实际库名**（图题
  是脚本写死的常量）；两库基因集不同、分数不可比（教材 §3.4.7）。
- **检查点**：
  1. 两个 PDF 都落盘 + stdout 表每个数能指回输入文件的一行（教材 §3.4.11）；
  2. 输入自查对照 README §四预期区间（未实测）：contigs **1–5 条**、总长 **4.6–4.9 Mb**、
     BUSCO Complete（S+D）**>97%**（仅在同库前提下成立，见「同库前置」）；明显偏离先查上游，不查绘图；
  3. BUSCO 图序必须是 `Single-copy → Duplicated → Fragmented → Missing`（脚本用
     显式 levels 绑定，是 §3.5.1 的正面对策）；退回字母序（D→F→M→S）就是失效
     第 1 条现场；
  4. 报告行文写你的实际评估库名，不照抄脚本图题的固定库名（见「同库前置」）。
- **出错信号**：
  - `找不到 QUAST 报告` / `找不到 BUSCO summary` 停止 → 路径错或文件名没写全
    （注意真实文件名形如 `short_summary.specific.….txt`，教材 §3.4.2）；
  - `BUSCO summary 中找不到 C/S/D/F/M 汇总行` 停止 → 文件给错（要的是
    `short_summary*.txt`，不是 full_table 或运行日志）；
  - 某根柱子缺一块而图照出（无报错） → 正则未命中、该指标是 NA：静默类
    （教材 §3.4.7），拿 QUAST 报告原文逐行核对。

### 步骤 3.4：进化树 + 泛基因组（qsub + `02_plot_tree_and_pangenome.R`，`ngs_ug_phylo`）

- **目的**：u08 报告的演化图版（模板 §6 树、§7 泛基因组组成）。
- **命令**（作业内激活**另一个环境**——ggtree 只在 `ngs_ug_phylo`；【集群未实测】；
  投递前先清旧图防掩盖，登录节点执行）：

  ```bash
  rm -f results/figures/core_gene_tree.pdf results/figures/pangenome_composition.pdf
  cat > /d3/scratch/${USER}/ngs/u02_phylo.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N u02_phylo
  #$ -cwd
  #$ -j y
  #$ -pe smp 1
  source /opt/miniconda3/bin/activate
  conda activate ngs_ug_phylo
  REPO='<课程仓库路径>'
  cd /d3/scratch/${USER}/ngs
  Rscript ${REPO}/03_code/undergraduate/scripts/02_plot_tree_and_pangenome.R results/figures \
          tree:ident/core_gene_alignment.treefile roary:pangenome/gene_presence_absence.csv
  EOF
  cd /d3/scratch/${USER}/ngs && qsub u02_phylo.job
  ```

  还没有真实产物时，先用 `--demo` 通路径（**只出 1 个 PDF**：脚本内置数据不设树
  输入，四类计数 3120/210/890/1450 为设例，未实测，不进报告）：

  ```bash
  Rscript ${REPO}/03_code/undergraduate/scripts/02_plot_tree_and_pangenome.R \
          results/figures --demo
  ```

  这条命令在做什么：`tree:` 把 Newick 树画成带支持率的系统树（6.5 × 5 英寸 PDF），
  `roary:` 把 `gene_presence_absence.csv`（前 14 列注释、第 15 列起每株一列）按基因簇
  出现在多少株里分四类画柱状图（6 × 4 英寸），四类计数同时打印到日志。
- **产出**：`results/figures/core_gene_tree.pdf` + `results/figures/pangenome_composition.pdf`。
- **检查点**：
  1. **预期产物计数 = 2 个 PDF**（真实数据：树 + 泛基因组各一）。脚本缺 ggtree/ape 时
     打印 `[skip]` 跳过画树、退出码仍是 0——拿错环境时树图**静默缺失**；核对**本次
     作业日志**里的 `Saved:` 行数与新落盘文件，不看退出码、不被旧文件掩盖（教材
     §3.4.7）。**`--demo` 例外：只有 1 个 PDF**（`pangenome_composition.pdf`）——
     demo 数到 1 个是正常的，不是环境坏了；
  2. 日志里四类计数之和 = 基因簇总数；空类由 `tidyr::complete` 补零显示，
     四类全 0 不可能出现——出现先想上游 Roary 没跑完；
  3. 分母口径：脚本总株数取自表结构（菌株列数 = 总列数 − 14），并对 `No. isolates`
     做缺失/越界检查（超出 1..N 直接停止）。教材 §3.4.7 该处仍写旧的「取
     `No. isolates` 最大值」口径，与现行脚本不一致——**以脚本源码与本次日志为准**，
     株数从列数来；你要能说出株数从哪来；
  4. 图内类名 `Core (>=99%) / Soft-core (95-99%) / Shell (15-95%) / Cloud (<15%)`
     是 Roary 默认百分比口径；报告行文按课程口径写「允许缺失 k 株（≈ x%）」，
     不写会在小样本上退化的「95% 核心」。
- **出错信号**：
  - 日志 `[skip] 未安装 ggtree/ape` → 环境错（讲义 ⑨ 9.1），改激活 `ngs_ug_phylo`
    重投；
  - `列 'No. isolates' 不存在` / `菌株列不足 2 列` / `'No. isolates' 超出 1..N 范围`
    停止 → csv 被截断或读错文件（教材 §3.4.2）；
  - 树画出来空/单节点 → 上游 IQ-TREE 没跑完，回 u08 模块 5 查；
  - 支持率读法：枝上数字是重抽样下的稳定性，不是「该分支为真的概率」；
    UFBoot 与标准 bootstrap 不同尺度，不可互比（教材 §3.4.7、脚本结尾提示）。

### 步骤 3.5：图面验收（对齐教材 §3.4.11 六项图注）

- **目的**：把「图能出」升级为「图可信、别人照记录能重画」。
- **命令**（qsub；在上一步作业尾部追加，或单独投一个小作业）：

  ```bash
  Rscript -e 'suppressPackageStartupMessages({library(readr); library(dplyr); library(ggplot2)}); sessionInfo()'
  ```

  这条命令在做什么：`sessionInfo()` 打印的是**当前这个 R 进程**已加载的包与版本，
  所以要放在同一作业里、先加载绘图脚本同款包（三个脚本都用 readr/dplyr/ggplot2）再
  打印，才反映真实出图环境；输出对照课程 pin（R 4.3.1、ggplot2 3.4.2）摘录进验收记录。
  作业脚本是 bash，`sessionInfo()` 是 R 函数**不能裸写**（裸写报 `command not
  found`），必须经 `Rscript -e` 调用。
- **检查点**（图注六项逐项有值：输入 / 处理 / 参数 / 样本量 n / 环境 / 证据状态）：
  1. 每张图轴名带单位（条、Mb、%），分面逐面标单位；
  2. BUSCO 图四档顺序正确（回看步骤 3.3 检查点 3）；
  3. 每张图能回答「它支持报告里的哪一句话」；
  4. 控制台 `Removed N rows` 类提示与缺失值个数对账（教材 §3.5.3：绘图丢行有
     提示、筛选丢行无警告，两笔账分开记）；
  5. 本科两条导出自查（§3.5.4 本科只到识别）：图内文字一律英文（课程环境约定，降低
     字体依赖，不是技术定律）；导出后放大看一遍——有没有方块、字够不够大；字太小时
     先判画布是否明显大于目标版面，再决定改画布还是改字号与布局。
- **出错信号**：所有点同色、图例多出写着颜色字符串的假条目 → 常量被写进 `aes()`
  （教材 §3.5.2；课程脚本无此写法，多半犯在自己补画的图上）；图上类序倒置
  → 教材 §3.5.1。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填结果；「自查判据」列给来源，预期区间均标「未实测」。

| 栏目 | 单位 | 来源步骤 | 自查判据（来源） |
|---|---|---|---|
| 各 k 主峰深度（k=17/21/25） | ×（深度） | 3.2 | 主线数据几十的量级（README §2.1，Illumina ≈48×，未实测）；三档并排比较 |
| k-mer 图面（错误峰/主峰虚线必有；2× 重复峰可选） | 有/无 | 3.2 | 脚本副标题口径（教材 §3.4.7）；真实数据无重复峰不代表错 |
| QUAST 四指标（contigs / N50 / 最长 contig / 总长） | 条 / Mb | 3.3 | contigs 1–5、总长 4.6–4.9 Mb（README §四，未实测） |
| BUSCO S/D/F/M 四档 + 实际评估库名 | % + 库名 | 3.3 | Complete >97%（README §四，**同库** `xanthomonadales_odb10` 前提，未实测）；四档顺序 S→D→F→M（教材 §3.5.1） |
| 泛基因组四类计数 + 总株数 | 个 / 株 | 3.4 | 四类之和 = 基因簇总数；株数 = csv 总列数 − 14（脚本现行口径） |
| 产出 PDF 计数 | 张 | 3.2–3.4 | 真实数据合计 **5 张**（k-mer 1 + QUAST/BUSCO 2 + 树/泛基因组 2）；`--demo` 合计 4 张（树图跳过，见 §3.4 检查点 1） |
| sessionInfo 摘录 | — | 3.5 | R 4.3.1、ggplot2 3.4.2（课程 pin） |

## 5. 失效条件对照（教材 §3.5：本实验在哪一步、看什么能察觉）

1. **因子水平决定图序与标签对应**（§3.5.1）｜察觉：步骤 3.3 检查点 3 看 BUSCO 图序
   是否 S→D→F→M；3.1 的 selftest 算例 A/C 先给你看过「顺序倒置」与「标签换主人」
   长什么样；自己补图时出图前打印 `levels(f)` 与 `table(f)`。
2. **常量写进 `aes()` 被当成分类变量**（§3.5.2）｜察觉：步骤 3.5 图面验收——所有点
   同色、图例多出写着字符串的假条目就是；按课程脚本原样跑不会犯，犯在自己补画的图上。
3. **NA 静默丢弃/传播，样本量悄悄变小**（§3.5.3）｜察觉：步骤 3.2/3.3 的 stdout 表与
   行数对账；`Removed N rows` 提示与缺失值个数对账；`na.rm` 后的均值注明 n_used；
   3.1 算例 B/E 是现跑样本（ctrl 组 0 行无警告；11.75 只用了 2/3 个数）。
4. **方块与缩小的字**（§3.5.4，本科只要求识别）｜察觉：步骤 3.5 导出后放大检查；
   图内文字用英文是课程环境约定，不是技术定律（教材 §3.3、§3.4.9）。

## 6. 思考题（教材 §3.7 第 1–5 题，不给答案）

1. 读一份 4 行 4 列的组装指标表，写出读表后三条检查命令及各看什么；说明
   `read.csv()` 为什么把 `N50 (bp)` 改成 `N50..bp.`、怎么两行代码验证。
   （习题 1 → 教材 §3.4.2）
2. 把上题表转成长表（折叠三列）：转换后行数怎么算？单位不统一（条/bp/%）画
   分面图要注意什么？（习题 2 → 教材 §3.4.3、§3.4.6）
3. BUSCO 四档不设水平时图例什么顺序？显式绑定的依据是代码习惯还是生物学含义？
   （习题 3 → 教材 §3.4.4；步骤 3.1 算例 A 刚看过）
4. 8 个样本 Q30（含 2 个缺失）：`mean()` 与 `na.rm = TRUE` 各得什么？按「不低于 90」
   筛选存活几行？直接画散点图被移除几行？四个数写清各自分母。（习题 4 → 教材
   §3.4.4、§3.5.3；可手算复核）
5. 用 R 自带 `iris` 画三张散点图（`aes(color = Species)` / 颜色写在 `aes()` 外 /
   `aes(color = "#0072B2")`），描述三张图在颜色与图例上的差别，并说明为什么语言模型
   生成的代码常写成第三种。（习题 5 → 教材 §3.4.5、§3.5.2）

## 7. 提交物

- **对应考核**：上机考核材料**待发布**（课程考核目录已核实暂无 U02 条目），规格以
  任课教师课堂通知为准；本实验提交先按 L0-2 自测上机题第 8–10 题的**同类产出**准备。
- **打包命名**：`学号_姓名_U02.zip`（若作业系统要求填作业号，以教师公布的编号为准）。
- **提交内容**（真实数据产出）：图 PDF 五个（`kmer.pdf`、`quast_compare.pdf`、
  `busco_stacked.pdf`、`core_gene_tree.pdf`、`pangenome_composition.pdf`）；本指导
  §4 结果记录表（填写完整）；验收记录（脚本名 + 参数、作业日志 stdout 表摘录、
  sessionInfo 摘录、产出文件计数、控制台警告摘录）。真实数据未就绪时：`--demo`
  只用于跑通流程、图不进报告；可先交填写完整的记录表与作业日志摘录（注明 demo
  设例），图版补交以课堂通知为准。
- **去向**：u08 综合项目报告中，图分别进模板 §2.2（k-mer）、§3.1（QUAST/BUSCO）、§6
  （树）、§7（泛基因组）；评分维度见 `08_assessment/undergraduate/project/undergrad_project.md`。
- **诚实红线**：`--demo` 产物一律不进报告（设例，未实测）；预期区间不得写成实测；
  报告图注必须写清实际 BUSCO 库名与证据状态。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念 / 失效条件 / 习题） | `textbook/chapters/ch03/manuscript.qmd` §3.4 / §3.5 / §3.7 |
| 本单元讲义（原理细节、⑨ 常见错误 9.1–9.4） | `02_lectures/undergraduate/unit02_r_visualization/02_r_visualization_lecture.md` |
| 三个绘图脚本 | `03_code/undergraduate/scripts/02_plot_kmer_histogram.R`、`02_plot_assembly_metrics.R`、`02_plot_tree_and_pangenome.R` |
| 上游评估脚本（步骤 3.3 真实输入的产出方） | `03_code/undergraduate/scripts/06_kmer_survey.sh`、`06_assembly_eval.sh`（u06 实验指导步骤 1/4） |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch03_factor_levels.R`、`textbook/demos/ch03_na_propagation.R` |
| 数据说明、下载与预期区间 | `06_data/undergraduate/README.md` §2.1（登记值）、§2.2（12 株清单）、§四（自查区间） |
| 环境定义 | `07_envs/conda/env_ug_base.yml`（`ngs_ug_base`）、`07_envs/conda/env_ug_phylo.yml`（`ngs_ug_phylo`） |
| 作业与报告模板 | `08_assessment/undergraduate/project/undergrad_project.md`、`undergrad_report_template.md` |
