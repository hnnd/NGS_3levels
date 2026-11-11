# 博士专题实践 p02：单细胞聚类稳定性与伪重复诊断

| 项目 | 内容 |
|---|---|
| **对应专题** | `p02` 单细胞与空间转录组（`02_lectures/phd/topic02_scrnaseq_spatial/02_scrnaseq_spatial_lecture.md`） |
| **权重** | 占课程总成绩 **4.5%**（专题实践 27% 的一部分，契约 `assessment.materials`） |
| **运行环境** | `ngs_phd_sc`（`07_envs/conda/env_phd_singlecell.yml`）——单细胞包迭代快，**必须**随结果导出 `env_snapshot.yml` |
| **配套脚本** | `03_code/phd/scripts/`：`02_seurat_pipeline.R`、`02_pseudobulk_de.R`、`02_power_cells.R`、`02_spatial_visium.R`、`02_run_seurat.sh`（SGE） |
| **建议用时** | 上机 5–7 小时（`SCTransform` / `FindAllMarkers` 需 `qsub`），写报告 3 小时 |

## ① 任务背景

讲义 §4.1 与 §⑦ 那句话是本次作业的全部依据：**细胞是观测单位，个体才是统计单位。**

单细胞分析里最容易产出、也最容易被审稿人打回的两类结论是：①「我们鉴定出 12 类细胞」——而 `resolution` 没有真值，这句话本身不可检验；②「处理组 vs 对照组有 8 432 个差异基因，最小 `p_adj < 1e-300`」——这个数量级本身就是伪重复的指纹，不是信号强度的证明。本次作业要求你对自己产出的每一个簇和每一个差异基因，回答"它在什么范围内成立"。

本作业**不考你会不会跑 Seurat**——`02_seurat_pipeline.R` 已封装完整流程。考的是四个参数（`percent.mt`、PC 数、`resolution`、`min.features`）你能否**说出本数据的定量依据**，而不是引用教程里的数字（讲义 ① 第 2 条）。

**评分表里「方法选择与结果可信度说明」占 30%**（契约 `rubric_requirements.method_justification`，p02 在 `stats_plugin_topics` 名单内）；「AI 使用与验证记录」占 10%（契约 `ai_verification_log`，博士层全部作业强制）。

**本作业用的数据**（`bash 06_data/phd/download_phd.sh --topic p02 --run`，说明见 `06_data/phd/README.md`）：

- **单细胞 `GSE222584`**：水稻 RRSV / RGSV 侵染茎基部，9 个样本 = 3 处理（Mock / RGSV / RRSV）× 3 时间点（7/14/21 dpi），10X 三件套约 332 MB，`Seurat::Read10X()` 直读。**注意：采样日期（`0828`/`0904`/`0911`）与 dpi 完全共线**——这是真实存在、无法用统计手段拆开的混杂。你的报告必须点明这一点，并说清它让哪些结论无法成立（这一条计入「方法选择与结果可信度说明」）。
- **空间：10X 官方 `V1_Mouse_Brain_Sagittal_Anterior` 演示数据**（64 MB）。**公开的植物 Visium 数据稀缺**，故空间部分只学方法（`Load10X_Spatial()` 的目录结构与空间可视化，与物种无关）。报告第 5 节要回答：换成你自己的植物样本，这一步会卡在哪。

> **体系是原核的同学注意**：单细胞与空间转录组**只能做真核**（讲义 ③）。用上述公开真核数据完成即可，并在报告第 5 节写明：与你主线体系的对应关系、**结论如何迁移回主线**（迁移的是方法判断力，不是具体基因）——这正是契约 `main_dataset.substitution_rule` 要求的那段说明。

## ② 交付物

打包为 `学号_姓名_p02.zip`：

```
学号_姓名_p02/
├── report.pdf                      # 主报告，正文 ≤ 8 页
├── scripts/
│   ├── run_seurat.sh               # 你实际用的 SGE 作业脚本（改自 02_run_seurat.sh）
│   └── params_rationale.md         # 四个关键参数的定值依据，逐条附支撑图表编号
├── results/
│   ├── qc_metrics.tsv              # 过滤前后细胞数、nFeature/percent.mt 分位数
│   ├── cluster_stability.tsv       # 多 resolution（0.2/0.4/0.6/0.8/1.0）的簇数与你关心簇的存续
│   ├── markers_top.tsv             # FindAllMarkers 输出的每簇 top marker
│   ├── de_findmarkers.tsv          # FindMarkers 的组间比较结果
│   ├── de_pseudobulk.tsv           # 02_pseudobulk_de.R 的结果
│   └── power_cells.txt             # 02_power_cells.R 的输出
├── figs/                           # 标题/轴/图例一律英文
│   ├── fig1_qc_violin.png
│   ├── fig2_elbow.png
│   ├── fig3_umap_by_batch.png      # 整合前后各一版
│   ├── fig4_umap_by_cluster.png
│   ├── fig5_stability.png          # 多分辨率一致性（clustree 式）或重抽样共聚类
│   └── fig6_de_comparison.png      # FindMarkers vs pseudobulk 显著基因数对比
├── ai_logs/prompt_and_reply.md     # ⑧ 的 marker 表任务原文往返
├── results/ai_marker_audit.tsv     # 逐条判定表（见 ③ 第 6 步）
└── env_snapshot.yml
```

