#!/usr/bin/env Rscript
# ============================================
# 脚本名称：ch12_paired_power.R（合成算例 · R base，无第三方包）
# 功能描述：四个统计数字机制的教科书级复现入口
#   A. 配对 vs 独立（讲义演示 1a）：同一份合成数据，配对 t 检验 p = 5.07e-05，
#      按独立两样本处理 p = 0.601 —— 差四个数量级；漏识别配对 = 把最大信号源当噪声
#   B. 正态性检验陷阱（讲义演示 1c）：n = 4 的对数正态（明显偏态）数据，
#      shapiro.test 给出 p = 0.981 —— 小样本下正态性检验没有功效，
#      不能拿它当「t 还是 Wilcoxon」的自动开关
#   C. 功效表（讲义演示 6）：power.t.test(delta=1, sd=1, alpha=0.05)，
#      n = 3 功效仅 0.157，n = 10 为 0.562，达到 0.8 需每组 n = 17
#   D. 口径注记：R power.t.test 双侧默认 strict = FALSE，功效 = 非中心 t 的
#      上尾单侧概率（漏掉下尾项）；n = 2 时与双侧精确差 0.004（0.091 vs 0.095）。
#      讲义印刷值（0.091/0.157/.../0.649）即 R 该口径，本脚本照印并在 D 注明
# 服务章节：第 12 章 §12.4 概念与方法（p 值读法、功效）、§12.5 失效条件
#           第 1 条（不显著不等于无差异：n = 3 功效 16%，p 几乎不携带信息）
# 数据性质：【合成算例】全部为正态/对数正态伪随机数（set.seed 与讲义一致），
#   与任何真实样本无关，不得写成真实样本结果。
# 正文引用的输出：
#   1. 配对 p = 5.07e-05 vs 独立 p = 0.601（相差约四个数量级；讲义演示 1a）
#   2. shapiro.test 对 n = 4 对数正态数据 p = 0.981（「完全看不出不正态」）
#   3. 功效表 n = 2..12：0.091/0.157/0.222/0.286/0.347/0.406/0.461/0.513/
#      0.562/0.607/0.649；达 0.8 需 n = 17（讲义演示 6）
#   4. power.t.test 双侧 strict = FALSE 口径说明（n = 2：0.091 vs 双侧精确 0.095）
# 用法：Rscript demos/ch12_paired_power.R            # 打印全部算例
#       Rscript demos/ch12_paired_power.R --selftest # 断言关键输出
#       Rscript demos/ch12_paired_power.R --help
# 作者：lab_designer（任务 CH12_CASE_001）
# 日期：2026-11-04
# ============================================

usage <- function() {
  cat("用法: Rscript demos/ch12_paired_power.R [--selftest] [--help]\n")
  cat("  合成算例（R base，无第三方包），复现讲义 l0_06 演示 1a/1c/6 的印刷数字。\n")
}

## ---- 算例 A：配对 vs 独立（对齐讲义演示 1a，set.seed(11)） ----
case_paired_vs_indep <- function() {
  cat("\n[算例 A] 同一份合成数据：配对处理 vs 当成独立两样本（讲义演示 1a）\n")
  set.seed(11)
  before <- rnorm(8, mean = 10, sd = 3)              # 8 个个体处理前
  after  <- before + rnorm(8, mean = 1.2, sd = 0.5)  # 每个个体都升高约 1.2
  p_indep  <- t.test(before, after, var.equal = TRUE)$p.value
  p_paired <- t.test(before, after, paired = TRUE)$p.value
  cat(sprintf("  独立两样本 t 检验 : p = %.3g\n", p_indep))
  cat(sprintf("  配对 t 检验       : p = %.3g   <- 相差约 %.1f 个数量级\n",
              p_paired, abs(log10(p_indep) - log10(p_paired))))
  cat("  漏识别配对 = 把个体基线差异（最大信号源）算进组内误差，功效被稀释\n")
  invisible(list(p_indep = p_indep, p_paired = p_paired))
}

## ---- 算例 B：正态性检验在小样本下没有功效（对齐讲义演示 1c，set.seed(2026)） ----
case_shapiro_trap <- function() {
  cat("\n[算例 B] 用 shapiro.test 的 p 值当方法选择开关，n = 4 时会骗你（演示 1c）\n")
  set.seed(2026)
  b <- rlnorm(4, meanlog = 1.5, sdlog = 1)   # 明显偏态的对数正态数据
  p_shapiro <- shapiro.test(b)$p.value
  cat(sprintf("  对数正态样本 n = 4：shapiro.test p = %.3f —— 「完全看不出不正态」\n",
              p_shapiro))
  cat("  方法选择看数据生成机制与图，不看正态性检验的 p 值\n")
  invisible(list(p_shapiro = p_shapiro))
}

