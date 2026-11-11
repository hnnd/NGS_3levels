#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_depth_conversion_calculation.py — 生成 13_depth_conversion_calculation.svg
（FIG-M01-15：换算账损耗扣除双算例）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-15（P37，cols 一栏，800×700）。
数据（与 demos 现跑一致）：demos/ch13_variance_partition.py --selftest Part 0：
380 Mb × 30× ÷ (0.90 × 0.92) = 13.77 Gb；分母 0.68 例 = 16.76 Gb
（教材 §13.4.4 L230–232 手算同式）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_depth_conversion_calculation.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    # 与 demos Part 0 同式复算（核对表见回执）
    base = 380 * 30 / (0.90 * 0.92) / 1000
    high = 380 * 30 / 0.68 / 1000
    assert abs(base - 13.77) < 0.005, f"基准例应为 13.77 Gb，得 {base:.2f}"
    assert abs(high - 16.76) < 0.005, f"高重复例应为 16.76 Gb，得 {high:.2f}"
    print(f"check: 基准例 {base:.2f} Gb；高重复例 {high:.2f} Gb（demos Part 0 同式）")

    s = SVG(800, 700)

    # 顶部公式框
    s.rect(60, 66, 680, 92, BLUE, rx=14)
    s.text(400, 126, "下单量 = 基因组×深度÷有效", 36, WHITE, "middle", "bold")

    # 左卡：基准例（绿）
    s.rect(60, 210, 320, 220, GREEN_TINT, GREEN, 5, rx=16)
    s.text(220, 276, "基准例：", 32, GREEN, "middle", "bold")
    s.text(220, 330, "13.77 Gb", 34, INK, "middle", "bold")
    s.text(220, 368, "380 Mb × 30×", 30, GRAY, "middle")
    s.text(220, 406, "÷ 0.828", 30, GRAY, "middle")

    # 右卡：高重复/细胞器例（橙）
    s.rect(420, 210, 320, 220, ORANGE_TINT, ORANGE, 5, rx=16)
    s.text(580, 276, "高重复例：", 32, INK, "middle", "bold")
    s.text(580, 330, "16.76 Gb", 34, INK, "middle", "bold")
    s.text(580, 396, "分母 0.68", 30, GRAY, "middle")

    # 底部红色警告（全图唯一红色）
    s.rect(170, 492, 460, 72, RED, rx=14)
    s.text(400, 539, "分母三项须有来源", 34, WHITE, "middle", "bold")

    s.save("13_depth_conversion_calculation.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
