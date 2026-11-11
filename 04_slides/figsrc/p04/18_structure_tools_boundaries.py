#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_structure_tools_boundaries.py — 生成 18_structure_tools_boundaries.svg
（FIG-P04-18：第 36 页 cols 一栏「群体结构三工具解释边界」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-18（P36，cols，800×700）。
依据：教材 §20.4.5——PCA 是无先验的奇异值分解，连续梯度会自发出规则波形，
未剪枝 LD 会让共分离标记在同一主成分上同步极化；ADMIXTURE 假定 K 个离散祖先
成分，连续渐变与抽样不均会切出「虚构成分」，CV 最低的 K 不等于真实亚群数；
TreeMix 的迁移边是对协方差残差的贪心吸收，只能当工作假说，须由 f₃/f₄ 独立证实。
图内中文严格取方案给定 26 字（3 句，各按 4–5 字折成两行放在栏下）；
PCA、ADMIXTURE、TreeMix 与 K 属符号。
结构＝三栏并列：PCA 点云与自发波形、ADMIXTURE 堆叠条形、TreeMix 树上的一条
迁移边；栏下各一句解释边界。
红只标「祖先成分非真实种群」一处。
无网络；不涉及随机数（示意图形，非真实数据）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 18_structure_tools_boundaries.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["主成分几何投影波形", "祖先成分非真实种群", "迁移边为残差假说"]
TEXT = "".join(PHRASES)

COLS = [
    (30, "PCA", BLUE, BLUE_TINT, ("主成分几何", "投影波形"), BLUE),
    (282, "ADMIXTURE", CYAN_DEEP, CYAN_TINT, ("祖先成分", "非真实种群"), RED),
    (534, "TreeMix", ORANGE, ORANGE_TINT, ("迁移边为", "残差假说"), INK),
]


def icon_pca(s, cx, cy, color):
    """连续梯度点云 + 自发波形曲线。"""
    for i in range(6):
        for j in range(4):
            s.circle(cx - 78 + i * 30 + j * 4, cy + 26 - j * 20 + i * 3, 6, color)
    s.path(f"M {cx - 92} {cy + 30} Q {cx - 46} {cy - 46} {cx} {cy + 6} "
           f"Q {cx + 46} {cy + 58} {cx + 92} {cy - 18}", GRAY, 4, dash="10 8")


def icon_admix(s, cx, cy, color):
    """K 个离散祖先成分的堆叠条形。"""
    cols = (color, GRAY, BLUE)
    heights = ((0.6, 0.2, 0.2), (0.5, 0.3, 0.2), (0.35, 0.25, 0.4),
               (0.2, 0.3, 0.5), (0.15, 0.35, 0.5), (0.1, 0.3, 0.6))
    for i, hs in enumerate(heights):
        x = cx - 90 + i * 32
        y = cy + 44
        for h, c in zip(hs, cols):
            bh = h * 100
            y -= bh
            s.rect(x, y, 26, bh, c, None, 0, rx=2)
        s.text(x + 13, cy + 76, str(i + 1), 30, GRAY, "middle")


def icon_treemix(s, cx, cy, color):
    """带一条迁移边的树：一条主干、三个末端。"""
    s.line(cx - 100, cy + 4, cx - 66, cy + 4, color, 4)
    s.line(cx - 66, cy - 44, cx - 66, cy + 48, color, 4)
    for y0, tip in ((-44, -70), (4, -24), (48, 70)):
        s.line(cx - 66, cy + y0, cx - 18, cy + y0, color, 4)
        s.line(cx - 18, cy + y0, cx - 18, cy + tip, color, 4)
    s.path(f"M {cx - 18} {cy - 70} Q {cx + 40} {cy - 96} {cx + 52} {cy - 16}",
           GRAY, 4, dash="10 8")
    s.polygon([(cx + 54, cy - 8), (cx + 34, cy - 16), (cx + 50, cy - 28)],
              GRAY)


def main():
    s = SVG(800, 700, "Three structure tools, three boundaries", plan=TEXT)

    for x, head, col, tint, lines, tcol in COLS:
        s.rect(x, 70, 236, 560, tint, col, 4, rx=14)
        s.text(x + 118, 130, head, 32, col, "middle", "bold")
        s.line(x + 24, 152, x + 212, 152, PANEL, 3)

    icon_pca(s, 148, 300, BLUE)
    icon_admix(s, 400, 300, CYAN_DEEP)
    icon_treemix(s, 652, 300, ORANGE)

    for x, head, col, tint, lines, tcol in COLS:
        s.text(x + 118, 470, lines[0], 30, tcol, "middle", "bold")
        s.text(x + 118, 516, lines[1], 30, tcol, "middle", "bold")

    s.save("18_structure_tools_boundaries.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 26, TEXT
    raise SystemExit(main())
