# 06_data — 课程数据集索引

> 契约：`00_design/course_contract.yaml` → `main_dataset`（三层 status 均为 `determined`）
> 文档版本：v2.0 ｜ 2026-08-30 ｜ 第 7 轮"主线数据集就位"
> 入 git 的只有 `README.md` / `*.sh` / `*.tsv` / `.gitkeep`，**数据本身一律不入库**（见根目录 `.gitignore`）

---

## 一、三层主线一览

课程数据全部选用**公开数据**——学生在校外、脱离实验室内网也能自学完整跑通。

| 层次 | 主线体系 | 锚点研究 | 下载量 | 数据包 |
|---|---|---|---|---|
| **本科** | *Xanthomonas oryzae* pv. *oryzae*（水稻白叶枯病菌，4.7 Mb） | `PRJEB100987` 西非 Xoo 群体 | **485 MB**（只做 u08 仅 67 MB） | [`undergraduate/`](undergraduate/README.md) |
| **硕士** | 西非水稻农业生态系统：病原线 + 寄主线 + 群落线 | `PRJEB100987` / `PRJDB36269` / `PRJDB13364` / `PRJDB12800` | 约 **10 GB**（降采样后） | [`master/`](master/README.md) |
| **博士** | 水稻–稻瘟病菌（*Oryza sativa* – *Pyricularia oryzae*） | `GSE222584` / `PRJNA661210` / `PRJEB53625` / RDP1 / `MTBLS13460` | 约 **15 GB** | [`phd/`](phd/README.md) |

**为什么跨层不同物种**：契约 `cross_level_consistency: per_level`——本科主线是细菌（组装要在课堂时段跑完），而博士 p02 的单细胞/空间只能做真核、p05 的 GWAS 需上百个体表型群体，物理上无法共用一个体系。取舍是放弃"本硕博同一物种"的连续感，换取每层内部真正连贯。

### 三个"内建标准答案"的设计（自学场景下最稀缺的东西）

自学最大的困难不是跑不动，是**跑完了不知道自己对不对**。三层主线各埋了一个可对照的答案：

| 层次 | 内建答案 |
|---|---|
| 本科 | k-mer 扫描与长读长组装用**同一株 CIX4481**，且作者已发表该株完成图 `GCA_987216485`——自己的组装可与标准答案直接比 |
| 硕士 | m02 的 CIX2779 有已发表完成图 `GCA_024981335`；且该株在 m03 里**又是参考基因组**——自己比自己变异数应约等于 0，是现成的流程阴性对照 |
| 博士 | RDP1 附带**已发表的全部 36,901 SNP × 34 性状 MLM p 值**，学生跑完 GEMMA 可直接比对 |

另有一处数据结构上的便利：硕士 m04/m05 用的 `PRJDB36269` 是**同一批水稻根样本同时做了 ATAC-seq 与配套 RNA-seq**，m05 讲义要求的「差异 peak ∩ 差异基因」因此无需任何假设即成立。

---

## 二、登录号：先核验，再登记，才能写进材料

**本课程所有登录号都经过在线核验。** 这条规矩来自一次真实事故：m01 讲义原写的 `PRJNA294222` 在 ENA 与 NCBI **均查无此项**，却在仓库里活了三轮没被发现——它形状合法、上下文合理，DOI/URL 语法检查抓不到。

```bash
bash 06_data/verify_accessions.sh                    # 核验注册表全表（联网查 ENA + NCBI + MetaboLights）
bash 06_data/verify_accessions.sh PRJEB100987 SRR2584863   # 只核验指定的几个
```

- **注册表**：[`accessions.tsv`](accessions.tsv)（列：登录号 / 用途 / 期望物种关键词）
- **离线闸门**：`validate_course.py` 的 `dataset_accession` 检查——材料里出现的登录号必须已在注册表登记，否则报 error
- **新增数据的流程**：ENA Portal API 检索拿到**真实**登录号 → `verify_accessions.sh` 核验 → 追加进 `accessions.tsv` → 才能写进讲义/作业
- 刻意展示的反面教材（如演示"登录号不存在时报什么错"的假号）走校验器白名单，不必登记

---

## 三、下载

每层一份下载脚本，均为 **ENA FTP 直下 + md5 强校验 + 断点续传 + 可选降采样 + SHA256 manifest**，默认 `--dry-run` 只打印命令：

```bash
bash 06_data/undergraduate/download_ug.sh --run              # 本科全套 485 MB
bash 06_data/master/download_master.sh --topic m04 --run     # 硕士按专题下
bash 06_data/phd/download_phd.sh --all --dry-run             # 博士先看要下什么
```

各脚本的分层选项、降采样参数与预期文件清单见对应目录的 README。

> **不要把数据下进仓库**。建议 `/d3/scratch/${USER}/ngs/data/`（集群）或任意仓库外目录，
> 再按需软链接到 `06_data/raw/`。

---

## 四、已知限制（如实记录，不在材料中掩盖）

契约 `main_dataset.*.known_limitations` 逐条登记，讲义与作业中均已标注：

| 涉及 | 限制 | 课程怎么处理 |
|---|---|---|
| 硕士 m04/m05 | `PRJDB36269` 只有 **2 个生物学重复**（讲义原要求 ≥3） | 取 30/60/120 min 三个配对时间点得 12 样本，用 `~rep+time+treatment`，`rep`(A/B) 正好充当讲义要教的 batch，时序用 LRT；样本量限制本身即统计插件要讨论的内容 |
| 硕士 m06/m07 | 扩增子与宏基因组**非同批采样**（已实查 ENA 全部候选，不存在同时含足量 AMPLICON 与 WGS 且分组可用的项目） | 讲义讲明"丰度差异不可直接归因于方法差异"——这正是统计插件「混杂」一节的现成案例 |
| 博士 p02 | 公开**植物 Visium 数据稀缺** | 用 10X 官方演示数据学方法，域内研究作阅读对象，并要求学生回答"换成植物样本这一步会卡在哪" |
| 博士 p06 | 转录组与代谢组**非同一批样本**，而 WGCNA/MOFA2 以配对为前提 | 只能做流程练习，**不能下跨组学生物学结论**；"指出这个缺陷并写出自己会怎么设计配对采样"已作为作业要求 |

---

## 五、实验室数据（校内可选）

本科 u08 的《学生实验操作手册》锚定实验室自测数据 `/data/lab/ngs/reads.fa`（集群 `10.7.254.22`，SGE）。**校内上课以手册为准**；公开数据是校外自学的等价替代，走完全相同的 6 个模块与 12 个工具。契约 `main_dataset.undergraduate.lab_data_optional` 记录了这层关系。

## 六、目录

```
06_data/
├── accessions.tsv            # 已核验登录号注册表（入 git）
├── verify_accessions.sh      # 在线核验工具（入 git）
├── undergraduate/  master/  phd/    # 每层 README + download_*.sh（入 git）
├── raw/                      # 原始数据落地处（不入 git）
├── processed/                # 中间结果（不入 git）
└── reference/                # 参考基因组与注释（不入 git，见其 README）
```
