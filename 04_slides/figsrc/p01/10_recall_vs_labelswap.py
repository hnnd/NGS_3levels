#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_recall_vs_labelswap.py — 生成 10_recall_vs_labelswap.svg
（FIG-P01-11：第 ② 步双指标验证机制）【data-plot】

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-11（P32，cols 一栏，800×700）。
依据：教材 §24.4.4 第 ② 步「已知答案回归测试」——两件事互不顶替：召回率看
绝对方向（spike-in 是否全部落在上调侧），换标签镜像相关看实现自洽（估计量
是否对称、符号是否随标签严格翻转）。
图内数字全部取自 demos 现跑（textbook/demos/ch24_label_swap_mirror.py
--selftest，2026-11-11，6/6 PASS），见回执核对表：
  正确方向上调侧命中 20/20；方向写反 0/20；换标签相关 = -1.000。
本脚本不重造数据：直接 import 该 demo 的 make_counts / lfc_estimate，用同一组
参数（--n-gene 2000、--n-spike 20、--true-lfc 3.0、--seed 20261105）复算，
与上列数字不一致即失败退出。
配色：深蓝坐标与面板骨架；绿色 20/20 召回与镜像拟合；红色 1 处标 0/20 方向颠倒。
无网络；随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_recall_vs_labelswap.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import numpy as np                                    # noqa: E402
from svghelp import *                                 # noqa: E402,F401,F403
from ch24_label_swap_mirror import (                  # noqa: E402
    make_counts, lfc_estimate)

TEXT = "第二步双指标：召回看绝对方向，换标签相关负一看自洽。两步互不顶替。"
N_GENE, N_SPIKE, TRUE_LFC, SEED = 2000, 20, 3.0, 20261105
REF = {"up": 20, "flipped": 0, "cor": -1.000}


def numbers():
    counts, spike = make_counts(N_GENE, N_SPIKE, TRUE_LFC, SEED)
    lfc = lfc_estimate(counts)
    got = {"up": int((lfc[spike] > 0).sum()),
           "flipped": int(((-lfc)[spike] > 0).sum()),
           "cor": round(float(np.corrcoef(lfc, -lfc)[0, 1]), 3)}
    for k, v in REF.items():
        if abs(got[k] - v) > 1e-9:
            raise SystemExit(f"图面数字与 demos 现跑不一致：{k} "
                             f"got={got[k]} ref={v}")
    return got, lfc, spike


def bars(s, x, base, n, up, color, w=9, pitch=12, hmin=24, hmax=44):
    """一行 n 根等距细条：up=True 向上（正值侧），False 向下（负值侧）。"""
    for i in range(n):
        h = hmin + (hmax - hmin) * (i % 5) / 4.0
        x0 = x + i * pitch
        y0 = base - h if up else base
        s.rect(x0, y0, w, h, color, None, 0)


def main():
    got, lfc, spike = numbers()
    s = SVG(800, 700, "Recall and label-swap mirror test", plan=TEXT)

    # ---------- 左面板：绝对方向（20 根 spike-in 落在哪一侧）----------
    s.panel(40, 44, 352, 256, BLUE_TINT, BLUE, 3, 14)
    s.text(64, 84, "direction", 30, GREEN, "start", "bold")
    s.text(372, 84, f"{got['up']}/{N_SPIKE}", 32, GREEN, "end", "bold")
    s.text(64, 156, "REF", 30, GREEN, "start", "bold")
    s.line(64, 172, 372, 172, GRAY, 2)
    bars(s, 128, 172, N_SPIKE, True, GREEN)
    s.text(64, 274, "REV", 30, PURPLE, "start", "bold")
    s.line(64, 246, 372, 246, GRAY, 2)
    bars(s, 128, 246, N_SPIKE, False, PURPLE)
    s.text(372, 232, f"{got['flipped']}/{N_SPIKE}", 30, RED, "end", "bold")

    # ---------- 右面板：实现自洽（换标签后严格落在 y = -x 上）----------
    s.panel(410, 44, 350, 256, WHITE, BLUE, 3, 14)
    s.text(434, 84, "mirror", 30, BLUE, "start", "bold")
    s.text(736, 84, f"cor {got['cor']:.3f}", 30, GREEN, "end", "bold")
    cx, cy, sc = 608, 200, 30.0          # 原点与每 log2FC 单位像素
    s.line(516, cy, 700, cy, GRAY, 2)    # x 轴（原始方向）
    s.line(cx, 272, cx, 132, GRAY, 2)    # y 轴（换标签方向）
    s.polygon([(700, cy), (688, cy - 6), (688, cy + 6)], GRAY)
    s.polygon([(cx, 132), (cx - 6, 144), (cx + 6, 144)], GRAY)
    # 理论镜像线 y = -x（灰虚线）+ 实测点（绿，严格落在线上）
    s.line(cx - 2.6 * sc, cy + 2.6 * sc, cx + 2.6 * sc, cy - 2.6 * sc,
           GRAY, 3, dash="9 8")
    mags = np.percentile(np.abs(lfc), np.linspace(20, 96, 7))
    for v in mags[mags <= 2.5]:
        s.circle(cx + v * sc, cy - v * sc, 6, GREEN)
        s.circle(cx - v * sc, cy + v * sc, 6, GREEN)
    s.text(434, 258, "y = -x", 30, GRAY)

    # ---------- 底部对齐结论卡：两笔指标各占一行 ----------
    s.rect(40, 330, 720, 150, WHITE, BLUE, 3, rx=14)
    s.text(64, 380, "recall", 30, INK)
    s.text(736, 380, f"{got['up']}/{N_SPIKE}  >=  18", 32, GREEN, "end", "bold")
    s.line(64, 404, 736, 404, PANEL, 3)
    s.text(64, 452, "mirror", 30, INK)
    s.text(736, 452, f"cor = {got['cor']:.3f}", 32, GREEN, "end", "bold")

    s.caption(["第二步双指标：召回看绝对方向，",
               "换标签相关负一看自洽。",
               "两步互不顶替。"], [INK, INK, BLUE], 30,
              top=520, gap=44, pad_top=16)
    s.save("10_recall_vs_labelswap.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
