#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_pe_adapter_three_channels.py — 生成 12_pe_adapter_three_channels.svg
（FIG-U04-15：fastp 双端接头识别三通道【算法/机制】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-15（P33，cols 一栏，viewBox 800×700）。
通道一：重叠推断（深蓝，R1/R2 overlap，best）→ 通道二：自动扫描（青蓝，
--detect_adapter_for_pe）→ 通道三：显式指定（橙，--adapter_sequence）；
右侧红字「无重叠不等于无接头」。
依据：教材 §6.4.4 L124–130。图内汉字 30，红色 1 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 12_pe_adapter_three_channels.py
"""
from svghelp import *


def main():
    s = SVG(800, 700)
    rows = [("通道一：重叠推断", BLUE, "R1/R2 overlap", True),
            ("通道二：自动扫描", CYAN_DEEP, "--detect_adapter_for_pe", False),
            ("通道三：显式指定", ORANGE_DEEP, "--adapter_sequence", False)]
    for i, (lab, color, mech, best) in enumerate(rows):
        y = 80 + i * 180
        s.rect(40, y, 300, 120, color, rx=16)
        s.text(190, y + 74, lab, 30, WHITE, "middle", "bold")
        s.rect(352, y, 336, 120, WHITE, stroke=color, sw=5, rx=16)
        s.text(520, y + 74, mech, 30, GRAY, "middle")
        s.arrow(340, y + 60, 348, y + 60, color, sw=6)
        if best:
            s.rect(632, y + 34, 44, 44, GREEN, rx=10)
            s.text(654, y + 65, "1", 30, WHITE, "middle", "bold")

    # 右侧红字（唯一红色处）
    s.text_rot(752, 350, "无重叠不等于无接头", -90, size=32, fill=RED)

    s.save("12_pe_adapter_three_channels.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
