#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_asymmetric_leakage.py — 生成 10_asymmetric_leakage.svg
（FIG-P03-10：第 24 页 cols 一栏「交叉比对渗漏手算规则与非对称放大天平」）【data-plot】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-10（P24，cols，800×700）。
依据：教材 §16.4.3 L189–197——保守区读段在两物种间互相误配，渗漏率 ε = 0.1% 恒定，
但两侧基数悬殊：宿主漏进病原的伪计数 ε(1−f_P) 相对病原真实份额 f_P 放大成
ε(1−f_P)/f_P = 19.9%（f_P = 0.5%）；病原漏进宿主只有 ε f_P/(1−f_P) = 0.0005%，
两者相差四个数量级，同一 ε 在两侧的后果完全不对称。
数字入口：`textbook/demos/ch16_cross_mapping_leakage.py --selftest` Part 0（现跑打印
「p = 0.5%：19.900%（讲义印 19.9%）」与反向 0.0005%）。本脚本直接 import 该 demo 的
`closed_form(c, p)` 用同一参数（c = 0.001、p = 0.005）复算并断言，不一致即失败退出；
见回执核对表。
图内中文严格取方案给定 30 字（4 句）。`ε`、`f_P`、百分数与 `0.1%` 属符号，不计汉字。
结构＝三条横带：① 两物种份额条（宿主 99.5% 长条、病原 0.5% 细条）；② 宿主→病原放大
（红色高柱 19.9%）；③ 病原→宿主几乎为零（青蓝小点 0.0005%）；底部公式与结论。
配色：深蓝＝宿主，浅橙＝病原，红色只标「虚增两成」与「四量级」两处。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_asymmetric_leakage.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from svghelp import *                                        # noqa: E402,F401,F403
from ch16_cross_mapping_leakage import closed_form           # noqa: E402

PHRASES = ["宿主漏千分之一", "病原侧虚增两成", "宿主侧仅百万分五",
           "非对称放大四量级"]
TEXT = "".join(PHRASES)
EPS, F_P = 0.001, 0.005                   # 讲义 §4.3 的 ε 与侵染早期 f_P
REF_PATH, REF_HOST = 0.199, 5.025126e-06  # demos 现跑：19.900% 与 0.0005%（比值口径）


def numbers():
    cf = closed_form(EPS, F_P)
    got = (cf["naive_dual_path"], cf["naive_dual_host"])
    for v, ref in zip(got, (REF_PATH, REF_HOST)):
        if abs(v - ref) > 1e-9:
            raise SystemExit(f"图面数字与 demos 现跑不一致：got={v} ref={ref}")
    return got


def main():
    p_amp, h_amp = numbers()
    s = SVG(800, 700, "Asymmetric leakage between two species", plan=TEXT)

    # ---------- ① 两物种份额条：宿主 99.5%、病原 0.5% ----------
    s.text(50, 132, "99.5%", 30, BLUE, "start", "bold")
    s.text(742, 132, "0.5%", 30, ORANGE, "end", "bold")
    s.rect(50, 58, 694, 28, BLUE, None, 0, rx=10)
    s.rect(744, 52, 16, 40, ORANGE, None, 0, rx=4)      # 0.5% 细条（放大显示）

    # ---------- ② 宿主 → 病原：ε 放大成 19.9%（红色高柱）----------
    s.text(60, 200, PHRASES[0], 30, INK, "start", "bold")
    s.chip(60, 280, "0.1%", 30, ORANGE_TINT, ORANGE, ORANGE)
    s.arrow(186, 280, 240, 280, GRAY, 5, 14)
    s.rect(250, 218, 140, 152, RED, None, 0, rx=8)       # 柱高对应 19.9%
    s.text(410, 268, PHRASES[1], 30, RED, "start", "bold")
    s.text(410, 336, f"{p_amp * 100:.1f}%", 40, RED, "start", "bold")
    s.line(40, 372, 760, 372, GRAY, 3)

    # ---------- ③ 病原 → 宿主：ε 只剩 0.0005%（青蓝小点）----------
    s.text(60, 446, PHRASES[2], 30, INK, "start", "bold")
    s.chip(60, 520, "0.1%", 30, CYAN_TINT, CYAN, CYAN)
    s.arrow(186, 520, 240, 520, GRAY, 5, 14)
    s.circle(316, 552, 9, CYAN)
    s.text(344, 556, f"{h_amp * 100:.4f}%", 30, CYAN_DEEP, "start", "bold")
    s.line(40, 566, 760, 566, GRAY, 3)

    # ---------- ④ 底部：公式卡 + 结论条 ----------
    s.rect(44, 592, 342, 84, WHITE, BLUE, 3, rx=12)
    s.text(215, 648, "ε (1 − f_P) / f_P", 30, BLUE, "middle", "bold")
    s.band(408, 592, 344, 84, PHRASES[3], RED, WHITE, 32)
    s.save("10_asymmetric_leakage.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
