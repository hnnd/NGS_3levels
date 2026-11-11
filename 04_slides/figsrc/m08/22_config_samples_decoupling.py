#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_config_samples_decoupling.py — FIG-M08-22 样本清单与配置外置解耦（P45，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-22（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.3（会随数据集、机器与批次变化的项一律写进配置；
流程文件只引用键名，不出现具体路径、样本名、线程数与阈值）。
图内汉字 = 方案原句逐字，共 27 字（样本清单与配置外置 / 核心流程仅引用键名 /
换样本机器不改代码）；文件名与键名用 ASCII。红 1 处标「不改代码」。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 22_config_samples_decoupling.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

# 左上、左下两张外置卡
LT, LB = (40, 26, 320, 152), (40, 206, 320, 152)
RX, RW = 428, 332


def main():
    s = SVG()

    # 左：外置的可变项（青蓝样本清单、橙配置）
    s.rect(*LT, CYAN_TINT, CYAN, 4, rx=14)
    s.text(200, 78, "samples.tsv", 30, CYAN_DEEP, "middle", "bold")
    s.text(200, 130, "sample / R1 / R2", 30, GRAY, "middle")

    s.rect(*LB, ORANGE_TINT, ORANGE_DEEP, 4, rx=14)
    s.text(200, 258, "config.yaml", 30, ORANGE_DEEP, "middle", "bold")
    s.text(200, 310, "threads / thresholds", 30, GRAY, "middle")

    # 右：核心流程只引用键名
    s.rect(RX, 26, RW, 332, WHITE, BLUE, 4, rx=16)
    s.text(RX + RW / 2, 78, "Snakefile", 30, BLUE, "middle", "bold")
    for i, line in enumerate(["config['threads']", "samples = load()",
                              "no literals"]):
        s.text(RX + RW / 2, 150 + i * 56, line, 30, GRAY, "middle")
    s.text(RX + RW / 2, 322, "核心流程仅引用键名", 30, BLUE, "middle", "bold")

    # 注入流：两条外置卡各自接到流程卡左沿
    s.arrow(364, 102, 424, 102, CYAN, 5, 16)
    s.arrow(364, 282, 424, 282, CYAN, 5, 16)

    # 左列语义标签
    s.text(200, 400, "样本清单与配置外置", 30, BLUE, "middle", "bold")

    # 底部唯一警示：换样本机器不改代码
    s.rect(120, 464, 560, 116, RED_TINT, RED, 5, rx=16)
    s.text(400, 518, "换样本机器不改代码", 34, RED, "middle", "bold")
    s.text(400, 562, "config.yaml + samples.tsv", 30, RED, "middle")

    return s.save("22_config_samples_decoupling.svg")


if __name__ == "__main__":
    raise SystemExit(main())
