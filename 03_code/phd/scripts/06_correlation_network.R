#!/usr/bin/env Rscript
# ============================================================
# p06 多组学整合 —— 模块特征基因 × 代谢物相关网络
# 环境：conda activate ngs_phd_multiomics
#
# 讲义对应：⑦ 统计插件（全矩阵 BH 校正、置换检验、选择性推断）、
#           ④ 4.9（相关 vs 偏相关、阈值的决定性作用）、⑤ 步骤 5
#
# 【统计纪律】先算完整相关矩阵 → BH 校正 → 按 q 值筛边。
# 反过来"先挑好看的边再算 p 值"是选择性推断，p 值失效（讲义 ⑦(1)）。
#
# Cytoscape 与 igraph 两条路径（讲义 ⑤ 步骤 0）：
#   本脚本输出的 edges.tsv / nodes.tsv 两者通用；
#   同时用 igraph 直接出一张 PDF，保证无图形界面的集群上也能复现。
#
# 所有图的 title / axis / legend 一律英文。
# ============================================================
suppressPackageStartupMessages({
  library(readr); library(dplyr); library(tidyr); library(ggplot2); library(igraph)
})
set.seed(20260829)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  stop("用法: 06_correlation_network.R <module_eigengenes.tsv> <metab_clr.tsv> <outdir> [选项]\n",
       "  module_eigengenes.tsv : 06_wgcna_analysis.R 的输出（行=module, 列=样本）\n",
       "  metab_clr.tsv         : 06_metabolome_preprocess.R 的输出（行=feature, 列=样本）\n",
       "选项:\n",
       "  --method spearman  CLR 后仍可能有偏态与离群点，秩相关更稳\n",
       "  --fdr 0.05         BH 校正后的 q 值阈值\n",
       "  --n-perm 1000      置换检验次数：打乱样本标签重跑，估整体假发现水平")
}
me_f <- args[1]; met_f <- args[2]; outdir <- args[3]
opt_n <- function(flag, default) {
  i <- match(flag, args); if (is.na(i) || i == length(args)) default else as.numeric(args[i + 1])
}
opt_s <- function(flag, default) {
  i <- match(flag, args); if (is.na(i) || i == length(args)) default else args[i + 1]
}
method <- opt_s("--method", "spearman")
fdr    <- opt_n("--fdr", 0.05)
n_perm <- opt_n("--n-perm", 1000)
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

read_mat <- function(path) {
  d <- read_tsv(path, show_col_types = FALSE) |> as.data.frame()
  rownames(d) <- d[[1]]
  as.matrix(d[, -1, drop = FALSE])
}
me <- read_mat(me_f); met <- read_mat(met_f)
common <- intersect(colnames(me), colnames(met))
if (length(common) < 6) stop("两份输入的共同样本少于 6 个，检查样本命名")
me <- me[, common, drop = FALSE]; met <- met[, common, drop = FALSE]
n <- length(common)
n_tests <- nrow(me) * nrow(met)
message(sprintf("样本 %d 个；模块 %d 个 × 代谢特征 %d 个 = %s 次相关检验",
                n, nrow(me), nrow(met), format(n_tests, big.mark = ",")))
message(sprintf("  若两侧完全独立，p < 0.05 下期望约 %.0f 对「显著」（讲义 ⑦(1)）",
                0.05 * n_tests))

# ---- 1. 全矩阵相关 + p 值 ----
cor_mat <- cor(t(me), t(met), method = method, use = "pairwise.complete.obs")
t_stat  <- cor_mat * sqrt((n - 2) / (1 - cor_mat^2))
p_mat   <- 2 * pt(-abs(t_stat), df = n - 2)

edges <- expand_grid(module = rownames(cor_mat), feature = colnames(cor_mat)) |>
  mutate(cor = as.vector(t(cor_mat)), p = as.vector(t(p_mat)))
# ---- 2. BH 校正：对**全部**检验，不是对你挑出来的那些（讲义 ⑦(1)）----
edges$q_BH <- p.adjust(edges$p, method = "BH")
write_tsv(edges, file.path(outdir, "correlation_all_pairs.tsv"))

