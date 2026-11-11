# 博士代码作业：把你自己的分析链写成可交付的工作流

| 项目 | 内容 |
|---|---|
| **对应专题** | `p07` Nextflow / Snakemake 工作流开发（`02_lectures/phd/topic07_workflow_nextflow/07_workflow_nextflow_lecture.md`），并综合 p02–p06 的任一条分析链 |
| **权重** | 占课程总成绩 **18%**（契约 `assessment.levels.phd` 的「代码作业」项，是博士层除课题方案外最重的一项） |
| **运行环境** | `ngs_phd_workflow`（`07_envs/conda/env_phd_workflow.yml`）+ 你的分析链所需环境 |
| **参照实现** | `03_code/phd/workflows/`（Nextflow DSL2）｜ `03_code/master/pipelines/`（Snakemake，功能等价） |
| **建议用时** | 12–16 小时，分散在 p07 课后两周内完成 |

> ## ⚠ 纯英文路径硬约束（契约 `delivery.nextflow_ascii_path_required`）
>
> **Nextflow 24+ 在含非 ASCII 字符的路径下会把所有 `include` 判为 `Invalid include source`。** 本课程仓库路径含中文，因此**开发目录必须是纯英文路径**（如 `~/my_p07_project/`）。报错信息看起来像"文件不存在"，极具误导性（讲义 ⑨-3 实测记录）。
>
> 交付时**必须在 README 里写明这条约束**——这是你把流程交给合作方时对方第一个会踩的坑。

## ① 任务背景

p07 的专题实践（3%）是"跑通配套流程并读懂它"。本作业是下一步，也是本课程唯一一次完整的**工程交付**：**把你自己毕业课题里最核心的那条分析链，写成一条别人能跑、两年后你自己也能跑的流程。**

它占 18%，理由在大纲 `syllabus_phd.md` 的考核重心里：博士生毕业后要独立决定"用什么数据回答什么问题"，而一条别人跑不通的分析链等于没有结果。讲义 ⑦ 那句话是本作业的验收哲学：**代码公开而参数不公开，等于没公开**——审稿人问"你的过滤阈值是多少"，`nextflow.config`（或 `config.yaml`）就是答案。

**允许你选 Snakemake 而不是 Nextflow**（⑩ Q6 明确写了"允许结论是继续用 Snakemake，但必须说清依据"）。选哪个不影响得分，**不写选择依据才扣分**。

**评分表里「AI 使用与验证记录」占 10%**（契约 `ai_verification_log`，博士层全部考核材料强制）。本作业不在 `stats_plugin_topics` 名单内，无独立的方法说明栏——**统计判断由被封装的那些专题的作业承载**（p02/p04/p05/p06）。

## ② 交付物

一个 **git 仓库**（打包为 `学号_姓名_code.zip`，含 `.git/` 目录——提交历史是评分依据之一）：

```
学号_姓名_code/
├── README.md                       # 三个问题：这是什么、怎么跑、跑出来是什么
│                                   # 必须含：纯英文路径约束、引擎选择依据、版本号
├── main.nf + nextflow.config        # Nextflow 路线
│   或 Snakefile + config.yaml       # Snakemake 路线（二选一）
├── modules/ 或 rules/               # 一个 process/rule 一个文件
├── subworkflows/                    # Nextflow 路线；Snakemake 可用 include
├── conf/ 或 profiles/               # 本机 / 集群（SGE 或 SLURM）/ 容器
├── bin/                             # 自写脚本；不在流程里写绝对路径
├── assets/samples.csv 或 samples.tsv # 样本清单
├── envs/                            # 每步一个 conda yaml（或容器声明）
├── test/
│   ├── make_demo_data.py            # 或复用课程的；固定随机种子、离线可生成
│   └── expected_task_counts.md      # 空跑应有的任务数及其分解 —— 你自己的验收标准
├── docs/
│   ├── dag.html                     # -with-dag 或 --dag 产出
│   ├── params_rationale.md          # 每个 params 的含义与定值依据（审稿人会问的那些）
│   └── reproducibility_checklist.md # ⑩ Q7⑤：三年后复现第 X 章需要哪几个文件
├── run_logs/
│   ├── stub_or_dryrun.log           # -stub-run（或 snakemake -n）
│   ├── full_run.log
│   ├── resume_nochange.log          # 不改任何东西再跑，应全部 cached
│   └── resume_paramchange.log       # 改一个阈值再跑，观察哪些重跑
├── trace.txt + report.html          # 或 Snakemake 的 --report
└── .gitignore                       # 代码入库、数据不入库
```

**同时提交** `handover_note.md`（≤ 2 页，可放仓库根目录）：

