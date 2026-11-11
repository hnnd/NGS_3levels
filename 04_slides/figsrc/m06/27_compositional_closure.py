#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""27_compositional_closure.py — FIG-M06-27 相对丰度组成性闭合伪影（data-plot）

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-27（P46，cols 一栏 800×700，data-plot）。
数据来源：`demos/ch18_compositional_closure.py --selftest` 现跑输出（本脚本 import 同函数、同参数
复算并断言）：目标类群 A 绝对量翻倍（份额 0.400 → 0.571，+17.1 个百分点），其余 7 个类群绝对量
不变却在相对丰度上全部被判显著下降（−1.5% 至 −3.7% 个百分点，7.0/7 个）；居中 CLR 把未变类群
效应量恢复到 0（|均值| = 0.0031，显著数 0.3 个），A 恢复为 +ln2 = 0.693。
图内汉字 = 方案原句逐字，共 20 字（一菌真实翻倍 / 七类群虚假下调 / 和为一闭合伪影）；
其余为份额变化、CLR 值与类群编号。无网络；随机数经 demos 同种子（20261104）复算。
用法：PYTHONDONTWRITEBYTECODE=1 python3 27_compositional_closure.py
"""
import contextlib
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]           # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch18_compositional_closure as cc             # noqa: E402

from svghelp import *                              # noqa: F401,F403,E402


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        r = cc.run(8, 10, 20000, 2.0, 0.40, 20, 0.05, 0.5, 20261104)

    d_rel = r["d_rel"]              # 份额的绝对变化（A 的 +0.171 即 +17.1 个百分点）
    d_clrc = r["d_clrc"]            # 居中 CLR 变化
    sig_rel_down = r["sig_rel_down"]
    sig_clrc = r["sig_clrc"]

    # 与 demos --selftest 同口径的断言：一菌翻倍、七类全降、CLR 恢复
    assert abs(d_rel[0] - 0.171) < 0.002, d_rel[0]
    assert all(x < 0 for x in d_rel[1:]), d_rel[1:]
    assert 6.9 <= sig_rel_down <= 7.1, sig_rel_down
    assert 0.2 <= sig_clrc <= 0.5, sig_clrc
    assert abs(d_clrc[0] - 0.693) < 0.01, d_clrc[0]
    assert max(abs(x) for x in d_clrc[1:]) < 0.02, d_clrc[1:]
    print(f"check: A {100*d_rel[0]:+.1f}%，未变 7 类 {100*min(d_rel[1:]):+.1f}% ~ "
          f"{100*max(d_rel[1:]):+.1f}%，相对下降显著 {sig_rel_down:.1f}/7，"
          f"居中 CLR 显著 {sig_clrc:.1f} 个，A 居中 CLR {d_clrc[0]:+.3f}")

    s = SVG()

    L, R = 176, 736
    n = 8
    pitch = (R - L) / n
    bw = 46

    # ============ 上：相对丰度变化（A 上涨，其余七类被闭合压成「显著下降」） ============
    B, T = 372, 196                 # 零线、纵轴上限（+20 个百分点）
    sy = (B - T) / 0.20             # 纵轴 ±20 个百分点：+17.1 与 −1.5~−3.7 同尺度

    s.line(L, B, R, B, INK, 4)                       # 零线
    s.text(L - 12, B - 10, "Δ", 30, GRAY, "end")
    s.text(L - 12, T + 10, "+20%", 30, GRAY, "end")

    for i in range(n):
        cx = L + pitch * (i + 0.5)
        v = d_rel[i]
        h = abs(v) * sy
        if i == 0:
            s.rect(cx - bw / 2, B - h, bw, h, CYAN, rx=6)
            s.text(cx + 8, B - h - 16, f"{100*v:+.1f}%", 32, CYAN_DEEP, "start", "bold")
        else:
            s.rect(cx - bw / 2, B, bw, max(h, 6), ORANGE, rx=4)

    # 七类的幅度：一根红色方括号 + 区间标注（红色仅此 2 处：括号与区间数字）
    zb_x0 = L + pitch * 1
    zb_x1 = R
    zb_y = B + 84
    t = 12
    s.path(f"M {zb_x0} {zb_y - t} L {zb_x0} {zb_y} L {zb_x1} {zb_y} "
           f"L {zb_x1} {zb_y - t}", stroke=RED, sw=5)
    s.text((zb_x0 + zb_x1) / 2, zb_y + 46,
           f"{100*min(d_rel[1:]):+.1f}% ~ {100*max(d_rel[1:]):+.1f}%",
           32, RED, "middle", "bold")

    # 类群标签行
    for i in range(n):
        cx = L + pitch * (i + 0.5)
        s.text(cx, B + 40, "A" if i == 0 else str(i), 30, INK, "middle", "bold")

    # ============ 下：居中 CLR 恢复（同序类群，条形贴零线） ============
    B2, T2 = 640, 566
    s.line(L, B2, R, B2, GRAY, 4)
    s.text(L - 12, B2 - 10, "clr", 30, GRAY, "end")

    sy2 = (B2 - T2) / 0.80
    for i in range(n):
        cx = L + pitch * (i + 0.5)
        v = d_clrc[i]
        if i == 0:
            h = abs(v) * sy2
            s.rect(cx - bw / 2, B2 - h, bw, h, GREEN, rx=6)
            s.text(cx + 8, B2 - h - 14, f"{v:+.3f}", 30, GREEN, "start", "bold")
        else:
            # 未变类群：直接落在零线上（圆点 = 变化量为 0，不与 A 的绿柱混淆）
            s.circle(cx, B2, 9, GREEN_TINT, GREEN, 3)
        s.text(cx, B2 + 44, "A" if i == 0 else str(i), 30, INK, "middle", "bold")

    # ============ 图内原句三句 ============
    s.text(96, 64, "一菌真实翻倍", 34, CYAN_DEEP, "start", "bold")
    s.text(704, 64, "七类群虚假下调", 34, ORANGE_DEEP, "end", "bold")
    s.text(400, 128, "和为一闭合伪影", 32, INK, "middle", "bold")

    s.save("27_compositional_closure.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
