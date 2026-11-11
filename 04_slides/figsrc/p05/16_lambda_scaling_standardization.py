#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_lambda_scaling_standardization.py — 生成 16_lambda_scaling_standardization.svg
（FIG-P05-16：P34「λ 的四态判读：档位是经验口径」，cols 左栏）【data-plot】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-16（800×700，中文共 29 字）。
数据入口：`textbook/demos/ch21_lambda_gc_scaling.py`（h²=0.5、M_eff=25000、
每场景 50 次重复取中位、种子 20261104）。本脚本按 demos 的随机数消耗顺序
重放（先抽部分 0 的 200000 个均匀数，再逐场景调 `sim_polygenic_lam`，
最后抽部分 3 的注入序列），因此得到的四个 λ 观测与部分 3 的两个 λ 与
demos 打印值逐位一致：
  N=413 → 1.0075（理论 1.0083）；N=3500 → 1.0721（1.0700）；
  N=5000 → 1.1058（1.1000）；N=10000 → 1.2152（1.2000）。
  λ_1000：团队 A（n=150, λ=1.05）→ 1.3333；团队 B（n=3500, λ=1.15）→ 1.0429。
  注入 5 个 nc=40 强信号前后 λ 都是 1.0679（零漂移），而 min p 从
  1.71×10⁻⁵ 掉到 2.50×10⁻¹²。
