#!/usr/bin/env Rscript
# ============================================
# 脚本名称：02_plot_assembly_metrics.R
# 功能描述：① 把两套组装（Canu / Flye）的 QUAST 指标画成分面对比柱状图
#           ② 把 BUSCO 的 C/S/D/F/M 结果画成堆叠百分比条形图
#           这两张图是项目手册 §4.2「必须对比 Canu 和 Flye 并说明选择理由」的证据图
#           对应讲义 u02 §⑤ 步骤 4.2、4.3
# 用法：
#   Rscript 02_plot_assembly_metrics.R <输出目录> [quast_canu:<report.tsv> quast_flye:<report.tsv>]
#                                                 [busco_canu:<short_summary.txt> busco_flye:<...>]
#   Rscript 02_plot_assembly_metrics.R results/figures --demo    # 用内置示例数据试跑
# 环境：conda activate ngs_ug_base
# 注意：图中所有文字一律英文（Linux 服务器通常无中文字体，中文会显示为方块）
# 作者：王运生
# 日期：2026-08-29
# ============================================

suppressPackageStartupMessages({
  library(readr); library(dplyr); library(tidyr); library(ggplot2); library(stringr)
})

PALETTE_ASM <- c(Canu = "#0072B2", Flye = "#D55E00")               # 色盲友好（Okabe–Ito）
PALETTE_BUSCO <- c("Single-copy" = "#0072B2", "Duplicated" = "#56B4E9",
                   "Fragmented"  = "#E69F00", "Missing"    = "#B0B0B0")
BUSCO_LEVELS <- c("Single-copy", "Duplicated", "Fragmented", "Missing")
METRIC_LEVELS <- c("# contigs", "N50 (Mb)", "Largest contig (Mb)", "Total length (Mb)")

usage <- function() {
  cat("用法: Rscript 02_plot_assembly_metrics.R <输出目录> [key:path ...] | --demo\n")
  cat("  key 取值: quast_canu / quast_flye / busco_canu / busco_flye\n")
}

# ---- 解析 QUAST report.tsv：第 1 列是指标名，第 2 列是数值 ----
parse_quast <- function(path, assembler) {
  if (!file.exists(path)) stop("找不到 QUAST 报告: ", path, call. = FALSE)
  raw <- read_tsv(path, col_names = c("metric", "value"), col_types = "cc", skip = 1)
  pick <- function(pattern) {
    hit <- raw$value[str_detect(raw$metric, pattern)][1]
    suppressWarnings(as.numeric(hit))
  }
  tibble(
    assembler = assembler,
    `# contigs`            = pick("^# contigs$|^# contigs \\("),
    `N50 (Mb)`             = pick("^N50$") / 1e6,
    `Largest contig (Mb)`  = pick("^Largest contig$") / 1e6,
    `Total length (Mb)`    = pick("^Total length$") / 1e6
  )
}

# ---- 解析 BUSCO short_summary.txt 里的 C:..%[S:..%,D:..%],F:..%,M:..% 行 ----
parse_busco <- function(path, assembler) {
  if (!file.exists(path)) stop("找不到 BUSCO summary: ", path, call. = FALSE)
  line <- grep("C:.*S:.*D:.*F:.*M:", readLines(path), value = TRUE)[1]
  if (is.na(line)) stop("BUSCO summary 中找不到 C/S/D/F/M 汇总行: ", path, call. = FALSE)
  num <- function(tag) as.numeric(str_match(line, paste0(tag, ":([0-9.]+)%"))[, 2])
  tibble(assembler = assembler,
         category  = factor(BUSCO_LEVELS, levels = BUSCO_LEVELS),
         percent   = c(num("S"), num("D"), num("F"), num("M")))
}

