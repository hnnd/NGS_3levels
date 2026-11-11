# 硕士专题作业 m08：可一键重跑的项目目录

| 项目 | 内容 |
|---|---|
| **对应专题** | `m08` 分析流程工程化与可重复报告（`02_lectures/master/topic08_workflow_engineering/08_workflow_engineering_lecture.md`） |
| **权重** | 占课程总成绩 **3.5%**（专题作业 37% 的一部分，契约 `assessment.materials`） |
| **运行环境** | `ngs_ms_workflow`（`07_envs/conda/env_master_workflow.yml`） |
| **配套流程** | `03_code/master/pipelines/`（`Snakefile` / `config.yaml` / `samples.tsv` / `envs/` / `scripts/` / `report/report.qmd`） |
| **建议用时** | 上机 2.5–3 小时（讲义 ⑤ 的八个步骤已给出分钟数），整理与交叉验收 1–2 小时 |
| **本讲不产生统计推断** | 因此评分表**没有**「方法选择与结果可信度说明」项——本专题不在契约 `stats_plugin_topics` 名单内（讲义 ⑦ 已写明哨兵句） |

## ① 任务背景

这次作业**不发新数据、不学新分析**。改造对象是**你自己在 m02–m07 里跑过的命令**。

你此刻大概率正处在这样的状态：换个样本得把整串命令重敲一遍；上个月那次 `fastp` 用的 Q20 还是 Q30 已经想不起来；某个中间文件被误删，只好从头再跑三小时。这次作业就是把这些手工劳动固化成**别人（和三个月后的你）能一键重跑的东西**。

验收方式因此与其他作业根本不同：**不是助教读你的报告，是同学在他自己的账号下把你的项目跑一遍**。跑不通就是没完成——这一条无法靠写得漂亮弥补。这也是本层次"流程完整性"定位最直接的检验，同一套逻辑会在期末项目的「可重复性 25 分」上再用一次，那次占分更重。

## ② 交付物

提交一个 **git 仓库归档**（`git bundle` 或 `.zip`，须含 `.git/` 目录以便查看提交历史），命名 `学号_姓名_m08.zip`。解压后结构（对齐大纲「作业与产出」）：

```
学号_姓名_m08/
├── README.md            # 回答三个问题：这是什么 / 怎么跑 / 产出什么
├── config.yaml          # 样本清单路径与全部可变参数（阈值、线程、路径）
├── samples.tsv          # 四列 sample / fq1 / fq2 / condition，制表符分隔
├── Snakefile            # 3–5 条工作 rule + rule all，含 wildcards
├── envs/*.yaml          # 每条 rule 的 conda 环境
├── scripts/             # 步骤 1 参数化后的 shell / R 脚本
├── report/report.qmd    # 参数化 Quarto 报告模板
├── logs/                # 各 rule 各样本的日志（**不要写进 output:**）
├── benchmarks/          # 各 rule 的资源占用记录
├── dag.png              # snakemake --dag 导出的依赖图
└── results/             # 可整个删除后由 snakemake 重建
```

另附一份 **`handover.md`（≤ 2 页）**，这是本次作业的"报告"，写四件事：

| 节 | 内容 | 对应讲义 |
|---|---|---|
| 1 改造对象 | 你选了 m02–m07 中的哪个专题、原来那串命令长什么样、痛点在哪 | ⑤ 步骤 1 |
| 2 rule 划分依据 | 拆成几条 rule、每条的 input/output；**哪些参数进了 `config.yaml`、为什么** | ④、⑤ 步骤 2–3 |
| 3 断点续跑演示 | 删掉一个中间结果后 `-n` 的输出，指出 `reason` 与 `wildcards` 两行说明了什么 | ⑥ |
| 4 资源判读 | 从 `benchmarks/` 里挑一条 rule，给出你会申请的 `h_vmem` 与 `threads` 及理由 | ⑥ |
| 5 交叉验收记录 | 验收同学姓名、他的执行命令、结果（通过 / 失败及原因）、你的修复 | ⑤ 步骤 8 |

