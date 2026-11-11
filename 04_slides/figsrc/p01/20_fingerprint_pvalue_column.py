#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_fingerprint_pvalue_column.py — 生成 20_fingerprint_pvalue_column.svg
（FIG-P01-21：判读指纹一 · 筛选列误用）【data-plot】

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-21（P56，cols 一栏，800×700）。
依据：教材 §24.4.4 与讲义 ⑥6.2 第 1 行——`padj` 换成 `pvalue` 后，差异基因数
从 20 上下跳到 100 上下，多出来的几乎全是假阳性。
图内数字全部取自 demos 现跑（textbook/demos/ch24_pvalue_vs_padj.py --selftest，
2026-11-11，6/6 PASS），见回执核对表：
  padj<0.05 → 21 个；pvalue<0.05 → 114 个；虚增 114/21 = 5.4×。
本脚本不重造数据：直接 import 该 demo 的 bh_adjust，用同一组参数（--m-null
1975、--seed 20261105）复算，与上列数字不一致即失败退出。
配色：绿色正常差异集；红色 1 处标「虚增至 114 个」；深蓝标尺。无网络；
随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 20_fingerprint_pvalue_column.py
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

TEXT = "指纹一：差异基因数从20跳到100，假阳性暴涨，检查是否误用原始值。"
M_NULL, M_DE, SEED = 1975, 20, 20261105
REF = {"padj_n": 21, "p_n": 114, "ratio": 5.4}


def numbers():
    rng = np.random.default_rng(SEED)
    p_null = rng.random(M_NULL)
    p_de = 10.0 ** (-rng.uniform(6, 10, M_DE))
    p = np.concatenate([p_null, p_de])
    padj = bh_adjust(p)
    got = {"padj_n": int((padj < 0.05).sum()),
           "p_n": int((p < 0.05).sum())}
    got["ratio"] = round(got["p_n"] / got["padj_n"], 1)
    for k, v in REF.items():
        if abs(got[k] - v) > 1e-9:
            raise SystemExit(f"图面数字与 demos 现跑不一致：{k} "
                             f"got={got[k]} ref={v}")
    return got


def main():
    got = numbers()
    s = SVG(800, 700, "Fingerprint 1: wrong DE column", plan=TEXT)

    base, unit = 434, 2.3               # 基线 y、每个基因的像素高
    # 左：正确列（21 个，绿）；右：误用列（114 个，红）
    x1, x2, bw = 190, 470, 150
    s.line(90, base, 740, base, BLUE, 4)

    y1 = base - got["padj_n"] * unit
    s.rect(x1, y1, bw, got["padj_n"] * unit, GREEN, WHITE, 3, rx=4)
    s.text(x1 + bw / 2, y1 - 18, str(got["padj_n"]), 34, GREEN, "middle", "bold")

    y2 = base - got["p_n"] * unit
    s.rect(x2, y2, bw, got["p_n"] * unit, RED, WHITE, 3, rx=4)
    s.text(x2 + bw / 2, y2 - 18, str(got["p_n"]), 34, RED, "middle", "bold")

    # 虚增倍数：从正确高度拉一条虚线到误用柱
    s.line(x1 + bw + 14, y1, x2 - 14, y1, GRAY, 3, dash="8 7")
    s.text(405, y1 - 14, f"{got['ratio']} X", 30, RED, "middle", "bold")

    s.text(x1 + bw / 2, base + 40, "padj < 0.05", 30, INK, "middle", "bold")
    s.text(x2 + bw / 2, base + 40, "pvalue < 0.05", 30, INK, "middle", "bold")

    # 纵轴口径：柱高 = 差异基因数（无刻度）
    s.text(90, 84, "DE genes", 30, GRAY)
    s.arrow(78, base - 6, 78, 148, GRAY, 3, 11)

    # 排查入口（图内只写列名，不写命令行）
    s.rect(40, 486, 720, 62, BLUE_TINT, BLUE, 3, rx=10)
    s.text(400, 526, "grep -n pvalue", 30, BLUE, "middle", "bold")

    s.caption(["指纹一：差异基因数从20跳到100，假阳性暴涨，",
               "检查是否误用原始值。"], [INK, INK], 30,
              top=558, gap=44, pad_top=12)
    s.save("20_fingerprint_pvalue_column.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 25, TEXT
    raise SystemExit(main())
