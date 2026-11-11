#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_snakemake_triggers_funnel.py — FIG-M08-12 Snakemake ≥7.8 五类重跑触发器（P29，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-12（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.3（7.8 起五类触发器默认全开：时间戳/参数/输入集合/软件环境/代码；
线程等资源不进触发器，除非插进命令；元数据丢失后退化为只比时间戳）。
图内汉字 = 方案原句逐字，共 29 字（五类触发器默认全开 / 时间戳参数输入环境代码 /
资源变更不触发重算）；英文原词只作 ASII 佐证，不重复进中文标签。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 12_snakemake_triggers_funnel.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

NAMES = ["时间戳", "参数", "输入", "环境", "代码"]


def main():
    s = SVG()

    s.text(400, 52, "五类触发器默认全开", 34, BLUE, "middle", "bold")

    # 顶部入口
    s.rect(90, 88, 620, 58, BLUE, rx=12)
    s.text(400, 126, "input missing / mtime newer", 30, WHITE, "middle")

    # 漏斗：五层向中轴收窄，每层右侧绿色勾＝默认开启
    for i, name in enumerate(NAMES):
        y = 164 + i * 62
        lx, rx = 90 + i * 26, 710 - i * 26
        s.arrow(400, y - 12, 400, y - 4, CYAN, 4, 10)
        s.rect(lx, y, rx - lx, 48, CYAN_TINT, CYAN, 3, rx=8)
        s.text(lx + 22, y + 33, name, 30, INK, "start")
        s.text(rx - 24, y + 33, "✓", 30, GREEN, "middle", "bold")

    # 右侧排除注记（橙）：资源变更不进触发器
    s.rect(552, 500, 216, 122, WHITE, ORANGE, 4, rx=14)
    s.text(660, 550, "资源变更", 30, ORANGE_DEEP, "middle", "bold")
    s.text(660, 592, "不触发重算", 30, ORANGE_DEEP, "middle", "bold")

    # 底部：元数据丢失后退化为 mtime（红，ASCII 佐证不增汉字）
    s.rect(74, 490, 446, 132, RED_TINT, RED, 5, rx=16)
    s.text(297, 542, "no .snakemake/", 30, RED, "middle", "bold")
    s.text(297, 592, "-> mtime only", 30, RED, "middle")

    return s.save("12_snakemake_triggers_funnel.svg")


if __name__ == "__main__":
    raise SystemExit(main())
