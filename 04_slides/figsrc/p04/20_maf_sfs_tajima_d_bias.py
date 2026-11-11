#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_maf_sfs_tajima_d_bias.py — 生成 20_maf_sfs_tajima_d_bias.svg
（FIG-P04-20：第 39 页 cols 一栏「MAF 过滤切除稀有端与 Tajima's D 假正漂移」）【data-plot】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-20（P39，cols，800×700）。
依据：教材 §20.4.7 与 §20.5.3——多样性统计依赖稀有等位基因的真实频数分布；
在多样性分析前滤 MAF 等于把 SFS 的稀有端人为切掉：θ_W 按被删位点数等比坍塌，
π 因为权重集中在中间频率几乎不动，两者之差被动转正，Tajima's D 系统性偏正。
数字入口：`textbook/demos/ch20_tajima_d_maf_bias.py --selftest`
（单倍体 n = 40、每次 20 000 个分离位点、200 次重复、种子 20261104；demo 现跑
打印 S 20000→15187（−24.1%）、θ_W 4701.96→3570.44（−24.1%）、
π 4587.10→4351.03（−5.1%）、Tajima's D −0.092→+0.825）。
本脚本直接调用该 demo 的 `run()` 取同一批统计量并断言上列读数，
不一致即失败退出；见回执核对表。
图内中文严格取方案给定 26 字（3 句：一句标 SFS 稀有端被切，两句进底部结论条）；
S、θ_W、π、D_T 与数字属符号。
结构＝上半张折叠 SFS（第 1 个计数类被红色感叹号标为切除档）＋下半四行
「过滤前 → 过滤后」的读数对照。
红只标「次频切除位点坍塌」与「分离位点骤降两成四」两处。
无网络；随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 20_maf_sfs_tajima_d_bias.py
"""
import contextlib
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from svghelp import *                                        # noqa: E402,F401,F403
from ch20_tajima_d_maf_bias import run                        # noqa: E402
import numpy as np                                           # noqa: E402

PHRASES = ["次频切除位点坍塌", "分离位点骤降两成四", "多样性几乎保持平稳"]
TEXT = "".join(PHRASES)

SITES, REPS, MAF, SEED = 20000, 200, 0.05, 20261104
REF = dict(S=15187, pi=4587.10, tw=4701.96, D=-0.092,
           pi_f=4351.03, tw_f=3570.44, D_f=0.825)


def numbers():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        stat = run(40, SITES, REPS, MAF, SEED)
    got = {k: float(np.median(v)) for k, v in stat.items()}
    got["S"] = SITES
    checks = [("S", got["S_f"], REF["S"]), ("pi", got["pi"], REF["pi"]),
              ("tw", got["tw"], REF["tw"]), ("D", got["D"], REF["D"]),
              ("pi_f", got["pi_f"], REF["pi_f"]),
              ("tw_f", got["tw_f"], REF["tw_f"]), ("D_f", got["D_f"], REF["D_f"])]
    for name, g, e in checks:
        tol = 0.006 if name in ("D", "D_f") else 0.6
        if abs(g - e) > tol:
            raise SystemExit(f"图面数字与 demos 现跑不一致：{name}={g} vs {e}")
    return got


def main():
    d = numbers()
    s = SVG(800, 700, "MAF filtering cuts the rare end of the SFS", plan=TEXT)

    # ---------- 上半：折叠 SFS ----------
    s.text(60, 66, PHRASES[0], 30, RED, "start", "bold")
    x0, ybase, hmax = 70, 330, 196
    heights = [180, 92, 62, 47, 38, 32, 27, 23, 20, 18]
    for i, h in enumerate(heights):
        x = x0 + i * 68
        if i == 0:                                    # 被 MAF 0.05 切掉的计数类
            s.rect(x, ybase - h, 40, h, PAPER, GRAY, 3, rx=5, dash="9 7")
        else:
            s.rect(x, ybase - h, 40, h, BLUE_TINT, BLUE, 3, rx=5)
    s.arrow(60, ybase, 752, ybase, BLUE, 5, 14)
    for i in range(10):
        s.text(x0 + i * 68 + 20, ybase + 34, str(i + 1), 30, GRAY, "middle")
    s.text(20, ybase + 34, "i", 30, BLUE, "middle", "bold")

    # MAF 0.05 的切点
    xc = x0 + 54
    s.line(xc, 108, xc, ybase, GRAY, 3, dash="8 8")
    s.text(xc + 8, 100, "0.05", 30, GRAY, "start", "bold")

    # ---------- 下半：四行读数对照 ----------
    rows = [("S", f"{SITES}", f"{d['S_f']:.0f}", "−24.1%"),
            ("θ_W", f"{d['tw']:.2f}", f"{d['tw_f']:.2f}", "−24.1%"),
            ("π", f"{d['pi']:.2f}", f"{d['pi_f']:.2f}", "−5.1%"),
            ("D_T", f"{d['D']:+.3f}".replace("-", "−"), f"{d['D_f']:+.3f}", "+0.92")]
    for i, (lab, before, after, delta) in enumerate(rows):
        y = 396 + i * 50
        s.text(44, y, lab, 32, BLUE, "start", "bold")
        s.text(300, y, before, 30, BLUE, "end", "bold")
        s.arrow(322, y - 10, 378, y - 10, GRAY, 4, 12)
        s.text(400, y, after, 30, ORANGE, "start", "bold")
        s.text(620, y, delta, 30, GRAY, "start", "bold")

    s.caption([PHRASES[1], PHRASES[2]], [RED, GREEN], 30, gap=40, pad_top=22)

    s.save("20_maf_sfs_tajima_d_bias.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 26, TEXT
    raise SystemExit(main())
