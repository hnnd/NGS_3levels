---
title: "实验指导 p07：Nextflow 流程跑通、缓存验证与范式对照"
level: phd
topic: p07
textbook: [ch23]
lecture: ../02_lectures/phd/topic07_workflow_nextflow/07_workflow_nextflow_lecture.md
env: ngs_phd_workflow
---

# 实验指导 p07：Nextflow 流程跑通、缓存验证与范式对照

> 上机时手边打开的这份文件。每步回答五件事：做什么、敲什么、产出哪个文件、看到什么算对、看到什么说明错了。
> 原理与判据在教材第 23 章（§23.4 概念方法、§23.5 九条失效、§23.7 习题、§23.9 答案、§23.10 数字索引）；
> 本指导只放操作与自查入口。
>
> **数字标注规则（全篇遵守）**：检查点里的每个数只来自四类合格入口——① 教材正文带复现入口的数（手算
> `4+1+4+1=10`、`4+1+1+1=7`、退出码 `137=128+9`、`143=128+15`、内存余量 1.3 至 2 倍，见 §23.4.5、§23.4.7、§23.4.8）；
> ② `06_data/phd/README.md` p07 节与 `06_data/accessions.tsv` 的登记事实；③ 环境 pin（`env_phd_workflow.yml`：
> `nextflow>=23.04,<26.10`、`snakemake=7.28.1`、`r-base=4.3.1`）；④ 本指导在 ASCII 副本上的**桩跑实测**（Nextflow
> 26.04.4 build 12445、`NXF_OFFLINE=true`、合成数据 60 转录本 × 4 样本 × 3000 对读段，逐条记在 §3，回执列了命令
> 与退出码）。**四类不能互相顶替**：桩跑的 `completed=` 只证明接线与缓存键行为，**不证明任何业务数值**；教材已撤下的
> 数、被标记暂缓装配的图、脚本注释里的经验区间一律不用。**真实数据（18 个样本）本轮一次也没跑**，凡涉及它的产物
> 一律写「集群实跑未验证」。
>
> **开工前必读的三条**（不知道这三条，第一个小时基本全废）：
>
> 1. **项目必须拷到纯 ASCII 路径**。课程仓库路径含中文（`.../课程/研究生/...`），实测在 `.../中文_nf/`
>    下桩跑直接失败，报 **5 条** `Invalid include source`（`main.nf:22`、`main.nf:23`、
>    `subworkflows/local/quantify.nf:5`、`:6`、`:7`），退出码非 0、`completed=0`；同一份项目拷到 ASCII
>    路径后 `completed=10`。这个报错看着像「文件不存在」，其实模块文件一个不少。**不要把「`include` 省略
>    `.nf` 后缀」当成因**——实测去掉两处 include 的后缀仍 `completed=10`，另一成因只有「目标文件确实不在」
>    （教材 §23.5.8 只记了非 ASCII 这一条）。
> 2. **`-profile test,conda` 在本机是失败路径**。本机没有 conda/mamba，实测
>    `Failed to create Conda environment … status : 127 … bash: line 1: mamba: command not found`
>    （配置里 `conda.useMamba = true`，而环境 yml 从未声明 mamba，教材 §23.4.9 把这条挂为未核实项）。
>    处置：先 `command -v mamba`；没有就把个人副本里的 `useMamba` 置 `false`，**再**确认 `command -v conda`
>    ——本机实测改完 `useMamba=false` 后仍失败，报到的是 `status : 127`、`bash: line 1: conda: command not found`；
>    两者都没有时，按 §1 在登录节点建环境，或改走 `-profile test,singularity`（镜像自带环境，但镜像要在
>    登录节点先拉，本机未实测）。
> 3. **桩跑的 `work/<hash>/.command.sh` 只有 stub 体**。实测一个 FASTP 任务的 `.command.sh` 共 6 行：首行 `#!/bin/bash -ue`，
>    其后 5 行是 `printf '' | gzip -c > …` 与 `echo … > versions.yml`，里面**没有** `fastp`，也没有 `salmon`。它是
>    「插值后的执行体」没错，但插值的是桩代码。要看真实命令必须真跑（步骤 5），而该路径本机失败——
>    本课的「真实命令长什么样」只能由你在能建环境的机器上取。
>
> **计算纪律**：下载、建环境、拉镜像、生成演示数据在登录节点；fastp、salmon、合并、Quarto 渲染都算计算，
> 一律 `qsub`（本机**没有** `qsub`/`qstat`，SGE 路径本轮未跑）。桩跑（`-stub-run`）不落真实计算，可留登录节点。
> `03_code/`、`06_data/`、`07_envs/` 是只读原材料：要改流程就「`cp` 个人副本 → 改指定行 → `grep` 确认 → 跑副本」。
>
> **本指导不挂任何图、不提图号**：第 23 章的配图与图注归正文与幻灯片，读图以教材为准；被标记暂缓装配的
> 那张缓存图本指导一字不引。模型与字段名留英文，其余说明用中文。

## 0. 本实验对应什么

- **教材**：第 23 章「分析流程工程化」。博士层起读 §23.4.7–§23.4.9（通道语义、任务哈希与缓存、迁移判据与 nf-core）
  与 §23.5.4、§23.5.5、§23.5.8、§23.5.9 四条失效；硕士层 §23.4.1–§23.4.6、§23.5.1–§23.5.3、§23.5.6、§23.5.7 只作对照与
  回指，不另设步骤。
- **学习目标**：LO23-05（含 `meta` 与 `stub:` 的 DSL2 进程、队列/值通道的派生数、用 `-stub-run` 的 10 与 7 验收接线）、
  LO23-06（任务哈希因子、全量失效与误命中、双实验验证缓存）、LO23-07（三条迁移判据与迁移前后的同构验证）。
- **学时**：p07 共 4 学时（2 理论 + 2 实践，`00_design/course_contract.yaml`），本实验是实践环节；作业另建议上机 4–5
  小时、写报告 2 小时（`08_assessment/phd/assignments/p07_workflow_nextflow_practice.md`）。
- **环境**：`ngs_phd_workflow`（`07_envs/conda/env_phd_workflow.yml`）。pin：`nextflow>=23.04,<26.10`（L25）、
  `snakemake=7.28.1`（L27）、`r-base=4.3.1`（L31）、`setuptools<81`（L19），另有 `openjdk`（Nextflow 依赖 JVM）、
  `graphviz`（DAG 渲染）、`quarto`。**Docker / Singularity / Apptainer 不在任何课程 yml 里**（系统级运行时，契约
  `env_exempt_tools`；yml L5–6 头注明写「不走 conda」）。**起点不是零**：默认你已在硕士 m08 写过 rule / input / output /
  wildcards / `rule all` / `expand` / `--use-conda`，并做过 `l1_p07` 的 Q9、Q10（Q10 那个最小 Snakefile 就是步骤 8 的素材）。
- **能验收什么、不能验收什么**（教材 §23.6.2 的两层验收）：工程层——空跑计数、续跑命中、DAG 接线、`work/` 现场、
  报告产物齐全，都能在合成数据上验；生物学层——真实读段的矩阵、TPM、benchmark，本实验**一条都不验**，
  要等你在集群上真跑，本指导不预填数字。

