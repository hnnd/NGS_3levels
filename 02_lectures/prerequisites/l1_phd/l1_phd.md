# L1：博士专用前置补丁（映射表）

> **适用对象**：博士 ｜ L1 预备课映射包 ｜ 零新增内容
>
> **阅读重点**：按所学博士专题，定位需要补读的硕士讲义章节、能力要求和自查方法。
>
> **自查**：`08_assessment/prerequisites/l1_phd_selftest.md`。

<!-- 契约：00_design/course_contract.yaml → prerequisite_packs.L1；设计依据：00_design/prerequisite_packs.md 第三节；原文档版本：v1.0，2026-08-29。 -->

博士层的 5 个专题依赖硕士层的特定能力。本映射包列出对应章节和最短补课路径，你可以根据自测结果补齐缺口。

---

## 学习目标

完成本前置包后，你应当能够：

1. 说出自己要上的每个博士专题依赖哪些硕士层章节，并在开课前把缺口补上
2. 读懂群体 VCF：8 个固定列 + FORMAT/样本列的结构，`GT`/`DP`/`GQ`/`AD` 的含义，以及 `--maf`/`--geno`/`--hwe` 这类过滤参数在拦什么
3. 读懂 DESeq2 的输入与输出：`dds` 对象、`results()` 六列、`padj` 与 `NA` 的来历，以及哪种矩阵能喂给下游
4. 说清直系同源与旁系同源的区别，并读懂 OrthoFinder 的 orthogroup 输出目录
5. 读一条 Snakemake rule，说出它的 `input` / `output` / `wildcards` 分别是什么、执行顺序由谁决定
6. 通过 L1 自测（10 题，含 2 道上机题），用错题定位自己还缺哪一块

> **自查**：根据错题指出需要补学的内容。自测完成即给分，具体要求见“自测入口”。

## 为什么这是前置

博士层 32 学时全部用于**设计与判断**，不讲基础操作。但博士层的 8 个专题里有 5 个**直接站在硕士层的能力之上**：

| 不补会在哪一步卡住 | 具体表现 |
|---|---|
| p03 实践第 4 步「时序差异分析」 | 打开 `DESeqDataSetFromMatrix` 就不知道 `colData` 该怎么写，`~ time` 的 LRT 更无从谈起 |
| p04 实践第 1 步「数据准备」 | 拿到群体 VCF 第一件事就是质控，`--max-missing 0.9 --maf 0.05` 里每个数字都得说出理由 |
| p05 实践第 1 步「基因型质控」 | `--maf 0.05 --geno 0.1 --mind 0.1` 三个阈值，以及常见模板里的 `--hwe 1e-6` 为什么在自交水稻上不加，课堂要求你逐条解释；不懂 VCF 只能背 |
| p06 实践「相关性整合」 | 转录组侧要用 `vst()` 结果而不是原始 counts，不知道 DESeq2 输出的形态就选错矩阵 |
| p07 全程 | 本专题起点是「你已经会写 Snakemake rule」，课堂从第一分钟就在讲 Nextflow 与 Snakemake 的范式差异 |

**L0 只覆盖到质控**（Linux、R、Conda、数据格式、FastQC、统计方法选择）。质控之后的变异检测、差异表达、比较基因组、工作流，L0 一概不管——那是硕士层的内容。L1 就是补这段落差的地图。

> 这一节回答的是「我凭什么要花时间补课」。答案：上面 5 行里任何一行你答不上来，对应的那次实践课你就只能抄命令。

## 核心内容

### 映射总表

| 模块 id | 博士专题 | 依赖的硕士层内容 |
|---|---|---|
| `l1_p03` | p03 宿主-病原互作组学 | 硕 m04《转录组分析》**§差异表达分析**<br>硕 m02《基因组组装与比较 / 泛基因组》**§比较基因组与直系同源** |
| `l1_p04` | p04 群体遗传学基础与群体基因组 | 硕 m03《重测序与变异检测》**§VCF 格式与变异过滤** |
| `l1_p05` | p05 GWAS 关联分析与后 GWAS 挖掘 | 硕 m03《重测序与变异检测》**§VCF 格式与变异过滤** |
| `l1_p06` | p06 多组学整合分析 | 硕 m04《转录组分析》**§表达矩阵与 DESeq2 输出** |
| `l1_p07` | p07 Nextflow / Snakemake 工作流开发 | 硕 m08《分析流程工程化与可重复报告》**§Snakemake rule 编写** |

