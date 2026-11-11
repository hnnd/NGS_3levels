#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_host_interaction_grid.py — 生成 14_host_interaction_grid.svg
（FIG-P03-14：第 31 页 cols 一栏「宿主侧全因子交互模型 LRT 设计网格」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-14（P31，cols，800×700）。
依据：教材 §16.4.5 L262–273——宿主侧要问的是「哪些基因的响应随接种而改变」，而不是
「哪些基因随时相变化」。全因子模型把接种、时相与两者交互项一起拟合；简约模型只留
主效应、把交互项扣掉；两模型做似然比检验（Δχ²）。关键在每时点都平行的未接种 Mock
行：没有它，昼夜节律、叶龄与取样伤害会被整体读成侵染响应，交互项失去对照基线。
图内中文严格取方案给定 30 字（4 句）。`G11`、`Mock`、`hpi`、`Δχ²` 是样本名、字段名
与统计符号，不作说明性英文。实心点＝接种样本、空心点＝未接种样本（图形语义代替
额外的中文标注）。
配色：深蓝＝宿主网格与简约模型，青蓝＝全模型交互项，红色只标 Mock 行与它的作用两处。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 14_host_interaction_grid.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["接种配未接种三时点", "全模型含交互项", "简约模型扣交互", "剥离节律与伤害"]
TEXT = "".join(PHRASES)

GX, GY, CW, CH = 150, 118, 192, 104          # 网格原点、单格宽高（横 3 列）
HOURS = ("12", "24", "48")                    # 方案给定三时点


def row(s, y, filled, label):
    """一行 3 格 × 3 重复；filled=True 实心（接种）、False 空心（未接种）。"""
    s.text(130, y + CH / 2 + 11, label, 30, BLUE, "end", "bold")
    for j in range(3):
        cx = GX + j * CW + CW / 2
        s.rect(GX + j * CW + 3, y + 3, CW - 6, CH - 6,
               BLUE_TINT if filled else WHITE, BLUE, 3, rx=8)
        for k in (-1, 0, 1):
            dx = cx + k * 36
            dy = y + CH / 2
            if filled:
                s.circle(dx, dy, 13, BLUE)
            else:
                s.circle(dx, dy, 13, WHITE, BLUE, 4)


def main():
    s = SVG(800, 700, "Full-factorial interaction grid with mock rows", plan=TEXT)

    # ---------- 顶部说明 ----------
    s.text(400, 74, PHRASES[0], 30, BLUE, "middle", "bold")

    # ---------- 时相表头 ----------
    for j, h in enumerate(HOURS):
        cx = GX + j * CW + CW / 2
        s.text(cx, 108, h, 30, GRAY, "middle", "bold")

    # ---------- 网格：接种行在上、未接种 Mock 行在下 ----------
    row(s, GY, True, "G11")
    row(s, GY + CH + 12, False, "Mock")

    # Mock 行红框：缺了它就没人剥离本底变化（唯一红色图形标记）
    my = GY + CH + 12
    s.rect(GX - 6, my - 6, CW * 3 + 12, CH + 12, "none", RED, 4, rx=10,
           dash="10 7")

    # ---------- Mock 行的作用（红色结论条）----------
    s.band(96, 372, 608, 74, PHRASES[3], RED, WHITE, 32)
    s.arrow(400, 366, 400, my + CH + 8, RED, 5, 14, dash="8 6")

    # ---------- 两个模型：全模型（含交互）与简约模型（扣交互）----------
    s.chip(216, 502, PHRASES[1], 30, CYAN_TINT, CYAN, INK, h=76,
           anchor="middle", pad=26)
    s.chip(586, 502, PHRASES[2], 30, BLUE_TINT, BLUE, INK, h=76,
           anchor="middle", pad=26)

    # ---------- 收敛到似然比检验 ----------
    s.arrow(216, 542, 348, 588, GRAY, 5, 14)
    s.arrow(586, 542, 452, 588, GRAY, 5, 14)
    s.rect(352, 580, 96, 68, WHITE, BLUE, 4, rx=12)
    s.text(400, 626, "Δχ²", 32, BLUE, "middle", "bold")
    s.save("14_host_interaction_grid.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
