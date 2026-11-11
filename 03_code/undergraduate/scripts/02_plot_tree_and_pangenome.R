#!/usr/bin/env Rscript
# ============================================
# 脚本名称：02_plot_tree_and_pangenome.R
# 功能描述：① 把 IQ-TREE 的 .treefile 画成带支持率的系统进化树
#           ② 把 Roary 的 gene_presence_absence.csv 汇总成核心/软核心/壳/云基因组成图
#           对应讲义 u02 §⑤ 步骤 4.4；对应项目手册 §4.5、§4.6
# 用法：
#   Rscript 02_plot_tree_and_pangenome.R <输出目录> [tree:<core.treefile>] [roary:<gene_presence_absence.csv>]
#   Rscript 02_plot_tree_and_pangenome.R results/figures --demo   # 用内置示例数据试跑
# 环境：conda activate ngs_ug_phylo   （ggtree 在这个环境里，不在 ngs_ug_base）
# 注意：图中所有文字一律英文（Linux 服务器通常无中文字体，中文会显示为方块）
# 作者：王运生
# 日期：2026-08-29
# ============================================

suppressPackageStartupMessages({
  library(readr); library(dplyr); library(ggplot2)
})

# Roary 的分类阈值（与 Roary 默认口径一致）：按"在多少比例的菌株中出现"划分
PAN_LEVELS <- c("Core (>=99%)", "Soft-core (95-99%)", "Shell (15-95%)", "Cloud (<15%)")
PAN_COLORS <- c("#0072B2", "#56B4E9", "#E69F00", "#B0B0B0")
names(PAN_COLORS) <- PAN_LEVELS

usage <- function() {
  cat("用法: Rscript 02_plot_tree_and_pangenome.R <输出目录> [tree:path] [roary:path] | --demo\n")
}

# ---- 进化树：ggtree 只在 ngs_ug_phylo 环境里 ----
plot_tree <- function(treefile, out_pdf) {
  if (!requireNamespace("ggtree", quietly = TRUE) || !requireNamespace("ape", quietly = TRUE)) {
    message("[skip] 未安装 ggtree/ape —— 请先 conda activate ngs_ug_phylo（见讲义 ⑨ 9.1）")
    return(invisible(NULL))
  }
  if (!file.exists(treefile)) stop("找不到树文件: ", treefile, call. = FALSE)
  tree <- ape::read.tree(treefile)
  p <- ggtree::ggtree(tree) +
    ggtree::geom_tiplab(size = 3, align = TRUE) +                     # 菌株名（英文）
    ggtree::geom_nodelab(size = 2.5, hjust = -0.2) +                  # UFBoot / bootstrap 支持率
    ggplot2::xlim(0, max(ape::node.depth.edgelength(tree)) * 1.6) +   # 留白，否则标签被裁掉
    ggplot2::labs(title    = "ML phylogeny of core genes (IQ-TREE)",
                  subtitle = "Node labels = branch support; support is stability under resampling, not P(true)")
  ggsave(out_pdf, plot = p, width = 6.5, height = 5, units = "in")
  cat("Saved:", out_pdf, "\n")
}

# ---- Roary：gene_presence_absence.csv 前 14 列是注释，第 15 列起是每个菌株一列 ----
summarise_roary <- function(csv_path) {
  if (!file.exists(csv_path)) stop("找不到 Roary 输出: ", csv_path, call. = FALSE)
  df <- read_csv(csv_path, col_types = cols(.default = col_character()), progress = FALSE)
  n_isolates_col <- "No. isolates"
  if (!n_isolates_col %in% names(df)) {
    stop("列 'No. isolates' 不存在——确认这是 Roary 的 gene_presence_absence.csv", call. = FALSE)
  }
  # 菌株总数取自列数（前 14 列注释），不能用 max(No. isolates)：
  # 若没有任何基因存在于全部菌株，max 会小于真实总数，把 shell 误判成 core（UP-044）
  n_strains <- ncol(df) - 14L
  if (n_strains < 2L) stop("菌株列不足 2 列——前 14 列应为注释列", call. = FALSE)
  n_iso <- suppressWarnings(as.numeric(df[[n_isolates_col]]))
  if (anyNA(n_iso)) stop("'No. isolates' 含 ", sum(is.na(n_iso)), " 个缺失/非数值", call. = FALSE)
  if (any(n_iso < 1 | n_iso > n_strains)) {
    stop("'No. isolates' 超出 1..", n_strains, " 范围——检查列结构", call. = FALSE)
  }
  frac <- n_iso / n_strains
  classify(frac)
}

classify <- function(frac) {
  cls <- cut(frac, breaks = c(-Inf, 0.15, 0.95, 0.99, Inf),
             labels = rev(PAN_LEVELS), right = FALSE)
  tibble(class = factor(as.character(cls), levels = PAN_LEVELS)) |>
    count(class, name = "n_genes") |>
    tidyr::complete(class, fill = list(n_genes = 0))
}

demo_pan <- function() {
  tibble(class = factor(PAN_LEVELS, levels = PAN_LEVELS),
         n_genes = c(3120, 210, 890, 1450))
}

plot_pan <- function(df, out_pdf) {
  p <- ggplot(df, aes(x = class, y = n_genes, fill = class)) +
    geom_col(width = 0.65) +
    geom_text(aes(label = n_genes), vjust = -0.4, size = 3.5) +
    scale_fill_manual(values = PAN_COLORS) +
    scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +
    labs(x = "Gene class", y = "Number of gene clusters",
         title    = "Pan-genome composition (Roary)",
         subtitle = "Core = shared by nearly all isolates; cloud = strain-specific accessory genes") +
    theme_bw(base_size = 12) +
    theme(legend.position = "none", axis.text.x = element_text(angle = 15, hjust = 1))
  ggsave(out_pdf, plot = p, width = 6, height = 4, units = "in")
  cat("Saved:", out_pdf, "\n")
  print(as.data.frame(df))
}

main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) < 1) { usage(); quit(status = 1) }
  out_dir <- args[1]; specs <- args[-1]
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

  if (length(specs) == 0 || identical(specs[1], "--demo")) {
    message("[demo] 使用内置示例数据（不画树，只画泛基因组组成）")
    plot_pan(demo_pan(), file.path(out_dir, "pangenome_composition.pdf"))
    return(invisible(NULL))
  }

  get_path <- function(key) {
    hit <- grep(paste0("^", key, ":"), specs, value = TRUE)
    if (length(hit) == 0) return(NA_character_)
    sub(paste0("^", key, ":"), "", hit[1])
  }
  tree_path  <- get_path("tree")
  roary_path <- get_path("roary")

  if (!is.na(tree_path))  plot_tree(tree_path, file.path(out_dir, "core_gene_tree.pdf"))
  if (!is.na(roary_path)) plot_pan(summarise_roary(roary_path),
                                   file.path(out_dir, "pangenome_composition.pdf"))
  if (is.na(tree_path) && is.na(roary_path)) { usage(); quit(status = 1) }
  cat("提示：支持率衡量的是分支在数据重抽样下的稳定性，不是'该分支为真的概率'；\n")
  cat("      UFBoot 与标准 bootstrap 不在同一尺度，不可直接互相比较。\n")
}

main()