demo_quast <- function() {
  tibble(assembler = c("Canu", "Flye"),
         `# contigs` = c(3, 5), `N50 (Mb)` = c(2.10, 1.70),
         `Largest contig (Mb)` = c(2.30, 1.95), `Total length (Mb)` = c(4.12, 4.05))
}
demo_busco <- function() {
  tibble(assembler = rep(c("Canu", "Flye"), each = 4),
         category  = factor(rep(BUSCO_LEVELS, 2), levels = BUSCO_LEVELS),
         percent   = c(97.2, 0.8, 0.6, 1.4, 95.1, 2.3, 1.0, 1.6))
}

plot_quast <- function(df) {
  long <- pivot_longer(df, cols = -assembler, names_to = "metric", values_to = "value")
  long$metric <- factor(long$metric, levels = METRIC_LEVELS)       # 固定指标出场顺序
  ggplot(long, aes(x = assembler, y = value, fill = assembler)) +
    geom_col(width = 0.6) +
    geom_text(aes(label = round(value, 2)), vjust = -0.4, size = 3.2) +
    # free_y：contig 数与 N50 量纲差 6 个数量级，共用一根 y 轴会让矮柱子完全看不见
    facet_wrap(~ metric, scales = "free_y", nrow = 1) +
    scale_fill_manual(values = PALETTE_ASM) +
    scale_y_continuous(expand = expansion(mult = c(0, 0.15))) +    # 顶部留白给数值标签
    labs(x = NULL, y = "Value", title = "QUAST metrics: Canu vs Flye",
         subtitle = "Higher N50 and fewer contigs = better contiguity; check BUSCO before deciding") +
    theme_bw(base_size = 12) + theme(legend.position = "none")
}

plot_busco <- function(df) {
  ggplot(df, aes(x = assembler, y = percent, fill = category)) +
    geom_col(width = 0.6) +
    scale_fill_manual(values = PALETTE_BUSCO) +
    labs(x = NULL, y = "BUSCO (%)", fill = "Category",
         title = "BUSCO completeness (bacteria_odb10)",
         subtitle = "C = Single-copy + Duplicated; high Duplicated suggests assembly redundancy") +
    theme_bw(base_size = 12)
}

main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  if (length(args) < 1) { usage(); quit(status = 1) }
  out_dir <- args[1]; specs <- args[-1]
  dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

  if (length(specs) == 0 || identical(specs[1], "--demo")) {
    message("[demo] 使用内置示例数据（数值取自讲义示例，仅用于跑通流程）")
    quast_df <- demo_quast(); busco_df <- demo_busco()
  } else {
    kv <- do.call(rbind, lapply(specs, function(s) {
      p <- strsplit(s, ":", fixed = TRUE)[[1]]
      if (length(p) != 2) stop("参数格式应为 key:path，收到: ", s, call. = FALSE)
      data.frame(key = p[1], path = p[2], stringsAsFactors = FALSE)
    }))
    get_path <- function(k) kv$path[kv$key == k][1]
    quast_df <- bind_rows(
      if (!is.na(get_path("quast_canu"))) parse_quast(get_path("quast_canu"), "Canu"),
      if (!is.na(get_path("quast_flye"))) parse_quast(get_path("quast_flye"), "Flye"))
    busco_df <- bind_rows(
      if (!is.na(get_path("busco_canu"))) parse_busco(get_path("busco_canu"), "Canu"),
      if (!is.na(get_path("busco_flye"))) parse_busco(get_path("busco_flye"), "Flye"))
  }

  if (nrow(quast_df) > 0) {
    f <- file.path(out_dir, "quast_compare.pdf")
    ggsave(f, plot = plot_quast(quast_df), width = 9, height = 3.6, units = "in")
    cat("Saved:", f, "\n"); print(as.data.frame(quast_df))
  }
  if (nrow(busco_df) > 0) {
    f <- file.path(out_dir, "busco_stacked.pdf")
    ggsave(f, plot = plot_busco(busco_df), width = 5.5, height = 4, units = "in")
    cat("Saved:", f, "\n"); print(as.data.frame(busco_df))
  }
  cat("提示：报告里写选择理由时必须引用具体数值，并同时讨论连续性(N50)与完整性(BUSCO)——\n")
  cat("      N50 高不等于组装对，错误连接同样会抬高 N50。\n")
}

main()
