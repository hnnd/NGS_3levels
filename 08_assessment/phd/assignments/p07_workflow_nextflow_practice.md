# 博士专题实践 p07：Nextflow 流程跑通、缓存验证与范式对照

| 项目 | 内容 |
|---|---|
| **对应专题** | `p07` Nextflow / Snakemake 工作流开发（`02_lectures/phd/topic07_workflow_nextflow/07_workflow_nextflow_lecture.md`） |
| **权重** | 占课程总成绩 **3%**（专题实践 27% 的一部分，契约 `assessment.materials`） |
| **运行环境** | `ngs_phd_workflow`（`07_envs/conda/env_phd_workflow.yml`）。Docker / Singularity 不在其中（契约 `env_exempt_tools`） |
| **配套流程** | `03_code/phd/workflows/`（`main.nf` / `nextflow.config` / `conf/` / `modules/local/` / `subworkflows/local/` / `bin/`）｜**对照物**：`03_code/master/pipelines/`（硕士 m08 的 Snakemake 版，功能等价） |
| **建议用时** | 上机 4–5 小时，写报告 2 小时 |

> ## ⚠ 开工前必读：纯英文路径硬约束
>
> **本课程仓库路径含中文（`.../课程/研究生/...`），Nextflow 24+ 在含非 ASCII 字符的路径下会把所有 `include` 判为 `Invalid include source`，流程根本编译不过**（契约 `delivery.nextflow_ascii_path_required`，讲义 ⑨-3 实测记录）。
>
> **第一条命令就是**：`cp -r 03_code/phd/workflows ~/p07_nf && cd ~/p07_nf`
>
> 报错信息极具误导性（它看起来像文件不存在），不知道这一条会在第一步卡住。**把流程交给合作方时也要说明这一点。**

## ① 任务背景

本讲的起点不是零。硕士 m08 已经教过 rule / input / output / wildcards / `rule all` / `expand` / `--use-conda`，因此本作业**不考"为什么要用工作流引擎"**，只考下一个问题：**当流程要给别人用、要在几百个样本上跑、要在两年后被审稿人重跑时，Snakemake 的哪些设计开始变成阻力，Nextflow 用什么换掉了它，代价是什么。**

本作业的验收方式是**数字而非截图**：`-stub-run` 的 `completed=10`、`-resume` 的 `cached=`。讲义 ⑥ 那三种"结果不对"的形态里，**前两种不报错**——`completed=7` 而状态仍是 SUCCESS，是本讲最重要的一课：**任务数与样本数对不上，就是 channel 接线错了，不要去看日志找报错——不会有报错。**

本作业与 `phd_code_assignment.md`（代码作业 18%）的分工：**本次是"跑通配套流程并读懂它"，代码作业是"把你自己的分析写成流程"。** 本次的步骤 7（把自己的 Snakefile 转过来）是代码作业的起点。

**评分表里「AI 使用与验证记录」占 10%**（契约 `ai_verification_log`）。p07 不在 `stats_plugin_topics` 名单内（讲义 ⑦ 明确写"本讲无独立统计要点"），因此**没有**独立的「方法选择与结果可信度说明」评分栏。

## ② 交付物

打包为 `学号_姓名_p07.zip`：

```
学号_姓名_p07/
├── report.pdf                        # 主报告，正文 ≤ 6 页
├── run_logs/
│   ├── stub_run.log                  # -stub-run 的完整输出（含 completed= 那一行）
│   ├── resume_1.log                  # 完整跑一遍
│   ├── resume_2.log                  # 删一个中间结果后 -resume
│   ├── resume_3.log                  # 改 --fastp_qual 30 后 -resume
│   └── run_counts.tsv                # 三次运行的 completed= / cached= 汇总 + 每个数字的解释
├── artifacts/
│   ├── dag.html                      # -with-dag 产出
│   ├── trace.txt                     # 资源实测（peak_rss / realtime / %cpu）
│   └── report.html                   # -with-report 产出
├── work_dir_forensics.md             # 任选一个任务，贴出 .command.sh 并说明它与你以为的差别
├── paradigm_comparison.md            # ⑩ Q5：Snakefile 与 main.nf 三处等价但写法不同的地方
├── ai_logs/prompt_and_reply.md       # ⑧ 的原文往返（含你告诉它的 Nextflow 版本号）
├── results/ai_audit.tsv              # ⑧ 的五条核查结论表
└── env_snapshot.yml
```

报告正文必须含以下五节：

