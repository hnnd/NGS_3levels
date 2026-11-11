#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_two_thresholds.py — 生成 01_two_thresholds.svg（FIG-P01-01：两道门槛）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-01（P10，cols 一栏，800×700）。
依据：教材 §24.1 L8–16（产出代码的门槛降到接近零，判断对错的门槛原样留在
原处）、讲义 ③ 前言。纯示意，无数据、无网络、无随机数。
图内中文 = 方案指定整句逐字一致（27 汉字）；面板名、刻度只用字母与数字。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_two_thresholds.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "代码生成趋零，判断对错留在原处。语言换代码极易，语义验证断层。"
BASE = 470          # 门槛基线
TOP = 170           # 门槛满高


def main():
    s = SVG(800, 700, "Two thresholds: generate vs judge", plan=TEXT)
    s.line(56, BASE, 744, BASE, BLUE, 4)                    # 基准线（深蓝）

    # 左：A 门槛——原高墙的轮廓（虚线）与塌缩后的现状（绿平地）
    s.text(64, 128, "A  GENERATE", 32, BLUE, "start", "bold")
    s.rect(120, TOP, 150, BASE - TOP, "none", GRAY, 3, rx=4, dash="12 9")
    s.arrow(195, TOP + 26, 195, BASE - 26, GREEN, 7, 18)
    s.rect(110, BASE - 12, 170, 12, GREEN)
    s.text(300, BASE - 18, "0", 34, GREEN, "start", "bold")

    # 右：B 门槛——高墙原样不动（红＝唯一警示区：语义门槛未被挪动）
    s.text(500, 128, "B  JUDGE", 32, BLUE, "start", "bold")
    s.rect(520, TOP, 150, BASE - TOP, RED_TINT, RED, 5)
    s.text(595, BASE - 60, "100", 40, RED, "middle", "bold")

    # 两门槛的高度落差：双向标尺
    s.arrow(390, TOP + 40, 390, BASE - 20, GRAY, 5, 13)
    s.arrow(390, BASE - 20, 390, TOP + 40, GRAY, 5, 13)
    s.text(390, 150, "gap", 30, GRAY, "middle")

    s.caption(["代码生成趋零，判断对错留在原处。",
               "语言换代码极易，语义验证断层。"], [INK, INK], 30,
              top=512, gap=46)
    s.save("01_two_thresholds.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())