## 1. 实验前检查

- **前置自测**（题号在 `08_assessment/prerequisites/` 逐一存在）：`l0_01_linux` Q5、Q9（远程服务器与集群作业提交——
  步骤 9 的两个调度器都靠它）、Q8（批量与文本处理——步骤 7 读 trace 用得上）、Q10（项目目录组织——步骤 1 与
  步骤 10 的交付树同源）；`l0_03_conda` Q9、Q10（环境快照导出、非交互作业里激活环境——步骤 5 与步骤 10 的
  `env_snapshot.yml`）；`l1_phd` 的 **Q9、Q10**（读一条完整 rule 与手写最小 Snakefile，Q10 的产物是步骤 8 的输入）。
- **建/激活环境并核验工具链**（建环境与下载属允许的 I/O 型任务）。在课程仓库根目录敲：

  ```bash
  conda env create -f 07_envs/conda/env_phd_workflow.yml   # 只需一次
  conda activate ngs_phd_workflow
  nextflow -version          # 记带 version + build 的那一行
  snakemake --version
  dot -V                     # graphviz，步骤 4 的 DAG 渲染要用
  command -v apptainer singularity   # 两个名字命中一个即可；都没有就只走 conda 路径
  command -v mamba conda             # 步骤 5 的前置；两个都没有时别急着跑 -profile conda
  ```

  这条命令在做什么：`nextflow -version` 的 banner 之后有 `version … build …`、`created …`、`cite doi:…` 三行，检查点要的是带 version 与
  build 的那一行。yml L24 注释写「集群实装 26.04.6」，与 pin 差两个小版本，**本实验只在本机 26.04.4 上验过**，集群侧版本请自己记进报告第 1 节，不要照抄任何一处注释。
- **检查点**：`nextflow -version` 带 `version` 的那一行落在 `23.04 ≤ v < 26.10`（本机 26.04.4 build 12445）；`snakemake --version`
  打印 7.28.1（yml L27 的 pin，**不是**本机实测——本机宿主 shell 报 `snakemake: command not found`，它只存在于
  `ngs_phd_workflow` 环境里）；`dot -V` 有版本行；`command -v` 至少打印一个容器运行时路径（本机 `apptainer 1.3.4`
  与 `singularity` 都在），都没有时不要带着这个缺口进步骤 9。
- **出错信号**：`nextflow: command not found` → 环境未激活（教材 §23.5.3 的同族问题，只是发生在登录节点）；
  版本 ≥ 26.10 → §23.5.9，**不要**去改源码迁就新版本，先按 yml 装回区间内的版本；`dot: command not found` →
  graphviz 缺，步骤 4 只会少一张图，不影响计数验收；两个容器名都没有 → 先 `module avail` 看是否要 `module load`，
  仍无则联系助教；**不要** `conda install apptainer`（系统级软件，不属于任何课程 yml）。
- **脚本静态检查**（课程仓库根目录；应无输出、退出码 0、不产生文件）：

  ```bash
  bash -n 06_data/phd/download_phd.sh
  bash -n 06_data/verify_accessions.sh
  PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile 03_code/phd/workflows/bin/merge_quant.py
  PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile 03_code/master/pipelines/scripts/make_demo_data.py
  ```

  本指导现跑结果：两条 `bash -n` 均 rc=0；两个 `py_compile` 均 rc=0（**运行完删掉生成的 `__pycache__`**，否则污染只读
  目录——本指导已删）。`bash -n` 只对 `.sh` 有意义，对 `.nf` 跑它会报 `syntax error near unexpected token`，那是用错了
  检查器；`.nf` 的静态检查用 `nextflow lint .`（步骤 4 尾）。
- **自查演示**（不需要集群，也不需要建 conda 环境；四个脚本各自打印 PASS 计数）。在课程仓库根目录运行：

  ```bash
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch23_queue_channel_starvation.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch23_resume_hash_factors.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch23_stale_output_mtime.py --selftest
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch23_wildcard_ambiguity.py --selftest
  ```

  本指导现跑：**6/6 PASS、6/6 PASS、9/9 PASS、7/7 PASS**，四个脚本 rc 全 0，单次都在秒级、只用标准库。它们对应教材四条机制：队列通道
  饥饿（正确接线 10、误接 7，200/200 次饥饿、值通道 0/200）、任务哈希收集顺序（裸 `collect()` 24 个唯一键、`toSortedList` 1 个、动态因子
  400/400 未命中）、时间戳调度器（无变更执行 0、改阈值后计划作业 0 而 160 细胞中 97 个不同）、通配符歧义（同前缀 500/500、异前缀 0/500）。
  **这些是合成算例，只对各自的生成模型成立**，写进报告必须标「合成算例」。

## 2. 实验数据

本实验**不发新数据**。三条轨道任选其一（默认第一条）：

| 轨道 | 数据 | 规模与口径 | 用途 |
|---|---|---|---|
| 合成演示数据（默认） | `demo/ref/transcripts.fa` + `demo/reads/{CK_1,CK_2,TR_1,TR_2}_{1,2}.fq.gz` | 4 样本、60 条转录本各 1500 bp、每样本 100 bp 读段、质量恒定单字符 `I`（即 Q40）、处理组固定上调 `tx0003`/`tx0007`/`tx0011`、种子 20260829；生成器默认每样本 20000 对，本实验统一降到 **3000** 对以加速（`make_demo_data.py` L26/L30/L90–94，教材 §23.1 与 §23.10） | 离线试跑；只证明链路通，**不具生物学意义**，当结果写进报告是本课要防的第一类错误 |
| p03 子集（真实数据轨道） | `PRJNA661210`（= `GSE157400`）的 18 个样本：日本晴 × {G11 接种, H2O 模拟} × {12, 24, 48} hpi × 3 重复 | 课程取每个 run 前 200 万条读段；登录号在 `06_data/accessions.tsv` L11、L12 登记，设计与取用见 `06_data/phd/README.md` L70、L74、L80、L81 | 把流程切到真实数据的最终对象：只改样本清单与 `--transcriptome`，`.nf` 不动 |
| 你自己的 Snakefile | 你在 m08 或 `l1_p07` Q10 跑通过的流程 | 规模以你的课题为准 | 步骤 8 的转换素材（作业真正要改造的对象） |

- **两处数据缺陷必须写进报告**：① 合成数据无生物学信息（教材 §23.1 原话「合成数据不具任何生物学意义」）；② `PRJNA661210` 的降采样取的是**每个 run 的前 200 万条读段**（文件头部，不是随机样本），FASTQ 开头的读段按 flowcell 位置排序，质量与 GC 分布可能有偏，**绝对丰度类结论不可靠**（`06_data/phd/README.md` p03 节）。
  真实轨道上的一切产物本轮**未跑、未实测**，报告里标 unverified。
- **工作目录**：`/d3/scratch/${USER}/nf/`（纯 ASCII、scratch 配额大）。数据也放纯英文路径下
  （`06_data/phd/README.md` L159 与契约 `delivery.nextflow_ascii_path_required` 同口径）。课程仓库是只读原材料，
  **复制出来改，不要改课程源文件**。
