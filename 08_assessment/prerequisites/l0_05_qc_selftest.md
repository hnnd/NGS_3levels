# L0-5 自测：FastQC / MultiQC 质量控制

> 对应材料：`02_lectures/prerequisites/l0_05_qc/l0_05_qc.md`
> 契约：`00_design/course_contract.yaml` → `prerequisite_packs.selftest_spec`
> **10 题，其中第 8、9、10 题为上机题** ｜ 建议用时 60–90 分钟 ｜ 开课前提交
> 前置：先完成 `l0_04_formats` 自测（本自测预设你会读 Phred 与 FASTQ 结构）

---

## 关于这份自测，先读这三条

**① 为什么必须有上机题（本自测 3 道）。** 选择题能猜对，也能抄。上机题的产出——一张模块解读表、一次清洗前后对比、一段带数字的质量结论——**直接反映你能不能动手判断**，而且**正是后续每个实践专题第一步要交的东西**。你在第 10 题写的那段结论，就是本科 u08 报告 §2.3/§2.4、硕士各专题实践开工前必须先有的东西。不是额外作业。

**② 计分方式：完成即给分，不按对错计。** 契约 `gate_mechanism.scoring: completion_based`。目的是**拿到诊断数据**（教师看错题分布，决定首次课那 15–20 分钟讲什么），不是筛人。按对错计分会让人抄答案，错题分布随之失真，闸门就废了。

**③ 因此参考答案直接附在文末。** 抄答案没有收益，公开答案反而让这份自测同时成为**学习工具**：做完一题就翻到后面对一次。**建议先全部做完再看答案**，但不做强制要求。

**三层期望差异**：本科（生信科班）通过线更高——第 8 题要对报告中出现的**每一个**模块写解读，第 10 题结论段落须每句带数字；硕士 / 博士（非生信专业）达到出口能力即可——第 8 题写清 3 个 FAIL 各自的原因与处理决定，第 9、10 题产出正确。

**本科生注意**：u04 已系统覆盖本模块内容，**材料可以跳过，这份自测不可以跳过**（`00_design/prerequisite_packs.md` §四）。

**每题都标注了它检验哪条「出口能力」**，做不出来就回材料对应小节。

---

## 第 1 题 ｜ 不做质控的代价，和做过头的代价

> **检验出口能力 1**：说出不做质控与过度清洗各自的代价。

(a) 举出**三个**具体后果，说明"不做质控会怎样"，并各自指明是由哪种数据缺陷引起的（不要写"结果不准"这种笼统说法）。
(b) 反过来，举出**两个**"过度清洗"的具体代价。
(c) 用一句话概括质控的目标——注意，"让 FastQC 全绿"不是正确答案，请说明为什么不是。

---

## 第 2 题 ｜ FastQC 到底在做什么

> **检验出口能力 2**：理解 FastQC 的性质与边界。

判断下列说法对错，**每条都要说明理由**：

(a) FastQC 需要参考基因组才能评估比对情况。
(b) FastQC 的每个模块都基于文件里的全部 read 统计。
(c) 一个模块报 FAIL，意味着统计上显著地存在问题。
(d) *Overrepresented sequences* 报出一条序列，FastQC 会告诉你它来自哪里。
(e) `summary.txt` 只有 10 行，说明这次运行不完整、有模块没跑出来。

---

## 第 3 题 ｜ 模块解读

> **检验出口能力 2**：说出模块的横纵轴与正常形态。

对下面四个模块，各写出：**横轴是什么 / 纵轴是什么 / 正常长什么样 / 出现异常最可能的原因**。

(a) Per base sequence quality
(b) Per sequence GC content
(c) Adapter Content
(d) Sequence Length Distribution

---

## 第 4 题 ｜ 红灯辨析（本自测的核心题）

> **检验出口能力 3**：区分"真问题"与"这类数据本来就长这样"。

下面五种情况，哪些**必须处理**、哪些**不该处理**？逐条说明理由；判定为"不该处理"的，要说清它的**成因**。

(a) 一份 RNA-seq 数据的 *Per base sequence content* 前 12 bp 报 FAIL。
(b) 一份细菌 WGS 数据的 *Adapter Content* 在 130 bp 之后升到 15%。
(c) 一份 RNA-seq 数据的 *Sequence Duplication Levels* 报 FAIL，去重后只剩 40% 的 read。
(d) 一份 16S 扩增子数据的 *Per base sequence content* 全程报 FAIL。
(e) 一份细菌 WGS 数据的 *Per sequence GC content* 出现两个峰，主峰 42%，次峰 60%。

