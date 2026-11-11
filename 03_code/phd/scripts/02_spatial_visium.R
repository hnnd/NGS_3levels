#!/usr/bin/env Rscript
# ============================================================
# 脚本名称：02_spatial_visium.R
# 功能描述：p02 空间转录组（10X Visium）标准流程 ——
#           Load10X_Spatial → 质控 → SCTransform(assay="Spatial") →
#           降维聚类 → SpatialDimPlot / SpatialFeaturePlot。
# 环境    ：conda activate ngs_phd_sc
# 作者    ：王运生
# 日期    ：2026-08-29
#
# 用法：Rscript 02_spatial_visium.R --indir <spaceranger_outs> --outdir <out> \
#          [--resolution 0.8] [--npcs 30] [--features GENE1,GENE2]
#
# 【结论表述纪律，讲义 §4.8】Visium 的 spot 直径 55 um、中心间距 100 um，
#  一个 spot 内含多个细胞，spot 之间还有未采样的间隙。
#  "spot 里检测到某基因" != "某个细胞表达某基因" —— 写结论时不得越过这条线。
# ============================================================
suppressPackageStartupMessages({
  library(Seurat); library(ggplot2); library(patchwork)
})
set.seed(20260829)

argv <- commandArgs(trailingOnly = TRUE)
getopt <- function(f, d = NULL) { i <- which(argv == f); if (!length(i)) d else argv[i + 1] }
indir  <- getopt("--indir");  if (is.null(indir)) stop("必须给 --indir（Space Ranger outs 目录）")
outdir <- getopt("--outdir", "results/p02/spatial")
res    <- as.numeric(getopt("--resolution", "0.8"))
npcs   <- as.integer(getopt("--npcs", "30"))
feats  <- getopt("--features", NA)
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

message("[1/5] Load10X_Spatial: ", indir)
# 目录须含 filtered_feature_bc_matrix.h5 与 spatial/（新版 tissue_positions.csv，
# 旧版 tissue_positions_list.csv；版本不匹配时见讲义 ⑨-E10）
sp <- Load10X_Spatial(data.dir = indir)
message("    spots = ", ncol(sp), "  genes = ", nrow(sp))

message("[2/5] QC")
sp$nCount_Spatial_log10 <- log10(sp$nCount_Spatial + 1)
p_qc <- (VlnPlot(sp, features = "nCount_Spatial", pt.size = 0) + NoLegend() +
           labs(x = NULL, y = "UMI per spot")) |
        (SpatialFeaturePlot(sp, features = "nCount_Spatial") +
           theme(legend.position = "right"))
ggsave(file.path(outdir, "spatial_qc.png"), p_qc, width = 10, height = 4.5, dpi = 200)
# 空间数据不按 UMI 数硬性过滤 spot：低 UMI 可能是真实的低细胞密度区域，
# 直接滤掉会人为制造"组织空洞"。先看图，再决定。

message("[3/5] SCTransform (assay = 'Spatial') + PCA/UMAP")
sp <- SCTransform(sp, assay = "Spatial", verbose = FALSE)
sp <- RunPCA(sp, assay = "SCT", npcs = npcs, verbose = FALSE)
sp <- RunUMAP(sp, dims = seq_len(npcs), verbose = FALSE)
sp <- FindNeighbors(sp, dims = seq_len(npcs), verbose = FALSE)
sp <- FindClusters(sp, resolution = res, verbose = FALSE)

message("[4/5] plots")
p_clu <- (DimPlot(sp, reduction = "umap", label = TRUE) + NoLegend() + ggtitle("UMAP")) |
         (SpatialDimPlot(sp, label = TRUE, label.size = 3) + ggtitle("Spatial clusters"))
ggsave(file.path(outdir, "spatial_clusters.png"), p_clu, width = 11, height = 5, dpi = 200)
# 判读：簇的空间分布应当与组织结构对得上；若呈规则条带且与形态无关，
# 多为芯片区域/图像配准问题或该基因根本没表达（讲义 §6.2 末行）。

if (!is.na(feats)) {
  gl <- intersect(strsplit(feats, ",")[[1]], rownames(sp))
  if (length(gl)) {
    ggsave(file.path(outdir, "spatial_features.png"),
           SpatialFeaturePlot(sp, features = gl, ncol = min(3, length(gl))),
           width = 4 * min(3, length(gl)), height = 4 * ceiling(length(gl) / 3), dpi = 200)
  } else message("    --features 里没有一个基因存在于本数据，跳过")
}

message("[5/5] save")
saveRDS(sp, file.path(outdir, "visium.rds"))
mk <- FindAllMarkers(sp, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25, verbose = FALSE)
write.table(mk, file.path(outdir, "spatial_markers.tsv"), sep = "\t", quote = FALSE, row.names = FALSE)
writeLines(capture.output(sessionInfo()), file.path(outdir, "sessionInfo.txt"))
cat("[p02-04] done ->", outdir, "\n")
cat("[p02-04] 提醒：spot != 单细胞。要落到细胞层面需做去卷积（RCTD/cell2location），\n")
cat("           且其可靠性完全取决于参考单细胞数据是否覆盖了组织里真实存在的所有类型。\n")