**不在表内的三个专题**：p01（AI 辅助的生信工作流）、p02（单细胞与空间转录组）、p08（课题设计与汇报）**不依赖硕士层的特定章节**，L0 六个模块即足够。这不是漏写——p01 讲的是 AI 输出验证方法论，p02 的 Seurat/Scanpy 流程自成体系（需要的是 L0 的 R 能力），p08 是方案设计与汇报。**看到这三个专题没有 L1 条目，说明你不用为它们补课。**

### 补课材料的确切位置（硕士层已于 2026-08-29 完成重写）

硕士层讲义已按契约改名并建立锚点章节，下表是**当前有效**的定位：

| L1 模块 | 目标章节 | 文件 |
|---|---|---|
| `l1_p03` | m04 §差异表达分析 | `02_lectures/master/topic04_rnaseq/04_rnaseq_lecture.md` |
| `l1_p03` | m02 §比较基因组与直系同源 | `02_lectures/master/topic02_assembly_pangenome/02_assembly_pangenome_lecture.md` |
| `l1_p04` | m03 §VCF 格式与变异过滤 | `02_lectures/master/topic03_resequencing/03_resequencing_lecture.md` |
| `l1_p05` | m03 §VCF 格式与变异过滤 | 同上 |
| `l1_p06` | m04 §表达矩阵与 DESeq2 输出 | `02_lectures/master/topic04_rnaseq/04_rnaseq_lecture.md` |
| `l1_p07` | m08 §Snakemake rule 编写 | `02_lectures/master/topic08_workflow_engineering/08_workflow_engineering_lecture.md` |

> 这些章节都是按"**让没上过硕士课的博士生脱离前后文独立读懂**"的标准写的，
> 可以直接跳读，不必从讲义开头看起。

### l1_p03 — p03 宿主-病原互作组学的前置

**你在这个专题会遇到什么**
课堂实践第 4 步要你用 `DESeq2` 跑 `~ time` 的 LRT 做时序差异分析，第 5 步要你从 OrthoFinder 输出里提「物种特异基因」当候选毒力因子。也就是说，上课第一小时你就要**同时**动用差异表达和直系同源两套能力。此外还有一个反直觉的点：宿主与病原必须**分开归一化**——不理解 DESeq2 的 size factor 是怎么估出来的，就会把两个物种合起来算 TPM（AI 辅助任务专门考这个错）。

**你需要具备的能力清单**（每条都能自问自答才算过）

- 我能解释为什么 RNA-seq 计数数据用负二项分布而不是正态分布
- 我能写出 `~ batch + condition` 这样的设计公式，并说出它和 `~ condition` 的差别
- 我能说出 `padj` 和 `pvalue` 的区别，以及为什么筛差异基因要用 `padj`
- 我能解释 ortholog 与 paralog 的区别，以及为什么「BLAST 双向最佳命中」不等于直系同源
- 我能在 OrthoFinder 的输出目录里找到 `Orthogroups.GeneCount.tsv` 和 `Single_Copy_Orthologue_Sequences/`，并说出各自用途

**去哪里补**
① `02_lectures/master/topic04_rnaseq/04_rnaseq_lecture.md` → §3.3 差异表达统计检验、§4.3 下游分析中的 DESeq2 段（重写后为 m04 §差异表达分析）
② `02_lectures/master/topic02_assembly_pangenome/02_assembly_pangenome_lecture.md` → §2.4 同源基因术语、§3.1 同源基因鉴定方法对比、§4.3 步骤一：运行 OrthoFinder（重写后为 m02 §比较基因组与直系同源）

**最短补课路径（约 90 分钟）**
差异表达侧只看**分布假设 + 设计公式 + padj**三点，`3.1 定量方法对比`（Salmon vs featureCounts）可以跳过，p03 课堂会重讲双参考场景下的定量。
直系同源侧只看**同源概念辨析**与 **OrthoFinder 输出结构**；泛基因组的 core/shell/cloud 划分、CAFE5 基因家族扩张收缩**与 p03 无关，可跳过**。