| 节 | 内容 | 对应讲义 |
|---|---|---|
| 1 DAG 说明 | 哪些步骤逐样本、哪些必须等全部样本到齐；各几个 | ⑩ Q7① |
| 2 运行时才知道输出数量的步骤 | 有没有（组装出多少 contig、聚类出多少 OTU）；Snakemake 用 `checkpoint`，Nextflow 怎么表达 | ⑩ Q7② |
| 3 引擎选择依据 | 几台机器、几种调度器；据此选 Snakemake 还是 Nextflow | ⑩ Q7④、Q6 |
| 4 资源实测 | `trace.txt` / benchmark 的 `peak_rss` 与实际申请值的关系 | ⑥ |
| 5 交叉验收记录 | 同学在**他自己的账号下**跑通的证据（截图或日志片段 + 他的一句话确认） | ④ 的验收条款 |

## ③ 完成步骤

1. **选链**：从你毕业课题里挑**最花时间、最常重跑**的那条分析链（⑩ Q7）。**不要选课程示例数据**——本作业的价值在于你以后真的会用它。数据敏感时可用结构相同的模拟数据，在 README 写明。
2. **先画 DAG 再写代码**：哪些逐样本、哪些汇总，先在纸上定下来。`handover_note.md` 第 1 节就是这一步的产物。
3. **按讲义 ⑤ 步骤 7 的顺序开发**：先写单个 process 跑通 → 再接成 workflow → 再拆进 `modules/` → 最后把参数全部移进配置文件。**顺序不要颠倒**——一上来就模块化，出了问题分不清是接线错还是命令错。
4. **造演示数据**：固定随机种子、离线可生成、体量小到能在几分钟内跑完。**这是交叉验收的前提**——同学不可能有你的真实数据。
5. **写下你自己的验收数字**：`test/expected_task_counts.md` 写明空跑应有多少任务及其分解（如"4 样本 × 3 步 + 2 个汇总 = 14"）。**这个数字是你自己的 `completed=10`**——没有它，channel 接错了你不会知道（讲义 ⑥ 第 1 种形态，**不报错**）。
6. **缓存验证**：不改任何东西再跑一次，**必须全部 cached**；再改一个阈值跑一次，说明哪些重跑、为什么。
7. **集群 profile**：至少写一个（SGE 或 SLURM）。注意作业**不继承**登录 shell 环境（⑨-6），靠 `-profile conda`/`singularity` 或 `--use-conda` 解决；SGE 还须在 `clusterOptions` 写 `-S /bin/bash`。
8. **交叉验收**：找一位同学在**他自己的账号下**从 git clone 开始跑通，记录他遇到的每个问题——**他踩的坑就是你 README 缺的段落**。
9. **git 提交历史**：不要一次性 `git add .` 提交全部。按功能分次提交，commit message 写清做了什么。**提交历史反映开发过程，是「工程质量与可重复性」的评分依据之一。**

## ④ 评分标准

总分 100，折算为课程总成绩的 18%。

| 评分维度 | 权重 | 评分要点 |
|---|---|---|
| **流程正确性与可运行性** | 50 | **助教在独立环境中从 git clone 开始实际执行——跑不通该项不得分**；空跑任务数与 `expected_task_counts.md` 一致；不改参数再跑全部 cached；改参数后重跑范围正确；集群 profile 至少一个可用；`publishDir`/输出用 `copy` 而非 symlink |
| **工程质量与可重复性** | 28 | 参数全部在配置文件里、流程代码中无硬编码路径/阈值/线程数；一个 process/rule 一个文件；`bin/` 脚本不写绝对路径；每步有环境或容器声明；`.gitignore` 做到代码入库数据不入库；git 提交历史分次且 message 有意义；`docs/params_rationale.md` 逐条给定值依据 |
| **AI 使用与验证记录** | 10 | 见下方口径 |
| **文档质量** | 12 | README 回答"这是什么、怎么跑、跑出来是什么"三个问题并写明**纯英文路径约束**与版本号；`handover_note.md` 五节完整；`reproducibility_checklist.md` 是具体文件清单而非原则 |

> **「流程正确性与可运行性」的执行方式**：助教在干净环境中 `git clone` → 按 README 跑演示数据。**README 漏写一步导致跑不通，算跑不通**——这正是本作业要训练的能力（讲义 ⑩ Q6："如果迁，第一步做什么、怎么证明迁移前后结果一致"）。

### 「AI 使用与验证记录」的评分口径（契约 `ai_verification_log`）

记录四要素：**用了什么提示（原文）** / **AI 给了什么** / **哪里错了** / **你是怎么发现的**。

