#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_pathogen_collinearity.py — 生成 15_pathogen_collinearity.svg
（FIG-P03-15：第 33 页 cols 一栏「病原侧时间与生物量高度共线陷阱」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-15（P33，cols，800×700）。
依据：教材 §16.4.5 L283–287、§16.5.5 L434——in planta 取样时，病原的「侵染时相」与
「菌丝生物量」由同一次取样同时决定：时相越往后，叶片里的菌丝就越多。两个协变量在
实验设计上近乎 1:1 绑定，模型无法把「时间效应」与「生物量效应」分开，任何病原侧
时序系数只能读作相对变化，不能读成绝对表达水平。
图内中文严格取方案给定 30 字（4 句）。`12`、`48 hpi`、`0.5%`、`30%` 为刻度与数值。
结构＝上下两条同向粗箭头（时相推移 / 生物量扩增），中间用红色绑定链把两行逐点扣在
一起，再以红色结论条点明高度共线，末尾蓝色条给出唯一可下的结论。
配色：浅橙＝病原生物量与时相，红色只标共线绑定与结论两处，深蓝＝相对比较框架。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 15_pathogen_collinearity.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["侵染时相推移", "菌丝生物量扩增", "时间与生物量高度共线", "仅能作相对比较"]
TEXT = "".join(PHRASES)
TIES = (300, 402, 504, 606)                  # 绑定链四个横坐标（避开左侧标签）


def main():
    s = SVG(800, 700, "Time and fungal biomass are collinear", plan=TEXT)

    # ---------- 上行：侵染时相推移 12 → 48 hpi ----------
    s.text(60, 120, PHRASES[0], 30, INK, "start", "bold")
    s.arrow(60, 170, 740, 170, ORANGE, 12, 26)
    s.circle(60, 170, 12, ORANGE)
    s.text(60, 216, "12", 30, ORANGE, "start", "bold")
    s.text(740, 216, "48 hpi", 30, ORANGE, "end", "bold")

    # ---------- 下行：菌丝生物量扩增 0.5% → 30% ----------
    s.arrow(60, 430, 740, 430, ORANGE, 12, 26)
    s.text(60, 392, PHRASES[1], 30, INK, "start", "bold")
    s.text(60, 476, "0.5%", 30, ORANGE, "start", "bold")
    s.text(740, 476, "30%", 30, ORANGE, "end", "bold")

    # ---------- 中间：绑定链（红虚线段）＋ 覆盖其上的结论卡 ----------
    for x in TIES:
        s.line(x, 184, x, 268, RED, 5, dash="9 7")
        s.line(x, 352, x, 416, RED, 5, dash="9 7")
    s.rect(170, 272, 460, 76, WHITE, RED, 4, rx=12)
    s.text(400, 322, PHRASES[2], 30, RED, "middle", "bold")

    # ---------- 底部：唯一可下的结论 ----------
    s.band(96, 542, 608, 80, PHRASES[3], BLUE, WHITE, 32)
    s.save("15_pathogen_collinearity.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
