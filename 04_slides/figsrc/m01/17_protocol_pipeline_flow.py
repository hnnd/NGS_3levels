#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_protocol_pipeline_flow.py — 生成 17_protocol_pipeline_flow.svg
（FIG-M01-20：测序方案与公共数据获取六步流水线）

方案：reviews/course/M01_FIGP_001.md §4 FIG-M01-20（P47，cols 一栏，800×700）。
依据：教材 §13.4.6 L288–313、§13.6 L375–385；讲义 ⑤。无数字、无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_protocol_pipeline_flow.py
"""
from svghelp import *  # noqa: F401,F403

W, H = 240, 92
TOP = [(40, "① 层级：", "数清样本"), (290, "② 检索：", "取 10 字段"),
       (540, "③ 下载：", "直链优先")]
BOT = [(540, "⑥ 方案：", "六段式"), (290, "⑤ 整理：", "sample sheet"),
       (40, "④ 验收：", "四步闭环")]


def shield(s, cx, cy, r, color):
    pts = [(cx, cy - r), (cx + r * 0.85, cy - r * 0.45),
           (cx + r * 0.7, cy + r * 0.4), (cx, cy + r),
           (cx - r * 0.7, cy + r * 0.4), (cx - r * 0.85, cy - r * 0.45)]
    s.polygon(pts, color)


def main():
    s = SVG(800, 700)

    for x, l1, l2 in TOP:
        s.rect(x, 96, W, H, BLUE, rx=14)
        s.text(x + W / 2, 142, l1, 32, WHITE, "middle", "bold")
        s.text(x + W / 2, 178, l2, 30, WHITE, "middle")
    for x, l1, l2 in BOT:
        if l1.startswith("④"):
            s.rect(x, 300, W, H, BLUE, RED, 7, rx=14)
            shield(s, x + W - 30, 300, 26, RED)
        else:
            s.rect(x, 300, W, H, BLUE, rx=14)
        s.text(x + W / 2, 346, l1, 32, WHITE, "middle", "bold")
        s.text(x + W / 2, 382, l2, 30, WHITE, "middle")

    # 流向箭头（青蓝）：①→②→③→⑥→⑤→④
    s.arrow(280, 142, 290, 142, CYAN, 7)
    s.arrow(530, 142, 540, 142, CYAN, 7)
    s.arrow(660, 188, 660, 300, CYAN, 7)
    s.arrow(540, 346, 530, 346, CYAN, 7)
    s.arrow(290, 346, 280, 346, CYAN, 7)

    # 高亮验收：绿色箭头汇入④（产物校验闭环，不新增文字）
    s.arrow(160, 500, 160, 392, GREEN, 7)

    s.save("17_protocol_pipeline_flow.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
