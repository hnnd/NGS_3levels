# 硕士专题作业 m03：变异检测报告与过滤阈值敏感性分析

| 项目 | 内容 |
|---|---|
| **对应专题** | `m03` 重测序与变异检测（`02_lectures/master/topic03_resequencing/03_resequencing_lecture.md`） |
| **权重** | 占课程总成绩 **5%**（专题作业 37% 的一部分，契约 `assessment.materials`） |
| **运行环境** | `ngs_ms_variant`（`07_envs/conda/env_master_variant.yml`）+ `ngs_ms_base`（作图与报告） |
| **配套脚本** | `03_code/master/scripts/03_gatk_pipeline.sh`（比对 → 去重 →（可选 BQSR）→ HaplotypeCaller → 联合调用 → 硬过滤）、`03_filter_sensitivity.sh`（三组阈值对照，**本次作业必跑**） |
| **建议用时** | 上机 5–7 小时（GATK 走 `qsub`），写报告 3 小时 |

## ① 任务背景

这次作业检验的不是"你会不会跑 GATK"——`03_gatk_pipeline.sh` 已经把 Best Practices 写好了。检验的是**你能不能对每一条过滤阈值说出它在拦什么**。

讲义 ⑥ 6.2.4 有一句话是本讲的题眼：GATK 官方那套硬过滤数值是 Broad 用**人类高深度数据 + 高置信 truth set** 画出分布后取的经验切点，**不是普适常数**。换物种、换深度、换比对器、换建库方式，分布就会平移。所以非模式物种照抄这套数字，本身就是一个需要论证的决定——而论证的方式就是阈值敏感性分析。

更隐蔽的是 ⑨-E7：`VariantFiltration` 引用了 VCF 里不存在的标签时，只打一条 `WARN`、退出码 0，**这条阈值一条位点也没拦**。你的方法学里写着六条阈值，实际生效的可能只有四条，而报告上看不出任何异常。

本讲的 ⑥ 6.2 还是 **L1 锚点**：博士 `p04`（群体基因组）与 `p05`（GWAS）经 L1 映射直达此处。你这次作业产出的 VCF 与过滤记录，就是那两讲的输入格式。**评分表里「方法选择与结果可信度说明」占 30%**（契约 `rubric_requirements.method_justification`）。

## ② 交付物

打包为 `学号_姓名_m03.zip`，解压后目录结构如下（**文件名按此命名，助教按名清点**）：

```
学号_姓名_m03/
├── report.pdf                      # 主报告，正文 ≤ 9 页（不含附图）
├── scripts/
│   ├── gatk_pipeline.sh            # 你实际用的流程脚本（改自 03_gatk_pipeline.sh）
│   └── filter_sensitivity.sh       # 你实际用的敏感性分析脚本（改自 03_filter_sensitivity.sh）
├── results/
│   ├── flagstat_all.tsv            # 各样本比对率、properly paired、singletons 汇总
│   ├── dup_metrics_all.tsv         # 各样本 PERCENT_DUPLICATION 汇总
│   ├── callable_summary.tsv        # callable region 比例（无此表则"某基因无变异"不成立）
│   ├── filter_counts.tsv           # 每条 filter 各拦掉多少位点（bcftools query 统计）
│   ├── sensitivity_table.tsv       # 宽/默认/严三组阈值的变异数、Ti/Tv、平均深度对照
│   └── high_impact.tsv             # SnpEff HIGH 影响变异清单（去重后，见 ⑥ 失分点 8）
├── figs/                           # 图的标题/轴/图例一律英文（课程规则）
│   ├── fig1_qc_summary.png         # 比对率 / 重复率 / callable 比例
│   ├── fig2_qd_mq_hist.png         # QD 与 MQ 的分布直方图（判断阈值是否适合你的数据）
│   ├── fig3_sensitivity.png        # 三组阈值下变异数与 Ti/Tv 的对照
│   └── fig4_allele_balance.png     # 杂合位点的 AD 等位平衡分布
└── env_snapshot.yml                # conda env export --no-builds
```

报告正文必须含以下六节，缺一节按「流程完整性」扣分：

| 节 | 内容 | 对应讲义 |
|---|---|---|
| 1 比对与前处理 | 比对率、properly paired、重复率、**callable 比例**四个数字全报 | ⑥ 6.1 |
| 2 调用策略 | `-ploidy` 取值与理由；是否走 gVCF 联合调用；做不做 BQSR、不做怎么交代 | ⑤ 5.2、5.3、④ 4.4 |
| 3 过滤阈值与生效验证 | 六条阈值逐条说明在拦什么；**每条各拦掉多少位点**（`filter_counts.tsv`） | ⑥ 6.2.4、6.2.7 |
| 4 阈值敏感性分析 | 宽/默认/严三组的变异数、Ti/Tv、平均深度对照；你最终选哪组、依据是什么 | ⑤ 5.5、⑥ 6.2.7 |
| 5 下游交付与注释 | 6.2.6 四步里你做了哪几步、**哪几步刻意没做及原因**；HIGH 影响变异清单 | ⑥ 6.2.6、6.3 |
| 6 **方法选择与结果可信度说明**（≤ 1 页） | 见 ④ 的四问 | ⑦ 全节 |

