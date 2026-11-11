# 硕士专题作业 m02：基因组质量报告 + 泛基因组组成报告

| 项目 | 内容 |
|---|---|
| **对应专题** | `m02` 基因组组装与比较 / 泛基因组（`02_lectures/master/topic02_assembly_pangenome/02_assembly_pangenome_lecture.md`） |
| **权重** | 占课程总成绩 **5%**（专题作业 37% 的一部分，契约 `assessment.materials`） |
| **运行环境** | `ngs_ms_genome`（组装 / 评估 / 比较基因组）+ `ngs_ms_base`（R 绘图）；见 `07_envs/conda/env_master_genome.yml` |
| **配套脚本** | `03_code/master/scripts/02_assembly_pipeline.sh`（K-mer → 组装 → 评估）、`02_orthofinder_cafe.sh`（直系同源 → 泛基因组 → CAFE5），均含 SGE 作业头 |
| **建议用时** | 上机 5–7 小时（组装与 OrthoFinder 走 `qsub`，等待期可写报告），写报告 3 小时 |

## ① 任务背景

这次作业检验的不是"你会不会跑 Flye 和 OrthoFinder"——脚本已经写好，`[checkpoint]` 步骤还提供了预跑输出。检验的是**你能不能读懂这些工具吐出来的数字，并说出它们各自的边界在哪**。

讲义 ⑦ 用一整节讲了同一件事的三个侧面：`C:99.1%[S:51.3%,D:47.8%]` 与 `C:99%[S:98%,D:1%]` 的 C 一样，前者的组装大概率是错的；N50 变大可能是错接变多而不是组装变好；CAFE5 的家族级 p 值小只说明"单一 λ 解释不了"，**不等于**"这个家族在适应性上重要"。这三条都不会有任何报错，只会安静地进入你的论文。

本次作业承接 m01 的 sample sheet 格式，产出的组装与注释是期中项目"基因组线"的起点。**评分表里「方法选择与结果可信度说明」占 30%**，这是契约 `rubric_requirements.method_justification` 对统计要点专题的强制要求（本讲的焦点是 CAFE5 显著性检验与 BUSCO 解读边界）。

## ② 交付物

打包为 `学号_姓名_m02.zip`，解压后目录结构如下（**文件名按此命名，助教按名清点**）：

```
学号_姓名_m02/
├── report.pdf                      # 主报告，正文 ≤ 10 页（不含附图）
├── scripts/
│   ├── assembly_pipeline.sh        # 你实际用的组装脚本（改自 02_assembly_pipeline.sh）
│   └── orthofinder_cafe.sh         # 你实际用的比较基因组脚本（改自 02_orthofinder_cafe.sh）
├── results/
│   ├── genomescope_summary.txt     # GenomeScope 的 summary.txt
│   ├── quast_report.tsv            # QUAST 的 report.tsv
│   ├── busco_short_summary.txt     # BUSCO 的 short_summary（含库名与版本）
│   ├── orthogroups_class.tsv       # 每个 orthogroup 的 core/softcore/shell/cloud/unique 归类
│   ├── stats_per_species.tsv       # OrthoFinder 的 Statistics_PerSpecies.tsv（体检用，必交）
│   └── cafe_significant.tsv        # CAFE5 显著家族表，须同时含 p 与 BH 校正后的 q
├── figs/                           # 图的标题/轴/图例一律英文（课程规则）
│   ├── fig1_kmer_histogram.png     # GenomeScope 拟合图
│   ├── fig2_pangenome_pie.png      # core/shell/cloud/unique 组成
│   ├── fig3_rarefaction.png        # 稀释曲线，core 与 pan 两条
│   ├── fig4_upset.png              # 共享模式 UpSet 图
│   └── fig5_cafe_top.png           # 显著扩张/收缩家族 Top 10
└── env_snapshot.yml                # conda env export --no-builds
```

报告正文必须含以下六节，缺一节按「流程完整性」扣分：

| 节 | 内容 | 对应讲义 |
|---|---|---|
| 1 K-mer 特征估计 | Genome Haploid Length / Heterozygosity / Percent Repeat；**Model Fit 是否 ≥ 90%** | ⑥ 6.1 |
| 2 组装与连续性 | `# contigs`、Total length、N50、L50、misassembly；`assembly_info.txt` 的 `circ.` 列 | ⑥ 6.2 |
| 3 完整性评估 | BUSCO 的 **C / S / D / F / M 五个数全报**，写明**库名与版本**及 n 值 | ⑥ 6.3、⑦ 4–6 |
| 4 K-mer 估计 vs 组装长度的差异 | 差异百分比 + 讲义 6.1 的三种成因中你选了哪一种、证据是什么 | ⑥ 6.1 |
| 5 泛基因组组成 | core/softcore/shell/cloud/unique 计数与饼图；稀释曲线是否收敛；**基因组个数与选样方式** | ⑥ 6.4、⑦ 8 |
| 6 基因家族扩张收缩 | Top 10 显著家族及功能注释；**p 与 q 都要报**；两棵不同标定树的 Top 20 重叠率 | ⑥ 6.5、⑦ 1–3、9 |
| 7 **方法选择与结果可信度说明**（≤ 1 页） | 见 ④ 的四问 | ⑦ 全节 |

