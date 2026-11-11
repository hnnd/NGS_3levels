#!/usr/bin/env Rscript
# ============================================================
# p06 多组学整合 —— MOFA2 跨组学共享潜因子
# 环境：conda activate ngs_phd_multiomics
#
# 讲义对应：④ 4.8（潜因子、方差分解、与 WGCNA 的分工、局限）、⑥（因子读法）、⑨-E5
#
# 输入要求（讲义 §4.8）：各 view 近似高斯 —— 转录组给 vst，代谢组给 CLR 后的矩阵。
# 不要把原始 counts 或原始峰强度丢进来，高斯似然会被极端值主导。
#
# 所有图的 title / axis / legend 一律英文。
# ============================================================
suppressPackageStartupMessages({
  library(MOFA2); library(readr); library(dplyr); library(ggplot2)
})
set.seed(20260829)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 4) {
  stop("用法: 06_mofa2_integration.R <vst_matrix.tsv> <metab_clr.tsv> <sample_meta.tsv> <outdir> [选项]\n",
       "  vst_matrix.tsv  : 转录组 vst 矩阵（行=基因, 列=样本）\n",
       "  metab_clr.tsv   : 代谢组 CLR 矩阵（行=feature, 列=样本），来自 06_metabolome_preprocess.R\n",
       "  sample_meta.tsv : 列 sample, group, batch[, run_order]\n",
       "选项:\n",
       "  --num-factors 10  因子数**上限**；MOFA 会自动丢弃解释方差过低的因子\n",
       "  --seed 20260829   变分推断有随机性，不固定种子结果不可复现")
}
rna_f <- args[1]; met_f <- args[2]; meta_f <- args[3]; outdir <- args[4]
opt <- function(flag, default) {
  i <- match(flag, args); if (is.na(i) || i == length(args)) default else as.numeric(args[i + 1])
}
num_factors <- opt("--num-factors", 10)
seed_val    <- opt("--seed", 20260829)
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

read_mat <- function(path) {
  d <- read_tsv(path, show_col_types = FALSE) |> as.data.frame()
  rownames(d) <- d[[1]]
  as.matrix(d[, -1, drop = FALSE])
}
rna <- read_mat(rna_f); met <- read_mat(met_f)
meta <- read_tsv(meta_f, show_col_types = FALSE) |> as.data.frame()
if ("is_qc" %in% colnames(meta)) meta <- meta[!meta$is_qc, , drop = FALSE]  # QC 不进模型

common <- Reduce(intersect, list(colnames(rna), colnames(met), meta$sample))
if (length(common) < 6) stop("三份输入的共同样本少于 6 个，检查样本命名是否一致（配对性是硬要求，讲义 §4.6）")
rna <- rna[, common, drop = FALSE]; met <- met[, common, drop = FALSE]
meta <- meta[match(common, meta$sample), , drop = FALSE]
message(sprintf("配对样本 %d 个；transcriptome %d 特征，metabolome %d 特征",
                length(common), nrow(rna), nrow(met)))

# 输入形态自检（讲义 §4.8）
if (all(abs(rna - round(rna)) < 1e-8) && max(rna) > 100) {
  stop("转录组 view 看起来是原始 counts。MOFA2 的高斯似然要 vst/rlog 矩阵，见讲义 §4.8。")
}
# 去掉零方差特征，否则 create_mofa 会报错
rna <- rna[matrixStats::rowSds(rna) > 0, , drop = FALSE]
met <- met[matrixStats::rowSds(met) > 0, , drop = FALSE]

mofa <- create_mofa(list(transcriptome = rna, metabolome = met))
data_opts  <- get_default_data_options(mofa)
data_opts$scale_views <- TRUE      # view 间特征数/尺度差异大时按 view 缩放（讲义 §4.8）
model_opts <- get_default_model_options(mofa)
model_opts$num_factors <- num_factors
train_opts <- get_default_training_options(mofa)
train_opts$seed <- seed_val
train_opts$convergence_mode <- "slow"   # 教学/发表用 slow；快速探索可用 fast

mofa <- prepare_mofa(mofa, data_options = data_opts,
                     model_options = model_opts, training_options = train_opts)
# 若这一步报 ModuleNotFoundError: No module named 'mofapy2'，见讲义 ⑨-E5：
#   在同一 conda 环境里装 mofapy2，并 reticulate::use_condaenv("ngs_phd_multiomics", required = TRUE)
model <- run_mofa(mofa, outfile = file.path(outdir, "mofa_model.hdf5"), use_basilisk = FALSE)

samples_metadata(model) <- meta |> rename(sample = sample)

# ---- 1. 方差分解：本脚本最有用的输出（讲义 §4.8 与 ⑥）----
var_exp <- get_variance_explained(model)$r2_per_factor[[1]]
write_tsv(as_tibble(var_exp, rownames = "factor"), file.path(outdir, "variance_explained.tsv"))
plot_variance_explained(model, x = "view", y = "factor") +
  labs(title = "Variance explained per factor and view",
       x = "View", y = "Factor", fill = "R2 (%)")
ggsave(file.path(outdir, "variance_explained.png"), width = 5.5, height = 5, dpi = 150)

# 判读提示（讲义 ⑥）：
#  - 两个 view 都有可观方差 -> 跨组学共变结构，这是你要找的
#  - 只在一个 view 上很大   -> 该组学特有变异（可能是技术性的）
#  - Factor1 很大但样本按 batch 排开 -> 这是批次因子，不是生物学
for (f in seq_len(min(3, nrow(var_exp)))) {
  df <- data.frame(factor_value = get_factors(model)[[1]][, f],
                   group = meta$group,
                   batch = if ("batch" %in% colnames(meta)) as.factor(meta$batch) else "NA")
  ggplot(df, aes(group, factor_value, colour = batch)) +
    geom_jitter(width = 0.15, size = 2.5) +
    labs(title = sprintf("Factor %d: group vs batch", f),
         x = "Group", y = sprintf("Factor %d value", f), colour = "Batch") +
    theme_bw()
  ggsave(file.path(outdir, sprintf("factor%d_group_batch.png", f)),
         width = 6, height = 4, dpi = 150)
}

# ---- 2. 各因子的 top loading 特征 ----
loadings <- lapply(views_names(model), function(v) {
  w <- get_weights(model, views = v)[[1]]
  do.call(rbind, lapply(seq_len(ncol(w)), function(f) {
    o <- order(abs(w[, f]), decreasing = TRUE)[1:min(20, nrow(w))]
    data.frame(view = v, factor = colnames(w)[f], feature = rownames(w)[o], weight = w[o, f])
  }))
}) |> bind_rows()
write_tsv(as_tibble(loadings), file.path(outdir, "top_loadings.tsv"))

message("完成。模型：", file.path(outdir, "mofa_model.hdf5"))
message("提醒（讲义 §4.8）：因子无方向、无因果；loading 大小不是 p 值。")
message("  因子与表型的关联要另做检验并做多重检验校正（讲义 ⑦）。")