**(f)** 写出你在面对任何一个红灯时应该先问自己的那一句话。

---

## 第 5 题 ｜ 接头污染

> **检验出口能力 4**：接头识别与去除。

(a) 接头为什么会出现在 read 里？用文库片段长度与读长的关系解释。
(b) 由此推论：*Adapter Content* 曲线抬升的**高度**反映了什么？
(c) 一个人不去接头就直接比对，会看到什么现象？（至少说两个，其中一个要落在 CIGAR 上）
(d) fastp 的 `--detect_adapter_for_pe` 与 `--adapter_sequence` 各在什么情况下用？如果 fastp 报 `reads with adapter trimmed: 0` 但 FastQC 的 Adapter Content 明显抬升，你会怎么办？

---

## 第 6 题 ｜ 参数推理

> **检验出口能力 4**：解释 fastp 参数为什么取这个值。

某人手上是 **PE100** 数据，直接照抄了讲义里给 PE150 用的 fastp 命令：

```bash
fastp -i A_R1.fq.gz -I A_R2.fq.gz -o c_R1.fq.gz -O c_R2.fq.gz \
    --detect_adapter_for_pe --cut_front --cut_tail \
    --cut_window_size 4 --cut_mean_quality 30 --length_required 80
```

结果：`reads failed due to too short` 占 35%，且清洗后 Q30 百分比反而**下降**了。

(a) 35% 被判"太短"是哪个参数造成的？你会改成多少，依据是什么？
(b) Q30 反而下降，是哪个参数造成的？机制是什么？
(c) `--cut_mean_quality 30` 有什么问题？
(d) 如果不动 `--length_required` 而只把 `--cut_mean_quality` 调低，能解决 (a) 吗？为什么？

---

## 第 7 题 ｜ 长读长

> **检验出口能力 6**：判断长读长该看什么、不该看什么。

(a) 列出 PacBio / Nanopore 数据**该看**的四个指标，和**不该看**的三个 FastQC 模块。
(b) 为什么 per-base quality 曲线在长读长上没有意义？请从"FastQC 怎么画这张图"入手解释。
(c) 长读长数据要不要做末端质量修剪？给出理由（提示：组装器做了什么）。
(d) 有人对 PacBio 的 FASTA 跑 FastQC，得到 `SequenceFormatException: ID line didn't start with '@'`。这个报错说明什么？**他真正的错误是哪一步？**

---

## 第 8 题 ｜【上机】跑 FastQC，判断每个红灯是真问题还是正常现象

> **检验出口能力 2、3**：逐模块解读；区分真问题与正常特征。
> **提交物**：`summary.txt` 全文 + 一张模块解读表 + (c) 的一段说明。

按材料「上机操作」步骤 1–2 生成演示数据并跑 FastQC。

(a) 贴出 `summary.txt` 全文。你应该看到 **3 个 FAIL**。
(b) 做一张表，格式为 **模块名 → 现象 → 我的判断（正常 / 需处理 / 需进一步查证）→ 依据**。
 - 硕博：至少覆盖 3 个 FAIL 模块。
 - 本科：覆盖 `summary.txt` 里出现的**每一个**模块。
 - 允许写"需进一步查证"，但必须写清**要查什么**。
(c) **这 3 个 FAIL 不是 3 个独立的问题。** 说明其中哪两个可以追溯到同一个根本原因，是什么原因，你怎么判断的。由此说明：为什么"先诊断再动手"比"看到红灯就裁剪"更重要？
(d) 这份演示数据是**模拟的 DNA-seq**。如果它是 **RNA-seq**，(b) 表中哪一行的判断会改变？为什么？

---

## 第 9 题 ｜【上机】用 fastp 清洗，并解释那个"变差了却正常"的指标

> **检验出口能力 4、5**：运行 fastp 并解释参数；从对比中读出结论。
> **提交物**：fastp 的 `Filtering result` 段 + 清洗前后 summary 的 `diff` 输出 + (c)(d) 的说明。

按材料「上机操作」步骤 3–4 清洗并复检。

