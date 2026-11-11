#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_two_ledgers_balance.py — 生成 13_two_ledgers_balance.svg
（FIG-P01-14：两笔账并排看与假阳性控制）【data-plot】

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-14（P38，cols 一栏，800×700）。
依据：教材 §24.4.5「两笔账」——召回账（真阳性是否找齐）与假阳性账（假阳性比例
是否管住）必须并排看；只看召回率时「全部报显著」也能得满分。两根柱按
「显著总数 → 其中真阳性（绿，下段）/ 假阳性（上段）」堆叠，两柱同一像素标度，
柱高即显著总数，可直接比高矮。
图内数字全部取自 demos 现跑（textbook/demos/ch24_pvalue_vs_padj.py --selftest，
2026-11-11，6/6 PASS），见回执核对表：
  p<0.05 检出 114 = 94 假 + 20 真（FDP 82%）；padj<0.05 检出 21 = 20 真 + 1 假
  （FDP 5%）。
本脚本不重造数据：直接 import 该 demo 的 bh_adjust，用同一组参数（--m-null
1975、--seed 20261105）复算，与上列数字不一致即失败退出。
配色：绿色真阳性；红色 1 处标「未校正 94 个假阳性（82%）」；紫色容许误差；
深蓝基准线。无网络；随机数只用 demo 的固定种子。
注：右柱只混入 1 个空假设基因，按同一标度只有 2.6 px，故下段紫色块按最小可见
高度绘制并在旁标数值，不改变两柱的标度关系。
用法：PYTHONDONTWRITEBYTECODE=1 python3 13_two_ledgers_balance.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import numpy as np                                    # noqa: E402
from svghelp import *                                 # noqa: E402,F401,F403
from ch24_pvalue_vs_padj import bh_adjust             # noqa: E402

TEXT = "两笔账并排看：未校正假阳性率八成，校正后控制在百分之五。防全显著。"
M_NULL, M_DE, SEED = 1975, 20, 20261105
REF = {"p_tot": 114, "p_fp": 94, "p_tp": 20, "padj_tot": 21,
       "padj_fp": 1, "padj_tp": 20}


def numbers():
    rng = np.random.default_rng(SEED)
    p_null = rng.random(M_NULL)
    p_de = 10.0 ** (-rng.uniform(6, 10, M_DE))
    p = np.concatenate([p_null, p_de])
    padj = bh_adjust(p)
    n_p05 = int((p < 0.05).sum())
    n_null_in_p05 = int((p[:M_NULL] < 0.05).sum())
    n_padj05 = int((padj < 0.05).sum())
    n_null_in_padj05 = int((padj[:M_NULL] < 0.05).sum())
    got = {"p_tot": n_p05, "p_fp": n_null_in_p05, "p_tp": n_p05 - n_null_in_p05,
           "padj_tot": n_padj05, "padj_fp": n_null_in_padj05,
           "padj_tp": n_padj05 - n_null_in_padj05}
    for k, v in REF.items():
        if got[k] != v:
            raise SystemExit(f"图面数字与 demos 现跑不一致：{k} "
                             f"got={got[k]} ref={v}")
    return got


def main():
    got = numbers()
    s = SVG(800, 700, "Two ledgers: recall vs false positives", plan=TEXT)

    base, unit, bw = 452, 2.6, 130        # 基线 y、每基因像素高、柱宽
    x1, x2 = 180, 470
    s.line(80, base, 740, base, BLUE, 4)

    # ---- 左柱：未校正 p < 0.05（114 = 94 假 + 20 真）----
    y_tp = base - got["p_tp"] * unit                       # 真阳性块顶 = 400
    y_fp = y_tp - got["p_fp"] * unit                       # 假阳性块顶 = 156
    s.rect(x1, y_tp, bw, got["p_tp"] * unit, GREEN, WHITE, 3, rx=4)
    s.rect(x1, y_fp, bw, got["p_fp"] * unit, RED, WHITE, 3, rx=4)
    s.text(x1 + bw / 2, y_tp + 34, str(got["p_tp"]), 32, WHITE, "middle", "bold")
    s.text(x1 + bw / 2, y_fp + 60, str(got["p_fp"]), 34, WHITE, "middle", "bold")
    s.text(x1 + bw / 2, y_fp - 20, "FDP 82%", 30, RED, "middle", "bold")

    # ---- 右柱：校正后 padj < 0.05（21 = 20 真 + 1 假）----
    s.rect(x2, y_tp, bw, got["padj_tp"] * unit, GREEN, WHITE, 3, rx=4)
    h_fp = max(got["padj_fp"] * unit, 9)                  # 1 个基因按最小可见高
    s.rect(x2, y_tp - h_fp, bw, h_fp, PURPLE, WHITE, 3, rx=4)
    s.text(x2 + bw / 2, y_tp + 34, str(got["padj_tp"]), 32, WHITE, "middle",
           "bold")
    s.text(x2 + bw + 24, y_tp - h_fp - 6, f"{got['padj_fp']}", 30, PURPLE,
           "start", "bold")
    s.text(x2 + bw + 24, y_tp + 26, "FDP 5%", 30, PURPLE, "start", "bold")

    # 柱下名称与总数
    s.text(x1 + bw / 2, base + 50, "p < 0.05", 30, INK, "middle", "bold")
    s.text(x1 + bw / 2, base + 90, f"n = {got['p_tot']}", 30, GRAY, "middle")
    s.text(x2 + bw / 2, base + 50, "padj < 0.05", 30, INK, "middle", "bold")
    s.text(x2 + bw / 2, base + 90, f"n = {got['padj_tot']}", 30, GRAY, "middle")

    # 纵轴：柱高即显著总数（无刻度，只标方向）
    s.text(96, 238, "count", 30, GRAY)
    s.arrow(84, base - 4, 84, 160, GRAY, 3, 11)

    s.caption(["两笔账并排看：未校正假阳性率八成，",
               "校正后控制在百分之五。防全显著。"], [INK, INK], 30,
              top=568, gap=44, pad_top=16)
    s.save("13_two_ledgers_balance.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
