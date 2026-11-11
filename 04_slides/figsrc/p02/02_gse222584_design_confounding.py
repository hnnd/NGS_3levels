#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_gse222584_design_confounding.py — 生成 02_gse222584_design_confounding.svg
（FIG-P02-02：主线数据 GSE222584 的 3×3 设计与批次—时点共线）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-02（Slide 11，cols 一栏，800×700）。
依据：教材 §17.1 L12–14、§17.6 L343–348；`06_data/phd/README.md` p02 节
（9 样本 = 3 处理 × 3 时点，文件名 0828 / 0904 / 0911 = 三次采样，与 dpi 完全共线）。
纯示意，无随机数、无网络；处理名与日期为登在册数据集的事实字段。
图内汉字 = 方案指定整句逐字一致（29 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 02_gse222584_design_confounding.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "三处理乘三时点单重复。采样日期与周期完全共线，时间效应不可辨识。"
# 图内标签的中文译文（D135）；Mock/RRSV/RGSV 为处理名、dpi 为字段名，保留英文。
EXTRA = "采样日期即时间"
ROWS = ("Mock", "RRSV", "RGSV")
COLS = ("7 dpi", "14 dpi", "21 dpi")
DATES = ("0828", "0904", "0911")


def main():
    s = SVG(800, 700, "GSE222584 design: time confounded with batch", plan=TEXT,
            extra=EXTRA)
    x0, cw = 190, 156
    y0, rh = 124, 84

    s.text(60, 100, "n=1", 30, BLUE, "start", "bold")
    for j, c in enumerate(COLS):
        s.text(x0 + cw * j + cw / 2, 100, c, 32, BLUE, "middle", "bold")

    for i, r in enumerate(ROWS):
        cy = y0 + rh * i + rh / 2
        s.text(176, cy + 11, r, 32, INK, "end")
        for j in range(3):
            x = x0 + cw * j
            s.rect(x + 8, y0 + rh * i + 6, cw - 16, rh - 12, WHITE, BLUE, 3,
                   rx=8)
            # 每格只有一个样本点：单重复
            s.circle(x + cw / 2, cy, 12, CYAN)

    # 采样日期：三次采样各一天，落在同一列
    for j, d in enumerate(DATES):
        s.text(x0 + cw * j + cw / 2, 440, d, 32, ORANGE, "middle", "bold")

    # 红色（1 处）：日期与 dpi 一一对应 ⇒ 批次与时间完全共线
    s.line(x0 + 10, 468, x0 + 3 * cw - 10, 468, RED, 5)
    s.polygon([(x0 + 10, 468), (x0 + 26, 461), (x0 + 26, 475)], RED)
    s.polygon([(x0 + 3 * cw - 26, 461), (x0 + 3 * cw - 10, 468),
               (x0 + 3 * cw - 26, 475)], RED)
    s.text((x0 + 3 * cw) / 2, 508, "采样日期即时间", 32, RED, "middle", "bold")

    s.caption(["三处理乘三时点单重复。",
               "采样日期与周期完全共线，时间效应不可辨识。"], [INK, INK], 30,
              top=524)
    s.save("02_gse222584_design_confounding.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