本作业**鼓励用 AI 写代码**——真实工作里你也会这么做。考的是你能否验证它。至少提交一次实质性的 AI 往返记录（放 `ai_logs/`），并按讲义 ⑧ 的五条核查给出结论：① channel 消费语义（**AI 几乎必错且不报错**的地方）；② 并发行为（数任务数）；③ `-resume` 缓存；④ 资源声明有没有丢失或写死；⑤ 结果一致（`md5sum` 比对）。

**发现路径必须具体**：是"我数了任务数发现少了 3 个"，还是"跑完发现计数矩阵少了几列"？前者说明验收数字已经内化。

> 只交"AI 错了"不给分。**未使用 AI 时写明原因即可，不扣分**（例如"这条链的每一步我都写过，直接改的旧脚本"）；**但通篇声称 AI 输出全部正确且无验证过程的，本栏不得分。**

## ⑤ 提交方式与截止

- **提交入口**：课程 LMS「代码作业」；文件名 `学号_姓名_code.zip`（含 `.git/`，≤ 100 MB；演示数据须小到可入包）
- **截止时间**：p07 课后 **第 21 天 23:59**（与课题方案设计的初稿期错开，避免两项撞车）
- **交叉验收**：`handover_note.md` 第 5 节须在截止前完成，验收同学的确认可以是邮件/聊天截图
- **迟交**：3 天内按 90% 计，超过 3 天按 70% 计，超过 7 天不计分（可申请一次不扣分延期，须在截止前提出）
- **重交**：允许在截止前重复提交，以最后一次为准
- **诚信**：允许基于课程配套流程改写（**并在 README 注明改自哪里**）；允许用 AI 生成代码（须按 ④ 记录验证过程）；**不允许**提交同学的仓库或未经改写的他人流程

## ⑥ 常见失分点

| # | 失分点 | 长什么样 | 怎么自查 |
|---|---|---|---|
| 1 | **助教环境跑不通** | README 漏了一步（建环境、造数据、必填参数） | 找同学从 clone 开始走一遍——**他踩的坑就是你 README 缺的段落** |
| 2 | **没有自己的验收数字** | `expected_task_counts.md` 缺失或写得含糊 | 任务数与样本数对不上是**唯一**能抓出 channel 接错的信号，而且**不会有报错**（讲义 ⑥ 第 1 种） |
| 3 | **参数硬编码在流程里** | `-p 8`、`/home/xxx/data/ref.fa`、`--qual 20` 直接写在 process/rule 里 | 换数据集 = 改 params，换集群 = 换 profile，**流程代码一行都不用动**（`nextflow.config` 的配置分离原则） |
| 4 | **`-resume` 完全不命中**（⑨-7） | 不改任何东西再跑仍全量重跑 | 按序查：`collect()` → 时间戳/随机数/`$PWD` → 换了机器或 `work/` → 输入被重新生成 → 改了容器/conda 声明 |
| 5 | **`publishDir` 用默认 symlink**（⑥ 第 3 种） | 结果目录里是断链，或内容是上一次的 | **教学与交付一律 `mode: 'copy'`**，集群跨文件系统尤其容易踩 |
| 6 | **集群上 `command not found`**（⑨-6） | 本机好好的，`qsub`/`sbatch` 出去就挂 | 作业不继承登录 shell 环境；靠 profile 让每步自带环境。SGE 须写 `-S /bin/bash` |
| 7 | **一次性提交全部代码** | git 历史只有一个 commit "init" | 提交历史是「工程质量」的评分依据；按功能分次提交 |
| 8 | **数据入库** | `.git/` 里有 fastq/bam，包体积超限 | `.gitignore`：代码入库、数据不入库 |
| 9 | **没写纯英文路径约束** | README 里只字未提 | 合作方第一个会踩的坑，且报错极具误导性（⑨-3、契约 `delivery.nextflow_ascii_path_required`） |
| 10 | **资源按猜的申请** | `h_vmem=64G` 但 `peak_rss` 只有 3 GB，或反过来被 OOM 杀掉 | **不要猜**——看上一次 `trace.txt` 的 `peak_rss`，按 1.5–2 倍申请（⑥、⑩ Q3） |
| 11 | **选了 Snakemake 却不写理由** | `handover_note.md` 第 3 节空着 | 允许结论是"继续用 Snakemake"，**但必须说清依据**（⑩ Q6/Q7④） |
| 12 | **`reproducibility_checklist.md` 写成原则** | "要保存代码和数据" | ⑩ Q7⑤ 要的是**具体文件清单**，并检查这些文件是不是都已经在 git 里 |