(a) 贴出 fastp 输出的 `Read1 before/after filtering` 与 `Filtering result` 两段。回答：Q20 与 Q30 百分比各变化了多少？`reads with adapter trimmed` 是多少？这个数字和生成数据时设定的"30% 的 read 带接头"对得上吗？
(b) 贴出清洗前后 `summary.txt` 的 `diff` 输出。3 个 FAIL 分别变成了什么？
(c) ⚠ **有一个模块从 PASS 掉到了 WARN。** 是哪一个？**这算不算清洗失败？** 说明它变差的原因，并由此得出一条一般性的结论。
(d) 逐个解释你用的这四个参数为什么取这个值：`--cut_tail`（为什么不加 `--cut_front`）、`--cut_window_size 4`、`--cut_mean_quality 20`、`--length_required 50`。
(e) 跑一次 `multiqc --force -o qc -n multiqc_report.html qc`。单样本时 MultiQC 的价值有限——用一句话说明它在什么情况下才不可替代。

---

## 第 10 题 ｜【上机】长读长质控，并写出可直接进报告的结论

> **检验出口能力 6、7**：长读长判据；带数字依据的书面结论。
> **提交物**：统计输出 + 一段 100–150 字的质量结论 + (c)(d) 的回答。

用 `l0_04_formats` 上机步骤 0 生成的 `longreads.fa`（固定种子，数字应与参考答案一致）。

(a) 运行材料「上机操作」步骤 5 的统计命令，贴出输出的五个数字。
(b) **写一段 100–150 字的质量结论**，按"数据是什么 → 数字 → 与判据比 → 结论 → 预处理选择及理由"的结构组织。要求：**每个结论后面都有数字**，并写清判据来源（深度多少算够？N50 要跨过什么？）。这段话可直接填进本科 u08 报告的 §2.3 与 §2.4。
(c) 你在 (b) 里写了"不做质量修剪"。**这个决定的理由是什么？** 如果只写"无"而不给理由，会有什么问题？
(d) 假设同一批数据深度是 94×，但 N50 只有 1.2 kb。**深度够了，为什么还是不行？** 说明这两个指标各自管什么、为什么不能互相替代。

---

## 参考答案与评分要点

> **再次提醒**：本自测完成即给分，不按对错计。答案公开是为了让你做完立刻自查。**标 ★ 的是最常错的点。**

### Q1

(a) ① **比对率下降**——接头是人工序列，基因组里根本没有，带接头的 read 要么比不上、要么末端被大段软剪切；② **假变异**——read 末端质量掉到 Q10 时每 10 个碱基错 1 个，这些错误在中等深度位点会被变异检测软件当成真 SNP；③ **组装碎片化**——错误碱基在组装图里制造大量假分支，组装器无法延伸，contig 数暴涨。
(b) ① 把所有 Q<30 的碱基都切掉会损失一大半数据；② 把 RNA-seq 前 10–15 bp 一律裁掉换来的是更短的 read 和更低的比对特异性（而那段"异常"本来就无害）。
(c) **质控的目标不是让 FastQC 全绿，而是让数据适合下游分析。** ★ "全绿"不是目标，因为 PASS/WARN/FAIL 的阈值是按典型 WGS 数据定的；你的数据只要不是典型 WGS，为了变绿而做的处理往往是在损失真实信号。

### Q2

(a) **错**。FastQC 是**无参考**的体检，只看 FASTQ 文件本身的统计分布，完全不涉及比对。
(b) **错**。★ 质量、GC、长度统计的是全部 read，但 *Sequence Duplication Levels* 与 *Overrepresented sequences* **只用文件开头的 10 万条**建模（官方 Help 写明 `first 100,000 sequences`），且过表达序列分析会把长于 50 bp 的 read 截断到 50 bp。多个 lane 拼起来的文件，开头那部分不一定代表全体。
(c) **错**。★ PASS/WARN/FAIL 是 Babraham 依据典型 DNA-seq 经验分布**人工设定的固定阈值**，**既没有零假设也没有 p 值**，不是统计检验的结果。
(d) **错**。它只报告现象。来源可能是接头、rRNA、高表达基因、PhiX 或污染——**必须你自己去 BLAST**。
(e) **错**。*Per tile sequence quality* 只在 read 名含 Illumina lane/tile 坐标时出现，*Kmer Content* 在 v0.12 默认关闭。**模块少不是运行不完整，是这份数据用不上它们。**

### Q3

