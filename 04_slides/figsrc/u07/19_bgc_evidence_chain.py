#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_bgc_evidence_chain.py — 生成 19_bgc_evidence_chain.svg（FIG-U07-19：次级代谢基因簇四级证据链，FT09-02）

方案：reviews/course/U07_FIGP_001.md §4.2 FIG-U07-19（P60，cols 一栏，viewBox 800×700）。
数据：无量字数字。DNA 预测 → 转录表达 → 代谢产物 → 生物活性四级证据；
antiSMASH 结果停在第 1 级，预测非合成、必须化学证据（教材 §9.4.8 L328–344、
§9.5.4；figures/ch09_figures.yml FT09-02 落地，替代 hold_redraw 的 F09-05，
图内坚决不出现 MIBiG 相似度阈值）。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 19_bgc_evidence_chain.py
"""
from svghelp import *  # noqa: F401,F403

STEPS = [
    ("基因在", "DNA", BLUE, 40, 420),
    ("表达在", "RNA-seq", CYAN_DEEP, 230, 330),
    ("产物在", "compound", GREEN, 420, 240),
    ("活性在", "activity", ORANGE, 610, 150),
]


def main():
    s = SVG(800, 700)

    # 四级阶梯（证据等级递进，底色逐级加深语义）
    for i, (name, sub, color, x, y) in enumerate(STEPS):
        s.rect(x, y, 150, 90, color, rx=12)
        s.text(x + 10, y + 40, name, 32, WHITE, "start", "bold")
        s.text(x + 75, y + 72, sub, 30, WHITE, "middle")
        s.circle(x + 130, y + 22, 15, WHITE)
        s.text(x + 130, y + 32, str(i + 1), 30, color, "middle", "bold")

    # 沿阶梯上方的虚线推进箭头（不压台阶文字）
    s.polyline([(130, 398), (688, 136)], GRAY, 4, dash="14 10")
    s.polygon([(688, 136), (662, 140), (678, 162)], GRAY)

    # 1 → 3 级之间的鸿沟：红色警示叉（红色语义处 1）
    s.path(f"M 232 210 L 282 260 M 282 210 L 232 260", RED, 9)

    # 底部红色结论条（红色语义处 2）
    s.rect(190, 580, 420, 60, RED, rx=12)
    s.text(400, 622, "预测非合成，必须化学证据", 32, WHITE, "middle", "bold")

    s.save("19_bgc_evidence_chain.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
