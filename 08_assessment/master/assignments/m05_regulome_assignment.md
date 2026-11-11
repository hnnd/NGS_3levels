# 硕士专题作业 m05：调控组分析报告（ChIP-seq / ATAC-seq / CUT&Tag）

| 项目 | 内容 |
|---|---|
| **对应专题** | `m05` 转录调控与表观组（`02_lectures/master/topic05_regulome/05_regulome_lecture.md`） |
| **权重** | 占课程总成绩 **5%**（专题作业 37% 的一部分，契约 `assessment.materials`） |
| **运行环境** | `ngs_ms_transcriptome`（**与 m04 共用**，见 `07_envs/conda/env_master_transcriptome.yml`）+ `ngs_ms_base` |
| **配套脚本** | `03_code/master/scripts/05_peak_calling.sh`（比对 → 清洗 → MACS2 → deepTools → IDR，含 SGE 作业头）、`05_peak_annotation.R`（ChIPseeker 注释 + 与 RNA-seq 交集的置换检验） |
| **建议用时** | 上机 5–7 小时（HOMER 首次预解析很慢，提前起），写报告 3 小时 |

## ① 任务背景

m04 回答"哪些基因变了"，本专题回答"谁让它变的"。两讲共用一个环境不是省事，是因为**本次作业要把你 m04 的差异基因表拿回来做交集**——请提前确认你 m04 的 `deg_sig.tsv` 还在。

这次作业检验的不是"你会不会跑 MACS2"。检验的是**你能不能在没有任何报错的情况下发现实验失败了**。讲义 ⑥ 6.3 那张质控表里第三行是典型：`ATAC_trt_r1` 比对率仍有 88%，看着没问题，但线粒体吃掉 68% 的读段 → 核基因组有效深度不足 → FRiP 0.06、TSS enrichment 2.1 双双塌陷。**只看比对率完全发现不了这个问题。**

同样安静的还有 ⑨-错误 2：`macs2 callpeak` 不给 `-c` 不会报任何错，正常跑完，peak 数从 3 万暴涨到 20 万——那 17 万个是超声偏好与拷贝数变异冒充的信号。

**评分表里「方法选择与结果可信度说明」占 30%**（契约 `rubric_requirements.method_justification`，本讲焦点是 peak calling 的统计模型、IDR 重复一致性、motif 富集的显著性）。本次作业完成后即进入期中项目（大纲：专题 5 结束后布置）。

## ② 交付物

打包为 `学号_姓名_m05.zip`，解压后目录结构如下（**文件名按此命名，助教按名清点**）：

```
学号_姓名_m05/
├── report.pdf                      # 主报告，正文 ≤ 9 页（不含附图）
├── scripts/
│   ├── peak_calling.sh             # 你实际用的上游脚本（改自 05_peak_calling.sh）
│   └── peak_annotation.R           # 你实际用的注释与交集脚本（改自 05_peak_annotation.R）
├── results/
│   ├── qc_table.tsv                # 每样本：比对率/重复率/线粒体%/NRF/FRiP/TSS enrich/判定
│   ├── peaks_summary.tsv           # 各样本 peak 数与宽度中位数
│   ├── reproducible_peaks.bed      # IDR 通过的 peak（第 5 列 scaled IDR ≥ 540）
│   ├── peak_annotation.csv         # ChIPseeker 注释结果
│   ├── homer_known_top.tsv         # Top known motif：P-value / % Targets / % Background 三列全要
│   └── peak_gene_overlap.tsv       # 与 m04 差异基因的交集 + 置换检验 p 值
├── figs/                           # 图的标题/轴/图例一律英文（课程规则）
│   ├── fig1_fraglen.png            # ATAC 片段长度分布（应见核小体阶梯）
│   ├── fig2_tss_heatmap.png        # computeMatrix + plotHeatmap
│   ├── fig3_cor_heatmap.png        # 重复间 Spearman 相关（须含 input）
│   ├── fig4_idr_plot.png           # idr --plot 的输出
│   ├── fig5_anno_pie.png           # plotAnnoPie + plotDistToTSS
│   └── fig6_permutation.png        # 交集的置换零分布与观测值
└── env_snapshot.yml                # conda env export --no-builds
```

报告正文必须含以下六节，缺一节按「流程完整性」扣分：

| 节 | 内容 | 对应讲义 |
|---|---|---|
| 1 技术选型与实验设计 | 选 ChIP / CUT&Tag / ATAC 的理由（九维对照表至少三维）；对照与重复安排 | ④ 技术选型 |
| 2 QC 指标表 | 比对率、重复率、线粒体%、NRF、FRiP、TSS enrichment **六项全报**，逐样本判定 | ⑥ 6.1、6.3 |
| 3 peak calling 与参数依据 | narrow / broad / ATAC 三套参数你用了哪套、为什么；peak 数与**中位宽度** | ⑤ 步骤 2、⑥ 6.2 |
| 4 重复一致性 | Spearman 相关矩阵（含 input）；IDR 通过数与两重复各自 peak 数之比 | ⑥ 6.4、6.5 |
| 5 注释与 motif、与 RNA-seq 交集 | 注释分布饼图；Top motif 的 Targets vs Background；交集数与**置换检验 p 值** | ⑥ 6.6、⑦ |
| 6 **方法选择与结果可信度说明**（≤ 1 页） | 见 ④ 的四问 | ⑦ 全节 |

