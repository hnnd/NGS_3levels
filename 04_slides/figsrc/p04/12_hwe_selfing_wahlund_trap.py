#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_hwe_selfing_wahlund_trap.py — 生成 12_hwe_selfing_wahlund_trap.svg
（FIG-P04-12：第 27 页 cols 一栏「自交与 Wahlund 致 HWE 假显著」）【data-plot】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-12（P27，cols，800×700）。
依据：教材 §20.4.3——Wahlund 合并样本 99.6% 位点 p < 1e-6（分群后逐亚群检验
回到名义水平，p < 0.05 占 4.5%）；自交体系 s = 0.95（F = 0.905）时 100.0%
位点 p < 1e-6，盲目 `--hwe 1e-6` 删掉的是几乎所有真实多态位点。
数字入口：`textbook/demos/ch20_hwe_selfing_wahlund.py --selftest`
（二倍体口径、每场景 2000 个 SNP、种子 20261104）。本脚本直接调用该 demo 的
`run()` 重算三条比例并断言，不一致即失败退出；见回执核对表。
图内中文严格取方案给定 27 字（3 句，各按 4–5 字折成两行放在柱下）；
百分比与数字属符号。
结构＝三根「被 p < 1e-6 误杀的真实位点比例」柱（Wahlund 合并 99.6%、分群后
4.5%、自交 100.0%），横向虚线标 5% 名义水平。
红只用于两根误杀柱（合并样本与自交体系）。
无网络；随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 12_hwe_selfing_wahlund_trap.py
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
from ch20_hwe_selfing_wahlund import run                      # noqa: E402

PHRASES = ["分层样本误杀九成九", "分群后回到名义水平", "高自交体系位点全删"]
TEXT = "".join(PHRASES)

REF = dict(kill_w=99.6, split=4.5, kill_s=100.0)


def numbers():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = run(1000, 100, 0.95, 2000, 20261104)
    got = dict(kill_w=100 * r["kill_w"], split=100 * r["reject05_split"],
               kill_s=100 * r["kill_s"])
    for k, v in got.items():
        if abs(v - REF[k]) > 0.05:
            raise SystemExit(f"图面数字与 demos 现跑不一致：{k}={v:.1f}%")
    return got


def main():
    d = numbers()
    s = SVG(800, 700, "Blind HWE filtering kills real polymorphisms", plan=TEXT)

    ybase, hpl = 470, 330
    yv = lambda v: ybase - v / 100.0 * hpl

    s.arrow(84, ybase, 748, ybase, BLUE, 5, 14)
    s.arrow(84, ybase, 84, ybase - hpl - 14, BLUE, 5, 14)
    for v in (0, 50, 100):
        y = yv(v)
        s.line(76, y, 84, y, BLUE, 3)
        s.text(64, y + 10, str(v), 30, GRAY, "end")

    # 5% 名义水平
    y5 = yv(5)
    s.line(748, y5, 96, y5, GRAY, 3, dash="12 9")
    s.text(744, y5 - 12, "5%", 30, GRAY, "end", "bold")

    bars = [(170, d["kill_w"], RED, ("分层样本", "误杀九成九"), RED),
            (400, d["split"], GREEN, ("分群后回到", "名义水平"), GREEN),
            (630, d["kill_s"], RED, ("高自交体系", "位点全删"), RED)]
    for cx, v, col, lines, tcol in bars:
        top = yv(v)
        s.rect(cx - 60, top, 120, ybase - top, col, None, 0, rx=8)
        if v > 30:
            s.text(cx, top + 50, f"{v:.1f}%", 30, WHITE, "middle", "bold")
        else:
            s.text(cx, top - 18, f"{v:.1f}%", 30, col, "middle", "bold")
        s.text(cx, ybase + 50, lines[0], 30, tcol, "middle", "bold")
        s.text(cx, ybase + 96, lines[1], 30, tcol, "middle", "bold")

    s.save("12_hwe_selfing_wahlund_trap.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())
