#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_on_contig_edge_geometry.py — 生成 20_on_contig_edge_geometry.svg（FIG-U07-20：on contig edge 坐标判定几何示意）【data-plot】

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-20（P61，cols 一栏，viewBox 800×700）。
数据（教材设例，算术复核）：教材 §9.4.8 L334–342、§9.5.4、§9.7 习题 6——
region contig_3:1–28,400，contig 总长 28,850 bp，右端余量 450 bp；
起点等于 1 即贴边（完整性未知），另一端有余量不抵消该判定。
设例标注（图内灰字）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 20_on_contig_edge_geometry.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    total, end = 28850, 28400
    margin = total - end
    assert margin == 450
    print(f"check: 总长 {total} − 终点 {end} = 余量 {margin} bp")

    s = SVG(800, 700)
    s.text(30, 48, "设例", 30, GRAY, "start")

    PX = 700.0 / total  # 700 px = 28,850 bp
    X0 = 50
    x_end = X0 + end * PX   # ≈ 739.3
    x_tot = X0 + total * PX  # = 750

    # contig 条（深蓝）+ BGC 区域（橙）+ 右端余量（灰）
    s.rect(X0, 140, 700, 48, BLUE, rx=6)
    s.rect(X0, 140, end * PX, 48, ORANGE, rx=6)
    s.rect(x_end, 140, x_tot - x_end, 48, PANEL, rx=6)

    # 左端：起点 = 1（红色竖线 + 红字标签，红色语义处 1）
    s.line(X0, 108, X0, 218, RED, 7)
    s.text(66, 108, "起点等于一", 32, RED, "start", "bold")
    s.text(X0, 250, "1", 30, GRAY, "middle")

    # 右端：终点坐标经竖线引入余量放大插图（本例未触发贴边）
    s.line(x_end, 188, x_end, 240, GRAY, 3)
    s.line(x_tot, 188, x_tot, 240, GRAY, 3)
    # 放大插图：余量 450 bp（300× 放大示意，按比例 150 单位 = 450 bp）
    s.rect(560, 240, 210, 96, WHITE, GRAY, 3, rx=8)
    s.text(655, 266, "450 bp", 30, GRAY, "middle")
    s.rect(595, 278, 120, 18, ORANGE, rx=4)
    s.line(595, 296, 595, 320, GRAY, 4)
    s.line(715, 296, 715, 320, GRAY, 4)
    s.text(595, 348, "28,400", 30, GRAY, "middle")
    s.text(715, 348, "28,850", 30, GRAY, "middle")
    s.text(785, 430, "终点等于总长", 32, INK, "end", "bold")

    # 右端有余量不抵消贴边判定
    s.text(400, 500, "右端有余量不抵消", 32, INK, "middle", "bold")

    # 底部红色判据条（红色语义处 2）
    s.rect(210, 580, 380, 60, RED, rx=12)
    s.text(400, 622, "贴边即完整性未知", 32, WHITE, "middle", "bold")

    s.save("20_on_contig_edge_geometry.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
