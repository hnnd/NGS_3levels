#!/usr/bin/env Rscript
# ============================================================
# m07 宏基因组 —— 组成性数据分析（讲义 ⑦ 统计插件的配套代码）
# 环境：conda activate ngs_ms_microbiome
#
# 三件事，对应讲义 ⑦ 的三个小节：
#   1) ⑦-7.1/7.2 伪相关演示：两个绝对丰度独立的类群，转相对丰度后出现负相关
#   2) ⑦-7.3/7.4 CLR 变换与零值处理：伪计数 vs Dirichlet 抽样的差别
#   3) ⑦-7.6 差异丰度两法对比：ALDEx2 与 ANCOM-BC 各跑一次，报显著类群重叠度
#
# 作业评分点（08_assessment/master/assignments/m07_metagenome_assignment.md）：
#   重叠度低本身就是结论——说明结果对方法选择敏感，只有两法都支持的类群
#   才能作为主要结论。本脚本把重叠度算出来并写进 overlap_summary.tsv。
#
# 所有图的 title / axis / legend 一律英文（Linux 中文字体常显示为方块）。
# ============================================================
suppressPackageStartupMessages({
  library(ggplot2)
})
set.seed(20260829)

a <- commandArgs(trailingOnly = TRUE)
if (length(a) < 1) {
  stop("用法: 07_compositional_analysis.R <outdir> [abundance.tsv] [metadata.tsv]\n",
       "  outdir        : 输出目录\n",
       "  abundance.tsv : 行=类群, 列=样本, 第一列为 taxon_id（原始计数，不要用相对丰度）\n",
       "  metadata.tsv  : 列 sample, group（两组）\n",
       "  省略后两个参数时只跑第 1 部分（伪相关演示），用于课堂演示与自测")
}
outdir <- a[1]
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
abund_path <- if (length(a) >= 2) a[2] else NA_character_
meta_path  <- if (length(a) >= 3) a[3] else NA_character_

# ------------------------------------------------------------------
# 1) 伪相关演示（讲义 ⑦-7.1、7.2）
#    这一段不需要任何数据，也不需要装任何包——先亲眼看一次再谈方法。
# ------------------------------------------------------------------
message("[1/3] 伪相关演示")
n <- 200
abs_a  <- rlnorm(n, 5, 1)      # 类群 A 的绝对丰度
abs_b  <- rlnorm(n, 5, 1)      # 类群 B 的绝对丰度，与 A 独立生成
others <- rlnorm(n, 7, 0.3)    # 其余类群合计
tot    <- abs_a + abs_b + others
rel_a  <- abs_a / tot
rel_b  <- abs_b / tot

cor_abs <- cor(abs_a, abs_b)
cor_rel <- cor(rel_a, rel_b)
message(sprintf("  绝对丰度 r = %+.3f（本来就独立）", cor_abs))
message(sprintf("  相对丰度 r = %+.3f（纯粹由“总和为 1”造出来）", cor_rel))

demo <- rbind(
  data.frame(x = abs_a, y = abs_b, space = sprintf("Absolute (r = %+.2f)", cor_abs)),
  data.frame(x = rel_a, y = rel_b, space = sprintf("Relative (r = %+.2f)", cor_rel))
)
p1 <- ggplot(demo, aes(x, y)) +
  geom_point(alpha = 0.5, size = 1.2) +
  geom_smooth(method = "lm", formula = y ~ x, se = FALSE, colour = "firebrick") +
  facet_wrap(~ space, scales = "free") +
  labs(title = "Spurious correlation induced by closure",
       subtitle = "Taxa A and B are independent in absolute abundance",
       x = "Taxon A", y = "Taxon B") +
  theme_bw(base_size = 11)
ggsave(file.path(outdir, "fig_spurious_correlation.png"), p1,
       width = 8, height = 3.6, dpi = 300)

