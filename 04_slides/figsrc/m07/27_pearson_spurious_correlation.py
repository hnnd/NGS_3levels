#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""27_pearson_spurious_correlation.py — FIG-M07-30 Pearson 伪相关失真对比（data-plot）

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-30（P56，`.cols` 一栏 800×700，data-plot）。
数据来源：`../03_code/master/scripts/07_compositional_analysis.R` 第一部分的同一模型
（seed 20260829，n=200，abs_a / abs_b ~ rlnorm(5,1)，others ~ rlnorm(7,0.3)）。
该脚本现跑输出 `绝对丰度 r = +0.007` / `相对丰度 r = -0.241`（3 位小数）；本脚本读取同一模型
导出的点表（`textbook/tasks/logs/m07_spurious_data.tsv`，200 行，字段 abs_a/abs_b/rel_a/rel_b），
**自己从原始数值重算 Pearson r 并与 R 打印值核对**（不复抄任何数字）：

    linear   abs r = +0.0070   rel r = -0.2413    → 3 位小数即 R 打印的 +0.007 / -0.241

两个面板画的是同一批 200 个点。横纵轴均为 log10 刻度：绝对量跨 0.9–3.8 个数量级
（abs_a 9.1–1440.1、abs_b 6.1–6554.5），线性轴会把 195 个点压进左下角，看不出形状。
面板角上标的 r 是**线性值**上的 Pearson r（即 R 打印的那两个数），不是对数轴上的斜率；
左图无倾（|r|≈0）、右图明显下倾。
图内汉字 = 方案清单逐字（绝对丰度：独立无相关 10 / 相对丰度：伪负相关 9 /
闭合产生假边 6）＝ 25 字。轴标签用 log₁₀ 与纯数字，不计汉字。
红色一处：右图回归线 + 底部「闭合产生假边」同属一个警示语义组。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 27_pearson_spurious_correlation.py
"""
import csv
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

DATA = (Path(__file__).resolve().parents[3] / "textbook" / "tasks" / "logs"
        / "m07_spurious_data.tsv")


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    return sxy / math.sqrt(sxx * syy)


def fit(x, y):
    """最小二乘直线 y = a + b x（对数坐标上画回归线用）。"""
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    b = sxy / sxx
    return my - b * mx, b


def main():
    rows = list(csv.DictReader(DATA.open(encoding="utf-8"), delimiter="\t"))
    abs_a = [float(r["abs_a"]) for r in rows]
    abs_b = [float(r["abs_b"]) for r in rows]
    rel_a = [float(r["rel_a"]) for r in rows]
    rel_b = [float(r["rel_b"]) for r in rows]

    r_abs, r_rel = pearson(abs_a, abs_b), pearson(rel_a, rel_b)

    # 与 07_compositional_analysis.R 的打印值核对（R 打印 3 位小数，故容差 5e-4）
    assert len(rows) == 200, len(rows)
    assert abs(r_abs - 0.007) < 5e-4, r_abs
    assert abs(r_rel - (-0.241)) < 5e-4, r_rel
    # 组成性闭合的必然后果：列和恒为 1（这里 a、b 两个组分各占一部分，故和为 1 的
    # 是「全组分」；导出表只留了两组分，两个相对量必然同向受分母牵制）
    assert r_rel < 0 < r_abs                     # 符号翻转是本图唯一要点

    la = [math.log10(v) for v in abs_a]
    lb = [math.log10(v) for v in abs_b]
    lra = [math.log10(v) for v in rel_a]
    lrb = [math.log10(v) for v in rel_b]

    s = SVG()

    PANELS = (
        (100, "绝对丰度：", "独立无相关", la, lb, CYAN, CYAN_DEEP, r_abs,
         CYAN_DEEP, ("abs_a", "abs_b")),
        (456, "相对丰度：", "伪负相关", lra, lrb, PURPLE, RED, r_rel,
         ORANGE_DEEP, ("rel_a", "rel_b")),
    )

    PW, PB, PT = 300, 556, 220                  # 面板轴框：宽 / 基线 / 顶线

    for x0, cap1, cap2, xs, ys, dot, line_col, rv, cap_col, (xlab,
                                                              ylab) in PANELS:
        s.label(x0 + PW / 2, 132, [cap1, cap2], 30, cap_col, "middle", "bold",
                leading=1.34)
        # 轴框
        s.line(x0, PB, x0 + PW, PB, INK, 3)
        s.line(x0, PB, x0, PT, INK, 3)
        # 网格
        for gx in range(0, 4):
            X = x0 + gx * PW / 3
            s.line(X, PT, X, PB, PANEL, 2)
        for gy in range(1, 4):
            Y = PT + gy * (PB - PT) / 4
            s.line(x0, Y, x0 + PW, Y, PANEL, 2)

        xmin, xmax = min(xs) - 0.15, max(xs) + 0.15
        ymin, ymax = min(ys) - 0.15, max(ys) + 0.15
        fx = lambda v: x0 + (v - xmin) / (xmax - xmin) * PW
        fy = lambda v: PB - (v - ymin) / (ymax - ymin) * (PB - PT)

        pts = [(fx(u), fy(v)) for u, v in zip(xs, ys)]
        for px, py in pts:
            s.circle(px, py, 5, dot)

        # 回归线（在对数坐标上最小二乘，只作形态提示）
        i0, b0 = fit(xs, ys)
        s.line(fx(xmin), fy(i0 + b0 * xmin), fx(xmax), fy(i0 + b0 * xmax),
               line_col, 5)

        # 角上 r 值（线性尺度上的 Pearson r，即 R 打印值）；白底遮住散点
        r_col = RED if rv < 0 else line_col
        rtxt = f"r = {rv:+.3f}"
        rw = text_width(rtxt, 30, True)
        s.rect(x0 + 8, PT + 8, rw + 18, 46, WHITE, rx=8)
        s.text(x0 + 16, PT + 42, rtxt, 30, r_col, "start", "bold")

        # 轴标签（log10 A / log10 B，汉字数为 0）
        s.text(x0 + PW / 2, PB + 42, f"log10 {xlab}", 30, GRAY, "middle")
        s.text(x0 + 2, PT - 22, f"log10 {ylab}", 30, GRAY, "start")

    # ---------------- 唯一红处（第二组）：闭合产生假边 ----------------
    s.text(400, 666, "闭合产生假边", 36, RED, "middle", "bold")

    reds = s.save("27_pearson_spurious_correlation.svg")
    print(f"check: abs r={r_abs:+.3f} rel r={r_rel:+.3f} n={len(rows)}"
          f"（红 {reds} 处）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