(a) **Per base sequence quality**：横轴 = read 上的碱基位置，纵轴 = 该位置所有 read 的 Q 值箱线图。正常 = 全程在绿区（Q≥28），末端略降（相位偏移导致的系统性衰减）。异常：中段突然塌陷 → 该 lane 有气泡或试剂问题；整体偏低 → 上机浓度或文库问题。
(b) **Per sequence GC content**：横轴 = 每条 read 的 GC 百分比，纵轴 = read 条数。正常 = 单个正态样的峰，峰位等于物种 GC 含量。异常：**双峰或肩峰 → 污染**（另一物种、接头二聚体、rRNA）。
(c) **Adapter Content**：横轴 = 碱基位置，纵轴 = 该位置起接头序列的累计占比。正常 = 贴着 0 的平线。异常：末端抬升 → 文库片段短于读长，必须去接头。
(d) **Sequence Length Distribution**：横轴 = read 长度，纵轴 = 条数。原始 Illumina 数据正常 = 一根竖线（长度全一致）。★ **清洗后变成一个分布是正常的**（修剪造成），不是问题。

### Q4

(a) **不该处理。** ★ 成因是建库用的**随机六聚体引物并非真正随机**，对某些起始序列有偏好，导致前十几个碱基组成系统性偏离（**Hansen et al. 2010, DOI: 10.1093/nar/gkq224**）。这是该建库方式的固有特征；STAR / HISAT2 完全能容忍。裁掉换来的是更短的 read 和更差的比对特异性。
(b) **必须处理。** 15% 远超 5% 的经验阈值，说明文库片段明显短于读长。用 fastp 去接头。
(c) **不该处理。** 高表达基因（actin、rRNA 残留）本来就被测到成千上万次，序列相同的 read 是**真实的生物学信号**。★ RNA-seq **不做去重**；DNA-seq / WES 才需要 `MarkDuplicates`。去掉 60% 的 read 等于削掉真实表达量。
(d) **不该处理。** 扩增子测的就是同一段保守区，所有 read 在同一位置碱基几乎相同，四条线当然不平行。**这是设计使然**，处理反而会破坏后续 DADA2 去噪。
(e) **需进一步查证，不要直接修剪。** 双峰指向污染（另一物种、接头二聚体或 rRNA）。★ 正确顺序是**先把过表达序列 BLAST 一下定性**，再决定是过滤、丢样本还是重做文库——盲目修剪解决不了污染。
(f) **"这个红灯，是数据的问题，还是这类数据本来就长这样？"**

### Q5

(a) 文库片段（insert）**比读长短**时，测序仪读完真实序列后会继续读进另一端的接头。片段 120 bp、读长 150 bp，则每条 read 末尾 30 bp 是接头。
(b) 反映**文库片段大小分布**——抬升越早越高，说明短片段占比越大。
(c) ① 比对率下降；② ★ CIGAR 里出现大量**末端软剪切 `S`**（比对器把接头段剪掉不参与比对），例如 `100M50S`。另外还可能看到插入片段长度估计异常。
(d) `--detect_adapter_for_pe` 用于双端数据、且不确定接头序列时（从 R1/R2 重叠区自动推断）；`--adapter_sequence` 用于已知建库试剂盒时，比自动检测更稳。★ 若 trimmed 为 0 而 FastQC 明显抬升，说明**自动检测没认出来**：从 FastQC 报告里看 Adapter Content 命中的是哪一类接头（TruSeq / Nextera / smallRNA），再用 `--adapter_sequence` 显式指定（TruSeq 常见 `AGATCGGAAGAGC`）。

### Q6

(a) **`--length_required 80`**。★ 这个值是按 PE150 定的；PE100 的 read 只有 100 bp，修剪掉一点末端就跌破 80。应改为 **36 左右**（一般取读长的 1/3 上下，PE150 用 50，PE100 用 36）。
(b) **`--cut_front`**。5' 端质量本来就好，从前端滑窗切掉的是**好碱基**，同时 3' 端的坏碱基未必切干净，于是分母变小而坏碱基占比上升，Q30 百分比反而下降。★ **通常只开 `--cut_tail`**。
(c) `--cut_mean_quality 30` 过严：Q30 = 0.1% 错误率，把大量完全可用的碱基（Q20–Q29）当垃圾切掉。常规下限用 **20**（Q20 = 1% 错误率）。
(d) **不能**。`--cut_mean_quality` 调低会让修剪变温和、read 保留得更长，确实能减少一部分"太短"，但根本原因是**长度阈值本身对 PE100 不合理**。★ 两个参数管的是不同环节：一个决定切多少，一个决定切完之后留不留。必须改 `--length_required`。