## ③ 完成步骤

**不要重抄讲义**——下面只给路标与本次作业特有的要求。

1. **取数据**。用课程提供的长读长数据（≤ 50 Mb 基因组）与 8–12 个近缘菌株的 `.faa`；或用你自己课题的数据。**组装与 OrthoFinder 必须 `qsub` 提交**，不要在登录节点跑。
2. **K-mer 估计**（⑤ 5.2）。`jellyfish count` 的 `-C` 不能省（DNA 双链，不合并等于把每个 k-mer 数成两半）。作业脚本头必须写 `#$ -S /bin/bash`，否则 `<(zcat ...)` 进程替换会报语法错（⑨-5）。
3. **组装**（⑤ 5.3）。**读长类型参数必须与数据匹配**：HiFi → `--pacbio-hifi`，ONT 普通 → `--nano-raw`，ONT 高精度 → `--nano-hq`。选错的后果见 ⑨-4（contig 数暴涨、总长远超估计）。跑不完就用 `checkpoints/` 下的预跑输出。
4. **评估**（⑤ 5.4）。QUAST **必须给 `-r`/`-g`**，否则报告里没有 misassembly 一栏，只有连续性指标——那种报告不能当作"正确性检查通过"。BUSCO 在计算节点要 `--offline --download_path`（⑨-1）。
5. **跑完 OrthoFinder 的第一件事是看体检表**（⑨-2）：`Statistics_PerSpecies.tsv` 的基因数与 species-specific orthogroup 计数，**某一列明显离群就是警报**——那是注释流程不统一，不是生物学。真核数据须先只留最长转录本。
6. **泛基因组统计与稀释曲线**（⑤ 5.6，在 `ngs_ms_base` 的 R 里）。稀释曲线对每个 N 做 100 次无放回抽样，画中位数与四分位区间。
7. **CAFE5**（⑤ 5.7）。转换后**先过滤**：行和为 0 的家族、单物种计数 > 100 的超大家族（会把 λ 拉偏，⑨-6）。树必须是超度量树，自查 `R -e 'library(ape); is.ultrametric(read.tree("tree.nwk"))'`（⑨-3）。
8. **两棵树各跑一次**（⑦ 9 的作业要求）：用两种不同标定的超度量树，报告 Top 20 显著家族的**重叠率**。这一条是本次作业区别于"照着跑一遍"的关键。
9. **导出环境快照**：`conda env export --no-builds > env_snapshot.yml`。

> **允许用 AI 辅助写代码**，但报告里出现的每个数字必须是你自己跑出来的。硕士层不强制提交 AI 验证记录（那是博士层 `ai_verification_log` 的要求），但若 AI 生成的代码导致了错误结论，按「结果正确性」扣分，不因"是 AI 写的"减免。

## ④ 评分标准

总分 100，折算为课程总成绩的 5%。

| 评分维度 | 权重 | 评分要点 |
|---|---|---|
| **流程完整性** | 40 | 交付物 ② 的全部文件齐全；七节报告结构完整；脚本可原样重跑且与 `results/` 自洽；两棵树的对照实验确实做了；图表标签为英文 |
| **结果正确性** | 30 | 读长类型参数与数据匹配；BUSCO 的 C/S/D/F/M 五个数全报且写明库名与 n；QUAST 给了 `-r` 才谈 misassembly；CAFE5 输入已过滤且列序与树叶名对应；泛基因组结论同时给出基因组个数与选样方式 |
| **方法选择与结果可信度说明** | 30 | 见下方四问，**评分不看结论对不对，看推理链是否闭合** |

### 「方法选择与结果可信度说明」的四个问题（契约 `method_justification`）

一页之内回答完，每问约 7–8 分：

