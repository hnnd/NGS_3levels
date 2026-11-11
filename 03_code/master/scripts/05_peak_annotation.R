#!/usr/bin/env Rscript
# ============================================
# 脚本名称：05_peak_annotation.R
# 功能描述：硕士 m05 转录调控与表观组 —— 下游分析
#           ChIPseeker peak 注释（特征分布 / TSS 距离 / peak-基因关联表）
#           + 与 m04 差异表达基因取交集 + 交集大小的置换检验
# 课程专题：m05（02_lectures/master/topic05_regulome/05_regulome_lecture.md ⑤ 步骤 5、7；⑦ 第 6 条）
# 运行环境：ngs_ms_transcriptome（07_envs/conda/env_master_transcriptome.yml）
# 用法：
#   Rscript 05_peak_annotation.R \
#       --peak reproducible_peaks.bed --gff ref/annotation.gff3 \
#       --deg topic04_deseq2_results.csv --outdir results/m05
# 【图表规则】所有图的标题 / 轴标签 / 图例一律英文 ——
#            Linux 上 matplotlib/R 的默认中文字体多显示为方块。中文解释写在报告正文里。
# 作者：王运生
# 日期：2026-08-29
# ============================================

suppressPackageStartupMessages({
  library(ChIPseeker)
  library(GenomicFeatures)
  library(GenomicRanges)
  library(ggplot2)
})

set.seed(20260829)   # 置换检验必须可复现（全局规则：experiment-reproducibility）

# --------------------------------------------
# 1. 参数解析（全部可覆盖，不写死路径）
# --------------------------------------------
parse_args <- function(args) {
  defaults <- list(
    peak    = "reproducible_peaks.bed",       # MACS2/IDR 产出的 peak 区间
    gff     = "ref/annotation.gff3",          # 本物种自己的注释，不要用别的物种预置 TxDb
    deg     = "topic04_deseq2_results.csv",   # m04 产出：含 gene_id / log2FoldChange / padj
    outdir  = "results/m05",
    tss_up  = "-3000",                        # promoter 窗口上游
    tss_down = "3000",                        # promoter 窗口下游
    padj    = "0.05",                         # m04 差异基因的 padj 阈值
    lfc     = "1",                            # m04 差异基因的 |log2FC| 阈值
    nperm   = "1000"                          # 置换次数
  )
  for (a in args) {
    kv <- regmatches(a, regexec("^--([A-Za-z_]+)=?(.*)$", a))[[1]]
    if (length(kv) == 3L && nzchar(kv[3])) defaults[[kv[2]]] <- kv[3]
  }
  defaults
}

opt <- parse_args(commandArgs(trailingOnly = TRUE))
dir.create(opt$outdir, recursive = TRUE, showWarnings = FALSE)
message("[m05] peak = ", opt$peak, " | gff = ", opt$gff, " | deg = ", opt$deg)

# --------------------------------------------
# 2. 构建 TxDb 并读入 peak
#    ⚠ 染色体命名必须与 TxDb 一致（chr1 vs 1），否则注释全落 Distal Intergenic
#      且只报 warning 不报错（讲义 ⑨ 错误 4）。
# --------------------------------------------
txdb <- makeTxDbFromGFF(opt$gff, format = "gff3")
peak <- readPeakFile(opt$peak)

style_txdb <- tryCatch(seqlevelsStyle(txdb)[1], error = function(e) NA_character_)
if (!is.na(style_txdb)) {
  ok <- tryCatch({ seqlevelsStyle(peak) <- style_txdb; TRUE }, error = function(e) FALSE)
  if (!ok) message("[m05] 自动统一 seqlevelsStyle 失败，请手工检查染色体命名")
}
shared <- intersect(seqlevels(peak), seqlevels(txdb))
if (length(shared) == 0L) {
  stop("peak 与 TxDb 没有任何共同染色体名——命名不匹配或用错了物种的注释。\n",
       "  peak: ", paste(head(seqlevels(peak), 3), collapse = ", "), "\n",
       "  txdb: ", paste(head(seqlevels(txdb), 3), collapse = ", "))
}
message("[m05] peak 数 = ", length(peak), "；共同染色体 = ", length(shared))

# --------------------------------------------
# 3. 注释（特征分布 + 到最近 TSS 的距离）
# --------------------------------------------
anno <- annotatePeak(peak,
                     tssRegion = c(as.numeric(opt$tss_up), as.numeric(opt$tss_down)),
                     TxDb = txdb)
anno_df <- as.data.frame(anno)
write.csv(anno_df, file.path(opt$outdir, "peak_annotation.csv"), row.names = FALSE)

# 红灯自检：intergenic > 95% 几乎一定是命名/物种不匹配，不是生物学发现
feat <- sub(" .*", "", anno_df$annotation)
intergenic_frac <- mean(feat == "Distal", na.rm = TRUE)
if (isTRUE(intergenic_frac > 0.95)) {
  warning("Distal Intergenic 占比 ", round(intergenic_frac * 100, 1),
          "% —— 先怀疑染色体命名或 TxDb 物种不匹配（讲义 ⑨ 错误 4），再谈生物学。")
}