| 节 | 内容 | 对应讲义 |
|---|---|---|
| 1 环境与路径约束 | 你实际用的 Nextflow 版本号；纯英文路径的处置 | ⑤、⑨-3 |
| 2 空跑与 DAG | `completed=10` 的四项分解（4×FASTP + 1×SALMON_INDEX + 4×SALMON_QUANT + 1×MERGE_COUNTS）；对照 `quantify.nf` 说明接线 | ⑤ 步骤 2、3 |
| 3 缓存三连 | 三次 `-resume` 的数字与**每个数字的解释**；第三次为什么 `SALMON_INDEX` 仍命中 | ⑤ 步骤 5、⑥ |
| 4 work 目录取证与资源 | `.command.sh` 的插值结果；`trace.txt` 的 `peak_rss` 与 `%cpu` 判读 | ⑥ |
| 5 范式对照 | ⑩ Q5 的三处；以及 ⑩ Q1 的 channel 派生任务数推演 | ⑩ Q1、Q5 |

## ③ 完成步骤

1. **拷到纯英文路径**（见上方警示），`nextflow -version` 记下版本号——**它决定语法严格程度**（⑨-1/⑨-2）。
2. **造演示数据**：`python3 <课程仓库>/03_code/master/pipelines/scripts/make_demo_data.py --outdir demo --reads-per-sample 3000`（固定随机种子，离线可生成）。
3. **空跑**：`nextflow run . -stub-run -profile test`，**期望 `completed=10`。这个数字是验收标准**——出现 7 或 4 就是 channel 接错了，回讲义 ④2 找原因。
4. **DAG**：`-with-dag dag.html`，浏览器打开后对照 `subworkflows/local/quantify.nf` 看接线。
5. **真跑**：`nextflow run . -profile test,conda`（首次需联网建环境；集群计算节点常无外网，**先在登录节点跑一次把环境建好**）。
6. **缓存三连**（⑤ 步骤 5）：完整跑 → 删一个中间结果后 `-resume` → 改 `--fastp_qual 30` 后 `-resume`。**三次的 `cached=` 与 `completed=` 都要记录并解释**，特别是第三次为什么 `SALMON_INDEX` 仍然命中。
7. **work 目录取证**：任选一个任务 `cd` 进 `Work dir:`，`cat .command.sh` 看**插值后的真实命令**。养成第一动作是进 work 目录，而不是回头改代码。
8. **AI 任务（⑧）**：贴上你自己的 Snakefile（含 `config.yaml` 与 `samples.tsv`）让 AI 转成 DSL2，**把你的 Nextflow 版本号告诉它**，按五条核查填 `ai_audit.tsv`。
9. **集群提交（可选加分项，不单独计权重）**：`-profile test,singularity,slurm --queue <你的队列> -resume`，观察 Nextflow 自己在提交、排队、回收。

## ④ 评分标准

总分 100，折算为课程总成绩的 3%。

| 评分维度 | 权重 | 评分要点 |
|---|---|---|
| **完成度与结果正确性** | 50 | 交付物 ② 齐全；`-stub-run` 达到 **`completed=10`**；三次 `-resume` 日志完整且 `run_counts.tsv` 的每个数字都有解释；`dag.html` / `trace.txt` / `report.html` 三件产出齐全；`work_dir_forensics.md` 贴的是真实 `.command.sh` |
| **判断与讨论质量** | 28 | 第三次 `-resume` 中 `SALMON_INDEX` 命中的原因解释正确（`fastp_qual` 不出现在它的脚本里）；`trace.txt` 的 `%cpu` 与 `cpus` 声明不匹配时能指出问题（⑩ Q3）；⑩ Q1 的三种 channel 情形任务数推演正确；`paradigm_comparison.md` 的三处对照说清"两种范式为什么会长成那样" |
| **AI 使用与验证记录** | 10 | 见下方口径 |
| **报告质量** | 12 | 五节结构完整；版本号与路径约束写明；日志为原始输出未经编辑；图表标签英文 |

### 「AI 使用与验证记录」的评分口径（契约 `ai_verification_log`）

记录四要素：**用了什么提示（原文）** / **AI 给了什么** / **哪里错了** / **你是怎么发现的**。本次落点是讲义 ⑧ 的五条核查，**逐条写结论，不是"看起来没问题"**：

