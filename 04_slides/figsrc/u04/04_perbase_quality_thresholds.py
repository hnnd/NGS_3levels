#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_perbase_quality_thresholds.py — 生成 04_perbase_quality_thresholds.svg
（FIG-U04-04：Per base quality 双阈值与实跑轨迹【data-plot】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-04（P16，cols 一栏，viewBox 800×700）。
坐标系：横轴 BaseGroup 1–55，纵轴 Quality 0–40；橙色虚线 Q25（中位数 < 25）、
红色虚线 Q20（中位数 < 20）；深蓝实线为 demos 复算的分组中位轨迹；
组 82–83 中位 24.0 触发 WARN（橙圈），组 96–97 中位 19.0 触发 ERROR（红圈）；
底部红框「模块判定 FAIL」。
数据来源（直接调用，保证逐项一致）：demos/ch06_perbase_quality.py
  --selftest Part A/C（THRESH/qual_profile/base_groups/group_stats/first_trigger）。
无网络、无随机数（确定性剖面）。用法：PYTHONDONTWRITEBYTECODE=1 python3 04_perbase_quality_thresholds.py
"""
import sys

import numpy as np

from svghelp import *

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from ch06_perbase_quality import (  # noqa: E402
    THRESH, base_groups, first_trigger, group_stats, module_status,
    qual_profile,
)


def main():
    prof = qual_profile(100)
    labels, mean_g, med_g, q1_g = group_stats(np.tile(prof, (2000, 1)))
    assert len(labels) == 55
    w = first_trigger(labels, med_g, q1_g, "warn")
    e = first_trigger(labels, med_g, q1_g, "error")
    assert w[0] == "82-83" and abs(w[1] - 24.0) < 1e-9
    assert e[0] == "96-97" and abs(e[1] - 19.0) < 1e-9
    assert module_status(q1_g, med_g) == "fail"
    print(f"check: WARN {w[0]} 中位 {w[1]}，ERROR {e[0]} 中位 {e[1]}，判定 fail")

    s = SVG(800, 700)
    X0, X1, Y0, Y1 = 100, 740, 80, 540   # 绘图区
    QMAX = 40

    def gx(i):
        return X0 + (i + 0.5) * (X1 - X0) / 55

    def gy(q):
        return Y0 + (QMAX - q) * (Y1 - Y0) / QMAX

    # 网格与坐标刻度
    for q in (0, 10, 20, 30, 40):
        s.line(X0, gy(q), X1, gy(q), PANEL, sw=3)
        s.text(X0 - 12, gy(q) + 10, str(q), 30, GRAY, "end")
    for lab, i in (("1", 0), ("28", 27), ("55", 54)):
        s.line(gx(i), Y1, gx(i), Y1 + 10, INK, sw=3)
        s.text(gx(i), Y1 + 44, lab, 30, GRAY, "middle")
    s.text((X0 + X1) / 2, Y1 + 64 + 46, "Base group", 30, GRAY, "middle")
    s.line(X0, Y1, X1, Y1, INK, sw=4)
    s.line(X0, Y0, X0, Y1, INK, sw=4)
    s.text_rot(38, (Y0 + Y1) / 2, "Quality", -90)

    # 双阈值虚线（WARN 橙 Q25 / ERROR 红 Q20）
    s.line(X0, gy(THRESH["warn"]["median"]), X1,
           gy(THRESH["warn"]["median"]), ORANGE_DEEP, sw=5, dash="16 12")
    s.line(X0, gy(THRESH["error"]["median"]), X1,
           gy(THRESH["error"]["median"]), RED, sw=5, dash="16 12")
    s.text(X0 + 12, gy(25) - 14, "中位数 < 25", 30, ORANGE_DEEP, "start",
           "bold")
    s.text(X0 + 12, gy(20) - 14, "中位数 < 20", 30, RED, "start", "bold")

    # 分组中位轨迹（深蓝实线）
    pts = [(gx(i), gy(float(med_g[i]))) for i in range(55)]
    s.polyline(pts, BLUE, sw=5)
    iw, ie = labels.index("82-83"), labels.index("96-97")
    s.circle(gx(iw), gy(24.0), 13, WHITE, stroke=ORANGE_DEEP, sw=7)
    s.circle(gx(ie), gy(19.0), 13, WHITE, stroke=RED, sw=7)
    s.text(gx(iw), gy(24.0) - 58, "82–83 组触发", 30, ORANGE_DEEP, "middle",
           "bold")
    s.text(gx(ie) - 12, gy(19.0) + 52, "96–97 组触发", 30, RED, "end",
           "bold")

    # 底部红框：模块判定
    s.rect(250, 590, 300, 70, WHITE, stroke=RED, sw=6, rx=14)
    s.text(400, 638, "模块判定 FAIL", 34, RED, "middle", "bold")

    s.save("04_perbase_quality_thresholds.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