### Q7

(a) **该看**：读长分布形状、**read N50**、总碱基量、估算深度（最长 read 也算，可作第五项）。**不该看**：per-base sequence quality、per base sequence content、adapter content。
(b) ★ FastQC 把所有 read 的第 1 位对齐画箱线图。Illumina 的 read 都是 150 bp，"第 100 位"对所有 read 都意味着"接近末端"，有可比性；PacBio 的 read 有 500 bp 也有 8 万 bp，"第 100 位"对前者是末端、对后者是刚开头，**把它们放进同一个箱子统计出来的数字无法解释**。何况长读长的错误是**随机分布**的，根本不存在"第几个碱基更容易错"。
(c) **不要修剪。** Canu 与 Flye 在组装流程内自带 read 纠错（error correction）与筛选环节；外部修剪会缩短 read，**削弱组装器跨越重复区的能力**——而长读长的全部价值就在于这个跨越能力。
(d) 报错本身说明 FastQC 只认 FASTQ（首行必须是 `@`），而 FASTA 首行是 `>`。★ 但**他真正的错误不是"文件格式不对"，而是"选错了工具"**——长读长数据本来就不该跑 FastQC。修正方向不是把 FASTA 转成 FASTQ，而是改用读长分布 / N50 / 深度这套判据。

### Q8

(a) 期望的 `summary.txt`（3 个 FAIL）：

```text
PASS	Basic Statistics	demo_R1.fq.gz
FAIL	Per base sequence quality	demo_R1.fq.gz
PASS	Per sequence quality scores	demo_R1.fq.gz
FAIL	Per base sequence content	demo_R1.fq.gz
PASS	Per sequence GC content	demo_R1.fq.gz
PASS	Per base N content	demo_R1.fq.gz
PASS	Sequence Length Distribution	demo_R1.fq.gz
PASS	Sequence Duplication Levels	demo_R1.fq.gz
PASS	Overrepresented sequences	demo_R1.fq.gz
FAIL	Adapter Content	demo_R1.fq.gz
```

(b) 三个 FAIL 的参考解读：

| 模块 | 现象 | 判断 | 依据 |
|---|---|---|---|
| Adapter Content | 末端曲线明显抬升 | **需处理** | 接头是人工序列，留着会压低比对率并造成末端软剪切 |
| Per base sequence content | 后段四条线剧烈分离 | **需处理（但不是独立问题）** | 30% 的 read 末段是同一条固定接头序列，把该位置碱基组成拉偏；去接头后自然消失 |
| Per base sequence quality | 末端箱线图落入红区 | **需处理** | 相位偏移造成的系统性衰减；用滑窗修剪，不要一刀切固定长度 |

(c) ★ *Adapter Content* 与 *Per base sequence content* 追溯到**同一个原因：末端的接头污染**。判断依据是：数据里 30% 的 read 片段短于读长，末段是同一条固定序列——固定序列既会被 Adapter Content 检出，也必然让该位置的 ACGT 比例偏离。**一次去接头能同时消除两个红灯。** 这就是"先诊断再动手"的价值：看到 3 个红灯就做 3 种处理，等于对同一个问题重复下刀，多切的那部分全是净损失。
(d) 若是 RNA-seq，★ **Per base sequence content 那一行的判断可能要改成"正常，不处理"**——RNA-seq 前 10–15 bp 的组成偏离来自随机六聚体引物偏差（Hansen et al. 2010），是建库方式的固有特征。**注意区分位置**：本演示数据的偏离在**末端**（接头造成，要处理），随机引物偏差在**开头**（不处理）。另外 RNA-seq 的 Duplication Levels 报红也不该处理。

### Q9

(a) 期望输出：

```text
Read1 before filtering:  total reads: 2000   Q20 bases: 190000(95%)   Q30 bases: 128000(64%)
Read1 after  filtering:  total reads: 2000   Q20 bases: 172152(100%)  Q30 bases: 128000(74.3529%)
Filtering result:
reads passed filter: 2000
reads failed due to low quality: 0
reads failed due to too many N: 0
reads failed due to too short: 0
reads with adapter trimmed: 608
bases trimmed due to adapters: 13848
```

