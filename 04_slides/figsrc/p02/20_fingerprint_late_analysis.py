#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_fingerprint_late_analysis.py — 生成 20_fingerprint_late_analysis.svg
（FIG-P02-24：晚期分析与空间制图异常的三枚指纹）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-24（Slide 56，cols 一栏，800×700）。
依据：教材 §17.5.1 L301–305、§17.5.3 L322–327、§17.5.4 L332–335、讲义 ⑥ 6.2。
纯示意：无数据、无随机数、无网络；p 值刻度只表达「成片极小值」的形态。
图内汉字 = 方案指定整句逐字一致（30 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 20_fingerprint_late_analysis.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "过度校正抹杀特异簇，伪重复诱发显著性雪崩，点阵未对准伪造空间条带。"


def main():
    s = SVG(800, 700, "Late analysis fingerprints", plan=TEXT)

    for x, head, col in ((40, "ERASED", BLUE), (290, "AVALANCHE", BLUE),
                         (540, "STRIPE", CYAN_DEEP)):
        s.rect(x, 56, 220, 400, WHITE, PANEL, 3, rx=14)
        s.text(x + 110, 104, head, 30, col, "middle", "bold")

    # 指纹一：整合后处理特异亚群消失
    s.cluster(108, 190, 38, 30, GREEN, seed=3, rmin=3, rmax=5)
    s.cluster(196, 186, 22, 16, ORANGE, seed=8, rmin=3, rmax=5)
    s.cluster(150, 282, 40, 34, GREEN, seed=4, rmin=3, rmax=5)
    s.arrow(150, 228, 150, 262, RED, 6, 16)

    # 指纹二：成片 p 值极小，显著性雪崩
    s.line(310, 330, 490, 330, INK, 3)
    s.line(400, 330, 400, 140, INK, 3)
    for i, h in enumerate((26, 40, 168, 150, 34, 22)):
        s.rect(322 + i * 28, 330 - h, 20, h, BLUE)
    s.text(404, 136, "1e-300", 30, RED, "start", "bold")

    # 指纹三：点阵未对准，出现与组织形态无关的规则条带
    s.rect(566, 130, 168, 210, WHITE, PANEL, 3)
    for i in range(6):
        s.rect(566, 130 + i * 35, 168, 16, CYAN)

    s.caption(["过度校正抹杀特异簇，伪重复诱发显著性雪崩，",
               "点阵未对准伪造空间条带。"], [INK, INK], 30, top=500)
    s.save("20_fingerprint_late_analysis.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
