#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_pseudoreplication_power_curve.py — 生成 05_pseudoreplication_power_curve.svg
（FIG-P02-05：细胞级伪重复的假阳性率随细胞数暴涨 vs pseudobulk 稳态）【data-plot】

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-05（Slide 17，cols 一栏，800×700）。
数据：**直接调用** demos/ch17_pseudorep_vs_pseudobulk.py 的生成逻辑（同一函数、
同一参数 genes=150 / samples=3 / reps=20 / alpha=0.05 / sigma=0.3 / seed=20261104），
并逐点断言 0.723 / 0.854 / 0.925 / 0.068 与对照 0.051 与 demos 现跑输出逐位一致。
图内汉字 = 方案指定整句逐字一致（28 汉字）；轴、图例用英文（04_slides/README）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 05_pseudoreplication_power_curve.py
"""
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]        # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
from svghelp import *  # noqa: F401,F403
import ch17_pseudorep_vs_pseudobulk as demo  # noqa: E402

TEXT = "假阳性率随细胞数暴涨，聚合检验紧贴基准。膨胀源自同管共享方差。"
# 图内标签的中文译文（D135：说明性短语一律中文；FP / 数字等字段与符号保留）
EXTRA = "每样本细胞数细胞级聚合检验"
GENES, SAMPLES, REPS, ALPHA, SIGMA, SEED = 150, 3, 20, 0.05, 0.3, 20261104
MS = (250, 1000, 4000)


def compute():
    """与 demos --selftest 完全相同的调用路径，返回实测假阳性率。"""
    res = demo.run(GENES, SAMPLES, REPS, ALPHA, SIGMA, SEED)
    rng = np.random.default_rng(SEED + 999)
    control = float(np.mean([demo.fp_at(GENES, SAMPLES, 4000, 0.0, rng, ALPHA)
                             for _ in range(REPS // 2)]))
    return res, control


def main():
    res, control = compute()
    cell = [res[m][0] for m in MS]
    pb = [res[m][1] for m in MS]

    # 与 demos 现跑输出逐点核对（三位小数）
    assert [round(v, 3) for v in cell] == [0.723, 0.854, 0.925], cell
    assert [round(v, 3) for v in pb] == [0.068, 0.068, 0.068], pb
    assert round(control, 3) == 0.051, control
    print(f"check: cell={[round(v, 3) for v in cell]} "
          f"pseudobulk={[round(v, 3) for v in pb]} control={control:.3f}")

    s = SVG(800, 700, "Pseudoreplication false-positive rate", plan=TEXT,
            extra=EXTRA)
    X0, X1, YT, YB = 150, 720, 130, 430
    XP = (200, 400, 600)

    def py(v):
        return YB - v * (YB - YT) / 1.0

    s.line(X0, YT, X0, YB, INK, 3)
    s.line(X0, YB, X1, YB, INK, 3)
    s.yaxis(X0, YT, YB, [(py(1.0), "1.0"), (py(0.5), "0.5"), (py(0.0), "0.0")])
    for x, m in zip(XP, MS):
        s.line(x, YB, x, YB + 8, INK, 3)
        s.text(x, YB + 40, str(m), 30, GRAY, "middle")
    s.text(150, 106, "FP", 30, GRAY, "start", "bold")
    s.text((X0 + X1) / 2, 500, "每样本细胞数", 30, GRAY, "middle")

    # 图例行（拉丁标注）
    s.line(150, 74, 205, 74, RED, 6, cap="round")
    s.text(216, 84, "细胞级", 30, RED, "start", "bold")
    s.line(440, 74, 495, 74, GREEN, 6, cap="round")
    s.text(506, 84, "聚合检验", 30, GREEN, "start", "bold")

    # pseudobulk 稳态（绿）+ 独立抽样对照（青，空心点）
    s.line(165, py(pb[0]), 715, py(pb[0]), GREEN, 6)
    for x in XP:
        s.circle(x, py(pb[0]), 8, GREEN)
    s.text(245, 392, f"{pb[0]:.3f}", 30, GREEN, "start", "bold")
    s.circle(600, py(control), 10, WHITE, CYAN_DEEP, 4)
    s.line(600, py(control), 638, py(control), CYAN_DEEP, 3, dash="6 6")
    s.text(646, 420, f"{control:.3f}", 30, CYAN_DEEP, "start", "bold")

    # 细胞级伪重复（红，唯一警示区）：平台随 m 抬升并逼近 1
    pts = [(x, py(v)) for x, v in zip(XP, cell)]
    s.polyline(pts, RED, 7)
    for (x, y), v in zip(pts, cell):
        s.circle(x, y, 9, RED)
        s.text(x, y - 22, f"{v:.3f}", 30, RED, "middle", "bold")

    s.caption(["假阳性率随细胞数暴涨，聚合检验紧贴基准。",
               "膨胀源自同管共享方差。"], [INK, INK], 30, top=536)
    s.save("05_pseudoreplication_power_curve.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())
