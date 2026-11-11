#!/usr/bin/env Rscript
# ============================================================
# 脚本名称：03_dual_deseq2_lrt.R
# 功能描述：p03 宿主-病原互作组学 —— 宿主/病原分开归一化 + 侵染时序 LRT
#           + 「高表达 + 强分泌信号 + 物种特异」候选效应子排序表
# 作者：王运生
# 日期：2026-08-29
# 环境：source ${CONDA_ROOT:-/opt/miniconda3}/bin/activate ngs_phd_interaction
# 运行：Rscript 03_dual_deseq2_lrt.R <counts_host_dir> <counts_path_dir> <samples.tsv> \
#            <effectorp.tsv> <signalp_prediction_results.txt> <specific_genes.txt> <outdir>
# 配套讲义：02_lectures/phd/topic03_host_pathogen/03_host_pathogen_lecture.md §5.4、§5.6
# ============================================================
#
# 核心纪律（讲义 §4.4）：
#   宿主与病原**分别**建 DESeqDataSet、**分别**估 size factor。
#   本脚本刻意不提供"合并矩阵"的入口——合并后算 TPM/CPM 是系统性错误。
#
# 所有图的 title / axis / legend 一律英文（Linux 中文字体常显示为方块）。

suppressPackageStartupMessages({ library(DESeq2); library(ggplot2) })
set.seed(20260829)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 7) {
  stop("用法: 03_dual_deseq2_lrt.R <counts_host_dir> <counts_path_dir> <samples.tsv> ",
       "<effectorp.tsv> <signalp_prediction_results.txt> <specific_genes.txt> <outdir>\n",
       "  samples.tsv 需含列: sample treatment time  (treatment 取值含 mock / inoculated)")
}
host_dir <- args[1]; path_dir <- args[2]; samp_f <- args[3]
eff_f <- args[4]; sp_f <- args[5]; spec_f <- args[6]; outdir <- args[7]
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

# ---------------------------------------------------------------- 读入
read_counts <- function(dir, samples) {
  mats <- lapply(samples, function(s) {
    f <- file.path(dir, paste0(s, ".tsv"))
    if (!file.exists(f)) stop("缺少计数文件: ", f)
    x <- read.delim(f, header = FALSE, row.names = 1, col.names = c("gene", s))
    x
  })
  # 显式按基因名对齐后再 cbind，绝不依赖各文件行序一致
  genes <- Reduce(intersect, lapply(mats, rownames))
  as.matrix(do.call(cbind, lapply(mats, function(m) m[genes, , drop = FALSE])))
}

coldata <- read.delim(samp_f, stringsAsFactors = FALSE)
stopifnot(all(c("sample", "treatment", "time") %in% colnames(coldata)))
rownames(coldata) <- coldata$sample
coldata$treatment <- relevel(factor(coldata$treatment), ref = "mock")     # 显式定参考水平
coldata$time      <- factor(coldata$time, levels = sort(unique(coldata$time)))

cts_h <- read_counts(host_dir, coldata$sample)
cts_p <- read_counts(path_dir, coldata$sample)
coldata <- coldata[colnames(cts_h), , drop = FALSE]
stopifnot(identical(colnames(cts_h), rownames(coldata)))

# ---------------------------------------------------------------- 宿主侧：交互模型 LRT
# 只用接种组跑 ~ time，会把昼夜节律/发育/伤害响应整体误报为侵染响应（讲义 §4.5）
dds_h <- DESeqDataSetFromMatrix(cts_h, coldata, design = ~ treatment + time + treatment:time)
dds_h <- dds_h[rowSums(counts(dds_h) >= 10) >= 3, ]
dds_h <- estimateSizeFactors(dds_h)                       # 宿主侧"多数基因不变"通常成立
dds_h <- DESeq(dds_h, test = "LRT", reduced = ~ treatment + time)
res_h <- results(dds_h)
write.csv(as.data.frame(res_h), file.path(outdir, "host_timecourse_LRT.csv"))

# ---------------------------------------------------------------- 病原侧：~time LRT
# 病原侧没有 mock，只能建 ~ time；且 time 与生物量共线，结论须打折扣（讲义 §4.5）
inoc <- rownames(coldata)[coldata$treatment == "inoculated"]
cd_p <- droplevels(coldata[inoc, , drop = FALSE])
dds_p <- DESeqDataSetFromMatrix(cts_p[, inoc, drop = FALSE], cd_p, design = ~ time)
dds_p <- dds_p[rowSums(counts(dds_p)) > 0, ]
# 早期时间点大量基因为 0 → 默认法报 "every gene contains at least one zero"（讲义 ⑨-E3）
dds_p <- estimateSizeFactors(dds_p, type = "poscounts")
dds_p <- DESeq(dds_p, test = "LRT", reduced = ~ 1)
res_p <- results(dds_p)
write.csv(as.data.frame(res_p), file.path(outdir, "pathogen_timecourse_LRT.csv"))

