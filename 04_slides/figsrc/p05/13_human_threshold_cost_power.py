#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_human_threshold_cost_power.py — 生成 13_human_threshold_cost_power.svg
（FIG-P05-13：P30「照搬人类阈值的代价是可以算的」，cols 左栏）【data-plot】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-13（800×700，中文共 28 字）。
数据入口：`textbook/demos/ch21_thresholds_fwer_fdr.py` 的 `nc_for_power()`：
  α = 2×10⁻⁶ → 80% 功效所需非中心参数 nc = 31.3；
  α = 5×10⁻⁸ → nc = 39.6；同样效应的位点需样本量 ×1.27（+27%）；
  RDP1 规模 N = 413、α = 2×10⁻⁶ 时 80% 功效检出限 q ≈ 0.076（= 7.6% 方差）。
三个数与 demos 部分 B 的打印值一致，脚本内断言。
图内中文严格取方案给定两句（13 + 15 = 28 字）；nc、α、N、q 为符号。
配色：绿＝适度阈值基准，红色只标非中心参数抬升与样本量代价这一处。
依赖：numpy + scipy（同 demos）；无网络；无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_human_threshold_cost_power.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch21_thresholds_fwer_fdr as demo                     # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["非中心参数自三十一升至四十",         # 13
           "同等位点样本多四分之一微效全漏"]      # 15
TEXT = "".join(PHRASES)


def check_data():
    nc_meff = demo.nc_for_power(2e-6, 0.8)
    nc_human = demo.nc_for_power(5e-8, 0.8)
    q_rdp1 = nc_meff / 413.0
    assert abs(nc_meff - 31.3) < 0.1, nc_meff
    assert abs(nc_human - 39.6) < 0.1, nc_human
    assert abs(nc_human / nc_meff - 1.265) < 0.01, nc_human / nc_meff
    assert abs(q_rdp1 - 0.076) < 0.001, q_rdp1
    print(f"check: nc(2e-6)={nc_meff:.1f}, nc(5e-8)={nc_human:.1f}, "
          f"×{nc_human / nc_meff:.3f}, q(413)={q_rdp1:.4f}")
    return nc_meff, nc_human, q_rdp1


def main():
    nc_meff, nc_human, q_rdp1 = check_data()
    s = SVG(800, 700, "Cost of importing the human threshold", plan=TEXT)

    # ---------- 两根柱：80% 功效所需非中心参数 ----------
    ybase, ytop = 380.0, 110.0
    vmax = 45.0

    def py(v):
        return ybase - v / vmax * (ybase - ytop)

    s.line(120, ybase, 700, ybase, INK, 4)
    s.line(120, ybase, 120, ytop - 10, INK, 4)
    for v in (0, 10, 20, 30, 40):
        s.line(112, py(v), 700, py(v), PANEL, 2, dash="6 8")
        s.text(104, py(v) + 10, str(v), 30, GRAY, "end")

    s.rect(204, py(nc_meff), 92, py(0) - py(nc_meff), GREEN_TINT, GREEN, 4,
           rx=8)
    s.text(250, py(nc_meff) - 18, f"{nc_meff:.1f}", 32, GREEN, "middle",
           "bold")
    s.rect(474, py(nc_human), 92, py(0) - py(nc_human), RED_TINT, RED, 4,
           rx=8)
    s.text(520, py(nc_human) - 18, f"{nc_human:.1f}", 32, RED, "middle",
           "bold")
    s.sci(250, 424, "2×10", "−6", 30, GREEN, "middle")
    s.sci(520, 424, "5×10", "−8", 30, RED, "middle")
    s.text(582, 300, "+27%", 32, RED, "start", "bold")

    s.text(400, 476, PHRASES[0], 32, INK, "middle", "bold")

    # ---------- 底部：RDP1 规模只能检出 7.6% 方差 ----------
    s.line(130, 588, 700, 588, INK, 4)
    s.text(130, 546, "N=413", 30, GRAY, "start", "bold")
    s.rect(250, 552, 570 * q_rdp1, 36, GREEN_TINT, GREEN, 4, rx=6)
    s.text(250 + 570 * q_rdp1 + 16, 582, "7.6%", 32, GREEN, "start", "bold")

    s.text(400, 650, PHRASES[1], 32, RED, "middle", "bold")

    s.save("13_human_threshold_cost_power.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())
