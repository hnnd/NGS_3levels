#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_pcr_duplicate_support.py — 生成 07_pcr_duplicate_support.svg
（FIG-M03-10：PCR 早期错误 8 拷贝放大与去重前后对账）【data-plot】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-10（P22，cols 一栏，800×700）。
数据：textbook/demos/ch10_pcr_duplicate_support.py Part 1（n=24, K=8, D=31）
现跑核对：去重前 AD=23,8（ALT 25.8%）QUAL 91.9；去重后 AD=23,1（ALT 4.2%）
QUAL 6.7；表观重复率 7/31 ≈ 22.6%。图内中文按方案（单分子扩增 虚假变异
证据坍缩 真实证据 变异丢弃）。D135（2026-11-10，总编复检）：图内英文说明
短语已译中文，工具名/字段名/命令/参数保留英文，字数不再按 ≤30 字核验。
依据：教材 §10.4.2。
"""
import math

from svghelp import *  # noqa: F401,F403

N, K, Q = 24, 8, 0.01


def phred_tail(x, d, q):
    if x <= 0:
        return 0.0
    cdf = sum(math.comb(d, k) * q ** k * (1.0 - q) ** (d - k)
              for k in range(x))
    return -10.0 * math.log10(max(1.0 - cdf, 1e-300))


def main():
    D = N - 1 + K
    dup_rate = (K - 1) / D
    pb, pa = phred_tail(K, D, Q), phred_tail(1, N, Q)
    assert abs(pb - 91.9) < 0.05 and abs(pa - 6.7) < 0.05
    assert abs(K / D - 0.258) < 0.0005 and abs(1 / N - 0.042) < 0.0005
    assert abs(dup_rate - 0.226) < 0.0005
    print(f"check vs demos: AD 23,{K}/23,1; QUAL {pb:.1f}/{pa:.1f}; "
          f"dup {dup_rate:.1%}")

    s = SVG(800, 700)

    def panel(x, t1, t2, tcol):
        s.rect(x, 70, 350, 480, WHITE, PANEL, 3, rx=14)
        s.text(x + 175, 112, t1, 30, tcol, "middle", "bold")
        s.text(x + 175, 150, t2, 30, GRAY, "middle")

    def hbar(x, y, v, col, label):
        w = max(v * 11, 14)
        s.rect(x, y, w, 38, col, None, rx=5)
        s.text(x - 14, y + 30, label, 30, GRAY, "end")
        s.text(x + w + 14, y + 30, str(v), 32, col, "start", "bold")

    # 左：去重前
    panel(40, "单分子扩增", "去重前  D=31", RED)
    hbar(100, 190, 23, BLUE, "REF")
    hbar(100, 262, 8, RED, "ALT")
    s.text(215, 350, "AD = 23,8", 32, INK, "middle", "bold")
    s.text(215, 392, "ALT 25.8%", 30, RED, "middle", "bold")
    s.rect(80, 420, 270, 58, RED_TINT, RED, 4, rx=10)
    s.text(215, 461, "QUAL 91.9", 32, RED, "middle", "bold")
    s.rect(60, 494, 310, 48, RED_TINT, RED, 4, rx=10)
    s.text(215, 529, "虚假变异", 32, RED, "middle", "bold")

    # 右：去重后
    panel(410, "证据坍缩  真实证据", "去重后  D=24", GREEN)
    hbar(470, 190, 23, BLUE, "REF")
    hbar(470, 262, 1, GREEN, "ALT")
    s.text(585, 350, "AD = 23,1", 32, INK, "middle", "bold")
    s.text(585, 392, "ALT 4.2%", 30, GREEN, "middle", "bold")
    s.rect(450, 420, 270, 58, GREEN_TINT, GREEN, 4, rx=10)
    s.text(585, 461, "QUAL 6.7", 32, GREEN, "middle", "bold")
    s.rect(430, 494, 310, 48, GREEN_TINT, GREEN, 4, rx=10)
    s.text(585, 529, "变异丢弃", 32, GREEN, "middle", "bold")

    # 底部对账条
    s.rect(40, 580, 720, 58, BLUE_TINT, BLUE, 4, rx=12)
    s.text(400, 621, f"D={D}  表观重复率 (K-1)/D = 7/31 ≈ {dup_rate:.1%}",
           32, BLUE, "middle", "bold")
    s.text(400, 676, "合成算例： ch10_pcr_duplicate_support.py Part 1",
           30, GRAY, "middle")
    s.save("07_pcr_duplicate_support.svg")


if __name__ == "__main__":
    main()