- **真实轨道的样本清单要自己造**：`assets/samples.csv` 里四行指向 `demo/reads/`，是给合成数据用的；p03 子集是
  **单端**数据（每个 run 只有一个 `.fastq.gz`），而本流程的 `FASTP`/`SALMON_QUANT` 读的是 `[fq1, fq2]` 双端元组
  （`main.nf` L65–66、`modules/local/fastp.nf` L26）。**照抄四列双端清单会直接失败**，要改流程或改定量步骤，
  那属于作业之外的改造，写进报告「数据轨选择」一节说明你停在哪一步。

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出文件 / 检查点 / 出错信号（→ 教材 §23.5.x）。命令里的脚本名、参数名、输出文件名
> 与 `03_code/phd/workflows/`、`03_code/master/pipelines/scripts/` 的现版逐字一致（修订时逐个 `grep`，证据在任务回执）。
> **在哪敲命令**：项目根固定为 `/d3/scratch/${USER}/nf`，课程仓库位置用 `${REPO_DIR}` 表示（校内由教师公布）。
> **不要**原样输入 `<尖括号占位符>`——`<` 是 Bash 重定向符，会把命令截成语法错误。每条命令先 `cd` 到项目根：
> `${projectDir}` 指流程文件所在目录，但 `samples.csv` 里的 `demo/reads/...` 是**相对运行目录**的路径
> （`main.nf` L65–66 的 `file(...)` 按当前目录解析）。

### 步骤 0：环境与版本预检

- **目的**：确认引擎版本与工具链，把版本号写进报告第 1 节——它决定语法严格程度（教材 §23.5.9）。
- **命令**（登录节点）：

  ```bash
  conda activate ngs_phd_workflow
  nextflow -version            # 记带 version 与 build 的那一行（banner 之后）
  snakemake --version
  dot -V
  command -v apptainer singularity
  ```

- **产出文件**：无（版本号抄进 `report.pdf` 第 1 节与 `env_snapshot.yml`）。
- **检查点**：版本落在 yml 区间 `>=23.04,<26.10`（`07_envs/conda/env_phd_workflow.yml` L25）；
  本机实测 26.04.4 build 12445。`snakemake --version` = 7.28.1（yml L27 pin）。`dot -V` 有版本行。
- **出错信号**：版本 ≥ 26.10 → §23.5.9：新版本会拒绝旧语法，报错指向代码而不指向版本；
  处置是装回区间内版本，**不是改流程**。容器运行时一个都没有 → §23.5.5 的边界问题，先别走容器轨。

### 步骤 1：复制到纯 ASCII 路径

- **目的**：绕开非 ASCII 路径导致的 `Invalid include source`，并建立可修改的个人副本（后续步骤要改两处文件）。
- **命令**（登录节点）：

  ```bash
  mkdir -p /d3/scratch/${USER}
  cp -r "${REPO_DIR}/03_code/phd/workflows" /d3/scratch/${USER}/nf
  cd /d3/scratch/${USER}/nf
  pwd
  ls main.nf nextflow.config conf modules/local subworkflows/local bin assets
  ```

- **产出文件**：`/d3/scratch/${USER}/nf/`（个人项目，含 `main.nf`、`nextflow.config`、`conf/`、
  `modules/local/`、`subworkflows/local/`、`bin/merge_quant.py`、`assets/samples.csv`）。
- **检查点**：`pwd` 输出里没有任何中文；`main.nf` L22–23 两条 `include` 分别指向
  `./subworkflows/local/quantify.nf` 与 `./modules/local/merge_counts.nf`；`quantify.nf` L5–7 三条
  `include` 指向 `modules/local/` 的三个模块。
- **出错信号**：`Invalid include source` → 两种成因（路径含非 ASCII / 目标文件确实不存在）。
  实测在 `.../中文_nf/` 下属 **5 条**（`main.nf:22`、`main.nf:23`、`quantify.nf:5`、`:6`、`:7`），退出码非 0；
  同一份项目在 ASCII 路径下 `completed=10`。**不是** `.nf` 后缀的错（去掉后缀实测仍 10），
  也不是模块写错——回 §23.5.8，把整个项目与数据一起搬到纯英文路径。

### 步骤 2：生成合成演示数据

- **目的**：造一份可离线复现的输入，使后面所有计数都不依赖外网与真实数据。
- **命令**（登录节点；在项目根 `/d3/scratch/${USER}/nf` 敲，**生成器在课程仓库里，不在被复制的项目里**）：

  ```bash
  python3 "${REPO_DIR}/03_code/master/pipelines/scripts/make_demo_data.py" \
      --outdir demo --reads-per-sample 3000
  ```

  这条命令在做什么：写一个 60 条转录本的 FASTA 与 4 个样本各一对 FASTQ。参数名与默认值（`--outdir` 默认
  `data`、`--n-transcripts` 60、`--transcript-length` 1500、`--reads-per-sample` 20000、`--read-length` 100）
  直查生成器 L90–94；本步骤把每样本读段数降到 3000，是**指定的非默认值**。生成器只有一个固定种子
  （L26 `SEED = 20260829`、L102 `set_seeds(SEED)`），同一台机器上重复生成内容一致。
- **产出文件**：`demo/ref/transcripts.fa`（实测 **60 条**序列、序列长 1500）、`demo/reads/CK_1_1.fq.gz` …
  `TR_2_2.fq.gz` 共 **8 个**（实测每个 3000 条读段，`zcat | wc -l` = 12000 行）。
- **检查点**：`grep -c '>' demo/ref/transcripts.fa` = 60；`ls demo/reads/*.fq.gz | wc -l` = 8；每个文件的
  读段数与 `--reads-per-sample` 一致。`conf/test.config` L6 的 `transcriptome = "${projectDir}/demo/ref/transcripts.fa"`
  指向的正是这个位置。
- **出错信号**：`can't open file .../03_code/master/...` → 你在项目根用了相对路径，而生成器不在项目内
  （`conf/test.config` L2 的用法注释也是同一形式，照抄会踩）；把 `--outdir` 指到别处而没覆盖 `--transcriptome`
  → 流程第一步就报 `No such file or directory`，回 §23.5.7 先 `ls` 再查基准。

### 步骤 3：桩跑验收接线（`completed=10`）

- **目的**：在没装任何生信软件的节点上验证 DAG 与通道接线，这是本讲第一个验收点。
- **命令**（项目根；登录节点可跑）：

  ```bash
  nextflow run . -stub-run -profile test
  ```

  接线由三处决定：`main.nf` L54–67 的样本队列通道（`Channel.fromPath(samplesheet)` → `splitCsv` → `map` 出
  `[meta, [fq1, fq2]]`）、L72 的 `Channel.value( file(params.transcriptome) )`（值通道）、`quantify.nf` L32 的
  `.first()`（零成本保险）、`main.nf` L74 的 `QUANTIFY( ch_reads, ch_transcriptome )`，以及 L79–83 的排序 + `MERGE_COUNTS`。
- **产出文件**：`results_test/{clean,qc,index,quant,counts,pipeline_info}`；`pipeline_info/` 下四件 `trace.txt`、`report.html`、
  `timeline.html`、`dag.html`（`nextflow.config` L87–90 默认全开），另有 `versions.yml`（`main.nf` L86–91 的 `collectFile`）。
