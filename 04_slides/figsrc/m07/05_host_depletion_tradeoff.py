#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_host_depletion_tradeoff.py — FIG-M07-06 去宿主严松权衡与选择性误伤（data-plot）

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-06（P18，`.cols` 一栏 800×700，data-plot）。
数据来源：`demos/ch19_host_depletion_tradeoff.py --selftest` 现跑输出（本脚本 import 同函数、
同参数复算并断言），根际/组织型 h=70% 档：
  松 τ=0.80：总微生物误伤 0.86%、保守同源 8.56%、典型类 0.001%；
  严 τ=0.63：总微生物误伤 4.56%、保守同源 44.16%（红柱）、典型类 0.158%。
图内汉字 = 方案原句逐字，共 27 字（松阈值：误伤少残留多 / 严阈值：保守同源误伤四成 / 选择性误杀）；
三类条的类名按「工具/字段名可留英文」用 total / conserved / typical 三词，避免超出 30 汉字红线。
横轴为对数刻度（0.01%–100%），否则 0.001% 与 44% 在同一线性轴上不可同框；数值写在条端。
无网络；随机数经 demos 同种子（20261104）复算，不另取种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_host_depletion_tradeoff.py
"""
import contextlib
import io
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]           # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch19_host_depletion_tradeoff as hd          # noqa: E402

from svghelp import *                              # noqa: F401,F403,E402


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        r = hd.run(400000, 0.10, 20261104)
    lo = r[("根际/组织型 h=70%", "松")]
    st = r[("根际/组织型 h=70%", "严")]

    # 与 demos --selftest 同口径的断言：图里只画这几个数
    assert abs(100 * lo["mic_kill"] - 0.86) < 0.02, lo["mic_kill"]
    assert abs(100 * st["mic_kill"] - 4.56) < 0.02, st["mic_kill"]
    assert abs(100 * st["cons_kill"] - 44.16) < 0.05, st["cons_kill"]
    assert abs(100 * st["typ_kill"] - 0.158) < 0.002, st["typ_kill"]
    assert st["cons_kill"] > 5 * st["typ_kill"]

    GROUPS = [
        ("τ=0.80", CYAN_DEEP, CYAN, lo),
        ("τ=0.63", ORANGE_DEEP, ORANGE, st),
    ]

    s = SVG()

    # ---------------- 对数横轴画在上方：0.01% → 100% ----------------
    L, R, AX = 344, 668, 176
    VX = 792                        # 数值右对齐锚点（条端与数值之间留白）
    XMIN, XMAX = -2.0, 2.0                       # log10(百分比)
    s.line(L, AX, R, AX, INK, 4)
    for pct in (0.01, 1, 100):                  # 只标三个十倍级，避免刻度文字相挤
        x = L + (math.log10(pct) - XMIN) / (XMAX - XMIN) * (R - L)
        s.line(x, AX, x, AX + 12, INK, 3)
        s.line(x, AX + 12, x, 528, PANEL, 3, dash="10 10")
        s.text(x, AX - 14, f"{pct:g}%", 30, GRAY, "middle")

    # ---------------- 两组 × 三条，横条 + 右侧数值列 --------------
    CATS = [("total", "mic_kill"), ("conserved", "cons_kill"),
            ("typical", "typ_kill")]
    ROW0, PITCH, BH, GROUP_GAP = 212, 52, 28, 62
    y = ROW0

    for gi, (name, head, barcol, d) in enumerate(GROUPS):
        s.text(24, y - 16, name, 32, head, "start", "bold")
        if gi:                          # 第一组的分隔线与上方对数轴重合，跳过
            s.line(L, y - 36, VX, y - 36, PANEL, 3)
        for cat, key in CATS:
            pct = 100 * d[key]
            frac = (math.log10(max(pct, 0.01)) - XMIN) / (XMAX - XMIN)
            w = max(frac * (R - L), 8)
            col = barcol
            if key == "cons_kill" and name == "τ=0.63":
                col = RED                      # 唯一红处：保守同源类在严档被误杀
            s.text(L - 18, y + BH / 2 + 11, cat, 30, INK, "end")
            s.rect(L, y, R - L, BH, PANEL, rx=8)
            s.rect(L, y, w, BH, col, rx=8)
            s.text(VX, y + BH / 2 + 11,
                   f"{pct:.3f}%" if pct < 1 else
                   (f"{pct:.2f}%" if pct < 10 else f"{pct:.1f}%"),
                   30, RED if col == RED else INK, "end", "bold")
            y += PITCH
        y += GROUP_GAP

    # ---------------- 方案原句 ----------------
    s.text(400, 104, "松阈值：误伤少残留多", 34, CYAN_DEEP, "middle", "bold")
    s.text(400, 616, "严阈值：保守同源误伤四成", 34, RED, "middle", "bold")
    s.text(400, 668, "选择性误杀", 30, GRAY, "middle")

    s.save("05_host_depletion_tradeoff.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
