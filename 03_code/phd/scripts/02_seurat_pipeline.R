#!/usr/bin/env Rscript
# ============================================================
# 脚本名称：02_seurat_pipeline.R
# 功能描述：p02 单细胞标准流程 —— 读入 CellRanger 输出 → 质控 → SCTransform →
#           PCA/UMAP → 多分辨率聚类（聚类稳定性，讲义 §⑦-1）→ marker →
#           Harmony 批次整合（含"批次与处理是否混杂"的前置检查，§4.7）。
# 环境    ：conda activate ngs_phd_sc
# 作者    ：王运生
# 日期    ：2026-08-29
#
# 用法：
#   Rscript 02_seurat_pipeline.R --indir <10x_dir> --outdir <out> \
#           [--mt-pattern "^MT-"] [--cp-pattern ""] [--npcs 30] \
#           [--resolution 0.5] [--batch-col batch] [--meta meta.tsv] \
#           [--step all|annotate] [--singler-ref none]
#
# 【所有图的 title/axis/legend 一律英文】：Linux 默认字体下中文显示为方块。
# 【阈值不写死】：percent.mt / nFeature 的界从本数据分布定（§4.3），
#                 脚本给的是分位数默认值，不是人类 PBMC 的经验常数。
# ============================================================
suppressPackageStartupMessages({
  library(Seurat); library(ggplot2); library(dplyr); library(harmony)
})
set.seed(20260829)

# ---------------- 参数 ----------------
argv <- commandArgs(trailingOnly = TRUE)
getopt <- function(flag, default = NULL) {
  i <- which(argv == flag)
  if (length(i) == 0) return(default)
  argv[i + 1]
}
indir       <- getopt("--indir")
outdir      <- getopt("--outdir", "results/p02")
mt_pattern  <- getopt("--mt-pattern", "^MT-")
cp_pattern  <- getopt("--cp-pattern", "")      # 植物必填，如 "^ATCG"（叶绿体）
npcs        <- as.integer(getopt("--npcs", "30"))
res_main    <- as.numeric(getopt("--resolution", "0.5"))
batch_col   <- getopt("--batch-col", "batch")
meta_f      <- getopt("--meta", NA)
step        <- getopt("--step", "all")
singler_ref <- getopt("--singler-ref", "none")
if (is.null(indir)) stop("必须给 --indir（CellRanger filtered_feature_bc_matrix 目录）")
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)
res_grid <- sort(unique(c(0.2, 0.4, 0.6, 0.8, 1.0, res_main)))  # 稳定性扫描（§⑦-1）；并入主分辨率，否则下文取不到 SCT_snn_res.<res_main>

# ---------------- 1. 读入 ----------------
message("[1/8] Read10X: ", indir)
mtx <- Read10X(data.dir = indir)               # 目录必须含 barcodes/features/matrix 三件套（⑨-E1）
obj <- CreateSeuratObject(mtx, project = "p02", min.cells = 3, min.features = 200)
if (!is.na(meta_f)) {
  md <- read.delim(meta_f, row.names = 1, stringsAsFactors = FALSE)
  obj <- AddMetaData(obj, md[colnames(obj), , drop = FALSE])
}
message("    cells = ", ncol(obj), "  genes = ", nrow(obj))

# ---------------- 2. 质控指标：前缀必须按物种改 ----------------
message("[2/8] QC metrics (mt='", mt_pattern, "' cp='", cp_pattern, "')")
obj[["percent.mt"]] <- PercentageFeatureSet(obj, pattern = mt_pattern)
if (nzchar(cp_pattern)) obj[["percent.cp"]] <- PercentageFeatureSet(obj, pattern = cp_pattern)
# 主动拦截"不报错的错误"：前缀不匹配时该列会全为 0（⑨-E2）
if (sum(obj$percent.mt) == 0) {
  warning("percent.mt 全为 0 —— pattern '", mt_pattern,
          "' 很可能与本物种基因命名不匹配。请 grep features.tsv 确认后重跑。")
}
qc_vars <- c("nFeature_RNA", "nCount_RNA", "percent.mt",
             if (nzchar(cp_pattern)) "percent.cp")
ggsave(file.path(outdir, "qc_violin.png"),
       VlnPlot(obj, features = qc_vars, ncol = length(qc_vars), pt.size = 0) &
         theme(axis.title.x = element_blank()),
       width = 3 * length(qc_vars), height = 4, dpi = 200)

# ---------------- 3. 过滤：阈值来自本数据分布 ----------------
lo <- quantile(obj$nFeature_RNA, 0.01); hi <- quantile(obj$nFeature_RNA, 0.99)
mt_hi <- quantile(obj$percent.mt, 0.95)
message(sprintf("[3/8] filter: nFeature %d-%d, percent.mt < %.2f (本数据分位数)",
                round(lo), round(hi), mt_hi))
obj <- subset(obj, subset = nFeature_RNA > lo & nFeature_RNA < hi & percent.mt < mt_hi)
message("    cells after filter = ", ncol(obj))

