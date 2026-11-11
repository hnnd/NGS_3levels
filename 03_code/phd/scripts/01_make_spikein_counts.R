#!/usr/bin/env Rscript
# ============================================================
# 脚本名称：01_make_spikein_counts.R
# 功能描述：p01 实践 —— 生成一份"已知正确答案"的 counts 数据。
#           三步验证法的第 ② 步（回归测试）必须有已知答案才能执行；
#           在契约 main_dataset.phd 落定之前，用本脚本现场生成。
# 环境    ：conda activate ngs_phd_base
# 作者    ：王运生
# 日期    ：2026-08-29
#
# 产出（<outdir> 下）：
#   counts.tsv   2000 基因 x 6 样本，原始整数 counts，文库大小刻意不等
#   coldata.tsv  sample / condition / batch 三列（batch 与 condition 交叉，非混杂）
#   spikein.txt  20 个真实 log2FC = 3（即 8 倍上调）的基因名 —— 这就是"已知答案"
#
# set.seed 固定，全班拿到同一份数据，便于横向对答案。
# ============================================================
suppressPackageStartupMessages(library(stats))
set.seed(20260829)

args <- commandArgs(trailingOnly = TRUE)
outdir <- if (length(args) >= 1) args[1] else "results/p01"
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

n_gene    <- 2000
n_each    <- 3                     # 每组生物学重复数
n_spike   <- 20                    # 人为上调的基因数
true_lfc  <- 3                     # log2 倍数 = 3，即 8 倍
disp      <- 0.15                  # 负二项离散度（真实 RNA-seq 的常见量级）

genes   <- sprintf("gene%04d", seq_len(n_gene))
samples <- c(paste0("C", 1:n_each), paste0("T", 1:n_each))
# 文库大小刻意不等：这样"归一化有没有做"才看得出来（size factor 不应全为 1）
lib_factor <- c(1.00, 0.62, 1.45, 0.81, 1.30, 0.95)

# 基线表达：对数正态，覆盖低表达到高表达
base_mu <- 2^rnorm(n_gene, mean = 5.5, sd = 2.2)
spike   <- sample(which(base_mu > 30), n_spike)     # 只在中高表达基因里做 spike-in

mu <- matrix(rep(base_mu, times = length(samples)), nrow = n_gene)
colnames(mu) <- samples; rownames(mu) <- genes
mu[spike, 4:6] <- mu[spike, 4:6] * 2^true_lfc       # 处理组 T1-T3 上调 8 倍
for (j in seq_along(samples)) mu[, j] <- mu[, j] * lib_factor[j]

cts <- matrix(rnbinom(n_gene * length(samples), mu = as.vector(mu), size = 1 / disp),
              nrow = n_gene, dimnames = list(genes, samples))

coldata <- data.frame(
  sample    = samples,
  condition = rep(c("ctrl", "treat"), each = n_each),
  batch     = rep(c("b1", "b2", "b1"), times = 2),   # 与 condition 交叉，不混杂
  stringsAsFactors = FALSE
)

write.table(data.frame(gene_id = rownames(cts), cts, check.names = FALSE),
            file.path(outdir, "counts.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
write.table(coldata, file.path(outdir, "coldata.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)
writeLines(genes[spike], file.path(outdir, "spikein.txt"))

cat(sprintf("[p01-01] %d genes x %d samples -> %s\n", n_gene, length(samples), outdir))
cat(sprintf("[p01-01] spike-in %d genes, true log2FC = %.1f (treat vs ctrl)\n", n_spike, true_lfc))
cat(sprintf("[p01-01] library sizes: %s\n", paste(colSums(cts), collapse = ", ")))
