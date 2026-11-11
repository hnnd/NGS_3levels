#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""03_avr_pita_closed_loop.py — 生成 03_avr_pita_closed_loop.svg
（FIG-P03-03：第 13 页 cols 一栏「AVR-Pita / Pi-ta 基因对基因验证闭环」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-03（P13，cols，800×700）。
依据：教材 §16.1 L20–26（*AVR-Pita* 位于稻瘟菌染色体末端的不稳定区，田间逃逸既有
缺失也有点突变；*Pi-ta* 抗/感等位只差一个氨基酸；两者直接物理结合触发抗性）、
§16.4.6 L301（结构域/分类器产出候选，功能断言要靠实验）。
图内中文严格取方案给定 26 字（4 句）。基因名 *AVR-Pita* / *Pi-ta* 是术语原名，按方案
保留（COURSE_SYNC §7.10 允许工具与字段名留英文），不加任何英文说明句。
结构：左卡＝病原染色体末端（橙色端粒重复 + 红色基因座 = 不稳定区）；右卡＝水稻受体
两条蛋白条带，仅一处橙色残基不同（等位差单残基）；中央绿色双向箭头＝直接结合；
下方绿色横幅＝触发抗性；底部红色印章＝计算只供候选，右侧烧瓶图标表示湿实验收尾。
配色：深蓝宿主、浅橙病原、绿色示抗性通路，红色只作「计算只供候选」一处警示。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 03_avr_pita_closed_loop.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["端粒不稳定区", "等位差单残基", "直接结合触发抗性", "计算只供候选"]
TEXT = "".join(PHRASES)


def flask(s, cx, cy, color=GREEN):
    """锥形瓶图标：表示「湿实验收尾」这一步，无需文字。"""
    s.path(f"M {cx - 14} {cy - 30} L {cx + 14} {cy - 30} "
           f"L {cx + 14} {cy - 8} L {cx + 30} {cy + 26} "
           f"Q {cx + 34} {cy + 34} {cx + 22} {cy + 34} "
           f"L {cx - 22} {cy + 34} Q {cx - 34} {cy + 34} {cx - 30} {cy + 26} "
           f"L {cx - 14} {cy - 8} Z", color, 4, fill=WHITE)
    s.rect(cx - 16, cy - 34, 32, 8, color, None, 0, rx=3)
    s.path(f"M {cx - 25} {cy + 12} L {cx + 25} {cy + 12}", color, 3)


def main():
    s = SVG(800, 700, "AVR-Pita / Pi-ta gene-for-gene closed loop", plan=TEXT)

    # ---------- 左卡：稻瘟菌染色体末端，AVR-Pita 在端粒不稳定区 ----------
    s.panel(36, 66, 320, 218, ORANGE_TINT, ORANGE, 4)
    s.text(60, 120, "AVR-Pita", 32, ORANGE, "start", "bold")
    s.rect(60, 148, 268, 32, WHITE, ORANGE, 4, rx=8)         # 染色体臂
    for i in range(4):                                       # 端粒重复
        s.rect(62 + i * 20, 150, 13, 28, ORANGE)
    s.polygon([(296, 142), (322, 164), (296, 186)], ORANGE)   # 染色体末端
    s.rect(190, 144, 44, 40, RED_TINT, RED, 4, rx=6)          # 基因座
    s.text(60, 250, PHRASES[0], 30, RED, "start", "bold")

    # ---------- 右卡：水稻受体，抗/感两条等位只差一个残基 ----------
    s.panel(444, 66, 320, 218, BLUE_TINT, BLUE, 4)
    s.text(468, 120, "Pi-ta", 32, BLUE, "start", "bold")
    for row, y in enumerate((146, 186)):                     # 两条等位条带
        s.rect(468, y, 268, 30, WHITE, BLUE, 4, rx=8)
        for i in range(8):
            s.rect(480 + i * 32, y + 2, 24, 26, BLUE_TINT, BLUE, 3, rx=5)
        if row == 1:                                          # 仅此一处不同
            s.rect(480 + 4 * 32, y + 2, 24, 26, ORANGE, ORANGE, 3, rx=5)
    s.text(468, 250, PHRASES[1], 30, BLUE, "start", "bold")

    # ---------- 中央：直接物理结合（双向绿箭头）----------
    s.arrow(362, 184, 418, 184, GREEN, 7, 17)
    s.arrow(418, 200, 362, 200, GREEN, 7, 17)

    # ---------- 下方：结合触发抗性（绿横幅，唯一绿色结论条）----------
    s.band(150, 344, 500, 70, PHRASES[2], GREEN, WHITE, 32)
    s.arrow(90, 306, 90, 340, GREEN, 6, 15)
    s.arrow(710, 306, 710, 340, GREEN, 6, 15)

    # ---------- 底部：印章「计算只供候选」+ 烧瓶＝湿实验收尾 ----------
    s.stamp(330, 528, 330, 96, PHRASES[3], RED, RED, 32)
    s.arrow(506, 528, 552, 528, GRAY, 6, 16)
    flask(s, 636, 522)
    s.save("03_avr_pita_closed_loop.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 26, TEXT
    raise SystemExit(main())
