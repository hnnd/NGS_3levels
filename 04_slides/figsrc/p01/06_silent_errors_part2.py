#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_silent_errors_part2.py — 生成 06_silent_errors_part2.svg
（FIG-P01-07：后两类静默语义错误）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-07（P24，cols 一栏，800×700）。
依据：教材 §24.4.2 表 24-1 序号 4–5：
  ④ 阈值凭空搬运——`percent.mt < 5` 这类从人类 PBMC 教程搬来的常数套到植物、
     真菌或昆虫样本上，「阈值是常数，任何常数都能跑通」；
  ⑤ 配对关系丢失——`design = ~ condition` 丢掉真实存在的 `batch`，批次效应被
     处理组效应吸收。
本图不写「剔除多少细胞」「方差占比多少」这类无入口的数字，也不画任何真实分布：
横轴刻度 0 / 5 / 20 只作位置标尺（percent.mt 的取值范围），不据此下定量结论。
图内中文只有底部方案整句（29 汉字），卡片标题与判据用代码术语。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_silent_errors_part2.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "静默错误二：设计式漏掉批次混杂，跨物种生搬单细胞阈值。常数皆跑通。"
AX0, AX1, AXY = 110, 720, 214
AXMAX = 20.0
PER_MT = 5.0                       # 教程阈值 percent.mt = 5（教材 §24.4.2 表 24-1）


def xpos(v):
    return AX0 + (AX1 - AX0) * v / AXMAX


def main():
    s = SVG(800, 700, "Silent semantic errors, part 2", plan=TEXT)

    # ---- ④ 阈值搬运 ----
    s.rect(40, 30, 720, 252, ORANGE_TINT, ORANGE, 4, rx=12)
    s.badge(64, 72, "4", ORANGE, WHITE, 30, "start")
    s.text(122, 84, "percent.mt < 5", 32, ORANGE, "start", "bold")


    s.line(AX0, AXY, AX1, AXY, GRAY, 3)
    x5 = xpos(PER_MT)
    # 阈值左侧整段被丢弃（示意区间，不标数量）；橙色＝阈值误用，非红色警示
    s.rect(AX0, AXY - 66, x5 - AX0, 66, ORANGE_TINT, ORANGE, 3, dash="8 6")
    s.cross((AX0 + x5) / 2, AXY - 34, 15, ORANGE, 8)
    # 阈值右侧：作物取值域（示意曲线，非实测分布）
    s.polyline([(x5, AXY), (xpos(8), AXY - 34), (xpos(11), AXY - 54),
                (xpos(14), AXY - 48), (xpos(17), AXY - 26), (AX1, AXY)],
               ORANGE, 5)
    s.line(x5, AXY - 84, x5, AXY + 10, ORANGE, 4, dash="9 6")
    for v, lbl in ((0.0, "0"), (5.0, "5"), (20.0, "20")):
        s.text(xpos(v), AXY + 42, lbl, 30, GRAY, "middle")

    # ---- ⑤ 配对丢失 ----
    s.rect(40, 296, 720, 206, BLUE_TINT, BLUE, 4, rx=12)
    s.badge(64, 338, "5", BLUE, WHITE, 30, "start")
    s.text(122, 350, "design = ~ condition", 32, BLUE, "start", "bold")

    s.rect(80, 400, 210, 70, WHITE, BLUE, 3, rx=10)
    s.text(185, 444, "condition", 30, INK, "middle")
    s.rect(324, 400, 170, 70, WHITE, GRAY, 3, rx=10, dash="9 7")
    s.text(409, 444, "batch", 30, GRAY, "middle")
    s.cross(530, 435, 16, GRAY, 7)
    s.arrow(556, 435, 604, 435, RED, 5, 14)
    s.text(616, 445, "absorbed", 30, RED, "start", "bold")

    s.caption(["静默错误二：设计式漏掉批次混杂，",
               "跨物种生搬单细胞阈值。常数皆跑通。"], [INK, INK], 30,
              top=536, gap=44, pad_top=16)
    s.save("06_silent_errors_part2.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
