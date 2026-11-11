#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_knn_graph_modularity_split.py — 生成 11_knn_graph_modularity_split.svg
（FIG-P02-13：近邻图按模块度切分，分辨率越高切得越碎）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-13（Slide 30，cols 一栏，800×700）。
依据：教材 §17.4.6 L161–165、§17.5.3 L314–320（resolution 与簇数近似单调，
客观真值不存在）。网络节点由确定性线性同余摆放，无随机库、无网络，无数值断言。
图内汉字 = 方案指定整句逐字一致（30 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 11_knn_graph_modularity_split.py
"""
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "近邻图优化模块度切分流形。分辨率越高簇数单调增加，客观真值不存在。"


def net(s, cx, cy, rad, n, color, seed, edge=BLUE):
    """在圆周上摆 n 个节点并连成近邻环（确定性，无随机库）。"""
    st = (seed * 2654435761 % 2 ** 31) or 11
    pts = []
    for i in range(n):
        st = (1103515245 * st + 12345) % 2 ** 31
        a = 2 * math.pi * i / n + 0.4 * (st / 2 ** 31 - 0.5)
        st = (1103515245 * st + 12345) % 2 ** 31
        r = rad * (0.62 + 0.38 * (st / 2 ** 31))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    for i in range(n):
        for j in (i + 1, i + 2):
            x1, y1 = pts[i]
            x2, y2 = pts[j % n]
            s.line(round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1),
                   edge, 3)
    for x, y in pts:
        s.circle(round(x, 1), round(y, 1), 6, color)


def main():
    s = SVG(800, 700, "KNN graph modularity split", plan=TEXT)

    # 左：低分辨率 —— 只切 3 个粗大团
    s.rect(40, 56, 344, 400, WHITE, PANEL, 3, rx=14)
    s.text(60, 96, "γ = 0.2", 32, BLUE, "start", "bold")
    for cx, cy, col, sd in ((165, 170, GREEN, 1), (270, 245, BLUE, 2),
                            (165, 340, PURPLE, 3)):
        net(s, cx, cy, 56, 9, col, sd)
    s.text(212, 432, "3", 40, BLUE, "middle", "bold")

    # 右：高分辨率 —— 同一流形被切成 8 个碎亚群
    s.rect(416, 56, 344, 400, WHITE, PANEL, 3, rx=14)
    s.text(436, 96, "γ = 1.0", 32, BLUE, "start", "bold")
    small = [(474, 150, GREEN), (548, 146, CYAN), (622, 152, GREEN),
             (696, 148, PURPLE), (474, 240, BLUE), (548, 244, ORANGE),
             (622, 238, GREEN), (696, 242, CYAN)]
    for i, (cx, cy, col) in enumerate(small):
        net(s, cx, cy, 30, 5, col, i + 5, edge=PANEL)
    s.text(588, 432, "8", 40, BLUE, "middle", "bold")
    # 红色（1 处）：客观真值不存在，切到几类由参数决定
    s.text(585, 350, "NO TRUTH", 32, RED, "middle", "bold")

    # 单调：3 → 8
    s.arrow(212, 478, 588, 478, BLUE, 5, 16)

    s.caption(["近邻图优化模块度切分流形。",
               "分辨率越高簇数单调增加，客观真值不存在。"], [INK, INK], 30,
              top=500)
    s.save("11_knn_graph_modularity_split.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