Q20 从 95% → **100%**，Q30 从 64% → **74.4%**，都是上升。`reads with adapter trimmed: 608` 与设定的 30%（600 条）吻合（多出的 8 条是随机序列偶然匹配上接头开头），★ 也与 FastQC 的 Adapter Content FAIL 相互印证——**两个独立来源指向同一结论，这才叫证据。**

(b) 期望 `diff`（下面是压缩排版，真实输出每个差异占 4 行：`NcN` / `< 旧` / `---` / `> 新`）：

```text
2c2  FAIL Per base sequence quality   →  WARN
4c4  FAIL Per base sequence content   →  PASS
7c7  PASS Sequence Length Distribution →  WARN
10c10 FAIL Adapter Content            →  PASS
```

3 个 FAIL 全部消除（两个到 PASS，一个到 WARN）。

(c) ★ 是 ***Sequence Length Distribution*，从 PASS 掉到 WARN。这不算清洗失败。** 原因：修剪让 read 长度不再整齐划一，分布从一根竖线变成一个真实分布，FastQC 按"长度应当一致"的阈值报了 WARN。**一般性结论：某个指标在清洗后变差，本身不是失败的证据——必须看它变差的原因。** 这是本模块第三个"红灯（黄灯）不是问题"的实例，而且是你自己动手做出来的。

(d) `--cut_tail` 而不加 `--cut_front`：5' 端质量本就好，从前端切会损失好碱基并可能拉低 Q30（见第 6 题）。`--cut_window_size 4`：窗口太小会对单个坏碱基过敏、太大会切得过狠，4 是通用值。`--cut_mean_quality 20`：Q20 = 1% 错误率，是常规下限；设 30 会切掉大量正常碱基。`--length_required 50`：本演示是 100 bp 读长，50 是合理下限；太短的 read 会产生大量多重比对。

(e) ★ MultiQC 的价值在**多样本横向对比**：某个样本的 %GC 与其他样本差 15 个百分点、某条质量曲线明显低于其余——这类问题（污染、拿错样、index 串扰）**只有把样本放在一起看才发现得了**，单样本报告永远看不出来。

### Q10

(a) 期望输出：

```text
条数=1200  总量=9.41 Mb  N50=10254 bp  最长=94597 bp  深度=94.1X
```

(b) 参考写法：

> 本数据为模拟 PacBio 长读长（FASTA 格式，无质量值行），共 1200 条 read，碱基总量 9.41 Mb，read N50 = 10 254 bp，最长 read 94 597 bp；按目标基因组 100 kb 估算，测序深度约 94×。该深度高于长读长细菌组装通常要求的 50×（100× 更稳），N50 = 10.3 kb 远超 rRNA 操纵子长度（约 5 kb），能跨越主要重复区；最长 read 达 94 kb，佐证 DNA 提取完整。**判定数据质量满足组装要求。** 未对数据做质量修剪，原因是 Canu 与 Flye 在组装流程内已包含 read 纠错环节，外部修剪会缩短 read、削弱跨越重复区的能力。

★ 评分看的是**结构**：数据是什么 → 数字 → 与判据比 → 结论 → 预处理选择及理由。只写"数据质量良好"在任何一层都会失分。

(c) 理由是**组装器自带纠错**（Canu、Flye 在组装前含 error correction 环节），外部修剪只会缩短 read、削弱跨重复区能力，得不偿失。★ 只写"无"而不给理由的问题是：**看报告的人无法判断你是有意选择还是根本忘了做**。报告模板写"如无则注明无"不等于"可以不解释"——预处理是一个**决定**，决定必须有依据。

(d) ★ 深度和 N50 管的是两件不同的事：**深度管"每个碱基被读到几次"**，它决定纠错能力与共识序列准确性；**N50 管"单条 read 能跨多长"**，它决定能不能一次性穿过重复区。N50 = 1.2 kb 小于 rRNA 操纵子的约 5 kb，read 会整条落在重复区内部，无法判断属于哪个拷贝——**组装仍然会在重复区断开，拼不出完成图**。此时深度再高也没用，因为高深度的短 read 无法提供"跨越"信息。正确做法是回去查 DNA 提取（避免剪切力、改用大片段方案）并重新建库。

---

**做完后**：把上机题的提交物（第 8 题 `summary.txt` 与模块解读表、第 9 题 fastp 输出与 `diff`、第 10 题统计结果与结论段落）整理成一份文件提交。**首次课只用 15–20 分钟过集中出错的点，不重讲。**
