#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_lca_escalation_ladder.py — FIG-M07-10 参考库缺失引发的 LCA 上浮与假精确阶梯（data-plot）

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-10（P22，`.cols` 一栏 800×700，data-plot）。
数据来源：`demos/ch19_lca_escalation.py --selftest` 现跑输出；本脚本 import 同函数、同参数
（n_reads=200000、unique_frac=0.35、n_sisters=4、seed=20261104）复算并断言：
  D0 属齐全：种(正确) 34.9% / 属(上浮) 65.1%；
  D1 删目标种 T：属(上浮) 65.0% / 未分类 35.0%，种级整批丢失；
  D4 剩 1 姐妹种：种(错误) 64.8% / 未分类 35.2%（唯一命中直下 → 张冠李戴）。
图内汉字 = 方案原句逐字，共 29 字（库全：定种三成半 / 缺种：上浮到属六成半 /
剩单种：假精确张冠李戴）；阶段名只写「库全 / 缺种 / 剩单种」，百分比与条内数字为阿拉伯数字。
三段堆叠条共用 100% 标尺：绿=定到正确种，青蓝=上浮到属，灰=未分类，红（唯一红处）=定到错误种。
无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 10_lca_escalation_ladder.py
"""
import contextlib
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]           # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch19_lca_escalation as lca                  # noqa: E402

from svghelp import *                              # noqa: F401,F403,E402

ROWS = [("库全：定种三成半", "D0 属齐全"),
        ("缺种：上浮到属六成半", "D1 删目标种T"),
        ("剩单种：假精确张冠李戴", "D4 剩1姐妹")]


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        r = lca.run(200000, 0.35, 4, 20261104)
    d0, d1, d4 = (r[n] for n in ("D0 属齐全", "D1 删目标种T", "D4 剩1姐妹"))

    # 与 demos --selftest 同口径：图里只画这些数
    assert abs(100 * d0["种(正确)"] - 34.9) < 0.2
    assert abs(100 * d1["属(上浮)"] - 65.0) < 0.2
    assert abs(100 * d1["种(正确)"]) < 0.5
    assert abs(100 * d4["种(错误)"] - 64.8) < 0.2
    assert abs(100 * d4["未分类"] - 35.2) < 0.2

    DATA = [
        (ROWS[0][0], [("种(正确)", d0["种(正确)"], GREEN),
                      ("属(上浮)", d0["属(上浮)"], CYAN),
                      ("未分类", d0["未分类"], PANEL)]),
        (ROWS[1][0], [("种(正确)", d1["种(正确)"], GREEN),
                      ("属(上浮)", d1["属(上浮)"], CYAN),
                      ("未分类", d1["未分类"], PANEL)]),
        (ROWS[2][0], [("种(正确)", d4["种(正确)"], GREEN),
                      ("种(错误)", d4["种(错误)"], RED),
                      ("未分类", d4["未分类"], PANEL)]),
    ]

    s = SVG()
    L, R = 48, 736                             # 100% 标尺
    BH, PITCH, Y0 = 66, 190, 150
    for i, (cap, segs) in enumerate(DATA):
        y = Y0 + i * PITCH
        s.text(L, y - 22, cap, 36, RED if i == 2 else BLUE, "start", "bold")
        x = L
        for name, frac, col in segs:
            w = (R - L) * frac
            if w < 4:
                continue
            s.rect(x, y, w, BH, col, rx=8)
            pct = 100 * frac
            if w >= 118:                       # 够宽就写进条内（反白/深色字）
                ink = WHITE if col in (GREEN, CYAN, RED) else INK
                s.text(x + w / 2, y + BH / 2 + 11, f"{pct:.1f}%", 30, ink,
                       "middle", "bold")
            else:                              # 零段只在条端外标 0.0%
                s.text(x + w + 10, y + BH / 2 + 11, f"{pct:.1f}%", 30, GRAY,
                       "start", "bold")
            x += w
    # 100% 标尺基线（零段位置一眼可见）
    for i in range(3):
        s.line(L, y + BH, R, y + BH, INK, 3)

    reds = s.save("10_lca_escalation_ladder.svg")
    print(f"check: D0 {100*d0['种(正确)']:.1f}%/{100*d0['属(上浮)']:.1f}%；"
          f"D1 {100*d1['属(上浮)']:.1f}%/{100*d1['未分类']:.1f}%；"
          f"D4 {100*d4['种(错误)']:.1f}%/{100*d4['未分类']:.1f}%（红 {reds} 处）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
