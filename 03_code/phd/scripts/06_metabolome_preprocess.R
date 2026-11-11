#!/usr/bin/env Rscript
# ============================================================
# p06 多组学整合 —— 内嵌模块「非测序组学数据入门」配套脚本
# 代谢组/蛋白组峰表预处理：QC-RSD 过滤 → 缺失机制诊断 → 按机制填补 → CLR
# 环境：conda activate ngs_phd_multiomics
#
# 讲义对应：④ 4.1–4.4（峰表结构、QC 与漂移、MNAR vs MAR、组成性数据）
# 关键顺序（讲义 §4.4）：过滤 → 判断机制 → 填补 → CLR。CLR 对 0/NA 无定义，
# 顺序颠倒会得到 -Inf/NaN（讲义 ⑨-E7）。
#
# 所有图的 title / axis / legend 一律英文（Linux 中文字体常显示为方块）。
# ============================================================
suppressPackageStartupMessages({
  library(readr); library(dplyr); library(tidyr); library(ggplot2)
})
set.seed(20260829)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  stop("用法: 06_metabolome_preprocess.R <peaks.tsv> <sample_meta.tsv> <outdir> [选项]\n",
       "  peaks.tsv       : 行=feature(第一列 feature_id), 列=样本, 值=峰强度(缺失写 NA)\n",
       "  sample_meta.tsv : 列 sample, group, run_order, batch, is_qc(TRUE/FALSE)\n",
       "选项:\n",
       "  --qc-rsd 20        QC 样本上 RSD(%) 阈值，超过则剔除该特征 (LC-MS 20 / GC-MS 30)\n",
       "  --max-missing 0.5  整体缺失率超过此值的特征直接删除，不填补\n",
       "  --mnar-quantile 0.2 判为 MNAR 的特征用「观测值该分位数 / 5」左截断填补")
}
peaks_f <- args[1]; meta_f <- args[2]; outdir <- args[3]
opt <- function(flag, default) {
  i <- match(flag, args); if (is.na(i) || i == length(args)) default else as.numeric(args[i + 1])
}
qc_rsd_max   <- opt("--qc-rsd", 20)
max_missing  <- opt("--max-missing", 0.5)
mnar_q       <- opt("--mnar-quantile", 0.2)
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

peaks <- read_tsv(peaks_f, show_col_types = FALSE) |> as.data.frame()
rownames(peaks) <- peaks[[1]]
mat <- as.matrix(peaks[, -1, drop = FALSE])
meta <- read_tsv(meta_f, show_col_types = FALSE) |> as.data.frame()
stopifnot(all(c("sample", "group") %in% colnames(meta)))
if (!"is_qc" %in% colnames(meta)) meta$is_qc <- FALSE
common <- intersect(colnames(mat), meta$sample)
if (length(common) < 3) stop("峰表列名与 sample_meta 的 sample 对不上，先核对两边命名")
mat <- mat[, common, drop = FALSE]
meta <- meta[match(common, meta$sample), , drop = FALSE]
qc_idx <- which(meta$is_qc)
bio_idx <- which(!meta$is_qc)
message(sprintf("特征 %d 个；样本 %d 个（其中 QC %d 个）", nrow(mat), ncol(mat), length(qc_idx)))

# ---- 1. QC 样本：漂移诊断 + RSD 过滤（讲义 §4.2）----
if (length(qc_idx) < 3) {
  warning("QC 样本少于 3 个：无法评估仪器漂移。\n",
          "  注意『无法评估』不等于『不存在』——报告中必须写明这一限制（讲义 §4.2）。")
} else {
  rsd <- apply(mat[, qc_idx, drop = FALSE], 1,
               function(x) 100 * sd(x, na.rm = TRUE) / mean(x, na.rm = TRUE))
  keep_rsd <- is.finite(rsd) & rsd <= qc_rsd_max
  message(sprintf("QC-RSD <= %.0f%%：保留 %d / %d 个特征", qc_rsd_max, sum(keep_rsd), nrow(mat)))
  write_tsv(tibble(feature_id = rownames(mat), qc_rsd = rsd, kept = keep_rsd),
            file.path(outdir, "qc_rsd.tsv"))
  mat <- mat[keep_rsd, , drop = FALSE]

  # 漂移图：QC 的总强度 ~ 进样顺序。正常应无趋势
  if ("run_order" %in% colnames(meta)) {
    drift <- tibble(run_order = meta$run_order,
                    total_intensity = colSums(mat, na.rm = TRUE),
                    sample_type = ifelse(meta$is_qc, "QC", "Sample"))
    ggplot(drift, aes(run_order, total_intensity, colour = sample_type)) +
      geom_point(size = 2) +
      geom_smooth(data = subset(drift, sample_type == "QC"),
                  method = "loess", formula = y ~ x, se = FALSE, colour = "black") +
      labs(title = "Signal drift across injection order",
           x = "Injection order", y = "Total intensity", colour = "Sample type") +
      theme_bw()
    ggsave(file.path(outdir, "qc_drift.png"), width = 7, height = 4.5, dpi = 150)
  }
}

