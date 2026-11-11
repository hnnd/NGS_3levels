# L0-2 自测：R / tidyverse / ggplot2 基础

> 对应材料：[`02_lectures/prerequisites/l0_02_r/l0_02_r.md`](../../02_lectures/prerequisites/l0_02_r/l0_02_r.md)
> 模块 id `l0_02_r` ｜ 适用：本科 / 硕士 / 博士 ｜ 建议用时 **40–60 分钟**
> 契约：`course_contract.yaml` → `prerequisite_packs.selftest_spec`（10 题，≥2 道上机题，completion_based）

---

## 开始之前：这份自测怎么用

**1. 为什么有上机题（本自测共 3 道，第 8–10 题）。**
选择题能猜、能抄，做完你和教师都不知道你到底会不会。上机题的产出——**一段筛选汇总的代码、一张 `ggsave` 出来的图文件、一段判读说明**——直接反映能力，而且**正是后续课堂第一步就要做的事**：硕士 m04 拿到 DESeq2 结果表后的第一个动作就是 `filter(padj < 0.05) |> arrange(padj)`；博士 p01 的核心实践是**读一段被植入错误的差异表达 R 脚本并找出错误**；本科 u08 报告要求的四张图全部靠 ggplot2 + `ggsave`。做完这份自测，你不是"考过了"，你是把那一步提前练过了。

**2. 计分方式：完成即给分，不按对错计。**
目的是**拿到诊断数据**，不是筛人——教师看的是全班错在哪，好在首课用 15–20 分钟只过集中出错的点，不重讲、不补课。按对错计分会让人抄答案，错题分布随之失真，这个闸门就废了。

**3. 所以参考答案就直接附在文末（`## 参考答案与评分要点`）。**
既然不按对错计分，抄答案没有任何收益；而公开答案让这份自测同时是一份**学习工具**。**但请先自己做完再翻**：你写下的错误答案，比正确答案更有诊断价值。

**4. 请如实记录卡点。** 做不出来就在该题下写"卡在哪一步、报什么错"（把报错原文粘上）。这直接决定首课讲什么。

**5. 通过标准**：10 题全部作答（含 3 道上机题的提交物：代码 + 图文件 + 说明）即视为完成。
三层学生做同一份题；诊断参考线（**本科 ≥ 80%、硕/博 ≥ 60%**）只供教师看错题分布，**不计入成绩**。

**提交方式**：新建 `l0_02_<你的学号>.md`（或 `.R` + 说明），按题号写答案；上机题把**代码原文 + 控制台输出**粘进去，并附导出的图文件。

---

## 第一部分：概念与判断（第 1–7 题）

### Q1（出口能力：数据类型）

`read_csv()` 读进来一张表后，`glimpse(df)` 显示某列是 `<chr>`，但你确信它应该是数值。

(a) 列出**两种**会让数值列变成字符型的常见原因。
(b) 如果不管它直接画柱状图，x 轴或 y 轴会出现什么异常？
(c) 写出把这一列转回数值的一行代码（假设列名是 `n50`，缺失值被写成了 `"-"`）。

### Q2（出口能力：数据类型）

以下四种 R 数据结构，分别对应下面哪个生信场景？连线并各写一句理由。

```
结构：vector ／ data.frame ／ list ／ factor
场景：A. DESeq2 返回的分析对象      B. 样本信息表（样本名、分组、批次）
      C. 一列 contig 长度            D. 图上要按 control → treat 顺序排列的分组变量
```

### Q3（出口能力：dplyr 基本动词）

你有一张 DESeq2 结果表 `res`，列包括 `gene`、`baseMean`、`log2FoldChange`、`pvalue`、`padj`。
写出一段 dplyr 代码，得到「**显著上调**基因清单」：`padj < 0.05` 且 `log2FoldChange > 1`，按 `padj` 从小到大排序，只保留 `gene`、`log2FoldChange`、`padj` 三列。

### Q4（出口能力：dplyr 基本动词）

下面这段代码想算"每组的平均表达量"，但结果不对/有警告。指出问题并改正。

```r
res |>
  group_by(group) |>
  summarise(mean_expr = mean(expr))
```

再回答：为什么 `summarise()` 之后建议加 `.groups = "drop"`？

### Q5（出口能力：ggplot2 图层语法入门）

解释下面三行的**输出差异**（各画出什么样、有没有图例），并说明第三行错在哪。

```r
geom_point(aes(color = group))
geom_point(color = "steelblue")
geom_point(aes(color = "steelblue"))
```

