#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""31_self_vs_self_decision_tree.py — 生成 31_self_vs_self_decision_tree.svg
（FIG-M03-31：自比阴性对照四步排查决策树）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-31（P58，cols 一栏，800×700）。
图内中文按方案（自比变异大于零 查倍性 查索引版本 查标签 查重复区）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；命令参数、索引
后缀与登录号（-ploidy 1、.fai/.bwt、@RG SM/LB、segdup、ERR15732332、
GCA_024981335）保留英文，字数不再按 ≤30 字核验。依据：教材 §10.4.9、
§10.5.3、§10.6。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 44, "自比对照门禁", 36, INK, "middle", "bold")

    s.rect(180, 68, 440, 90, BLUE_TINT, BLUE, 4, rx=14)
    s.text(400, 104, "ERR15732332 → GCA_024981335", 30, INK, "middle", "bold")
    s.text(400, 140, "CIX2779 比对自身完成图", 30, GRAY, "middle")

    s.arrow(400, 158, 400, 196, GRAY, 6)
    s.rect(250, 200, 300, 66, WHITE, BLUE, 4, rx=12)
    s.text(400, 242, "SNV 数 ≈ 0 ？", 32, INK, "middle", "bold")

    # 放行支
    s.arrow(550, 233, 640, 233, GREEN, 6)
    s.rect(640, 186, 140, 96, GREEN_TINT, GREEN, 4, rx=12)
    s.text(710, 220, "放行", 30, GREEN, "middle", "bold")
    s.text(710, 252, "12 样本", 30, GREEN, "middle", "bold")
    s.text(710, 284, "联合分型", 30, GREEN, "middle", "bold")

    # 告警支
    s.arrow(400, 266, 400, 306, RED, 6)
    s.rect(200, 310, 400, 62, RED_TINT, RED, 4, rx=12)
    s.text(400, 350, "自比变异大于零", 32, RED, "middle", "bold")

    steps = [
        ("1", "-ploidy 1", "查倍性"),
        ("2", ".fai/.bwt", "查索引版本"),
        ("3", "@RG SM/LB", "查标签"),
        ("4", "segdup", "查重复区"),
    ]
    for i, (num, en, zh) in enumerate(steps):
        x = 50 + i * 185
        s.arrow(400, 372, x + 75, 420, GRAY, 5)
        s.rect(x, 424, 150, 140, WHITE, BLUE, 4, rx=12)
        s.circle(x + 75, 462, 24, BLUE)
        s.text(x + 75, 472, num, 30, WHITE, "middle", "bold")
        s.text(x + 75, 516, zh, 30, INK, "middle", "bold")
        s.text(x + 75, 548, en, 30, GRAY, "middle")
    for i in range(3):
        xa = 50 + i * 185 + 150
        s.arrow(xa + 6, 494, xa + 28, 494, GRAY, 5)

    s.rect(40, 600, 720, 76, GREEN_TINT, GREEN, 4, rx=14)
    s.text(400, 630, "全通过但计数 >0 → 参考有问题",
           30, GREEN, "middle", "bold")
    s.text(400, 660, "孟德尔不一致 = 线索而非上界", 30, GRAY,
           "middle")
    s.save("31_self_vs_self_decision_tree.svg")


if __name__ == "__main__":
    main()
