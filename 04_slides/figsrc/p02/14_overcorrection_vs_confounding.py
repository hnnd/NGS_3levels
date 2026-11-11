#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_overcorrection_vs_confounding.py — 生成 14_overcorrection_vs_confounding.svg
（FIG-P02-17：过度校正抹平生物突起 vs 批次—处理完全共线不可辨识）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-17（Slide 37，cols 一栏，800×700）。
依据：教材 §17.4.8 L201–205、§17.5.3 L322–327。纯示意：无数据、无随机数、无网络；
左栏点团形状为示意，右栏 2×2 表为「每批次只含一个处理」的设计矩阵。
图内汉字 = 方案指定整句逐字一致（28 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 14_overcorrection_vs_confounding.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "过度校正抹平特异突起；批次与处理完全共线时方差分解不可辨识。"


def main():
    s = SVG(800, 700, "Over-correction vs complete confounding", plan=TEXT)

    # ---------- 左：过度校正把处理特异亚群并进主簇 ----------
    s.rect(40, 56, 344, 380, WHITE, PANEL, 3, rx=14)
    s.text(60, 96, "A  OVER-CORRECT", 32, BLUE, "start", "bold")
    s.cluster(190, 250, 78, 90, GREEN, seed=5, rmin=3.5, rmax=6.0)
    s.cluster(300, 190, 40, 40, ORANGE, seed=9, rmin=3.5, rmax=6.0)
    s.arrow(336, 168, 262, 206, RED, 6, 16)
    s.text(212, 406, "ERASED", 32, GRAY, "middle", "bold")

    # ---------- 右：批次 × 处理完全共线 ----------
    s.rect(416, 56, 344, 380, WHITE, PANEL, 3, rx=14)
    s.text(436, 96, "B  CONFOUNDED", 32, BLUE, "start", "bold")
    x0, y0, cw, rh = 470, 140, 130, 78
    s.text(x0 + cw / 2, 128, "CTL", 30, GRAY, "middle", "bold")
    s.text(x0 + cw * 1.5, 128, "TRT", 30, GRAY, "middle", "bold")
    s.rect(x0, y0, cw * 2, rh * 2, WHITE, GRAY, 3)
    s.line(x0 + cw, y0, x0 + cw, y0 + rh * 2, GRAY, 3)
    s.line(x0, y0 + rh, x0 + cw * 2, y0 + rh, GRAY, 3)
    for i, b in enumerate(("B1", "B2")):
        s.text(x0 - 12, y0 + rh * i + 48, b, 30, GRAY, "end", "bold")
    for d in range(3):                    # B1 只有对照、B2 只有处理
        s.circle(x0 + 34 + d * 30, y0 + rh / 2, 9, CYAN)
        s.circle(x0 + cw + 34 + d * 30, y0 + rh * 1.5, 9, ORANGE)

    # 红色（第 2 处）：方差分解无解
    s.text(588, 352, "INF SOLUTIONS", 30, RED, "middle", "bold")
    s.text(588, 404, "rank deficit", 30, GRAY, "middle")

    s.caption(["过度校正抹平特异突起；",
               "批次与处理完全共线时方差分解不可辨识。"], [INK, INK], 30,
              top=486)
    s.save("14_overcorrection_vs_confounding.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())
