#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_heritability_gate_power.py — 生成 05_heritability_gate_power.svg
（FIG-P05-05：P18「遗传力闸门：先算一遍再决定跑不跑」，cols 左栏）【data-plot】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-05（800×700，中文共 27 字）。
数据入口（现算，不手填）：
  ① 遗传力闸门手算（教材 §21.4.2，与本脚本同一算式）：
     nc = N·h²_SNP/M_eff = 400 × 0.2 / 25000 = 3.2×10⁻³；
     临界值 = χ²₁ 的 1−2×10⁻⁶ 分位 = scipy.stats.chi2.ppf(1−2e-6, 1) = 22.60。
  ② 80% 功效所需非中心参数 nc₈₀ = 31.3 —— 直接调用
     `textbook/demos/ch21_thresholds_fwer_fdr.py` 的 `nc_for_power(2e-6, 0.8)`。
  ③ 检出限 q(N) = nc₈₀ / N；RDP1 规模 N = 413 → q ≈ 0.076（同 demos 部分 B 输出）。
三个数都在脚本里断言，改参数会当场失败。
图内中文严格取方案给定两句（13 + 14 = 27 字）；数字与 χ²、N、q 为符号，不占
汉字预算。配色：红色只标「非中心参数极低」那一档，绿色标可检出的 RDP1 点。
依赖：numpy + scipy（demos 本身依赖 scipy，此处只经它取分布分位数）；无网络，
无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_heritability_gate_power.py
"""
import math
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch21_thresholds_fwer_fdr as demo                     # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["非中心参数极低微效位点全灭",        # 13
           "四百材料仅能检出百分之八方差"]      # 14
TEXT = "".join(PHRASES)

N_RDP1 = 413
ALPHA = 2e-6
H2 = 0.2
M_EFF = 25000


def check_data():
    """三个数字全部现算并与 demos/教材输出对表。"""
    nc_single = 400 * H2 / M_EFF                       # 教材 §21.4.2 手算
    crit = float(stats.chi2.ppf(1.0 - ALPHA, df=1))
    nc80 = demo.nc_for_power(ALPHA, 0.8)               # demos 部分 B
    q_rdp1 = nc80 / N_RDP1                             # 检出限
    assert abs(nc_single - 0.0032) < 1e-12, nc_single
    assert abs(crit - 22.60) < 0.01, crit
    assert abs(nc80 - 31.3) < 0.1, nc80
    assert abs(q_rdp1 - 0.076) < 0.001, q_rdp1
    print(f"check: nc={nc_single:.4f}, crit={crit:.2f}, nc80={nc80:.2f}, "
          f"q(413)={q_rdp1:.4f}")
    return nc_single, crit, nc80, q_rdp1


def main():
    nc_single, crit, nc80, q_rdp1 = check_data()
    s = SVG(800, 700, "Heritability gate and detection limit", plan=TEXT)

    # ---------- 上半：同一坐标上的数量级悬殊 ----------
    x0, x1, dec = 132.0, 740.0, 121.6

    def px(v):
        return x0 + (math.log10(v) + 3.0) * dec

    for e in (-3, -2, -1, 0, 1, 2):
        gx = px(10.0 ** e)
        s.line(gx, 250, gx, 258, INK, 3)
        if e < 0:
            s.sci(gx, 292, "10", str(e).replace("-", "−"), 30, GRAY,
                  "middle")
        else:
            s.text(gx, 292, ("1", "10", "100")[e], 30, GRAY, "middle")
    s.line(x0, 258, x1, 258, INK, 4)

    s.text(56, 148, "nc", 30, INK, "start", "bold")
    s.rect(x0, 112, px(nc_single) - x0, 46, RED_TINT, RED, 4, rx=8)
    s.sci(px(nc_single) + 14, 146, "3.2×10", "−3", 30, RED, "start",
          "bold")

    s.text(56, 224, "crit", 30, INK, "start", "bold")
    s.rect(x0, 190, px(crit) - x0, 46, BLUE_TINT, BLUE, 4, rx=8)
    s.text(px(crit) + 14, 224, "22.60", 30, BLUE, "start", "bold")

    s.text(400, 344, PHRASES[0], 32, RED, "middle", "bold")

    # ---------- 下半：检出限 q 随样本量衰减 ----------
    yq0, yq1 = 540.0, 384.0            # q=0 / q=0.32

    def pxn(n):
        return 110.0 + (math.log10(n) - 2.0) / (math.log10(3000.0) - 2.0) * 590.0

    def pyq(q):
        return yq0 - q / 0.32 * (yq0 - yq1)

    s.line(110, yq0, 720, yq0, INK, 4)
    s.line(110, yq0, 110, yq1 - 10, INK, 4)
    for q in (0.0, 0.1, 0.2, 0.3):
        yy = pyq(q)
        s.line(104, yy, 110, yy, INK, 3)
        s.text(96, yy + 10, f"{q:.1f}", 30, GRAY, "end")

    ns = np.geomspace(100.0, 3000.0, 40)
    s.curve([(pxn(n), pyq(nc80 / n)) for n in ns], BLUE, 6)

    for n in (100, N_RDP1, 1000, 3000):
        s.line(pxn(n), yq0, pxn(n), yq0 + 10, INK, 3)
        s.text(pxn(n), yq0 + 42, str(n), 30, GRAY, "middle")
    s.text(730, 522, "N", 30, INK, "start", "bold")

    # 可检出区（曲线以上＝q 大于检出限，绿）+ RDP1 点
    top = pyq(0.32)
    s.polygon([(110, top), (700, top)] + [(pxn(n), pyq(nc80 / n))
                                          for n in ns[::-1]],
              GREEN_TINT, None, 0)
    gx, gy = pxn(N_RDP1), pyq(q_rdp1)
    s.circle(gx, gy, 9, GREEN)
    s.line(gx + 10, gy - 6, gx + 62, gy - 44, GREEN, 3, dash="8 6")
    s.text(gx + 68, gy - 44, "7.6%", 32, GREEN, "start", "bold")

    s.text(400, 636, PHRASES[1], 32, GREEN, "middle", "bold")

    s.save("05_heritability_gate_power.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())
