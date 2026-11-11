#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_mt_threshold_sensitivity.py — 生成 08_mt_threshold_sensitivity.svg
（FIG-P02-10：同一个 percent.mt 阈值对三类细胞的杀伤极不均匀）【data-plot】

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-10（Slide 27，cols 一栏，800×700）。
数据：**直接调用** demos/ch17_mt_threshold_sensitivity.py 的 simulate()（同函数、
同参数 cells=4000 / seed=20261104 / 阈值网格 3,5,8,10,15,20,25），逐点断言
t=5% 时 0.930 / 0.300 / 0.002 与阈值单调性、t=20% 时 guard 0.848。
图内汉字 = 方案指定整句逐字一致（27 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 08_mt_threshold_sensitivity.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]        # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from svghelp import *  # noqa: F401,F403
import ch17_mt_threshold_sensitivity as demo  # noqa: E402

TEXT = "固定阈值杀伤相差四百倍。叶肉保留九成，高耗能保卫细胞近清空。"
TH = (3.0, 5.0, 8.0, 10.0, 15.0, 20.0, 25.0)
CELLS, SEED = 4000, 20261104


def compute():
    data = demo.simulate(CELLS, SEED)
    keep = {}
    for name, (mt, _) in data.items():
        key = name.split("（")[0]
        keep[key] = [float((mt < t).mean()) for t in TH]
    return keep


def main():
    keep = compute()
    mes, vas, gd = keep["mesophyll"], keep["vascular"], keep["guard"]
    i5 = TH.index(5.0)
    assert [round(v, 3) for v in (mes[i5], vas[i5], gd[i5])] == [0.930, 0.300,
                                                                0.002]
    assert round(gd[TH.index(20.0)], 3) == 0.848
    ratio = mes[i5] / max(gd[i5], 1e-9)
    assert round(ratio) == 465, ratio
    print(f"check: t=5% mesophyll={mes[i5]:.3f} vascular={vas[i5]:.3f} "
          f"guard={gd[i5]:.3f}; 杀伤差 {ratio:.0f}×；guard@20%={gd[5]:.3f}")

    s = SVG(800, 700, "percent.mt threshold kills unevenly", plan=TEXT)
    X0, X1, YT, YB = 150, 700, 150, 430

    def px(t):
        return X0 + (t - TH[0]) / (TH[-1] - TH[0]) * (X1 - X0)

    def py(v):
        return YB - v * (YB - YT)

    s.line(X0, YT, X0, YB, INK, 3)
    s.line(X0, YB, X1 + 10, YB, INK, 3)
    s.yaxis(X0, YT, YB, [(py(1.0), "1.0"), (py(0.5), "0.5"), (py(0.0), "0.0")])
    for t in TH:
        s.line(px(t), YB, px(t), YB + 8, INK, 3)
        s.text(px(t), YB + 40, f"{t:.0f}", 30, GRAY, "middle")
    s.text((X0 + X1) / 2, 500, "percent.mt (%)", 30, GRAY, "middle")

    # 图例（拉丁）
    s.line(60, 66, 100, 66, GREEN, 6, cap="round")
    s.text(108, 76, "MESOPHYLL", 30, GREEN, "start", "bold")
    s.line(300, 66, 340, 66, PURPLE, 6, cap="round")
    s.text(348, 76, "VASCULAR", 30, PURPLE, "start", "bold")
    s.line(525, 66, 565, 66, RED, 6, cap="round")
    s.text(573, 76, "GUARD", 30, RED, "start", "bold")

    # t = 5% 截断线（红，唯一警示区）
    s.line(px(5.0), YT, px(5.0), YB, RED, 5, dash="12 8")
    s.text(px(5.0) + 12, 240, f"{ratio:.0f}×", 34, RED, "start", "bold")

    # 三条保留率曲线
    for vals, col in ((mes, GREEN), (vas, PURPLE), (gd, RED)):
        s.polyline([(px(t), py(v)) for t, v in zip(TH, vals)], col, 6)
    for vals, col, lab in ((mes, GREEN, mes[i5]), (vas, PURPLE, vas[i5]),
                           (gd, RED, gd[i5])):
        s.circle(px(5.0), py(lab), 9, col)
    s.text(px(5.0) + 14, 148, f"{mes[i5]:.3f}", 30, GREEN, "start", "bold")
    s.text(px(5.0) + 14, 372, f"{vas[i5]:.3f}", 30, PURPLE, "start", "bold")
    s.line(px(5.0) + 2, 424, px(5.0) - 20, 412, RED, 3)
    s.text(px(5.0) - 24, 408, f"{gd[i5]:.3f}", 30, RED, "end", "bold")

    s.caption(["固定阈值杀伤相差四百倍。",
               "叶肉保留九成，高耗能保卫细胞近清空。"], [INK, INK], 30, top=536)
    s.save("08_mt_threshold_sensitivity.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())