- **检查点**：末行 `[SUCCESS] completed=10 failed=0 cached=0`。这个 10 是手算：4 个 FASTP + 1 个 SALMON_INDEX
  + 4 个 SALMON_QUANT + 1 个 MERGE_COUNTS = `4+1+4+1=10`（教材 §23.4.7）；桩跑复现同值。**它只证明接线，
  不证明业务数值。** 首行出现的 `WARN: The operator 'first' is useless when applied to a value channel`
  是**正常的**，说明上游 `Channel.value` 写对了（`quantify.nf` L22–31 的注释就是这条判据）。
- **出错信号**：
  - `completed=7` → 索引误走队列通道，且 `.first()` 被去掉（`main.nf` L72 改成 `Channel.fromPath`、
    `quantify.nf` L32 改成不带 `.first()`）。实测 7 次清空重跑都是 `completed=7`、终态 `[SUCCESS]`、只产 1 份
    `quant.sf`；幸存样本一轮三次为 CK_2 / CK_1 / CK_2，另一轮四连为 CK_1 / CK_2 / TR_1 / TR_2——四个样本都当过幸存者，
    **每次都不固定，别把某个样本名当稳定判据**。`7` 的手算是 `4+1+1+1=7`（教材 §23.4.7）。
  - `completed=4` → 样本清单只读到一行。实测把 `assets/samples.csv` 删到只剩表头 + 1 行，得 `completed=4`。
    **这与 7 不是同一机制**，别合并成一个「通道坏了」（教材 §23.9 答案 3②）。
  - 两种都可能以 `[SUCCESS]` 收尾，**没有报错可查**——判据是「任务数与样本数对不上」，不是日志里找 error（机制见 §23.4.7 通道语义与 §23.5.4 的「静默给出旧结果」）。

### 步骤 4：DAG 与模块边界审阅

- **目的**：把接线画成图，看清 `QUANTIFY` 内部三个 process 谁接谁，以及样本通道与 `MERGE_COUNTS` 的汇聚位置。
- **命令**（项目根）：

  ```bash
  nextflow run . -stub-run -profile test -with-dag dag.html
  ls -l dag.html results_test/pipeline_info/dag.html
  md5sum dag.html results_test/pipeline_info/dag.html
  nextflow lint .
  ```

  这条命令在做什么：`-with-dag` 只是**再写一份** DAG，不是「生成 DAG」。`nextflow.config` L90 已把 dag 默认写到
  `${params.outdir}/pipeline_info/dag.html`，命令行再指名会在当前目录另写一份。
- **产出文件**：`dag.html`（当前目录）与 `results_test/pipeline_info/dag.html`（默认位置）；`nextflow lint .`
  的终端输出。
- **检查点**：两份 dag 的 md5 **相同**（实测同为 `fbe9ba5f1309a3f0efb3067a2b6da28c`），别以为文件没生成。**图上每个 process 只出现一次**——
  实测 `dag.html` 里 `FASTP`、`SALMON_INDEX`、`SALMON_QUANT`、`MERGE_COUNTS` 各出现 1 次，且 `QUANTIFY` 被画成一个子图框：
  这是**模板图**，节点数是 process 数（4），**不是实例数**（10）。所以「4 个 FASTP」只能从 `completed=10` 的四项分解里读出来，
  别指望在图上数出 10 个节点。图上该见的连线是 `v7 --> v8 --> v9`（`SALMON_INDEX` 经一个中转点接到 `SALMON_QUANT`）与
  `v0 --> v1 --> v3`（样本队列通道接 `FASTP`）。`nextflow lint .` 实测 0 error、6 warning（`Channel` 构造器与闭包隐式参数两类弃用），
  **warning 不是失败**，写法与课程流程一致即可；报告里可各记一条，作为「引擎在演进」的现场证据。
- **出错信号**：把图上节点数当实例数 → 模板图只有 4 个 process，`completed=7` 在图上**看不出来**，回步骤 3 的计数判据；
  两份 md5 不同 → 你改了参数或改了清单，两次不是同一个键（下面步骤 6 会讲这个判据，机制见 §23.5.4）；
  图上有节点而 `completed=` 明显少于四类任务之和 → 先怀疑样本清单没读全，回步骤 3 的 `completed=4` 分支（§23.5.4 的「静默偏差」）。

### 步骤 5：真实计算（`-profile test,conda` 或容器）

- **目的**：把桩换掉，真跑 fastp 与 salmon，得到有数值意义的中间产物。
- **命令**（项目根；首次建环境在登录节点，算力走 `qsub` 或交给 executor）：

  ```bash
  command -v mamba conda            # 先看这一步，别跳过
  grep -n "useMamba" nextflow.config
  nextflow run . -profile test,conda
  ```

  没 mamba 时改副本再跑（**改的是个人副本，不是课程源文件**）：

  ```bash
  sed -i 's/conda.useMamba      = true/conda.useMamba      = false/' nextflow.config
  grep -n "useMamba" nextflow.config    # 期望看到 = false
  command -v conda                      # 这一步不通过就别重跑，见下方出错信号
  nextflow run . -profile test,conda
  ```

- **产出文件**：`results_test/{clean,qc,index,quant,counts}` 的实体产物；`.conda_cache/`（`nextflow.config` L52 指定）；
  `versions.yml` 里应是真实版本。
- **检查点**：`versions.yml` 记到 `fastp 0.23.4` 与 `salmon 1.10.3`（与各模块 `conda` 串一致：`fastp.nf` L8
  `bioconda::fastp=0.23.4`、`salmon_index.nf` L7 与 `salmon_quant.nf` L7 `bioconda::salmon=1.10.3`、`merge_counts.nf`
  L9 `conda-forge::python=3.10`）；`quant/` 下每样本一份 `<sample>.quant.sf` 与一个 `<sample>/quant.sf`
  （`salmon_quant.nf` L30 的 `cp` 就是为保留样本身份）。**真实保留率、检测到的转录本数、TPM 一律不预填**——合成数据上
  这些数没有科学含义，真实数据轨未跑（标 unverified）。
- **出错信号**：`Failed to create Conda environment … status : 127 … mamba: command not found` → `useMamba=true` 而机器
  上没 mamba（教材 §23.4.9 的未核实项）；把 `useMamba` 置 `false`。**改完仍失败**时看第二行：实测本机再报
  `status : 127` + `bash: line 1: conda: command not found`，说明连 conda 都没有——先按 §1 建环境，或改走容器轨
  `nextflow run . -profile test,singularity`（本机桩跑 rc=0、`completed=10`，但**桩跑不拉镜像**，真跑要在登录节点先拉好，
  未实测）。作业内 `command not found`（salmon/fastp）而登录节点正常 → §23.5.3：环境没进作业，不是软件没装；SGE 要 `-V`
  才继承，SLURM 要 `--export=NONE` 才不继承（`conf/sge.config` L8、`conf/slurm.config` L7 正是这两种写法）。

### 步骤 6：缓存三连（本讲核心实验）