## ③ 完成步骤

**不要重抄讲义**——下面只给路标与本次作业特有的要求。

1. **取数据**。用课程提供的重测序数据，或你自己课题的数据（推荐；期中项目的"变异线"会接着用）。样本数建议 ≥ 3 以便走联合调用。
2. **建三套索引**（⑤ 5.1）：`bwa-mem2 index`、`samtools faidx`、`gatk CreateSequenceDictionary`，**缺一不可**（⑨-E1）。`-R '@RG...'` 必须用**单引号**（⑨-E10）。
3. **比对与去重**（⑤ 5.1、5.2）。`MarkDuplicates` 的 `-M` 输出的 `PERCENT_DUPLICATION` 是文库复杂度的直接指标，**必须进报告**。NovaSeq 的 patterned flowcell 记得给 `--OPTICAL_DUPLICATE_PIXEL_DISTANCE 2500`。
4. **算 callable 比例**（⑥ 6.1）。这一步很多人跳过，但**没有这个数，"某基因无变异"的结论无法成立**——那可能是漏检而不是阴性结论。
5. **变异检测与联合调用**（⑤ 5.3）。`--java-options "-Xmx16g"`，且 `qsub` 申请的内存要**大于** `-Xmx`（JVM 另有开销，留 20%，⑨-E5）。
6. **SNP 与 InDel 分开过滤**（⑤ 5.4）。`--filter-name` 与 `--filter-expression` 必须成对且顺序对应；**分开写多条**而不是塞进一个 `||` 表达式——否则第 3 节的"每条拦掉多少"根本统计不出来。
7. **验证阈值真的生效**（⑨-E7，本次作业硬性要求）：
   ```bash
   bcftools view -h raw_snp.vcf.gz | grep INFO=            # 过滤前：确认标签存在
   bcftools query -f '%FILTER\n' filt_snp.vcf.gz | sort | uniq -c | sort -rn   # 过滤后：每条拦了多少
   ```
   某条 filter 计数为 0，要么是这条阈值确实没拦到东西，要么是 JEXL 静默失效——**报告里必须区分这两种情况**。
8. **跑敏感性分析**（`03_filter_sensitivity.sh`，必做）。宽 / 默认 / 严三组各过滤一次，输出变异数、Ti/Tv、平均深度对照表。Ti/Tv 接近 0.5 说明假阳性大量混入（随机测序错误的 Ti/Tv ≈ 0.5）。
9. **注释与提取**（⑤ 5.5）。非模式物种需自建 SnpEff 库（⑨-E8），建完**必须核对日志里的基因数与 CDS 数是否与 GFF3 一致**。统计 HIGH 变异数时注意一个变异可能有多条 ANN，**不要重复计数**。
10. **导出环境快照**：`conda env export --no-builds > env_snapshot.yml`。

> **允许用 AI 辅助写代码**，但报告里出现的每个数字必须是你自己跑出来的。硕士层不强制提交 AI 验证记录（那是博士层 `ai_verification_log` 的要求），但若 AI 生成的代码导致了错误结论，按「结果正确性」扣分，不因"是 AI 写的"减免。

## ④ 评分标准

总分 100，折算为课程总成绩的 5%。

| 评分维度 | 权重 | 评分要点 |
|---|---|---|
| **流程完整性** | 40 | 交付物 ② 的全部文件齐全；六节报告结构完整；敏感性分析三组都跑了；脚本可原样重跑且与 `results/` 自洽；图表标签为英文 |
| **结果正确性** | 30 | 四个前处理数字全报（含 callable 比例）；`-ploidy` 与研究对象匹配；SNP 与 InDel 分开过滤且 InDel 用了更宽的 FS；每条 filter 的拦截计数与 `filter_counts.tsv` 对得上；6.2.6 四步的取舍与下游用途匹配（群体遗传学**不得**滤 MAF）；HIGH 变异未重复计数 |
| **方法选择与结果可信度说明** | 30 | 见下方四问，**评分不看结论对不对，看推理链是否闭合** |

### 「方法选择与结果可信度说明」的四个问题（契约 `method_justification`）

一页之内回答完，每问约 7–8 分：

| 要回答的问题 | 本专题的落点 | 不合格的写法 |
|---|---|---|
| **1. 为什么用这个检验 / 模型？** | 为什么用硬过滤而不是 VQSR（⑥ 6.2.5 的两条硬条件：可靠 truth set + 样本量，非模式物种两条都不满足）；为什么走 gVCF 联合调用 | "GATK Best Practices 就是这么写的" |
| **2. 为什么用这个阈值？** | 六条阈值逐条：QD 2.0 / FS 60 / MQ 40 / SOR 3 / MQRankSum −12.5 / ReadPosRankSum −8 各在拦什么，**这些数从哪来**（人类高深度 truth set），你验证过它在你的数据上合适吗（附 `fig2_qd_mq_hist.png`） | "这是 GATK 推荐值" |
| **3. 假阳性风险在哪？** | Ti/Tv 离本物种经验值多远；有没有哪条 filter 拦掉了 > 50% 的位点（说明该指标分布与 GATK 假设不符）；有没有 JEXL 静默失效（⑨-E7）；杂合位点占比是否异常 | "结果可靠" |
| **4. 什么证据能推翻你的结论？** | 你打算用什么独立证据证明阈值合适——Ti/Tv、孟德尔错误率、双 caller 交集、还是与已知位点的一致率；敏感性分析三组之间结论变了没有 | "需要进一步验证" |

