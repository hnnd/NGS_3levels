---
title: "实验指导 m08：分析流程工程化与可重复报告"
level: master
topic: m08
textbook: [ch23]
lecture: ../02_lectures/master/topic08_workflow_engineering/08_workflow_engineering_lecture.md
env: ngs_ms_workflow
---

# 实验指导 m08：分析流程工程化与可重复报告

> 上机时手边打开：每步说清这条命令做什么、敲什么、看到什么算对、什么说明错了。原理与判据在教材第 23 章
> （§23.4 概念、§23.5 失效条件），本指导只放操作与自查入口。数字一律按标签读：**手算**＝纸上可复核的算式；
> **合成输入事实**＝教材 23.1 带脚本入口的默认值；**配置事实**＝`config.yaml` 现读值，不是通用生物学阈值；
> **本机引擎复跑**＝只证明引擎行为、集群未实测；**合成算例**＝`demos/ch23_*.py --selftest`；**unverified**＝未实测。
> 合成演示数据只证明工程链路跑得通，不含生物学信息——把它当结果写进报告，是本课要防的第一类错误（教材 23.1）。

## 0. 本实验对应什么

- **教材**：第 23 章 分析流程工程化：Snakemake 与 Nextflow。本实验覆盖硕士层学习目标
  LO23-01（参数化脚本）、LO23-02（完整 rule 与重跑判读）、LO23-03（conda 与容器边界）、
  LO23-04（参数化报告与元数据失效）。教材 23.4.7–23.4.9 与 §23.5.4/23.5.5/23.5.8/23.5.9
  是博士层内容，不在本实验范围（Nextflow 只留一句「另一个引擎」的边界声明）。
- **学时**：m08 共 4 学时（2 h 理论 + 2 h 实践），本实验是实践环节；上机建议 2.5–3 小时，
  整理与交叉验收 1–2 小时。
- **环境**：主环境 `ngs_ms_workflow`（`07_envs/conda/env_master_workflow.yml`：snakemake 7.28.1、
  quarto 未钉版本、r-base 4.3.1、graphviz）。fastp 0.23.4 与 salmon 1.10.3 **不在主环境里**，
  由流程的 per-rule 环境 `envs/qc.yaml`、`envs/quant.yaml` 在运行时自建；报告用 `envs/report.yaml`
  （quarto + r-base 4.3.1 + r-tidyverse 2.0.0）。Docker / Apptainer 是系统级运行时，不在任何课程 yml 中。
- **作业**：`08_assessment/master/assignments/m08_workflow_engineering_assignment.md`，占课程总成绩 3.5%；
  本专题不产生统计推断，评分无「方法选择与结果可信度」项，但对阈值记录有三处硬要求（见 §7）。
- **计算纪律**：计算一律 `qsub` 投计算节点——fastp、Salmon、合并、报告渲染、容器执行都算计算；
  登录节点只做复制项目、生成演示数据、编辑、`-n` 空跑、`--conda-create-envs-only` 预建环境、拉镜像。计算节点不通外网（根 `CLAUDE.md` 集群事实）。

## 1. 实验前检查

- **前置模块**（讲义 ②，先确认自测能过）：`l0_01_linux` Q3（管道与重定向）、Q4（grep/sed/awk）、
  Q8（批量处理）、Q9（提交集群作业）；`l0_03_conda` Q2（channel 顺序）、Q4（三种导出的差别）、
  Q7（`EnvironmentNameNotFound`）、Q9（手写 yml 并导出）、Q10（SGE 作业内激活环境）。
- **硬前提**（讲义 ②）：本实验的改造对象是**你自己在 m02–m07 真敲过、跑通过的命令**，连同当时的
  样本清单、阈值与版本、结果表。没带材料的同学用配套流程的合成数据走完全部步骤，但期末仍要交自己课题的版本，且演示数据项目的「完整性」上限 80 分（作业 ③ 第 8 步）。
- **激活主环境并核验工具链**：

  ```bash
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_workflow
  command -v snakemake quarto dot
  snakemake --version     # 课程 yml 钉 7.28.1；对不上先查环境，不要继续
  quarto --version        # yml 未钉版本：记录你机器上的实际值，写进 handover
  R --version             # 主环境 r-base 4.3.1
  command -v apptainer singularity   # 容器运行时：步骤 8 要用，两个名字命中一个即可
  ```

  这条命令在做什么：在登录节点确认工具链齐全，`dot` 来自 graphviz，步骤 3 画依赖图要用；
  `apptainer` 与 `singularity` 是同一个运行时的新旧两个命令名（无 root 集群用它替代 Docker，教材 23.4.4）。
  建环境与核版本属「准备」，留在登录节点；真正跑分析的计算作业不会继承你终端里的 conda 变量（教材 §23.5.3），所以后面的作业脚本各自带一段激活与 `command -v` 自检。
- **检查点**：`snakemake --version` 打印 7.28.1（`env_master_workflow.yml` L19 的 pin）；`quarto` 与
  `dot` 有路径。quarto 版本以你机器实装值为准，不要凭讲义或本指导预写。
  **容器运行时**：上一条命令至少打印出一个可执行文件路径（两个名字命中任一个就算过）；一个都没有时不要带着这个缺口进步骤 8。
- **出错信号**：`snakemake: command not found` → 环境未激活（教材 §23.5.3）；版本与 yml 不符 → 停下，
  先找助教核环境，不要拿错版本的行为当课程口径。容器运行时两个名字都无路径 → 先 `module avail` 看是否要 `module load apptainer`（各集群命名不同），
  仍无则联系助教确认该集群是否提供容器权限；不要用 `conda install apptainer` 绕（系统级软件，不属于任何课程 yml）。

## 2. 实验数据

本实验**不发新数据**（讲义 ②），两条轨道任选其一作为你流程的对象：

| 轨道 | 数据 | 规模与口径 | 用途 |
|---|---|---|---|
| 合成演示数据（默认） | `data/ref/transcripts.fa` + `data/reads/{CK_1,CK_2,TR_1,TR_2}_{1,2}.fq.gz` | 4 样本、60 条转录本各 1500 bp、每样本 20000 对 100 bp 读段、质量恒定为单个 `I`（即 Q40）、种子 20260829、处理组固定上调 `tx0003`/`tx0007`/`tx0011`（合成输入事实，教材 23.1；`scripts/make_demo_data.py` L26/L30/L73/L90–94） | 无自备数据时的离线试跑；只证明链路通，不具生物学意义 |
| 真实数据（硕士层对象） | `PRJDB36269` 的 12 个 RNA-seq run（m04 主线：2 处理 × 3 时间点 × 2 重复） | 登录号在 `06_data/accessions.tsv` L51 登记；m04 每样本降采样 300 万条，m04+m05 合计约 4 GB（`06_data/master/README.md` m04 节） | 把流程切到真实数据的最终对象：只改 `samples.tsv` 与 `config.yaml`，Snakefile 不动 |
| 你自己的 m02–m07 产物 | 你在前面任一专题跑过的原始数据与清单 | 规模以你的专题为准 | 作业真正要改造的对象（推荐） |

- **数据限制必须写进报告**：`PRJDB36269` 只有 2 个生物学重复（设计是 2×3×2），流程能跑通，
  统计结论不能超出这个设计（教材 23.6.1；`06_data/master/README.md` m04 节）。
- **工作目录**：`/d3/scratch/${USER}/ngs/m08_project`（scratch 配额大；家目录配额小，放结果扣规范性分）。
  课程仓库是只读原材料，**复制出来改，不要改课程源文件**。
- **合成数据的预期性质**：质量恒定 Q40 意味着 fastp 过滤近乎零丢弃，改 Q20→Q30 未必改变任何计数
  （unverified 于真实数据）；步骤 6 与 7 会用它说明「报告活性」判据的正确读法。

## 3. 实验步骤