pdf(file.path(opt$outdir, "peak_annotation_plots.pdf"), width = 8, height = 6)
plotAnnoPie(anno)                                        # 标签由 ChIPseeker 生成，为英文
plotDistToTSS(anno, title = "Distribution of peaks relative to TSS")
dev.off()

# --------------------------------------------
# 4. peak 关联基因集合（"最近基因"，不是"靶基因"——讲义 §4.5）
# --------------------------------------------
peak_genes <- unique(na.omit(as.character(anno_df$geneId)))
writeLines(peak_genes, file.path(opt$outdir, "peak_nearest_genes.txt"))
message("[m05] peak 关联基因数 = ", length(peak_genes))

# --------------------------------------------
# 5. 读 m04 差异表达结果，取差异基因与"可检测基因全集"
#    全集 = 实际参与检验、padj 非 NA 的基因（被独立过滤掉的基因不在检验空间里）
# --------------------------------------------
deg_raw <- read.csv(opt$deg, stringsAsFactors = FALSE)
gene_col <- intersect(c("gene_id", "gene", "GeneID", "X"), names(deg_raw))[1]
if (is.na(gene_col)) stop("差异表达表里找不到基因 ID 列（gene_id / gene / GeneID / X）")

deg_raw$.gene <- as.character(deg_raw[[gene_col]])
tested   <- deg_raw[!is.na(deg_raw$padj), ]
universe <- unique(tested$.gene)
deg_set  <- unique(tested$.gene[tested$padj < as.numeric(opt$padj) &
                                abs(tested$log2FoldChange) > as.numeric(opt$lfc)])
message("[m05] 可检测基因全集 = ", length(universe), "；差异基因 = ", length(deg_set))

# 只保留同时出现在全集里的 peak 关联基因，否则交集与置换的分母不一致
peak_genes_in <- intersect(peak_genes, universe)
observed <- length(intersect(peak_genes_in, deg_set))
message("[m05] 观察到的交集大小 = ", observed)

# --------------------------------------------
# 6. ⚠ 置换检验：交集大小的经验 p 值（讲义 ⑦ 第 6 条）
#    两侧列表各自已做过 FDR 校正，但交集大小的零分布没有封闭形式，
#    不能直接宣称"重叠显著"。
#    零模型：固定 n = |peak 关联基因|，从可检测基因全集中随机抽 n 个，与差异基因求交。
#    局限：打乱的是基因标签，假定每个基因被 peak 关联的先验概率相同，
#          忽略了基因密度与启动子 CpG 岛的不均匀性。更严格的零模型是用
#          `bedtools shuffle -incl mappable.bed -excl blacklist.bed -chrom`
#          打乱 peak 坐标后重新注释，代价高一到两个量级。报告里注明用了哪一种。
# --------------------------------------------
n_perm <- as.integer(opt$nperm)
n_draw <- length(peak_genes_in)
null_overlap <- vapply(seq_len(n_perm), function(i) {
  length(intersect(sample(universe, n_draw), deg_set))
}, numeric(1))

emp_p <- (1 + sum(null_overlap >= observed)) / (n_perm + 1)
fold  <- observed / max(median(null_overlap), 1e-9)

perm_stat <- data.frame(
  observed          = observed,
  null_median       = median(null_overlap),
  null_mean         = mean(null_overlap),
  null_q95          = as.numeric(quantile(null_overlap, 0.95)),
  fold_over_median  = round(fold, 3),
  n_permutations    = n_perm,
  empirical_p       = emp_p
)
write.csv(perm_stat, file.path(opt$outdir, "overlap_permutation_test.csv"), row.names = FALSE)
print(perm_stat)

# 交集基因表：带上 m04 的方向，供 §4.7 的方向推断使用
overlap_tbl <- tested[tested$.gene %in% intersect(peak_genes_in, deg_set),
                      c(".gene", "log2FoldChange", "padj")]
names(overlap_tbl)[1] <- "gene_id"
overlap_tbl$rna_direction <- ifelse(overlap_tbl$log2FoldChange > 0, "up", "down")
write.csv(overlap_tbl, file.path(opt$outdir, "diffpeak_x_deg.csv"), row.names = FALSE)

# --------------------------------------------
# 7. 置换零分布图（英文标签）
# --------------------------------------------
p <- ggplot(data.frame(overlap = null_overlap), aes(x = overlap)) +
  geom_histogram(bins = 40, fill = "grey70", colour = "white") +
  geom_vline(xintercept = observed, colour = "firebrick", linewidth = 1) +
  annotate("text", x = observed, y = Inf, vjust = 1.5, hjust = -0.1,
           colour = "firebrick",
           label = sprintf("observed = %d\nempirical p = %.4f", observed, emp_p)) +
  labs(title    = "Permutation null for peak-gene / DEG overlap",
       subtitle = sprintf("%d permutations; %d genes drawn from %d testable genes",
                          n_perm, n_draw, length(universe)),
       x = "Overlap size under null", y = "Frequency") +
  theme_bw(base_size = 12)
ggsave(file.path(opt$outdir, "overlap_permutation.pdf"), p, width = 7, height = 5)

message("[m05] 完成。产出目录：", normalizePath(opt$outdir))
message("[m05] 报告措辞提醒：交集显著且方向一致仍只是相关性证据，")
message("      写「候选直接调控靶标」，不写「证明了 X 调控 Y」（讲义 §4.7）。")