### Q6（出口能力：ggplot2 图层语法入门 / 读入表格数据）

一张宽表 `qc`：一行一个样本，列有 `sample`、`reads_M`、`q30_pct`。
你想画"两个指标分面对比"的柱状图，直接写 `ggplot(qc, aes(x = sample, y = ???))` 就卡住了。

(a) 为什么宽表画不了？（用 ggplot2 的映射规则解释）
(b) 写出转换代码。
(c) 转换后 `facet_wrap()` 里为什么通常要加 `scales = "free_y"`？

### Q7（出口能力：画出基本图形并导出）

判断对错并说明理由：

(a) 图里想写中文标题，只要把 `title = "质量分布"` 写进 `labs()` 就行。
(b) `ggsave("p.png", width = 12, height = 8, dpi = 300)` 导出的图，字看着太小，应该把 `base_size` 调大。
(c) `ggsave("p.pdf")` 不写 `plot =` 也没关系，反正存的就是刚画的那张。
(d) `ggsave("results/figures/p.pdf", ...)` 在 `results/figures` 不存在时会自动建目录。

---

## 第二部分：上机题（第 8–10 题）

> **这三题必须真的跑 R**（RStudio Server 或 `Rscript` 都行）。提交物：代码原文 + 控制台输出 + 图文件。

### Q8（上机 ★ 出口能力：读入表格数据、筛选与汇总）

先在 R 里造出这份 CSV（**不依赖任何外部数据，人人可复现**）：

```r
library(tidyverse); set.seed(2026)
qc <- tibble(
  sample  = paste0("S", sprintf("%02d", 1:16)),
  group   = rep(c("control", "treat"), each = 8),
  batch   = rep(c("b1", "b2"), times = 8),
  reads_M = c(rnorm(8, 22, 3), rnorm(8, 26, 5)),
  q30_pct = c(rnorm(8, 93, 1.5), rnorm(8, 90, 3.0)))
write_csv(qc, "l0_02_qc.csv")
```

**要求**：**重新用 `read_csv()` 把它读回来**（不要直接用内存里的 `qc`），然后：
1. `glimpse()` 确认 5 列的类型；
2. 筛出 `q30_pct >= 90` 的样本；
3. 新增一列 `pass`（`q30_pct >= 90` 为 `"pass"`，否则 `"fail"`）——注意这一列要在**筛选前**加，否则全是 `pass`；
4. 按 `group` 分组，汇总每组的样本数、`reads_M` 均值、`q30_pct` 均值。

**提交物**：完整代码 + `glimpse()` 输出 + 汇总表的输出。

### Q9（上机 ★ 出口能力：画出基本图形并导出）

**用第 8 题的 `l0_02_qc.csv` 画一张 ggplot2 图并用 `ggsave` 导出。**

**要求**（每条都是评分点）：
1. 图形自选（散点 / 箱线 / 柱状皆可），但必须**用颜色或填充区分 `group`**；
2. **两个轴都有名字且带单位**（如 `Reads (million)`、`Q30 (%)`），图例有标题；
3. **图内所有文字一律英文**——这是课程铁律，Linux 上中文会变成方块 `□□□`；
4. 用 Okabe–Ito 色盲友好配色（如 `scale_color_manual(values = c(control = "#0072B2", treat = "#D55E00"))`）；
5. `ggsave()` 导出 PDF，**显式写 `plot = p`**，`width = 6, height = 4`；
6. 输出目录若不存在，先 `dir.create(..., recursive = TRUE)`。

**提交物**：
1. 完整代码；
2. 导出的 PDF 文件（连同作业一起交）；
3. 一句话说明：如果导出来发现字太小，你会改哪个参数、为什么（**不是**改 `base_size`）。

### Q10（上机 ★ 出口能力：把图读懂 + 把流程写成可重跑的脚本）

(a) 把第 9 题的代码改写成**可重跑的 R 脚本** `plot_qc.R`，用 `commandArgs(trailingOnly = TRUE)` 接收输入 CSV 与输出 PDF 两个参数（**不要写死路径**），并在结尾 `cat()` 一句成功标记。用 `Rscript plot_qc.R l0_02_qc.csv results/figures/qc.pdf` 跑通。

(b) 看着你画出来的图，写 100–150 字回答：这张图**想让读者接受的判断是什么**？两组的差异是"看起来有差别"还是"能下结论"？你还需要什么信息才敢下结论？

**提交物**：脚本全文 + `Rscript` 的命令与输出 + 100–150 字说明。