## ③ 完成步骤

**按讲义 ⑤ 的八个步骤做即可**，下面只标出本次作业特有的硬要求：

1. **步骤 1（20 min）· 命令 → 参数化脚本**。验收方式：**把脚本拷到 `/tmp` 下用相对路径调用仍能跑通**——能跑通说明没有硬编码路径残留。
2. **步骤 2（10 min）· `samples.tsv` 与 `config.yaml`**。**`Snakefile` 里一个具体路径都不许出现**。写完 `cat -A samples.tsv | head` 确认分隔符是 `^I`（制表符）而不是空格。
3. **步骤 3（40 min）· 脚本 → Snakemake**。3–5 条 rule，**每条都必须有 `log:` 与 `benchmark:`，且两者路径中都带 wildcards**（否则 20 个样本写同一个文件互相覆盖）。
4. **步骤 4–5（25 min）· 验证与断点续跑**。`snakemake -n` → `--dag` → `--use-conda -c 8` → 故意 `rm -rf` 一个中间结果 → 再 `-n` 看它只打算重跑受影响的部分。**这一步的终端输出要贴进 `handover.md` 第 3 节。**
5. **步骤 6（15 min）· 容器化一步 + 集群提交**。用 BioContainers 镜像跑其中一条 rule，对比容器内外 `--version` 是否一致。
6. **步骤 7（20 min）· Quarto 报告**。判据是"**改掉 `config.yaml` 里一个阈值 → 重跑 → 报告里的数字自己变了**"。报告尾部必须固定保留 `sessionInfo()` 与 `conda env export --from-history`。
7. **步骤 8（10 min）· 打包与交叉验收**。`git init && git add . && git commit`（`.gitignore` 排除 `data/` `results/` `logs/` `.snakemake/`），然后**交给同学在他自己账号下跑 `snakemake --use-conda -c 4`**。
8. **无自备数据时**：`python3 scripts/make_demo_data.py --outdir data` 生成微型演示数据（固定随机种子）。**但用演示数据的项目在「完整性」上限为 80 分**——本讲的价值在于改造你自己的真实分析。

> **允许用 AI 辅助写 Snakefile**，但你必须能解释每一条 rule 的 wildcards 匹配方向（讲义 ④）。交叉验收失败时"AI 是这么写的"不作为理由。

## ④ 评分标准

总分 100，折算为课程总成绩的 3.5%。**本专题无独立统计要点**（讲义 ⑦），因此评分维度与 m02–m07 不同。

| 评分维度 | 权重 | 评分要点 |
|---|---|---|
| **完整性** | 50 | ② 的目录结构齐全；3–5 条 rule 均含 `input`/`output`/`params`/`threads`/`log`/`benchmark`/`shell`；`dag.png` 与断点续跑演示到位；**交叉验收通过**（同学在自己账号下 `snakemake --use-conda -c 4` 能跑通并渲染出报告）——此项不通过，本维度上限 25 分 |
| **规范性** | 30 | `Snakefile` 中无任何硬编码路径/样本名/阈值；`log:` 与 `benchmark:` 路径含 wildcards；log 未写进 `output:`；`.gitignore` 正确排除数据与 `.snakemake/`；`config.yaml` 已 git commit；脚本含 `set -euo pipefail` |
| **报告质量** | 20 | `handover.md` 五节齐全；rule 划分依据说得出理由；`-n` 的 `reason`/`wildcards` 判读正确；资源判读用 `max_rss` 而**不是** `max_vms`；Quarto 报告是"活的"（改阈值→数字自己变）且尾部有 `sessionInfo()` 与环境快照 |

> **可重复性的三处硬要求**（讲义 ⑦）：① 全部阈值只存放在 `config.yaml` 并随 git 版本化；② `report.qmd` 有「阈值与参数记录」一节，由流程经 `-P` 传入；③ 报告尾部有 `sessionInfo()` + `conda env export --from-history`。**三者缺一，本次作业按未完成计。**

