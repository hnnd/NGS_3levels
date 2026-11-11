#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_scale_drop.py — 生成 15_scale_drop.svg
（FIG-U02-15：drop——无数据的水平画不画）

方案：reviews/course/U02_FIGP_001.md §4 FIG-U02-15（P40，cols 一栏，viewBox 800×700）。
数据：两个水平 control / trt、数据只落 trt——drop=TRUE 时位置 1；drop=FALSE 时
空位在 1、trt 在 2（教材 §3.4.6 L217 本机核验，ggplot2 4.0.3；本任务已在 ta 复跑一致）。
与 FIG-U02-09 分工：本图讲标度层空位，09 讲因子对象残留（方案问题 Q2）。
红 1 处＝位置变化标记。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 15_scale_drop.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    s.text(190, 60, "drop = TRUE", 32, INK, "middle", "bold")
    s.rect(40, 84, 300, 420, WHITE, BLUE, 4, rx=8)
    s.line(70, 450, 320, 450, INK, 3)
    s.rect(145, 180, 90, 270, GREEN)
    s.text(190, 496, "1", 34, BLUE, "middle", "bold")
    s.text(190, 540, "trt", 30, INK, "middle")

    s.text(610, 60, "drop = FALSE", 32, INK, "middle", "bold")
    s.rect(460, 84, 300, 420, WHITE, BLUE, 4, rx=8)
    s.line(490, 450, 740, 450, INK, 3)
    s.rect(525, 180, 90, 270, "none", GRAY, 4, dash="12 9")
    s.rect(635, 180, 90, 270, GREEN)
    s.text(610, 142, "空位保留", 30, GRAY, "middle", "bold")
    s.text(570, 496, "1", 34, GRAY, "middle", "bold")
    s.text(680, 496, "2", 34, RED, "middle", "bold")
    s.text(570, 540, "control", 30, GRAY, "middle")
    s.text(680, 540, "trt", 30, INK, "middle")
    s.text(680, 590, "位置会变", 30, RED, "middle", "bold")

    s.text(400, 664, "limits 只改这一层", 30, GRAY, "middle")
    s.save("15_scale_drop.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
