#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_variant_four_gates.py — 生成 02_variant_four_gates.svg
（FIG-M03-02：真变异四条件门禁漏斗）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-02（P11，cols 一栏，800×700）。
图内中文按方案（独立分子 质量可靠 单倍型合理 过滤过线 假变异拦截）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文，工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §10.1、§10.4.2–
§10.4.8。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    gates = [
        ("1", "独立分子", 90),
        ("2", "质量可靠", 182),
        ("3", "单倍型合理", 274),
        ("4", "过滤过线", 366),
    ]
    widths = [640, 500, 360, 220]
    for i, (num, label, y) in enumerate(gates):
        w = widths[i]
        w2 = widths[i + 1] if i + 1 < len(widths) else 120
        x1, x2 = 380 - w / 2, 380 + w / 2
        nx1, nx2 = 380 - w2 / 2, 380 + w2 / 2
        last = i == 3
        s.polygon([(x1, y), (x2, y), (nx2, y + 76), (nx1, y + 76)],
                  GREEN_TINT if last else BLUE_TINT, BLUE, 5)
        s.text(380, y + 42, f"{num}  {label}", 34,
               GREEN if last else BLUE, "middle", "bold")
        # 假阳性侧落通道
        s.polygon([(x2 - 6, y + 18), (x2 + 58, y + 30), (x2 + 58, y + 54),
                   (x2 - 2, y + 68)], RED_TINT, RED, 4)
        s.line(x2 + 14, y + 26, x2 + 42, y + 56, RED, 5)
        s.line(x2 + 42, y + 26, x2 + 14, y + 56, RED, 5)

    # 出口 PASS
    s.arrow(380, 452, 380, 512, GREEN, 7)
    s.rect(280, 514, 200, 66, GREEN_TINT, GREEN, 5, rx=12)
    s.text(380, 558, "PASS", 36, GREEN, "middle", "bold")

    # 红色废弃通道
    s.rect(682, 116, 96, 326, RED_TINT, RED, 5, rx=14)
    s.text(730, 200, "假变异", 32, RED, "middle", "bold")
    s.text(730, 242, "拦截", 32, RED, "middle", "bold")
    s.text(730, 306, "任一", 30, GRAY, "middle")
    s.text(730, 342, "门禁", 30, GRAY, "middle")
    s.text(730, 378, "破损", 30, GRAY, "middle")
    s.text(730, 414, "掉落", 30, GRAY, "middle")

    s.text(380, 634, "MarkDuplicates → 硬过滤兜底 → HC", 30, GRAY,
           "middle")
    s.text(380, 676, "→ QD/FS/SOR/MQ/RankSum 双过线", 30, GRAY, "middle")
    s.save("02_variant_four_gates.svg")


if __name__ == "__main__":
    main()