## ⑤ 提交方式与截止

- **提交入口**：课程 LMS「专题作业 m08」；文件名 `学号_姓名_m08.zip`（≤ 50 MB——`results/` 与 `data/` 已被 `.gitignore` 排除，超出说明打包方式不对）
- **截止时间**：m08 课后 **第 14 天 23:59**（比其他作业多 4 天，用于安排交叉验收）
- **交叉验收**：截止前 5 天内完成，**验收同学与你不能互为对方的验收人**（避免互相放水）；验收记录写进 `handover.md` 第 5 节，须含验收同学姓名与实际执行的命令
- **迟交**：3 天内按 90% 计，超过 3 天按 70% 计，超过 7 天不计分（可申请一次不扣分延期，须在截止前提出）
- **重交**：允许在截止前重复提交，以最后一次为准
- **诚信**：流程可参考配套 `03_code/master/pipelines/`，但 rule 划分与参数化必须针对**你自己的分析**；直接提交配套流程原样（只改名字）按未完成计

## ⑥ 常见失分点

来自讲义 ⑨ 与往届作业的真实问题，**按出现频率排序**：

| # | 失分点 | 长什么样 | 怎么自查 |
|---|---|---|---|
| 1 | **`samples.tsv` 用空格而非制表符** | 不报错；`-n` 里 `fastp` 只有 1 个而不是 4 个 | `cat -A samples.tsv \| head`，列间必须是 `^I` |
| 2 | **`MissingInputException` 而文件明明在**（⑨-1） | 相对路径以**运行 snakemake 的当前目录**为基准，不是 Snakefile 所在目录 | `ls` 确认文件在 → cd 到项目根再跑，或加 `-d /path/to/project`。**不要 `touch` 造空文件糊弄** |
| 3 | **改了 `config.yaml` 阈值却 `Nothing to be done`**（⑥） | **正常但危险**：Snakemake 只看文件时间戳，不看参数变化 | 用 `-R <rule>` 强制重跑；每次改 `config.yaml` 必须 git commit |
| 4 | **拿 `max_vms` 去申请内存**（⑥） | 申请 48 G 实际只用 3.2 G，占着集群不放 | 只看 `max_rss`，乘 1.5–2 倍余量 |
| 5 | **log 写进了 `output:`**（⑨-7） | rule 失败时 Snakemake 删掉不完整输出，**唯一的排错线索也被删了** | log 只写在 `log:` 里；现场已丢时用 `--keep-incomplete` 重跑留证 |
| 6 | **wildcard 把路径吃进去**（⑨-2） | `-n` 里出现 `wildcards: sample=clean/CK_1` | 顶部加 `wildcard_constraints: sample=r"[A-Za-z0-9_.-]+"`，别等出问题再加 |
| 7 | **集群提交报 `command not found`**（⑨-4） | SGE/SLURM 作业**不继承登录 shell 的环境** | 作业脚本里自己 `source .../activate && conda activate`，并加 `command -v` 自检；`--cluster` 里也要写 `-S /bin/bash` |
| 8 | **Quarto 报告是"死的"** | 用相对路径读结果表，本地能跑，被流程从别的工作目录调用时读到旧文件——渲染成功、图也有，**数字是过期的** | 用 `-P` 传 `realpath` 绝对路径；改一个阈值重跑，看报告数字变没变 |
| 9 | **`rm -rf .snakemake/` 解锁**（⑨-3） | 元数据一起被删，下次运行认为所有输出"来路不明"而全部重跑 | 先 `ps -u $USER \| grep snakemake` 与 `qstat -u $USER` 确认，再 `snakemake --unlock` |
| 10 | **README 答不出三个问题** | 只写了"这是我的作业" | 这是什么 / 怎么跑 / 产出什么——三问缺一按「报告质量」扣分 |
