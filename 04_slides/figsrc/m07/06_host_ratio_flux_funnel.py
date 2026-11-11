#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_host_ratio_flux_funnel.py — FIG-M07-07 宿主占比失衡的通量对比（data-plot）

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-07（P19，`.cols` 一栏 800×700，data-plot）。
数据来源：`demos/ch19_host_depletion_tradeoff.py --selftest` 的组间偏移手算断言
（(1−0.85)/(1−0.40) = 0.25，即 A 组有效微生物通量只有 B 组的 1/4）。本脚本复算并断言。
图内汉字 = 方案清单逐字，共 28 字（宿主八成五：有效剩一成半 / 宿主四成：有效剩六成 /
四倍技术鸿沟）；百分比 85/15/40/60 与通量比 0.25 为数字。
红色水平虚线 = 等通量下采样线：落在 A 组有效通量的同一水平，B 组须下采样到该水平才可比。
无随机数、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_host_ratio_flux_funnel.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

HA, HB = 0.85, 0.40


def main():
    ratio = (1 - HA) / (1 - HB)      # 与 demos --selftest 同式
    assert abs(ratio - 0.25) < 1e-9

    GROUPS = [
        (152, ["宿主八成五：", "有效剩一成半"], HA, ORANGE, ORANGE_TINT, ORANGE_DEEP),
        (472, ["宿主四成：", "有效剩六成"], HB, CYAN, CYAN_TINT, CYAN_DEEP),
    ]
    print(f"check: A 宿主 {HA:.0%} 有效 {1-HA:.0%}；B 宿主 {HB:.0%} 有效 {1-HB:.0%}；"
          f"通量比 {ratio:.2f}（4 倍）")

    s = SVG()

    TOP, FH, BW = 208, 356, 176

    for x, cap, hfrac, col, tint, deep in GROUPS:
        cx = x + BW / 2
        s.label(cx, 104, cap, 32, deep, "middle", "bold")

        # 堆叠条：上段宿主（橙），下段微生物有效通量（组色）；百分比写在各段内
        s.rect(x, TOP, BW, FH * hfrac, ORANGE_TINT, ORANGE_DEEP, 4, rx=6)
        s.rect(x, TOP + FH * hfrac, BW, FH * (1 - hfrac), tint, col, 4, rx=6)

        s.text(cx, TOP + FH * hfrac / 2 + 12, f"{hfrac:.0%}", 34, ORANGE_DEEP,
               "middle", "bold")
        s.text(cx, TOP + FH * (hfrac + (1 - hfrac) / 2) + 11,
               f"{1 - hfrac:.0%}", 32, deep, "middle", "bold")

    # ---------------- 等通量下采样线：A 组有效通量水平 ----------------
    y_line = TOP + FH - FH * (1 - HA)
    s.line(48, y_line, 752, y_line, RED, 5, dash="14 10")
    s.text(752, y_line - 18, "0.25", 32, RED, "end", "bold")

    s.text(400, 650, "四倍技术鸿沟", 34, RED, "middle", "bold")

    s.save("06_host_ratio_flux_funnel.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