> 每步五栏：目的 / 命令 / 产出文件 / 检查点 / 出错信号（→ 教材 §23.5.x）。命令里的脚本名、参数名、
> 输出文件名与 `03_code/master/pipelines/` 现版逐字一致（本指导修订时逐个 `grep` 核对，见任务回执）。
> 需要改流程时一律「复制个人副本 → 改指定行 → `grep` 确认 → `qsub` 副本」，不得投递后再补参数（COURSE_SYNC §7）。
>
> **在哪敲命令**：SSH 登录后当前目录是家目录。下文项目根固定为 `/d3/scratch/${USER}/ngs/m08_project`；
> 课程仓库位置用 `${REPO_DIR}` 表示（步骤 0 第一行定义，校内由教师公布，校外为 `git clone` 路径）。
> **不要**原样输入 `<尖括号占位符>`——`<` 是 Bash 重定向符，会把命令截成语法错误。`snakemake` 的相对路径
> 以**你运行命令时的当前目录**为基准（教材 §23.5.7），所以每条命令先 `cd` 到项目根。

### 步骤 0：复制项目与环境预检

- **目的**：在 scratch 建立可修改的个人流程副本，确认主环境与项目文件齐全。
- **命令**（登录节点）：

  ```bash
  REPO_DIR=/path/to/NGS_3Levels        # ← 课程仓库在本机的实际位置
  mkdir -p /d3/scratch/${USER}/ngs
  cp -r "${REPO_DIR}/03_code/master/pipelines" /d3/scratch/${USER}/ngs/m08_project
  cd /d3/scratch/${USER}/ngs/m08_project
  ls Snakefile config.yaml samples.tsv envs scripts report
  source /opt/miniconda3/bin/activate && conda activate ngs_ms_workflow
  snakemake --version && quarto --version && command -v dot
  ```

  这条命令在做什么：把配套流程（`Snakefile` / `config.yaml` / `samples.tsv` / `envs/*.yaml` /
  `scripts/*.py` / `report/report.qmd`）整目录复制成个人项目——原目录是公共材料，只读。
- **产出文件**：`/d3/scratch/${USER}/ngs/m08_project/` 个人项目；版本记录（写进 handover）。
- **检查点**：上面 `ls` 逐项存在：`Snakefile`、`config.yaml`、`samples.tsv`、
  `envs/{qc,quant,report}.yaml`、`scripts/{make_demo_data,merge_quant}.py`、`report/report.qmd`。
  版本事实：snakemake 7.28.1 是主环境 pin；fastp 0.23.4、salmon 1.10.3、r-base 4.3.1 是
  `envs/{qc,quant,report}.yaml` 的 per-rule pin，**此刻尚未创建**——主环境有 snakemake 不代表 fastp 装好了
  （qc.yaml L9、quant.yaml L8、report.yaml L10–13）。
- **出错信号**：`ls` 缺文件 → 重新 `cp -r`；主环境命令不可解析 → 教材 §23.5.3；版本对不上 → 找助教核环境。

### 步骤 1：准备输入与样本清单