## ③ 完成步骤

**不要重抄讲义**——下面只给路标与本次作业特有的要求。

1. **取数据**。用课程提供的调控组数据，或你自己课题的数据。**`-g` / `--effectiveGenomeSize` 在 MACS2 与 deepTools 两处必须填同一个数**，否则 bigwig 归一化与 peak 显著性不在同一尺度。非模式物种按 0.8–0.9 × 基因组总长估。
2. **比对与清洗**（⑤ 步骤 1）。`-F 1804` 与 `-q 30` 都要；**ATAC 必须去线粒体**。作业脚本里必须写 `conda activate`——作业不继承终端的 conda 状态。
3. **算 FRiP 与片段长度分布**。FRiP 每个样本都要算。ATAC 的 `fraglen.txt` 画出来应见清晰的核小体阶梯；只有单峰说明消化过度，染色质结构信息已丢失。
4. **peak calling 用对参数**（⑤ 步骤 2）。三套命令的差别**不是风格问题，是三种数据的物理性质不同**：ATAC 用默认 narrow 建模会得到十几万个中位宽 < 150 bp 的碎 peak（⑨-错误 1）。改完对比 peak 数与中位宽度，应从"15 万 / 130 bp"变成"3–6 万 / 400–800 bp"。
5. **有 input 就必须给 `-c`**（⑨-错误 2）。ATAC 无对照属正常，但报告里必须写明"无对照，peak 集合含较高假阳性风险"，并用 IDR 而非单样本 peak 数作主要证据。
6. **IDR 要用宽松阈值喂**（⑤ 步骤 4）。两个重复各自用 `-p 1e-3` call peak——IDR 靠排名靠后的噪声 peak 估计混合模型的噪声成分，只喂高置信 peak 会让估计不稳。
7. **ChIPseeker 的 TxDb 必须由你自己的 GFF3 现场构建**（⑨-错误 4）。注释后**立刻**检查 `table(as.data.frame(anno)$annotation)`，intergenic > 95% 就是红灯。
8. **HOMER 用 summit ±100 bp**（`-size 200`）而非整个 peak，加 `-mask`，`-preparsedDir` 指向自己的可写目录（⑨-错误 3）。**首次预解析耗时几十分钟量级，作业时限要留够。**
9. **与 m04 差异基因取交集并做置换检验**（⑤ 步骤 7、⑦）。GFF3 转 BED 时 `start` 必须减 1（1-based 闭区间 → 0-based 半开）。只报交集个数不报置换 p 值不得分——交集数本身没有可解释性。
10. **导出环境快照**：`conda env export --no-builds > env_snapshot.yml`。

> **允许用 AI 辅助写代码**，但报告里出现的每个数字必须是你自己跑出来的。硕士层不强制提交 AI 验证记录（那是博士层 `ai_verification_log` 的要求），但若 AI 生成的代码导致了错误结论，按「结果正确性」扣分，不因"是 AI 写的"减免。

## ④ 评分标准

总分 100，折算为课程总成绩的 5%。

| 评分维度 | 权重 | 评分要点 |
|---|---|---|
| **流程完整性** | 40 | 交付物 ② 的全部文件齐全；六节报告结构完整；QC 六项指标逐样本都报；IDR 与置换检验都跑了；脚本可原样重跑且与 `results/` 自洽；图表标签为英文 |
| **结果正确性** | 30 | `-g` 在 MACS2 与 deepTools 两处一致；三套 peak calling 参数选对且 peak 数与中位宽度落在合理量级；有 input 时给了 `-c`；IDR 用宽松阈值输入；注释未大面积落 intergenic；交集报告了置换 p 值而非只有个数 |
| **方法选择与结果可信度说明** | 30 | 见下方四问，**评分不看结论对不对，看推理链是否闭合** |

### 「方法选择与结果可信度说明」的四个问题（契约 `method_justification`）

一页之内回答完，每问约 7–8 分：

| 要回答的问题 | 本专题的落点 | 不合格的写法 |
|---|---|---|
| **1. 为什么用这个检验 / 模型？** | MACS2 的局部 λ 泊松模型靠什么估背景、没有 input 时它从哪里估；为什么用 IDR 而不是"取两个重复的交集"；相关性为什么用 Spearman 而非 Pearson | "MACS2 是标准工具" |
| **2. 为什么用这个阈值？** | `-q 0.05` 还是 `--broad-cutoff 0.1`；IDR 阈值 0.05（scaled 540）；MAPQ ≥ 30 与 `-F 1804` 各滤掉什么；`--effectiveGenomeSize` 这个数怎么估的 | "用了默认参数" |
| **3. 假阳性风险在哪？** | 无对照时 peak 集合的假阳性来源（超声偏好、拷贝数变异、开放染色质偏好）；测序量不同的样本**不能直接比 peak 数**；HOMER de novo 在巨大搜索空间下的伪显著（Top motif 是 GC-rich 低复杂度且 Targets/Background 只差 1–2 倍） | "结果可靠" |
| **4. 什么证据能推翻你的结论？** | 交集 137 个基因——若两列表独立期望交集是多少？观测值与置换零分布中位数差多远？若两者不一致，问题可能出在哪 | "需要进一步验证" |

