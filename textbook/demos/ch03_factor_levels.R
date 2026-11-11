#!/usr/bin/env Rscript
# ============================================
# 脚本名称：ch03_factor_levels.R（合成算例 · R base，无第三方包）
# 功能描述：演示「因子 levels 仲裁图表出场顺序与回归对照组」的四个机制
#   A. 不设 levels：离散类目一律按 levels 顺序出场，默认 levels = 字母序
#      → BUSCO 四类被排成 Duplicated→Fragmented→Missing→Single-copy（生物逻辑倒置）
#   B. 标签命名改变字母序 → 同一组数据、同一个 lm()，对照组悄悄换人、系数符号反转
#   C. levels(f) <- 按位置改名（不是按值改名）→ 标签与数据错位，结论方向反转而不报错
#   D. 筛选后 levels 幽灵残留 → levels 与 table() 里残留计数为 0 的类目；图上是否出现取决于离散标度 drop（默认 TRUE 不显示）
# 服务章节：第 3 章 §3.4 概念与方法（因子）、§3.5 失效条件第 1 条
#           （因子水平按字母序决定图例顺序与回归的对照组，改名不改水平就改变结论方向）
# 数据性质：【合成算例】全部为固定常数构造，无随机数、无 RNG（故无需随机种子）；
#   与任何真实菌株 / 真实样本无关，不得写成真实样本结果。
#   B/C 例组均值 10.0 / 13.0 为设例；A 例百分比与 02_plot_assembly_metrics.R
#   --demo 的 Canu 列一致（该脚本头注明「数值取自讲义示例，仅用于跑通流程」）。
# 正文引用的输出：
#   1. BUSCO 默认 levels = c("Duplicated","Fragmented","Missing","Single-copy")，
#      Single-copy 从生物逻辑第 1 位被排到第 4 位；显式 levels 后回到第 1 位
#   2. 组均值差恒为 +3.0：参考组换人后 lm 系数由 +3.0 变 −3.0（数据一个数都没变）
#   3. levels() 按位置改名后「ctrl」标签承载的组均值由 10.0 变成 13.0
#   4. 筛选掉 ctrl 后 nlevels 仍为 2、table() 中 ctrl 计数为 0（空类目）；droplevels 后剩 1 个水平
# 用法：Rscript demos/ch03_factor_levels.R            # 打印全部算例
#       Rscript demos/ch03_factor_levels.R --selftest # 断言关键输出
#       Rscript demos/ch03_factor_levels.R --help
# 作者：lab_designer（任务 CH03_CASE_001）
# 日期：2026-11-03
# ============================================

usage <- function() {
  cat("用法: Rscript demos/ch03_factor_levels.R [--selftest] [--help]\n")
  cat("  合成算例（无随机数），演示因子 levels 对顺序/对照组的仲裁作用。\n")
}

fmt_num <- function(x) formatC(x, format = "f", digits = 1)

## ---- 算例 A：BUSCO 四类的字母序倒置 ----
case_busco_order <- function() {
  cat("\n[算例 A] BUSCO 类目：默认 levels（字母序）vs 显式 levels（生物逻辑序）\n")
  cats <- c("Single-copy", "Duplicated", "Fragmented", "Missing")
  pct  <- c(97.2, 0.8, 0.6, 1.4)   # 设例：与 02_plot_assembly_metrics.R --demo 的 Canu 列一致
  f_alpha  <- factor(cats)                            # 默认：levels = sort(唯一值)
  f_biolog <- factor(cats, levels = cats)             # 显式：按 优→劣 绑定
  cat("  默认 levels   :", paste(levels(f_alpha), collapse = " -> "), "\n")
  cat("  显式 levels   :", paste(levels(f_biolog), collapse = " -> "), "\n")
  pos_alpha  <- match("Single-copy", levels(f_alpha))
  pos_biolog <- match("Single-copy", levels(f_biolog))
  cat("  'Single-copy' 出场位置: 默认 =", pos_alpha, "（被排到末位）; 显式 =", pos_biolog, "（回到首位）\n")
  # barplot(table()) 与 ggplot2 离散轴同样按 levels 顺序排布：
  cat("  table(默认因子) 的类目顺序（= 柱序/图例序）:\n")
  print(table(f_alpha))
  invisible(list(alpha = levels(f_alpha), pos_alpha = pos_alpha,
                 pos_biolog = pos_biolog, pct = pct))
}

## ---- 算例 B：字母序换掉回归对照组，系数符号反转（数据不变） ----
case_reference_flip <- function() {
  cat("\n[算例 B] 同一组数据、同一个 lm()：标签命名决定对照组，系数符号跟着反\n")
  n_per <- 4L
  y <- c(rep(10.0, n_per), rep(13.0, n_per))          # 合成：ctrl 均值 10.0、trt 均值 13.0（无噪声）
  ref_coef <- function(labels) {
    f <- factor(rep(labels, each = n_per))            # 默认 levels = 字母序
    fit <- lm(y ~ f)
    c(reference = levels(f)[1L], coef_trt_group = unname(coef(fit)[2L]))
  }
  r1 <- ref_coef(c("ctrl", "trt"))
  cat("  标签 c(\"ctrl\",\"trt\")      -> 参考组 =", r1["reference"],
      "; 非参考组系数 =", fmt_num(as.numeric(r1["coef_trt_group"])), "\n")
  r2 <- ref_coef(c("b_ctrl", "a_trt"))                # 命名带前缀：字母序把处理组排到对照组前面
  cat("  标签 c(\"b_ctrl\",\"a_trt\")  -> 参考组 =", r2["reference"],
      "; 非参考组系数 =", fmt_num(as.numeric(r2["coef_trt_group"])), "\n")
  cat("  两组数据完全相同（均值差恒为 13.0 - 10.0 = +3.0），仅系数所属标签换人 -> 解读方向反转\n")
  # 显式 levels 恢复对照组：
  f_ok <- factor(rep(c("b_ctrl", "a_trt"), each = n_per), levels = c("b_ctrl", "a_trt"))
  cat("  显式 levels=c(\"b_ctrl\",\"a_trt\") -> 参考组 =", levels(f_ok)[1L],
      "; 系数 =", fmt_num(unname(coef(lm(y ~ f_ok))[2L])), "（方向恢复）\n")
  invisible(list(r1 = r1, r2 = r2))
}

