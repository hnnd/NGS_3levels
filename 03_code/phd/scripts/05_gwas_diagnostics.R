#!/usr/bin/env Rscript
# ============================================================
# 脚本名称：05_gwas_diagnostics.R
# 功能描述：p05 GWAS 诊断 —— QQ 图 + λ_GC + λ–PC 曲线 + 曼哈顿图 + 显著位点表
# 作者：王运生
# 日期：2026-08-29
# 用法：Rscript 05_gwas_diagnostics.R <gemma_output_dir> <n_eff> [out_dir]
#       n_eff = 有效独立检验数（p04 的 prune.prune.in 行数，或置换检验结果）
# 配套讲义：02_lectures/phd/topic05_gwas/05_gwas_lecture.md §5.7、⑥ 6.1、⑦ 7.3
# ============================================================
#
# 顺序纪律（讲义 §4.4）：**先 QQ、再 λ、最后曼哈顿**。
#   - 整体抬升（曲线从最小的 -log10p 起就系统性高于对角线）= 模型没搭对，
#     曼哈顿图上的一切都不可解读；
#   - 尾部抬升（前 90–99% 贴合、只有末端翘起）= 可能是真信号。
#   两者在曼哈顿图上都表现为"很多超线的点"，肉眼无法区分——这就是必须先画 QQ 的原因。
# λ 的读法：λ 只用中位数，对尾部不敏感，它检测的正是"整体抬升"；且 λ 随样本量与
#   性状多基因性上升（Yang et al. 2011），"λ<1.05 才算干净"在大样本上是错的。
# 图中一律使用英文标签（项目图表规则）。

