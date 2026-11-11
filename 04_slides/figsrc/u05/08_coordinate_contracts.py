#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_coordinate_contracts.py — 生成 08_coordinate_contracts.svg（FIG-U05-08：三套坐标契约）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-08（P28，cols 一栏，viewBox 800×700）。
参考轴 contig1（2000 bp）高亮同一段 100 bp（起点＝第 1001 碱基）；三张写法卡：
SAM POS=1001｜contig1:1001-1100｜BED contig1 1000 1100；红箭头＝BED 数字直接抄进
命令行 → 101 bp、无报错。数字＝教材 §7.4.4 L180 设例逐字（手算可复核，contig1 中性名）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 08_coordinate_contracts.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    # 数据自检（教材 §7.4.4 L180 正文算术）
    assert 1100 - 1001 + 1 == 100      # 命令行：1-based 闭区间
    assert 1100 - 1000 == 100          # BED：0-based 半开
    assert 1100 - 1000 + 1 == 101      # BED 误抄进命令行
    print("check: SAM POS=1001；CLI 1001-1100=100 bp；BED 1000 1100=100 bp；"
          "误抄=101 bp")

    s = SVG(800, 700)
    PX_PER_BP = 600 / 2000             # 参考轴 600 px = 2000 bp（示意）

    # 参考轴与高亮段（1001–1100 → 轴上 [1000,1100) bp）
    s.rect(60, 60, 600, 40, BLUE, rx=8)
    s.text(80, 88, "contig1", 30, WHITE, "start", "bold")
    s.text(620, 88, "2000 bp", 30, WHITE, "end", "bold")
    gx = 60 + 1000 * PX_PER_BP
    gw = 100 * PX_PER_BP
    s.rect(gx, 52, gw, 56, "none", GREEN, 6)
    s.text(60 + 1050 * PX_PER_BP, 34, "同一段", 30, INK, "middle", "bold")
    s.text(60 + 1050 * PX_PER_BP, 146, "1001–1100", 30, GREEN, "middle",
           "bold")

    cards = [
        (150, BLUE, "SAM", "POS = 1001", "1-based, closed"),
        (280, CYAN_DEEP, "CLI", "contig1:1001-1100", "= 100 bp"),
        (410, PURPLE, "BED", "contig1  1000  1100", "= 100 bp"),
    ]
    for y, color, chip, line1, line2 in cards:
        s.rect(60, y, 480, 96, WHITE, color, 5, rx=14)
        s.rect(60, y, 118, 96, color, rx=14)
        s.text(119, y + 60, chip, 32, WHITE, "middle", "bold")
        s.text(200, y + 42, line1, 32, INK, "start", "bold")
        s.text(200, y + 78, line2, 30, GRAY, "start", "bold")

    # 红箭头：BED 数字直接抄进命令行 → 101 bp（唯一红）
    s.arrow(570, 458, 570, 404, RED, 6, head=18)
    s.text(665, 350, "抄错变 101 bp", 30, RED, "middle", "bold")
    s.text(665, 392, "无报错", 30, GRAY, "middle", "bold")

    s.save("08_coordinate_contracts.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
