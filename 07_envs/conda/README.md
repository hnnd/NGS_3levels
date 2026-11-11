# Conda 环境说明

## 为什么按任务拆分，而不是每层一个大环境

单一大环境在 bioconda 上**通常解不出来**：

| 冲突组合 | 原因 |
|---|---|
| BUSCO / QUAST vs antiSMASH | augustus、sepp 与 antiSMASH 的 Python 依赖链版本互斥 |
| QIIME2 vs 其他一切 | 官方明确要求独立环境 |
| GATK4 vs R 栈 | Java 运行时与 r-base 的依赖纠缠，solve 时间极长 |

因此每个层次拆成若干**按任务内容划分**的环境，学生按当前单元/专题激活对应环境。
拆分方案由 `00_design/course_contract.yaml` 的 `levels.<level>.env_files` 定义，
并由 `03_code/tools/validate_course.py` 的 `env_tool_coverage` 校验：
每个专题必须被至少一个环境 `covers`，且其 `core_tools` 出现在这些环境的依赖并集中。

## 本科生（4 个环境，第 1 轮已建）

| 文件 | 环境名 | 用途 | 覆盖单元 |
|---|---|---|---|
| `env_ug_base.yml` | `ngs_ug_base` | 通用与质控比对 | u01–u05, u07 |
| `env_ug_assembly.yml` | `ngs_ug_assembly` | 基因组扫描与组装 | u06, u08 |
| `env_ug_annotation.yml` | `ngs_ug_annot` | 注释与完整性 | u07, u08 |
| `env_ug_phylo.yml` | `ngs_ug_phylo` | 鉴定/进化/泛基因组 | u08 |

```bash
conda env create -f env_ug_base.yml
conda activate ngs_ug_base
```

## 硕士生 / 博士生

契约已定义 6 + 6 个环境（见 `env_files`），文件将在**第 3 轮（硕士）、第 4 轮（博士）**
随讲义生产创建。

> ⚠ **时间依赖**：L0 前置包要求"开课前 2 周发布"，学生要按 L0 的指引建本层环境。
> 因此**硕士层环境文件必须在硕士课开课前 2 周之前完成**（即第 3 轮须早于硕士开课），
> 博士层同理。开课顺序本科 → 硕士 → 博士，与生产轮次一致。

## 已弃用

`deprecated/` 下的 `env_undergraduate.yml`、`env_master.yml`、`env_phd.yml`
是拆分前的单体环境，仅作历史参考，**不要用它们建环境**。

## 不走 conda 的工具

以下工具在 `course_contract.yaml` 的 `env_exempt_tools` 中豁免，
不要试图写进 yml，否则永远 solve 不出来：

| 工具 | 原因 | 获取方式 |
|---|---|---|
| GenomeScope | 本课手册用 wget 下载 `genomescope.R` 后 Rscript 运行 | 手册 §4.1 |
| SignalP | DTU 学术许可，需单独申请 | services.healthtech.dtu.dk |
| EffectorP | 独立分发的 Python 工具 | GitHub |
| GAPIT | R 包，非 bioconda 渠道 | `install.packages` / GitHub |
| Cytoscape | 桌面 Java 应用 | 官网下载 |
| ANNOVAR | 需官网注册后下载 | annovar.openbioinformatics.org |
| Docker | 系统级容器运行时 | 需管理员安装 |
| QIIME2 | 官方要求独立环境 | 按 QIIME2 官方文档单独创建 |

## 版本 pin 策略

已在旧环境验证过的工具保留原有版本 pin；**本轮新增的工具暂不 pin**，
以提高首次 solve 成功率。首次成功创建后请回填精确版本：

```bash
conda activate ngs_ug_base
conda env export --no-builds > env_ug_base.lock.yml
```

## 验证状态（2026-11-05 更新）

全部 16 个环境已于第 7 轮在集群 `/d3/lab/envs` 实建，并用 `qsub` 在计算节点跑通首次实践课脚本（见项目 CLAUDE.md §一、§三）。2026-11-05 改动的 9 个 yml（补包与钉版本）已在 ta 上以 `CONDA_OVERRIDE_GLIBC=2.18` 复现集群 glibc 约束、`conda env create --dry-run` 全部解出；**集群上的已建环境尚未按新 yml 增量安装**，需管理员确认后执行。
在 ta 等新系统上试解时务必加 `CONDA_OVERRIDE_GLIBC=2.18`，否则结果不代表集群：

```bash
conda env create -f env_ug_base.yml --dry-run
```

若某个包名解析失败，最可能的两处：
- `jellyfish` → 试 `kmer-jellyfish`
- `bioconductor-ggtree` → 试 `r-ggtree`
