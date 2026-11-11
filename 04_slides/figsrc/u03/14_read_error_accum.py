#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_read_error_accum.py — 生成 14_read_error_accum.svg（FIG-U03-14：单读错误累积）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-14（P39，cols 一栏，800×700）【data-plot】。
数据：demos/ch04_phred_q.py --selftest 算例 A（150 bp 全 Q30，P=0.001，纯算术），
此处复算并断言：期望 0.15 错/条、6.67 条见 1 错、全长无错 (1−0.001)^150 ≈ 86.06%、
至少含 1 错 ≈ 13.94%。面积图：绿色 = 全长无错 (1−p)^L，红色 = 至少含 1 错。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 14_read_error_accum.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch04_phred_q as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403,E402

P = demo.q_to_p(30)          # 0.001
L_MAX = 150
X0, X1 = 70, 470             # 1 → 150 bp
Y_TOP, Y_BOT = 150, 590      # 100% → 0%


def x_of(length):
    return X0 + (length - 1) / (L_MAX - 1) * (X1 - X0)


def y_of(frac):
    return Y_BOT - frac * (Y_BOT - Y_TOP)


def main():
    p_noerr = (1 - P) ** L_MAX          # 0.8606
    p_err = 1 - p_noerr                 # 0.1394
    exp_err = L_MAX * P                 # 0.15
    reads_per_err = 1 / exp_err         # 6.67
    assert abs(p_noerr - 0.8606) < 1e-3 and abs(p_err - 0.1394) < 1e-3
    assert abs(exp_err - 0.15) < 1e-9 and abs(reads_per_err - 6.6667) < 0.01
    print(f"check: 无错 {p_noerr:.4f} / 含错 {p_err:.4f} / "
          f"{exp_err:.2f} 错/条 / {reads_per_err:.2f} 条/错（demos 一致）")

    s = SVG(800, 700)
    s.text(400, 46, "单读错误累积", 36, BLUE, "middle", "bold")
    s.text(400, 88, "全长无错八成六，至少一错近一成四", 30, GRAY, "middle",
           "bold")

    # 面积堆叠：绿色 = (1-p)^L，红色 = 1-(1-p)^L
    pts = [(L, (1 - P) ** L) for L in range(1, L_MAX + 1)]
    green = [(x_of(L), y_of(f)) for L, f in pts]
    red = [(x_of(L), y_of(1 - f)) for L, f in pts]
    d_green = (f"M {green[0][0]} {green[0][1]} " +
               " ".join(f"L {x:.1f} {y:.1f}" for x, y in green[1:]) +
               f" L {X1} {Y_BOT} L {X0} {Y_BOT} Z")
    d_red = (f"M {red[0][0]} {Y_TOP} " +
             " ".join(f"L {x:.1f} {y:.1f}" for x, y in red[1:]) +
             f" L {X1} {Y_TOP} Z")
    s.path(d_red, None, 0, fill=RED)
    s.path(d_green, None, 0, fill=GREEN)
    # 边界线
    s.polyline(green, INK, 4)

    # 坐标轴标注
    s.text(60, Y_TOP + 10, "100%", 26, GRAY, "end", "bold")
    s.text(60, Y_BOT + 10, "0%", 26, GRAY, "end", "bold")
    s.text(X0, 630, "1 bp", 26, GRAY, "start", "bold")
    s.text(X1, 630, "150 bp", 26, GRAY, "end", "bold")

    # 终点标注：13.9% 含错
    s.text(X1 - 8, y_of(p_noerr) - 14, f"含错 {p_err * 100:.1f}%", 28, WHITE,
           "end", "bold")
    s.text(X1 - 8, y_of(p_noerr) + 30, f"无错 {p_noerr * 100:.1f}%", 28,
           WHITE, "end", "bold")

    # 右侧大数字卡
    s.rect(510, 200, 250, 110, WHITE, PANEL, 4, rx=14)
    s.text(635, 252, f"{exp_err:.2f}", 44, BLUE, "middle", "bold")
    s.text(635, 292, "错 / 条", 28, GRAY, "middle", "bold")
    s.rect(510, 340, 250, 110, WHITE, PANEL, 4, rx=14)
    s.text(635, 392, f"{reads_per_err:.2f}", 44, BLUE, "middle", "bold")
    s.text(635, 432, "条 / 错", 28, GRAY, "middle", "bold")

    s.save("14_read_error_accum.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
