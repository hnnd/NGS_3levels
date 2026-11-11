#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_maf_fst_dual_impact.py — 生成 09_maf_fst_dual_impact.svg
（FIG-P04-09：第 22 页 cols 一栏「MAF 过滤对全基因组 F_ST 的双向冲击」）【data-plot】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-09（P22，cols，800×700）。
依据：教材 §20.4.2——稀有变异几乎只添分母不添分子，剔出真实稀有类后
全基因组 ΣN/ΣD 由 0.0757 升到 0.0841（1.11 倍）；按观测 min(p̂1, p̂2) ≥ 0.05
过滤会顺带剔掉「一群固定」的高分化位点，读数反降到 0.0634。
数字入口：`textbook/demos/ch20_fst_average_trap.py --selftest` Part 1
（两群各 20 条单倍体、10 000 个 SNP、种子 20261104；demo 现跑打印
0.0757 / 0.0841（1.11 倍）/ 0.0634）。本脚本直接调用该 demo 的 `run()`
重算三条读数并断言，不一致即失败退出；见回执核对表。
图内中文严格取方案给定 27 字（3 句，每句按 4–5 字折成两行放在柱下）；
数字与 × 属符号。
结构＝三档阶梯柱（全量 / 剔真实稀有 / 按观测频率滤）＋一条 1.11 倍上升箭头。
红只标「滤观测频率反向降低」一处。
无网络；随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 09_maf_fst_dual_impact.py
"""
import contextlib
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from svghelp import *                                        # noqa: E402,F401,F403
from ch20_fst_average_trap import (hudson_components, make_snps,  # noqa: E402
                                   run)
import numpy as np                                           # noqa: E402

PHRASES = ["滤真实稀有读数抬高", "全量读数零点零七六", "滤观测频率反向降低"]
TEXT = "".join(PHRASES)

REF = dict(all=0.0757, no_rare=0.0841, obs=0.0634, ratio=1.11)


def numbers():
    """按 demo 的同一设定重算三档读数（demo 内部同序抽取，固定种子可复现）。"""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = run(5000, 5000, 50, 0.20, 0.005, 20261104)
    n1 = n2 = 20
    rng = np.random.default_rng(20261104)
    p1, p2, _ = make_snps(5000, 5000, 0.20, 0.005, n1, n2, rng)
    N, D = hudson_components(p1, p2, n1, n2)
    obs_maf = np.minimum(p1, p2)                 # vcftools --maf 0.05 的实参口径
    got = dict(all=float(N.sum() / D.sum()),
               no_rare=float(r["fst_no_rare"]),
               obs=float(N[obs_maf >= 0.05].sum() / D[obs_maf >= 0.05].sum()))
    for k, v in got.items():
        if abs(v - REF[k]) > 5e-4:
            raise SystemExit(f"图面数字与 demos 现跑不一致：{k}={v:.4f}")
    ratio = got["no_rare"] / got["all"]
    if abs(ratio - REF["ratio"]) > 0.006:
        raise SystemExit(f"1.11 倍不一致：{ratio:.3f}")
    return got, ratio


def main():
    d, ratio = numbers()
    s = SVG(800, 700, "MAF filtering pushes F_ST both ways", plan=TEXT)

    ybase, vmax, hpl = 470, 0.10, 330
    yv = lambda v: ybase - v / vmax * hpl

    s.arrow(84, ybase, 748, ybase, BLUE, 5, 14)
    s.arrow(84, ybase, 84, ybase - hpl - 14, BLUE, 5, 14)
    for v in (0.00, 0.05, 0.10):
        y = yv(v)
        s.line(76, y, 84, y, BLUE, 3)
        s.text(64, y + 10, f"{v:.2f}", 30, GRAY, "end")

    bars = [(170, d["all"], BLUE, ("全量读数", "零点零七六"), INK),
            (400, d["no_rare"], CYAN_DEEP, ("滤真实稀有", "读数抬高"), CYAN_DEEP),
            (630, d["obs"], RED, ("滤观测频率", "反向降低"), RED)]
    for cx, v, col, lines, tcol in bars:
        top = yv(v)
        s.rect(cx - 60, top, 120, ybase - top, col, None, 0, rx=8)
        s.text(cx, top + 50, f"{v:.4f}", 30, WHITE, "middle", "bold")
        s.text(cx, ybase + 50, lines[0], 30, tcol, "middle", "bold")
        s.text(cx, ybase + 96, lines[1], 30, tcol, "middle", "bold")

    # 1.11 倍：全量 → 剔真实稀有的上升
    s.arrow(236, yv(d["all"]) - 6, 336, yv(d["no_rare"]) - 6, GRAY, 4, 12,
            dash="10 7")
    s.text(286, 168, f"×{ratio:.2f}", 30, GRAY, "middle", "bold")

    s.save("09_maf_fst_dual_impact.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())
