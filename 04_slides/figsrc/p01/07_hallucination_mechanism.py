#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_hallucination_mechanism.py — 生成 07_hallucination_mechanism.svg
（FIG-P01-08：token 似然优化 vs 命题真实）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-08（P25，cols 一栏，800×700）。
依据：教材 §24.4.2「幻觉的根源要写准」——生成模型最大化的是给定上下文时下一个
token 的条件似然（Σ log P(w_t | w_<t)），不是命题的真实性；知识边界之外的内容
只能按语言形态补齐；降低随机性只改变幻觉的形式与频率，不消除它
（[@ji2023hallucination]）。图内不写「温度 0 仍编造」，不写任何经验频率或准确率：
柱高只表示「按条件似然从高到低挑最像的下一个 token」，无刻度、无数值；下栏的
404 是形态示意（真实伪造串见教材 §24.4.7）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_hallucination_mechanism.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "优化目标非命题真实。平滑表象掩盖虚构后缀。降低随机性不除幻觉。"
BARS = (0.52, 0.74, 1.0, 0.44, 0.26, 0.15)


def main():
    s = SVG(800, 700, "Hallucination: token likelihood vs truth", plan=TEXT)

    # 上栏：语言模型侧——按条件似然排序挑下一个 token（青蓝）
    s.rect(40, 24, 720, 246, "#E7F5F8", CYAN, 4, rx=12)
    s.text(66, 74, "P(next_token | context)", 32, CYAN_DEEP, "start", "bold")
    s.text(720, 74, "argmax", 30, CYAN_DEEP, "end", "bold")
    for i, w in enumerate(BARS):
        x = 76 + i * 110
        h = 130 * w
        s.rect(x, 252 - h, 78, h, CYAN if i < 3 else PANEL)
    s.line(60, 256, 738, 256, CYAN_DEEP, 3)

    # 下栏：科学侧——要的是命题可追溯（深蓝标尺；红＝唯一警示点）
    s.rect(40, 296, 720, 208, BLUE_TINT, BLUE, 4, rx=12)
    s.text(66, 348, "claim: traceable?", 32, BLUE, "start", "bold")
    # 可追溯的论断（绿色）
    s.chip(78, 428, "REF ok", 30, GREEN_TINT, GREEN, INK, anchor="start",
           h=54)
    # 形态补齐出来的后缀（红色虚线槽）
    s.chip(300, 428, "404", 30, RED_TINT, RED, RED, anchor="start", h=54,
           dash="9 6")
    s.arrow(232, 428, 286, 428, GRAY, 5, 13)
    # 右侧：真实论断与补齐串的对齐线
    s.line(420, 372, 420, 480, GRAY, 3, dash="8 7")
    s.text(440, 408, "smooth", 30, GRAY)
    s.text(440, 462, "false", 30, RED, "start", "bold")

    s.caption(["优化目标非命题真实。平滑表象掩盖虚构后缀。",
               "降低随机性不除幻觉。"], [INK, INK], 30, top=536, gap=46,
              pad_top=16)
    s.save("07_hallucination_mechanism.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())