# ---- 2. 高缺失特征直接删除，不填补（讲义 §4.3 规矩①）----
miss_rate <- rowMeans(is.na(mat[, bio_idx, drop = FALSE]))
mat <- mat[miss_rate <= max_missing, , drop = FALSE]
miss_rate <- miss_rate[miss_rate <= max_missing]
message(sprintf("缺失率 <= %.0f%%：保留 %d 个特征", 100 * max_missing, nrow(mat)))

# ---- 3. 缺失机制诊断：缺失率 ~ 检出强度（讲义 §4.3）----
mean_obs <- apply(log2(mat[, bio_idx, drop = FALSE] + 1), 1, mean, na.rm = TRUE)
diag_df <- tibble(feature_id = rownames(mat), missing_rate = miss_rate, mean_log2_intensity = mean_obs)
rho <- suppressWarnings(cor(diag_df$missing_rate, diag_df$mean_log2_intensity,
                            method = "spearman", use = "complete.obs"))
message(sprintf("缺失率 vs 检出强度 Spearman rho = %.3f（明显为负即 MNAR 主导）", rho))
ggplot(diag_df, aes(mean_log2_intensity, missing_rate)) +
  geom_point(alpha = 0.4) + geom_smooth(method = "loess", formula = y ~ x, se = FALSE) +
  labs(title = sprintf("Missingness vs detected intensity (Spearman rho = %.2f)", rho),
       x = "Mean log2 intensity in detected samples", y = "Missing rate") +
  theme_bw()
ggsave(file.path(outdir, "missingness_vs_intensity.png"), width = 6.5, height = 4.5, dpi = 150)

# 逐特征判机制：缺失且强度低于总体中位数 -> MNAR；否则按 MAR 处理
is_mnar <- diag_df$mean_log2_intensity < median(diag_df$mean_log2_intensity, na.rm = TRUE) &
           diag_df$missing_rate > 0
diag_df$mechanism <- ifelse(is_mnar, "MNAR", "MAR/MCAR")
write_tsv(diag_df, file.path(outdir, "missingness_diagnosis.tsv"))
message(sprintf("判为 MNAR 的特征：%d 个；MAR/MCAR：%d 个", sum(is_mnar), sum(!is_mnar)))

# ---- 4. 按机制分别填补（讲义 §4.3 规矩②）----
impute_mnar <- function(x) {                    # 左截断：观测值低分位数 / 5
  if (all(is.na(x))) return(x)
  x[is.na(x)] <- quantile(x, mnar_q, na.rm = TRUE) / 5
  x
}
impute_mar <- function(x) {                     # 行中位数（kNN 的轻量替身；如需 kNN 见下方注释）
  if (all(is.na(x))) return(x)
  x[is.na(x)] <- median(x, na.rm = TRUE)
  x
}
# 若要用 kNN/missForest，装 impute 或 missForest 后替换 impute_mar：
#   imputed <- impute::impute.knn(mat_mar)$data
filled <- mat
filled[is_mnar, ]  <- t(apply(mat[is_mnar, , drop = FALSE], 1, impute_mnar))
filled[!is_mnar, ] <- t(apply(mat[!is_mnar, , drop = FALSE], 1, impute_mar))

# 敏感性分析用：全部按均值填补的版本（讲义 ⑧ 错误类别②的反例）
naive <- t(apply(mat, 1, impute_mar))
write_tsv(as_tibble(naive, rownames = "feature_id"),
          file.path(outdir, "metab_imputed_naive.tsv"))

# ---- 5. CLR 变换（讲义 §4.4）；必须在填补之后 ----
clr <- function(x) {
  stopifnot(all(x > 0))                          # 0/NA 在这里就该已经没有了
  log(x) - mean(log(x))
}
if (any(filled <= 0, na.rm = TRUE)) {
  pseudo <- min(filled[filled > 0], na.rm = TRUE) / 2
  message(sprintf("仍有非正值，加伪计数 %.4g（必须写进 Methods）", pseudo))
  filled[filled <= 0 | is.na(filled)] <- pseudo
}
clr_mat <- apply(filled, 2, clr)                 # 按样本（列）做 CLR
rownames(clr_mat) <- rownames(filled)
write_tsv(as_tibble(clr_mat, rownames = "feature_id"), file.path(outdir, "metab_clr.tsv"))

# ---- 6. QC 诊断 PCA：QC 应聚成中心一团（讲义 ⑥）----
pca <- prcomp(t(clr_mat), scale. = TRUE)
var_pct <- 100 * pca$sdev^2 / sum(pca$sdev^2)
pca_df <- tibble(PC1 = pca$x[, 1], PC2 = pca$x[, 2],
                 sample_type = ifelse(meta$is_qc, "QC", "Sample"), group = meta$group)
ggplot(pca_df, aes(PC1, PC2, colour = group, shape = sample_type)) +
  geom_point(size = 3) +
  labs(title = "PCA of CLR-transformed peak table",
       x = sprintf("PC1 (%.1f%%)", var_pct[1]), y = sprintf("PC2 (%.1f%%)", var_pct[2]),
       colour = "Group", shape = "Sample type") +
  theme_bw()
ggsave(file.path(outdir, "qc_drift_pca.png"), width = 6.5, height = 5, dpi = 150)

message("完成。下游输入：", file.path(outdir, "metab_clr.tsv"))
message("敏感性分析：把 metab_imputed_naive.tsv 走同一条下游流程，比较结论差多少（讲义 §4.3 规矩③）")
