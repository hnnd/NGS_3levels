#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_annotation_bias_specific_genes.py — 22_annotation_bias_specific_genes.svg
（FIG-M02-28，P64，cols）：注释口径不统一致假特异基因暴涨双面板【data-plot】

方案：reviews/course/M02_FIGP_001.md §4 FIG-M02-28（失效条件 11.5.1）。
数据（与 demos 现跑一致）：demos/ch11_annotation_bias.py --selftest
（种子 20261104）：统一注释（全 P1）各株基因数 2088–2132、特异家族 1629–1657；
混入第 12 株宽松规则（P2）后基因数 9993、特异家族 8150，其中背景噪声 ORF 7919 ＋
其余 11 株物理存在但 P1 漏检 221 ＋ 真实特异 10，假特异占比 99.9%。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 22_annotation_bias_specific_genes.py
"""
import contextlib
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch11_annotation_bias as demo  # noqa: E402

from svghelp import (BLUE, GRAY, GREEN, INK, ORANGE, PANEL, RED, SVG, WHITE)


def check_data():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = demo.run_panel(seed=20261104)
    assert min(r["uni_genes"]) == 2088 and max(r["uni_genes"]) == 2132
    assert min(r["uni_spec"]) == 1629 and max(r["uni_spec"]) == 1657
    assert r["mix_genes"][11] == 9993 and r["mix_spec"][11] == 8150
    assert (r["n_noise12"], r["n_miss"], r["n_real"]) == (7919, 221, 10)
    fake = (r["n_noise12"] + r["n_miss"]) / 8150 * 100
    assert abs(fake - 99.9) < 0.05, fake
    print(f"check: 统一 {min(r['uni_genes'])}–{max(r['uni_genes'])} 基因 / "
          f"{min(r['uni_spec'])}–{max(r['uni_spec'])} 特异；混入 P2 后 "
          f"{r['mix_genes'][11]} 基因 / {r['mix_spec'][11]} 特异；"
          f"8150 = 7919+221+10，假特异 {fake:.1f}%（demos 复算）")
    return r


def bars(s, x0, y_top, plot_h, vmax, genes, spec, g_colors, s_colors,
         pitch=26, gw=10):
    for j in range(12):
        bx = x0 + j * pitch
        gh = genes[j] / vmax * plot_h
        sh = spec[j] / vmax * plot_h
        s.rect(bx, y_top + plot_h - gh, gw, gh, g_colors[j])
        s.rect(bx + gw + 1, y_top + plot_h - sh, gw, sh, s_colors[j])


def main():
    r = check_data()

    s = SVG(800, 700)

    plot_h = 210.0
    # 左面板：统一注释（全 P1）
    s.rect(30, 70, 350, 340, WHITE, "#E9E9E5", 3, rx=14)
    s.text(205, 116, "统一注释：每株约 2100", 30, BLUE, "middle", "bold")
    s.rect(60, 136, 16, 16, BLUE)
    s.text(82, 151, "genes", 30, GRAY, "start")
    s.rect(190, 136, 16, 16, PANEL, GRAY, 3)
    s.text(212, 151, "specific", 30, GRAY, "start")
    bars(s, 49, 170, plot_h, 2132.0, r["uni_genes"], r["uni_spec"],
         [BLUE] * 12, [PANEL] * 12)
    s.line(49, 170 + plot_h, 370, 170 + plot_h, INK, 4)

    # 右面板：混入第 12 株宽松规则（P2）
    s.rect(420, 70, 350, 340, WHITE, "#E9E9E5", 3, rx=14)
    s.text(585, 116, "混入宽规则：基因跳至 9993", 30, ORANGE, "middle",
           "bold")
    g_colors = [BLUE] * 11 + [ORANGE]
    s_colors = [PANEL] * 11 + [RED]
    bars(s, 439, 170, plot_h, 9993.0, r["mix_genes"], r["mix_spec"],
         g_colors, s_colors, pitch=22, gw=8)
    s.line(439, 170 + plot_h, 760, 170 + plot_h, INK, 4)
    s.line(693, 200, 716, 200, ORANGE, 4)
    s.text(762, 210, "9993", 30, ORANGE, "end", "bold")
    s.line(693, 246, 716, 246, RED, 4)
    s.text(762, 256, "8150", 30, RED, "end", "bold")

    # 拆解卡：8150 = 7919 + 221 + 10
    s.rect(30, 440, 460, 84, WHITE, "#E9E9E5", 4, rx=14)
    cells = [("7919", "noise ORF", BLUE), ("221", "missed", ORANGE),
             ("10", "real", GREEN)]
    for i, (num, lab, color) in enumerate(cells):
        cx = 80 + i * 150
        s.text(cx, 482, num, 34, color, "middle", "bold")
        s.text(cx, 514, lab, 30, GRAY, "middle")
    s.text(530, 462, "特异 8150", 30, RED, "start", "bold")
    s.text(530, 508, "假特异 99.9%", 30, RED, "start", "bold")

    # 底部红字
    s.text(400, 640, "必须统一重注释", 34, RED, "middle", "bold")

    s.save("22_annotation_bias_specific_genes.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