### l1_p04 — p04 群体遗传学基础与群体基因组的前置

**你在这个专题会遇到什么**
课堂一上来就发给你一个群体 VCF（几十个个体 × 上百万位点），第一步就是质控：`vcftools --max-missing 0.9 --maf 0.05`、`plink --hardy`。如果不知道 VCF 的 FORMAT 字段和 GT 编码，这些参数就是天书——你会不明白 `--maf 0.05` 到底在按哪一列算频率，也不明白 `--hardy` 的输入是从哪几个基因型数出来的。更麻烦的是 p04 的统计要点专门讲「HWE 偏离到底是技术性还是生物学性」，这个判断的前提是你知道 `GT`、`DP`、`GQ` 分别在描述什么。

**你需要具备的能力清单**

- 我能说出 VCF 8 个固定列（CHROM POS ID REF ALT QUAL FILTER INFO）各是什么
- 我能解释 GT 字段里 `0/0`、`0/1`、`1/1`、`./.` 分别代表什么，以及 `|` 与 `/` 的区别
- 我能说出 `DP`、`GQ`、`AD` 三个 FORMAT 字段的含义，并指出哪个用于判断该个体该位点可不可信
- 我能解释硬过滤指标 QD / FS / MQ 各自在拦什么样的假阳性
- 我能区分**位点层面**的过滤（`--maf`、`--max-missing`）与**个体层面**的过滤（`--mind`、个体缺失率）

**去哪里补**
`02_lectures/master/topic03_resequencing/03_resequencing_lecture.md` → §5.1 VCF 格式详解、§5.2 基因型 (GT) 解读、§4.6 步骤五：变异过滤（重写后合并为 m03 §VCF 格式与变异过滤）

**最短补课路径（约 45 分钟）**
只需要 §5.1 + §5.2 + §4.6 三节。**GATK 全流程（§4.1–§4.5：建索引、比对、MarkDuplicates、BQSR、HaplotypeCaller）与 p04 无关，可全部跳过**——p04 的输入是别人已经 call 好的 VCF，你不需要会 call 变异，只需要会读和过滤。§3.5 结构变异检测同样跳过。

### l1_p05 — p05 GWAS 关联分析与后 GWAS 挖掘的前置

**你在这个专题会遇到什么**
p05 实践第一行命令就是 `plink --maf 0.05 --geno 0.1 --mind 0.1`（网上模板多带 `--hwe 1e-6`，RDP1 这类自交群体刻意不加），而大纲明确写着「**每个阈值须能说出理由**」。这四类参数横跨位点缺失率、个体缺失率、等位基因频率、HWE 四类质控逻辑，全部建立在 VCF 结构之上。后 GWAS 环节还要用 `bedtools intersect` 把候选区间和注释 GFF 取交集，这需要你清楚 VCF 的 CHROM/POS 坐标系统（1-based）与 BED（0-based）的差别。

**你需要具备的能力清单**

- 我能说出 `--maf 0.05` 过滤掉的是什么位点，以及为什么小样本 GWAS 要把 MAF 阈值调高
- 我能说出 `--geno`（位点缺失率）与 `--mind`（个体缺失率）的作用对象不同
- 我能解释为什么全基因组尺度的 HWE 过滤用 `1e-6` 而不是 `0.05`
- 我能把 VCF 转成 PLINK 的 bed/bim/fam 三件套，并说出 fam 文件六列的含义
- 我知道 VCF 的 POS 是 1-based、BED 是 0-based half-open，做区间交集时要注意坐标转换

**去哪里补**
与 `l1_p04` **完全相同**：`02_lectures/master/topic03_resequencing/03_resequencing_lecture.md` → §5.1、§5.2、§4.6（重写后为 m03 §VCF 格式与变异过滤）。

**最短补课路径（约 30 分钟）**
如果你已经为 p04 补过，**p05 不需要再补任何硕士层内容**。若只上 p05 不上 p04：只看 §5.1 VCF 格式详解与 §5.2 基因型解读即可，硬过滤指标（QD/FS/MQ）可以只看一遍知道存在——p05 拿到的通常是已过滤 VCF，你的工作是**群体层面**的二次质控。**不需要看 GATK 流程、不需要看 VQSR。**