- **目的**：生成（或接入）流程输入，确认样本清单四列齐全、双端成对、样本 ID 唯一。
- **命令**（登录节点；在**项目根**运行，不要在课程仓库根找 `scripts/`）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m08_project
  python3 scripts/make_demo_data.py --outdir data
  ls -lh data/ref/ data/reads/
  cat -A samples.tsv | head        # 列间必须是 ^I（制表符），不是空格
  ```

  这条命令在做什么：生成器按固定种子 20260829 合成 60 条转录本与 4 个样本的双端读段
  （默认参数 `--n-transcripts 60 --transcript-length 1500 --reads-per-sample 20000 --read-length 100`，
  脚本 L90–94；种子在 L26）。用真实数据时跳过生成，直接改 `samples.tsv`（四列
  `sample/fq1/fq2/condition`）与 `config.yaml` 指向你的数据，Snakefile 不用动；本实验不新下载数据。
- **产出文件**：`data/ref/transcripts.fa`；`data/reads/{CK_1,CK_2,TR_1,TR_2}_{1,2}.fq.gz`
  （或你的真实数据 + 更新后的 `samples.tsv`）。
- **检查点**：合成输入事实（教材 23.1 带脚本入口）：4 样本、60 条 × 1500 bp、每样本 20000 对 100 bp、
  上调 `tx0003`/`tx0007`/`tx0011`。读段文件数 = 样本数 × 每样本端数 = $4 \times 2 = 8$
  （`ls data/reads/*.fq.gz | wc -l` 应为 8）。样本 ID 在 `samples.tsv` 唯一、双端文件成对存在。
- **出错信号**：文件缺失、双端不成对 → 先查生成日志；**样本 ID 重复** → 停止自查：当前 `load_samples`
  用字典返回，重复 ID 会被静默覆盖，只留最后一行（Snakefile L36），不会报错。清单被空格而非制表符分隔 → 在读清单阶段就抛「缺少必需列」，不会带着错表进入流程
  （教材 23.4.2/§23.5.7；本机直接执行 `load_samples` 源码已复现）。

### 步骤 2：参数化与配置外置

- **目的**：把你那条线的命令参数化，并把一切会变的值收进 `config.yaml` 与 `samples.tsv`
  （对应作业「命令 → 参数化脚本」与「清单与配置」两步）。
- **命令**（无新计算；编辑在个人副本里进行）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m08_project
  # ① 按教材 23.4.1 的骨架改写你自己那条命令：set -euo pipefail、路径/样本名/线程数/阈值四处变量化、
  #    每步 2>&1 留日志。批量参数的 argparse 写法参照 scripts/merge_quant.py L64–67（四个必需参数）。
  # ② 验收（作业步骤 1 的硬标准）：把**你自己**改写好的脚本拷到 /tmp，输入指向项目里的同一批文件，
  #    在那里真跑一次，再回项目根用同一输入跑一次，两份输出表 diff 无差异才算过。
  #    --help 只验接口，验不出硬编码路径：
  mkdir -p /tmp/m08_paramcheck && cd /tmp/m08_paramcheck
  cp /d3/scratch/${USER}/ngs/m08_project/scripts/你的脚本.py .    # 换成你的文件名
  python3 你的脚本.py --help | head -8
  python3 你的脚本.py ... > own_tmp.log 2>&1; echo "rc=$?"   # ... 按 --help 填参数，输入写项目的实际路径
  cd /d3/scratch/${USER}/ngs/m08_project && python3 scripts/你的脚本.py ... > own_project.log 2>&1
  # ③ 同形演练（还没有自己的脚本时用仓库脚本走一遍；两样本夹具，输出可核对）：
  cd /tmp/m08_paramcheck && cp /d3/scratch/${USER}/ngs/m08_project/scripts/merge_quant.py .
  printf 'Name\tLength\tEffectiveLength\tTPM\tNumReads\ntx0001\t1500\t1400\t1.0\t1\n' > q1.sf && cp q1.sf q2.sf
  python3 merge_quant.py --quant-files q1.sf q2.sf --sample-names S1 S2 \
    --counts-out c.tsv --tpm-out t.tsv && head -2 c.tsv
  cd /d3/scratch/${USER}/ngs/m08_project     # 做完回到项目根，后续步骤都在这里
  # ④ 改 config.yaml：samples_tsv(L13)、transcriptome(L16)、三条线程(L20–23)、fastp 阈值(L29–31)、
  #    salmon libtype 与 index_kmer(L34–36)、报告三项(L40–43)
  grep -n 'samples_tsv\|transcriptome\|threads\|qualified_quality_phred\|length_required\|index_kmer\|thresholds_note' config.yaml
  ```

  这条命令在做什么：参数化解决「换样本、换机器」（教材 23.4.1）；配置外置的纪律是**会随数据集、
  机器与批次变化的东西一律进配置文件**——样本清单路径、参考序列、线程数、阈值全在 `config.yaml`，
  Snakefile 只引用键名。口径要认清：`results/`、`envs/`、`scripts/`、`report/` 是配套流程的
  **固定项目目录约定**（可以保留字面路径，Snakefile L44 就是 `RESULTS = "results"`）；
  要外置的是样本、输入、参考这类可变路径，不是「Snakefile 里一个路径都不许出现」。
- **产出文件**：你参数化后的脚本（放 `scripts/`）、更新后的 `config.yaml` 与 `samples.tsv`。
- **检查点**：`cat -A samples.tsv` 列间是 `^I`；每行恰四列、样本 ID 唯一、输入文件非空。
  **你自己的脚本**：在 `/tmp/m08_paramcheck` 与项目根各跑一次，两次 `rc=0` 且日志里没有
  `No such file or directory`；两份输出表 `diff` 无差异（同输入同参数）。这一步才是作业步骤 1 的验收，
  换成仓库脚本跑的 ③ 只是同形演练。③ 的判据：表头 `transcript` + 两个样本名、数值与输入一致
  （本机现跑：`transcript S1 S2`、`tx0001 1.0000 1.0000`，rc=0；两份夹具内容相同所以相等，
  想看两列不同就把 `q2.sf` 的 `NumReads` 改成 2）。换目录能跑通，说明路径都来自参数。
  `grep` 确认阈值只出现在 `config.yaml`，不在 Snakefile 的 `shell` 里写死。
- **出错信号**：空格分隔的清单 → 读清单阶段报「缺少必需列：['sample','fq1','fq2','condition']」
  （**显式失败**，不是旧讲义写的「不报错、fastp 只有 1 个」，教材 23.4.2/§23.5.7）；缺参、空路径、绝对路径残留 → 教材 §23.4.1 与 §23.5.7。

### 步骤 3：空跑与 DAG 预演

- **目的**：让引擎在动手前告诉你它打算跑哪些节点、为什么——先 `-n`，确认无误再投递。
- **命令**（`-n` 是空跑、不产生计算量，登录节点执行；DAG 渲染属计算，走步骤 4 的作业）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m08_project
  snakemake -n 2>&1 | tee logs_dryrun_01.txt | tail -30
  # 画依赖图要调 dot，属计算：写成一条作业（下面这份就是本节自己给出的脚本，不必先看后面的步骤）
  cat > m08_dag.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m08_dag
  #$ -cwd
  #$ -j y
  #$ -pe smp 1
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_workflow
  command -v snakemake >/dev/null || { echo "[FATAL] snakemake 不在 PATH"; exit 1; }
  cd /d3/scratch/${USER}/ngs/m08_project
  snakemake --dag | dot -Tpng > dag.png
  EOF
  grep -n 'm08_dag\|conda activate\|dag.png' m08_dag.job   # 投前自查：作业名/激活/输出三处都在
  qsub m08_dag.job && qstat -u ${USER}
  ```

  这条命令在做什么：`-n` 只打印计划不执行；逐项读每个节点的 `reason`（为什么重跑）与 `wildcards`
  （绑定了什么值）——这两行是步骤 6 与全部排错的依据（教材 23.4.3）。作业头 `-S /bin/bash`
  防止 SGE 用默认 shell 执行（教材 §23.5.3）。作业脚本落在项目目录里（**自包含**：随项目一起复制、
  一起交付）。后面各步的作业都是「同结构 + 换作业名 + 换 `snakemake` 那一行」，`grep` 自查不变。
- **产出文件**：`logs_dryrun_01.txt`、`dag.png`（作业结束后落在项目根）、`m08_dag.job`。
- **检查点**（手算）：默认四样本的空跑应给 **total 12 = all 1 + fastp 4 + salmon_index 1 +
  salmon_quant 4 + merge_counts 1 + report 1**（$1+4+1+4+1+1=12$，教材 23.4.2；本机引擎复跑于
  snakemake 7.28.1 同 pin、同一份管道，也是 12，**集群未实测**）。首次运行时各节点 `reason` 以
  `Missing output files` 开头是正常形态；`salmon_quant` 这类下游还会并列
  `Input files updated by another job`（上游 `fastp` 本次要重跑）——判据是**没有** `Updated input files`。
  `wildcards` 绑定应为 `sample=CK_1` 这类**不含斜杠**的值；`dag.png` 非空且能打开。
- **出错信号**：
  - `fastp` 只有 1 个 → 最直接原因是清单里只读到一行样本（查清单行数、重复 ID、目标展开，教材 23.4.2），
    **不是**「空格分隔不报错」。
  - `wildcards: sample=clean/CK_1`（绑定含 `/`）→ 通配符贪婪吞路径，教材 §23.5.1；合成自查（在课程仓库
    根目录运行）：`PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch23_wildcard_ambiguity.py --selftest`
    → 同前缀歧义 500/500、异前缀 0/500（合成算例，本机现跑 7/7 PASS）。项目首部已有
    `wildcard_constraints: sample=r"[A-Za-z0-9_.-]+"`（Snakefile L47–48），新增 rule 时还要检查输出前缀唯一性。
  - `MissingInputException` → 教材 §23.5.7：先 `ls` 核文件真实存在且非空，再核当前目录；**不要 `touch`
    造空输入**。
  - `Target rules may not contain wildcards`（你删掉 `rule all` 做实验时）→ 教材 23.4.2：第一条带通配符的
    规则被当成默认目标。本机现跑删掉 `rule all` 后正是这句 `WorkflowError`，不是「只跑一个样本」。

### 步骤 4：预建 per-rule 环境并提交真实计算

- **目的**：让每条 rule 在自己的 conda 环境里跑（版本互不牵制，教材 23.4.4），并把全部计算交给计算节点。
- **命令**（① 在登录节点；② 作业脚本写在项目目录内，步骤 6/7/8/9 的作业都由它派生）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m08_project
  # ① 登录节点预建三个 per-rule 环境（计算节点无外网，首次 --use-conda 联网建环境必失败）
  snakemake --use-conda --conda-create-envs-only -c 1
  # ② 作业脚本：存成项目目录内的 m08_run.job（随项目一起复制、一起交付）
  cat > m08_run.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m08_run
  #$ -cwd
  #$ -j y
  #$ -pe smp 1
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_workflow
  command -v snakemake >/dev/null || { echo "[FATAL] snakemake 不在 PATH"; exit 1; }
  cd /d3/scratch/${USER}/ngs/m08_project
  snakemake --use-conda -j 50 \
    --cluster "qsub -S /bin/bash -cwd -j y -pe smp {threads} -N {rule}_{wildcards}"
  EOF
  grep -n 'm08_run\|conda activate\|--cluster' m08_run.job   # 投前自查三行都在
  qsub m08_run.job
  qstat -u ${USER}     # qw 排队 / r 运行 / Eqw 报错
  ```

  这条命令在做什么：驱动作业自己激活环境并 `command -v` 自检（找不到立刻退出，而不是等第一条 rule
  才死）；`--cluster` 串把每条 rule 作为 SGE 作业派发，`-S /bin/bash` 保证作业内 `source` 语法可用；
  `{threads}` 来自 `config.yaml` 的三条线程声明（默认都是 4），`{wildcards}` 让日志名可区分样本。
  命令参数已与源码逐项核对：fastp `-i/-I/-o/-O/-h/-j -w --qualified_quality_phred --length_required`
  加 `params.extra`（默认 `--detect_adapter_for_pe`，Snakefile L83–87，阈值来自 `config.yaml` L29–31）；
  salmon index `-t/-i/-k/-p`（L108–109，k 默认 31）；salmon quant `-i/-l/-1/-2/-p` 加
  `--validateMappings --seqBias`（L132–134，libtype 默认 A）。引擎驱动保持轻量，真正的计算在各 rule 作业里。
- **一个架构前提**：这条作业是「常驻主作业在计算节点上派发子作业」，要求该计算节点是 **submit host**
  （能执行 `qsub`）。不少 SGE 集群只允许登录节点投递，此时主作业会当场死在
  `Unable to run job: <节点名> is not a submit host`。遇到这句就改成在登录节点的 `tmux`／`screen`
  会话里前台跑同一条 `snakemake --use-conda -j 50 --cluster "qsub …"`（会话保住连接，SSH 断线不中断）；
  **不要**把 `-j 50` 的调度挪到裸终端里跑一次就走——那等于绕开本实验要练的作业纪律。两种方式都要在 handover 里写清你用的是哪一种。
- **产出文件**：`m08_run.job`（项目目录内）、`results/clean/{sample}_{1,2}.fq.gz`、
  `results/qc/{sample}.fastp.{html,json}`、
  `results/index/salmon/`、`results/quant/{sample}/quant.sf`、`results/counts/` 双矩阵、报告；
  每条 rule 的 `logs/<rule>/...log` 与 `benchmarks/<rule>/...tsv`。
- **检查点**（定性）：每条 rule 日志非空、输出存在；驱动 rc=0 只说明调度成功，**产物验收看步骤 5**。
  资源申请不预写任何通用 GB 数——首跑后按本 rule 的 `max_rss` 与实际数据规模复盘（余量 1.3–2 倍，教材 23.4.5）。
- **出错信号**：
  - 计算节点日志 `fastp: command not found` / `snakemake: command not found` → 环境未进入作业，
    教材 §23.5.3（SGE 默认不导出登录环境，要 `-V` 或作业内自激活；SLURM 默认导出，`--export=NONE` 才不继承）。
  - rule 作业失败 → 先看 `logs/<rule>/<sample>.log` 里的工具报错原文，不以驱动 rc 代替产物验收
    （教材 23.4.5：终端只印「job failed」外壳）。
  - 卡在创建环境且报找不到 `mamba` → 7.28.1 的 `--conda-frontend` 默认值是 `mamba`（`--help` 明文
    `(default: mamba)`），而课程 yml 未声明它；退一步用
    `snakemake --use-conda --conda-create-envs-only -c 1 --conda-frontend conda`。这是环境差异，不是你写错了流程。

### 步骤 5：逐类验收业务产物

- **目的**：对四类产物逐一验收，把「跑完了」与「产物对」分开。
- **命令**（作业结束后在项目根执行）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m08_project
  ls results/clean/ results/qc/                     # fastp：每样本双端 + html/json 各一
  ls results/index/salmon/                          # 索引：看目录内容，不只看目录存在
  head -1 results/quant/CK_1/quant.sf               # 定量：五列表头
  head -1 results/counts/counts_matrix.tsv; head -1 results/counts/tpm_matrix.tsv
  wc -l results/quant/*/quant.sf results/counts/*.tsv
  ```

- **产出文件**：验收记录（写进 §4 结果记录表）。
- **检查点**（本机引擎复跑于合成数据，集群未实测；数量随你的样本数变，结构判据不变）：
  1. **fastp**（Snakefile L66–70）：四样本产物齐全、双端文件非空。文件数手算：
     `results/clean/` 有 $4 \times 2 = 8$ 个（样本数 × 端数），`results/qc/` 也是 $4 \times 2 = 8$ 个
     （每样本 html + json 各一）；两条 `ls results/clean/ | wc -l` 与 `ls results/qc/ | wc -l` 各自数到 8。
     保留率、过滤数一律**不预填**（unverified；Q40 合成数据过滤近零丢弃是预期性质）。
  2. **索引**（L90–109）：输出是 `directory()` 声明的目录（L97），检查**目录里的索引内容**而不是目录存在
     本身；显式目录声明让引擎用哨兵文件判新旧并安全整目录删除（教材 23.4.3 官方口径）。
  3. **定量**（L112–134）：`quant.sf` 表头必须是 `Name/Length/EffectiveLength/TPM/NumReads` 五列
     （`merge_quant.py` L20 定义、L37–38 强校验，不是 salmon 输出会被拒读）。份数 = 样本数（合成数据 4 份），
     每份行数 = 转录本条数 + 1 行表头（合成数据 $60+1=61$，`wc -l results/quant/*/quant.sf` 可复核；用真实数据时换成你的转录本条数 + 1）。
  4. **汇总**（L137–153）：`counts_matrix.tsv` 与 `tpm_matrix.tsv` 行 = 转录本、列 = 样本；文件数与样本名数
     不一致时 merge 脚本 rc=1（L75–81，本机小夹具实跑复现 rc=1）。行数同样是「转录本条数 + 1 行表头」
     （合成数据 $60+1=61$），列数是 $1$（`transcript` 列名）$+4$（四个样本）= 5，表头为
     `transcript CK_1 CK_2 TR_1 TR_2`。**实际检测数、assigned reads、过滤率均 unverified**，由你实跑后填。
  5. mini 流程止于计数矩阵与文库量、PCA 报告——**没有 DESeq2、没有论文图复现**（教材 23.6.1）；
     报告里的差异分析阈值注记是「待接 m04 链」的记录义务，不是本流程产物。
- **出错信号**：merge 警告「转录本集合与第一个样本不一致」→ 各样本索引不是同一份（merge L96–98）；
  `quant.sf` 表头被拒 → 该文件不是 salmon 输出，查上游而不是改 merge；目录当文件用时先查 `directory()`。

### 步骤 6：断点续跑与参数触发双实验

- **目的**：亲手验证增量判据——删产物后重算范围落在哪条分支、改参数被哪个触发器捕获
  （这是 handover 第 3 节的核心素材）。
- **命令**（各段 `-n` 都在登录节点；A3 的真跑用一条由步骤 4 派生的作业）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m08_project
  # 前提：默认目标已跑齐（含 results/report/report.html）。报告还没渲出来就先做完步骤 7
  # （渲报告本身属计算，也得 qsub），再回到这里——不要用 touch 造一个空 report.html 糊过去：
  # 空报告会让 B 段「改参→重渲」这一步失去可观测对象，读不出机制。
  ls results/counts/counts_matrix.tsv results/report/report.html
  # 实验 A1：删一个中间产物，按默认目标空跑
  rm results/quant/CK_1/quant.sf
  snakemake -n 2>&1 | tee logs_dryrun_02A1.txt
  snakemake --summary 2>&1 | grep 'CK_1/quant.sf' | tee -a logs_dryrun_02A1.txt
  # 实验 A2：把它作为目标点名，这一支才会被重新计划
  snakemake -n results/quant/CK_1/quant.sf 2>&1 | tee logs_dryrun_02A2.txt
  # 实验 A3：真跑一次点名目标。派生作业：只把默认目标换成该路径，其余行不动
  sed 's#snakemake --use-conda -j 50#snakemake --use-conda -j 2 results/quant/CK_1/quant.sf#' \
    m08_run.job > m08_resume.job
  grep -n 'quant.sf\|-N m08_run' m08_resume.job    # 投前自查：目标已换；-N 相同也无妨（同名作业串行）
  qsub m08_resume.job && qstat -u ${USER}
  # 补回后再按默认目标空跑（等上一条作业结束后再执行）
  snakemake -n 2>&1 | tee logs_dryrun_02A3.txt
  # 实验 B：改一个阈值（先备份，改完 diff）
  cp config.yaml config.yaml.bak
  #   用编辑器把 fastp.qualified_quality_phred 从 20 改成 30
  diff config.yaml.bak config.yaml
  snakemake -n 2>&1 | tee logs_dryrun_02B.txt
  snakemake -n --rerun-triggers mtime 2>&1 | tee logs_dryrun_02B2.txt   # 对照：退回只看时间戳
  # 合成对照（机制量化，在课程仓库根目录运行）
  PYTHONDONTWRITEBYTECODE=1 python3 textbook/demos/ch23_stale_output_mtime.py --selftest
  ```

  这条命令在做什么：7.28.1（≥7.8）默认五类触发器全开——mtime、params、input、software-env、code
  （教材 23.4.3）。**A1 的结论与直觉相反**：`quant.sf` 是中间产物，既不是 `rule all` 的输入、也没被
  命令行点名；删掉它按默认目标空跑给 `Nothing to be done`，而 `--summary` 该行同时写 `missing` 与
  `no update`。增量判定只从目标倒推，被删文件的生产规则不在本次目标链上时引擎不检查它的输出（教材 23.4.2「以目标文件为起点」+23.4.3）。做 A1 前必须先让默认目标跑齐（含报告）。