报告正文必须含以下五节：

| 节 | 内容 | 对应讲义 |
|---|---|---|
| 1 质控与参数依据 | 四个参数各自的定值依据；**不许引用教程数字** | ④ 4.3、⑤ 5.0 |
| 2 聚类稳定性 | 至少两种评估手段的结论；你关心的簇在哪个 resolution 区间内存续 | ⑦-1 |
| 3 整合诊断 | 整合前后 UMAP + 至少一个定量指标；有没有过度校正 | ④ 4.7、⑥ 6.2 |
| 4 伪重复与 pseudobulk | 两套结果的显著基因数；掉出显著的基因有什么共同点 | ⑦-2、⑩ Q4 |
| 5 **方法选择与结果可信度说明**（≤ 1 页） | 见 ④ 的四问 | ⑦ 全节 |

## ③ 完成步骤

1. **建环境并立刻导出快照**（`conda env export --no-builds > env_snapshot.yml`）。单细胞包版本换一个结果就变，这份快照是你结果的一部分。
2. **主流程**：`02_seurat_pipeline.R`，注意 `--mt-pattern` / `--cp-pattern` **按物种改**（植物要同时算 `^ATMG` 与 `^ATCG`），设错返回全 0 且不报错（⑨-E2）。
3. **参数定值**：`params_rationale.md` 逐条写 `percent.mt` 阈值（先画分布图再定，⑩ Q1）、`--npcs`（ElbowPlot 拐点后再多取 5–10）、`--resolution`（**是一个区间不是一个值**）、`min.features`（稀有小细胞与非模式物种注释不全时要下调）。
4. **稳定性检验**（⑦-1）：至少做两种——多分辨率一致性、重抽样共聚类概率、silhouette。结论写成"**在 resolution 0.4–0.8 内，X 簇始终作为独立簇存在且 top marker 不变**"这种**可检验的陈述**。
5. **pseudobulk 对照**（⑦-2）：跑 `02_pseudobulk_de.R`，报告两套显著基因数，并取 `FindMarkers` 的 top 20 看它们在 pseudobulk 里的 `padj`——**掉出显著的那些基因有什么共同点**（⑩ Q4）。
6. **AI 任务（⑧）**：让 AI 为你的目标物种+组织列 marker 表（要求给基因 ID 与支持文献 DOI），做三项核查——① 基因 ID 到官方数据库（TAIR / RAP-DB / Ensembl Plants / Ensembl Metazoa / VectorBase / FungiDB）查真伪；② 是否把人/鼠 marker 搬过来（`CD4`、`PTPRC`、`EPCAM`，或"macrophage"这类植物中不存在的细胞类型）；③ DOI 用 `bash 03_code/phd/scripts/01_check_refs.sh` 核查后再人工确认摘要真的讲了这个 marker。填 `ai_marker_audit.tsv` 并统计三类错误占比。
7. **功效计算**（⑦-3）：跑 `02_power_cells.R`，并按 ⑩ Q5 的设定（目标类型占 0.5%、至少捕获 20 个、把握 90%）算一次，写出这个数字对预算意味着什么。
8. **必须 `qsub`**：`SCTransform` 与 `FindAllMarkers` 是内存大户（万级细胞常需 32–64 GB），登录节点跑会被杀（⑨-E7）。

## ④ 评分标准

总分 100，折算为课程总成绩的 4.5%。

| 评分维度 | 权重 | 评分要点 |
|---|---|---|
| **完成度与结果正确性** | 48 | 交付物 ② 齐全；四个参数各有本数据的定量依据（非教程数字）；稳定性检验 ≥ 2 种且结论写成可检验陈述；pseudobulk 对照完成且两套数字自洽；`percent.mt` 非全 0（⑨-E2）；差异表达用 `RNA`/`SCT` assay 而非 Harmony 降维坐标（⑨-E5） |
| **方法选择与结果可信度说明** | 30 | 见下方四问，**评分不看结论对不对，看推理链是否闭合** |
| **AI 使用与验证记录** | 10 | 见下方口径 |
| **报告质量** | 12 | 五节结构完整；图表标签英文；UMAP 同时给 batch 与 cluster 两版；数字可与 `results/` 对上 |