> (b) 问的正是硕士 m04 与博士 p06 每次出图后都要回答的问题；用什么检验、假阳性风险在哪，属于 `l0_06_stats` 模块，这里只要求你**意识到"图上有差别"不等于"有统计学差异"**。

---

## 出口能力对照表

| 题号 | 检验的出口能力 | 材料对应小节 |
|---|---|---|
| 1 | 数据类型（向量/数据框）：类型识别与修复 | 核心内容 §1 |
| 2 | 数据类型（向量/列表/数据框/因子） | 核心内容 §1 |
| 3 | `dplyr` 基本动词：`filter`/`arrange`/`select` | 上机操作 步骤 2 |
| 4 | `dplyr` 基本动词：`group_by` + `summarise` | 上机操作 步骤 2 |
| 5 | `ggplot2` 图层语法：`aes()` 内外之分 | 核心内容 §4 |
| 6 | 长表/宽表与 `pivot_longer`；分面 | 核心内容 §2；上机操作 步骤 3 |
| 7 | 导出与中文字体铁律 | 核心内容 §5；上机操作 步骤 5 |
| **8（上机）** | **读入表格数据 + 做筛选与汇总**（出口能力主干） | 上机操作 步骤 1–2 |
| **9（上机）** | **画出基本图形并导出**（出口能力主干） | 上机操作 步骤 3–5 |
| **10（上机）** | **写成可重跑脚本 + 读懂自己的图** | 上机操作 步骤 6 |

---

## 参考答案与评分要点

> **先自己做完再看。** 完成即给分、不按对错计——抄答案不会让你多得分，只会让你在 m04 / p02 的实践课上卡住。

**第 1 题** (a) 列里混进了 `NA` / `N/A` / `-` 这类占位符；或数字带了千分位逗号 `1,234`；（也接受：整列被引号包住、末尾有汇总行、用 `read.csv()` 读时列名被改）。
(b) 轴按**字符串**排序而不是数值——`10` 会排在 `9` 前面；若映射给连续标度还会报 `Discrete value supplied to continuous scale`。
(c) `df <- df |> mutate(n50 = as.numeric(na_if(n50, "-")))`

**第 2 题** C → `vector`（同类型的一排数）；B → `data.frame`（每列内部同类型、各列可不同、等长）；A → `list`（什么都能装、可嵌套，DESeq2/Seurat 的返回对象就是它）；D → `factor`（`levels` 决定图上出场顺序，否则按字母序 `control` 恰好在前，但换成 `treat`/`ck` 就乱了）。

**第 3 题**
```r
up <- res |>
  filter(padj < 0.05, log2FoldChange > 1) |>
  arrange(padj) |>
  select(gene, log2FoldChange, padj)
```
**要点**：用 `padj` 不是 `pvalue`（这正是 p01 那段"被植入错误的脚本"最爱藏的错）；`filter` 里多个条件用逗号即"且"。

**第 4 题** 问题有两处：① 没写 `.groups = "drop"`，会刷出 `` `summarise()` has grouped output by 'group' `` 提示，且返回值仍带分组，后续操作会**意外按组进行**；② 若 `expr` 里有 `NA`，`mean()` 直接返回 `NA`，要写 `mean(expr, na.rm = TRUE)`。改正：
```r
res |> group_by(group) |>
  summarise(n = n(), mean_expr = mean(expr, na.rm = TRUE), .groups = "drop")
```

**第 5 题**
- `aes(color = group)`：**数据驱动**——按 `group` 列上色，自动生成图例。
- `color = "steelblue"`（写在 `aes()` 外）：**固定设置**——所有点同一颜色，无图例。
- `aes(color = "steelblue")`：**错**。ggplot 把字符串 `"steelblue"` 当成一个只有一个水平的**分类变量**，于是所有点被涂成默认第一色（红），还多出一个写着 `steelblue` 的图例。
**记忆点：数据驱动写进 `aes()`，固定值写在 `aes()` 外。**

**第 6 题** (a) ggplot2 的**每个 `aes()` 映射必须指向数据框的一列**。宽表里 `reads_M` 和 `q30_pct` 是两列，没有一列叫"指标名"、也没有一列叫"数值"，所以无法把"指标"映射给分面、把"数值"映射给 y。
(b)
```r
long <- qc |> pivot_longer(cols = c(reads_M, q30_pct),
                           names_to = "metric", values_to = "value")
ggplot(long, aes(x = sample, y = value, fill = group)) + geom_col() +
  facet_wrap(~ metric, scales = "free_y", ncol = 1)
```
(c) 两个指标量纲差一个数量级以上（reads 是 20 左右、Q30 是 90 左右），共用一根 y 轴会把小的那个压平；`free_y` 让每个分面各用各的 y 轴。

