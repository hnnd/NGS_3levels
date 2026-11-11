#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_fingerprint_double_normalization.py — 生成 22_fingerprint_double_normalization.svg
（FIG-P01-23：判读指纹三 · 双重归一化）【data-plot】

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-23（P58，cols 一栏，800×700）。
依据：教材 §24.4.4 与讲义 ⑥6.2 第 3 行——先把 counts 转成 CPM 再 round 喂给
DESeq2，归一化信息被抹掉第二次：文库大小被强行拉平到 ≈1e6，size factors 从
0.6–1.5 挤到 1.0 附近。判读指纹就是「因子全在 1.0 附近，而原始文库差好几倍」。
图内数字全部取自 demos 现跑（textbook/demos/ch24_double_normalization_sizefactors.py
--selftest，2026-11-11，5/5 PASS），见回执核对表：
  原始：文库 1.94×10^5–4.63×10^5（max/min 2.39）；size factors 0.625–1.484（散布 2.38×）
  round(CPM)：文库被拉平到 ≈1.00×10^6（max/min 1.0001）；size factors 0.983–1.012（散布 1.03×）
本脚本不重造数据：直接 import 该 demo 的 make_counts / median_of_ratios，用同一组
参数（--n-gene 2000、--seed 20261105）复算，与上列数字不一致即失败退出。
配色：青蓝正常离散因子；红色 1 处标「因子挤在 1.0 附近」；深蓝标尺。
无网络；随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 22_fingerprint_double_normalization.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import numpy as np                                    # noqa: E402
from svghelp import *                                 # noqa: E402,F401,F403
from ch24_double_normalization_sizefactors import (  # noqa: E402
    make_counts, median_of_ratios)

TEXT = "指纹三：缩放因子挤在1.0附近，原始文库差2.5倍，归一化做了两次。"
N_GENE, SEED = 2000, 20261105
REF = {"lib_min": 193671, "lib_max": 463355, "sf_min": 0.625, "sf_max": 1.484,
       "sf_spread": 2.38, "cpm_sf_min": 0.983, "cpm_sf_max": 1.012,
       "cpm_spread": 1.03}


def numbers():
    cts = make_counts(N_GENE, SEED)
    lib = cts.sum(axis=0).astype(int)
    sf = median_of_ratios(cts)
    cpm = np.round(cts / lib[None, :] * 1e6)
    sf2 = median_of_ratios(cpm)
    got = {"lib_min": int(lib.min()), "lib_max": int(lib.max()),
           "sf_min": round(float(sf.min()), 3),
           "sf_max": round(float(sf.max()), 3),
           "sf_spread": round(float(sf.max() / sf.min()), 2),
           "cpm_sf_min": round(float(sf2.min()), 3),
           "cpm_sf_max": round(float(sf2.max()), 3),
           "cpm_spread": round(float(sf2.max() / sf2.min()), 2)}
    for k, v in REF.items():
        if abs(got[k] - v) > 1e-9:
            raise SystemExit(f"图面数字与 demos 现跑不一致：{k} "
                             f"got={got[k]} ref={v}")
    return got, sf, sf2


def main():
    got, sf, sf2 = numbers()
    s = SVG(800, 700, "Fingerprint 3: double normalization", plan=TEXT)

    # 左右两个面板：原始 counts vs round(CPM)
    # 面板一：size factor 散点（0.5–1.6 的实数轴，synthetic 6 个点）
    s.panel(40, 40, 344, 274, BLUE_TINT, BLUE, 3, 14)
    s.text(60, 82, "counts", 32, BLUE, "start", "bold")
    s.text(366, 82, f"{got['sf_spread']:.2f} X", 32, BLUE, "end", "bold")
    ax, ay, asc = 84, 208, 150.0          # 轴起点、基线、每单位像素
    s.line(ax, ay, 356, ay, GRAY, 3)                       # 因子 = 1.0 基线
    s.line(ax, ay - 0.45 * asc, ax, ay + 0.45 * asc, GRAY, 3)
    for x, v in zip(np.linspace(96, 344, 6), sf):
        s.circle(x, ay - (v - 1.0) * asc, 9, CYAN, BLUE, 3)
    # 刻度文字放到底边一行（原 274 与纵轴竖线相交，字被轴穿过）
    s.text(74, 300, "0.6", 30, GRAY, "middle")
    s.text(356, 300, "1.5", 30, GRAY, "middle")

    # 面板二：round(CPM) 后因子被拉平
    s.panel(410, 40, 350, 274, WHITE, RED, 4, 14)
    s.text(430, 82, "round(CPM)", 32, RED, "start", "bold")
    s.text(740, 82, f"{got['cpm_spread']:.2f} X", 32, RED, "end", "bold")
    s.line(454, ay, 726, ay, GRAY, 3)
    s.line(454, ay - 0.45 * asc, 454, ay + 0.45 * asc, GRAY, 3)
    for x, v in zip(np.linspace(466, 714, 6), sf2):
        s.circle(x, ay - (v - 1.0) * asc * 6, 9, RED, RED, 2)
    s.text(444, 300, "0.98", 30, GRAY, "middle")
    s.text(726, 300, "1.01", 30, GRAY, "middle")

    # 文库大小：同一标度下两栏对照
    s.rect(40, 330, 720, 116, WHITE, BLUE, 3, rx=12)
    s.text(66, 374, "library", 30, GRAY)
    s.text(66, 424, "after_round(CPM)", 30, GRAY)
    s.text(736, 374, f"{got['lib_min']} - {got['lib_max']}", 30, BLUE,
           "end", "bold")
    s.text(736, 424, "1.00 X 10^6  flat", 30, RED, "end", "bold")

    # 指纹判据
    s.rect(40, 466, 720, 62, RED_TINT, RED, 4, rx=10)
    s.text(400, 506, "factors ≈ 1.0  +  libraries ~2.5 X", 30, RED, "middle",
           "bold")

    s.caption(["指纹三：缩放因子挤在1.0附近，",
               "原始文库差2.5倍，归一化做了两次。"], [INK, INK], 30,
              top=560, gap=44, pad_top=14)
    s.save("22_fingerprint_double_normalization.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 24, TEXT
    raise SystemExit(main())
