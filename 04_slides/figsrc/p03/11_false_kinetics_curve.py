#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_false_kinetics_curve.py — 生成 11_false_kinetics_curve.svg
（FIG-P03-11：第 26 页 cols 一栏「恒定错误率造出假时序动力学曲线」）【data-plot】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-11（P26，cols，800×700）。
依据：教材 §16.4.3 L198–207——渗漏率 ε 全程恒定，但病原真实份额 f_P 随时序从
0.5% 涨到 30%，伪计数 ε(1−f_P) 相对 f_P 的虚增幅度随之从 19.9% 塌到 0.23%；
矩阵里读成「保守家族基因早期虚高、随侵染持续下调」，伪造出一条斜率漂亮的假下调
动力学（表观下调约 85.3 倍）。
数字入口：`textbook/demos/ch16_cross_mapping_leakage.py --selftest` Part 1（现跑
实现值 19.555% / 4.876% / 0.883% / 0.233%，p = 0.5% / 2% / 10% / 30%；seed
20261104、N = 2e6、c = 0.001）。本脚本直接 import 该 demo 的 `simulate()` 用同一组
参数重算四点并断言，不一致即失败退出；见回执核对表。
图内中文严格取方案给定 27 字（4 句）。时相（12/24/36/48 hpi）、份额与百分数为符号。
结构＝一张坐标图：红色折线穿过四个实测点，绿色虚线压 0 位表「真实恒定」基准，右侧
红字标塌缩倍数与假下调方向。红色只用于曲线与两处警示文字（≤2 处）。
无网络；随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 11_false_kinetics_curve.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from svghelp import *                                        # noqa: E402,F401,F403
from ch16_cross_mapping_leakage import closed_form, simulate  # noqa: E402

PHRASES = ["错误率全程恒定", "虚增两成降至千二", "塌缩八十五倍", "伪造剧烈下调"]
TEXT = "".join(PHRASES)
C, N, SEED = 0.001, 2_000_000, 20261104
P_TIME = [0.005, 0.02, 0.10, 0.30]                          # 12/24/36/48 hpi
REF = [19.555, 4.876, 0.883, 0.233]                         # demos 现跑实现值 %
REF_COLLAPSE = 85.3


def numbers():
    got = []
    for p in P_TIME:
        r = simulate(C, p, N, SEED)
        got.append(100.0 * (r["path_naive"] - r["path_true"]) / r["path_true"])
    for v, ref in zip(got, REF):
        if abs(v - ref) > 1e-3:
            raise SystemExit(f"图面数字与 demos 现跑不一致：got={v:.3f} ref={ref}")
    collapse = (closed_form(C, P_TIME[0])["naive_dual_path"]
                / closed_form(C, P_TIME[-1])["naive_dual_path"])
    if abs(collapse - REF_COLLAPSE) > 0.05:
        raise SystemExit(f"塌缩倍数不一致：{collapse:.1f}")
    # 注记：85.3 是 demos 印刷的闭式比（19.9% / 0.233%）；四点实现值自身的比值
    # 为 84.0（19.555% / 0.2329%），图面标点用实现值、塌缩倍数用闭式口径。
    return got


def main():
    ys = numbers()
    s = SVG(800, 700, "A constant error rate fakes a kinetics curve", plan=TEXT)

    # ---------- 坐标框 ----------
    x0, x1, ybase, ytop = 104, 742, 486, 158   # ybase = 0%，ytop = 22%
    s.arrow(x0, ybase, x1 + 6, ybase, BLUE, 5, 14)
    s.arrow(x0, ybase, x0, ytop - 10, BLUE, 5, 14)
    for v in (0, 5, 10, 15, 20):
        y = ybase - v / 22.0 * (ybase - ytop)
        s.line(x0 - 8, y, x0, y, BLUE, 3)
        s.text(x0 - 18, y + 10, f"{v}%", 30, GRAY, "end")
    s.line(x0, ybase, x1, ybase, GREEN, 4, dash="10 8")     # 真实恒定基准

    # ---------- 四个实测点 + 红色折线 ----------
    px = [x0 + 42 + i * 176 for i in range(4)]
    py = [ybase - v / 22.0 * (ybase - ytop) for v in ys]
    s.polyline(list(zip(px, py)), RED, 6)
    for i, (x, y, v) in enumerate(zip(px, py, ys)):
        s.circle(x, y, 10, RED)
        # 标签一律放在点的右上侧：折线向右下走，右上永远是空的；
        # 抬到 y-16 是为了让最右一点的标签离开横轴箭头（箭头尖 y≈480–492）
        s.text(x + 26, y - 16, f"{v:.1f}%", 30, RED, "start", "bold")
    for x, lab in zip(px, ("12", "24", "36", "48")):
        s.text(x, ybase + 40, lab, 30, BLUE, "middle", "bold")
    s.text(430, 566, "hpi", 30, GRAY, "middle")

    # ---------- 左侧标签：错误率全程恒定（绿）----------
    s.text(56, 104, PHRASES[0], 30, GREEN, "start", "bold")
    s.line(56, 118, 300, 118, GREEN, 4, dash="10 8")

    # ---------- 底部结论两行 ----------
    s.caption([PHRASES[1], PHRASES[2] + "　" + PHRASES[3]],
              [INK, RED], 30, top=584, gap=48, pad_top=22)
    s.save("11_false_kinetics_curve.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())
