#!/usr/bin/env Rscript
# ============================================
# 脚本名称：ch13_batch_pca.R（合成算例 · R base，无第三方包）
# 功能描述：批次效应在 PCA 上的形态——平衡区组 vs 完全混杂的逐位复现
#   固化 l0_06_stats 讲义「演示 5」（set.seed(1234)，代码与讲义逐行一致，
#   仅去掉画图语句、保留 PC1/PC2 方差占比输出）：
#   - 平衡设计（每批 2 对照 + 2 处理）：PC1 ≈ 71%，批次沿 PC1、处理沿
#     另一方向分开，二者可拆 —— 批次可作协变量进 design 公式
#   - 混杂设计（批次 == 处理组）：PC1 ≈ 82%，批次与处理沿同一方向同样分开，
#     无法判断 PC1 上的分离是处理还是批次 —— 信息在采样时就没采到，
#     任何事后「去批次」软件都无法分离（失效条件 2 的几何面；
#     代数面见 demos/ch13_design_matrix_rank.py）
# 服务章节：第 13 章 §13.4「批次与区组」、§13.5 失效条件 2；
#           承接第 12 章 §12.4.9「PCA 不是检验」（PCA 只诊断、不分离）
# 数据性质：【合成算例】全部为正态伪随机数（set.seed(1234) 与讲义一致），
#   与任何真实样本无关，不得写成真实样本结果。
# 正文引用的输出：
#   1. 平衡设计 PC1/PC2 方差占比（讲义印刷值 ≈ 71% / 13.8%）
#   2. 混杂设计 PC1/PC2 方差占比（讲义印刷值 ≈ 82% / 3.3%）
#   3. 两个判读要点：平衡时批次与处理各占一个方向；混杂时二者共线、
#      PCA 分离无法归因（结合 design_matrix_rank 的秩亏结论）
# 环境注记：本机 R 4.5.2 现跑；课程 yml 为 r-base=4.3.1，
#   4.3.1 下的逐位复跑标 unverified（与 CH12/EXPERT 口径一致）。
# 用法：Rscript demos/ch13_batch_pca.R            # 打印两个设计的 PCA 占比
#       Rscript demos/ch13_batch_pca.R --selftest # 断言与讲义印刷值一致
#       Rscript demos/ch13_batch_pca.R --help
# 作者：lab_designer（任务 CH13_CASE_001）
# 日期：2026-11-04
# ============================================

usage <- function() {
  cat("用法: Rscript demos/ch13_batch_pca.R [--selftest] [--help]\n")
  cat("  合成算例（R base，无第三方包），复现讲义 l0_06 演示 5 的 PCA 方差占比。\n")
  cat("  参数：无（n_gene/n_samp/种子与讲义演示 5 固定一致，保证逐位复现）\n")
}

## ---- 讲义演示 5 的 PCA 计算（去画图版；代码逐行同 l0_06_stats §4 演示 5） ----
batch_pca <- function() {
  set.seed(1234)
  n_gene <- 2000; n_samp <- 8
  group      <- rep(c("A", "B"), each  = 4)     # 处理组
  batch_bal  <- rep(c("B1", "B2"), times = 4)   # 平衡设计：每批 2A + 2B
  batch_cnf  <- rep(c("B1", "B2"), each  = 4)   # 混杂设计：批次 == 处理组

  base  <- rnorm(n_gene, 8, 2)                                  # 基因基线表达
  g_eff <- c(rnorm(200, 1.2, 0.3), rep(0, n_gene - 200))        # 200 个基因响应处理
  b_eff <- rnorm(n_gene, 0, 1.0)                                # 批次给每个基因一个偏移
  noise <- matrix(rnorm(n_gene * n_samp, sd = 0.3), n_gene, n_samp)
  mk <- function(bt) matrix(base, n_gene, n_samp) +
          outer(g_eff, as.integer(group == "B")) +
          outer(b_eff, as.integer(bt == "B2")) + noise

  vp <- sapply(c("balanced", "confounded"), function(nm) {
    bt <- if (nm == "balanced") batch_bal else batch_cnf
    pc <- prcomp(t(mk(bt)), scale. = FALSE)
    100 * pc$sdev^2 / sum(pc$sdev^2)
  })
  colnames(vp) <- c("balanced", "confounded")
  rownames(vp) <- paste0("PC", 1:n_samp)
  vp
}

run_demo <- function() {
  vp <- batch_pca()
  cat("\n[讲义演示 5 现跑] 批次效应在 PCA 上长什么样（合成算例，set.seed(1234)）\n")
  cat(sprintf("  平衡区组设计（每批 2 对照 + 2 处理）：PC1 = %.1f%%，PC2 = %.1f%%\n",
              vp[1, "balanced"], vp[2, "balanced"]))
  cat("    → 批次沿 PC1 分开、处理沿另一方向分开：两个效应各占一个方向，可拆开；\n")
  cat("      把 batch 写进 design 公式即可剥离批次主效应\n")
  cat(sprintf("  完全混杂设计（批次 == 处理组）      ：PC1 = %.1f%%，PC2 = %.1f%%\n",
              vp[1, "confounded"], vp[2, "confounded"]))
  cat("    → 批次与处理沿同一方向、同样地分开：无法判断 PC1 的分离是处理还是批次；\n")
  cat("      区分二者的信息在采样时不存在，事后去批次软件救不了（失效条件 2）\n")
  cat("  判读边界：PCA 只诊断、不分离（§12.4.9）；「可拆 / 不可拆」的代数判据是\n")
  cat("    设计矩阵秩（demos/ch13_design_matrix_rank.py）\n")
  invisible(vp)
}

selftest <- function() {
  cat("\n[selftest] 断言与讲义演示 5 印刷值一致...\n")
  ok <- TRUE
  check <- function(cond, msg) {
    cat(if (cond) "  PASS: " else "  FAIL: ", msg, "\n", sep = "")
    if (!cond) ok <<- FALSE
  }
  vp <- run_demo()
  check(abs(vp[1, "balanced"] - 70.8) < 0.5 && abs(vp[2, "balanced"] - 13.8) < 0.5,
        sprintf("平衡设计 PC1/PC2 = %.1f%%/%.1f%% ≈ 讲义 70.8%%/13.8%%",
                vp[1, "balanced"], vp[2, "balanced"]))
  check(abs(vp[1, "confounded"] - 82.0) < 0.5 && abs(vp[2, "confounded"] - 3.3) < 0.5,
        sprintf("混杂设计 PC1/PC2 = %.1f%%/%.1f%% ≈ 讲义 82.0%%/3.3%%",
                vp[1, "confounded"], vp[2, "confounded"]))
  check(vp[1, "confounded"] > vp[1, "balanced"],
        "混杂设计 PC1 占比高于平衡设计（处理与批次共线 → 单一主方向）")
  cat(if (ok) "SELFTEST PASS\n" else "SELFTEST FAIL\n")
  invisible(ok)
}

main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  if ("--help" %in% args) { usage(); return(invisible(0L)) }
  if ("--selftest" %in% args) { quit(status = if (isTRUE(selftest())) 0L else 1L) }
  run_demo()
  cat("\n提示：以上全部为合成算例（伪随机数，set.seed 与讲义一致），不得写成真实样本结果。\n")
  invisible(0L)
}

main()
