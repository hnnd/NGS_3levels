#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""30_logs_vs_benchmarks_division.py — FIG-M08-30 logs/ 与 benchmarks/ 职责分工（P60，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-30（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.5（logs 留工具标准错误原文，是排错唯一依据；benchmarks 记 max_rss / cpu_time / s，
是资源申请依据；--keep-incomplete 防止失败现场被自动清理）。
图内汉字 = 方案原句逐字，共 23 字（日志留存崩溃报错 / 基准画像物理资源 /
保留不完整现场）；路径与字段名用 ASCII。红 1 处标「保留不完整现场」。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 30_logs_vs_benchmarks_division.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402


def main():
    s = SVG()

    # 顶部：同一个作业把证据写到两个目录（两条落线分别指向下方两卡）
    s.rect(56, 16, 688, 72, PANEL, rx=14)
    s.text(400, 62, "1 job -> 2 evidence dirs", 30, INK, "middle", "bold")
    s.line(212, 88, 212, 110, BLUE, 4)
    s.line(588, 88, 588, 110, BLUE, 4)

    # 左卡：logs/ 报错原文（橙色＝排错证据）
    s.rect(40, 116, 344, 320, ORANGE_TINT, ORANGE_DEEP, 4, rx=14)
    s.text(212, 168, "logs/<rule>/", 30, ORANGE_DEEP, "middle", "bold")
    s.text(212, 206, "<sample>.log", 30, ORANGE_DEEP, "middle", "bold")
    s.text(212, 262, "2>&1 > {log}", 30, GRAY, "middle")
    s.text(212, 322, "日志留存崩溃报错", 30, ORANGE_DEEP, "middle", "bold")
    s.text(212, 386, "traceback / stderr", 30, GRAY, "middle")

    # 右卡：benchmarks/ 资源画像（青蓝＝申请依据）
    s.rect(416, 116, 344, 320, CYAN_TINT, CYAN, 4, rx=14)
    s.text(588, 168, "benchmarks/<rule>/", 30, CYAN_DEEP, "middle", "bold")
    s.text(588, 206, "<sample>.tsv", 30, CYAN_DEEP, "middle", "bold")
    s.text(588, 262, "max_rss / cpu_time / s", 30, GRAY, "middle")
    s.text(588, 322, "基准画像物理资源", 30, CYAN_DEEP, "middle", "bold")
    s.text(588, 386, "3200 MB / 7100 / 7200", 30, GRAY, "middle")

    # 唯一警示：失败现场被自动清掉就无从排查
    s.rect(120, 484, 560, 128, RED_TINT, RED, 5, rx=16)
    s.text(400, 538, "保留不完整现场", 32, RED, "middle", "bold")
    s.text(400, 588, "--keep-incomplete", 30, RED, "middle")

    return s.save("30_logs_vs_benchmarks_division.svg")


if __name__ == "__main__":
    raise SystemExit(main())