### 「方法选择与结果可信度说明」的四个问题（契约 `method_justification`）

一页之内回答完：

| 要回答的问题 | 本专题的落点 | 不合格的写法 |
|---|---|---|
| **1. 为什么用这个检验 / 模型？** | 组间比较为什么用 pseudobulk + DESeq2 而不是 `FindMarkers`；检验单位是细胞还是样本 | "Seurat 默认用 Wilcoxon" |
| **2. 为什么用这个阈值？** | `percent.mt`、PC 数、`resolution` 各自的依据；**resolution 换成 0.4 和 0.8，你的核心结论变不变** | "参考了教程里的 5%" |
| **3. 假阳性风险在哪？** | 伪重复的量级（标准误缩小约 √(n_cell/n_indiv) 倍）；解离应激伪信号；批次与 condition 是否混杂 | "细胞数很多所以结果可靠" |
| **4. 什么证据能推翻你的结论？** | 若做 RNA 原位杂交或流式验证，你预期哪个簇最可能不重复，为什么；生物学重复 < 3 时你放弃了哪些结论 | "需要进一步验证" |

### 「AI 使用与验证记录」的评分口径（契约 `ai_verification_log`）

记录四要素：**用了什么提示（原文）** / **AI 给了什么** / **哪里错了** / **你是怎么发现的**（对应 p01 三步验证法的哪一步）。本次的落点是 ⑧ 的 marker 表三项核查：`ai_marker_audit.tsv` 必须逐条给出判定与证据（查了哪个数据库、DOI 的 HTTP 状态、摘要里有没有这个 marker），并统计三类错误占比、附 200 字反思（AI 在哪类物种/组织上错得最多、为什么）。

> 只报告"AI 错了"不给分，要给出**提示词 + 错误定位 + 发现路径**。**未使用 AI 完成某一步时写明原因即可，不扣分；但通篇声称 AI 输出全部正确且无验证过程的，本栏不得分。**

## ⑤ 提交方式与截止

- **提交入口**：课程 LMS「专题实践 p02」；文件名 `学号_姓名_p02.zip`（≤ 200 MB，超出则去掉 `.rds` 中间对象，保留 `results/` 与 `figs/`）
- **截止时间**：p02 课后 **第 10 天 23:59**
- **迟交**：3 天内按 90% 计，超过 3 天按 70% 计，超过 7 天不计分（可申请一次不扣分延期，须在截止前提出）
- **重交**：允许在截止前重复提交，以最后一次为准
- **诚信**：可与同学讨论方法，分析与写作须独立完成；直接提交他人结果文件按学术不端处理

## ⑥ 常见失分点

| # | 失分点 | 长什么样 | 怎么自查 |
|---|---|---|---|
| 1 | **`percent.mt` 全为 0**（⑨-E2） | 不报错，质控图上一条贴地直线——`^MT-` 用在了非人物种上 | `grep -ci '^ATMG' features.tsv`；脚本里加 `stopifnot(sum(obj$percent.mt) > 0)` |
| 2 | **把 `FindMarkers` 的组间结果当结论**（⑦-2） | 成片 `p_val_adj < 1e-300`，报告里写"差异极显著" | 这个数量级本身就是伪重复指纹。必须跑 pseudobulk 对照，并写明检验单位 |
| 3 | **pseudobulk 用了 `AverageExpression()`**（⑨-E9） | `some values in assay are not integers` | pseudobulk 必须 `rowSums` **原始 counts**，不是取均值、不是归一化值 |
| 4 | **用 Harmony 降维坐标做差异表达**（⑨-E5） | 不报错，`log2FC` 数值离奇 | Harmony 只改 reduction 不改表达矩阵；`DefaultAssay(obj) <- "RNA"` |
| 5 | **只报一个 resolution 的簇数** | "我们鉴定出 12 类细胞" | 这不是可检验陈述。改写成"在 0.4–0.8 区间内 X 簇稳定存在" |
| 6 | **整合过度校正未诊断** | 整合后批次完美混匀，但处理组特异的簇消失了 | 对比整合前后簇数与处理特异 marker 的表达（⑥ 6.2） |
| 7 | **批次与 condition 完全混杂却照样整合** | 一个批次全对照、一个全处理 | 脚本会警告并拒绝整合（§4.7）；此时 Harmony 不能用，见 ⑩ Q6 |
| 8 | **作业日志只有 `Killed`**（⑨-E7/E8） | 无 R 报错，内存超限被杀 | `#$ -l h_vmem=64G`；或先 `subset` 抽样调通再全量。**不要在登录节点跑** |
| 9 | **图里出现方块字** | 中文标题在集群 R 环境下渲染为 □□□ | 课程规则：图内一律英文 |
