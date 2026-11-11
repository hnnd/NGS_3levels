#!/usr/bin/env Rscript
# ============================================================
# 脚本名称：02_pseudobulk_de.R
# 功能描述：p02 §⑦-2 的落地 —— 同一份数据、同一个比较，分别用
#           ① FindMarkers（把细胞当独立样本 = 伪重复）
#           ② pseudobulk + DESeq2（把样本当独立样本 = 诚实做法）
#           跑一遍，输出两套结果与显著基因数对比表。
#           讲义预期：② 的显著基因数比 ① 少 1-2 个数量级，这是纠正不是损失。
# 环境    ：conda activate ngs_phd_sc（需 Seurat + DESeq2）
# 作者    ：王运生
# 日期    ：2026-08-29
#
# 用法：Rscript 02_pseudobulk_de.R --rds <integrated.rds> \
#          --sample-col sample --celltype-col celltype --condition-col condition \
#          [--celltype <只做某一类>] [--min-cells 10] --outdir <out>
#
# 关键：pseudobulk 必须对【原始 counts 求和】，不能用 AverageExpression()
#       取均值/归一化值 —— 那会得到非整数并被 DESeq2 拒绝（⑨-E9），
#       更重要的是它把"这个样本有多少细胞"这一信息扔掉了。
# ============================================================
suppressPackageStartupMessages({
  library(Seurat); library(DESeq2); library(Matrix)
})
set.seed(20260829)

argv <- commandArgs(trailingOnly = TRUE)
getopt <- function(f, d = NULL) { i <- which(argv == f); if (!length(i)) d else argv[i + 1] }
rds_f    <- getopt("--rds");            if (is.null(rds_f)) stop("必须给 --rds")
sam_col  <- getopt("--sample-col", "sample")
ct_col   <- getopt("--celltype-col", "celltype")
cond_col <- getopt("--condition-col", "condition")
only_ct  <- getopt("--celltype", NA)
min_cells<- as.integer(getopt("--min-cells", "10"))
outdir   <- getopt("--outdir", "results/p02/de")
dir.create(outdir, showWarnings = FALSE, recursive = TRUE)

obj <- readRDS(rds_f)
md  <- obj@meta.data
for (cc in c(sam_col, ct_col, cond_col)) {
  if (!cc %in% colnames(md)) stop("meta.data 缺列: ", cc)
}
DefaultAssay(obj) <- "RNA"          # Harmony 只改 reduction，差异表达必须回到表达 assay（⑨-E5）
cts_all <- GetAssayData(obj, assay = "RNA", layer = "counts")

cell_types <- if (!is.na(only_ct)) only_ct else sort(unique(as.character(md[[ct_col]])))
summary_tab <- data.frame()

for (ct in cell_types) {
  keep <- which(as.character(md[[ct_col]]) == ct)
  if (length(keep) < 3 * min_cells) { message("跳过 ", ct, "（细胞太少）"); next }
  message("=== ", ct, "：", length(keep), " cells ===")
  sub <- obj[, keep]
  sub_md <- md[keep, , drop = FALSE]

  ## ---------- ① FindMarkers：细胞当样本（伪重复） ----------
  Idents(sub) <- factor(sub_md[[cond_col]])
  lv <- levels(Idents(sub))
  if (length(lv) != 2) { message("  condition 不是两水平，跳过"); next }
  fm <- tryCatch(FindMarkers(sub, ident.1 = lv[2], ident.2 = lv[1],
                             logfc.threshold = 0, min.pct = 0.1, verbose = FALSE),
                 error = function(e) { message("  FindMarkers 失败: ", conditionMessage(e)); NULL })
  n_fm <- if (is.null(fm)) NA_integer_ else sum(fm$p_val_adj < 0.05, na.rm = TRUE)

  ## ---------- ② pseudobulk：按 (样本 x 细胞类型) 求和原始 counts ----------
  grp <- factor(as.character(sub_md[[sam_col]]))
  idx <- sparse.model.matrix(~ 0 + grp)                 # 细胞 -> 样本 的 0/1 指示矩阵
  colnames(idx) <- levels(grp)
  pb <- as.matrix(cts_all[, keep, drop = FALSE] %*% idx)  # 求和，不是取均值
  n_cell <- as.vector(table(grp)[colnames(pb)])
  pb <- pb[, n_cell >= min_cells, drop = FALSE]           # 细胞过少的样本直接剔除（⑨-E6）
  if (ncol(pb) < 4) { message("  可用样本 < 4，无法做 pseudobulk 推断"); next }

  cd <- unique(sub_md[, c(sam_col, cond_col)])
  rownames(cd) <- as.character(cd[[sam_col]])
  cd <- cd[colnames(pb), , drop = FALSE]
  cd[[cond_col]] <- factor(cd[[cond_col]], levels = lv)
  stopifnot(all(pb %% 1 == 0))                            # 主动拦截"喂了非整数"（⑨-E9）

  dds <- DESeqDataSetFromMatrix(pb, cd, as.formula(paste("~", cond_col)))
  dds <- dds[rowSums(counts(dds)) >= 10, ]
  dds <- DESeq(dds, quiet = TRUE)
  res <- as.data.frame(results(dds, contrast = c(cond_col, lv[2], lv[1])))
  res$gene <- rownames(res)
  n_pb <- sum(res$padj < 0.05, na.rm = TRUE)

  safe <- gsub("[^A-Za-z0-9_]", "_", ct)
  if (!is.null(fm)) write.table(data.frame(gene = rownames(fm), fm),
                                file.path(outdir, paste0(safe, "_findmarkers.tsv")),
                                sep = "\t", quote = FALSE, row.names = FALSE)
  write.table(res, file.path(outdir, paste0(safe, "_pseudobulk.tsv")),
              sep = "\t", quote = FALSE, row.names = FALSE)

  summary_tab <- rbind(summary_tab, data.frame(
    cell_type = ct, n_cells = length(keep), n_samples = ncol(pb),
    sig_findmarkers = n_fm, sig_pseudobulk = n_pb,
    ratio = ifelse(is.na(n_fm) || n_pb == 0, NA, round(n_fm / max(n_pb, 1), 1))))
}

write.table(summary_tab, file.path(outdir, "de_comparison_summary.tsv"),
            sep = "\t", quote = FALSE, row.names = FALSE)
print(summary_tab)
cat("\n[p02-02] FindMarkers 的 n 是细胞数，pseudobulk 的 n 是样本数。\n")
cat("[p02-02] 两者差 1-2 个数量级是正常的；组间比较请报告 pseudobulk 的结果。\n")
cat("[p02-02] done ->", outdir, "\n")
