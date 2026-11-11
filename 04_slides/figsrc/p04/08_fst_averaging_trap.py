#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_fst_averaging_trap.py — 生成 08_fst_averaging_trap.svg
（FIG-P04-08：第 21 页 cols 一栏「滑窗求平均两法分叉」）【data-plot】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-08（P21，cols，800×700）。
依据：教材 §20.4.2——同一批窗口，分量和之比（ΣN/ΣD，vcftools 的
`WEIGHTED_FST`）中位数 0.0723 [P10 0.0379, P90 0.1153]，比值平均
（mean(N/D)，`MEAN_FST`）中位数 0.0455 [P10 0.0239, P90 0.0639]，窗口级偏差
中位数 0.0279；只看窗内常见变异时偏差降到 0.0067（约为 1/4）。
数字入口：`textbook/demos/ch20_fst_average_trap.py --selftest`
（两群各 20 条单倍体、10 000 个 SNP、每窗 50 个、种子 20261104）。
本脚本直接调用该 demo 的 `run()` 取同一批窗口读数并断言中位数与分位数，
不一致即失败退出；见回执核对表。
图内中文严格取方案给定 30 字（4 句）；列名、数字与 P10/P90 属符号。
结构＝两根中位数＋P10–P90 须线（左深蓝／右橙）与中间一条偏差双向箭头。
红只标「比值平均被稀有拉偏」一处。
无网络；随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 08_fst_averaging_trap.py
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
from ch20_fst_average_trap import run                        # noqa: E402
import numpy as np                                           # noqa: E402

PHRASES = ["分量和之比稳定", "比值平均被稀有拉偏", "偏差百分之二点八", "认准加权列名"]
TEXT = "".join(PHRASES)

REF = dict(roa=(0.0723, 0.0379, 0.1153), aor=(0.0455, 0.0239, 0.0639),
           dev=0.0279)


def numbers():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = run(5000, 5000, 50, 0.20, 0.005, 20261104)
    med_roa = float(np.median(r["roa"]))
    med_aor = float(np.median(r["aor"]))
    p10_roa = float(np.percentile(r["roa"], 10))
    p90_roa = float(np.percentile(r["roa"], 90))
    p10_aor = float(np.percentile(r["aor"], 10))
    p90_aor = float(np.percentile(r["aor"], 90))
    dev = float(np.median(r["dev_mixed"]))
    got = (med_roa, p10_roa, p90_roa, med_aor, p10_aor, p90_aor, dev)
    ref = (0.0723, 0.0379, 0.1153, 0.0455, 0.0239, 0.0639, 0.0279)
    for g, e in zip(got, ref):
        if abs(g - e) > 5e-4:
            raise SystemExit(f"图面数字与 demos 现跑不一致：{g:.4f} vs {e}")
    return dict(roa=(med_roa, p10_roa, p90_roa),
                aor=(med_aor, p10_aor, p90_aor), dev=dev)


def main():
    d = numbers()
    s = SVG(800, 700, "Averaging order splits window F_ST", plan=TEXT)

    ybase, ytop = 450, 150
    vmax = 0.13

    def yv(v):
        return ybase - v / vmax * (ybase - ytop)

    s.arrow(84, ybase, 748, ybase, BLUE, 5, 14)
    s.arrow(84, ybase, 84, ytop - 6, BLUE, 5, 14)
    for v in (0.00, 0.05, 0.10):
        y = yv(v)
        s.line(76, y, 84, y, BLUE, 3)
        s.text(64, y + 10, f"{v:.2f}", 30, GRAY, "end")

    cols = [(250, d["roa"], BLUE, "WEIGHTED_FST", PHRASES[0], BLUE),
            (560, d["aor"], ORANGE, "MEAN_FST", PHRASES[1], RED)]
    for cx, (med, p10, p90), col, name, phrase, pcol in cols:
        s.line(cx, yv(p90), cx, yv(p10), col, 5)
        for v in (p90, p10):
            s.line(cx - 24, yv(v), cx + 24, yv(v), col, 5)
        s.rect(cx - 44, yv(med) - 13, 88, 26, col, None, 0, rx=8)
        s.text(cx, 172, name, 30, col, "middle", "bold")
        if cx == 250:
            s.text(cx - 62, yv(med) + 11, f"{med:.4f}", 30, col, "end", "bold")
        else:
            s.text(cx + 62, yv(med) + 11, f"{med:.4f}", 30, col, "start", "bold")
        s.text(cx, 512, f"[{p10:.3f}, {p90:.3f}]", 30, GRAY, "middle")
        s.text(cx, 552, phrase, 30, pcol, "middle", "bold")

    # 中间：两种口径的窗口级偏差
    s.darrow(405, yv(d["roa"][0]) + 6, yv(d["aor"][0]) - 6, GRAY, 4, 12)
    s.text(405, 272, f"{d['dev']:.4f}", 30, GRAY, "middle", "bold")

    s.caption([PHRASES[2], PHRASES[3]], [INK, BLUE], 30, top=566, gap=44,
              pad_top=22)

    s.save("08_fst_averaging_trap.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