- **目的**：用三次运行把「什么进任务哈希、什么不进」变成可记录的计数。
- **命令**（项目根；三次逐条记数字）：

  ```bash
  nextflow run . -stub-run -profile test                            # ① 基线
  nextflow run . -stub-run -profile test -resume                   # ② 不改任何东西续跑
  rm -rf results_test/quant/CK_1*                                  # 删一个已发布的中间产物
  nextflow run . -stub-run -profile test -resume                   # ③ 删发布目录后续跑
  nextflow run . -stub-run -profile test -resume --salmon_kmer 25  # ④ 改只被索引+定量引用的参数
  nextflow run . -stub-run -profile test -resume --fastp_qual 30   # ⑤ 对照：改只被质控引用的参数
  ```

  为什么用 `-stub-run`：本机建不了 conda 环境（步骤 5），而缓存判据与是否桩跑无关——哈希算的是脚本插值文本、输入指纹、
  被引用的参数与容器/conda 声明（教材 §23.4.8）。**计数本身可在桩跑上复现**，真实数据上的产物不行。
- **产出文件**：五次运行的完整终端输出（作业要求落成 `run_logs/{stub_run,resume_1,resume_2,resume_3}.log`）；
  `run_counts.tsv`（每个数字配一句解释）。
- **检查点**（本指导逐条实测，Nextflow 26.04.4、ASCII 路径、Stub、合成数据）：

  | 运行 | 实测计数 | 可写进报告的解释 |
  |---|---|---|
  | ① 基线 | `completed=10 cached=0` | 首次运行，`work/` 里没有可复用的哈希 |
  | ② 无改动 `-resume` | `completed=0 cached=10` | 键没变，全命中（教材 §23.4.8 的验收动作） |
  | ③ 删 `results_test/quant/CK_1*` 后 `-resume` | `completed=0 cached=10` | 删**发布目录**不让缓存失效；`-resume` 把发布目录完整重建（实测重建后 `quant/` 四份 `.quant.sf` 与四个子目录都在） |
  | ④ `--salmon_kmer 25` | `completed=6 cached=4` | `salmon_index.nf` L22 插值了 `${params.salmon_kmer}`：1 索引 + 4 定量 + 1 合并重算，4 个 FASTP 命中（`6 = 1+4+1`，教材 §23.4.8、§23.9 答案 10③） |
  | ⑤ `--fastp_qual 30` | `completed=9 cached=1` | `fastp.nf` L30 插值了 `${params.fastp_qual}`：4 个 FASTP 脚本文本变而重算，其产物变又让 4 个定量与 1 个合并的**输入指纹**变而连带重算，只有索引命中（`9 = 4+4+1`） |

  **6/4 只属于 `--salmon_kmer`，9/1 只属于 `--fastp_qual`**。把 6/4 写成「参数微调」而不点名参数，会让读者以为
  那是 fastp 的结果——这是教材已纠正的旧口径。**条件可用的第三例**：`--salmon_libtype IU` 实测 `completed=5
  cached=5`（`salmon_quant.nf` L23 插值 `${params.salmon_libtype}`，只影响 4 个定量 + 1 个合并）；教材未收这个数，
  只作「参数被脚本引用的范围决定重算面」的旁证，**不作验收标准**。**加分实验（条件可用）**：`touch
  demo/reads/CK_1_1.fq.gz` 后 `-resume` → 实测 `completed=3 cached=7`（FASTP CK_1 + QUANT CK_1 + MERGE）。它证明
  默认输入指纹含 mtime，但**依赖文件系统时间精度**，不是能稳定复现的检查点，也不许写成「一定失效/一定不失效」。
- **出错信号**：② 得 `cached=0` → 先排除「两次本来就不是同一个键」：`nohup`/`qsub` 换目录、清单被重写、脚本里注入
  了 `$RANDOM` 或时间戳、`bin/` 里的脚本改过、镜像/conda 声明变过（§23.5.4）。④ 或 ⑤ 得 `10/0`（全重算）→ 汇总
  步骤用了无序 `collect()`（课程流程用 `toSortedList`，`main.nf` L79–83），或脚本插值了动态因子。删过 `work/` 或
  `.nextflow/` → 键库消失，重新全量算一遍是**正常行为**，不是缓存坏了（实测删 `work/` 后 `-resume` 仍是 `10/0`）。

### 步骤 7：`work/` 现场取证与资源判读

- **目的**：养成「先下潜到任务目录，再回头改代码」的动作；读 trace 判资源。
- **命令**（项目根）：

  ```bash
  grep -n "Work dir" .nextflow.log | tail -1        # 或从报错信息里抄 Work dir:
  nextflow log                                     # 先列出这次会话的 run 名（第 3 列）
  nextflow log <run_name> -f workDir,name | head -5 # 该 run 每个任务的目录与名字
  nextflow log <run_name> -f hash,name,status        # 任务的短哈希与终态
  cd work/<两位>/<其余>                             # 换成上一条打印的路径
  ls -la
  cat .command.sh
  cat .exitcode
  cat results_test/pipeline_info/trace.txt
  ```

  这条命令在做什么：`.command.sh` 是**插值后**的执行体，`.command.run` 是引擎的包装脚本，`.command.err`/`.command.out` 是
  两条流的原样捕获，`.exitcode` 是终态码，`.command.trace` 是该任务的度量。**`-f` 只在给了 run 名之后才按任务展开**：
  不带 run 名时 `nextflow log -f workDir,name` 仍只打印 run 列表（本机 26.04.4 实测），别把两行的输出搞混。
- **产出文件**：`work_dir_forensics.md`（作业要求：贴出**一个任务**的 `.command.sh` 并说明它与你以为的差别）；
  `artifacts/trace.txt`。
- **检查点**：一个任务目录里实测有 **7 个** `.command.*` 类文件加上 `.exitcode`（`.command.begin`、`.command.err`、
  `.command.log`、`.command.out`、`.command.run`、`.command.sh`、`.command.trace`），产物与输入并列存放。
  `trace.txt` 的**表头 14 列**（实测：`task_id hash native_id name status exit submit duration realtime %cpu peak_rss
  peak_vmem rchar wchar`），一行一个任务。**桩跑下 `.command.sh` 只有 stub 体**（实测 6 行：首行 `#!/bin/bash -ue`，其后 5 行含 `printf '' | gzip -c > …`），没有 `fastp`、没有 `salmon`——这是本步骤最容易误判处，报告里要写明「我贴的是桩体」或「我在能建环境的机器上真跑过」。
  退出码读法：`137 = 128+9`（SIGKILL，常见于超 cgroup 内存被 OOM 终止）、`143 = 128+15`（SIGTERM，常见于墙钟超时，
  教材 §23.4.8）。申请内存按 `peak_rss` 的 **1.3 至 2 倍**，不用 `peak_vmem`（含未使用的地址空间）。
- **出错信号**：把 `peak_vmem` 当内存依据 → 按教材 §23.4.5 的算例 `48000/3200 = 15`，会浪费十几倍配额；`.exitcode`
  是 0 却产出为空 → 看 `.command.out`/`.command.err`，多数是桩跑（空文件是设计好的占位），不是真跑失败；
  `.command.sh` 里没看到你以为的命令而退出码 0 → 先确认这次运行到底有没有 `-stub-run`；空产物配 0 退出码这条判据
  在 §23.5.7 的后果段（`touch` 造空文件 → 下游空结果）与 §23.5.4（把旧结果当新结果）里是同一族。

