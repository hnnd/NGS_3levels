#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_reference_fabrication_modes.py — 生成 16_reference_fabrication_modes.svg
（FIG-P01-17：AI 编造引用的三种伪造形态）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-17（P44，cols 一栏，800×700）。
依据：教材 §24.4.7 与 §24.5.2——编造引用不是一种而是三种：
  ① 完全虚构：作者、期刊看着像真的，题名与页码凭空生成，一查即穿；
  ② 真前缀 + 随机后缀：`10.1038/` 是真的，`s41586-023-99999-9` 是拼出来的，
     DOI 解析直接 404；
  ③ 真实文献张冠李戴：DOI、作者、题名全部真实可解析，但被引用来支撑它并不
     支持的论断——脚本查不出来，只能人工读摘要。
右侧拦截面：①②可脚本化（解析/比对），③只能人工。红色 1 处标 ③。
图内文字不含任何真实 DOI 或论文标识（避免出现无法追溯的号码）；`404` 是
HTTP 状态码，属机制说明。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_reference_fabrication_modes.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "编造引用三形态：完全虚构，真前缀假后缀404，真实文献张冠李戴。"
MODES = [
    ("1", "fully_invented", ["fake_title", "fake_pages"], GRAY, PANEL, "script"),
    ("2", "real_prefix · fake_suffix", ["10.1038/  404"], ORANGE, ORANGE_TINT,
     "script"),
    ("3", "real_paper · wrong_claim", ["resolvable", "unsupported_claim"],
     RED, RED_TINT, "manual"),
]


def main():
    s = SVG(800, 700, "Three modes of fabricated citations", plan=TEXT)

    for i, (no, head, lines, edge, tint, how) in enumerate(MODES):
        y = 40 + i * 154
        # 卡片加宽到 500：三种形态的标题串最长 401 单位，470 宽时末字会压到右边框
        s.rect(40, y, 500, 142, tint, edge, 5 if i == 2 else 3, rx=12)
        s.badge(62, y + 40, no, edge if i != 2 else RED, WHITE, 30, "start")
        s.text(116, y + 50, head, 30, edge, "start", "bold")
        for j, ln in enumerate(lines):
            s.text(66, y + 94 + j * 36, ln, 30, INK)

    # 右侧：可拦截手段（每张卡片单独标一行，右侧栏宽 140）
    s.text(716, 112, "script", 30, BLUE, "middle", "bold")
    s.text(716, 266, "script", 30, BLUE, "middle", "bold")
    s.text(716, 420, "manual", 30, PURPLE, "middle", "bold")

    s.caption(["编造引用三形态：完全虚构，",
               "真前缀假后缀404，真实文献张冠李戴。"], [INK, INK], 30,
              top=560, gap=44, pad_top=16)
    s.save("16_reference_fabrication_modes.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 25, TEXT
    raise SystemExit(main())