- **产出文件**：`logs_dryrun_02A1.txt`、`02A2.txt`、`02A3.txt`、`02B.txt`、`02B2.txt`、`config.yaml.bak`
  与 diff、一段文字说明（handover 第 3 节原料）。
- **检查点**（每一条都是「触发集合 → 计数」的手算，可照着 DAG 自己数；本机引擎复跑与手算一致，
  **集群未实测**；工具版本差异见下面的资料口径）：
  - A1 → `Nothing to be done`（目标集合为空 ⇒ 0 个作业），`--summary` 里该行 `missing` + `no update` 并存；
  - A2 → 点名 `quant.sf` 后目标集合 = {salmon_quant(CK_1)} ⇒ `total 1`（`Missing output files`、`wildcards: sample=CK_1`）；
  - A3 → 补回该文件后默认目标重排 = merge_counts + report + all，$1+1+1=3$ ⇒ `total 3`
    （`Updated input files: .../quant.sf`），fastp 与索引不重跑；只删**目标侧**矩阵同为 merge+report+all
    $=3$，只删报告为 report+all $=2$；
  - B → 触发集合 = 四个 fastp（`Params have changed since last execution`）+ 四个 salmon_quant
    （上游 clean reads 变了，`Input files updated by another job`）+ merge_counts + report + all
    ⇒ $4+4+1+1+1=11$；`salmon_index` 不重跑，正好 $12-1=11$（12 见步骤 3 的构成）。
    同一份改过的配置加 `--rerun-triggers mtime` 退回 `Nothing to be done`——「只认时间戳」的旧行为，只作对照，不要当默认。
  - 演示脚本把这条失效通路量化：改参后 0 作业、旧汇总 160 个细胞里 97 个不同（60.6%）、`-R` 强制后
    只补 2 个作业（合成算例，本机现跑 9/9 PASS；40 转录本 × 4 样本、Poisson 均值 25）。
