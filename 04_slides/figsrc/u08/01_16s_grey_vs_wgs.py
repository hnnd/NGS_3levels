#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_16s_grey_vs_wgs.py — 生成 01_16s_grey_vs_wgs.svg（FIG-U08-01：
16S 灰区困境 vs 全基因组分辨力）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-01（P11，cols 一栏，800×700）。
数据：16S 全长 1.5 kb（教材 §18.4.1）；Xoo 基因组约 4 Mb（手册、教材 §11.1）；
97.8% 为讲义设例并标「设例」（ALN §0.6）。红 1 处＝16S 灰区标签（开章动机）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 01_16s_grey_vs_wgs.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # —— 左卡片：16S rDNA ——
    s.rect(40, 110, 330, 400, WHITE, PANEL, 4, rx=16)
    s.text(70, 168, "16S rDNA", 36, BLUE, "start", "bold")
    # 标尺 1.5 kb
    s.rect(80, 220, 250, 22, BLUE, rx=6)
    for tx in (80, 205, 330):
        s.line(tx, 250, tx, 266, BLUE, 4)
    s.text(205, 300, "1.5 kb", 30, GRAY, "middle")
    s.text(205, 380, "16S：1.5 kb，属内分不开", 30, INK, "middle", "bold")
    # 灰区红标签（唯一红；97.8% 为设例）
    s.rect(72, 424, 266, 58, RED, rx=12)
    s.text(205, 463, "97.8% 灰区（设例）", 30, WHITE, "middle", "bold")

    # —— 右卡片：全基因组 ——
    s.rect(430, 110, 330, 400, WHITE, PANEL, 4, rx=16)
    cx, cy, r = 595, 292, 108
    s.circle(cx, cy, r, "none", CYAN_DEEP, 12)
    for ang, w, h in ((-30, 56, 22), (45, 44, 22), (150, 50, 22), (235, 40, 20)):
        import math
        ex = cx + (r) * math.cos(math.radians(ang))
        ey = cy + (r) * math.sin(math.radians(ang))
        s.rect(ex - w / 2, ey - h / 2, w, h, ORANGE, rx=6)
    s.text(595, 170, "WGS ~4 Mb", 32, CYAN_DEEP, "middle", "bold")
    s.text(595, 452, "全基因组：~4 Mb", 30, INK, "middle", "bold")
    s.text(595, 490, "定种溯源", 30, INK, "middle", "bold")

    # 底部总结
    s.rect(200, 560, 400, 62, BLUE, rx=12)
    s.text(400, 603, "捕捉致病可变基因", 36, WHITE, "middle", "bold")

    s.save("01_16s_grey_vs_wgs.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
