#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_assembly_evidence_ladder.py — 生成 16_assembly_evidence_ladder.svg（FIG-U08-16：
组装选型四步台阶证据链）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-16（P47，cols 一栏，800×700）。
四级台阶自左下向右上递进：①总长对账（深蓝）→②结构与回贴（青蓝）→
③同库自比 BUSCO（绿）→④连续性（紫）；底部红色横幅＝不设 C 差 2% 一票否决
（教材 §8.4.9 L308–310、§8.4.8；严禁引入 3.8–4.3 Mb 区间与 C≥97%/D≤2% 假阈值，
ALN W1/W2/W3/W4）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 16_assembly_evidence_ladder.py
"""
from svghelp import *  # noqa: F401,F403

STEPS = [
    ("①", "总长对账", None, BLUE),
    ("②", "结构与回贴", None, CYAN_DEEP),
    ("③", "同库自比", "BUSCO", GREEN),
    ("④", "连续性", None, PURPLE),
]


def main():
    s = SVG(800, 700)
    BW, BH, PITCH, YTOP = 170, 120, 190, 110

    # 后台阶上升虚线（先于色块绘制，间隙中可见）
    s.polyline([(120, 560), (310, 440), (500, 320), (690, 200)], GRAY, 4,
               dash="14 12")

    for i, (num, name, sub, color) in enumerate(STEPS):
        x = 40 + i * PITCH
        y = 470 - i * (470 - YTOP) / 3
        s.rect(x, y, BW, BH, color, rx=14)
        s.text(x + BW / 2, y + 50, num, 44, WHITE, "middle", "bold")
        s.text(x + BW / 2, y + 88, name, 32, WHITE, "middle", "bold")
        if sub:
            s.text(x + BW / 2, y + 112, sub, 30, WHITE, "middle")

    # 红色横幅（唯一红：禁止旧的一票否决规则）
    s.rect(150, 612, 500, 60, RED, rx=12)
    s.text(400, 654, "不设 C 差 2% 一票否决", 34, WHITE, "middle", "bold")

    s.save("16_assembly_evidence_ladder.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