- **资料口径**：以上 `total` 与 `reason` 是本机对同一份 `03_code/master/pipelines` 的复跑记录；
  产生元数据那次真跑用的本机 fastp 1.0.1 与 salmon 1.10.0（**非课程 pin**），因此只声明引擎行为，
  不声明工具行为。本机渲不出真报告（见步骤 7 的验证边界），A1/B 的「默认目标已跑齐」是用
  `snakemake --touch` 给 `results/report/report.html` 补的元数据占位；占位只影响「报告产物是否存在」，
  不影响 A1 要演示的中间产物判据——你按步骤 7 渲出真报告后重做，结论应相同。
- **出错信号**：
  - A1 给出 `total 1` 或 `total 3` → 你删的不是中间产物（或删的是目标侧文件），先 `snakemake --summary`
    核每行的 `status`/`plan` 再解释，不要套用「删了就会重跑」。
  - A1 给出 `total 2`（report + all）→ 报告产物本来就缺，链条没闭合：先渲报告（步骤 7）再重做 A1。
  - B 仍 `Nothing to be done` → 先确认改的是 `config.yaml` 且 `diff` 有差异；仍无反应才按教材 §23.5.2
    查 `.snakemake/` 是否丢失（配套 `.gitignore` 排除了它，目录搬走或重新克隆都会丢）、mtime 是否被
    `touch`/`rsync -t` 保留；处置用 `snakemake -R fastp` 或 `--cleanup-metadata <输出>`，**不要删整个 `.snakemake/`**。
  - `Directory cannot be locked` → 先 `ps -u $USER | grep snakemake` 与 `qstat -u $USER` 确认无实例，
    再 `snakemake --unlock`（教材 §23.5.6）。
  - 样本绑定异常 → 教材 §23.5.1。

### 步骤 7：参数化报告与环境快照

