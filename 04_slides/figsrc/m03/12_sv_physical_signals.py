#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_sv_physical_signals.py — 生成 12_sv_physical_signals.svg
（FIG-M03-15：SV 四类间接物理信号与长读长读穿）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-15（P29，cols 一栏，800×700）。
图内中文按方案（异常插入 分裂读段 深度突变 局部组装 长读跨越重复断点）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.4.11、§10.5.5。
无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 46, "SV 四类信号", 36, INK, "middle", "bold")

    cells = [(40, 70), (420, 70), (40, 300), (420, 300)]
    titles = ["异常插入", "分裂读段", "深度突变", "局部组装"]
    cols = [BLUE, ORANGE, CYAN_DEEP, PURPLE]
    for (x, y), t, col in zip(cells, titles, cols):
        s.rect(x, y, 340, 200, WHITE, col, 4, rx=14)
        s.text(x + 170, y + 44, t, 32, col, "middle", "bold")

    # ① 异常插入
    s.line(70, 130, 350, 130, BLUE, 5)
    s.rect(90, 144, 64, 26, CYAN, None, rx=3)
    s.rect(286, 144, 64, 26, CYAN, None, rx=3)
    s.line(154, 157, 286, 157, PANEL, 8)
    s.polygon([(96, 151), (118, 151), (118, 163), (96, 163)], INK)
    s.polygon([(344, 151), (322, 151), (322, 163), (344, 163)], INK)
    s.text(210, 214, "跨度↑ / 倒位", 30, GRAY, "middle")
    s.text(210, 250, "缺失 / 倒位线索", 30, GRAY, "middle")

    # ② 分裂读段
    s.line(450, 130, 730, 130, BLUE, 5)
    s.rect(470, 144, 92, 26, ORANGE, None, rx=3)
    s.rect(606, 144, 104, 26, ORANGE, None, rx=3)
    s.line(562, 157, 606, 157, RED, 5, dash="9 7")
    s.text(590, 214, "CIGAR 50S100M", 30, GRAY, "middle")
    s.text(590, 250, "断点处软剪切", 30, GRAY, "middle")

    # ③ 深度台阶
    base = 440
    s.line(70, base, 350, base, BLUE, 4)
    pts = [(80, base - 34), (140, base - 34), (140, base - 70), (240, base - 70),
           (240, base - 8), (330, base - 8)]
    s.polyline(pts, CYAN, 7)
    s.darrow(148, base - 76, 148, base - 40, GREEN, 5, head=12)
    s.darrow(248, base - 14, 248, base - 64, RED, 5, head=12)
    s.text(210, 480, "重复 ×2 / 缺失 ≈0", 30, GRAY, "middle")

    # ④ 局部组装
    s.rect(450, 356, 104, 34, PANEL, GRAY, 3, rx=4)
    s.rect(616, 404, 104, 34, PANEL, GRAY, 3, rx=4)
    s.line(554, 373, 616, 421, PURPLE, 7)
    s.text(585, 478, "未比对→新连接", 30, PURPLE, "middle", "bold")

    # 底部对照
    s.rect(40, 530, 720, 120, WHITE, PANEL, 3, rx=14)
    s.text(180, 568, "segdup 断点", 30, INK, "middle", "bold")
    for k in range(4):
        s.rect(280 + k * 40, 580, 34, 22, CYAN, None, rx=3)
    s.text(320, 636, "短读长 MAPQ=0", 30, RED, "middle", "bold")
    s.rect(520, 576, 220, 30, GREEN, None, rx=6)
    s.text(630, 636, "长读跨越重复断点", 30, GREEN, "middle", "bold")
    s.save("12_sv_physical_signals.svg")


if __name__ == "__main__":
    main()