图内中文严格取方案给定三句（9 + 9 + 11 = 29 字）；λ、N、λ_1000 与数字为符号。
配色：深蓝＝理论标度律，绿＝标准化后的优异状态；红色只标「大样本自然膨胀」
这一处认知警示。
依赖：numpy + scipy（同 demos）；无网络；种子固定。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_lambda_scaling_standardization.py
"""
import math
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch21_lambda_gc_scaling as demo                       # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["大样本膨胀自然上升",       # 9
           "千人标度团队乙更优",      # 9
           "中位钝感不觉极端强信号"]   # 11
TEXT = "".join(PHRASES)

H2, M_EFF, NREP, SEED = 0.5, 25000, 50, 20261104


def check_data():
    """按 demos 的消耗顺序重放，取四个 λ 观测与部分 3 的两个 λ。"""
    rng = np.random.default_rng(SEED)
    rng.uniform(size=200000)                     # 部分 0 的零假设抽样
    obs = {}
    for n in (413, 3500, 5000, 10000):
        obs[n] = float(np.median(
            demo.sim_polygenic_lam(n, H2, M_EFF, NREP, rng)))
    nc = 3500 * H2 / M_EFF
    chi2_base = rng.noncentral_chisquare(df=1, nonc=nc, size=M_EFF)
    chi2_inj = chi2_base.copy()
    chi2_inj[:5] = rng.noncentral_chisquare(df=1, nonc=40.0, size=5)
    med = stats.chi2.ppf(0.5, df=1)
    lam_base = float(np.median(chi2_base)) / med
    lam_inj = float(np.median(chi2_inj)) / med
    p_base = float(stats.chi2.sf(chi2_base, df=1).min())
    p_inj = float(stats.chi2.sf(chi2_inj, df=1).min())

    assert [round(obs[n], 4) for n in (413, 3500, 5000, 10000)] == \
        [1.0075, 1.0721, 1.1058, 1.2152], obs
    assert round(lam_base, 4) == round(lam_inj, 4) == 1.0679, (lam_base, lam_inj)
    assert abs(p_base - 1.71e-5) < 1e-7 and abs(p_inj - 2.50e-12) < 1e-14
    l1000_a = 1.0 + (1.05 - 1.0) * 1000.0 / 150.0
    l1000_b = 1.0 + (1.15 - 1.0) * 1000.0 / 3500.0
    assert abs(l1000_a - 1.3333) < 1e-3 and abs(l1000_b - 1.0429) < 1e-3
    print("check: " + ", ".join(f"N={n}:{obs[n]:.4f}" for n in obs)
          + f"; λ 注入前后 {lam_base:.4f}/{lam_inj:.4f}; "
            f"min p {p_base:.2e}→{p_inj:.2e}; "
            f"λ1000 A={l1000_a:.4f} B={l1000_b:.4f}")
    return obs, lam_base, p_base, p_inj, l1000_a, l1000_b


def main():
    obs, lam_base, p_base, p_inj, l1000_a, l1000_b = check_data()
    s = SVG(800, 700, "Lambda scaling law and standardization", plan=TEXT)

    # ---------- 左：λ 随样本量上升（理论曲线 + 四个观测点）----------
    lx0, lx1, ly0, ly1 = 100.0, 390.0, 340.0, 70.0

    def pxn(n):
        return lx0 + (math.log10(n) - 2.0) / (math.log10(15000.0) - 2.0) \
            * (lx1 - lx0)

    def pyl(v):
        return ly0 - (v - 1.0) / 0.25 * (ly0 - ly1)

    s.line(lx0, ly0, lx1 + 14, ly0, INK, 4)
    s.line(lx0, ly0, lx0, ly1 - 12, INK, 4)
    for v in (1.0, 1.1, 1.2):
        s.line(lx0 - 8, pyl(v), lx0, pyl(v), INK, 3)
        s.text(lx0 - 16, pyl(v) + 10, f"{v:.1f}", 30, GRAY, "end")
    s.text(lx0 - 16, ly1 - 24, "λ", 32, BLUE, "end", "bold")

    ns = np.geomspace(100.0, 12000.0, 40)
    s.curve([(pxn(float(n)), pyl(1.0 + float(n) * H2 / M_EFF)) for n in ns],
            BLUE, 5)
    for n in (413, 3500, 5000, 10000):
        s.circle(pxn(n), pyl(obs[n]), 8, BLUE)
    for n in (413, 10000):
        s.line(pxn(n), ly0, pxn(n), ly0 + 9, INK, 3)
        s.text(pxn(n), ly0 + 40, str(n), 30, GRAY, "middle")

    # ---------- 右：λ 与 λ_1000 的翻转条形 ----------
    rx0, ry0, ry1 = 500.0, 340.0, 70.0

    def pyl2(v):
        return ry0 - (v - 1.0) / 0.40 * (ry0 - ry1)

    s.line(rx0 - 10, ry0, 762, ry0, INK, 4)
    s.line(rx0 - 10, ry0, rx0 - 10, ry1 - 12, INK, 4)
    for v in (1.0, 1.2, 1.4):
        s.line(rx0 - 18, pyl2(v), rx0 - 10, pyl2(v), INK, 3)
        s.text(rx0 - 24, pyl2(v) + 10, f"{v:.1f}", 30, GRAY, "end")

    # 每组两根：左＝原始 λ（空心），右＝λ_1000（实心）
    bars = [(520, 1.05, CYAN, False), (574, l1000_a, CYAN, True),
            (650, 1.15, PURPLE, False), (704, l1000_b, PURPLE, True)]
    for cx, v, col, solid in bars:
        top = pyl2(v)
        s.rect(cx, top, 36, ry0 - top, col if solid else WHITE, col, 4, rx=6)
        s.text(cx + 18, top - 12, f"{v:.2f}", 30, col, "middle", "bold")
    s.text(538, 378, "A", 32, CYAN_DEEP, "middle", "bold")
    s.text(668, 378, "B", 32, PURPLE, "middle", "bold")

    s.text(240, 424, PHRASES[0], 32, RED, "middle", "bold")
    s.text(605, 424, PHRASES[1], 32, GREEN, "middle", "bold")

    # 图例：λ（空心） vs λ_1000（实心）
    s.rect(486, 470, 34, 30, WHITE, BLUE, 4, rx=5)
    s.text(530, 495, "λ", 30, BLUE, "start", "bold")
    s.rect(586, 470, 34, 30, BLUE, BLUE, 4, rx=5)
    s.text(630, 495, "λ1000", 30, BLUE, "start", "bold")

    # ---------- 底部：λ 对尾部钝感 ----------
    s.text(400, 552, f"λ {lam_base:.4f} → {lam_base:.4f}", 30, INK,
           "middle")
    s.text(400, 598, f"min p {p_base:.2e} → {p_inj:.2e}", 30, INK, "middle")
    s.text(400, 652, PHRASES[2], 32, INK, "middle", "bold")

    s.save("16_lambda_scaling_standardization.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
