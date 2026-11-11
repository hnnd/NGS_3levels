#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_sample_correction_sign_flip.py — 生成 06_sample_correction_sign_flip.svg
（FIG-P04-06：第 19 页 cols 一栏「有限样本校正翻转 D 的符号」）【data-plot】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-06（P19，cols，800×700）。
依据：教材 §20.4.1 的手算算例（n = 4、L = 3）——三个位点的较少见等位计数
1/1/1 时 π = (4/3)×1.125/3 = 0.5000 < θ_W = 3/(a₄×3) = 0.5455，读数为负；
换成 1/1/2 时未校正 π = 1.25/3 = 0.4167（假负），乘 4/3 后 1.6667/3 = 0.5556
翻正。n/(n−1) = 4/3 是有限样本校正因子。
数字入口：教材 §20.4.1「手算一个方向」一段（可用计算器逐步复核）；
本脚本按同一闭式重算并断言，不一致即失败退出；见回执核对表。
图内中文严格取方案给定 30 字（4 句）；π、θ_W 与数字属符号。
结构＝一条 θ_W 基准线横贯三根读数柱（单例 0.5000 / 双例未校正 0.4167 /
双例校正后 0.5556），柱下各一句判读。红＝漏乘校正的假负，绿＝校正后的真正值。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_sample_correction_sign_flip.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["单例位点残差为负", "双例未校正为负", "校正后翻转为正", "有限样本校正关键"]
TEXT = "".join(PHRASES)

N, L = 4, 3
A_N = sum(1.0 / i for i in range(1, N))          # a₄ = 1 + 1/2 + 1/3
CORR = N / (N - 1)                              # 4/3
THETA_W = L / (A_N * L)                         # 每位点 θ_W


def pi_hat(counts):
    return sum(2 * (c / N) * (1 - c / N) for c in counts) / L


def numbers():
    groups = [(1, 1, 1), (1, 1, 2)]
    raw = [pi_hat(g) for g in groups]
    ref_raw = [0.375, 0.4167]                    # 教材 §20.4.1 手算：未校正口径
    for v, r in zip(raw, ref_raw):
        if abs(v - r) > 5e-5:
            raise SystemExit(f"未校正 π 与教材手算不一致：{v:.4f} vs {r}")
    if abs(raw[0] * CORR - 0.5) > 1e-9:
        raise SystemExit("单例校正后应为 0.5000")
    if abs(raw[1] * CORR - 0.5556) > 5e-5:
        raise SystemExit(f"双例校正后应为 0.5556，实际 {raw[1] * CORR:.4f}")
    if abs(THETA_W - 0.5455) > 5e-5:
        raise SystemExit(f"θ_W 应为 0.5455，实际 {THETA_W:.4f}")
    return raw[0] * CORR, raw[1], raw[1] * CORR


def main():
    v_single, v_raw, v_corr = numbers()
    s = SVG(800, 700, "Finite-sample correction flips the sign", plan=TEXT)

    # ---------- 顶部：口径与基准 ----------
    s.rect(60, 46, 680, 96, WHITE, BLUE, 4, rx=14)
    s.text(104, 108, f"n = {N}   L = {L}", 32, BLUE, "start", "bold")
    s.text(700, 108, f"θ_W = {THETA_W:.4f}", 32, BLUE, "end", "bold")

    # ---------- 三根读数柱 ----------
    ybase, unit = 470, 300 / 0.6            # 0.6 满量程
    bars = [(170, v_single, BLUE, ("单例位点", "残差为负"), INK),
            (400, v_raw, RED, ("双例未校正", "为负"), RED),
            (630, v_corr, GREEN, ("校正后翻转", "为正"), GREEN)]
    for cx, v, col, phrase, pcol in bars:
        h = v * unit
        s.rect(cx - 55, ybase - h, 110, h, col, None, 0, rx=8)
        s.text(cx, ybase - h + 52, f"{v:.4f}", 30, WHITE, "middle", "bold")
        s.text(cx, ybase + 46, phrase[0], 30, pcol, "middle", "bold")
        s.text(cx, ybase + 92, phrase[1], 30, pcol, "middle", "bold")

    # θ_W 基准线横贯三柱
    yt = ybase - THETA_W * unit
    s.line(88, yt, 712, yt, GREEN, 4, dash="12 8")
    s.text(88, yt - 16, f"{THETA_W:.4f}", 30, GREEN, "start", "bold")

    # ---------- 底部结论 ----------
    s.band(120, 588, 560, 78, PHRASES[3], BLUE, WHITE, 32)

    s.save("06_sample_correction_sign_flip.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