suppressPackageStartupMessages({
  library(qqman)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2L) {
  stop("用法：Rscript 05_gwas_diagnostics.R <gemma_output_dir> <n_eff> [out_dir]")
}
res_dir <- args[1]
n_eff   <- as.numeric(args[2])
out_dir <- if (length(args) >= 3L) args[3] else file.path(res_dir, "diagnostics")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

P_COL <- "p_wald"   # -lmm 4 同时给 p_wald / p_lrt / p_score；固定报一个并写明是哪个

lambda_gc <- function(p) {
  p <- p[is.finite(p) & p > 0 & p <= 1]
  median(qchisq(1 - p, df = 1)) / qchisq(0.5, df = 1)   # qchisq(0.5,1) = 0.4549
}

assoc_files <- list.files(res_dir, pattern = "\\.assoc\\.txt$", full.names = TRUE)
if (length(assoc_files) == 0L) {
  stop("在 ", res_dir, " 下没找到 *.assoc.txt。GEMMA 默认写到 ./output/（讲义 ⑨ E5）")
}

summary_rows <- list()
for (f in assoc_files) {
  tag <- sub("\\.assoc\\.txt$", "", basename(f))
  d   <- read.table(f, header = TRUE, stringsAsFactors = FALSE)
  if (!P_COL %in% names(d)) {
    warning("跳过 ", tag, "：没有列 ", P_COL, "（-lm 的输出列名可能不同）"); next
  }
  p <- d[[P_COL]]
  lam <- lambda_gc(p)
  # λ_1000：按样本量标准化到 n = 1000，跨研究比较时用（数量性状）。
  # 样本量脚本读不到，用环境变量 N_IND 传入；不传则不算。
  n_hint <- suppressWarnings(as.numeric(Sys.getenv("N_IND", NA)))
  lam1000 <- if (!is.na(n_hint) && n_hint > 0) 1 + (lam - 1) * 1000 / n_hint else NA_real_

  png(file.path(out_dir, paste0("qq_", tag, ".png")), width = 1500, height = 1500, res = 300)
  qq(p, main = sprintf("%s  (lambda = %.3f)", tag, lam))
  dev.off()

  thr_gw  <- 0.05 / n_eff     # Bonferroni with M_eff（讲义 §4.3）
  thr_sug <- 1 / n_eff        # suggestive
  d$CHR_num <- as.integer(factor(d$chr))                 # qqman 要求数值型 CHR（⑨ E7）
  write.table(unique(d[, c("chr", "CHR_num")]),
              file.path(out_dir, paste0("chr_map_", tag, ".tsv")),
              sep = "\t", quote = FALSE, row.names = FALSE)
  png(file.path(out_dir, paste0("manhattan_", tag, ".png")), width = 2400, height = 1000, res = 200)
  manhattan(d, chr = "CHR_num", bp = "ps", p = P_COL, snp = "rs",
            genomewideline = -log10(thr_gw), suggestiveline = -log10(thr_sug),
            main = sprintf("%s  (lambda = %.3f, threshold = %.2e)", tag, lam, thr_gw))
  dev.off()

  hits <- d[p < thr_gw, ]
  if (nrow(hits) > 0L) {
    keep <- intersect(c("chr", "rs", "ps", "allele1", "allele0", "af", "beta", "se", P_COL),
                      names(hits))
    hits <- hits[order(hits[[P_COL]]), keep]
    write.table(hits, file.path(out_dir, paste0("hits_", tag, ".tsv")),
                sep = "\t", quote = FALSE, row.names = FALSE)
  }
  summary_rows[[tag]] <- data.frame(
    model = tag, n_snp = nrow(d), lambda = round(lam, 4),
    lambda_1000 = ifelse(is.na(lam1000), NA, round(lam1000, 4)),
    thr_genomewide = signif(thr_gw, 3), n_hits = nrow(hits),
    min_p = signif(min(p, na.rm = TRUE), 3), stringsAsFactors = FALSE)
  message(sprintf("[INFO] %-14s lambda=%.3f  n_hits=%d  min_p=%.2e", tag, lam, nrow(hits), min(p, na.rm = TRUE)))
}

summ <- do.call(rbind, summary_rows)
summ <- summ[order(summ$model), ]
write.table(summ, file.path(out_dir, "model_summary.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)

# ---- λ–PC 曲线：选 PC 数的直接依据（讲义 ⑦ 7.2）----
pc_rows <- summ[grepl("^mlm_pc[0-9]+$", summ$model), ]
if (nrow(pc_rows) > 1L) {
  pc_rows$npc <- as.integer(sub("^mlm_pc", "", pc_rows$model))
  pc_rows <- pc_rows[order(pc_rows$npc), ]
  png(file.path(out_dir, "lambda_vs_npc.png"), width = 1600, height = 1200, res = 300)
  op <- par(mar = c(4.5, 4.5, 3, 4.5))
  plot(pc_rows$npc, pc_rows$lambda, type = "b", pch = 19, col = "#2166AC",
       xlab = "Number of principal components", ylab = expression(lambda[GC]),
       main = "Genomic inflation vs. number of PCs")
  abline(h = 1, lty = 2, col = "grey40")
  par(new = TRUE)
  plot(pc_rows$npc, pc_rows$n_hits, type = "b", pch = 17, col = "#B2182B",
       axes = FALSE, xlab = "", ylab = "")
  axis(4); mtext("Number of significant hits", side = 4, line = 3)
  legend("topright", legend = c("lambda", "hits"), col = c("#2166AC", "#B2182B"),
         pch = c(19, 17), lty = 1, bty = "n", cex = 0.8)
  par(op); dev.off()
  message("[INFO] lambda_vs_npc.png：取 'λ 接近 1 且信号未被抹平的最小 PC 数'（讲义 ⑦ 7.2）")
}

cat("\n===== 判读提示（讲义 ⑥ 6.1）=====\n",
    "λ 明显 > 1 且 QQ 整体抬升  → 系统性膨胀，先修模型，不要解读曼哈顿图\n",
    "λ ≈ 1 且 QQ 仅尾部抬升     → 形态正常，可以看曼哈顿图\n",
    "λ < 1 且 QQ 整体低于对角线 → 过度校正（PC 太多 / K 吸收了共线的真信号）\n",
    "尾部也贴合对角线           → 没有可检出信号；回去查 H² 与样本量，别放宽阈值\n", sep = "")
message("[INFO] 完成，输出在 ", out_dir)