## ⑤ 提交方式与截止

- **提交入口**：课程 LMS「专题作业 m03」；文件名 `学号_姓名_m03.zip`（≤ 200 MB，**不要**把 BAM 与原始 VCF 打进包里）
- **截止时间**：m03 课后 **第 10 天 23:59**
- **迟交**：3 天内按 90% 计，超过 3 天按 70% 计，超过 7 天不计分（可申请一次不扣分延期，须在截止前提出）
- **重交**：允许在截止前重复提交，以最后一次为准
- **诚信**：可与同学讨论方法，但数据处理与写作须独立完成；直接提交他人结果文件按学术不端处理

## ⑥ 常见失分点

来自讲义 ⑨ 与 ⑥ 6.4 的真实问题，**按出现频率与隐蔽程度排序**：

| # | 失分点 | 长什么样 | 怎么自查 |
|---|---|---|---|
| 1 | **过滤表达式引用了不存在的标签**（⑨-E7，最隐蔽） | 只有 `WARN JexlEngine - ... undefined variable MQRankSum`，退出码 0，**这条阈值一条位点也没拦** | 过滤前 `bcftools view -h \| grep INFO=` 确认标签存在；过滤后按 6.2.7 统计每条 filter 拦掉多少，全是 0 即没生效 |
| 2 | **不报 callable 比例就下"无变异"结论**（⑥ 6.1、6.4） | 某个已知抗性位点"没有变异"——其实该区域根本没有 callable 覆盖 | `gatk CallableLoci` 或 `samtools depth -a` 统计；这是**漏检不是阴性结论** |
| 3 | **`-R` 用了双引号**（⑨-E10） | `[E::bwa_set_rg] no ID within the read group line` | `\t` 被 shell 吃掉；一律用单引号 `-R '@RG\tID:...'` |
| 4 | **三套索引缺一套**（⑨-E1、E3、E4） | `Fasta dict file ... does not exist` ／ `incompatible contigs` ／ `some input files are not indexed` | `bwa-mem2 index` + `faidx` + `CreateSequenceDictionary` 三件套；全流程锁定同一份 FASTA |
| 5 | **`@RG` 的 `SM` 写成固定值**（⑥ 6.4） | VCF 里样本名全是 `sample1`；`bcftools stats` 的 `number of samples` 少于预期 | `samtools view -H x.bam \| grep '^@RG'`；多个 BAM 的 SM 写重了会被当成同一样本 |
| 6 | **`bcftools view -f PASS` 结果为空**（⑥ 6.4） | 没报错，就是空的 | `FILTER` 列是 `.` 说明从没跑过 `VariantFiltration`；`bcftools query -f '%FILTER\n' \| sort \| uniq -c` 一看便知 |
| 7 | **SNP 与 InDel 用同一套阈值** | InDel 被大量误杀，InDel/SNP 比例远低于经验值 | InDel 的 FS 阈值宽 3 倍多（200 vs 60），因为 InDel 本身就容易链不平衡（⑥ 6.2.4） |
| 8 | **HIGH 变异重复计数**（⑥ 6.3） | HIGH 变异数比实际位点数多出一截 | 一个变异可能有多条 ANN（不同转录本），默认第一条最严重；按位点去重后再统计 |
| 9 | **把 `MAF > 0.05` 写进群体遗传多样性分析**（⑥ 6.2.6、⑩ Q6） | 不报错。π、Tajima's D、SFS 全部失真 | 滤 MAF 会直接破坏频谱；**这是 p04 与 p05 分道扬镳的地方**，别照抄别人的过滤脚本 |
| 10 | **`MarkDuplicates` 崩在配对信息上**（⑨-E6） | `Value was put into PairInfoMap more than once` | 多 lane BAM 用 `cat` 合并了；改用 `samtools merge` / `gatk MergeSamFiles`，各 lane 的 `@RG ID` 必须唯一 |
| 11 | **GATK OOM**（⑨-E5） | `java.lang.OutOfMemoryError: Java heap space` | `--java-options "-Xmx16g"`，且 `qsub` 内存申请要大于 `-Xmx`（留 20% 给 JVM 开销） |
| 12 | **在自交系 / 克隆群体上用 `--hwe` 过滤**（⑥ 6.2.6） | 不报错，真实的生物学信号被当成基因分型错误剔除 | HWE 检验只在**随机交配群体**里可用于剔除分型错误 |
