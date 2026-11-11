#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23_biomass_curve_anomaly.py — 生成 23_biomass_curve_anomaly.svg
（FIG-P03-23：第 54 页 cols 一栏「生物量曲线异常指纹」）【data-plot】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-23（P54，cols，800×700）。
依据：教材 §16.6 L461、§16.5.1 L395；`06_data/phd/README.md` p03 节「自查判据」——
① 接种组病原读段占比随 hpi 单调上升（12 → 48 hpi 生物量增加）；
② 未接种 `H2O` 对照里分配给稻瘟菌的读段比例应当很低（本底）；
③ 若对照组病原比例与接种组相当，说明 gentrome 或竞争性比对参数有问题。
异常指纹有三类：Mock 组检出病原占比突破 1%（交叉比对本底失控或操作污染）、
同一时间点重复样本间跨越一个数量级（接种不同步）、全零占位（样本丢失）。
数字入口：判据阈值 1%（教材 §16.5.1 与 `06_data/phd/README.md`）；时序曲线形态为
教材描述的定性趋势，**不是实测数值**——本图不打印任何 f_P 实测百分点，只用「近零
基准线 + 上升轨迹 + 两处异常」的图形关系表达判读逻辑；判据常量在脚本内断言。
图内中文严格取方案给定 30 字（4 句）。时相刻度 12/24/36/48 hpi 为设计时点。
结构＝一张坐标图：绿实线（正常上升）、绿虚线（Mock 近零）、红实线（Mock 检出）、
灰虚线（重复离散）。红色只用于两处异常指纹。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 23_biomass_curve_anomaly.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["正常随时相上升", "未接种应近全零", "对照检出提示污染", "重复离散示不同步"]
TEXT = "".join(PHRASES)
MOCK_MAX = 0.01                             # 判据：Mock 组病原占比 ≥1% 即报污染
SPREAD_DECADE = 10.0                       # 判据：同时间点重复跨一个数量级即报不同步
HOURS = ("12", "24", "36", "48")


def check_thresholds():
    if not (0 < MOCK_MAX <= 0.05):
        raise SystemExit(f"Mock 本底阈值越界：{MOCK_MAX}")
    if SPREAD_DECADE < 10.0:
        raise SystemExit(f"重复离散判据越界：{SPREAD_DECADE}")
    return MOCK_MAX, SPREAD_DECADE


def main():
    check_thresholds()
    s = SVG(800, 700, "Biomass curve anomaly fingerprints", plan=TEXT)

    # ---------- 坐标框 ----------
    x0, x1, ybase, ytop = 96, 744, 452, 150
    s.arrow(x0, ybase, x1 + 6, ybase, BLUE, 5, 14)
    s.arrow(x0, ybase, x0, ytop - 10, BLUE, 5, 14)
    xs = [x0 + 56 + i * 176 for i in range(4)]
    for x, h in zip(xs[:3], HOURS[:3]):
        s.text(x, ybase + 40, h, 30, BLUE, "middle", "bold")
    s.text(xs[3] - 6, ybase + 40, HOURS[3], 30, BLUE, "end", "bold")
    s.text(744, 498, "hpi", 30, GRAY, "end")

    # ---------- 正常轨迹：接种组随时相上升（绿）----------
    rise = [(xs[0], 402), (xs[1], 344), (xs[2], 286), (xs[3], 228)]
    s.polyline(rise, GREEN, 6)
    for x, y in rise:
        s.circle(x, y, 9, GREEN)
    s.text(56, 88, PHRASES[0], 30, GREEN, "start", "bold")

    # ---------- 近零基准：Mock 组贴底（绿虚线）----------
    s.line(x0, 438, x1, 438, GREEN, 4, dash="10 8")
    s.text(56, 560, PHRASES[1], 30, GREEN, "start", "bold")
    s.arrow(90, 520, 90, 442, GREEN, 5, 14)

    # ---------- 异常一：Mock 检出（红实线 + 红字）----------
    bad = [(xs[0], 428), (xs[1], 392), (xs[2], 350), (xs[3], 300)]
    s.polyline(bad, RED, 5)
    for x, y in bad:
        s.circle(x, y, 8, RED)
    s.text(300, 202, PHRASES[2], 30, RED, "start", "bold")
    s.line(376, 214, 424, 300, RED, 3, dash="8 6")

    # ---------- 异常二：同时间点重复离散（灰虚线竖标）----------
    x = xs[1]
    s.line(x - 26, 322, x - 26, 412, GRAY, 4, dash="7 6")
    s.line(x + 26, 296, x + 26, 424, GRAY, 4, dash="7 6")
    s.dot(x - 26, 336, 8, GRAY)
    s.dot(x + 26, 402, 8, GRAY)
    s.text(300, 600, PHRASES[3], 30, GRAY, "start", "bold")
    s.arrow(352, 570, x + 26, 436, GRAY, 4, 12)
    s.save("23_biomass_curve_anomaly.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
