#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_size_factor_diagnostic.py — 生成 13_size_factor_diagnostic.svg
（FIG-P03-13：第 29 页 cols 一栏「size factor 诊断散点图」）【data-plot】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-13（P29，cols，800×700）。
依据：教材 §16.4.4 L240–241、§16.5.2 L408——median-of-ratios size factor 的隐含
假设是「多数基因不变」。合并双物种矩阵后，病原份额随时相上涨，占多数的宿主整体
被当成相对上调，size factor 于是把生物量增长吸收进归一化系数：左面板（各自归一化）
四个时相样本都落在 1 线附近；右面板（合并口径）同一批样本随时相单调阶梯下沉。
一旦漂移成立，「多数基因不变」这个前提已被破坏，差异检验在做之前就失效。
数字入口：`textbook/demos/ch16_mixed_tpm_bias.py --selftest` Part 1（现跑：每时相
median(merged/separate) 宿主基因 = 0.9950 / 0.9799 / 0.8995 / 0.6986，随时相单调
下降）。本脚本 import 该 demo 的 `simulate()` 用同一参数复算这四个比值并断言数值与
单调性，不一致即失败退出；见回执核对表。右面板四点是实测值；左面板是「各自归一化
同一批样本」的理想对齐示意，不打印任何数字（图上只有 1 线与横轴时相刻度）。
图内中文严格取方案给定 25 字（4 句）。`ratio` 属坐标轴字段名。
结构＝左右双面板（同一 y 标度 0.66–1.04、4 个时相列）：左平（绿）、右阶梯下沉（红带）。
配色：绿色＝正常对齐基准线，红色只标「漂移吸收生物量」与「检验前即失效」两处。
无网络；随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_size_factor_diagnostic.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import numpy as np                                    # noqa: E402
from svghelp import *                                 # noqa: E402,F401,F403
from ch16_mixed_tpm_bias import P_TIME, simulate      # noqa: E402

PHRASES = ["正常聚原点线", "漂移吸收生物量", "破坏多数不变", "检验前即失效"]
TEXT = "".join(PHRASES)
N_HOST, N_PATH, MOLS, SEED = 15000, 12000, 20_000_000, 20261104
REF_HOST = [0.9950, 0.9799, 0.8995, 0.6986]          # demos Part 1 现跑
Y_LO, Y_HI = 0.66, 1.04                             # y 轴标度（比值范围）


class Args:
    n_host, n_path, molecules, seed = N_HOST, N_PATH, MOLS, SEED


def numbers():
    rows = simulate(Args)
    got = []
    for p in P_TIME:
        sel = [r for r in rows if r["p"] == p]
        got.append(float(np.median(np.concatenate(
            [r["merged_h"] / np.maximum(r["sep_h"], 1e-12) for r in sel]))))
    for v, ref in zip(got, REF_HOST):
        if abs(v - ref) > 5e-3:
            raise SystemExit(f"图面数字与 demos 现跑不一致：got={v:.4f} "
                             f"ref={ref}")
    if not all(a > b for a, b in zip(got, got[1:])):
        raise SystemExit(f"宿主归一化比值未随时相单调下降：{got}")
    return got


def panel(s, x, w, ratios, color, band):
    """一个诊断面板：4 个时相列，比值 y 映射到 Y_LO..Y_HI。"""
    top, bot = 142, 384
    ypos = lambda v: bot - (v - Y_LO) / (Y_HI - Y_LO) * (bot - top)
    s.panel(x, 106, w, 330, WHITE, color, 3)
    s.line(x + 46, bot, x + w - 18, bot, BLUE, 4)                    # x 轴
    s.line(x + 46, top, x + 46, bot, BLUE, 4)                        # y 轴
    s.line(x + 46, ypos(1.0), x + w - 18, ypos(1.0), GREEN, 4,
           dash="9 8")                                               # 1 线
    sx = [x + 96 + i * (w - 160) / 3 for i in range(4)]
    if band:
        s.polyline([(sx[0], ypos(ratios[0])), (sx[-1], ypos(ratios[-1]))],
                   RED_TINT, 26)
    for i, (cx, r) in enumerate(zip(sx, ratios)):
        col = ORANGE if i < 2 else PURPLE
        s.circle(cx, ypos(r), 13 if band else 10,
                 col if band else GREEN)
        if i:
            s.line(sx[i - 1], ypos(ratios[i - 1]), cx, ypos(r),
                   col if band else GREEN, 4 if band else 3)
    for cx, lab in zip(sx, ("12", "24", "36", "48")):
        s.text(cx, bot + 34, lab, 30, BLUE, "middle", "bold")
    s.text(x + w - 18, top - 6, "ratio", 30, GRAY, "end")
    s.text(x + 22, ypos(1.0) + 10, "1", 30, GREEN, "end", "bold")


def main():
    ratios = numbers()
    s = SVG(800, 700, "Size factor diagnostic scatter", plan=TEXT)

    # ---------- 左面板：各自归一化 → 四个时相都贴 1 线（示意）----------
    s.text(44, 88, PHRASES[0], 30, GREEN, "start", "bold")
    panel(s, 44, 348, [0.999, 0.997, 0.998, 1.001], GREEN, False)

    # ---------- 右面板：合并口径 → 随时相阶梯下沉（实测四点）----------
    s.text(412, 88, PHRASES[1], 30, RED, "start", "bold")
    panel(s, 412, 344, ratios, RED, True)

    # ---------- 底部结论两行 ----------
    s.caption([PHRASES[2], PHRASES[3]], [INK, RED], 30,
              top=496, gap=48, pad_top=22)
    s.save("13_size_factor_diagnostic.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 25, TEXT
    raise SystemExit(main())
