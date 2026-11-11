#!/usr/bin/env Rscript
# ============================================================
# m06 扩增子测序分析 —— DADA2 去噪 → ASV 表 → 物种注释 → 多样性
# 环境：conda activate ngs_ms_microbiome
#
# 讲义 ⑦ 统计插件配套：α/β 多样性检验、PERMANOVA、betadisper。
# 所有图的 title / axis / legend 一律英文。
# ============================================================
suppressPackageStartupMessages({
  library(dada2); library(phyloseq); library(vegan); library(ggplot2)
})
set.seed(20260829)

a <- commandArgs(trailingOnly = TRUE)
if (length(a) < 5) stop("用法: 06_dada2_pipeline.R <fqdir> <outdir> <truncF> <truncR> <db> [threads]")
fqdir <- a[1]; outdir <- a[2]
truncF <- as.integer(a[3]); truncR <- as.integer(a[4]); db <- a[5]
threads <- ifelse(length(a) >= 6, as.integer(a[6]), 4)
# 以下用环境变量传入，保持位置参数接口不变（UP-056）：
#   TRIM_F / TRIM_R  引物长度（下机已去引物则 0）；V4 515F/806R 为 19/20，V3–V4 341F/805R 为 17/21
#   BATCH_COL        metadata.tsv 中的测序批次列名（默认 batch）；错误模型按批次分别学
#   MINBOOT          assignTaxonomy 的 bootstrap 阈值（默认 80，与讲义一致；dada2 默认 50）
env_int <- function(k, d) { v <- Sys.getenv(k, ""); if (nzchar(v)) as.integer(v) else d }
trimF <- env_int("TRIM_F", 0L); trimR <- env_int("TRIM_R", 0L)
minboot <- env_int("MINBOOT", 80L)
batch_col <- Sys.getenv("BATCH_COL", "batch")
if (truncF <= trimF || truncR <= trimR) stop("truncLen 必须大于 trimLeft")
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

fnF <- sort(list.files(fqdir, "_1\\.fastq(\\.gz)?$", full.names = TRUE))
fnR <- sort(list.files(fqdir, "_2\\.fastq(\\.gz)?$", full.names = TRUE))
if (length(fnF) == 0 || length(fnF) != length(fnR))
  stop("双端文件配不上：F=", length(fnF), " R=", length(fnR))
samples <- sub("_1\\.fastq(\\.gz)?$", "", basename(fnF))

filtF <- file.path(outdir, "filtered", paste0(samples, "_F.fq.gz"))
filtR <- file.path(outdir, "filtered", paste0(samples, "_R.fq.gz"))
names(filtF) <- names(filtR) <- samples

# ---- 0) 批次：混合不同测序 run 学同一个错误模型会使模型失真（讲义 ⑨-4）----
meta_f <- file.path(fqdir, "metadata.tsv")
meta <- if (file.exists(meta_f)) read.delim(meta_f, row.names = 1, check.names = FALSE) else NULL
if (!is.null(meta) && batch_col %in% colnames(meta)) {
  miss <- setdiff(samples, rownames(meta))
  if (length(miss)) stop("metadata.tsv 缺少样本：", paste(miss, collapse = ", "))
  batch <- as.character(meta[samples, batch_col])
  message("错误模型按 '", batch_col, "' 分 ", length(unique(batch)), " 个批次分别学习")
} else {
  batch <- rep("all", length(samples))
  warning("metadata.tsv 中没有批次列 '", batch_col, "'：全部样本当作同一测序 run 学错误模型。",
          "若样本来自多个 run/年份，这会使错误模型失真（讲义 ⑨-4）——请补批次列。")
}

# ---- 1) 过滤：maxEE 是 DADA2 的核心参数，比按 Q 值硬截更合理 ----
out <- filterAndTrim(fnF, filtF, fnR, filtR, truncLen = c(truncF, truncR),
                     trimLeft = c(trimF, trimR), maxN = 0, maxEE = c(2, 2), truncQ = 2,
                     rm.phix = TRUE, compress = TRUE, multithread = threads)
write.csv(out, file.path(outdir, "filter_stats.csv"))

# ---- 2–3) 按批次：学错误模型 → 去噪 → 合并（Big Data 组织：各批次单独建表再合并）----
keep <- out[, "reads.out"] > 0
if (any(!keep)) warning("过滤后为 0 条的样本被跳过：", paste(samples[!keep], collapse = ", "))
if (!any(keep)) {
  # 全部样本过滤后为 0：先写 track 表再停，避免在下游空表上崩溃、报错指向错误的一步
  write.csv(data.frame(sample = samples, batch = batch, input = out[, "reads.in"],
                       filtered = out[, "reads.out"]),
            file.path(outdir, "track.csv"), row.names = FALSE)
  stop("全部样本过滤后为 0 条读段——常见原因是 truncLen 大于实际读长（如 PE250 数据照抄 PE300 的截断位点），",
       "或 maxEE 过严。见 ", file.path(outdir, "track.csv"))
}
getN <- function(x) sum(getUniques(x))
tabs <- list(); trk <- list()
for (b in unique(batch[keep])) {
  idx <- which(keep & batch == b)
  errF <- learnErrors(filtF[idx], multithread = threads)
  errR <- learnErrors(filtR[idx], multithread = threads)
  png(file.path(outdir, paste0("error_model_F_", b, ".png")), 1200, 900, res = 120)
  print(plotErrors(errF, nominalQ = TRUE)); dev.off()
  ddF <- dada(filtF[idx], err = errF, pool = "pseudo", multithread = threads)
  ddR <- dada(filtR[idx], err = errR, pool = "pseudo", multithread = threads)
  if (length(idx) == 1) { ddF <- list(ddF); ddR <- list(ddR) }
  names(ddF) <- names(ddR) <- samples[idx]
  mg <- mergePairs(ddF, filtF[idx], ddR, filtR[idx])
  if (length(idx) == 1) mg <- setNames(list(mg), samples[idx])
  tabs[[b]] <- makeSequenceTable(mg)
  trk[[b]] <- data.frame(sample = samples[idx],
                         denoisedF = sapply(ddF, getN), denoisedR = sapply(ddR, getN),
                         merged = sapply(mg, function(m) sum(m$abundance)))
}
seqtab <- if (length(tabs) == 1) tabs[[1]] else mergeSequenceTables(tables = tabs)