## ---- 算例 C：功效表（对齐讲义演示 6，power.t.test） ----
case_power_table <- function() {
  cat("\n[算例 C] 功效：delta = 1、sd = 1、alpha = 0.05（讲义演示 6）\n")
  ns <- 2:12
  pw <- sapply(ns, function(n) power.t.test(n = n, delta = 1, sd = 1)$power)
  cat("  n        :", paste(sprintf("%5d", ns), collapse = ""), "\n")
  cat("  power    :", paste(sprintf("%5.3f", pw), collapse = ""), "\n")
  n80 <- ceiling(power.t.test(power = 0.8, delta = 1, sd = 1)$n)
  cat(sprintf("  达 80%% 功效需每组 n = %d；n = 3 时功效仅 %.3f —— 真实差异也有 %.0f%% 概率漏检\n",
              n80, pw[ns == 3], 100 * (1 - pw[ns == 3])))
  cat("  → n = 3 下「p > 0.05 所以无差异」几乎不携带信息（失效条件 1）\n")
  invisible(list(pw = pw, n80 = n80))
}

## ---- 算例 D：power.t.test 的双侧口径（strict = FALSE） ----
case_power_convention <- function() {
  cat("\n[算例 D] 口径注记：R power.t.test 双侧默认 strict = FALSE\n")
  cat("  功效 = 非中心 t 的上尾单侧概率（不加上对应下尾项），讲义印刷值即此口径。\n")
  df <- 2 * 2 - 2
  ncp <- 1 / sqrt(2 / 2)
  crit <- qt(0.975, df)
  p_upper <- pt(crit, df, ncp, lower.tail = FALSE)          # power.t.test 口径
  p_twosided <- p_upper + pt(-crit, df, ncp)                # 双侧精确
  cat(sprintf("  n = 2：上尾口径 %.3f（= power.t.test 输出）vs 双侧精确 %.3f，差 %.3f\n",
              p_upper, p_twosided, p_twosided - p_upper))
  cat("  n 稍大该差值即缩小（n = 3 时 0.002，n = 10 时 < 0.001）；教材引用讲义表\n")
  cat("  时按 R 口径标注即可，两者都在「15.7%/16%」的叙述噪声内\n")
  invisible(list(p_upper = p_upper, p_twosided = p_twosided))
}

selftest <- function() {
  cat("\n[selftest] 断言关键输出（与讲义印刷值逐位对齐）...\n")
  ok <- TRUE
  check <- function(cond, msg) {
    cat(if (cond) "  PASS: " else "  FAIL: ", msg, "\n", sep = "")
    if (!cond) ok <<- FALSE
  }
  a <- case_paired_vs_indep()
  check(a$p_paired < 1e-4 && a$p_paired > 4e-5,
        sprintf("算例 A：配对 p = %.3g ∈ (4e-05, 1e-04)（讲义 5.07e-05）", a$p_paired))
  check(a$p_indep > 0.5 && a$p_indep < 0.7,
        sprintf("算例 A：独立 p = %.3g ∈ (0.5, 0.7)（讲义 0.601）", a$p_indep))
  b <- case_shapiro_trap()
  check(b$p_shapiro > 0.95,
        sprintf("算例 B：n = 4 对数正态 shapiro p = %.3f > 0.95（讲义 0.981）",
                b$p_shapiro))
  c_ <- case_power_table()
  check(abs(c_$pw[2] - 0.157) < 0.002,
        sprintf("算例 C：n = 3 功效 = %.3f ≈ 0.157（讲义口径）",
                c_$pw[2]))
  check(abs(c_$pw[9] - 0.562) < 0.002,
        sprintf("算例 C：n = 10 功效 = %.3f ≈ 0.562", c_$pw[9]))
  check(c_$n80 == 17, sprintf("算例 C：达 0.8 功效需 n = %d = 17", c_$n80))
  d <- case_power_convention()
  check(abs(d$p_upper - 0.091) < 0.001 && d$p_twosided > d$p_upper,
        sprintf("算例 D：n = 2 上尾口径 %.3f ≈ 0.091 且双侧精确更大（%.3f）",
                d$p_upper, d$p_twosided))
  cat(if (ok) "SELFTEST PASS\n" else "SELFTEST FAIL\n")
  invisible(ok)
}

main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  if ("--help" %in% args) { usage(); return(invisible(0L)) }
  if ("--selftest" %in% args) { quit(status = if (isTRUE(selftest())) 0L else 1L) }
  case_paired_vs_indep(); case_shapiro_trap(); case_power_table(); case_power_convention()
  cat("\n提示：以上全部为合成算例（伪随机数，set.seed 与讲义一致），不得写成真实样本结果。\n")
  invisible(0L)
}

main()
