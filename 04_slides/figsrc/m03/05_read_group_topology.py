#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_read_group_topology.py — 生成 05_read_group_topology.svg
（FIG-M03-08：@RG 四核心标签到下游消费者的映射拓扑）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-08（P20，cols 一栏，800×700）。
图内中文按方案（读段标签 比对单元 样本列 平台错误率 文库去重边界 缺一报错）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文（编辑器示例
"each tag feeds one consumer" → "每个标签各有下游使用者"），工具名/字段名/
命令/参数保留英文，字数不再按 ≤30 字核验。依据：教材 §7.5.4、§10.4.2。
无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 50, "@RG → 下游", 36, INK, "middle", "bold")

    # 左：@RG 四标签
    s.rect(40, 80, 240, 540, BLUE_TINT, BLUE, 5, rx=16)
    s.text(160, 126, "读段标签", 32, BLUE, "middle", "bold")
    tags = [("ID", BLUE), ("SM", CYAN_DEEP), ("PL", PURPLE), ("LB", GREEN)]
    for i, (t, col) in enumerate(tags):
        y = 160 + i * 110
        s.rect(65, y, 190, 74, WHITE, col, 5, rx=12)
        s.text(160, y + 50, f"@RG {t}", 34, col, "middle", "bold")

    # 右：四个下游消费者
    cons = [
        (100, "比对单元", "SAM 记录键", BLUE, "ID"),
        (245, "样本列", "gVCF 合并", CYAN_DEEP, "SM"),
        (390, "平台错误率", "BQSR 模型", PURPLE, "PL"),
        (535, "文库去重边界", "MarkDup", GREEN, "LB"),
    ]
    for y, t1, t2, col, tag in cons:
        s.arrow(280, y + 37, 340, y + 37, col, 6)
        s.rect(340, y, 310, 84, WHITE, col, 5, rx=12)
        s.text(495, y + 38, t1, 32, col, "middle", "bold")
        s.text(495, y + 70, t2, 30, GRAY, "middle")

    # 警示
    s.rect(680, 250, 100, 190, RED_TINT, RED, 5, rx=14)
    s.text(730, 306, "缺一", 32, RED, "middle", "bold")
    s.text(730, 348, "报错", 32, RED, "middle", "bold")
    s.text(730, 398, "致命", 30, RED, "middle")
    for yy in (137, 282, 427, 572):
        s.line(650, yy, 680, 330, RED, 3, dash="9 9")

    s.text(400, 664, "每个标签各有下游使用者；缺标签 → GATK 报错",
           30, GRAY, "middle")
    s.save("05_read_group_topology.svg")


if __name__ == "__main__":
    main()