- **目的**：渲染「活的」Quarto 报告，并留下两类环境快照。
- **命令**（渲染是计算：经流程触发，或单独投递一条只跑 report 的作业）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m08_project
  # 触发方式（二选一，都必须在计算节点执行；登录节点不跑渲染）：
  #   ① 整条流程跑完时 report 已在步骤 4 的作业里渲过一版；
  #   ② 只重渲报告：派生一条作业——把默认目标换成报告路径，其余行不动
  sed -e 's/-N m08_run/-N m08_report/' \
      -e 's#snakemake --use-conda -j 50#snakemake --use-conda -j 2 results/report/report.html#' \
      m08_run.job > m08_report.job
  grep -n 'm08_report\|report.html' m08_report.job    # 改完先看：作业名与目标两处都在
  qsub m08_report.job && qstat -u ${USER}
  # 环境快照（只读操作，登录节点即可；不是 report rule 的自动产物）：
  conda env export --from-history > env_snapshot.yml
  # 可选：per-rule 环境各导一份。--use-conda 按 envs/qc.yaml 的**内容哈希**建环境，落在
  # .snakemake/conda/<哈希>，**不注册名字**，所以不能写 -n m08_qc 导出。7.28.1 的
  # --list-conda-envs 先打表头 environment / container / location，第三列才是磁盘目录：
  snakemake --use-conda --list-conda-envs | tee list_envs.txt
  # 取末列（路径里也可能含空格，故用 $NF 而非 $3），并做「非空 + 确实是目录」断言，失败即退出
  QCDIR=$(awk -F'\t' 'NR>1 && $1 ~ /qc\.yaml$/ {print $NF}' list_envs.txt)
  [ -d "${QCDIR}" ] || { echo "[FATAL] 没解析出 qc.yaml 的环境目录，先 cat list_envs.txt 核对表头"; exit 1; }
  conda env export -p "$(realpath "${QCDIR}")" --from-history > env_snapshot_m08_qc.yml
  head -3 env_snapshot_m08_qc.yml
  ```

  这条命令在做什么：report rule（Snakefile L156–183）用 `quarto render` 渲染 `report/report.qmd`，
  `-P` 注入本次运行的**绝对路径**（`realpath` 后的 counts、tpm、samples）与标题、作者、阈值注记
  （六个 `-P` 见 L179–183）；qmd 里读这三个路径算文库量与 log2(TPM+1) PCA，尾部固定 `sessionInfo()`
  （report.qmd L25–29、L84–87）。相对路径读结果表的失败形态是「渲染成功、图也有、数字是过期的」（教材 23.4.6），所以路径必须经 `-P` 注入。
- **一个必须避开的目录陷阱**：`--output-dir` 只在「单文档且不在 Quarto 项目内、或该文档已列进项目
  `render` 清单」时可用。课程仓库根有 `_quarto.yml`（课程站配置，`render` 不含 `report/`），在仓库里试渲会报
  `ERROR: The --output-dir flag can only be used when rendering projects.`，看着像流程写错，其实只是目录选错——
  这也是步骤 0 要求复制到 `/d3/scratch` 的理由之一（本机已复现该报错）。
- **产出文件**：`results/report/report.html`、`env_snapshot.yml`、`m08_report.job`（项目目录内）、
  可选的 `env_snapshot_m08_qc.yml`。
- **检查点**（活性判据，教材 23.4.6）：报告读到的矩阵路径与本次运行一致、第 3 节出现 `config.yaml` 的
  阈值注记（`Snakefile` 传的是 `params.note`，report.qmd 第 3 节渲染它）、样本表是这次跑的那张、尾部有
  R `sessionInfo()`；需要手动改 HTML 或重新贴图 = 报告没接进流程。**活性验收的正确读法**：先核参数触发
  与输入接线（步骤 6 的 `reason`），再看报告是否更新；默认合成数据全为 Q40，Q20→Q30 不保证改变任何计数——「数字必须变」不是唯一证据。
- **出错信号**：`Unable to locate an installed version of pandoc` → pandoc/Quarto 环境混用（讲义 ⑨-5）：
  确认 report rule 走 `envs/report.yaml`，`quarto check` 逐项核 pandoc/R/knitr；
  `there is no package called 'tidyverse'` → 命令跑在**宿主 R** 上（主环境 yml 与 `envs/report.yaml`
  都声明了 `r-tidyverse=2.0.0`，只有裸宿主 R 可能没有）；`--output-dir` 报错 → 按上一条查目录，别改 Snakefile；
  PCA 输入全零方差行被过滤后图异常 → 查输入矩阵是否为空。
- **验证边界**：本步**未在本机跑通**——仓库内试渲撞 `--output-dir` 目录报错，挪到仓库外再试则卡在
  `there is no package called 'tidyverse'`（本机裸宿主 R 4.5.2 无 tidyverse，且本机没有 `ngs_ms_workflow`
  环境可激活）。两条都与流程写法无关，故 `report.html` 的产出与活性判读由你实跑后填写（**集群未实测**）；
  指导只核对过 report rule 的命令构造（`realpath` + 六个 `-P` 参数名）。

### 步骤 8：容器化单条 rule（作业步骤 6 的必做项）

- **目的**：体验「环境锁定的下一层」——当前 Snakefile 只有 `conda:` 没有 `container:`，这一步是在**个人副本**里
  给选定 rule 加容器声明的改造（作业 ③ 第 6 步要求「用 BioContainers 镜像跑其中一条 rule，对比容器内外 `--version`」，不做就交一个缺项作业）。
- **命令**（镜像拉取与 `inspect` 属只读准备、在登录节点；**版本对照与容器里真跑 fastp 都属计算**，一律 `qsub`）：

  ```bash
  cd /d3/scratch/${USER}/ngs/m08_project
  # ① 镜像放进项目内的 containers/（随项目一起交付，同学交叉验收时不必再联网拉）
  mkdir -p containers
  apptainer pull containers/fastp_0.23.4.sif docker://quay.io/biocontainers/fastp:0.23.4--h5f740d0_0
  # ② 个人副本 Snakefile 的 rule fastp 内加一行。写相对项目根的路径，不要写自己的绝对路径：
  #      container: "containers/fastp_0.23.4.sif"
  grep -n 'container:' Snakefile        # 确认加到位；相对路径随项目复制到哪儿都成立
  # ③ 记镜像身份（标签是可变指针，digest 才是锁定）
  apptainer inspect containers/fastp_0.23.4.sif | head -20
  # ④ 版本对照也属计算：写成一条作业，两个版本号都落进同一份作业日志
  cat > m08_container.job <<'EOF'
  #!/bin/bash
  #$ -S /bin/bash
  #$ -N m08_container
  #$ -cwd
  #$ -j y
  #$ -pe smp 1
  source /opt/miniconda3/bin/activate
  conda activate ngs_ms_workflow
  cd /d3/scratch/${USER}/ngs/m08_project
  apptainer exec containers/fastp_0.23.4.sif fastp --version
  snakemake --use-conda --list-conda-envs > list_envs.txt
  QCDIR=$(awk -F'\t' 'NR>1 && $1 ~ /qc\.yaml$/ {print $NF}' list_envs.txt)
  [ -d "${QCDIR}" ] || { echo "[FATAL] 没解析出 qc.yaml 的环境目录，先 cat list_envs.txt"; exit 1; }
  conda run -p "$(realpath "${QCDIR}")" fastp --version
  EOF
  grep -n 'apptainer exec\|fastp --version' m08_container.job   # 投前自查
  qsub m08_container.job && qstat -u ${USER}   # 作业日志里应有两条 fastp 版本号
  # ⑤ 让容器版真跑一次 fastp：派生作业，加 --use-singularity，并用 -R fastp 强制目标
  sed 's#snakemake --use-conda -j 50#snakemake --use-conda --use-singularity -j 4 -R fastp#' \
    m08_run.job > m08_run_container.job
  grep -n 'use-singularity\|-R fastp' m08_run_container.job
  qsub m08_run_container.job && qstat -u ${USER}
  ```

  这条命令在做什么：容器把除内核外的整段用户态换掉，与 conda 只换用户态解释器与依赖包不是同一层
  （教材 23.4.4 的对照表）；无 root 的集群用 Apptainer（原 Singularity），不用 Docker。7.28.1 的接口名
  只有 `--use-singularity`，它**按名字找 `singularity` 这个可执行文件**（镜像既可写 `docker://` URL，
  也可写本地 `.sif` 路径）；多数集群把 `singularity` 做成指向 `apptainer` 的软链，此时引擎照常工作；
  只有 `apptainer` 而没有该别名时先 `module load` 或 `ln -s` 建软链，**不要改 `container:` 里的路径**。
  固定 tag 只是锁定的**下限**——标签是可变指针，长期归档要记 `@sha256` 摘要。
- **可能撞上的挂载边界**：Apptainer 默认自动挂载 `$HOME`、`/tmp` 与当前目录，但 `/d3` 这类并行文件系统
  要看宿主的自动挂载配置。若容器里报 `cannot open file /d3/scratch/...`，说明项目目录没被挂进容器——
  不要改 `container:`，在 `snakemake` 那一行加 `--singularity-args "--bind /d3"` 即可
  （7.28.1 的这个参数就是在 `singularity exec` 的参数位里追加内容，`--help` 有明文）。
- **产出文件**：个人副本的 `container:` 声明、`containers/fastp_0.23.4.sif`（随项目交付）、镜像 digest 记录、
  `m08_container.job` 的作业日志（容器内与 per-rule 环境内两条 `fastp --version`）、
  `m08_run_container.job` 的日志（写进 handover）。
- **检查点**（配置事实 + 仓库实查）：镜像名、固定 tag、digest 三项都记录；两个环境的 `fastp --version`
  都是 `0.23.4`。`envs/qc.yaml` 钉 `fastp=0.23.4`（L9），镜像 tag 同为 `0.23.4`。
  **容器确实跑过的证据**不是作业 rc=0，而是该次日志里出现引擎自己的容器激活行
  `Activating singularity image containers/fastp_0.23.4.sif`（本机 7.28.1 现跑复现此行，
  source 为 `snakemake/shell.py` L206 的 `logger.info`），且 fastp 的 `logs/fastp/<sample>.log` 非空。
  digest 记法与核对方式：Quay 的 tag 页给 `docker-content-digest`，本次实查（2026-11-10）`0.23.4--h5f740d0_0` 对应
  `sha256:b635334b6bb25eba14d0b8c240a45a51234984247d79715f8cd0b7959df850c2`；
  `apptainer inspect` 里 `glibc: Debian GLIBC 2.28-10`。digest 是**该标签在某时点指向的内容身份**，
  不是「该 tag 永久不变」——换机器前重新核对，变了说明镜像被重建过。若宿主上 `fastp --version` 是别的版本，那是主环境外的另一份安装，不代表 per-rule 环境（见步骤 0）。
- **出错信号**：计算节点拉取 `docker://` 失败 → 回登录节点预拉取本地 `.sif`；求解期 `UnsatisfiableError`
  （形如 `would require __glibc >=2.28`）与运行期 `GLIBC_2.xx not found` 是两类不同失败 → 按教材 §23.5.5
  分「求解还是运行」定位，处置有换兼容旧构建、单 rule 容器、换新节点三条，不写「conda 一概无能为力」。

### 步骤 9：交叉验收与提交