| # | 核查什么 | 怎么查 | AI 的典型错法 |
|---|---|---|---|
| 1 | **channel 消费语义** | 找出所有"1 份参考 / 1 个索引"的输入，确认它来自 value channel 或经 `.first()`/`.collect()` | 直接把 `SALMON_INDEX.out` 接给逐样本 process——Snakemake 里索引是普通文件依赖可被反复引用，**Nextflow 的 queue channel 不能** |
| 2 | **并发行为** | 数 `-stub-run` 的 `completed=`，与"样本数 × 步骤数 + 汇总步骤"对比 | 该逐样本的写成了 `collect()`，或该汇总的没 `collect()` |
| 3 | **`-resume` 缓存** | 连跑两次 `-resume`，第二次必须全 `cached` | 汇总步骤用 `collect()` 导致输入无序，缓存永不命中 |
| 4 | **资源声明** | 逐条比对 `threads:` 与 `label`/`cpus`；确认 shell 里用 `${task.cpus}` 而非写死数字 | 资源声明整个丢失，或翻译成写死的 `-p 8` |
| 5 | **结果一致** | 同一份小数据两版都跑一遍，`md5sum` 逐文件比对 | 输出目录结构或文件名变了，`publishDir` 漏了某类产物 |

> **第 1 条是 AI 几乎必错的地方，而且错了不报错**——它是"AI 输出看起来完全合理但语义已经变了"的教科书案例。**你能不能靠 `completed=` 这个数字把它抓出来，比你会不会写 DSL2 更重要。**
>
> 若某次 AI 恰好写对了，也要写清你**验证过**它对。**未使用 AI 完成某一步时写明原因即可，不扣分；但通篇声称 AI 输出全部正确且无验证过程的，本栏不得分。**

## ⑤ 提交方式与截止

- **提交入口**：课程 LMS「专题实践 p07」；文件名 `学号_姓名_p07.zip`（≤ 50 MB，不要打包 `work/` 目录）
- **截止时间**：p07 课后 **第 7 天 23:59**（代码作业以本次为起点，逾期会连带压缩代码作业的时间）
- **迟交**：3 天内按 90% 计，超过 3 天按 70% 计，超过 7 天不计分（可申请一次不扣分延期，须在截止前提出）
- **重交**：允许在截止前重复提交，以最后一次为准
- **诚信**：日志必须是你自己机器/账号上跑出来的（`trace.txt` 含主机与时间信息）；提交他人日志按学术不端处理

## ⑥ 常见失分点

| # | 失分点 | 长什么样 | 怎么自查 |
|---|---|---|---|
| 1 | **没拷到纯英文路径**（⑨-3） | `Invalid include source: '/path/to/subworkflows/local/quantify.nf'` | 本仓库路径含中文，Nextflow 24+ 必然报此错。另一个独立原因是 `include` 省略了 `.nf` 后缀 |
| 2 | **`completed=7` 却当成成功**（⑥ 第 1 种） | 状态是 SUCCESS，计数矩阵少了几列 | queue channel 被第一个任务消费光，其余样本**静默饿死**。判据：任务数与样本数对不上就是接线错，**不会有报错** |
| 3 | **每次 `-resume` 都全量重跑**（⑥ 第 2 种、⑨-7） | `cached=0` | 按序自查：`collect()` 换 `toSortedList()` → 脚本里有没有时间戳/随机数/`$PWD` → 换过机器或 `work/` 目录 → 输入被重新生成过 → 改了 `container`/`conda` 声明 |
| 4 | **`publishDir` 里是上一次的结果**（⑥ 第 3 种） | 结果存在但内容陈旧，或断链 | `mode: 'symlink'`（默认）指向 `work/`；**教学与交付一律用 `mode: 'copy'`** |
| 5 | **配置里写 `def` 变量**（⑨-1） | `Variable declarations cannot be mixed with config statements` | 24+ 严格解析器。去掉时间戳，用 `-with-report run1.html` 显式指名 |
| 6 | **脚本顶层写 `workflow.onComplete`**（⑨-2） | `Statements cannot be mixed with script declarations` | 旧写法 23.x 能跑、24+ 不能。最稳的是不写它 |
| 7 | **输出 glob 与实际文件名对不上**（⑨-4） | `Missing output file(s) '*.clean.fq.gz'`，而命令里产出的是 `*.cleaned.fq.gz` | 报错里已经把真实命令打出来了。`cd` 进 `Work dir:` `ls -la`。**永远从第一个报错查起** |
| 8 | **任务被 OOM 杀掉**（⑨-5） | `terminated with an error exit status (137)` | 137 = 超内存，143 = 超时。**要多少内存不要猜**——看 `trace.txt` 的 `peak_rss` 按 1.5–2 倍申请 |
| 9 | **集群上 `command not found`**（⑨-6） | `.command.sh: line 3: salmon: command not found` | 作业不继承登录 shell 环境。靠 `-profile conda`/`singularity` 让每个 process 自带环境；SGE 还须在 `clusterOptions` 写 `-S /bin/bash` |
| 10 | **只交截图不交日志** | 报告里贴了终端截图，没有 `run_logs/` | 本次验收依据是数字，助教要能在日志里 `grep` 到 `completed=` 与 `cached=` |