# ---- track 表：每一步各剩多少读段。合并骤减（重叠不足）只在这里看得见，不报错 ----
#      先写一版（去嵌合前），这样即使下一步失败也留得下诊断依据
track <- data.frame(sample = samples, batch = batch, input = out[, "reads.in"],
                    filtered = out[, "reads.out"])
track <- merge(track, do.call(rbind, trk), by = "sample", all.x = TRUE)
track$merged_frac <- round(track$merged / track$filtered, 3)
write.csv(track, file.path(outdir, "track.csv"), row.names = FALSE)
low <- track$sample[!is.na(track$merged_frac) & track$merged_frac < 0.5]
if (length(low)) warning("以下样本合并后保留不足过滤后读段的 50%（检查 truncLen/trimLeft 与扩增子长度的重叠）：",
                         paste(low, collapse = ", "))
if (ncol(seqtab) == 0 || sum(seqtab) == 0)
  stop("双端合并后 0 条读段——几乎总是 truncLen − trimLeft 之和不够覆盖扩增子（重叠不足）。见 ",
       file.path(outdir, "track.csv"))

seqtab.nochim <- removeBimeraDenovo(seqtab, method = "consensus", multithread = threads)
cat(sprintf("嵌合体去除：保留 %.1f%% 的序列丰度\n",
            100 * sum(seqtab.nochim) / sum(seqtab)))
track$nonchim <- rowSums(seqtab.nochim)[match(track$sample, rownames(seqtab.nochim))]
write.csv(track, file.path(outdir, "track.csv"), row.names = FALSE)
saveRDS(seqtab.nochim, file.path(outdir, "seqtab_nochim.rds"))

# ---- 4) 物种注释 ----
taxa <- assignTaxonomy(seqtab.nochim, db, minBoot = minboot, multithread = threads)
write.csv(taxa, file.path(outdir, "taxonomy.csv"))

# ---- 5) 多样性与统计（讲义 ⑦ 的落点）----
if (!is.null(meta)) {
  common <- intersect(rownames(seqtab.nochim), rownames(meta))
  ps <- phyloseq(otu_table(seqtab.nochim[common, ], taxa_are_rows = FALSE),
                 tax_table(taxa), sample_data(meta[common, , drop = FALSE]))

  p1 <- plot_richness(ps, x = "group", measures = c("Observed", "Shannon")) +
    labs(x = "Group", y = "Alpha diversity", title = "Alpha diversity") +
    theme_bw(base_size = 12)
  ggsave(file.path(outdir, "alpha_diversity.png"), p1, width = 7, height = 5, dpi = 300)

  # α 多样性用原始计数（未抽平；深度差异大时须先看 track 表并在方法中说明）；
  # Bray-Curtis 用相对丰度，与讲义 5.4 / ⑦7.6 一致
  ps_rel <- transform_sample_counts(ps, function(x) x / sum(x))
  d <- phyloseq::distance(ps_rel, method = "bray")
  grp <- sample_data(ps)$group
  ad <- adonis2(d ~ grp, permutations = 999)
  bd <- betadisper(d, grp); bt <- permutest(bd, permutations = 999)
  sink(file.path(outdir, "beta_stats.txt"))
  cat("=== PERMANOVA (adonis2, Bray-Curtis) ===\n"); print(ad)
  cat("\n=== betadisper（离散度齐性检验）===\n"); print(bt)
  cat("\n【怎么读】PERMANOVA 显著但 betadisper 也显著时，组间差异可能来自\n",
      "离散度不齐而非中心位置差异——这时不能直接说'群落组成不同'。\n")
  cat("\n【重复数警示】3 vs 3 时置换检验的最小可能 p 值就是 0.1，\n",
      "无论真实差异多大都做不出 p<0.05。见 l0_06_stats。\n")
  sink()

  ord <- ordinate(ps_rel, method = "PCoA", distance = "bray")
  p2 <- plot_ordination(ps_rel, ord, color = "group") + geom_point(size = 3) +
    labs(title = "PCoA (Bray-Curtis)", color = "Group") + theme_bw(base_size = 12)
  ggsave(file.path(outdir, "pcoa.png"), p2, width = 6, height = 5, dpi = 300)
} else {
  message("未找到 metadata.tsv，跳过多样性统计。")
}
message(sprintf("完成。产出在 %s/", outdir))
