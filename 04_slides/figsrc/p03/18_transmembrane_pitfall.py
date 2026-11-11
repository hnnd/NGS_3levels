#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_transmembrane_pitfall.py — 生成 18_transmembrane_pitfall.svg
（FIG-P03-18：第 36 页 cols 一栏「信号肽疏水 h 区伪装成跨膜螺旋陷阱」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-18（P36，cols，800×700）。
依据：教材 §16.4.6 L308–311、§16.5.4 L424——信号肽的 h 区本身就是一段疏水螺旋，
和跨膜螺旋在物理性质上几乎不可区分。把全长蛋白直接送进 TM 预测，h 区被识别成跨膜
段，真效应子会被整条剔除；正确规程是先按 SignalP 给出的切割位点切掉信号肽，再对
成熟肽做 TM 预测，这样才不会误杀。
图内中文严格取方案给定 30 字（4 句）。`TM` 为工具名与概念符号。
结构＝上下两条蛋白条带路径：上（错误）h 区被红虚线圈住并判成跨膜段，右端大红叉；
下（正确）虚切线上加剪刀，成熟肽一侧无跨膜段，右端绿色对勾。条带两段颜色（左橙 h 区、
右青蓝成熟肽）本身就是图形语义，不再加注。
配色：浅橙＝信号肽 h 区，青蓝＝成熟肽，红色只标误杀路径与结论，绿色只标正确路径与
结论。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 18_transmembrane_pitfall.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["疏水区假冒跨膜段", "全长直跑误杀效应子", "先切除信号肽", "成熟肽上判跨膜"]
TEXT = "".join(PHRASES)
BARY, BARH, HEADW, BARW = 132, 48, 138, 470   # 条带几何：左端 h 区宽 138


def bar(s, y):
    """蛋白条带：橙段（信号肽 h 区）＋青蓝段（成熟肽）。"""
    s.rect(58, y, BARW, BARH, CYAN_TINT, None, 0, rx=BARH / 2)
    s.rect(58, y, HEADW, BARH, ORANGE, None, 0, rx=BARH / 2)
    s.rect(58, y, BARW, BARH, "none", BLUE, 3, rx=BARH / 2)


def scissors(s, cx, cy, color):
    """剪刀图标：两片刀身 + 两个拇指环。"""
    s.line(cx - 8, cy + 4, cx + 26, cy + 22, color, 5)
    s.line(cx - 8, cy - 4, cx + 26, cy - 22, color, 5)
    s.circle(cx - 18, cy + 8, 9, WHITE, color, 4)
    s.circle(cx - 18, cy - 8, 9, WHITE, color, 4)


def main():
    s = SVG(800, 700, "Hydrophobic region posing as a TM helix", plan=TEXT)

    # ---------- 上：错误路径——h 区被直接判成跨膜段 ----------
    s.text(44, 92, PHRASES[0], 30, INK, "start", "bold")
    bar(s, BARY)
    s.rect(50, BARY - 10, HEADW + 20, BARH + 20, "none", PURPLE, 4, rx=12,
           dash="9 7")
    s.text(244, BARY + 34, "TM", 30, ORANGE, "start", "bold")
    s.arrow(228, BARY + 24, 196, BARY + 20, ORANGE, 5, 14)
    s.cross(650, BARY + 24, 32, RED, 10)
    s.text(44, 258, PHRASES[1], 30, RED, "start", "bold")
    s.line(44, 292, 756, 292, PANEL, 4)

    # ---------- 下：正确路径——先切信号肽，再判成熟肽 ----------
    s.text(44, 372, PHRASES[2], 30, GREEN, "start", "bold")
    by = 512
    bar(s, by)
    s.line(196, by - 24, 196, by + BARH + 24, GREEN, 4, dash="9 7")   # 切割位点
    scissors(s, 152, by - 52, GREEN)                                 # 剪刀悬在切割位点上方
    s.text(216, by - 66, PHRASES[3], 30, GREEN, "start", "bold")
    s.arrow(284, by - 44, 264, by + 10, GREEN, 5, 14)

    # ---------- 正确路径的判定结果：成熟肽段上无跨膜螺旋 ----------
    s.check(650, by + 24, 32, GREEN, 10)
    s.save("18_transmembrane_pitfall.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