## ⑤ 提交方式与截止

- **提交入口**：课程 LMS「专题作业 m05」；文件名 `学号_姓名_m05.zip`（≤ 200 MB，**不要**把 BAM 与 bigwig 打进包里）
- **截止时间**：m05 课后 **第 10 天 23:59**。同期布置**期中项目**（大纲：专题 5 结束后布置、专题 7 结束时提交），两者时间有重叠，请提前规划
- **迟交**：3 天内按 90% 计，超过 3 天按 70% 计，超过 7 天不计分（可申请一次不扣分延期，须在截止前提出）
- **重交**：允许在截止前重复提交，以最后一次为准
- **诚信**：可与同学讨论方法，但数据处理与写作须独立完成；直接提交他人结果文件按学术不端处理

## ⑥ 常见失分点

来自讲义 ⑨ 与 ⑥ 的"不对的样子"，**按隐蔽程度排序——前三条都不报错**：

| # | 失分点 | 长什么样 | 怎么自查 |
|---|---|---|---|
| 1 | **没给 input 对照**（⑨-错误 2） | **无报错**，正常跑完。peak 数从 3 万暴涨到 20 万以上，FRiP 反而下降，IGV 上大量 peak 落在着丝粒周边与 rDNA，HOMER Top motif 是低复杂度重复 | 日志里有对照时会出现 `#1.2 read input tags...` 与 `#1 total tags in control:`，无对照这两行完全消失 |
| 2 | **ChIPseeker 的染色体命名不匹配**（⑨-错误 4） | **只是 warning，脚本正常跑完**。`plotAnnoPie` > 95% Distal Intergenic，`plotDistToTSS` 几乎全部 > 100 kb | 注释后立刻 `table(as.data.frame(anno)$annotation)`；用 `seqlevelsStyle(peak) <- seqlevelsStyle(txdb)[1]` 统一；**TxDb 必须用自己的 GFF3 现场建**，用别的物种的预置包症状相同但更隐蔽 |
| 3 | **按测序量不同的样本直接比 peak 数**（⑩ Q2、⑦） | 无报错。"处理组 68 000 个 peak、对照组 41 000 个，说明染色质变开放"——而两者测序量是 52 M 与 31 M | peak 数随深度增加而增加；必须做深度饱和曲线或降采样到同一深度再比 |
| 4 | **ATAC 用 MACS2 默认参数**（⑨-错误 1） | `WARNING: Fewer paired peaks (23) than 1000!` 或 `Can't find enough pairs of symmetric peaks to build model!`；即使侥幸建模成功也得到 15 万个碎 peak | 改用 `--nomodel --shift -100 --extsize 200 --keep-dup all -f BAMPE`；改完 peak 数与中位宽度应显著变化 |
| 5 | **只看比对率就判样本合格**（⑥ 6.3） | 比对率 88% 看着正常，实际线粒体 68%、FRiP 0.06、TSS enrich 2.1 | 六项指标一起看；线粒体 > 60% 时核基因组有效深度只有名义深度的 40% |
| 6 | **HOMER 找不到基因组配置 / 预解析目录只读**（⑨-错误 3） | `Genome hg38 not found in .../homer/config.txt`；或 `Could not open .../preparsed/ for writing` | 非模式物种直接传 FASTA 路径，不要下 HOMER 预置基因组；加 `-preparsedDir /d3/scratch/${USER}/homer_preparsed`（先 `mkdir -p`） |
| 7 | **`--broad` 输出拿去做 `-size 200`** | broadPeak **只有九列，没有第 10 列 summit** | 需要 summit 的下游不能用 broadPeak；narrow 才有 `*_summits.bed` |
| 8 | **IDR 读 gzip 输入**（⑨-错误 5） | `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x8b in position 1` | `0x1f 0x8b` 是 gzip 魔数；先 `gunzip -c` 解压再跑 |
| 9 | **染色体名过滤时静默丢染色体**（⑨-错误 6） | `region "1" specifies an unknown reference name. Continue anyway.` ——**只是 Continue anyway，结果 BAM 会变空或缺染色体** | `samtools view -H clean.bam \| grep ^@SQ \| head` 与 `head ${GENOME}.fai` 对照 |
| 10 | **GFF3 转 BED 忘了 start−1** | 无报错。所有 peak-基因距离系统性偏移 1 bp，边界判断出错 | GFF3 是 1-based 闭区间，BED 是 0-based 半开（`l0_04_formats`） |
| 11 | **IDR 结果差就改用"取交集"凑数量**（⑥ 6.5） | 通过 IDR 的 peak 只剩几百个，于是换成交集报了几千个 | 散点均匀弥散说明两个重复几乎不一致；应回头查是哪个重复出了问题，不是换统计口径 |
