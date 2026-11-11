#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_levels_residue.py — 生成 09_levels_residue.svg
（FIG-U02-09：筛掉一组，水平表还在）【data-plot】

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-09（P30，cols 一栏，viewBox 800×700）。
数据（现跑核对）：Rscript textbook/demos/ch03_factor_levels.R 算例 D——
筛选后 nlevels=2、table: ctrl=0, trt=4；droplevels() 后 nlevels=1。
本脚本 subprocess 现跑该 demo 并解析输出，与上述期望值断言一致后才画图；
图内数字全部来自本次现跑。依据：教材 §3.4.4 L175、§3.10 表。
红 2 处（满额）：ctrl 空位红描边 + 计数 0 红字。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 09_levels_residue.py
"""
import re
import subprocess
import sys
from pathlib import Path

from svghelp import *  # noqa: F401,F403

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
DEMO = ROOT / "textbook" / "demos" / "ch03_factor_levels.R"

EXPECT = dict(n_before=2, ctrl=0, trt=4, n_after=1)


def run_demo():
    out = subprocess.run(["Rscript", str(DEMO)], capture_output=True,
                         text=True, cwd=str(ROOT), check=True).stdout
    m1 = re.search(r"筛选后 nlevels = (\d+) ; table: ctrl=(\d+), trt=(\d+)", out)
    m2 = re.search(r"droplevels 后 nlevels = (\d+)", out)
    if not m1 or not m2:
        raise SystemExit("未能从 demo 输出解析算例 D")
    got = dict(n_before=int(m1.group(1)), ctrl=int(m1.group(2)),
               trt=int(m1.group(3)), n_after=int(m2.group(1)))
    print("demo 算例 D 现跑:", got)
    if got != EXPECT:
        raise SystemExit(f"算例 D 与教材口径不一致: {got} != {EXPECT}")
    return got


def main():
    d = run_demo()
    s = SVG(800, 700)

    s.text(140, 60, "筛选后 levels 不缩", 32, INK, "middle", "bold")
    s.rect(20, 84, 240, 400, WHITE, BLUE, 4, rx=8)
    s.line(40, 430, 250, 430, INK, 3)
    s.rect(60, 150, 80, 280, "none", RED, 4, dash="12 9")
    s.rect(160, 150, 80, 280, GREEN)
    s.text(200, 132, f"trt = {d['trt']}", 30, GREEN, "middle", "bold")
    s.text(100, 466, "ctrl", 30, GRAY, "middle")
    s.text(200, 466, "trt", 30, INK, "middle")
    s.text(140, 528, f"nlevels = {d['n_before']}", 32, BLUE, "middle", "bold")

    s.text(400, 60, "table() 计数", 32, INK, "middle", "bold")
    s.rect(280, 84, 240, 400, WHITE, BLUE, 4, rx=8)
    s.line(310, 250, 490, 250, PANEL, 3)
    s.line(310, 360, 490, 360, PANEL, 3)
    s.text(400, 216, f"ctrl = {d['ctrl']}", 34, RED, "middle", "bold")
    s.text(400, 326, f"trt = {d['trt']}", 34, INK, "middle", "bold")

    s.text(660, 60, "droplevels() 后剩", 32, INK, "middle", "bold")
    s.rect(540, 84, 240, 400, WHITE, BLUE, 4, rx=8)
    s.line(560, 430, 770, 430, INK, 3)
    s.rect(620, 150, 80, 280, GREEN)
    s.text(660, 132, f"trt = {d['trt']}", 30, GREEN, "middle", "bold")
    s.text(660, 466, "trt", 30, INK, "middle")
    s.text(660, 528, f"nlevels = {d['n_after']}", 32, BLUE, "middle", "bold")

    s.rect(20, 596, 760, 60, PANEL, rx=10)
    s.text(400, 637, "demos/ch03_factor_levels.R --selftest", 30, GRAY, "middle")
    s.save("09_levels_residue.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