## ---- 算例 C：levels() 按位置改名，标签与数据错位 ----
case_positional_rename <- function() {
  cat("\n[算例 C] levels(f) <- c(...) 按【位置】改名：数据没动，标签换了主人\n")
  n_per <- 4L
  y <- c(rep(10.0, n_per), rep(13.0, n_per))
  f <- factor(rep(c("ctrl", "trt"), each = n_per), levels = c("ctrl", "trt"))
  means_before <- tapply(y, f, mean)
  cat("  改名前组均值: ctrl =", fmt_num(means_before["ctrl"]),
      ", trt =", fmt_num(means_before["trt"]), "\n")
  levels(f) <- c("trt", "ctrl")                       # 原代号 1（ctrl 的数据）现在叫 "trt"
  means_after <- tapply(y, f, mean)
  cat("  改名后组均值: trt =", fmt_num(means_after["trt"]),
      ", ctrl =", fmt_num(means_after["ctrl"]), "  <- 'ctrl' 标签现在承载处理组数据\n")
  fit <- lm(y ~ f)
  cat("  lm 系数: 参考组 =", levels(f)[1L], "; 非参考组系数 =",
      fmt_num(unname(coef(fit)[2L])),
      "  <- 数值仍是 +3.0，但读作『ctrl 比 trt 高』，结论方向与算例 B 相反\n")
  invisible(list(ctrl_before = unname(means_before["ctrl"]),
                 ctrl_after  = unname(means_after["ctrl"]),
                 coef = unname(coef(fit)[2L])))
}

## ---- 算例 D：筛选后 levels 幽灵残留 ----
case_ghost_levels <- function() {
  cat("\n[算例 D] 筛掉 ctrl 后，levels 字典仍残留该类目 -> levels/table() 残留计数为 0 的类目（ggplot2 离散标度默认 drop=TRUE 不画出）\n")
  f <- factor(rep(c("ctrl", "trt"), each = 4L))
  f_sub <- f[f != "ctrl"]                             # 逻辑筛选：ctrl 行已剔除
  cat("  筛选后 nlevels =", nlevels(f_sub),
      "; table:", paste(names(table(f_sub)), as.integer(table(f_sub)), sep = "=", collapse = ", "),
      "（ctrl 计数 0 但类目仍在）\n")
  f_drop <- droplevels(f_sub)
  cat("  droplevels 后 nlevels =", nlevels(f_drop),
      "; table:", paste(names(table(f_drop)), as.integer(table(f_drop)), sep = "=", collapse = ", "), "\n")
  invisible(list(nlevels_before = nlevels(f_sub),
                 ctrl_count = as.integer(table(f_sub)["ctrl"]),
                 nlevels_after = nlevels(f_drop)))
}

selftest <- function() {
  cat("\n[selftest] 断言关键输出 ...\n")
  ok <- TRUE
  check <- function(cond, msg) {
    cat(if (cond) "  PASS: " else "  FAIL: ", msg, "\n", sep = "")
    if (!cond) ok <<- FALSE
  }
  a <- case_busco_order()
  check(identical(a$alpha, sort(a$alpha)), "算例 A：默认 levels 恰为字母序")
  check(a$pos_alpha == 4L && a$pos_biolog == 1L, "算例 A：Single-copy 默认排第 4、显式排第 1")
  check(abs(sum(a$pct) - 100) < 1e-9, "算例 A：BUSCO 设例四档合计 100%")
  b <- case_reference_flip()
  check(abs(as.numeric(b$r1["coef_trt_group"]) - 3.0) < 1e-9,
        "算例 B：标签 ctrl/trt 时系数 = +3.0（trt - ctrl）")
  check(abs(as.numeric(b$r2["coef_trt_group"]) - (-3.0)) < 1e-9,
        "算例 B：字母序换人后系数 = -3.0（数据未变）")
  c_ <- case_positional_rename()
  check(abs(c_$ctrl_before - 10.0) < 1e-9 && abs(c_$ctrl_after - 13.0) < 1e-9,
        "算例 C：位置改名后 'ctrl' 标签均值 10.0 -> 13.0")
  check(abs(c_$coef - 3.0) < 1e-9, "算例 C：系数数值仍是 +3.0，仅解读方向反转")
  d <- case_ghost_levels()
  check(d$nlevels_before == 2L && d$ctrl_count == 0L && d$nlevels_after == 1L,
        "算例 D：筛选后 2 水平（ctrl=0）、droplevels 后 1 水平")
  cat(if (ok) "SELFTEST PASS\n" else "SELFTEST FAIL\n")
  invisible(ok)
}

main <- function() {
  args <- commandArgs(trailingOnly = TRUE)
  if ("--help" %in% args) { usage(); return(invisible(0L)) }
  if ("--selftest" %in% args) { quit(status = if (isTRUE(selftest())) 0L else 1L) }
  case_busco_order(); case_reference_flip(); case_positional_rename(); case_ghost_levels()
  cat("\n提示：以上全部为合成算例（无随机数），组均值 10.0/13.0 为设例；\n")
  cat("      对策只有一条：离散类目一律显式 factor(x, levels = c(...)) 绑定出场顺序。\n")
  invisible(0L)
}

main()
