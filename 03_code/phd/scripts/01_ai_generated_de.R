#!/usr/bin/env Rscript
# ============================================================
# 脚本名称：01_ai_generated_de.R
# 功能描述：p01 实践材料 —— 一段"AI 生成"的差异表达分析脚本。
#           它能跑通、不报错、出图，形态完全正常。
#           【教师已在其中植入若干处生物学错误，位置不公布。】
#           学生任务：用讲义 §4.3 的三步验证法把它们找出来。
# 环境    ：conda activate ngs_phd_base
# 作者    ：王运生（改写自 AI 输出）
# 日期    ：2026-08-29
#
# 用法：Rscript 01_ai_generated_de.R <counts.tsv> <coldata.tsv> <outdir>
#
# 提示（也是本讲的方法论）：不要靠通读代码找错——生信代码的错误通常不在语法里，
# 而在"矩阵单位、比较方向、筛选列、设计公式"这四个代码之外的地方。
# 先跑 01_verify_de.R 看指纹，再回头定位。
# ============================================================
suppressPackageStartupMessages({
  library(DESeq2); library(ggplot2)
})
set.seed(20260829)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 3) {
  stop("用法: 01_ai_generated_de.R <counts.tsv> <coldata.tsv> <outdir>")
}
counts_f <- args[1]; col_f <- args[2]; outdir <- args[3]
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

cts <- read.delim(counts_f, row.names = 1, check.names = FALSE)
cts <- as.matrix(cts)
coldata <- read.delim(col_f, stringsAsFactors = FALSE)
rownames(coldata) <- coldata$sample
coldata <- coldata[colnames(cts), , drop = FALSE]
coldata$condition <- factor(coldata$condition)

# --- 归一化：先把原始 counts 转成 CPM，消除文库大小差异 ---
cpm <- t(t(cts) / colSums(cts)) * 1e6
mat <- round(cpm)

# --- 构建 DESeq2 对象并检验 ---
dds <- DESeqDataSetFromMatrix(countData = mat,
                              colData   = coldata,
                              design    = ~ condition)
dds <- dds[rowSums(counts(dds)) >= 10, ]
dds <- DESeq(dds, quiet = TRUE)

res <- results(dds, contrast = c("condition", "ctrl", "treat"))
res <- as.data.frame(res)
res$gene <- rownames(res)

# --- 筛选差异基因 ---
sig <- subset(res, !is.na(pvalue) & pvalue < 0.05 & abs(log2FoldChange) > 1)
sig <- sig[order(sig$pvalue), ]

write.table(res, file.path(outdir, "de_results_all.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)
write.table(sig, file.path(outdir, "de_results_sig.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)
saveRDS(dds, file.path(outdir, "dds.rds"))

# --- 火山图（图内文字一律英文：Linux 中文字体常显示为方块）---
res$flag <- ifelse(!is.na(res$pvalue) & res$pvalue < 0.05 & abs(res$log2FoldChange) > 1,
                   "significant", "ns")
p <- ggplot(res, aes(x = log2FoldChange, y = -log10(pvalue), color = flag)) +
  geom_point(alpha = 0.6, size = 0.8) +
  scale_color_manual(values = c(ns = "grey70", significant = "#D55E00")) +
  labs(x = "log2 fold change", y = "-log10(p-value)", color = NULL,
       title = "Differential expression") +
  theme_bw(base_size = 12)
ggsave(file.path(outdir, "volcano.png"), plot = p, width = 6, height = 4.5, dpi = 200)

png(file.path(outdir, "dispersion.png"), width = 900, height = 700, res = 150)
plotDispEsts(dds)
dev.off()

cat(sprintf("[p01-02] 检验基因数 : %d\n", nrow(res)))
cat(sprintf("[p01-02] 差异基因数 : %d\n", nrow(sig)))
cat(sprintf("[p01-02] size factors: %s\n",
            paste(round(sizeFactors(dds), 3), collapse = ", ")))
cat(sprintf("[p01-02] resultsNames: %s\n", paste(resultsNames(dds), collapse = ", ")))
cat("[p01-02] done ->", outdir, "\n")
