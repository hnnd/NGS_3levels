#!/usr/bin/env Rscript
# ============================================================
# 脚本名称：01_verify_de.R
# 功能描述：p01 实践 —— 三步验证法的自动化实现（讲义 §4.3）。
#           ① 维度与语义自检   ② 已知答案的小样本回归测试   ③ 关键中间量手算复核
#           本脚本只报告"指纹"，不告诉你错在第几行 —— 定位是学生的任务。
# 环境    ：conda activate ngs_phd_base
# 作者    ：王运生
# 日期    ：2026-08-29
#
# 用法：Rscript 01_verify_de.R <data_dir> <ai_out_dir>
#   data_dir   含 counts.tsv / coldata.tsv / spikein.txt（01_make_spikein_counts.R 的产出）
#   ai_out_dir 含 de_results_all.tsv / de_results_sig.tsv / dds.rds（01_ai_generated_de.R 的产出）
# 产出：<ai_out_dir>/verify_report.txt
# ============================================================
suppressPackageStartupMessages(library(DESeq2))
set.seed(20260829)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) stop("用法: 01_verify_de.R <data_dir> <ai_out_dir>")
ddir <- args[1]; adir <- args[2]
report <- file.path(adir, "verify_report.txt")
con <- file(report, open = "wt")
say <- function(...) { line <- sprintf(...); cat(line, "\n"); writeLines(line, con) }

cts     <- as.matrix(read.delim(file.path(ddir, "counts.tsv"), row.names = 1, check.names = FALSE))
coldata <- read.delim(file.path(ddir, "coldata.tsv"), stringsAsFactors = FALSE)
rownames(coldata) <- coldata$sample
spike   <- readLines(file.path(ddir, "spikein.txt"))
res_ai  <- read.delim(file.path(adir, "de_results_all.tsv"), stringsAsFactors = FALSE)
rownames(res_ai) <- res_ai$gene
dds_ai  <- readRDS(file.path(adir, "dds.rds"))

# ---------------- ① 维度与语义自检 ----------------
say("=========== ① 维度与语义自检 ===========")
say("counts 维度           : %d x %d", nrow(cts), ncol(cts))
say("取值域                : [%s, %s]", format(min(cts)), format(max(cts)))
say("全为整数              : %s", all(cts %% 1 == 0))
say("列名与 coldata 对齐   : %s",
    identical(colnames(cts), coldata$sample[match(colnames(cts), coldata$sample)]))
say("各样本文库大小        : %s", paste(colSums(cts), collapse = ", "))
say("文库大小 max/min      : %.2f  <-- 若接近 1.00，说明喂进去的不是原始 counts",
    max(colSums(cts)) / min(colSums(cts)))
say("AI 脚本的 sizeFactors : %s", paste(round(sizeFactors(dds_ai), 3), collapse = ", "))
say("AI 脚本的 design      : %s", paste(deparse(design(dds_ai)), collapse = ""))
say("coldata 实际含有的列  : %s", paste(colnames(coldata), collapse = ", "))

# ---------------- ② 已知答案的回归测试 ----------------
say("")
say("=========== ② 已知答案的回归测试 ===========")
run_de <- function(cond_vec, contrast) {
  cd <- coldata[colnames(cts), , drop = FALSE]
  cd$condition <- factor(cond_vec)
  cd$batch <- factor(cd$batch)
  d <- DESeqDataSetFromMatrix(cts, cd, ~ batch + condition)
  d <- d[rowSums(counts(d)) >= 10, ]
  d <- DESeq(d, quiet = TRUE)
  list(dds = d, res = as.data.frame(results(d, contrast = contrast)))
}
ref <- run_de(coldata[colnames(cts), "condition"], c("condition", "treat", "ctrl"))
sw  <- run_de(ifelse(coldata[colnames(cts), "condition"] == "ctrl", "treat", "ctrl"),
              c("condition", "treat", "ctrl"))

hit_ref <- sum(ref$res[spike, "padj"] < 0.05, na.rm = TRUE)
say("参考流程（raw counts, ~batch+condition, treat vs ctrl）：")
say("  spike-in 召回     : %d / %d  (期望 >= 18)", hit_ref, length(spike))
say("  spike-in log2FC   : 中位数 %.2f  (期望 ≈ +3)",
    median(ref$res[spike, "log2FoldChange"], na.rm = TRUE))
say("  padj<0.05 基因数  : %d", sum(ref$res$padj < 0.05, na.rm = TRUE))
common <- intersect(rownames(ref$res), rownames(sw$res))
say("  换组标签后 log2FC 相关系数: %.3f  (期望 ≈ -1)",
    cor(ref$res[common, "log2FoldChange"], sw$res[common, "log2FoldChange"],
        use = "complete.obs"))

say("被验脚本（AI 版）：")
ai_spike <- res_ai[spike, ]
say("  spike-in 出现在上调侧的个数: %d / %d  <-- 若为 0，比较方向反了",
    sum(ai_spike$log2FoldChange > 0, na.rm = TRUE), length(spike))
say("  spike-in log2FC 中位数     : %.2f", median(ai_spike$log2FoldChange, na.rm = TRUE))
say("  与参考流程 log2FC 的相关性 : %.3f",
    cor(res_ai[intersect(rownames(res_ai), rownames(ref$res)), "log2FoldChange"],
        ref$res[intersect(rownames(res_ai), rownames(ref$res)), "log2FoldChange"],
        use = "complete.obs"))
n_sig_ai <- nrow(read.delim(file.path(adir, "de_results_sig.tsv")))
say("  被验脚本报出的差异基因数   : %d", n_sig_ai)
say("  参考流程的差异基因数       : %d",
    sum(ref$res$padj < 0.05 & abs(ref$res$log2FoldChange) > 1, na.rm = TRUE))
say("  若前者是后者的十倍量级，先查筛选用的是哪一列（pvalue vs padj）")

# ---------------- ③ 关键中间量手算复核 ----------------
say("")
say("=========== ③ 关键中间量手算复核 ===========")
say("AI 脚本 resultsNames  : %s  <-- 字面必须与你想要的方向一致",
    paste(resultsNames(dds_ai), collapse = ", "))
say("参考流程 resultsNames : %s", paste(resultsNames(ref$dds), collapse = ", "))
n_test <- sum(!is.na(res_ai$pvalue))
say("检验基因数 m          : %d", n_test)
say("p<0.05 的期望假阳性数 : %.0f  (m x 0.05)", n_test * 0.05)
say("实际 p<0.05 的基因数  : %d", sum(res_ai$pvalue < 0.05, na.rm = TRUE))
say("手算 BH 最小校正值    : %.3e", min(sort(res_ai$pvalue) * n_test / seq_len(n_test), na.rm = TRUE))
say("res$padj 的最小值     : %.3e", min(res_ai$padj, na.rm = TRUE))
g <- spike[1]
say("基因 %s 在 %s 的原始 counts = %d，文库 %d，手算 CPM = %.2f",
    g, colnames(cts)[1], cts[g, 1], sum(cts[, 1]), cts[g, 1] / sum(cts[, 1]) * 1e6)
say("")
say("下一步：对照讲义 §6.2 的三行指纹表，写出你的判断，再去代码里定位。")
close(con)
cat("\n[p01-03] 报告已写入:", report, "\n")
