#!/usr/bin/env Rscript
# ============================================================
# p06 多组学整合 —— WGCNA 加权共表达网络
# 环境：conda activate ngs_phd_multiomics
#
# 讲义对应：④ 4.7（软阈值/TOM/模块/ME-性状/hub 与三个批判点）、
#           ⑦ 统计插件（模块-性状 p 值同样要 BH 校正）、⑨-E2/E3/E4/E6/E8
#
# 【硬约束】输入必须是 vst() 或 rlog() 的方差稳定化矩阵，不是 counts、不是 TPM。
# 见硕士 m04 §4.4 与本讲 ⑨-E2：喂错矩阵软阈值曲线不收敛，硬调 β 得到的是噪声模块。
# 本脚本在 SFT.R.sq 达不到阈值时**直接停下报错**，不允许硬跑。
#
# 所有图的 title / axis / legend 一律英文。
# ============================================================
suppressPackageStartupMessages({
  library(WGCNA); library(readr); library(dplyr)
})
options(stringsAsFactors = FALSE)
enableWGCNAThreads(nThreads = 4)
set.seed(20260829)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  stop("用法: 06_wgcna_analysis.R <vst_matrix.tsv> <traits.tsv> <outdir> [选项]\n",
       "  vst_matrix.tsv : 行=基因(第一列 gene_id), 列=样本；**vst/rlog 矩阵**\n",
       "  traits.tsv     : 列 sample + 若干数值型性状\n",
       "选项:\n",
       "  --min-module-size 30    模块最小基因数；调小→碎片化，调大→小模块被并掉\n",
       "  --merge-cut-height 0.25 ME 相关 > 0.75 的模块合并；\"模块数过多\"最直接的旋钮\n",
       "  --deep-split 2          剪切树灵敏度 0-4，越大模块越多越细\n",
       "  --sft-target 0.8        无标度拟合优度目标；达不到即报错停止（讲义 ⑨-E2）")
}
mat_f <- args[1]; traits_f <- args[2]; outdir <- args[3]
opt <- function(flag, default) {
  i <- match(flag, args); if (is.na(i) || i == length(args)) default else as.numeric(args[i + 1])
}
min_module_size  <- opt("--min-module-size", 30)
merge_cut_height <- opt("--merge-cut-height", 0.25)
deep_split       <- opt("--deep-split", 2)
sft_target       <- opt("--sft-target", 0.8)
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

expr <- read_tsv(mat_f, show_col_types = FALSE) |> as.data.frame()
rownames(expr) <- expr[[1]]
mat <- as.matrix(expr[, -1, drop = FALSE])
traits <- read_tsv(traits_f, show_col_types = FALSE) |> as.data.frame()
rownames(traits) <- traits$sample

common <- intersect(colnames(mat), rownames(traits))
mat <- mat[, common, drop = FALSE]
traits <- traits[common, setdiff(colnames(traits), "sample"), drop = FALSE]

# 输入形态自检：vst 矩阵典型范围 0-20 且非整数；counts 是大整数（讲义 ⑨-E2）
if (all(abs(mat - round(mat)) < 1e-8) && max(mat, na.rm = TRUE) > 100) {
  stop("输入看起来是原始 counts（全整数且最大值 > 100）。\n",
       "  WGCNA 必须用 vst()/rlog() 矩阵，见讲义 ⑨-E2 与硕士 m04 §4.4。")
}
if (all(abs(colSums(mat) - 1e6) < 1) ) {
  stop("输入看起来是 TPM（每列和 = 1e6）。组成性数据会毁掉相关结构，见讲义 §4.4 与 ⑨-E2。")
}

datExpr <- t(mat)                                  # WGCNA 要 样本 × 基因（讲义 ⑨-E4）
stopifnot(nrow(datExpr) == nrow(traits))           # 报错提前到能看懂的地方
gsg <- goodSamplesGenes(datExpr, verbose = 0)
if (!gsg$allOK) datExpr <- datExpr[gsg$goodSamples, gsg$goodGenes, drop = FALSE]
n_samples <- nrow(datExpr)
message(sprintf("样本 %d 个，基因 %d 个", n_samples, ncol(datExpr)))
if (n_samples < 15) {
  warning(sprintf("样本数 %d < 15（WGCNA 官方建议下限）。\n", n_samples),
          "  相关系数的标准误极大，模块不可重复。正确做法是改用 MOFA2 或晚期整合；\n",
          "  若坚持要跑，报告中必须写明「探索性结果，未做保守性检验」（讲义 ⑨-E3）。")
}

# ---- 1. 软阈值 β：无标度拓扑拟合（讲义 §4.7 批判点一：这不是显著性检验）----
powers <- c(1:10, seq(12, 30, 2))
sft <- pickSoftThreshold(datExpr, powerVector = powers, networkType = "signed", verbose = 0)
write_tsv(as_tibble(sft$fitIndices), file.path(outdir, "soft_threshold_scan.tsv"))

png(file.path(outdir, "soft_threshold.png"), 1400, 600, res = 130)
par(mfrow = c(1, 2))
plot(sft$fitIndices[, 1], -sign(sft$fitIndices[, 3]) * sft$fitIndices[, 2], type = "n",
     xlab = "Soft threshold (power)", ylab = "Scale-free topology fit, signed R^2",
     main = "Scale independence")
text(sft$fitIndices[, 1], -sign(sft$fitIndices[, 3]) * sft$fitIndices[, 2],
     labels = powers, col = "red")
abline(h = sft_target, col = "blue", lty = 2)
plot(sft$fitIndices[, 1], sft$fitIndices[, 5], type = "n",
     xlab = "Soft threshold (power)", ylab = "Mean connectivity", main = "Mean connectivity")