- **目的**：把项目交给**另一账号**跑通——本作业的验收不是助教读报告，是同学在他自己账号下跑一遍。
- **命令**（验收同学侧；你只负责交接一个自包含目录）：

  ```bash
  ME=your_account          # ← 项目作者的集群账号
  PEER=peer_account        # ← 验收同学的集群账号
  # 交付前在作者侧放开读权限：项目目录、镜像文件、作业脚本都要能被别人读到
  chmod -R a+rX /d3/scratch/${ME}/ngs/m08_project
  mkdir -p /d3/scratch/${PEER}/ngs
  cp -r /d3/scratch/${ME}/ngs/m08_project /d3/scratch/${PEER}/ngs/m08_accept
  cd /d3/scratch/${PEER}/ngs/m08_accept
  ls m08_run.job containers/fastp_0.23.4.sif   # 自包含：作业脚本与镜像都在目录里，不必跨账号去作者目录取
  rm -rf .snakemake results                           # 先清缓存：per-rule 环境就住在 .snakemake/conda 下
  snakemake --use-conda --conda-create-envs-only -c 1  # 再按他的账号重建环境（无外网约束同上）
  python3 scripts/make_demo_data.py --outdir data     # 仅当交的是演示数据项目
  # 作业脚本沿用目录内的 m08_run.job，只改作业名（cd 与 container: 都是项目内相对路径，无需改）：
  sed -e "s/-N m08_run/-N m08_accept/" m08_run.job > m08_accept.job
  grep -n 'm08_accept\|m08_project' m08_accept.job   # 改完先看：作业名已换
  qsub m08_accept.job && qstat -u ${PEER}
  ```

  镜像跟着项目走（`container:` 写相对项目根的 `containers/fastp_0.23.4.sif`），所以同学在自己目录里
  重建环境后直接能跑容器版，不必去读作者 scratch 的绝对路径、也不必重新联网拉镜像——这正是把
  `container:` 改成项目内相对路径的理由（绝对路径换账号、换机器就是死链，教材 §23.5.8）。
  想验「镜像也要对方重新拉」，就让他删 `containers/` 后自己 `apptainer pull` 一次，差别写进 handover。
  为什么 `rm -rf .snakemake results` 必须排在 `--conda-create-envs-only` **之前**：「重建」才是交叉验收
  要证明的事，而 per-rule 环境就建在 `.snakemake/conda/` 下，先建环境再删目录等于把刚建好的环境删了。
  若你想验的正是「带执行记录交付」的另一种情形，就保留 `.snakemake/` 与 `results/` 直接跑 `-n` 看是否
  全命中——两种验法都要在 handover 里写清你选的是哪一种（教材 §23.5.2 对交付口径的两种要求）。
- **产出文件**：对方跑通的终端记录、README 三问（这是什么 / 怎么跑 / 产出什么）、交叉验收记录
  （验收人姓名、实际执行的命令、结果）——写进 handover 第 5 节。
- **检查点**：交叉验收在你之外的环境通过；`handover.md` 五节齐全（改造对象 / rule 划分依据 /
  断点续跑演示 / 资源判读 / 交叉验收记录）。
- **出错信号**：只在你的机器可跑 → 查路径（是否残留个人绝对路径）、环境（per-rule 环境是否重建）、
  输入（清单路径与校验和）、参数与种子记录是否齐全；直接提交配套流程原样只改名字，按作业诚信条款计未完成。

## 4. 结果记录表（学生填写）

> 只列栏目与单位，不预填你的结果。判据列注明来源：「手算」= 教材给算式可在纸上复核；「配置事实」=
> config/脚本的现读默认值；「本机引擎复跑」= 只证明引擎行为（命令 + 输出行可复核），产生元数据的那次
> 真跑用的是本机 fastp 1.0.1 / salmon 1.10.0（非同 pin），不是本机生物学结果；「unverified」= 未实测。

| 步骤 | 栏目 | 单位/口径 | 你的结果 | 自查判据（来源） |
|---|---|---|---|---|
| 0–1 | snakemake / quarto / R / graphviz 实装版本 | 版本号 | | snakemake 7.28.1（yml pin）；quarto 未 pin，记实装值；R 4.3.1（主环境） |
| 1 | 样本数 × 转录本数 × 每样本读段对 | 个 | | 4 × 60 × 20000（合成输入事实，教材 23.1） |
| 3 | `-n` 空跑 total 与构成 | 个 | | 手算 12 = all 1 + fastp 4 + index 1 + quant 4 + merge 1 + report 1（教材 23.4.2） |
| 3 | DAG 节点数与分支 | 个 | | 与 `-n` 计划一致；箭头方向符合「倒推依赖」（定性） |
| 4 | 每 rule 墙钟 s / max_rss / max_vms / cpu_time | s / MB / MB / s | | 四列语义按教材 23.4.5；申请内存 = max_rss × 1.3–2（手算口径），max_vms 不定内存 |
| 5 | fastp 产物：每样本双端 + html/json | 文件数 | | 4 样本齐全、非空（定性）；保留率 unverified，不预填 |
| 5 | quant.sf 表头 | 列名 | | Name/Length/EffectiveLength/TPM/NumReads 五列（merge 脚本 L20 强校验） |
| 5 | 矩阵维度（转录本 × 样本）与检测数 | 行 × 列 | | 演示输入 60 × 4（生成器默认）；实际检测数 unverified，实跑填写 |
| 6 | 删产物实验 A1 / A2 / A3 | 个（total）+ reason 文本 | | 手算见步骤 6 检查点（A1 0；A2 1；A3 3；删目标侧矩阵 3、删报告 2；教材 23.4.2/23.4.3）；本机引擎复跑同值（非课程 pin，集群未实测） |
| 6 | 改参实验 fastp 的 reason 与合计 | 文本 + 个 | | 手算 $4+4+1+1+1=11$（构成见步骤 6）；`--rerun-triggers mtime` 对照为 `Nothing to be done`（教材 23.4.3；本机引擎复跑） |
| 7 | 报告活性：改参前后数字对照 | 文字说明 | | 先核触发与接线，再看报告；Q40 数据下数字可不变（教材 23.4.6） |
| 7 | env_snapshot.yml 是否归档 | Y/N | | `conda env export --from-history`（教材 23.4.6 尾部快照） |
| 8 | 镜像 tag + digest + 容器内外版本 | 文本 | | tag 是下限、digest 是锁定（教材 23.4.4）；作业 ③ 第 6 步的必做项 |

## 5. 失效条件对照（教材 §23.5 硕士层条目：本实验在哪一步、看什么能察觉）

1. **通配符歧义让规则抓错输入（§23.5.1）**｜步骤 3。查：`-n` 里逐行读 `wildcards`，绑定值含 `/`
   （如 `sample=clean/CK_1`）就是贪婪；新增 rule 时比对输出前缀是否与既有 rule 同前缀——项目首部已有
   `wildcard_constraints: sample=r"[A-Za-z0-9_.-]+"`（Snakefile L47–48），但约束挡不住「两个合法绑定」。
   合成复现：`demos/ch23_wildcard_ambiguity.py --selftest`（500/500 对 0/500）。
2. **改了参数、输出已存在，下游不重建（§23.5.2）**｜步骤 6。查：改参后先 `-n`，`reason` 应出现
   `Params/Code have changed`；若 `Nothing to be done`，查 `.snakemake/` 是否随结果搬走（配套 `.gitignore`
   排除了它）、mtime 是否被保留（`rsync -t`、解包、`touch`）；处置 `-R <rule>` 或 `--cleanup-metadata`，
   不删整个记录目录。**第二个误导形态**（A1）：删 `quant.sf` 这类中间产物后按默认目标空跑也是
   `Nothing to be done`——增量判定只从目标倒推；`--summary` 里该行同时写 `missing` 与 `no update`。这不是缓存损坏，处置是点名该文件当目标。
3. **计算节点找不到命令，登录节点正常（§23.5.3）**｜步骤 4。查：作业日志出现 `snakemake: command not found`
   或 `fastp: command not found`；对照登录/计算节点的 `command -v`，确认作业脚本自激活并自检、
   `--cluster` 串内有 `-S /bin/bash`；SGE 默认不导出登录环境（`-V` 才带入），SLURM 默认导出（`--export=NONE` 才不继承）。
4. **目录锁与元数据误删（§23.5.6）**｜步骤 4/6 的重跑。查：`Directory cannot be locked` 时先 `ps`/`qstat`
   确认没有别的实例，再 `snakemake --unlock`；永远不用 `rm -rf .snakemake/` 代替解锁。
5. **输入缺失或路径基准错误（§23.5.7）**｜步骤 1–3。查：`MissingInputException` 时先 `ls` 核文件真实存在
   且非空，再核当前工作目录或 `-d`；`cat -A samples.tsv` 查制表符；当前脚本遇空格分隔在**读清单阶段** 报缺列，不会带错表进入 DAG；禁止 `touch` 造空输入。

