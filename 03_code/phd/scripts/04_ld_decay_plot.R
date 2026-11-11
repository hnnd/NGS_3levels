#!/usr/bin/env Rscript
# ============================================================
# 脚本名称：04_ld_decay_plot.R
# 功能描述：p04 —— 把 PLINK --r2 的输出按物理距离分箱，拟合 LD 衰减曲线，
#           报告半衰距离与 r² 降到 0.2 的距离（后者定 GWAS 的标记密度下限）
# 作者：王运生
# 日期：2026-08-29
# 用法：Rscript 04_ld_decay_plot.R <plink.ld> <max_kb> <bin_bp> <out_prefix> [n_ind]
# 配套讲义：02_lectures/phd/topic04_popgen/04_popgen_lecture.md §4.4、§5.5、⑦ 7.3
# ============================================================
#
# 三条必须随曲线一起报告的量（讲义 ⑦ 7.3）：样本量、分箱宽度与最大距离、MAF 阈值。
# 换任何一条，"半衰距离"的读数就会变——本脚本因此把它们全部写进输出文件与图注。
# 注意：无真实 LD 时 E[r^2] ≈ 1/n，小样本会把整条曲线整体抬高。脚本据此给出
# 基线 1/n 并同时报告"扣除基线后"的半衰距离，供跨群体比较时参考。
# 图中一律使用英文标签（项目图表规则）。

suppressPackageStartupMessages({
  library(ggplot2)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 4L) {
  stop("用法：Rscript 04_ld_decay_plot.R <plink.ld> <max_kb> <bin_bp> <out_prefix> [n_ind]")
}
ld_file    <- args[1]
max_kb     <- as.numeric(args[2])
bin_bp     <- as.numeric(args[3])
out_prefix <- args[4]
n_ind      <- if (length(args) >= 5L) as.numeric(args[5]) else NA_real_

message("[INFO] 读取 ", ld_file, "（大文件可能需要几分钟）")
ld <- read.table(ld_file, header = TRUE, stringsAsFactors = FALSE)
stopifnot(all(c("BP_A", "BP_B", "R2") %in% names(ld)))

ld$dist <- abs(ld$BP_B - ld$BP_A)
ld <- ld[ld$dist > 0 & ld$dist <= max_kb * 1000, ]
if (nrow(ld) == 0L) {
  stop("没有落在 0–", max_kb, " kb 区间内的位点对。检查是否忘了 --ld-window-kb / --ld-window-r2 0")
}

# ---- 分箱 ----
ld$bin <- floor(ld$dist / bin_bp) * bin_bp + bin_bp / 2
agg <- aggregate(R2 ~ bin, data = ld, FUN = mean)
cnt <- aggregate(R2 ~ bin, data = ld, FUN = length)
names(cnt)[2] <- "n_pairs"
agg <- merge(agg, cnt, by = "bin")
agg <- agg[order(agg$bin), ]
# 每箱位点对太少的箱不参与拟合，否则曲线会出现"中距离反弹"的假象（讲义 6.1）
agg_fit <- agg[agg$n_pairs >= 50L, ]

# ---- Hill–Weir 期望式拟合：E[r2] ≈ 1 / (1 + rho * d)，rho = 4 * Ne * c ----
fit <- try(nls(R2 ~ 1 / (1 + rho * bin), data = agg_fit,
               start = list(rho = 1e-4), control = nls.control(warnOnly = TRUE)),
           silent = TRUE)
if (inherits(fit, "try-error")) {
  message("[WARN] Hill–Weir 拟合不收敛，退回指数经验式 R2 = a * exp(-b * d) + c")
  fit <- nls(R2 ~ a * exp(-b * bin) + cc, data = agg_fit,
             start = list(a = max(agg_fit$R2), b = 1e-5, cc = min(agg_fit$R2)),
             control = nls.control(warnOnly = TRUE))
  model_name <- "exponential"
} else {
  model_name <- "Hill-Weir"
}
agg$fitted <- predict(fit, newdata = agg)

# ---- 读数：半衰距离与 r2 = 0.2 的距离 ----
r2_max   <- max(agg$fitted, na.rm = TRUE)
baseline <- if (!is.na(n_ind) && n_ind > 0) 1 / n_ind else 0
first_below <- function(target) {
  idx <- which(agg$fitted <= target)
  if (length(idx) == 0L) NA_real_ else agg$bin[idx[1]]
}
half_dist      <- first_below(r2_max / 2)
half_dist_adj  <- first_below(baseline + (r2_max - baseline) / 2)
dist_r2_0.2    <- first_below(0.2)

out_txt <- paste0(out_prefix, ".txt")
writeLines(c(
  "# LD decay summary —— 以下每一项在论文方法学里都必须出现（讲义 ⑦ 7.3）",
  sprintf("input_file\t%s", ld_file),
  sprintf("n_individuals\t%s", ifelse(is.na(n_ind), "NA（未提供，务必补上）", n_ind)),
  sprintf("baseline_1_over_n\t%.5f", baseline),
  sprintf("max_distance_kb\t%g", max_kb),
  sprintf("bin_width_bp\t%g", bin_bp),
  sprintf("n_pairs_used\t%d", nrow(ld)),
  sprintf("fit_model\t%s", model_name),
  sprintf("r2_max_fitted\t%.4f", r2_max),
  sprintf("half_decay_bp\t%s\t# r2 降到最大值一半", ifelse(is.na(half_dist), "NA", half_dist)),
  sprintf("half_decay_baseline_adjusted_bp\t%s\t# 扣除 1/n 基线后的半衰，跨群体比较用",
          ifelse(is.na(half_dist_adj), "NA", half_dist_adj)),
  sprintf("dist_at_r2_0.2_bp\t%s\t# 标记间距下限：GWAS 标记密度按它定（讲义 §4.4）",
          ifelse(is.na(dist_r2_0.2), "NA", dist_r2_0.2)),
  "# 提醒：MAF 过滤阈值本脚本读不到，请手工记录在方法学里。"
), out_txt)
message("[INFO] 写出 ", out_txt)

# ---- 出图（英文标签）----
subtitle <- sprintf("n = %s | bin = %g bp | max = %g kb | model = %s",
                    ifelse(is.na(n_ind), "NA", n_ind), bin_bp, max_kb, model_name)
p <- ggplot(agg, aes(x = bin / 1000)) +
  geom_point(aes(y = R2), size = 0.6, colour = "grey45", alpha = 0.7) +
  geom_line(aes(y = fitted), linewidth = 0.9, colour = "#2166AC") +
  geom_hline(yintercept = baseline, linetype = "dotted", colour = "grey30") +
  labs(x = "Physical distance (kb)", y = expression(Mean~r^2),
       title = "LD decay", subtitle = subtitle,
       caption = sprintf("half-decay = %s bp; r2 = 0.2 at %s bp",
                         ifelse(is.na(half_dist), "NA", half_dist),
                         ifelse(is.na(dist_r2_0.2), "NA", dist_r2_0.2))) +
  theme_bw(base_size = 11)
ggsave(paste0(out_prefix, ".png"), p, width = 6, height = 4.2, dpi = 300)
write.table(agg, paste0(out_prefix, "_binned.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
message("[INFO] 完成：", out_prefix, ".png / _binned.tsv")
