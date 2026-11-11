#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_depth_backcalculation.py — 生成 05_depth_backcalculation.svg
（FIG-P03-05：第 17 页 cols 一栏「归属计数倒推算术天平」）【data-plot】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-05（P17，cols，800×700）。
依据：教材 §16.4.1.1 L86–92——`D_used = P / f_P`；早期 `f_P = 0.5%`、病原侧需要
`P = 1×10⁷` 条计数时归属计数 `2×10⁹`（20 亿），`P = 2×10⁷` 时 `4×10⁹`（40 亿）。
数字入口：`textbook/demos/ch16_pathogen_power.py --selftest` Part 0（现跑打印
「P = 1e+07 … → D = P/p = 2e+09」与「4e+09」，并被 selftest 断言为讲义 20 亿/40 亿）。
本脚本按同一闭式重算并断言，不一致即 `raise SystemExit`；见回执核对表。
图内中文严格取方案给定 27 字（4 句）。`P`、`D_used`、`f_P` 与数字属符号，不计汉字。
结构＝三栏对账：左栏病原侧需求（橙色砝码芯片）、中栏「占比千分之五」的折算、
右栏落入基因注释的总归属计数（深蓝柱，2 倍关系按长度等比绘制）。
配色：橙色＝病原需求，深蓝＝总归属，红色只标「常规预算不可行」一处警示。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_depth_backcalculation.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["占比千分之五", "病原需千万读段", "总归属需二十亿", "常规预算不可行"]
TEXT = "".join(PHRASES)
F_PATH = 0.005
REQ = [(1e7, 2e9, ("1", "7"), ("2", "9")),
       (2e7, 4e9, ("2", "7"), ("4", "9"))]


def numbers():
    got = [(p, p / F_PATH) for p, _, _, _ in REQ]
    for (p, d), (p_ref, d_ref, _, _) in zip(got, REQ):
        if abs(p - p_ref) > 1 or abs(d - d_ref) > 1:
            raise SystemExit(f"图面数字与 demos 现跑不一致：P={p} D={d}")
    return got


def main():
    got = numbers()
    s = SVG(800, 700, "Back-calculating the required depth", plan=TEXT)

    # ---------- 顶部公式条 ----------
    s.rect(50, 46, 700, 92, WHITE, BLUE, 4, rx=14)
    s.text(400, 108, "D_used = P / f_P", 36, BLUE, "middle", "bold")

    # ---------- 三栏表头 ----------
    s.text(126, 200, PHRASES[1], 30, ORANGE, "middle", "bold")
    s.text(330, 200, PHRASES[0], 30, BLUE, "middle", "bold")
    s.text(750, 200, PHRASES[2], 30, BLUE, "end", "bold")
    s.line(50, 220, 750, 220, PANEL, 4)

    # ---------- 两档对账：左橙芯片 → 中折算 → 右深蓝柱（等长等比）----------
    scale = 214.0 / 4e9                                     # 4×10⁹ → 214 px
    for i, (_, d, p_sci, d_sci) in enumerate(REQ):
        y = 296 + i * 140
        # 芯片宽 210、字号 30：给上标留出净空（cairosvg 的实际字宽比近似估计略宽，
        # 宽 180 时上标「7」会贴到右边框上）。anchor 用 start——cairosvg 对
        # text-anchor=middle 的 <text> 内嵌 tspan 居中会算偏，上标会被甩到远处。
        s.rect(52, y - 40, 210, 80, ORANGE_TINT, ORANGE, 4, rx=12)
        s.sci(78, y + 11, "1×10" if i == 0 else "2×10",
              p_sci[1], 30, ORANGE, "start", "bold")
        s.arrow(272, y, 306, y, GRAY, 5, 14)
        s.text(320, y + 11, "÷ 0.005", 30, GRAY, "start")
        w = d * scale
        s.rect(438, y - 34, w, 68, BLUE, None, 0, rx=10)
        s.sci(438 + w + 12, y + 11, d_sci[0] + "×10", d_sci[1], 30,
              BLUE, "start", "bold")

    # ---------- 底部结论（唯一红色警示）----------
    s.band(120, 556, 560, 80, PHRASES[3], RED, WHITE, 32)
    s.save("05_depth_backcalculation.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())
