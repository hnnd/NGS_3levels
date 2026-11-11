#!/usr/bin/env Rscript
# ============================================
# 脚本名称：ch03_na_propagation.R（合成算例 · R base，无第三方包）
# 功能描述：演示 R 中 NA 的「静默传播 / 静默丢弃」五种机制
#   A. 汇总传播：mean()/sum() 遇 NA 整体返回 NA；na.rm=TRUE 改用小样本量但不声张
#   B. 逻辑筛选静默吞 NA：`subset(df, x > 阈)` 中 NA 行被无声剔除，无警告；
#      此处演示整组（ctrl）被一行 NA 连锅端掉的极端形态；
#      而 base 的 df[条件, ] 写法更隐蔽——NA 行被换成一行全 NA 的幻影行
#   C. lm() 静默丢行：nobs < nrow 而无警告；na.action=na.fail 把它逼成显式报错
#   D. 排序静默缩容：sort() 默认 na.last=NA——NA 被直接删去，向量长度悄悄变短
#   E. 分组汇总传播：tapply(..., mean) 遇 NA 组整体返回 NA，污染下游汇总表
# 服务章节：第 3 章 §3.4 概念与方法（NA 的三值逻辑）、§3.5 失效条件第 3 条
#           （NA 在汇总与绘图中被静默丢弃或传播，样本量在图上悄悄变小）
# 数据性质：【合成算例】全部为固定常数构造，无随机数、无 RNG（故无需随机种子）；
#   与任何真实样本无关，不得写成真实样本结果。S1–S6 表达量为设例。
# 正文引用的输出：
#   1. mean(c(12.1, 11.4, NA)) = NA；na.rm=TRUE 得 11.75，但参与计算的只有 2 个数
#   2. subset(df, expr > 13)：6 行静默剩 3 行，ctrl 组整组消失且无警告；
#      df[df$expr > 13, ] 则把 NA 行换成一行全 NA 的幻影行（样本名也是 NA）
#   3. lm(expr ~ group) 的 nobs = 5 而 nrow = 6（na.action 记录了被丢行号，但不警告）
#   4. sort(c(3, 1, NA, 2)) 默认返回 1 2 3——NA 被静默删除，长度 4→3
#      （na.last=TRUE 才保留并排在末尾）
#   5. tapply 分组均值：ctrl 组为 NA（传播），na.rm 后 ctrl = 11.75（n 仅 2）
# 用法：Rscript demos/ch03_na_propagation.R            # 打印全部算例
#       Rscript demos/ch03_na_propagation.R --selftest # 断言关键输出
#       Rscript demos/ch03_na_propagation.R --help
# 作者：lab_designer（任务 CH03_CASE_001）
# 日期：2026-11-03
# ============================================

usage <- function() {
  cat("用法: Rscript demos/ch03_na_propagation.R [--selftest] [--help]\n")
  cat("  合成算例（无随机数），演示 NA 的静默传播与静默丢弃。\n")
}

# 合成表达量表（设例）：ctrl 组 S3 缺失
make_df <- function() {
  data.frame(
    sample = paste0("S", 1:6),
    group  = rep(c("ctrl", "trt"), each = 3L),
    expr   = c(12.1, 11.4, NA, 15.2, 14.8, 15.9)
  )
}

## ---- 算例 A：汇总传播 ----
case_summary_propagation <- function() {
  cat("\n[算例 A] mean()/sum() 遇 NA 即整体卡死；na.rm=TRUE 悄悄改用 2 个数\n")
  x <- c(12.1, 11.4, NA)                              # 合成：ctrl 组表达量
  cat("  x =", paste(x, collapse = ", "), "\n")
  cat("  mean(x)              =", format(mean(x)), "（NA 传播，结果不可用）\n")
  cat("  mean(x, na.rm=TRUE)  =", formatC(mean(x, na.rm = TRUE), format = "f", digits = 2),
      "（可用，但参与计算的只有", sum(!is.na(x)), "/", length(x), "个数）\n")
  cat("  sum(x) / sum(x, na.rm=TRUE) 同样：NA  vs ",
      formatC(sum(x, na.rm = TRUE), format = "f", digits = 1), "\n")
  invisible(list(mean_na = is.na(mean(x)), mean_rm = mean(x, na.rm = TRUE),
                 n_used = sum(!is.na(x)), n_total = length(x)))
}

## ---- 算例 B：条件筛选对 NA 的两种静默处理（subset 丢行 / [ 造幻影行） ----
case_filter_drop <- function() {
  cat("\n[算例 B] 条件含 NA 的两种静默后果：subset() 无声丢行；df[条件, ] 造全 NA 幻影行\n")
  df <- make_df()
  cat("  全表 nrow =", nrow(df), "（ctrl/trt 各 3 行）\n")
  keep <- df$expr > 13                                # 含 NA（S3）
  cat("  条件向量 df$expr > 13:", paste(keep, collapse = ", "), "  <- 第 3 个是 NA\n")
  sub <- subset(df, expr > 13)                        # NA 行被无声剔除，无警告
  cat("  subset() 后 nrow =", nrow(sub), "；剩余样本:", paste(sub$sample, collapse = ", "), "\n")
  cat("  剩余组分布（ctrl 被整组静默剔除，控制台无任何警告）:\n"); print(table(sub$group))
  brk <- df[keep, ]                                   # base 写法：NA 索引 -> 全 NA 幻影行
  cat("  df[keep, ] 后 nrow =", nrow(brk),
      "；样本名列:", paste(ifelse(is.na(brk$sample), "<NA>", brk$sample), collapse = ", "),
      "  <- 幻影行的样本名、表达量全是 NA\n")
  cat("  两种写法都不报错：前者让组悄悄消失，后者让一行假数据混进下游\n")
  invisible(list(n_all = nrow(df), n_kept = nrow(sub), n_brk = nrow(brk),
                 ctrl_left = sum(sub$group == "ctrl"),
                 phantom_all_na = all(is.na(brk[1, ]))))
}

