#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""24_diagnostic_plot_fingerprints.py — 生成 24_diagnostic_plot_fingerprints.svg
（FIG-P04-24：第 53 页 cols 一栏「四大核心异常图型指纹」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-24（P53，cols，800×700）。
依据：教材 §20.6 的异常指纹表与 §20.5.4——① 衰减曲线在 r² = 0.2 处断崖截断：
漏了 `--ld-window-r2 0`（PLINK 默认只输出 r² ≥ 0.2 的位点对）；② 曲线尾部停在
0.03 下不去：样本少或有结构，先扣 1/n 抽样基线；③ PC1 与深度/缺失率单调相关：
技术批次伪装成结构；④ 一两个样本甩出天际：深度低、污染或异物种。四类都属
「程序正常退出、图也画得出来」的静默失效。
图内中文严格取方案给定 27 字（3 句）；r²、1/n、PC1 与数字属符号。
结构＝田字格四面板，每个面板一幅缩略图型：三格配一句判读，第四格（离群单点）
只用图形表示——方案给定的文字已全部用在前三格。
红只标「默认阈值远距离截断」一处（连同 0.2 截断虚线，同一语义）。
无网络；不涉及随机数（缩略图为示意，非真实输出）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 24_diagnostic_plot_fingerprints.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["默认阈值远距离截断", "抽样本底高企未扣除", "主成分与深度强相关"]
TEXT = "".join(PHRASES)


def frame(s, x, y, w, h, title, col=BLUE, tint=WHITE):
    s.rect(x, y, w, h, tint, col, 4, rx=14)
    s.text(x + w / 2, y + 40, title, 30, col, "middle", "bold")


def axes(s, x0, y0, x1, y1, col=BLUE):
    s.arrow(x0, y0, x1, y0, col, 4, 11)
    s.arrow(x0, y0, x0, y1, col, 4, 11)


def main():
    s = SVG(800, 700, "Four fingerprint shapes of a broken run", plan=TEXT)
    w, h = 360, 290

    # ---------- ① 0.2 处截断 ----------
    frame(s, 30, 52, w, h, "LD decay")
    axes(s, 62, 250, 356, 118, BLUE)
    pts = [(62 + i * 6, 122 + 118 * (1 - 0.9 ** (i * 0.9)))
           for i in range(0, 19)]
    s.polyline([(round(x, 1), round(y, 1)) for x, y in pts], BLUE, 5)
    s.line(176, 110, 176, 250, RED, 4, dash="10 8")
    s.text(188, 132, "0.2", 30, RED, "start", "bold")
    s.text(210, 312, PHRASES[0], 30, RED, "middle", "bold")

    # ---------- ② 尾部高平台 ----------
    frame(s, 410, 52, w, h, "LD decay")
    axes(s, 442, 250, 736, 118, BLUE)
    pts = [(442 + i * 6, 128 + 104 * (1 - 0.86 ** (i * 0.8)))
           for i in range(0, 30)]
    pts += [(442 + 180 + i * 6, 232) for i in range(0, 19)]
    s.polyline([(round(x, 1), round(y, 1)) for x, y in pts], BLUE, 5)
    s.line(442, 232, 736, 232, GRAY, 3, dash="8 8")
    s.text(700, 222, "1/n", 30, GRAY, "end", "bold")
    s.text(590, 312, PHRASES[1], 30, BLUE, "middle", "bold")

    # ---------- ③ PC1 与深度相关 ----------
    frame(s, 30, 360, w, h, "PC1 vs depth")
    axes(s, 62, 590, 356, 430, BLUE)
    for i in range(9):
        x = 78 + i * 30
        y = 576 - i * 18
        s.circle(x, y, 8, CYAN)
    s.line(70, 586, 342, 420, GRAY, 4, dash="12 9")
    s.text(210, 636, PHRASES[2], 30, BLUE, "middle", "bold")

    # ---------- ④ 离群单点 ----------
    frame(s, 410, 360, w, h, "PCA")
    axes(s, 442, 590, 736, 430, BLUE)
    for i in range(5):
        for j in range(4):
            s.circle(500 + i * 20, 548 - j * 18, 7, BLUE)
    s.circle(700, 450, 9, ORANGE)
    s.circle(700, 450, 24, ORANGE, ORANGE, 3, dash="8 7")

    s.save("24_diagnostic_plot_fingerprints.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())
