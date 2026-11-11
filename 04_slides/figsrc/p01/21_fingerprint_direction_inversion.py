#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_fingerprint_direction_inversion.py — 生成 21_fingerprint_direction_inversion.svg
（FIG-P01-22：判读指纹二 · 方向反转）【data-plot】

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-22（P57，cols 一栏，800×700）。
依据：教材 §24.4.4 与讲义 ⑥6.2 第 2 行——引用参考流程时 20 个已知上调 spike-in
全部落在上调侧；一旦 contrast 两个元素写反，20 个全部落到下调侧（上调侧命中
0/20），且两份 log2FC 之间的相关系数 ≈ −1。
图内数字全部取自 demos 现跑（textbook/demos/ch24_label_swap_mirror.py
--selftest，2026-11-11，6/6 PASS），见回执核对表：
  正确方向 20/20；方向写反 0/20；cor(log2FC_原, log2FC_反) = -1.000。
课程数据实测为 -0.990（本图在旁注里标明它属于另一数据口径，图面主值用合成算例）。
本脚本不重造数据：直接 import该 demo 的 make_counts / lfc_estimate，用同一组参数
（--n-gene 2000、--n-spike 20、--true-lfc 3.0、--seed 20261105）复算，与上列数字
不一致即失败退出。
配色：绿色正确上调；红色 1 处标「0/20 命中」；深蓝轨道骨架。无网络；随机数只用
demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 21_fingerprint_direction_inversion.py
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

TEXT = "指纹二：已知上调命中为零，相关系数负一，核对对比参数组别顺序。"
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
    return got


def track(s, y, n, up, color, label, count_txt, count_color):
    """一条轨道：中线 + n 根细条，全部向上（up=True）或全部向下。"""
    s.text(40, y + 10, label, 30, color, "start", "bold")
    s.line(252, y, 620, y, GRAY, 2)
    for i in range(n):
        h = 26 + (i % 4) * 8
        y0 = y - h if up else y
        s.rect(258 + i * 18, y0, 12, h, color, None, 0)
    s.text(660, y + 10, count_txt, 30, count_color, "start", "bold")


def main():
    got = numbers()
    s = SVG(800, 700, "Fingerprint 2: direction inversion", plan=TEXT)

    track(s, 190, N_SPIKE, True, GREEN, "reference", f"{got['up']}/{N_SPIKE}",
          GREEN)
    # 被检反向流程：整条轨道为一个红色警示区（底色带 + 红条 + 计数同属一处）
    s.rect(40, 286, 720, 100, RED_TINT, RED, 3, rx=14)
    track(s, 330, N_SPIKE, False, RED, "swapped", f"{got['flipped']}/{N_SPIKE}",
          RED)

    # 相关系数：合成算例 -1.000，课程数据实测 -0.990（口径不同，分两行写清）
    s.rect(40, 400, 720, 104, BLUE_TINT, BLUE, 3, rx=12)
    s.text(66, 446, f"cor = {got['cor']:.3f}", 32, BLUE, "start", "bold")
    s.text(66, 486, "course data: -0.990", 30, GRAY)

    # 排查入口（不写命令行，只写参数名）；深蓝＝指引，不是第二处红
    s.rect(40, 520, 720, 56, BLUE_TINT, BLUE, 3, rx=10)
    s.text(400, 558, "contrast ctrl/treat", 30, BLUE, "middle", "bold")

    s.caption(["指纹二：已知上调命中为零，相关系数负一，",
               "核对对比参数组别顺序。"], [INK, INK], 30,
              top=590, gap=42, pad_top=8)
    s.save("21_fingerprint_direction_inversion.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())
