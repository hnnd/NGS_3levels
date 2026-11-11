#!/usr/bin/env Rscript
# ============================================================
# 脚本名称：02_power_cells.R
# 功能描述：p02 §⑦-3 —— 稀有细胞类型的检出功效。
#           回答："欲以 <power> 的把握至少捕获 <k> 个占比 <prop> 的细胞类型，
#                  需要测多少个细胞？"
#           这是【实验设计阶段】的计算，测完再补是补不回来的。
# 环境    ：conda activate ngs_phd_sc（只用 R 自带 stats）
# 作者    ：王运生
# 日期    ：2026-08-29
#
# 用法：Rscript 02_power_cells.R [--prop 0.01] [--k 10] [--power 0.95] [--out <png>]
# ============================================================
set.seed(20260829)
argv <- commandArgs(trailingOnly = TRUE)
getopt <- function(f, d) { i <- which(argv == f); if (!length(i)) d else argv[i + 1] }
prop  <- as.numeric(getopt("--prop", "0.01"))
k     <- as.integer(getopt("--k", "10"))
power <- as.numeric(getopt("--power", "0.95"))
outpng<- getopt("--out", "results/p02/power_cells.png")
dir.create(dirname(outpng), showWarnings = FALSE, recursive = TRUE)

# 捕获数 X ~ Binomial(n, prop)；求最小 n 使 P(X >= k) >= power
prob_ge <- function(n, k, p) 1 - pbinom(k - 1, n, p)
n <- 10
while (prob_ge(n, k, prop) < power && n < 5e6) n <- n + 10
n_req <- n

cat(sprintf("目标细胞类型占比 : %.3f%%\n", prop * 100))
cat(sprintf("要求至少捕获     : %d 个\n", k))
cat(sprintf("要求把握         : %.0f%%\n", power * 100))
cat(sprintf("--> 需要测的细胞数: %d\n\n", n_req))

cat("与直觉的落差（本节的价值所在）：\n")
for (nn in sort(unique(c(round(k / prop), 1000, 2000, 5000, 10000)))) {
  cat(sprintf("  n = %6d  期望捕获 %5.1f 个  P(X>=%d) = %.3f\n",
              nn, nn * prop, k, prob_ge(nn, k, prop)))
}
cat(sprintf("\n注意 n = %d 时期望捕获恰好 %d 个，但把握只有 %.1f%% —— ",
            round(k / prop), k, prob_ge(round(k / prop), k, prop) * 100))
cat("期望值达标不等于把握达标。\n\n")
cat("两条限制（讲义 §⑦-3）：\n")
cat("  ① 本算式只管【捕获到】，不管【能不能达到统计显著】——\n")
cat("     后者还要叠一层样本数问题：捕获 1000 个稀有细胞但只有 2 个生物学重复，\n")
cat("     仍然做不了可信的组间比较（§⑦-2）。\n")
cat("  ② 预算固定时，组间比较优先【多个体 x 少细胞】；\n")
cat("     只有目标是【发现新细胞类型】时才该反过来。\n")

grid_n <- seq(100, max(3 * n_req, 5000), by = 50)
png(outpng, width = 900, height = 700, res = 150)
plot(grid_n, prob_ge(grid_n, k, prop), type = "l", lwd = 2, col = "#0072B2",
     xlab = "Number of cells sequenced", ylab = sprintf("P(capture >= %d cells)", k),
     main = sprintf("Detection power for a %.2f%% population", prop * 100))
abline(h = power, lty = 2, col = "grey40")
abline(v = n_req, lty = 2, col = "#D55E00")
legend("bottomright", bty = "n",
       legend = c(sprintf("target power = %.2f", power), sprintf("required n = %d", n_req)),
       col = c("grey40", "#D55E00"), lty = 2)
invisible(dev.off())
cat(sprintf("\n[p02-03] figure -> %s\n", outpng))
