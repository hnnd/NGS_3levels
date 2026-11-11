#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""32_jexl_three_layer_defense.py — 生成 32_jexl_three_layer_defense.svg
（FIG-M03-32：JEXL 缺失标签三道防御体系）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-32（P61，cols 一栏，800×700）。
图内中文按方案（头行初筛 逐条分开 逐条计数 全零即空转 防线生效）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；命令与模式
（view -h | grep、'^##INFO'、query '%FILTER'、sort | uniq -c）保留英文，
字数不再按 ≤30 字核验。依据：教材 §10.4.7（L221–226）、§10.5.2。
无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    s.text(400, 44, "三道防线", 36, INK, "middle", "bold")

    lines = [
        (76, "1", "头行初筛", "view -h | grep", "'^##INFO'",
         "已在头行声明", BLUE),
        (256, "2", "逐条分开", "逐行书写", "不拼 '||' 复合式",
         "无单点失效", CYAN_DEEP),
        (436, "3", "逐条计数", "query '%FILTER'", "sort | uniq -c",
         "逐条核验拦截数", GREEN),
    ]
    for y, num, t1, c1, c2, note, col in lines:
        s.rect(40, y, 720, 150, WHITE, col, 5, rx=16)
        s.circle(105, y + 54, 30, col)
        s.text(105, y + 65, num, 32, WHITE, "middle", "bold")
        s.text(245, y + 62, t1, 34, col, "middle", "bold")
        s.rect(350, y + 14, 250, 42, WHITE, col, 3, rx=8)
        s.text(475, y + 45, c1, 30, INK, "middle")
        s.rect(350, y + 64, 250, 42, WHITE, col, 3, rx=8)
        s.text(475, y + 95, c2, 30, INK, "middle")
        s.text(650, y + 136, note, 30, GRAY, "middle")

    s.arrow(400, 226, 400, 252, GRAY, 6)
    s.arrow(400, 406, 400, 432, GRAY, 6)

    s.rect(40, 606, 460, 70, RED_TINT, RED, 4, rx=14)
    s.text(270, 650, "全零即空转", 34, RED, "middle", "bold")
    s.rect(530, 606, 230, 70, GREEN_TINT, GREEN, 4, rx=14)
    s.text(645, 650, "防线生效", 34, GREEN, "middle", "bold")
    s.save("32_jexl_three_layer_defense.svg")


if __name__ == "__main__":
    main()
