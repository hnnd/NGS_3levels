#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_cigar_accounting.py — 生成 07_cigar_accounting.svg（FIG-U05-07：CIGAR 两条消耗账）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-07（P26，cols 一栏，viewBox 800×700）。
上组 50M2D10M5I15M：读段轴 50+10+5+15=80 vs 参考轴 50+2+10+15=77（2D 只消耗参考，
红描边）；下组 15S85M：读段 100 全留 SEQ、参考跨 85。数字＝教材 §7.4.3 L156 正文算术
（手算可复核）；NM 语义＝L158。deck 第三例（50M2D10M→60/62）不入图（一图一焦点）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 07_cigar_accounting.py
"""
from svghelp import *  # noqa: F401,F403

PX_PER_BP = 7  # 示意比例（两轴同尺，逐段对齐）


def main():
    # 数据自检（教材 §7.4.3 L156 正文算术）
    assert 50 + 10 + 5 + 15 == 80
    assert 50 + 2 + 10 + 15 == 77
    assert 15 + 85 == 100 and 85 == 85
    print("check: 读段 50+10+5+15=80；参考 50+2+10+15=77；15S85M → 100/85")

    s = SVG(800, 700)

    # ---- 上组：50M2D10M5I15M ----
    s.text(60, 84, "50M2D10M5I15M", 32, BLUE, "start", "bold")
    s.text(60, 126, "读段消耗", 30, INK, "start", "bold")
    # 读段轴：50 / 10 / 5 / 15（青蓝）
    y = 150
    x = 60
    for ln, lab in ((50, "50"), (10, "10"), (5, "5"), (15, "15")):
        s.rect(x, y, ln * PX_PER_BP, 40, CYAN, rx=4)
        s.text(x + ln * PX_PER_BP // 2, y + 28, lab, 30, WHITE, "middle",
               "bold")
        x += ln * PX_PER_BP
    s.text(645, y + 28, "= 80", 30, INK, "start", "bold")

    s.text(60, 240, "参考跨", 30, INK, "start", "bold")
    # 参考轴：50 / 2(D,红描边) / 10 / 15（深蓝）
    y = 250
    x = 60
    for ln, lab, is_d in ((50, "50", False), (2, "2D", True), (10, "10", False),
                          (15, "15", False)):
        if is_d:
            s.rect(x, y, ln * PX_PER_BP, 40, BLUE, RED, 5, rx=4)
            s.text(x + ln * PX_PER_BP // 2, y - 10, lab, 30, RED, "middle",
                   "bold")
        else:
            s.rect(x, y, ln * PX_PER_BP, 40, BLUE, rx=4)
            s.text(x + ln * PX_PER_BP // 2, y + 28, lab, 30, WHITE, "middle",
                   "bold")
        x += ln * PX_PER_BP
    s.text(630, y + 28, "= 77", 30, INK, "start", "bold")

    s.text(60, 334, "M ≠ 完全匹配，差异看 NM", 30, INK, "start", "bold")

    # ---- 下组：15S85M ----
    s.text(60, 404, "15S85M", 32, BLUE, "start", "bold")
    s.text(700, 418, "= 100", 30, INK, "middle", "bold")
    s.rect(60, 430, 15 * PX_PER_BP, 40, ORANGE, rx=4)
    s.text(60 + 15 * PX_PER_BP // 2, 458, "15", 30, INK, "middle", "bold")
    s.rect(60 + 15 * PX_PER_BP, 430, 85 * PX_PER_BP, 40, CYAN, rx=4)
    s.text(60 + 15 * PX_PER_BP + 85 * PX_PER_BP // 2, 458, "85", 30, WHITE,
           "middle", "bold")
    s.text(112, 505, "留在 SEQ", 30, INK, "middle", "bold")

    s.text(60, 552, "参考跨", 30, INK, "start", "bold")
    s.rect(60, 560, 85 * PX_PER_BP, 40, BLUE, rx=4)
    s.text(60 + 85 * PX_PER_BP // 2, 588, "85", 30, WHITE, "middle", "bold")
    s.text(672, 588, "= 85", 30, INK, "start", "bold")

    s.save("07_cigar_accounting.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