n_raw <- sum(edges$p < 0.05, na.rm = TRUE)
sig <- edges |> filter(q_BH < fdr) |> arrange(q_BH)
message(sprintf("p < 0.05：%d 对；BH q < %.2f：%d 对", n_raw, fdr, nrow(sig)))
if (nrow(sig) == 0) {
  message("没有边通过 FDR。**这是诚实的结果，不是失败**（讲义 ⑥ 与 l0_06_stats）。")
  message("  报告写法：『无相关对通过 BH 校正（q < 0.05）』，并把 top |r| 的对作为未校正候选列出。")
}

# ---- 3. 置换检验：BH 之外的第二道闸（讲义 ⑦(1)）----
perm_counts <- replicate(n_perm, {
  idx <- sample(seq_len(n))
  cm <- cor(t(me), t(met[, idx, drop = FALSE]), method = method, use = "pairwise.complete.obs")
  ts <- cm * sqrt((n - 2) / (1 - cm^2))
  pv <- 2 * pt(-abs(ts), df = n - 2)
  sum(p.adjust(as.vector(pv), method = "BH") < fdr)
})
perm_p <- (sum(perm_counts >= nrow(sig)) + 1) / (n_perm + 1)
message(sprintf("置换检验：真实通过 %d 条；置换中位数 %.1f 条；经验 p = %.4f",
                nrow(sig), median(perm_counts), perm_p))
write_tsv(tibble(observed_edges = nrow(sig), perm_median = median(perm_counts),
                 perm_max = max(perm_counts), empirical_p = perm_p),
          file.path(outdir, "permutation_summary.tsv"))

# ---- 4. 阈值敏感性：网络对阈值稳不稳（讲义 §4.9）----
thr <- seq(0.5, 0.95, by = 0.05)
sens <- tibble(threshold = thr,
               n_edges = sapply(thr, function(t) sum(abs(sig$cor) >= t, na.rm = TRUE)))
ggplot(sens, aes(threshold, n_edges)) + geom_line() + geom_point() +
  labs(title = "Edge count vs correlation threshold (FDR-passing pairs only)",
       x = "|correlation| threshold", y = "Number of edges") + theme_bw()
ggsave(file.path(outdir, "threshold_sensitivity.png"), width = 6, height = 4, dpi = 150)

# ---- 5. 导出边表/点表：Cytoscape 与 igraph 通用 ----
edge_out <- sig |>
  transmute(source = module, target = feature, correlation = cor,
            abs_cor = abs(cor), direction = ifelse(cor > 0, "positive", "negative"),
            p, q_BH)
write_tsv(edge_out, file.path(outdir, "edges.tsv"))
nodes <- bind_rows(
  tibble(id = unique(edge_out$source), omics = "transcriptome_module"),
  tibble(id = unique(edge_out$target), omics = "metabolite_feature")
)
# 提醒：代谢物节点应从注释表补一列 annotation_confidence（MSI Level），
#       并让它一路传到图注与正文（讲义 §4.5）。
write_tsv(nodes, file.path(outdir, "nodes.tsv"))

# ---- 6. igraph 出图：Cytoscape 的脚本化替代路径（讲义 ⑤ 步骤 0 路径 B）----
if (nrow(edge_out) > 0) {
  g <- graph_from_data_frame(edge_out, directed = FALSE, vertices = nodes)
  V(g)$color <- ifelse(V(g)$omics == "transcriptome_module", "#4C72B0", "#DD8452")
  E(g)$color <- ifelse(E(g)$direction == "positive", "#C44E52", "#55A868")
  E(g)$width <- 1 + 3 * E(g)$abs_cor
  pdf(file.path(outdir, "network_igraph.pdf"), width = 9, height = 9)
  plot(g, layout = layout_with_fr(g), vertex.size = 6, vertex.label.cex = 0.6,
       vertex.label.color = "black",
       main = sprintf("Module-metabolite network (BH q < %.2f, %d edges)", fdr, nrow(edge_out)))
  legend("bottomleft", legend = c("Transcriptome module", "Metabolite feature"),
         pch = 21, pt.bg = c("#4C72B0", "#DD8452"), bty = "n")
  legend("bottomright", legend = c("Positive", "Negative"),
         lty = 1, col = c("#C44E52", "#55A868"), bty = "n")
  dev.off()
}

message("完成。edges.tsv / nodes.tsv 可直接导入 Cytoscape（讲义 ⑤ 步骤 0 路径 A）。")
message("提醒（讲义 ⑦(4)）：通过 FDR 的边仍只是**候选假说**——共同上游、批次伪迹、")
message("  组成性伪相关都要逐项排除，之后还需正交实验验证才能谈因果。")