### l1_p06 — p06 多组学整合分析的前置

**你在这个专题会遇到什么**
p06 要把转录组和代谢组/蛋白组放在一起做 WGCNA 与 MOFA2。转录组这一侧的输入**不是**原始 counts，也不是 TPM，而是 `vst()` 或 `rlog()` 的方差稳定化结果——喂错矩阵，WGCNA 的软阈值曲线会直接崩掉（无标度拟合 R² 上不去）。同时 p06 的统计要点强调「250 万个相关检验」的多重检验问题，你得先知道 DESeq2 的 `padj` 是怎么来的，才能理解为什么相关矩阵也必须做 BH 校正。

**你需要具备的能力清单**

- 我能说出 `dds` 对象里装了什么，以及 `counts()`、`vst()`、`rlog()` 三者输出的差别与各自去向
- 我能逐列说出 `results()` 输出的六列：baseMean、log2FoldChange、lfcSE、stat、pvalue、padj
- 我能说出 `padj` 出现 `NA` 的两种原因（独立过滤、离群值检测）
- 我能解释为什么 WGCNA 要用 vst 矩阵而不是原始 counts 或 TPM
- 我能说出富集分析要的是基因列表、多组学整合要的是方差稳定化矩阵——**下游需要什么形态，取决于下游方法的假设**

**去哪里补**
`02_lectures/master/topic04_rnaseq/04_rnaseq_lecture.md` → §5.1 DESeq2 结果表、§3.2 归一化/标准化（重写后为 m04 §表达矩阵与 DESeq2 输出）

**最短补课路径（约 40 分钟）**
只看 §3.2 与 §5.1。**上游定量（§4.2 Salmon 索引与定量）与 p06 无关，可跳过**——p06 假定表达矩阵已经在手。差异表达的统计细节（§3.3）若你已为 p03 补过就不必重复；只上 p06 不上 p03 的话，§3.3 里只需要知道「padj 是 BH 校正后的 p 值」这一条。

### l1_p07 — p07 Nextflow / Snakemake 工作流开发的前置

**你在这个专题会遇到什么**
p07 大纲写明「**起点上移**：不从零讲工作流概念，从『你已经会写 Snakemake rule』出发」。课堂第一个理论点就是两种范式的对比——Snakemake 从输出反推输入（pull），Nextflow 数据从上游流向下游（push）。实践第一步是「取一个已有的 Snakemake 流程，逐步转成 Nextflow DSL2」。你必须**自带**一个能跑的 Snakefile，或至少能读懂发下来的那个。AI 辅助任务考的正是转换后 channel 语义是否等价——不懂 Snakemake 的 wildcards 展开机制，这道题无从下手。

**你需要具备的能力清单**

- 我能读一条 rule，指出它的 `input` / `output` / `params` / `threads` / `log` / `shell` 各是什么
- 我能解释 `wildcards`：一条 rule 是怎么处理 N 个样本的，`{sample}` 从哪里获得取值
- 我能说出 `rule all` 存在的理由（声明「我最终想要什么文件」，DAG 从这里倒推）
- 我能用 `snakemake -n` 看执行计划、用 `--dag | dot` 画依赖图，并读懂输出
- 我能说出 `--use-conda` 的作用，以及它与 `l0_03_conda` 里的 `environment.yml` 怎么衔接

**去哪里补**
`02_lectures/master/topic08_workflow_engineering/08_workflow_engineering_lecture.md` → §3.4 工作流管理：Snakemake、§4.3 任务三：Snakemake 工作流（重写后为 m08 §Snakemake rule 编写）

**最短补课路径（约 60 分钟，含动手）**
§3.4 读懂 rule 结构 → §4.3 照着把那个 Snakefile 实际跑一遍（这一步不能只读，p07 要拿你的 Snakefile 当转换素材）。Git（§3.1）、Docker 镜像构建（§3.3 / §4.2）、R Markdown / Quarto 报告（§3.5 / §4.4）与 p07 前置无关——容器化在 p07 课堂上会以 Singularity 重新讲一遍，Git 属于 L0 工程习惯范畴。

## 上机操作

