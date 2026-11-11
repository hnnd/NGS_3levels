#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_deseq2_three_input_states.py — 生成 09_deseq2_three_input_states.svg
（FIG-P01-10：DESeq2 输入三态与取整陷阱）【data-plot】

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-10（P29，cols 一栏，800×700）。
依据：教材 §24.4.4 输入三态表（含小数的 double → `stop: some values in assay
are not integers`；整数值的 double → 只发一句 message `converting counts to
integer mode`；integer → 不发声，1.42.0 与 1.50.2 实测一致）。
图内四个数字全部取自 demos 现跑（textbook/demos/ch24_double_normalization_
sizefactors.py --selftest，2026-11-11，5/5 PASS），见回执核对表：
  原始 counts 文库 max/min = 2.39；size factor 散布 = 2.38×（0.625–1.484）；
  先转 CPM 再 round 后：各列 max/min = 1.0001；size factor 散布 = 1.03×
  （0.983–1.012）。
本脚本不重造数据：直接 import 该 demo 的 make_counts 与 median_of_ratios，用同一组
参数（--n-gene 2000、--seed 20261105）复算，与上列数字不一致即失败退出。
无网络；随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 09_deseq2_three_input_states.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import numpy as np                                    # noqa: E402
from svghelp import *                                 # noqa: E402,F401,F403
from ch24_double_normalization_sizefactors import (   # noqa: E402
    make_counts, median_of_ratios)

TEXT = "输入三态：小数报错，整数值提示信息，整数通过。取整掩盖双重归一化。"
N_GENE, SEED = 2000, 20261105
REF = {"lib_ratio": 2.39, "sf_raw": 2.38, "cpm_lib_ratio": 1.0001,
       "sf_cpm": 1.03}


def numbers():
    cts = make_counts(N_GENE, SEED)
    lib = cts.sum(axis=0)
    sf = median_of_ratios(cts)
    got = {"lib_ratio": round(float(lib.max() / lib.min()), 2),
           "sf_raw": round(float(sf.max() / sf.min()), 2)}
    cpm = np.round(cts / lib[None, :] * 1e6)
    sf2 = median_of_ratios(cpm)
    got["cpm_lib_ratio"] = round(float(cpm.sum(axis=0).max()
                                      / cpm.sum(axis=0).min()), 4)
    got["sf_cpm"] = round(float(sf2.max() / sf2.min()), 2)
    for k, v in REF.items():
        if abs(got[k] - v) > 1e-9:
            raise SystemExit(f"图面数字与 demos 现跑不一致：{k} "
                             f"got={got[k]} ref={v}")
    return got, sf, sf2


def main():
    got, sf, sf2 = numbers()
    s = SVG(800, 700, "DESeq2 input states and the rounding trap", plan=TEXT)

    # 三支：输入形态（深蓝骨架）→ 解释器响应（红/橙/绿）
    branches = [
        ("double  (0.5)", "stop", RED, RED_TINT),
        ("double  (1.0)", "message", ORANGE, ORANGE_TINT),
        ("integer", "silent", GREEN, GREEN_TINT),
    ]
    for i, (inp, resp, edge, tint) in enumerate(branches):
        y = 44 + i * 100
        s.rect(40, y, 250, 76, WHITE, BLUE, 4, rx=10)
        s.text(64, y + 50, inp, 30, INK)
        s.arrow(298, y + 38, 366, y + 38, GRAY, 4, 12)
        s.chip(378, y + 38, resp, 30, tint, edge, INK, anchor="start", h=58)

    # 第 2 支的静默穿透：取整把显性报错降级成一句 message（红警示之二）
    s.line(378, 236, 720, 236, RED, 4, dash="10 8")
    s.cross(732, 236, 12, RED, 7)

    # 底部两栏对比：原始 counts vs CPM 后又取整（橙＝数据层误用，非第二处红）
    s.rect(40, 330, 720, 178, ORANGE_TINT, ORANGE, 4, rx=12)
    s.text(70, 382, "counts", 30, BLUE, "start", "bold")
    s.text(470, 382, "round(CPM)", 30, ORANGE, "start", "bold")
    s.line(446, 350, 446, 486, GRAY, 3, dash="8 7")
    s.text(70, 432, "lib max/min", 30, INK)
    s.text(70, 484, "SF spread", 30, INK)
    s.text(430, 432, f"{got['lib_ratio']:.2f} X", 32, BLUE, "end", "bold")
    s.text(430, 484, f"{got['sf_raw']:.2f} X", 32, BLUE, "end", "bold")
    s.text(680, 432, f"{got['cpm_lib_ratio']:.4f}", 32, ORANGE, "end", "bold")
    s.text(680, 484, f"{got['sf_cpm']:.2f} X", 32, ORANGE, "end", "bold")

    s.caption(["输入三态：小数报错，整数值提示信息，",
               "整数通过。取整掩盖双重归一化。"], [INK, INK], 30,
              top=534, gap=44, pad_top=18)
    s.save("09_deseq2_three_input_states.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())
