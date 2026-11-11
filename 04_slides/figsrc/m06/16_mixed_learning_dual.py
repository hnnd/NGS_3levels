#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_mixed_learning_dual.py — FIG-M06-16 跨 run 混学双向失真与 ASV 门槛左移（data-plot）

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-16（P29，cols 一栏 800×700，data-plot）。
数据来源：`demos/ch18_error_model_mixrun.py --selftest` 现跑输出（本脚本 import 同函数、同参数复算
并断言）：混学/A = 2.49（干净 run 错误率被高估）、混学/B = 0.626（脏 run 被低估）；
亲本丰度 1e6 时判定边界 k* 从 run B 真实 4851 左移到混学 3185；
2000 亲本 × 30 单碱基错误变异的合成队列里，混学把 24 113 个错误变异误判为 ASV（真实模型 0 个）。
图内汉字 = 方案原句逐字，共 18 字（干净批次高估 / 脏批次低估 / 门槛左移假丰度）；
其余为 Q 档、倍率、k* 与计数。无网络；随机数经 demos 同种子（20261104）复算。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_mixed_learning_dual.py
"""
import contextlib
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]           # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch18_error_model_mixrun as mx                # noqa: E402

from svghelp import *                              # noqa: F401,F403,E402


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        r = mx.run([10, 15, 20, 25, 30, 35, 40], 2000000, 0.5, 6.0, 1e-40,
                   30.0, 2000, 30, 20261104)

    q = [10, 15, 20, 25, 30, 35, 40]
    ratio_a = r["p_pool0"] / r["pA0"]
    ratio_b = r["p_pool0"] / r["pB0"]
    kb_t, kb_p, ka_t, ka_p = r["bd"][1e6]

    # 与 demos --selftest 同口径的四项断言
    assert abs(ratio_a - 2.49) < 0.02, ratio_a
    assert abs(ratio_b - 0.626) < 0.02, ratio_b
    assert (kb_t, kb_p, ka_t) == (4851, 3185, 1450), r["bd"][1e6]
    assert r["false_pool"] == 24113 and r["false_true"] == 0, r["false_pool"]
    print(f"check: 混学/A = {ratio_a:.2f}，混学/B = {ratio_b:.3f}，"
          f"k* {kb_t} → {kb_p}，误判 {r['false_pool']} 个")

    s = SVG()

    # ================= 左面板：双向失真（混学/真实 倍率 vs Q 档） =================
    L, B, R, T = 104, 470, 400, 190
    lo, hi = 0.4, 3.0
    sy = (B - T) / (hi - lo)

    def ypos(v):
        return B - (v - lo) * sy

    s.line(L, B, R, B, INK, 4)
    s.line(L, B, L, T, INK, 4)
    s.text(L - 8, T - 26, "ratio", 30, GRAY, "start")   # 纵轴倍率（轴名用英文）
    s.text(R, B + 84, "Q", 30, GRAY, "middle")

    # 1.0× 基准线（= 真实谱，未失真）
    y1 = ypos(1.0)
    s.line(L, y1, R, y1, GRAY, 3, dash="12 9")
    s.text(L - 14, y1 + 10, "1.0", 30, GRAY, "end")
    # 2.0× / 3.0× 参考线：让读者看出两条曲线各偏离基准多少
    for vv in (2.0, 3.0):
        yv = ypos(vv)
        s.line(L, yv, R, yv, PANEL, 3, dash="10 9")
        s.text(L - 14, yv + 10, f"{vv:.1f}", 30, GRAY, "end")

    for qq in (10, 20, 30, 40):
        x = L + (qq - 10) / 30.0 * (R - L)
        s.line(x, B, x, B + 10, INK, 3)
        s.text(x, B + 40, str(qq), 30, GRAY, "middle")

    pts_a = [(L + (q_ - 10) / 30.0 * (R - L), ypos(r["lp"][i] / r["p_a"][i]))
             for i, q_ in enumerate(q)]
    pts_b = [(L + (q_ - 10) / 30.0 * (R - L), ypos(r["lp"][i] / r["p_b"][i]))
             for i, q_ in enumerate(q)]
    s.curve(pts_a, CYAN, 6)
    s.curve(pts_b, ORANGE, 6)

    # 两条曲线的倍率标注（都放在各自曲线的内侧，不压轴线与刻度）
    s.text(L + 18, pts_a[0][1] - 18, "2.49×", 32, CYAN_DEEP, "start", "bold")
    s.text(R - 10, pts_b[-1][1] - 20, "0.63×", 32, ORANGE_DEEP, "end", "bold")

    # ================= 右面板：判定门槛左移（k* 与误判区） =================
    RL, RR = 470, 752
    RT = 190
    s.line(RL, B, RR, B, INK, 4)
    s.text((RL + RR) / 2, B + 40, "k*", 30, GRAY, "middle")

    x_mid = RL + 132      # 混学门槛 3185（左）
    x_true = RL + 232     # run B 真实门槛 4851（右）
    s.rect(x_mid, RT + 34, x_true - x_mid, B - RT - 34, RED_TINT, rx=8)
    s.line(x_true, RT + 10, x_true, B, BLUE, 6, dash="14 10")
    s.line(x_mid, RT + 10, x_mid, B, RED, 6, dash="14 10")

    s.text(x_mid, RT - 2, "3185", 32, INK, "middle", "bold")
    s.text(x_true, RT - 2, "4851", 32, BLUE, "middle", "bold")

    # 误判量级：白色胶囊压在红区内，避免与两侧竖线相贴
    s.chip((x_mid + x_true) / 2, B - 96, "24 113", 30, fill=WHITE,
           stroke=RED_TINT, ink=RED, sw=3)

    # ================= 图内原句（三个短语，各自独立成行） =================
    s.text(252, 596, "干净批次高估", 32, CYAN_DEEP, "middle", "bold")
    s.text(252, 644, "脏批次低估", 32, ORANGE_DEEP, "middle", "bold")
    s.text(606, 596, "门槛左移假丰度", 32, INK, "middle", "bold")

    s.save("16_mixed_learning_dual.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