L1 没有新知识点，所以这一节不是练习，是**体检**：下面 4 条能在服务器上立即跑通并答出问题，说明对应前置已具备；答不出就回上一节的「去哪里补」。数据路径以课程共享目录为准（开课前 2 周随材料发布）。

**① 检验 `l1_p04` / `l1_p05` 前置：读群体 VCF**

```bash
# 结构：看有几个样本、几条固定列
bcftools query -l pop.vcf.gz | head
bcftools view -h pop.vcf.gz | grep -m1 '^#CHROM'

# 提取 GT 并统计基因型分布
bcftools query -f '[%GT\t]\n' pop.vcf.gz | head -1000 \
  | tr '\t' '\n' | grep -v '^$' | sort | uniq -c | sort -rn
```

**要能回答**：`0/0` `0/1` `1/1` `./.` 各占多少？缺失率高说明什么？若某位点几乎全是 `0/1`，`--hwe` 会不会把它滤掉，该不该滤？

**② 检验 `l1_p03` / `l1_p06` 前置：读 DESeq2 结果表**

```bash
head -3 deseq2_results.csv
awk -F, 'NR>1 && $7!="NA" && $7<0.05 && ($3>1 || $3<-1)' deseq2_results.csv | wc -l
```

**要能回答**：六列各是什么？第 7 列（padj）为什么会有 `NA`？上面这条命令实际用了哪两个筛选条件、分别是什么含义？如果把 `$7` 换成 `$6`（pvalue）结果会怎样、为什么不该这么做？

**③ 检验 `l1_p03` 前置：读 OrthoFinder 输出**

```bash
ls OrthoFinder/Results_*/Orthogroups/
head -3 OrthoFinder/Results_*/Orthogroups/Orthogroups.GeneCount.tsv
```

**要能回答**：这张表的行是什么、列是什么？哪些行是「物种特异基因」（只在一个物种中计数非零）？为什么建树用 `Single_Copy_Orthologue_Sequences/` 而不是全部 orthogroup？

**④ 检验 `l1_p07` 前置：读一条 Snakemake rule**

```text
rule salmon_quant:
    input:  r1="raw/{sample}_1.fq.gz", r2="raw/{sample}_2.fq.gz", idx="index/"
    output: "quant/{sample}/quant.sf"
    threads: 8
    log:    "logs/salmon/{sample}.log"
    shell:  "salmon quant -i {input.idx} -l A -1 {input.r1} -2 {input.r2} "
            "-p {threads} -o quant/{wildcards.sample} &> {log}"
```

**要能回答**：`{sample}` 的取值从哪里来？如果有 12 个样本，Snakemake 会生成几个任务？`{wildcards.sample}` 和 `{input.r1}` 在展开时机上有什么不同？若把 `output` 改成 `"quant/quant.sf"` 会发生什么？

> 用 `snakemake -n -s Snakefile` 验证你的答案——干跑不消耗计算资源，是最便宜的自查方式。

## 常见错误与排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 在硕士讲义里搜不到「VCF 格式与变异过滤」 | 那是第 3 轮重写后的标题，现有讲义还是旧标题 | 查本文「新旧章节标题对照」表，按旧标题找；或直接读 `01_syllabus/syllabus_master.md` 中标 ⚠ 的锚点表格行 |
| `bcftools query` 报 `index required` | VCF 未建索引 | `bcftools index pop.vcf.gz` 或 `tabix -p vcf pop.vcf.gz`；确认文件是 bgzip 压缩而非普通 gzip |
| `bcftools query -f '[%GT]'` 输出空白 | 该 VCF 只有 sites（无样本列），或字段名写错 | `bcftools view -h` 看 `#CHROM` 行是否有样本名；FORMAT 字段必须放在方括号 `[]` 内按样本循环 |
| DESeq2 结果表里大片 `padj` 为 `NA` | 独立过滤（低表达基因被剔出多重检验）或 Cook's distance 离群检测 | 这是正常行为，不是 bug；筛选时用 `!is.na(padj) & padj < 0.05`，不要把 `NA` 当成显著 |
| WGCNA 软阈值曲线怎么都上不去 | 喂了原始 counts 或 TPM 而不是 `vst()` / `rlog()` 矩阵 | 回 `l1_p06`；p06 课堂会再强调一次，但输入矩阵选错是自己的责任 |
| `snakemake -n` 报 `Wildcards in input files cannot be determined` | `rule all` 未声明目标文件，或 output 里没有对应通配符 | 回 `l1_p07` 的 `rule all` 部分；先让 `-n` 干跑通过再谈实跑 |
| 「我三个专题都要上，是不是要补三遍」 | 映射有重叠 | `l1_p04` 与 `l1_p05` 指向**同一节**；`l1_p03` 与 `l1_p06` 共用 m04 讲义的不同小节。按本文各条的「最短补课路径」去重后，全部补齐约 3–4 小时 |
| 「p02 单细胞没有 L1，是不是漏了」 | 不是漏 | p01 / p02 / p08 确实不依赖硕士层特定章节，L0 即足够；见「核心内容」总表下的说明 |

