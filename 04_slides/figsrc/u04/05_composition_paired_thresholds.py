#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_composition_paired_thresholds.py — 生成 05_composition_paired_thresholds.svg
（FIG-U04-05：组成模块成对阈值阶梯【算法/判读】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-05（P18，cols 一栏，viewBox 800×700）。
左面板 Per base sequence content：A/T 或 G/C 差值超 10%（橙 WARN）、超 20%（FAIL 档）；
右面板 Per sequence GC content：偏离超 15%（橙 WARN）、超 30%（红 FAIL）；
底部红字「对比模型非物种」——红灯比的是理论模型，不是物种真实 GC。
阈值来源：FastQC v0.12.1 Configuration/limits.txt（demos/ch06_perbase_quality.py Part C 同源）。
依据：教材 §6.4.2 L76–82。图内汉字 19，红色 2 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_composition_paired_thresholds.py
"""
from svghelp import *


def main():
    s = SVG(800, 700)

    def panel(px, head1, head2, step1, step2, fail_red):
        s.rect(px, 60, 340, 440, WHITE, stroke=PANEL, sw=3, rx=16)
        s.rect(px, 60, 340, 96, BLUE if px < 400 else CYAN_DEEP, rx=16)
        s.rect(px, 92, 340, 64, BLUE if px < 400 else CYAN_DEEP)
        s.text(px + 170, 104, head1, 30, WHITE, "middle", "bold")
        s.text(px + 170, 142, head2, 30, WHITE, "middle", "bold")
        # 阶梯：左低右高，两级阈值（WARN 橙 / FAIL 红或深橙）
        c2 = RED if fail_red else ORANGE_DEEP
        word1, pct1 = step1.split()
        word2, pct2 = step2.split()
        s.rect(px + 30, 370, 130, 110, ORANGE, rx=10)
        s.text(px + 95, 412, word1, 30, INK, "middle", "bold")
        s.text(px + 95, 456, pct1, 30, INK, "middle", "bold")
        s.rect(px + 180, 260, 130, 110, c2, rx=10)
        s.text(px + 245, 302, word2, 30, WHITE, "middle", "bold")
        s.text(px + 245, 346, pct2, 30, WHITE, "middle", "bold")

    panel(40, "Per base sequence", "content", "差值超 10%", "差值超 20%",
          fail_red=False)
    panel(420, "Per sequence GC", "content", "偏离超 15%", "偏离超 30%",
          fail_red=True)

    # 底部红字横幅
    s.rect(40, 556, 720, 84, RED_TINT, rx=14)
    s.text(400, 612, "对比模型非物种", 34, RED, "middle", "bold")

    s.save("05_composition_paired_thresholds.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