# ---------------- 4. 标准化与降维 ----------------
message("[4/8] SCTransform + PCA + UMAP (npcs=", npcs, ")")
obj <- SCTransform(obj, verbose = FALSE)       # vars.to.regress 要不要加：见讲义 §4.4
obj <- RunPCA(obj, npcs = npcs, verbose = FALSE)
ggsave(file.path(outdir, "elbow.png"), ElbowPlot(obj, ndims = npcs),
       width = 5, height = 4, dpi = 200)
obj <- RunUMAP(obj, dims = seq_len(npcs), verbose = FALSE)

# ---------------- 5. 多分辨率聚类（稳定性，§⑦-1）----------------
message("[5/8] FindClusters over resolution grid: ", paste(res_grid, collapse = ", "))
obj <- FindNeighbors(obj, dims = seq_len(npcs), verbose = FALSE)
for (r in res_grid) obj <- FindClusters(obj, resolution = r, verbose = FALSE)
res_cols <- grep("^SCT_snn_res\\.", colnames(obj@meta.data), value = TRUE)
stab <- data.frame(resolution = res_grid,
                   n_cluster = sapply(res_cols, function(c) length(unique(obj@meta.data[[c]]))))
write.table(stab, file.path(outdir, "cluster_stability.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)
print(stab)
main_col <- paste0("SCT_snn_res.", res_main)
if (!main_col %in% colnames(obj@meta.data)) stop("找不到聚类列 ", main_col, "；现有：", paste(res_cols, collapse = ", "))
Idents(obj) <- obj@meta.data[[main_col]]
obj$seurat_clusters <- Idents(obj)

# ---------------- 6. Marker ----------------
if (step %in% c("all", "annotate")) {
  message("[6/8] FindAllMarkers (仅用于注释的描述性比较，不可用于组间检验，见 §⑦-2)")
  mk <- FindAllMarkers(obj, only.pos = TRUE, min.pct = 0.25,
                       logfc.threshold = 0.25, verbose = FALSE)
  write.table(mk, file.path(outdir, "markers.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
  top <- mk %>% group_by(cluster) %>% slice_max(avg_log2FC, n = 3) %>% pull(gene) %>% unique()
  ggsave(file.path(outdir, "marker_dotplot.png"),
         DotPlot(obj, features = top) + RotatedAxis() +
           labs(x = "Marker gene", y = "Cluster"),
         width = 2 + 0.28 * length(top), height = 5, dpi = 200)
}
if (!identical(singler_ref, "none")) {
  message("    SingleR 参考: ", singler_ref,
          " —— 注意：非模式物种通常没有可用参考，硬套会得到一串看似合理的错标签（§4.6）")
}

# ---------------- 7. Harmony 整合 ----------------
if (batch_col %in% colnames(obj@meta.data)) {
  # 无 condition 列时不能拿 batch 自比：table(batch, batch) 是对角阵，会被误判为
  # "完全混杂"而静默跳过整合（UP-054）。此时显式告警"无法检查混杂"，照常整合。
  n_batch <- length(unique(obj@meta.data[[batch_col]]))
  has_cond <- "condition" %in% colnames(obj@meta.data)
  if (has_cond) {
    tb <- table(batch = obj@meta.data[[batch_col]], condition = obj$condition)
    print(tb)
    confounded <- all(rowSums(tb > 0) <= 1) && ncol(tb) > 1
  } else {
    warning("meta.data 无 'condition' 列：无法检查批次与处理是否混杂，",
            "整合可能连同处理效应一起抹掉——请用 --meta 补 condition 列后重跑（§4.7）。")
    confounded <- FALSE
  }
  if (n_batch < 2) {
    message("[7/8] 跳过整合：列 '", batch_col, "' 只有 1 个批次")
  } else if (confounded) {
    warning("批次与 condition 完全混杂：任何整合方法都会连同处理效应一起抹掉（§4.7）。",
            "本脚本拒绝整合。请在方法中报告这一设计限制。")
  } else {
    message("[7/8] RunHarmony on '", batch_col, "'")
    p_before <- DimPlot(obj, group.by = batch_col) + ggtitle("Before integration")
    obj <- RunHarmony(obj, group.by.vars = batch_col, assay.use = "SCT")
    obj <- RunUMAP(obj, reduction = "harmony", dims = seq_len(npcs),
                   reduction.name = "umap_harmony", verbose = FALSE)
    p_after <- DimPlot(obj, reduction = "umap_harmony", group.by = batch_col) +
      ggtitle("After Harmony")
    ggsave(file.path(outdir, "integration_before_after.png"), p_before | p_after,
           width = 11, height = 4.5, dpi = 200)
    message("    对比两张图判断是否过度校正：混得越匀越好是错的判据（§4.7）")
  }
} else {
  message("[7/8] 跳过整合：meta.data 中没有列 '", batch_col, "'")
}

# ---------------- 8. 保存 ----------------
message("[8/8] saveRDS + sessionInfo")
saveRDS(obj, file.path(outdir, "integrated.rds"))
writeLines(capture.output(sessionInfo()), file.path(outdir, "sessionInfo.txt"))
cat("[p02-01] done ->", outdir, "\n")
