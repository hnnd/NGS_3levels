#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_design_matrix_rank_geometry.py — 生成 14_design_matrix_rank_geometry.svg
（FIG-M01-16：设计矩阵秩亏与等价解族几何）【data-plot】

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-16（P40，cols 一栏，800×700）。
数据（与 demos 现跑一致）：demos/ch13_design_matrix_rank.py --selftest
Part 1（平衡满秩 3：β̂=1.172, γ̂=2.109，唯一点解）与 Part 2（完全混杂 X=Z
秩亏 1：最小范数解 β̂=γ̂=1.606，等价解族 β+γ=3.2，RSS 恒 1.3879）。
教材 §13.4.5 L248–256、§13.5.2 L351。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 14_design_matrix_rank_geometry.py
"""
from svghelp import *  # noqa: F401,F403

# demos Part 1/2 印刷值（真值 β=1.2, γ=2.0）
BETA_BAL, GAMMA_BAL = 1.172, 2.109
BETA_MIN = 1.606          # 混杂最小范数解（对半分；精确和 3.212，教材按 1 位小数写 3.2）
SUM_BG = 3.2              # 混杂下唯一可估的 β+γ（教材口径）
RSS = 1.3879              # 等价解族恒定残差平方和


def main():
    # 与 demos 印刷值的内部一致性核对（β̂=γ̂ 对半分、和 3.212≈教材 3.2）
    assert abs(2 * BETA_MIN - 3.212) < 1e-9
    assert abs((BETA_BAL - 1.2)) < 0.2 and abs((GAMMA_BAL - 2.0)) < 0.2
    print(f"check: 平衡 β̂={BETA_BAL}, γ̂={GAMMA_BAL}；混杂最小范数解 "
          f"{BETA_MIN}（和 3.212，教材写 {SUM_BG}；RSS 恒 {RSS}）"
          "—— demos Part 1/2 印刷值")

    s = SVG(800, 700)

    # 上面板：平衡设计，两约束线交于唯一点（绿）
    s.rect(50, 50, 700, 290, WHITE, PANEL, 3, rx=14)
    s.line(150, 300, 700, 300, BLUE, 4)
    s.line(150, 80, 150, 300, BLUE, 4)
    px, py = 391, 198
    s.line(180, 92, 635, 320, BLUE, 5)
    s.line(250, 283, 620, 61, BLUE, 5)
    s.circle(px, py, 13, GREEN)
    s.text(425, 180, "平衡满秩 3：唯一解", 30, GREEN, "start", "bold")

    # 下面板：完全混杂，约束退化为一条直线（红）
    s.rect(50, 380, 700, 290, WHITE, PANEL, 3, rx=14)
    s.line(150, 630, 700, 630, BLUE, 4)
    s.line(150, 410, 150, 630, BLUE, 4)
    s.line(150, 410, 680, 630, RED, 6)
    mx = 150 + (BETA_MIN - 0.9) / 1.4 * 540
    my = 630 - (BETA_MIN - 0.9) / 1.4 * 220
    s.circle(mx, my, 12, WHITE, RED, 6)
    s.text(735, 432, "完全混杂秩 2：解不唯一", 30, RED, "end", "bold")
    s.text(735, 476, "β+γ 恒定，RSS 恒 1.388", 30, INK, "end", "bold")
    s.text(735, 520, "信息未记录", 30, INK, "end", "bold")

    s.save("14_design_matrix_rank_geometry.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