## ---- 算例 C：lm() 静默丢行 ----
case_lm_drop <- function() {
  cat("\n[算例 C] lm() 默认 na.omit：nobs 比 nrow 少 1，不警告\n")
  df <- make_df()
  fit <- lm(expr ~ group, data = df)
  cat("  nrow(df) =", nrow(df), "；nobs(fit) =", nobs(fit),
      "；被丢行号:", paste(as.integer(fit$na.action), collapse = ", "), "\n")
  cat("  把缺失逼成显式报错的方法：lm(..., na.action = na.fail)\n")
  msg <- tryCatch(lm(expr ~ group, data = df, na.action = na.fail),
                  error = function(e) conditionMessage(e))
  cat("  na.fail 报错原文:", msg, "\n")
  invisible(list(nrow = nrow(df), nobs = nobs(fit),
                 dropped = as.integer(fit$na.action)))
}

## ---- 算例 D：排序静默缩容 ----
case_sort_na <- function() {
  cat("\n[算例 D] sort() 默认 na.last=NA：NA 被直接删去，长度悄悄变短\n")
  x <- c(3, 1, NA, 2)
  s_default <- sort(x)
  s_keep    <- sort(x, na.last = TRUE)
  cat("  x =", paste(x, collapse = ", "),
      " -> sort(x) =", paste(s_default, collapse = ", "),
      "（长度 ", length(x), " -> ", length(s_default), "，NA 无声消失）\n", sep = "")
  cat("  sort(x, na.last=TRUE) =", paste(s_keep, collapse = ", "), "（显式要求才保留，排末尾）\n")
  invisible(list(sorted_default = s_default, sorted_keep = s_keep))
}

## ---- 算例 E：分组汇总传播 ----
case_group_summary <- function() {
  cat("\n[算例 E] tapply 分组均值：NA 组把整张汇总表拖成 NA\n")
  df <- make_df()
  g_mean  <- tapply(df$expr, df$group, mean)
  g_mean2 <- tapply(df$expr, df$group, mean, na.rm = TRUE)
  g_n     <- tapply(!is.na(df$expr), df$group, sum)
  out <- data.frame(
    group        = names(g_mean),
    mean_default = as.numeric(g_mean),
    mean_na.rm   = as.numeric(g_mean2),
    n_used       = as.numeric(g_n)
  )
  print(out, row.names = FALSE)
  cat("  默认汇总下 ctrl = NA（传播到下游任何用到它的计算）；na.rm 后 ctrl =",
      formatC(g_mean2["ctrl"], format = "f", digits = 2),
      "但 n 只有", g_n["ctrl"], "——图上柱子的高度与样本量脱节\n")
  invisible(list(ctrl_default = unname(g_mean["ctrl"]),
                 ctrl_rm = unname(g_mean2["ctrl"]),
                 ctrl_n = unname(g_n["ctrl"])))
}

selftest <- function() {
  cat("\n[selftest] 断言关键输出 ...\n")
  ok <- TRUE
  check <- function(cond, msg) {
    cat(if (cond) "  PASS: " else "  FAIL: ", msg, "\n", sep = "")
    if (!cond) ok <<- FALSE
  }
  a <- case_summary_propagation()
  check(isTRUE(a$mean_na), "算例 A：mean 遇 NA 返回 NA（传播）")
  check(abs(a$mean_rm - 11.75) < 1e-9 && a$n_used == 2L && a$n_total == 3L,
        "算例 A：na.rm 后 11.75，但只用了 2/3 个数")
  b <- case_filter_drop()
  check(b$n_all == 6L && b$n_kept == 3L && b$ctrl_left == 0L,
        "算例 B：subset() 后 6 行静默剩 3 行，ctrl 组整组消失")
  check(b$n_brk == 4L && isTRUE(b$phantom_all_na),
        "算例 B：df[keep, ] 造出一行全 NA 幻影行")
  c_ <- case_lm_drop()
  check(c_$nrow == 6L && c_$nobs == 5L && identical(c_$dropped, 3L),
        "算例 C：nobs=5 < nrow=6，被丢行号 3，无警告")
  d <- case_sort_na()
  check(identical(d$sorted_default, c(1, 2, 3)) && length(d$sorted_default) == 3L,
        "算例 D：sort 默认把 NA 删去，长度 4→3")
  check(identical(d$sorted_keep, c(1, 2, 3, NA)),
        "算例 D：na.last=TRUE 才保留并排末尾")
  e <- case_group_summary()
  check(is.na(e$ctrl_default) && abs(e$ctrl_rm - 11.75) < 1e-9 && e$ctrl_n == 2,
        "算例 E：ctrl 组默认 NA、na.rm 后 11.75（n=2）")
  cat(if (ok) "SELFTEST PASS\n" else "SELFTEST FAIL\n")
  invisible(ok)
}

main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  if ("--help" %in% args) { usage(); return(invisible(0L)) }
  if ("--selftest" %in% args) { quit(status = if (isTRUE(selftest())) 0L else 1L) }
  case_summary_propagation(); case_filter_drop(); case_lm_drop()
  case_sort_na(); case_group_summary()
  cat("\n提示：以上全部为合成算例（无随机数）；对策是出图/出表前先核对：\n")
  cat("  nrow(df) 与 sum(complete.cases(df)) 是否相等、nobs() 与样本量是否相等。\n")
  invisible(0L)
}

main()
