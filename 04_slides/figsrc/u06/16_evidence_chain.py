#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_evidence_chain.py — 生成 16_evidence_chain.svg（FIG-U06-16：证据链四步）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-16（P40，cols 一栏，800×700）。
数据：无量字数字。四步顺序不得改动：总长与污染 → 结构与回贴 → 完整性 →
连续性与拓扑（教材 §8.4.9 L308–310；红字＝不设"差 2% 一票否决"）。
版式（D127 修订）：等高等宽四步横向箭头链（①→②→③→④），台阶式上升会
暗示「后面的步骤更重要」，与教材「先排除严重错误、连续性最后看」语义相反。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 16_evidence_chain.py
"""
from svghelp import *  # noqa: F401,F403

STEPS = [
    ("①", "总长与污染"),
    ("②", "结构与回贴"),
    ("③", "完整性"),
    ("④", "连续性与拓扑"),
]
SHADES = ["#7A90BC", "#5E78A8", "#4A6497", BLUE]


def main():
    s = SVG(800, 700)
    X0, W, GAP, Y0, BH = 24, 158, 40, 250, 150
    for i, ((num, name), color) in enumerate(zip(STEPS, SHADES)):
        x = X0 + i * (W + GAP)
        # 等宽圆角框（等高，不再暗示步骤重要性递进）
        s.rect(x, Y0, W, BH, color, rx=14)
        s.text(x + W / 2, Y0 + 95, num, 56, WHITE, "middle", "bold")
        # 步骤名在框下方居中（圈号在框内，连读＝方案原文）
        s.text(x + W / 2, Y0 + BH + 70, name, 30, BLUE, "middle", "bold")
        if i < 3:
            s.arrow(x + W + 4, Y0 + BH / 2, x + W + GAP - 4, Y0 + BH / 2,
                    BLUE, 6)

    # 红色横幅（唯一红色：不设 C 一票否决）
    s.rect(150, 550, 500, 56, RED, rx=12)
    s.text(400, 588, "不设 C 一票否决", 34, WHITE, "middle", "bold")

    s.save("16_evidence_chain.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
