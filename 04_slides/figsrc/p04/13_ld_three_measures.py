#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_ld_three_measures.py — 生成 13_ld_three_measures.svg
（FIG-P04-13：第 29 页 cols 一栏「D、D′、r² 各答一个不同的问题」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-13（P29，cols，800×700）。
依据：教材 §20.4.4 的三度量表——D = p_AB − p_A p_B 是配子联合频率偏离独立期望
多少（随边际频率变、不可跨位点比）；D′ = D/D_max 回答历史上有没有发生过重组
（小样本与稀有位点偏高，一个配子型没抽到就 D′ = 1，适合划单倍型块）；
r² = D²/(p_A p_a p_B p_b) 回答知道一个位点能推出多少另一个，GWAS 样本量放大
1/r² 倍。MAF 0.02 与 0.48 时 D′ = 1 只对应 r² = 0.0221。
数字入口：教材 §20.4.4（20.9 第 3 题给全步骤）；本脚本按同一闭式重算
r² = D_max²/(p_A p_a p_B p_b) 并断言 0.0221，不一致即失败退出；见回执核对表。
图内中文严格取方案给定 30 字（4 句）；公式与数字属符号。
结构＝三行度量卡（名字 + 定义式 + 一句判读）＋底部一个 MAF 0.02/0.48 的算例条。
绿只标「只认相关平方」一处。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_ld_three_measures.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["偏离独立期望多少", "历史上重组过没有", "替代因果位点程度", "只认相关平方"]
TEXT = "".join(PHRASES)

P_A, P_B = 0.02, 0.48


def numbers():
    d_max = min(P_A * (1 - P_B), (1 - P_A) * P_B)
    r2 = d_max ** 2 / (P_A * (1 - P_A) * P_B * (1 - P_B))
    if abs(r2 - 0.0221) > 5e-5:
        raise SystemExit(f"r² 应为 0.0221，实际 {r2:.4f}")
    return r2


def main():
    r2 = numbers()
    s = SVG(800, 700, "D, D prime and r squared answer different questions",
            plan=TEXT)

    rows = [
        (44, "D", "D = p_AB − p_A p_B", PHRASES[0], BLUE, BLUE_TINT),
        (198, "D′", "D′ = D / D_max", PHRASES[1], CYAN_DEEP, CYAN_TINT),
        (352, "r²", "r² = D² / (p_A p_a p_B p_b)", PHRASES[2], BLUE, BLUE_TINT),
    ]
    for y, name, formula, phrase, col, tint in rows:
        s.rect(30, y, 740, 126, tint, col, 4, rx=14)
        s.circle(96, y + 63, 44, WHITE, col, 4)
        s.text(96, y + 76, name, 34, col, "middle", "bold")
        s.text(160, y + 54, formula, 30, INK, "start")
        s.text(744, y + 110, phrase, 30, col, "end", "bold")

    # ---------- 底部算例条 ----------
    s.rect(30, 500, 740, 66, WHITE, PANEL, 3, rx=12)
    s.text(52, 545, f"MAF {P_A} / {P_B} → D′ = 1, r² = {r2:.4f}", 30, GRAY,
           "start", "bold")

    s.band(120, 594, 560, 78, PHRASES[3], GREEN, WHITE, 32)

    s.save("13_ld_three_measures.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
