#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_fst_two_faces_dxy.py — 生成 22_fst_two_faces_dxy.svg
（FIG-P04-22：第 42 页 cols 一栏「F_ST 高有两副面孔，先问 d_XY」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-22（P42，cols，800×700）。
依据：教材 §20.4.8——Hudson 估计量可写成 F_ST ≈ 1 − π_within/d_XY，由此掉出
两条判读纪律：① 古老长期隔离是 d_XY 极高、群内 π 维持正常（分化是真的深）；
② 某一亚群经历局域清除或极端近期瓶颈是 π_within 断崖式下跌、d_XY 几乎不动，
分母没变分子塌了，F_ST 被机械抬高，两群其实分开不久。只报 F_ST 分不开这两副面孔。
图内中文严格取方案给定 29 字（4 句）；F_ST、π、d_XY 与数字属符号。
结构＝顶部恒等式卡＋左右两副面孔：左（古老隔离：群间距离拉满、群内点阵正常）、
右（局域清除：群间距离几乎不变、一个亚群的群内多样性塌陷、F_ST 被顶高）。
红只标「局域清除多样性塌陷」与「机械抬高」两处。
本图按教材 §20.4.8 重绘，替代讲义中轴读数与机理句不一致、已标待重绘的旧图。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 22_fst_two_faces_dxy.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["古老隔离群间拉满", "分歧深而群内正常", "局域清除多样性塌陷", "机械抬高"]
TEXT = "".join(PHRASES)

DOTS = [(-26, -12), (2, -26), (24, -4), (-14, 20), (16, 26), (-34, 8), (34, 18)]


def cluster(s, cx, cy, color, n=7):
    for dx, dy in DOTS[:n]:
        s.circle(cx + dx, cy + dy, 7, color)


def main():
    s = SVG(800, 700, "Two faces of a high F_ST", plan=TEXT)

    # ---------- 顶部恒等式 ----------
    s.rect(30, 48, 740, 92, WHITE, BLUE, 4, rx=14)
    s.text(400, 110, "F_ST ≈ 1 − π_within / d_XY", 36, BLUE, "middle", "bold")

    # ---------- 左：古老长期隔离 ----------
    s.panel(30, 164, 355, 436, GREEN_TINT, GREEN, 4)
    s.circle(112, 240, 52, WHITE, BLUE, 4)
    s.circle(303, 240, 52, WHITE, BLUE, 4)
    cluster(s, 112, 240, BLUE)
    cluster(s, 303, 240, BLUE)
    s.darrow_h(172, 243, 240, GREEN, 4, 12)
    s.text(207, 320, "d_XY ↑", 30, GREEN, "middle", "bold")
    s.text(207, 480, PHRASES[0], 30, GREEN, "middle", "bold")
    s.text(207, 534, PHRASES[1], 30, GREEN, "middle", "bold")

    # ---------- 右：局域清除 / 近期瓶颈 ----------
    s.panel(415, 164, 355, 436, RED_TINT, BLUE, 4)
    s.circle(497, 240, 52, WHITE, BLUE, 4)
    s.circle(688, 240, 52, WHITE, BLUE, 4)
    cluster(s, 497, 240, BLUE, n=3)
    cluster(s, 688, 240, BLUE)
    s.darrow_h(557, 628, 240, BLUE, 4, 12)
    s.text(592, 320, "d_XY ~", 30, BLUE, "middle", "bold")
    s.text(592, 480, PHRASES[2], 30, RED, "middle", "bold")
    s.text(592, 534, PHRASES[3] + " ↑", 30, RED, "middle", "bold")

    s.save("22_fst_two_faces_dxy.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
