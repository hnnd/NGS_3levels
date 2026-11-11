#!/usr/bin/env Rscript
# ============================================================
# m04 转录组分析 —— DESeq2 差异表达 + 富集
# 环境：conda activate ngs_ms_transcriptome
#
# 讲义 ⑦ 统计插件的配套代码：离散度估计、lfcShrink、
# independentFiltering 对 padj 的影响，都在这里能看到实际效果。
#
# 所有图的 title / axis / legend 一律英文（Linux 中文字体常显示为方块）。
# ============================================================
suppressPackageStartupMessages({
  library(DESeq2); library(ggplot2); library(readr); library(dplyr)
})
set.seed(20260829)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  stop("用法: 04_deseq2_analysis.R <counts.tsv> <coldata.tsv> <outdir> [design]\n",
       "  counts.tsv : 行=基因, 列=样本, 第一列为 gene_id\n",
       "  coldata.tsv: 列 sample, condition, [batch]\n",
       "  design     : 默认 ~condition；有批次时用 '~batch + condition'")
}
counts_f <- args[1]; col_f <- args[2]; outdir <- args[3]
design_str <- ifelse(length(args) >= 4, args[4], "~condition")
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

cts <- read_tsv(counts_f, show_col_types = FALSE) |> as.data.frame()
rownames(cts) <- cts[[1]]; cts <- as.matrix(cts[, -1, drop = FALSE])
coldata <- read_tsv(col_f, show_col_types = FALSE) |> as.data.frame()
rownames(coldata) <- coldata$sample

# 这是最高频的报错来源：列名与样本表对不上。
# 不能用 intersect() 取交集——那会把拼错/漏写的样本静默丢掉，样本量悄悄变小（UP-048）。
# 要求两边样本集合完全相同；只允许顺序不同，按 coldata 重排 counts 后再 identical 校验。
only_cts <- setdiff(colnames(cts), rownames(coldata))
only_col <- setdiff(rownames(coldata), colnames(cts))
if (anyDuplicated(colnames(cts)) || anyDuplicated(rownames(coldata))) {
  stop("counts 列名或 coldata 的 sample 有重复")
}
if (length(only_cts) || length(only_col)) {
  stop("counts 与 coldata 样本不一致——\n  仅在 counts: ", paste(only_cts, collapse = ", "),
       "\n  仅在 coldata: ", paste(only_col, collapse = ", "))
}
cts <- cts[, rownames(coldata), drop = FALSE]
stopifnot(identical(colnames(cts), rownames(coldata)))
coldata$condition <- factor(coldata$condition)
message(sprintf("样本 %d 个，基因 %d 个，设计公式 %s", ncol(cts), nrow(cts), design_str))

dds <- DESeqDataSetFromMatrix(round(cts), coldata, as.formula(design_str))
dds <- dds[rowSums(counts(dds)) >= 10, ]          # 预过滤：加速，不影响 padj 逻辑
dds <- DESeq(dds)

# ---- 离散度图：看收缩是否合理（讲义 ⑦ 的核心图）----
png(file.path(outdir, "dispersion_estimates.png"), 1000, 800, res = 130)
plotDispEsts(dds, main = "Dispersion estimates")
dev.off()

res <- results(dds, alpha = 0.05)
message("--- results() 摘要 ---"); print(summary(res))
n_na <- sum(is.na(res$padj))
message(sprintf("padj 为 NA 的基因：%d 个（independentFiltering 与离群值过滤所致）", n_na))

# lfcShrink：低表达基因的 log2FC 方差极大，收缩后排序才可靠
coef_name <- tail(resultsNames(dds), 1)
res_shrunk <- lfcShrink(dds, coef = coef_name, type = "apeglm")

out <- as.data.frame(res_shrunk) |>
  tibble::rownames_to_column("gene_id") |>
  arrange(padj)
write_tsv(out, file.path(outdir, "deseq2_results.tsv"))

# ---- 火山图（全英文）----
vol <- out |> mutate(sig = case_when(
  !is.na(padj) & padj < 0.05 & log2FoldChange >=  1 ~ "Up",
  !is.na(padj) & padj < 0.05 & log2FoldChange <= -1 ~ "Down",
  TRUE ~ "NS"))
p <- ggplot(vol, aes(log2FoldChange, -log10(pmax(padj, 1e-300)), color = sig)) +
  geom_point(alpha = 0.6, size = 1) +
  scale_color_manual(values = c(Up = "#D55E00", Down = "#0072B2", NS = "grey75")) +
  labs(x = "log2 fold change (shrunken)", y = "-log10 adjusted p-value",
       color = "Regulation", title = "Differential expression") +
  theme_bw(base_size = 12)
ggsave(file.path(outdir, "volcano.png"), plot = p, width = 6, height = 5, dpi = 300)

# ---- 供下游使用的变换矩阵 ----
# 重要：WGCNA（博士 p06）必须吃 vst 或 rlog，喂 counts 或 TPM 会让软阈值曲线崩掉
vsd <- vst(dds, blind = FALSE)
write_tsv(as.data.frame(assay(vsd)) |> tibble::rownames_to_column("gene_id"),
          file.path(outdir, "vst_matrix.tsv"))

pca <- plotPCA(vsd, intgroup = intersect(c("condition", "batch"), colnames(coldata)),
               returnData = TRUE)
pv <- round(100 * attr(pca, "percentVar"))
p2 <- ggplot(pca, aes(PC1, PC2, color = condition)) + geom_point(size = 3) +
  labs(x = paste0("PC1 (", pv[1], "%)"), y = paste0("PC2 (", pv[2], "%)"),
       title = "Sample PCA (vst)") + theme_bw(base_size = 12)
ggsave(file.path(outdir, "pca.png"), plot = p2, width = 6, height = 5, dpi = 300)

message(sprintf("完成。结果在 %s/：deseq2_results.tsv, vst_matrix.tsv, 3 张图", outdir))
message("报告要写清：设计公式为何这样选、padj 阈值、NA 的成因——这是评分项。")
