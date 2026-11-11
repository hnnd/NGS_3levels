#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_softclip_three_causes.py — 生成 06_softclip_three_causes.svg（FIG-U05-06：软剪切三类解释）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-06（P25，cols 一栏，viewBox 800×700）。
三联面板共用图式「多条读段的 S 段落在参考同一坐标附近」：
①接头残留（S 在一端、长度随修剪变）②真实分化/断点（S 聚集＋分裂比对）③参考缺口（各样本一致）。
依据教材 §7.4.3 L160 三类特征逐条。图内不写比例数字。
注：汉字预算 ≤30（方案角标若全写中文为 37 字超限），三张角标按「轴与图例用英文」
（04_slides/README）改写为英文，语义与教材 L160 逐条对应。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 06_softclip_three_causes.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    panels = [
        (30, "接头残留", ORANGE),
        (285, "分化或断点", PURPLE),
        (540, "参考缺口", BLUE),
    ]
    for x, title, color in panels:
        s.rect(x, 40, 220, 470, WHITE, color, 5, rx=16)
        s.text(x + 110, 92, title, 32, INK, "middle", "bold")

    # ---- ① 接头残留：S 集中在读段一端、长度随修剪参数变化 ----
    tip_x = 225
    rows = [140, 196, 252]
    # 左端对齐（比对起点一致），S 长度不同
    s.rect(60, rows[0], 120, 26, CYAN, rx=5)
    s.rect(180, rows[0], 30, 26, ORANGE, rx=5)
    s.rect(60, rows[1], 100, 26, CYAN, rx=5)
    s.rect(160, rows[1], 50, 26, ORANGE, rx=5)
    s.rect(60, rows[2], 130, 26, CYAN, rx=5)
    s.rect(190, rows[2], 35, 26, ORANGE, rx=5)
    s.line(60, 420, 240, 420, BLUE, 6)
    s.text(140, 462, "varies with", 30, GRAY, "middle", "bold")
    s.text(140, 498, "trimming", 30, GRAY, "middle", "bold")

    # ---- ② 真实分化/断点：S 聚集同一坐标 + 一条读段拆两落 ----
    s.rect(350, 140, 105, 26, CYAN, rx=5)
    s.rect(455, 140, 30, 26, PURPLE, rx=5)
    s.rect(380, 196, 75, 26, CYAN, rx=5)
    s.rect(455, 196, 30, 26, PURPLE, rx=5)
    s.rect(325, 252, 130, 26, CYAN, rx=5)
    s.rect(455, 252, 30, 26, PURPLE, rx=5)
    # 分裂比对：一段贴轴、一段落到远处（虚线相连 = 同一条读段）
    s.rect(310, 300, 70, 26, CYAN, rx=5)
    s.path("M 380 313 C 410 313, 415 237, 445 237", PURPLE, 4, dash="10 8")
    s.rect(445, 224, 50, 26, PURPLE, rx=5)
    s.line(315, 420, 495, 420, BLUE, 6)
    s.text(395, 462, "with split", 30, GRAY, "middle", "bold")
    s.text(395, 498, "alignments", 30, GRAY, "middle", "bold")

    # ---- ③ 参考缺口：各样本在同一坐标露出同款 S；参考轴在 S 处断开 ----
    for i, y in enumerate((140, 196, 252)):
        s.rect(558, y, 36, 30, BLUE_TINT, BLUE, 3, rx=5)
        s.text(576, y + 23, f"S{i+1}", 30, BLUE, "middle", "bold")
        s.rect(602, y, 88, 30, CYAN, rx=5)
        s.rect(690, y, 30, 30, BLUE, rx=5)
    # 参考轴在 S 聚集处断开一个口（缺口示意）
    s.line(565, 420, 672, 420, BLUE, 6)
    s.line(688, 420, 735, 420, BLUE, 6)
    s.line(672, 412, 680, 428, BLUE, 4)
    s.line(680, 412, 688, 428, BLUE, 4)
    s.text(650, 462, "all samples", 30, GRAY, "middle", "bold")
    s.text(650, 498, "agree", 30, GRAY, "middle", "bold")

    # 底部红条（唯一红）
    s.rect(30, 590, 730, 64, RED, rx=12)
    s.text(395, 633, "只报比例分不清", 34, WHITE, "middle", "bold")

    s.save("06_softclip_three_causes.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