### 步骤 8：AI 转换核查（对应教材的 AI 使用与验证要求）

- **目的**：把「AI 给的语法正确、语义已变」变成可判定的数字验收，而不是读代码凭感觉。
- **命令**（无固定命令；动作是三次交互 + 一次本地复核）：

  ```bash
  nextflow -version | grep -m1 'version'   # 把这一行原样贴给模型：语法严格程度取决于它（末尾是 build 号）
  cat Snakefile                      # 你已跑通的规则原文，与版本行一起贴给模型
  nextflow lint .                    # AI 给回代码后先静态跑一遍
  nextflow run . -stub-run -profile test   # 再接一次线：数 completed=
  ```

  转换的目标形态：扁平化到 `modules/local/`、参数全走 `params`、每个 process 带 `stub:`。核查五条（与作业 ④ 的
  五条同构）：① 通道消费语义（1 份参考/索引是否来自值通道或经 `.first()`/`.collect()`）；② 并发行为（`completed=`
  与「样本数 × 步骤数 + 汇总」对不对）；③ `-resume` 缓存（连跑两次第二次是否全 `cached`）；④ 资源声明（`label`/`cpus`
  有没有丢、shell 里是不是 `${task.cpus}` 而不是写死数字）；⑤ 结果一致（同一份小数据两版都跑，`md5sum` 逐文件比对）。
- **产出文件**：`results/ai_audit.tsv`（五条逐条结论，含「AI 的原话 / 我的判断 / 证据」三列）；`paradigm_comparison.md`
  （Snakefile 与 `main.nf` 三处等价但写法不同：驱动方向、样本身份、参数外置）；`ai_logs/prompt_and_reply.md`
  （原文往返，必须含你告诉它的版本号）。
- **检查点**：五条各自有**命令级证据**，不是「看起来没问题」。`completed=` 是最硬的那条：把「索引直接接给逐样本
  process」这种 AI 必错写法，用 `completed=7` 抓出来（步骤 3 的分支）；把「汇总用 `collect()`」用「第二次 `-resume`
  不是全命中」抓出来（步骤 6 的 ②）。模型给的任何数字都**不得直接采信**，要自己跑出来——报告里两种数字要能区分开。
- **出错信号**：AI 输出「全部通过」而你只有截图 → 本栏按未完成计；AI 把 `SALMON_INDEX.out.index`（队列通道）直接
  接给 `SALMON_QUANT` → 不报错、`completed=7`，这就是第 1 条必错项；AI 把 `meta` 丢掉只留文件名 → 下游 `condition`
  丢失，「样本身份能否携带协变量」这一课等于没做（教材 §23.4.7 的 `meta` 段落）；这三条在失效归口上属 §23.5.4
  的「怎样察觉」五条与「误命中不报错」。

### 步骤 9：集群提交（可选加分，不单独计权重）

- **目的**：看引擎自己在提交、排队、回收，确认 `clusterOptions` 的两种写法各解决什么。
- **命令**（登录节点；**队列名必须实查，不预填**）：

  ```bash
  sinfo -o "%P"                 # SLURM：本机实测只有 compute* / highmem / debug
  qconf -spl                    # SGE：并行环境名，conf/sge.config L5 的 smp 要与之对得上
  nextflow run . -stub-run -profile test,singularity,slurm --queue <实查到的分区>
  nextflow run . -stub-run -profile test,singularity,sge   --queue <实查到的队列>
  squeue -u ${USER}             # 或 qstat -u ${USER}
  ```

- **产出文件**：`squeue`/`qstat` 的一次输出；作业脚本里应能 `grep` 到 `--export=NONE`（SLURM）或 `-S /bin/bash`（SGE）。
- **检查点**：已实测与未验证要分清。**已实测（SLURM 桩跑）**：`--queue compute`（`sinfo -h -o "%P" | head -1` 去掉 `*`）
  跑通，`completed=10 failed=0`；`.nextflow.log` 里 **10 条** `Submitted process > …`、10 条 `Task completed`；
  任务 `.command.run` 头带 `#SBATCH -p compute`、`#SBATCH --export=NONE`、`#SBATCH -c 4`、`#SBATCH --mem 8192M`、
  `#SBATCH -t 02:00:00`（后三项来自 `conf/base.config` 的资源阶梯），这说明「作业不继承登录 shell 环境」落在哪一行。
  **已实测（失败路径）**：不给 `--queue` 时默认 `cpu` 不存在，报 `sbatch: error: invalid partition specified: cpu …
  Batch job submission failed`，`failed=1`。**仍未验证**：SGE 路径（本机没有 `qsub`/`qstat`/`qconf`，一条没跑）；
  桩跑不拉镜像（`singularity` 段只被 profile 接受）；真实读段与 18 样本全链。`squeue -u ${USER}` 本机只回了表头
  （作业跑得太快），这条要贴你自己那次非空输出。
- **出错信号**：作业内 `command not found` → §23.5.3，分调度器处置（SGE 补 `-V`、SLURM 查 `--export`，见
  `conf/sge.config` L8 与 `conf/slurm.config` L7）；`Invalid partition name specified` → 队列名不存在，回
  `sinfo -o "%P"` 实查，**别改流程代码**；镜像拉不下来 → 登录节点先拉好，计算节点常无外网。

### 步骤 10：交付与自查

- **目的**：把工程层证据打包成可复核的目录，并核对交付树与作业规格一致。
- **命令**（项目根；打包前先跑一遍自查）：

  ```bash
  ls results_test/pipeline_info/{trace.txt,report.html,timeline.html,dag.html}
  md5sum dag.html results_test/pipeline_info/dag.html     # 两份同名文件，别把两个目录的都交上去
  grep -c "" results_test/pipeline_info/trace.txt          # 行数 = 任务数 + 表头
  conda env export --from-history > env_snapshot.yml       # 环境快照，与流程产物无关
  grep -n "completed=\|cached=" run_logs/*.log             # 每个数字都要能在日志里 grep 到
  du -sh results_test work                                   # 判断哪些不进 zip
  ```

- **产出文件**：`学号_姓名_p07.zip`（≤ 50 MB，**不打包 `work/`**）。目录按作业 ②：
  `report.pdf`（≤ 6 页）、`run_logs/{stub_run,resume_1,resume_2,resume_3}.log` 与 `run_counts.tsv`、
  `artifacts/{dag.html,trace.txt,report.html}`、`work_dir_forensics.md`、`paradigm_comparison.md`、
  `ai_logs/prompt_and_reply.md`、`results/ai_audit.tsv`、`env_snapshot.yml`。
- **检查点**：`run_counts.tsv` 的每一个 `completed=`/`cached=` 都能在 `run_logs/` 的原始输出里
  `grep` 到，且每个数都配了机制解释（10/0、0/10、9/1 与 6/4 四种情形各对应哪条规则）；
  `env_snapshot.yml` 由 `conda env export --from-history` 单独导出，**不是流程产物**；
  三件 artifacts 都来自 `results_test/pipeline_info/`（`nextflow.config` L87–90 的默认位置），
  而 `-with-dag dag.html` 还会在当前目录再写一份（md5 与默认那份相同，实测 `fbe9ba5f…`）
  ——**交一个就行，别交两个不同目录的同名文件**。