## 自测入口

**自测文件**：`08_assessment/prerequisites/l1_phd_selftest.md`

| 项目 | 安排 |
|---|---|
| 题量 | 10 题，其中 **≥ 2 道上机题** |
| 覆盖 | 5 个模块（`l1_p03` / `l1_p04` / `l1_p05` / `l1_p06` / `l1_p07`）全覆盖，每题标注所属模块 |
| 发布 | 开课前 **2 周**，与 L0 六个模块的自测一同发布 |
| 提交 | 开课前提交，**必须提交** |
| 计分 | **完成即给分、不按对错计**；L0 + L1 合计占总成绩 **8%** |
| 参考答案 | 因不按对错计分，**答案直接附在自测文件末尾**，做完再对照 |
| 首课处理 | 教师用 15–20 分钟只过错题分布，**不重讲**已写清的内容 |

**通过标准**：10 题全部作答，包含 2 道上机题的实际产出。请如实记录不会的内容，教师会根据错题安排首课复盘。

## 参考资料

**课程内部文档**（本前置包的全部实质内容都在这里）

- `01_syllabus/syllabus_phd.md` — 博士大纲，「前置能力与自测入口」一节及各专题详细内容
- `01_syllabus/syllabus_master.md` — 硕士大纲，5 个 L1 锚点章节均以 ⚠ 标注，附要点表格
- `00_design/prerequisite_packs.md` — 前置包设计文档，第三节为 L1 定义
- `00_design/course_contract.yaml` — `prerequisite_packs.L1`，映射的唯一真值来源
- `02_lectures/master/topic03_resequencing/03_resequencing_lecture.md` — `l1_p04` / `l1_p05` 补课材料
- `02_lectures/master/topic04_rnaseq/04_rnaseq_lecture.md` — `l1_p03` / `l1_p06` 补课材料
- `02_lectures/master/topic02_assembly_pangenome/02_assembly_pangenome_lecture.md` — `l1_p03` 直系同源部分补课材料
- `02_lectures/master/topic08_workflow_engineering/08_workflow_engineering_lecture.md` — `l1_p07` 补课材料

**外部规范与文档**（需要查字段定义时用，不必通读）

- VCF/BCF 格式规范（hts-specs）：https://samtools.github.io/hts-specs/
- bcftools 手册：https://samtools.github.io/bcftools/bcftools.html
- Danecek P, et al. The variant call format and VCFtools. *Bioinformatics*, 2011, 27(15):2156–2158. DOI: 10.1093/bioinformatics/btr330
- DESeq2 官方 vignette：https://bioconductor.org/packages/release/bioc/vignettes/DESeq2/inst/doc/DESeq2.html
- Love MI, Huber W, Anders S. Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2. *Genome Biology*, 2014, 15:550. DOI: 10.1186/s13059-014-0550-8
- Emms DM, Kelly S. OrthoFinder: phylogenetic orthology inference for comparative genomics. *Genome Biology*, 2019, 20:238. DOI: 10.1186/s13059-019-1832-y
- Snakemake 官方文档：https://snakemake.readthedocs.io/en/stable/
- Mölder F, et al. Sustainable data analysis with Snakemake. *F1000Research*, 2021, 10:33. DOI: 10.12688/f1000research.29032.2
- PLINK 1.9 文档：https://www.cog-genomics.org/plink/1.9/
