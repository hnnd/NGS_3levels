#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_rule_shell_wiring.py — FIG-M08-08 规则字段向 Shell 命令插值映射（P22，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-08（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.2 字段表（params/threads/log/conda 都要显式引到 shell，
引擎不自动注入）。`-q` 是 fastp 的 `--qualified_quality_phred` 短写，
图内为控制字宽用短写，全称见页面出处行。
图内汉字 = 方案原句逐字，共 27 字（规则字段显式接线 / 参数注入命令 /
独立日志重定向 / 必须显式引用）；其余只有 ASCII 字段名与命令。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 08_rule_shell_wiring.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

FIELDS = [("params: qual=25", 196), ("threads: 8", 268),
          ("log: logs/qc.log", 340), ("conda: qc.yaml", 412)]


def main():
    s = SVG()

    # 左：规则字段卡（深蓝）
    s.rect(24, 96, 276, 372, BLUE_TINT, BLUE, 4, rx=14)
    s.label(162, 148, ["规则字段", "显式接线"], 30, BLUE, "middle", "bold", 1.3)
    for txt, y in FIELDS:
        s.text(162, y + 34, txt, 30, BLUE, "middle")

    # 中：注入连线（青蓝）+ 两行短标签（避开两卡）
    s.label(363, 166, ["参数注入", "命令"], 30, BLUE, "middle", "bold", 1.3)
    for _, y in FIELDS[:3]:
        s.arrow(310, y + 26, 418, y + 26, CYAN, 5, 14)

    # 右：shell 命令卡（橙）
    s.rect(430, 96, 346, 372, WHITE, ORANGE, 4, rx=14)
    s.label(603, 148, ["独立日志", "重定向"], 30, ORANGE_DEEP, "middle",
            "bold", 1.3)
    for txt, y in [("fastp -w {threads}", 224), ("-q {params.qual}", 300),
                   ("> {log} 2>&1", 376)]:
        s.text(603, y, txt, 30, ORANGE_DEEP, "middle")

    # 底：唯一警示
    s.rect(120, 508, 560, 96, RED_TINT, RED, 5, rx=16)
    s.text(400, 570, "必须显式引用", 34, RED, "middle", "bold")

    return s.save("08_rule_shell_wiring.svg")


if __name__ == "__main__":
    raise SystemExit(main())