**第 7 题** (a) **错**——Linux 服务器通常无中文字库，会显示成方块 `□□□`，控制台留下 `conversion failure ... dot substituted`。**课程铁律：图内一律英文，中文写进报告正文。**
(b) **错**——字号是绝对磅值，图越大字显得越小。**先把 `width`/`height` 调小**，再考虑 `base_size`。
(c) **错**——`plot =` 不写时存的是"最后画的那张图"，中间跑过别的代码就会存错，而且**不报错**。脚本里务必显式写。
(d) **错**——`ggsave` 不会建目录，会报 `Cannot find directory`。先 `dir.create("results/figures", recursive = TRUE, showWarnings = FALSE)`。

**第 8 题** 参考答案：
```r
library(tidyverse)
qc2 <- read_csv("l0_02_qc.csv", show_col_types = FALSE)
glimpse(qc2)     # 预期：sample <chr> group <chr> batch <chr> reads_M <dbl> q30_pct <dbl>

res <- qc2 |>
  mutate(pass = if_else(q30_pct >= 90, "pass", "fail")) |>   # 【先】加列
  filter(q30_pct >= 90)                                       # 【后】筛行

res |> group_by(group) |>
  summarise(n = n(), mean_reads = mean(reads_M),
            mean_q30 = mean(q30_pct), .groups = "drop")
```
**评分要点**：① 真的重新 `read_csv()` 了；② `mutate` 在 `filter` **之前**（顺序反了 `pass` 列会全是 `pass`——这是 dplyr 管道最典型的顺序陷阱）；③ `summarise` 带 `.groups = "drop"`。

**第 9 题** 参考答案：
```r
library(tidyverse)
qc2 <- read_csv("l0_02_qc.csv", show_col_types = FALSE)
p <- ggplot(qc2, aes(x = reads_M, y = q30_pct, color = group)) +
  geom_point(size = 2.5, alpha = 0.85) +
  scale_color_manual(values = c(control = "#0072B2", treat = "#D55E00")) +
  labs(x = "Reads (million)", y = "Q30 (%)", color = "Group",
       title = "Library yield vs base quality") +
  theme_bw(base_size = 12)
dir.create("results/figures", recursive = TRUE, showWarnings = FALSE)
ggsave("results/figures/qc_scatter.pdf", plot = p, width = 6, height = 4)
```
**评分要点**：轴名带单位；图例有标题；**全英文**；显式 `plot = p`；先 `dir.create`。
第 3 个提交物的正确回答：**改小 `width`/`height`**——字号是绝对磅值，图的物理尺寸越小，同样字号看起来越大。

**第 10 题** (a) 参考脚本：
```r
#!/usr/bin/env Rscript
suppressPackageStartupMessages(library(tidyverse))
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) stop("Usage: Rscript plot_qc.R <in.csv> <out.pdf>")
qc <- read_csv(args[1], show_col_types = FALSE)
p <- ggplot(qc, aes(x = reads_M, y = q30_pct, color = group)) + geom_point(size = 2.5) +
  scale_color_manual(values = c(control = "#0072B2", treat = "#D55E00")) +
  labs(x = "Reads (million)", y = "Q30 (%)", color = "Group") + theme_bw(base_size = 12)
dir.create(dirname(args[2]), recursive = TRUE, showWarnings = FALSE)
ggsave(args[2], p, width = 6, height = 4)
cat("Saved:", args[2], "\n")
```
**评分要点**：路径来自 `commandArgs()` 而不是写死；有成功标记；`Rscript` 真的跑通了。

(b) 开放题，无标准答案。合格的回答应当出现：**明确说出图想传达的判断**（如 "treat 组产量略高但 Q30 更分散"）；**承认 n = 8 / 点有重叠 / 只是描述性观察，不能据此下结论**；提出还需要的信息，例如**做检验并给出 p 值与效应量、检查批次（`batch` 列）是否与分组混杂、看每组的分布而不只是均值、确认样本量是否足够**。凡是写成"treat 组显著高于 control"却没有任何统计依据的，正是首课要纠的点。

---

*L0 自测版本 v1.0 ｜ 依据 contract_version 1.1 ｜ 最后更新 2026-08-29*
