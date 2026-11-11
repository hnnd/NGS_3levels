#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_project_bootstrap_layout.py — FIG-M08-21 个人工作区隔离与四样本数据生成（P44，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-21（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.1 与 §23.4.1、讲义 m08 ⑤ 步骤 0（课程材料只读，复制到个人工作区；
路径用纯 ASCII；合成数据由 make_demo_data.py 生成，不具生物学意义）。
图内汉字 = 方案原句逐字，共 26 字（复制到个人目录 / 纯路径规范 /
生成四样本数据 / 严禁改动源文件）；目录名与脚本名用 ASCII。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 21_project_bootstrap_layout.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

# (卡片文案, 中文语义, 底色, 主色, y)
STEPS = [("course/  (read-only)", "复制到个人目录", CYAN_TINT, CYAN, 96),
         ("~/work/m08/", "纯路径规范", CYAN_TINT, CYAN, 244),
         ("4 samples", "生成四样本数据", GREEN_TINT, GREEN, 392)]
X, W, H = 60, 680, 84


def main():
    s = SVG()

    for i, (label, zh, fill, ink, y) in enumerate(STEPS):
        s.text(96, y - 16, zh, 30, BLUE, "start", "bold")
        s.rect(X, y, W, H, fill, ink, 4, rx=14)
        s.text(X + W / 2, y + 54, label, 30, ink, "middle", "bold")
        if i:
            s.arrow(X + W - 52, STEPS[i - 1][4] + H + 2, X + W - 52, y - 4,
                    CYAN, 5, 14)

    # 唯一警示：严禁改动源文件
    s.rect(120, 546, 560, 116, RED_TINT, RED, 5, rx=16)
    s.text(400, 600, "严禁改动源文件", 36, RED, "middle", "bold")
    s.text(400, 640, "cp -r course/ ~/work/m08/", 30, RED, "middle")

    return s.save("21_project_bootstrap_layout.svg")


if __name__ == "__main__":
    raise SystemExit(main())