| 要回答的问题 | 本专题的落点 | 不合格的写法 |
|---|---|---|
| **1. 为什么用这个检验 / 模型？** | CAFE5 的零假设是"该家族可由全局单一 λ 的出生-死亡过程生成"——说清它检验的是什么、**不能**回答什么（⑦-1） | "CAFE5 是标准工具" |
| **2. 为什么用这个阈值？** | BUSCO 选了哪个 lineage 库、为什么不用最宽的那个；CAFE5 用 p 还是 BH 校正后的 q，取决于下游是逐个敲除验证还是做富集（⑦-3、⑦-6） | "用了默认参数" |
| **3. 假阳性风险在哪？** | 上千个 orthogroup 按 `p < 0.05` 筛，仅靠随机就有几十到上百个假阳性；λ 的估计质量被超大家族带偏则**所有 p 值一起偏**（⑦-2、⑦-3） | "结果可靠" |
| **4. 什么证据能推翻你的结论？** | 换一棵标定不同的树后 Top 名单的重叠率是多少（⑦-9）；core 曲线若仍在下降，你的核心基因组数还会缩水多少（⑦-8） | "需要进一步验证" |

## ⑤ 提交方式与截止

- **提交入口**：课程 LMS「专题作业 m02」；文件名 `学号_姓名_m02.zip`（≤ 200 MB，超出则去掉组装中间文件与 OrthoFinder 的 `WorkingDirectory/`）
- **截止时间**：m02 课后 **第 10 天 23:59**
- **迟交**：3 天内按 90% 计，超过 3 天按 70% 计，超过 7 天不计分（可申请一次不扣分延期，须在截止前提出）
- **重交**：允许在截止前重复提交，以最后一次为准
- **诚信**：可与同学讨论方法，但数据处理与写作须独立完成；直接提交他人结果文件按学术不端处理

## ⑥ 常见失分点

来自讲义 ⑨ 与 ⑥ 的"结果不对时长什么样"，**按出现频率排序**：

| # | 失分点 | 长什么样 | 怎么自查 |
|---|---|---|---|
| 1 | **注释流程不统一造成假的"物种特异基因"**（⑨-2） | **无报错**。`Statistics_PerSpecies.tsv` 里某个菌株基因数 7642 而别的 5100，species-specific orthogroup 1188 而别的 30 | 跑完 OrthoFinder 第一件事就看这张表，某列离群即警报；真核还要检查是否只留了最长转录本 |
| 2 | **Flye 读长类型参数选错**（⑨-4） | 不报错。Total length 41 Mb（预期 5 Mb）、Contigs 3127（预期个位数） | 组装完先看总长与 contig 数是否与 GenomeScope 估计同一量级；改对参数重跑，别指望后处理挽救 |
| 3 | **只报 BUSCO 的 C 不报 S/D**（⑦-4） | `C:99%` 看起来很好，实际 `[S:51%,D:48%]`——单倍型冗余或组装冗余 | C = S + D，D 是**异常信号不是加分项**；D 高时结合组装总长与 GenomeScope 倍性区分三种成因（⑦-5） |
| 4 | **CAFE5 拒绝非超度量树**（⑨-3） | `Error: Tree is not ultrametric`，或表现为 `Failed to initialize any models!` | 别直接喂 OrthoFinder 的 `SpeciesTree_rooted.txt`（分支长度是替换数不是时间）；`ape::is.ultrametric()` 返回 `FALSE` 即确诊 |
| 5 | **CAFE5 输入没过滤，λ 被拉偏**（⑨-6、⑦-2） | `Failed to initialize any models!`，或显著家族占比 > 20%（⑥ 6.5） | 过滤行和为 0 的家族与单物种 > 100 的超大家族；确认**输入表物种列顺序与树叶名完全对应**（列错位不报错，只给一整张错结果） |
| 6 | **N50 变大就说组装变好**（⑥ 6.2） | N50 上升的同时 misassembly 同步变多 | N50 对错接是奖励而非惩罚；必须与 misassembly 一起看，且没给 `-r` 时 misassembly 栏是空的 |
| 7 | **只报 p 不报 q**（⑦-3） | 显著家族表只有一列 p 值 | 家族级 p 值必须做 BH 校正后报 FDR，正文明确写的是 p 还是 q |
| 8 | **报核心基因组数却不给基因组个数**（⑦-8） | 写"核心基因组 2100 个基因"就没有了 | core 数随基因组数单调下降，必须同时给基因组个数、选样方式、core 曲线是否接近平台 |
| 9 | **`jellyfish` 在 SGE 作业里语法错**（⑨-5） | `syntax error near unexpected token '('` | 作业头写 `#$ -S /bin/bash`——SGE 默认 shell 不是 bash，`<(zcat ...)` 是 bash 进程替换 |
| 10 | **BUSCO 库下载失败**（⑨-1） | `Errno -3 Temporary failure in name resolution` | 计算节点不通外网。登录节点先 `busco --download`，作业里加 `--offline --download_path` |