write.table(
  data.frame(comparison = c("absolute", "relative"), pearson_r = c(cor_abs, cor_rel)),
  file.path(outdir, "spurious_correlation.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)

if (is.na(abund_path)) {
  message("未提供丰度表，只跑第 1 部分。完整分析请传入 abundance.tsv 与 metadata.tsv。")
  quit(save = "no", status = 0)
}

# ------------------------------------------------------------------
# 读入真实数据
# ------------------------------------------------------------------
cts <- read.delim(abund_path, row.names = 1, check.names = FALSE)
meta <- read.delim(meta_path, stringsAsFactors = FALSE)
if (!all(c("sample", "group") %in% names(meta)))
  stop("metadata.tsv 必须含 sample 与 group 两列")
if (!setequal(colnames(cts), meta$sample))
  stop("丰度表列名与 metadata$sample 不一致：",
       paste(setdiff(colnames(cts), meta$sample), collapse = ","))
cts <- cts[, meta$sample, drop = FALSE]        # 强制对齐顺序（m04 ⑨-E2 同类坑）
grp <- factor(meta$group)
if (nlevels(grp) != 2) stop("本脚本只处理两组比较，实际有 ", nlevels(grp), " 组")
if (max(cts) <= 1) warning("最大值 <= 1，输入看起来是相对丰度——差异丰度方法需要原始计数")

zero_frac <- mean(cts == 0)
message(sprintf("[读入] %d 个类群 × %d 个样本；零占比 %.1f%%", nrow(cts), ncol(cts), 100 * zero_frac))

# 预过滤：低流行度类群既无功效又拖累多重检验（阈值要写进方法学）
min_prev <- max(2, floor(0.1 * ncol(cts)))
keep <- rowSums(cts > 0) >= min_prev
message(sprintf("  预过滤：保留在 >= %d 个样本中出现的类群 %d/%d", min_prev, sum(keep), nrow(cts)))
cts <- cts[keep, , drop = FALSE]

# ------------------------------------------------------------------
# 2) CLR 变换与零值处理（讲义 ⑦-7.3、7.4）
#    对比两种伪计数，看低丰度类群的 CLR 值被扰动了多少。
# ------------------------------------------------------------------
message("[2/3] CLR 变换与零值敏感性")
clr <- function(x, pseudo) {
  x <- x + pseudo
  log(x) - mean(log(x))          # 每个样本内减自身几何平均的对数
}
clr_05 <- apply(cts, 2, clr, pseudo = 0.5)
clr_10 <- apply(cts, 2, clr, pseudo = 1.0)
delta <- rowMeans(abs(clr_05 - clr_10))

sens <- data.frame(
  taxon = rownames(cts),
  mean_count = rowMeans(cts),
  zero_frac = rowMeans(cts == 0),
  clr_shift_pseudo_0.5_vs_1.0 = delta
)
sens <- sens[order(-sens$clr_shift_pseudo_0.5_vs_1.0), ]
write.table(sens, file.path(outdir, "clr_zero_sensitivity.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)
message(sprintf("  伪计数 0.5→1.0 造成的平均 CLR 位移：中位 %.3f，最大 %.3f（最大者零占比 %.0f%%）",
                median(delta), max(delta), 100 * sens$zero_frac[1]))

p2 <- ggplot(sens, aes(x = zero_frac, y = clr_shift_pseudo_0.5_vs_1.0)) +
  geom_point(alpha = 0.6, size = 1.3) +
  labs(title = "Pseudocount choice hits sparse taxa hardest",
       x = "Fraction of zeros", y = "Mean |CLR(+0.5) - CLR(+1.0)|") +
  theme_bw(base_size = 11)
ggsave(file.path(outdir, "fig_clr_zero_sensitivity.png"), p2,
       width = 5.2, height = 3.6, dpi = 300)
write.table(data.frame(taxon = rownames(clr_05), clr_05, check.names = FALSE),
            file.path(outdir, "clr_matrix.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)

# ------------------------------------------------------------------
# 3) 差异丰度两法对比（讲义 ⑦-7.6）
#    两法结果不一致是常态；重叠度本身就是要报告的结果。
# ------------------------------------------------------------------
message("[3/3] ALDEx2 与 ANCOM-BC 对比")
alpha <- 0.05
sig_aldex <- NULL
sig_ancom <- NULL

if (requireNamespace("ALDEx2", quietly = TRUE)) {
  ax <- ALDEx2::aldex(reads = as.data.frame(cts), conditions = as.character(grp),
                      mc.samples = 128, test = "t", effect = TRUE, denom = "all")
  ax$taxon <- rownames(ax)
  write.table(ax, file.path(outdir, "aldex2_results.tsv"),
              sep = "\t", quote = FALSE, row.names = FALSE)
  # 讲义 ⑦-7.6：ALDEx2 推荐把 |effect| > 1 作为辅助判据，不要只看 q 值
  sig_aldex <- ax$taxon[ax$wi.eBH < alpha & abs(ax$effect) > 1]
  message(sprintf("  ALDEx2: %d 个显著（wi.eBH < %.2f 且 |effect| > 1）", length(sig_aldex), alpha))
} else {
  warning("未安装 ALDEx2，跳过。安装：mamba install -n ngs_ms_microbiome -c bioconda bioconductor-aldex2")
}

if (requireNamespace("ANCOMBC", quietly = TRUE) &&
    requireNamespace("TreeSummarizedExperiment", quietly = TRUE)) {
  tse <- TreeSummarizedExperiment::TreeSummarizedExperiment(
    assays = list(counts = as.matrix(cts)),
    colData = S4Vectors::DataFrame(group = grp, row.names = colnames(cts)))
  ab <- ANCOMBC::ancombc2(data = tse, assay_name = "counts", fix_formula = "group",
                          p_adj_method = "BH", prv_cut = 0, group = "group",
                          struc_zero = TRUE, alpha = alpha, verbose = FALSE)
  res <- ab$res
  write.table(res, file.path(outdir, "ancombc_results.tsv"),
              sep = "\t", quote = FALSE, row.names = FALSE)
  qcol <- grep("^q_group", names(res), value = TRUE)[1]
  if (is.na(qcol)) stop("ANCOM-BC 输出里找不到 q_group* 列，检查 fix_formula 与分组列名")
  sig_ancom <- res$taxon[res[[qcol]] < alpha]
  message(sprintf("  ANCOM-BC: %d 个显著（%s < %.2f）", length(sig_ancom), qcol, alpha))
} else {
  warning("未安装 ANCOMBC/TreeSummarizedExperiment，跳过。",
          "安装：mamba install -n ngs_ms_microbiome -c bioconda bioconductor-ancombc")
}

if (!is.null(sig_aldex) && !is.null(sig_ancom)) {
  both <- intersect(sig_aldex, sig_ancom)
  union_n <- length(union(sig_aldex, sig_ancom))
  jaccard <- if (union_n > 0) length(both) / union_n else NA_real_
  summary_tbl <- data.frame(
    metric = c("aldex2_sig", "ancombc_sig", "both", "union", "jaccard"),
    value  = c(length(sig_aldex), length(sig_ancom), length(both), union_n, round(jaccard, 3)))
  write.table(summary_tbl, file.path(outdir, "overlap_summary.tsv"),
              sep = "\t", quote = FALSE, row.names = FALSE)
  write.table(data.frame(taxon = both), file.path(outdir, "consensus_taxa.tsv"),
              sep = "\t", quote = FALSE, row.names = FALSE)
  message(sprintf("  重叠：%d 个（Jaccard = %.3f）→ 主要结论只用这 %d 个，其余进补充材料",
                  length(both), jaccard, length(both)))
  if (!is.na(jaccard) && jaccard < 0.5)
    message("  ⚠ 重叠度低于 0.5：结论对方法选择敏感，必须在方法学中如实报告（讲义 ⑦-7.6）")
} else {
  message("  两法未都跑成，无法计算重叠度——作业要求两法都跑，请先补装缺失的包")
}

message("完成，输出在 ", normalizePath(outdir))
