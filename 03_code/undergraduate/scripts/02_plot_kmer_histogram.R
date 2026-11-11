#!/usr/bin/env Rscript
# ============================================
# 脚本名称：02_plot_kmer_histogram.R
# 功能描述：把 Jellyfish histo 输出画成 k-mer 频率分布图，并标注错误峰 / 主峰 / 重复峰
#           支持多个 k 值同图对比（对应项目手册 §4.1 要求的 k=17/21/25 三档比较）
#           对应讲义 u02 §⑤ 步骤 4.1 与步骤 7
# 用法：
#   Rscript 02_plot_kmer_histogram.R <out.pdf> <k1>:<histo1> [<k2>:<histo2> ...]
# 示例：
#   Rscript 02_plot_kmer_histogram.R kmer.pdf 21:survey/reads.histo
#   Rscript 02_plot_kmer_histogram.R kmer_multi.pdf \
#           17:survey/reads.k17.histo 21:survey/reads.histo 25:survey/reads.k25.histo
#   Rscript 02_plot_kmer_histogram.R demo.pdf --demo      # 无数据时用内置模拟数据试跑
# 环境：conda activate ngs_ug_base
# 注意：图中所有文字一律英文（Linux 服务器通常无中文字体，中文会显示为方块）
# 作者：王运生
# 日期：2026-08-29
# ============================================

suppressPackageStartupMessages({
  library(readr)
  library(dplyr)
  library(ggplot2)
})

set.seed(42)                    # 可复现：模拟数据每次一致
XLIM_MAX <- 150                 # x 轴截断上限；不截断的话主峰会被超长尾巴压平
ERROR_PEAK_CUTOFF <- 5          # 深度小于该值的区域视为测序错误峰，不参与主峰搜索

usage <- function() {
  cat("用法: Rscript 02_plot_kmer_histogram.R <out.pdf> <k>:<histo> [<k>:<histo> ...]\n")
  cat("      Rscript 02_plot_kmer_histogram.R <out.pdf> --demo\n")
}

# ---- 读入一个 histo 文件：两列（深度、该深度的 distinct k-mer 数），无表头 ----
read_histo <- function(path, k) {
  if (!file.exists(path)) stop("文件不存在: ", path, call. = FALSE)
  df <- read_table(path, col_names = c("depth", "n_kmers"), col_types = "dd")
  df$k <- factor(paste0("k = ", k), levels = unique(paste0("k = ", k)))
  df
}

# ---- 生成模拟数据：错误峰 + 主峰 + 重复峰，用于无真实数据时演示 ----
make_demo <- function(k = 21, main_peak = 45) {
  depth <- 1:300
  n <- 3e7 * exp(-depth / 1.2) +                                   # 错误峰（低频，极高）
       8e5 * exp(-((depth - main_peak)^2) / (2 * 8^2)) +           # 主峰 ≈ 测序深度
       1.2e5 * exp(-((depth - 2 * main_peak)^2) / (2 * 12^2))      # 重复峰 ≈ 主峰 2 倍
  tibble(depth = depth, n_kmers = pmax(n, 1), k = factor(paste0("k = ", k)))
}

# ---- 找主峰：跳过错误峰区域后取最大值所在深度 ----
find_main_peak <- function(df) {
  cand <- dplyr::filter(df, depth > ERROR_PEAK_CUTOFF, depth <= XLIM_MAX)
  if (nrow(cand) == 0) return(NA_real_)
  cand$depth[which.max(cand$n_kmers)]
}

plot_spectrum <- function(df) {
  # 逐个 k 值找主峰（用 base R 的 split，避免依赖较新的 dplyr::pick）
  peaks <- do.call(rbind, lapply(split(df, df$k), function(d) {
    data.frame(k = d$k[1], peak = find_main_peak(d))
  }))
  peaks <- peaks[!is.na(peaks$peak), , drop = FALSE]

  p <- ggplot(df, aes(x = depth, y = n_kmers, color = k)) +
    geom_line(linewidth = 0.6) +
    # 主峰位置画虚线并标注数值 —— 基因组大小 ≈ 总 k-mer 数 / 主峰位置
    geom_vline(data = peaks, aes(xintercept = peak, color = k),
               linetype = "dashed", linewidth = 0.4, show.legend = FALSE) +
    geom_text(data = peaks, aes(x = peak, y = Inf, label = paste0("main peak = ", peak)),
              vjust = 1.6, hjust = -0.05, size = 3, show.legend = FALSE) +
    coord_cartesian(xlim = c(0, XLIM_MAX)) +   # 截断而非删数据（xlim() 会真的丢点）
    scale_y_log10() +                          # 错误峰比主峰高几个数量级，必须取 log
    scale_color_manual(values = c("#0072B2", "#D55E00", "#009E73", "#CC79A7")) +
    labs(title    = "k-mer frequency spectrum",
         subtitle = "Left spike = sequencing errors; main peak ~ depth; peak at 2x = repeats",
         x = "k-mer depth", y = "Number of distinct k-mers (log10)", color = NULL) +
    theme_bw(base_size = 12) +
    theme(panel.grid.minor = element_blank(), legend.position = "top")

  list(plot = p, peaks = peaks)
}

main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) < 2) { usage(); quit(status = 1) }
  out_pdf <- args[1]
  specs   <- args[-1]

  df <- if (identical(specs[1], "--demo")) {
    message("[demo] 使用内置模拟数据（无需真实 histo 文件）")
    make_demo()
  } else {
    bind_rows(lapply(specs, function(s) {
      parts <- strsplit(s, ":", fixed = TRUE)[[1]]
      if (length(parts) != 2) stop("参数格式应为 <k>:<histo 路径>，收到: ", s, call. = FALSE)
      read_histo(parts[2], parts[1])
    }))
  }

  res <- plot_spectrum(df)
  dir.create(dirname(out_pdf), recursive = TRUE, showWarnings = FALSE)  # ggsave 不会替你建目录
  ggsave(out_pdf, plot = res$plot, width = 7, height = 4.5, units = "in")

  cat("Saved:", out_pdf, "\n")
  cat("Main peak (approx. sequencing depth) per k:\n")
  print(as.data.frame(res$peaks))
  cat("提示：基因组大小 ≈ 总 k-mer 数 / 主峰位置；不同 k 值的估计有系统性差异，\n")
  cat("      这正是项目手册要求跑 k=17/21/25 三档对比的原因。\n")
}

main()
