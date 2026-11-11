#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""31_report_reactivity_loop.py — FIG-M08-31 可重复报告活性验收闭环（P61，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-31（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.6（报告活性的唯一判据：改配置阈值 → 参数变化触发增量重跑 →
报告注入新矩阵重新渲染 → 报告数字自己变；手工改 HTML 得到的数字不算接入流程）。
布局：四步纵向闭环，右侧回环箭头把第 ④ 步接回第 ① 步；底部红卡为唯一警示。
图内汉字 = 方案原句逐字，共 28 字（改动配置阈值 / 参数变化触发重跑 /
报告数字自动更新 / 手改视为未通）；第 ③ 步渲染卡内不放中文，配置项与文件名用 ASCII。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 31_report_reactivity_loop.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

# 四步卡：(y, 中文或 None, 主色, 底色, 标题, 副标题)
STEPS = [
    (22, "改动配置阈值", CYAN_DEEP, CYAN_TINT,
     "config.yaml", "qualified_quality_phred: 25"),
    (166, "参数变化触发重跑", BLUE, BLUE_TINT,
     "snakemake -n", "reason: Params changed"),
    (310, None, GRAY, WHITE,
     "quarto render report.qmd", "counts_matrix.tsv injected"),
    (454, "报告数字自动更新", GREEN, GREEN_TINT,
     "report.html", "numbers recomputed from matrix"),
]
X, W, H = 36, 604, 124


def main():
    s = SVG()

    for y, zh, color, tint, head, sub in STEPS:
        s.rect(X, y, W, H, tint, color, 4, rx=14)
        s.text(X + 24, y + 38, head, 30, color, "start", "bold")
        s.text(X + 24, y + 76, sub, 30, GRAY, "start")
        if zh:
            s.text(X + 24, y + 112, zh, 30, color, "start", "bold")

    # 步间下行箭头（在两卡缝隙里）
    for y in (22, 166, 310):
        s.arrow(X + 60, y + H + 2, X + 60, y + H + 17, CYAN, 5, 12)

    # 回环：④ 右出 → 沿右侧上行 → 折回 ①（表示闭环，不是单向流水线）
    ry, ty = 454 + H / 2, 22 + H / 2
    s.polyline([(X + W, ry), (X + W + 60, ry), (X + W + 60, ty),
                (X + W + 8, ty)], BLUE, 4, dash="12 8")
    s.arrow(X + W + 22, ty, X + W, ty, BLUE, 5, 14)

    # 唯一警示：手改 HTML 得到的数字不算接入流程
    s.chip(400, 622, "手改视为未通", 32, RED_TINT, RED, RED, padx=16, pady=12)

    return s.save("31_report_reactivity_loop.svg")


if __name__ == "__main__":
    raise SystemExit(main())