> 教材 §23.5.4/23.5.5/23.5.8/23.5.9 是博士层条目（Nextflow 缓存、容器边界、死链与非 ASCII 路径、
> 引擎版本漂移），不在本实验范围；步骤 8 的 glibc 二分是 §23.5.5 的入口体验，硕士层只需记住
> 「报错在求解还是运行」这一问。

## 6. 思考题（教材 §23.7 硕士层习题 1–6，不给答案）

1. 你有一段能跑通的手敲命令，里面写死了 `/home/you/data/` 与样本名 `CK_1`：① 把它参数化要改哪四处，
   每一处分别改成什么？② 只加 `set -e` 而不加 `pipefail`，哪一类失败仍会被吞掉？举一个具体命令。
   ③ 把脚本拷到 `/tmp` 用相对路径调用，检验的是什么？（§23.7 习题 1 → 23.4.1）
2. 一条 rule 输出 `results/{sample}.bam`，另一条输出 `results/{sample}.sorted.bam`，目标
   `results/A.sorted.bam` 会被哪条命中、绑定各是什么？成本最低的消歧改法是哪个，为什么字符集约束救不了这一例？（§23.7 习题 2 → 23.4.2）
3. 四样本流程 `snakemake -n` 显示 `total 12`：写出 12 的构成；`fastp` 只显示 1 个时先查什么、怎么查；
   删掉 `rule all` 会发生什么，为什么？（§23.7 习题 3 → 23.4.2/23.4.3）
4. 某 rule benchmark 为 `s=7200`、`max_rss=3200`、`max_vms=48000`、`cpu_time=7100`、`threads: 16`
   （教材设例）：申请多少内存、给多少线程？哪一列不能用来定内存？若把 `threads` 从 16 改成 2、命令文本不动，需要重跑吗？（§23.7 习题 4 → 23.4.5/23.4.3）
5. 集群无 root、计算节点无外网、宿主 glibc 偏旧：conda 可能在哪两个阶段失败、错误长什么样？容器解决的是
   哪一层？镜像要写到什么粒度才算锁定？（§23.7 习题 5 → 23.4.4）
6. 你要交付「活的报告」：路径以什么形式传入、为什么？用什么判据验收活性？报告尾部要留哪两类快照？
   结果目录没带 `.snakemake/` 时 `-n` 说 `Nothing to be done`，该不该信这批数字？（§23.7 习题 6 → 23.4.6/23.5.2）

## 7. 提交物

- **对应作业**：`08_assessment/master/assignments/m08_workflow_engineering_assignment.md`，文件名
  `学号_姓名_m08.zip`（≤ 50 MB）。评分维度：完整性 50 / 规范性 30 / 报告质量 20；权重占课程总成绩 3.5%。
- **两种数据轨道的打包口径分开**（作业规格的 50 MB 上限与「交 results/」两条要求本身尚未统一，
  遇到助教口径不一致时按本段处理并注明，由总编统一发布最终规格）：
  - **真实数据**（`PRJDB36269` 每样本 300 万条、m04+m05 约 4 GB，`06_data/master/README.md` m04 节）：
    `data/`、`results/`、`logs/`、`benchmarks/`、`.snakemake/` **不要打进 zip**——只交代码、配置、清单、
    报告与 `dag.png`，在 README 里写明「原始数据与中间结果按此清单重跑可得」。判断口径是「重跑一次的总字节数」，不是「能不能压缩」。
  - **合成演示数据**（`data/` 共 8 个读段文件 = 样本数 $4 \times$ 端数 $2$，转录本 60 条 × 1500 bp）：
    可随包提交，便于同学交叉验收时不用重新生成；仍要保证 zip ≤ 50 MB。
- **目录结构**（与作业 ② 一致）：`README.md`（三问）、`config.yaml`、`samples.tsv`（四列、制表符）、
  `Snakefile`（3–5 条 rule + `rule all`，每条含 `input/output/params/threads/log/benchmark/shell`
  与 `conda:`）、`envs/*.yaml`、`scripts/`、`report/report.qmd`、`logs/`、`benchmarks/`、`dag.png`、`results/`。
  作业 ③ 第 3 步要求 `log:`/`benchmark:` 路径「都带 wildcards」——按**该 rule 实际有几个并发实例**落实：
  带 `{sample}` 的 rule（`fastp`／`salmon_quant`）必须有；`salmon_index`／`merge_counts`／`report` 全流程
  只有一个实例，固定路径（`logs/salmon/index.log`）才是对的，凭空加 `{sample}` 没有值可填（作业原文与这条
  口径的差异已上报总编统一，不要自行裁决）。`log` 一律只写在 `log:`，不得进 `output:`。
- **一个必须知道的打包事实**：配套流程的 `.gitignore` 排除了 `data/`、`results/`、`logs/`、`benchmarks/`、
  `.snakemake/` 与 `dag.png`，而 `git bundle` 只打包被跟踪的文件，**不可能**同时包含这些交付物——
  按上面的轨道口径用目录 zip，并在 README 里写明执行记录（`.snakemake/`）是带上还是让对方整目录重跑（教材 23.6.3）；**不要声称 bundle 里已包含被忽略的文件**。
- **handover.md（≤ 2 页）五节**：① 改造对象（选了 m02–m07 哪个专题、原命令与痛点）② rule 划分依据
  （每条的 input/output；哪些参数进了 `config.yaml`、为什么）③ 断点续跑演示（步骤 6 的 A1/A2/A3 与 B/B2
  五段 `-n` 输出：指出 A1 的 `Nothing to be done` 与 `--summary` 的 `missing`/`no update` 为何并存、
  A2 的 `wildcards`、A3 的 `Updated input files`、B 的 `Params have changed`、B2 退回 mtime 的对照）
  ④ 资源判读（从 benchmarks 挑一条 rule，给 `h_vmem` 与 `threads` 及理由，用 `max_rss` 不用 `max_vms`，
  余量 1.3–2 倍）⑤ 交叉验收记录（验收人姓名、实际执行的命令、结果）。
- **可重复性三处硬要求**（缺一按未完成计）：全部阈值只在 `config.yaml` 并随 git 版本化；`report.qmd`
  有「阈值与参数记录」节（经 `-P` 传入）；报告尾部 `sessionInfo()` + `conda env export --from-history`。
- **交叉验收规则**：截止前 5 天内完成，验收同学与你不能互为对方的验收人；记录含姓名与实际执行的命令。
  用演示数据的项目完整性上限 80 分；直接提交配套流程原样按未完成计。截止：m08 课后第 14 天 23:59。

## 8. 附：教材/讲义/脚本指针

| 内容 | 位置 |
|---|---|
| 教材主章（概念/失效条件/习题/自检） | `textbook/chapters/ch23/manuscript.qmd` §23.4 / §23.5 / §23.7 / §23.10 |
| 本专题讲义（④ 原理、⑤ 八步骤、⑥ 结果解读、⑨ 排查 1–7） | `02_lectures/master/topic08_workflow_engineering/08_workflow_engineering_lecture.md` |
| 配套流程（本实验的操作对象） | `03_code/master/pipelines/`（`Snakefile` / `config.yaml` / `samples.tsv` / `envs/` / `scripts/` / `report/report.qmd`） |
| 合成自查演示（课程仓库根目录运行，均带 `--selftest`） | `textbook/demos/ch23_wildcard_ambiguity.py`、`ch23_stale_output_mtime.py` |
| 数据说明与真实数据规模 | `06_data/master/README.md` m04 节；`06_data/accessions.tsv` L51（PRJDB36269） |
| 环境定义 | `07_envs/conda/env_master_workflow.yml`（`ngs_ms_workflow`）；per-rule 环境在项目 `envs/*.yaml` |
| 作业规格 | `08_assessment/master/assignments/m08_workflow_engineering_assignment.md` |