- **出错信号**：`run_counts.tsv` 里出现「参数微调 → 6/4」这类不点名参数的写法 → 评分点要求
  「每个数字都有解释」，这种解释等于没有（这正是 §23.5.4「误命中不报错」要防的写法）；日志被编辑过
  （截断、拼接） → 按学术不端口径处理（作业 ⑤ 诚信条）；把 `work/` 打进 zip → 轻易超 50 MB，且哈希目录
  换机器无意义（§23.5.8 的交付目录问题）；报告里贴截图而日志缺 → 助教 `grep` 不到数字，按未完成计。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填你的结果。判据列注明来源：「手算」＝教材给算式可在纸上复核；「配置事实」＝
> `nextflow.config`/`conf/*.config` 的现读值；「桩跑实测」＝本指导在 26.04.4 上现跑的计数（命令与退出码在回执里）。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 0 | `nextflow` 版本 + build；`snakemake`、`dot` 版本 | 版本号 | | 区间 `>=23.04,<26.10`（yml L25），本机 26.04.4 build 12445；snakemake 7.28.1（yml L27 pin） |
| 1 | 路径是否纯 ASCII | Y/N | | `pwd` 无中文；反例实测 5 条 `Invalid include source` |
| 2 | 转录本数 × 样本数 × 每样本读段对 | 个 | | 60 × 4 × 3000（生成器参数 + 实测计数）；默认 20000，改了要写明 |
| 3 | `-stub-run` 的 `completed=` 与四项分解 | 个 | | 手算 `4+1+4+1=10`（§23.4.7）；桩跑实测同值 |
| 3 | 误接索引通道后的 `completed=` 与幸存样本 | 个 / 样本名 | | 手算 `4+1+1+1=7`；实测 7 次皆 7，幸存样本不固定 |
| 3 | 清单只剩一行时的 `completed=` | 个 | | 实测 4；与 7 不是同一机制 |
| 4 | 图上 process 数与两份 dag 的 md5 | 个 / 文本 | | 模板图 4 个 process 各 1 个节点（实例数看 `completed=10`）；两份 md5 实测相同 |
| 5 | `versions.yml` 里的 fastp/salmon 版本 | 版本号 | | 0.23.4 / 1.10.3（模块 `conda` 串）；真实保留率 unverified |
| 6 | 五次运行的 `completed=`/`cached=` | 个 | | 10/0、0/10、0/10、6/4、9/1（桩跑实测）；5/5 与 3/7 只作旁证 |
| 6 | 「为什么 6/4 不是 fastp」的一句话 | 文字 | | `salmon_index.nf` L22 插值 kmer；fastp 侧实测 9/1 |
| 7 | 一个任务的 `.command.*` 清单与 `.exitcode` | 个 / 码 | | 实测 7 个 `.command.*` + `.exitcode`；桩体不含真实命令 |
| 7 | `trace.txt` 列数与你选的资源列 | 列 / 数值 | | 实测 14 列；申请内存 = `peak_rss` × 1.3–2（§23.4.5） |
| 8 | 五条 AI 核查的结论与证据 | 条 | | 第 1 条用 `completed=7` 抓；第 3 条用第二次 `-resume` 抓 |
| 9 | 集群队列名与 `squeue`/`qstat` 一次输出 | 文本 | | 本机 SLURM 桩跑 `--queue compute` 得 `completed=10`（作业脚本含 `#SBATCH --export=NONE`）；SGE 未跑，`cpu` 分区不存在 |

## 5. 失效条件对照（教材 §23.5 九条：本实验里在哪一步、看什么能察觉）

1. **通配符歧义让规则抓错输入（§23.5.1）**｜不在本实验路径上（本流程用 `meta` 而非通配符），只在步骤 8 的转换前后对照里
   出现。查：转成 Nextflow 后若仍靠文件名拼身份，`meta` 就白带了；合成复现 `demos/ch23_wildcard_ambiguity.py --selftest`（500/500、0/500）。
2. **改了参数、输出已存在，下游不重建（§23.5.2）**｜步骤 6 的 ④⑤。查：改参后 `cached=` 是否只覆盖引用该参数的任务及其
   下游；本流程的对照是 9/1（fastp 侧）与 6/4（kmer 侧）。若改参后仍 `10/0` 而你以为只改了一处，回步骤 6 的解释。
3. **计算节点找不到命令，登录节点一切正常（§23.5.3）**｜步骤 5、步骤 9。查：作业日志里 `salmon: command not found` /
   `fastp: command not found`；登录节点有、作业里没有即环境没进作业。SGE 要 `-V`、SLURM 要 `--export=NONE`
   （`conf/sge.config` L8、`conf/slurm.config` L7）。
4. **缓存全量失效与误命中（§23.5.4）**｜步骤 6。查：不改任何东西连跑两次（实测 `0/10`）；未全命中先排除「两次本来不是
   同一个键」（换目录、清单被重写、注入 `$RANDOM`、`bin/` 改过、容器/conda 声明变过），再判缓存。误命中更危险：脚本读了
   不在 `input` 里声明的文件，内容变而键不变（§23.4.8 末段），查「每个读入的文件是否都在 `input`」。
5. **容器与 conda 的边界混淆（§23.5.5）**｜步骤 5。查：报错在**求解期**（`UnsatisfiableError` 一类）还是**运行期**
   （`GLIBC_2.29 not found` 一类），两者都不指向你的代码；容器换整段用户态、conda 换解释器与用户态依赖包，常规 conda
   构建不替换宿主 glibc。镜像写死 tag 只是下限，长期存档要记 `@sha256` 摘要。
6. **目录锁与元数据误删（§23.5.6）**｜步骤 6 的重跑。查：`Directory cannot be locked` 时先 `ps`/`squeue` 确认没有别的实例，
   再 `nextflow clean -f <run>` 清**指定运行**；永远不用 `rm -rf .nextflow/` 或 `rm -rf work/` 当解锁手段（实测删 `work/`
   的后果是全量重算，`10/0`）。
7. **找不到起点：输入缺失与路径基准（§23.5.7）**｜步骤 2、步骤 3。查：`No such file or directory` 先 `ls` 看文件真在不在，
   再查当前目录——`samples.csv` 里的 `demo/reads/...` 是相对**运行目录**（`main.nf` L65–66 的 `file(...)`），不是相对
   `main.nf`。用 `touch` 造空输入糊弄，流程会跑出空结果。
8. **交付目录的死链与非 ASCII 路径（§23.5.8）**｜步骤 1、步骤 10。查：交付前在目标机器上打开发布目录，`ls -l` 里若是符号
   链接就是死链风险；本流程 `nextflow.config` L26 已设 `publish_mode = 'copy'`（有意选择，别改成 `symlink`）。路径侧：
   `Invalid include source` 只认两种成因，非 ASCII 与目标文件真不存在。
