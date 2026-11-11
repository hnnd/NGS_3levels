#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_fastp_parameter_roles.py — 生成 11_fastp_parameter_roles.svg
（FIG-U04-14：fastp 四核心参数角色联动卡【参数/流程】）

方案：reviews/course/U04_FIGP_001.md §4 FIG-U04-14（P31，cols 一栏，viewBox 800×700）。
中央读段 + 四参数卡：双端接头侦测（青蓝，--detect_adapter_for_pe）、
尾端滑窗修剪（深蓝，--cut_tail）、均值二十切除（橙，--cut_mean_quality 20）、
五十长度兜底（绿，--length_required 50）；5′ 端红叉「不开 cut_front」。
依据：教材 §6.4.4 L132–140；03_code/undergraduate/scripts/04_run_fastqc.sh 参数配置。
图内汉字 26，红色 1 处。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 11_fastp_parameter_roles.py
"""
from svghelp import *


def main():
    s = SVG(800, 700)
    BASES = [GREEN, CYAN, ORANGE, PURPLE]   # A C G T（spec §2 碱基色编码）

    # 中央读段（10 bp 网格）
    for k in range(50):
        s.rect(150 + k * 10, 330, 9, 60, BASES[k % 4])
    s.text(150, 314, "5′", 30, GRAY, "start", "bold")
    s.text(650, 314, "3′", 30, GRAY, "end", "bold")

    # 四参数卡
    def card(x, y, w, color, title, flag, tx=None):
        s.rect(x, y, w, 116, WHITE, stroke=color, sw=6, rx=14)
        s.text(x + w / 2, y + 46, title, 30, color, "middle", "bold")
        s.text(x + w / 2, y + 90, flag, 30, GRAY, "middle")
        return (x + w / 2, y + 116 if y < 330 else y)

    card(220, 70, 360, CYAN_DEEP, "双端接头侦测", "--detect_adapter_for_pe")
    card(560, 230, 220, BLUE, "尾端滑窗修剪", "--cut_tail")
    card(400, 520, 380, ORANGE_DEEP, "均值二十切除", "--cut_mean_quality 20")
    card(25, 520, 330, GREEN_DEEP, "五十长度兜底", "--length_required 50")

    # 联动连线
    s.line(400, 186, 400, 324, CYAN_DEEP, sw=5, dash="10 8")
    s.line(560, 288, 652, 344, BLUE, sw=5, dash="10 8")
    s.line(600, 520, 566, 396, ORANGE_DEEP, sw=5, dash="10 8")
    s.line(190, 520, 196, 396, GREEN_DEEP, sw=5, dash="10 8")

    # 5′ 端红叉（唯一红色处）
    s.cross(106, 360, 30)
    s.text(122, 262, "不开 cut_front", 30, RED, "middle", "bold")

    s.save("11_fastp_parameter_roles.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