# ---------------------------------------------------------------- 归一化诊断（必看）
# size factor 若在吸收全局趋势而非校正深度，点会按时间顺序系统性偏离直线（讲义 §6.2）
diag_df <- data.frame(
  depth_ratio = colSums(counts(dds_p)) / mean(colSums(counts(dds_p))),
  size_factor = sizeFactors(dds_p),
  time        = cd_p$time
)
write.csv(diag_df, file.path(outdir, "pathogen_sizefactor_diagnostic.csv"))
ggsave(file.path(outdir, "pathogen_sizefactor_diagnostic.png"),
       ggplot(diag_df, aes(depth_ratio, size_factor, colour = time)) +
         geom_point(size = 3) + geom_abline(slope = 1, intercept = 0, linetype = "dashed") +
         labs(x = "Library depth / mean depth", y = "DESeq2 size factor",
              title = "Pathogen-side normalization diagnostic",
              subtitle = "Systematic deviation ordered by time point = normalization failure") +
         theme_bw(),
       width = 6, height = 5, dpi = 300)

# ---------------------------------------------------------------- 候选效应子排序表
# 三条证据（讲义 §5.6）。原始值全部输出，让读者能用自己的权重重排。
strip_pfx <- function(x) sub("^[^|]*\\|", "", sub("^PATH_", "", x))

eff <- read.delim(eff_f, stringsAsFactors = FALSE)
sp  <- read.delim(sp_f, comment.char = "#", header = FALSE, stringsAsFactors = FALSE)
spec <- strip_pfx(readLines(spec_f))

eff_id  <- strip_pfx(eff[[1]])
eff_prob <- suppressWarnings(as.numeric(eff[[grep("prob|score", tolower(names(eff)))[1]]]))
sp_id   <- strip_pfx(sp[[1]])
# SignalP 6 prediction_results.txt 列序：ID / Prediction / OTHER / SP(Sec/SPI) / LIPO / … / CS Position。
# 第 3 列是 OTHER（非信号肽）概率，取错会把排序证据方向取反且不报错（UP-052）。
# 因此按注释表头的列名定位 SP(Sec/SPI)，找不到表头时才退回第 4 列并告警。
sp_hdr  <- grep("^#\\s*ID\\t", readLines(sp_f, n = 5L), value = TRUE)
sp_col  <- if (length(sp_hdr)) {
  which(strsplit(sub("^#\\s*", "", sp_hdr[1]), "\t")[[1]] == "SP(Sec/SPI)")
} else integer(0)
if (length(sp_col) != 1L) {
  warning("SignalP 表头中未找到 SP(Sec/SPI) 列，按 SignalP 6 默认列序取第 4 列")
  sp_col <- 4L
}
sp_prob <- suppressWarnings(as.numeric(sp[[sp_col]]))
stopifnot(all(sp_prob >= 0 & sp_prob <= 1, na.rm = TRUE))

pdat <- as.data.frame(res_p)
pdat$gene <- strip_pfx(rownames(pdat))
pdat$expr <- log2(pdat$baseMean + 1)

cand <- data.frame(gene = unique(eff_id), stringsAsFactors = FALSE)
cand$effectorp_prob <- eff_prob[match(cand$gene, eff_id)]
cand$signalp_prob   <- sp_prob[match(cand$gene, sp_id)]
cand$log2_baseMean  <- pdat$expr[match(cand$gene, pdat$gene)]
cand$lrt_padj       <- pdat$padj[match(cand$gene, pdat$gene)]
cand$strain_specific <- cand$gene %in% spec

rank01 <- function(x) { r <- rank(x, na.last = "keep", ties.method = "average")
                        (r - 1) / (sum(!is.na(x)) - 1) }
cand$score <- rowMeans(cbind(rank01(cand$log2_baseMean),
                             rank01(cand$signalp_prob),
                             as.numeric(cand$strain_specific)), na.rm = TRUE)
cand <- cand[order(-cand$score), ]
write.table(cand, file.path(outdir, "candidate_effectors.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)

message("完成。产出：")
message("  host_timecourse_LRT.csv / pathogen_timecourse_LRT.csv")
message("  pathogen_sizefactor_diagnostic.png  ← 这张图不看，上面所有 p 值都不值得信")
message("  candidate_effectors.tsv  （", nrow(cand), " 条）")
message("提醒（讲义 §4.7）：这是候选表不是鉴定结果；score 的权重是主观的，")
message("  三列原始证据已一并输出，报告中必须写明你用的权重与理由。")
