#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23_pipeline_seven_steps.py — 生成 23_pipeline_seven_steps.svg
（FIG-P04-23：第 44 页 cols 一栏「群体基因组 7 步闭环流水线」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-23（P44，cols，800×700）。
依据：教材 §20.3 的流程骨架与 §20.4.7——① 质控底座（低质量基因型置缺失、不删
位点）→ ② 两套分流（popgen 不滤 MAF / struct 滤 0.05）→ ③ 多样性分化（默认
50 kb 窗只是试算）→ ④ 转 PLINK 做 HWE/LD 剪枝 → ⑤ 量出 LD 半衰距离 →
⑥ 群体结构推断（PCA/ADMIXTURE/TreeMix）→ ⑦ 以半衰的 2–5 倍为窗宽回头重跑 ③。
图内中文严格取方案给定 29 字（4 句）；序号与拉丁缩写属符号。
结构＝7 步蛇形流水线：上行 1→4、下行 5→7，最后一条红色回路从第 7 步绕回第 3 步
（回补窗宽），三句判读分别标在第 1、第 2、第 3 步下面。
红只用于回补回路与「量半衰回补窗宽」一句（同一处语义）。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 23_pipeline_seven_steps.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["质控底座置缺失", "两套分流各司其职", "多样性结构连锁", "量半衰回补窗宽"]
TEXT = "".join(PHRASES)

STEPS = [("1", "VCF", ""), ("2", "split", ""), ("3", "diversity", ""),
         ("4", "PLINK", ""), ("5", "LD", ""), ("6", "structure", ""),
         ("7", "iterate", "")]


def box(s, cx, cy, num, label, sub, col, tint):
    s.rect(cx - 76, cy - 50, 152, 100, tint, col, 4, rx=12)
    s.text(cx, cy + 2, num, 36, col, "middle", "bold")
    s.text(cx, cy + 38, label, 30, col, "middle", "bold")
    if sub:
        s.text(cx, cy + 66, sub, 30, col, "middle")


def main():
    s = SVG(800, 700, "Seven-step population genomics loop", plan=TEXT)

    xs = (104, 294, 484, 674)
    for i, cx in enumerate(xs):
        box(s, cx, 200, *STEPS[i], BLUE, BLUE_TINT)
    for cx, step in zip((674, 484, 294), STEPS[4:]):
        box(s, cx, 440, *step, CYAN_DEEP, CYAN_TINT)

    # 上行与下行的连接箭头
    for x0, x1 in ((180, 218), (370, 408), (560, 598)):
        s.arrow(x0, 200, x1, 200, BLUE, 5, 13)
    s.arrow(674, 250, 674, 390, BLUE, 5, 13)
    for x0, x1 in ((598, 560), (408, 370)):
        s.arrow(x0, 440, x1, 440, BLUE, 5, 13)

    # 回补回路：第 7 步 → 第 3 步
    s.path("M 294 490 L 294 566 L 16 566 L 16 96 L 484 96 L 484 150",
           RED, 5, dash="14 10")
    s.polygon([(484, 150), (466, 122), (502, 122)], RED)
    s.text(300, 78, PHRASES[3], 30, RED, "middle", "bold")

    # 三句判读（各按 3–5 字折成两行，避免越过相邻步）
    notes = [(104, BLUE, ("质控底座", "置缺失")),
             (294, CYAN_DEEP, ("两套分流", "各司其职")),
             (484, BLUE, ("多样性结构", "连锁"))]
    for cx, col, lines in notes:
        s.text(cx, 302, lines[0], 30, col, "middle", "bold")
        s.text(cx, 344, lines[1], 30, col, "middle", "bold")

    s.save("23_pipeline_seven_steps.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