9. **引擎版本漂移让流程编译失败（§23.5.9）**｜步骤 0。查：`nextflow -version` 落在 `>=23.04,<26.10` 内（yml L25 已钉上限）；
   升级前后各跑一次桩流程与一次 `-resume`，看计数（10）与命中（10）是否与升级前一致；本流程 `main.nf` L45 已用 `exit 0`
   而不是 `return`，可在文件里现场对照这句注释。

## 6. 思考题（教材 §23.7 博士层习题 7–11，不给答案）

1. 某进程两个输入：A 是 4 个样本的队列通道，B 是 1 份参考的队列通道。① 派生几个任务？② B 改成值通道后派生数如何变化？
   ③ 参考误走队列通道时，终态与产物长什么样、任务计数是多少？④ 用 `-stub-run` 怎么在一次运行里判断接线错了；连跑三次，
   幸存的样本是否固定？（§23.7 习题 7 → §23.4.7；步骤 3 就是这道题的现场）
2. 你要验证一个流程的缓存行为。① 设计三步实验：基线、删发布目录后续跑、改一个只影响上游的参数后续跑，分别预期什么计数？
   ② 若第二次续跑全量重算，列出四条排查方向与对应检查，并说明为什么这四条不能按「常见程度」排成名次逐条试？③ 若改参后
   只有该参数引用的任务重跑、其余命中，这算正常还是异常？（§23.7 习题 8 → §23.4.8、§23.5.4）
3. 某流程每次续跑都全量重算，作者说「缓存坏了」。① 列出至少三条机制。② 分界依据是什么：哪些改动落在流程写法一侧，
   哪些落在环境与操作一侧？③ 给出一个能在 5 分钟内缩小范围的实验，并说明它能区分什么、不能区分什么。（§23.7 习题 9 → §23.5.4）
4. 你要论证是否把一条成熟流程从 Snakemake 迁移到 Nextflow。① 写出三条判据，只有一条成立时该怎么做？② 设计迁移前后的
   同构验证方案（至少两轨）。③ 迁移后第一次续跑显示 `completed=6 cached=4`，解释这个分布的来源（哪一类任务重算、
   哪一类命中、为什么）。（§23.7 习题 10 → §23.4.8、§23.4.9）
5. 一条规则读了一个不在 `input` 声明的参考文件。① 这个文件变了会发生什么？② 为什么这类失效比「全量重算」更危险？
   ③ 写出两条能在代码审查阶段发现它的检查，并在本流程里指出一个最可能被悄悄读入而没声明的位置。（§23.7 习题 11 → §23.5.4、§23.4.8）

## 7. 提交物

- **对应作业**：`08_assessment/phd/assignments/p07_workflow_nextflow_practice.md`，文件名 `学号_姓名_p07.zip`
  （≤ 50 MB，**不打包 `work/`**）。评分维度：完成度与结果正确性 50 / 判断与讨论质量 28 / AI 使用与验证记录 10 /
  报告质量 12；权重占课程总成绩 3%。目录结构与步骤 10 的「产出文件」一致（`report.pdf` ≤ 6 页、`run_logs/`、
  `artifacts/`、`work_dir_forensics.md`、`paradigm_comparison.md`、`ai_logs/`、`results/`、`env_snapshot.yml`）。
- **报告五节**（与作业 ② 的表一致，顺序别改）：① 环境与路径约束（实际版本号、纯英文路径的处置）；② 空跑与 DAG
  （`completed=10` 的四项分解、对照 `quantify.nf` 说接线）；③ 缓存三连（三次 `-resume` 的数字与**每个**数字的解释，
  特别是「索引为什么仍命中」）；④ `work/` 取证与资源（`.command.sh` 的插值结果、`trace.txt` 的 `peak_rss` 与 `%cpu`
  判读）；⑤ 范式对照（三处等价但写法不同的地方，加通道派生任务数的推演）。
- **三处硬要求**（缺一按未完成计）：① 日志是原始输出、未编辑，`completed=`/`cached=` 能 `grep` 到；② `work_dir_forensics.md` 贴的
  `.command.sh` 要说明是桩体还是真跑体（桩体不含真实命令）；③ `env_snapshot.yml` 用 `conda env export --from-history` 导出，不是流程产物。
- **一处口径提醒**：作业 ② 要求 `resume_3.log` 是「改 `--fastp_qual 30` 后 `-resume`」。本实验把 `--fastp_qual 30`
  （→ 9/1）与 `--salmon_kmer 25`（→ 6/4）分开写，是因为教材只把 6/4 归给 kmer。只跑 fastp 那条就在报告里写 9/1
  并解释原因；两条都跑则 `run_counts.tsv` 分两行，**不要把 6/4 贴到 fastp 那一行**。
- **截止与诚信**：p07 课后第 7 天 23:59；日志必须是你自己账号上跑出来的（`trace.txt` 含主机与时间信息）。

## 8. 附：教材/讲义/脚本/数据指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念 / 九条失效 / 习题与答案 / 数字索引） | `textbook/chapters/ch23/manuscript.qmd` §23.4.7–§23.4.9、§23.5、§23.7、§23.9、§23.10 |
| 本专题讲义（④ 原理、⑤ 操作步骤 0–7、⑥ 结果解读、⑨ 排查、⑩ 练习） | `02_lectures/phd/topic07_workflow_nextflow/07_workflow_nextflow_lecture.md` |
| 配套流程（本实验的操作对象，只读） | `03_code/phd/workflows/`：`main.nf`、`nextflow.config`、`conf/{base,test,slurm,sge}.config`、`modules/local/*.nf`、`subworkflows/local/quantify.nf`、`bin/merge_quant.py`、`assets/samples.csv`、`README.md` |
| 对照物（硕士 m08 的 Snakemake 版，功能等价） | `03_code/master/pipelines/`（`Snakefile` / `config.yaml` / `samples.tsv` / `envs/`） |
| 演示数据生成器（**在课程仓库里，不在被复制的项目里**） | `03_code/master/pipelines/scripts/make_demo_data.py`（`--outdir` / `--n-transcripts` / `--transcript-length` / `--reads-per-sample` / `--read-length`） |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch23_queue_channel_starvation.py`、`ch23_resume_hash_factors.py`、`ch23_stale_output_mtime.py`、`ch23_wildcard_ambiguity.py` |
| 真实数据说明与规模、纯 ASCII 硬约束 | `06_data/phd/README.md` p07 节（L157、L159）；p03 节（18 样本设计 L74、单端 L80、头部截取 L81） |
| 登录号登记 | `06_data/accessions.tsv` L11 `PRJNA661210`、L12 `GSE157400` |
| 环境定义（只读） | `07_envs/conda/env_phd_workflow.yml`（`nextflow>=23.04,<26.10`、`snakemake=7.28.1`、`r-base=4.3.1`） |
| 作业规格与评分 | `08_assessment/phd/assignments/p07_workflow_nextflow_practice.md` ② 交付物 / ④ 评分 / ⑥ 失分点 |
| 前置自测 | `08_assessment/prerequisites/l0_01_linux_selftest.md` Q5/Q8/Q9/Q10、`l0_03_conda_selftest.md` Q9/Q10、`l1_phd_selftest.md` Q9/Q10 |
