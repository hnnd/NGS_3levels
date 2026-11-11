#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_directory_output_sentinel.py — FIG-M08-14 目录输出哨兵与两个官方排查出口（P33，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-14（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.3（5.2.0 起目录输出必须 `directory()` 声明，引擎写入时间戳哨兵判新旧；
两个官方出口是 `--rerun-triggers mtime` 与 `--cleanup-metadata`，不要暴删 `.snakemake/`）。
图内汉字 = 方案原句逐字，共 28 字（目录声明时间戳哨兵 / 退回时间戳排查 /
精准清指定元数据 / 严禁暴删）；其余只有 ASCII 参数名、目录名与哨兵文件名。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 14_directory_output_sentinel.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402


def main():
    s = SVG()

    # 左：directory() 机制卡（深蓝外框 + 青蓝哨兵文件）
    s.rect(18, 24, 380, 330, WHITE, BLUE, 4, rx=16)
    s.text(208, 76, "directory()", 32, BLUE, "middle", "bold")
    s.text(208, 130, "目录声明时间戳哨兵", 30, BLUE, "middle", "bold")
    s.rect(34, 158, 348, 92, CYAN_TINT, CYAN, 3, rx=10)
    s.label(208, 204, [".snakemake_", "timestamp"], 30, CYAN_DEEP, "middle",
            leading=1.4)
    s.text(208, 290, "output = directory()", 30, GRAY, "middle")

    # 右上：出口一（退回时间戳）
    s.rect(418, 24, 364, 156, GREEN_TINT, GREEN, 4, rx=16)
    s.text(600, 74, "退回时间戳排查", 30, GREEN, "middle", "bold")
    s.text(600, 126, "--rerun-triggers", 30, INK, "middle")
    s.text(600, 164, "mtime", 30, GRAY, "middle")

    # 右下：出口二（精准清元数据）
    s.rect(418, 198, 364, 156, GREEN_TINT, GREEN, 4, rx=16)
    s.text(600, 248, "精准清指定元数据", 30, GREEN, "middle", "bold")
    s.text(600, 300, "--cleanup-metadata", 30, INK, "middle")
    s.text(600, 338, "targets", 30, GRAY, "middle")

    # 底部：唯一警示（严禁暴删）
    s.rect(140, 404, 520, 118, RED_TINT, RED, 5, rx=16)
    s.text(400, 456, "严禁暴删", 36, RED, "middle", "bold")
    s.text(400, 502, "rm -rf .snakemake/", 30, RED, "middle")

    return s.save("14_directory_output_sentinel.svg")


if __name__ == "__main__":
    raise SystemExit(main())