text(sft$fitIndices[, 1], sft$fitIndices[, 5], labels = powers, col = "red")
dev.off()

fit <- -sign(sft$fitIndices[, 3]) * sft$fitIndices[, 2]
ok <- which(fit >= sft_target)
if (length(ok) == 0) {
  stop(sprintf("没有任何 power 使 SFT.R.sq 达到 %.2f（最大只到 %.3f）。\n", sft_target, max(fit)),
       "  按讲义 ⑨-E2 逐条排查：\n",
       "   ① 输入矩阵是不是 counts/TPM（最常见，占九成）；\n",
       "   ② 样本量是否 < 15；\n",
       "   ③ 批次结构是否过强（先看 PCA，把批次回归掉再试）；\n",
       "   ④ 样本是否混着完全不同的组织/时间点（应分组建网）。\n",
       "  **不要**把 β 硬调到 24/30 交差——那样得到的模块是噪声。")
}
power <- powers[min(ok)]
message(sprintf("选定 soft threshold power = %d（SFT.R.sq = %.3f）", power, fit[min(ok)]))

# ---- 2. 网络与模块（讲义 §4.7 步骤 4-5）----
cor <- WGCNA::cor            # 防止 tidyverse 等包遮蔽 cor（讲义 ⑨-E6）
net <- blockwiseModules(datExpr, power = power, networkType = "signed",
                        TOMType = "signed", minModuleSize = min_module_size,
                        deepSplit = deep_split, mergeCutHeight = merge_cut_height,
                        numericLabels = TRUE, pamRespectsDendro = FALSE,
                        maxBlockSize = 8000, saveTOMs = FALSE, verbose = 0)
cor <- stats::cor            # 还原
module_colors <- labels2colors(net$colors)
tab <- table(module_colors)
grey_frac <- sum(module_colors == "grey") / length(module_colors)
message(sprintf("模块数 %d（不含 grey）；grey 占 %.1f%%", sum(names(tab) != "grey"), 100 * grey_frac))
if (grey_frac > 0.6) {
  warning("grey 模块吞掉超过 60% 的基因：网络可能没有结构。见讲义 ⑨-E8。")
}
write_tsv(tibble(gene_id = colnames(datExpr), module = module_colors),
          file.path(outdir, "gene_modules.tsv"))

png(file.path(outdir, "module_dendrogram.png"), 1400, 700, res = 130)
plotDendroAndColors(net$dendrograms[[1]], module_colors[net$blockGenes[[1]]],
                    "Module colors", dendroLabels = FALSE, hang = 0.03,
                    addGuide = TRUE, guideHang = 0.05,
                    main = "Gene clustering dendrogram and module assignment")
dev.off()

# ---- 3. 模块特征基因 ME 与性状关联（讲义 ⑦(3)：这些 p 值也要 BH 校正）----
MEs <- orderMEs(moduleEigengenes(datExpr, module_colors)$eigengenes)
me_mat <- t(as.matrix(MEs))                        # 行=module, 列=样本
colnames(me_mat) <- rownames(datExpr)
write_tsv(as_tibble(me_mat, rownames = "module"), file.path(outdir, "module_eigengenes.tsv"))

trait_mat <- as.matrix(traits[, sapply(traits, is.numeric), drop = FALSE])
mt_cor <- cor(MEs, trait_mat, use = "pairwise.complete.obs")
mt_p   <- corPvalueStudent(mt_cor, n_samples)
mt_q   <- matrix(p.adjust(as.vector(mt_p), method = "BH"), nrow = nrow(mt_p),
                 dimnames = dimnames(mt_p))       # 全部格子一起校正，见讲义 ⑦(3)
write_tsv(tibble(module = rep(rownames(mt_cor), ncol(mt_cor)),
                 trait  = rep(colnames(mt_cor), each = nrow(mt_cor)),
                 cor = as.vector(mt_cor), p = as.vector(mt_p), q_BH = as.vector(mt_q)),
          file.path(outdir, "module_trait_association.tsv"))
message(sprintf("模块-性状检验 %d 次；q < 0.05 的有 %d 个", length(mt_q), sum(mt_q < 0.05)))

png(file.path(outdir, "module_trait_heatmap.png"), 1000, 900, res = 130)
labeledHeatmap(Matrix = mt_cor, xLabels = colnames(trait_mat), yLabels = rownames(mt_cor),
               ySymbols = rownames(mt_cor), colorLabels = FALSE, colors = blueWhiteRed(50),
               textMatrix = paste0(signif(mt_cor, 2), "\n(q=", signif(mt_q, 2), ")"),
               setStdMargins = FALSE, cex.text = 0.6, zlim = c(-1, 1),
               main = "Module-trait relationships (BH-adjusted q)")
dev.off()

# ---- 4. Hub 基因：kME 高 + 模块内连接度高（讲义 §4.7 批判点二：hub 是候选不是结论）----
kME <- signedKME(datExpr, MEs)
hub <- lapply(setdiff(unique(module_colors), "grey"), function(m) {
  idx <- which(module_colors == m)
  col <- paste0("kME", m)
  if (!col %in% colnames(kME)) return(NULL)
  d <- tibble(gene_id = colnames(datExpr)[idx], module = m, kME = kME[idx, col])
  d |> arrange(desc(kME)) |> slice_head(n = 10)
}) |> bind_rows()
write_tsv(hub, file.path(outdir, "hub_genes_top10_per_module.tsv"))

message("完成。下一步：把 module_eigengenes.tsv 交给 06_correlation_network.R 与代谢组做关联。")
message("提醒：hub 基因与显著模块都只是**候选假说**，需独立数据集 modulePreservation() + 正交实验验证（讲义 ⑦(4)）。")
