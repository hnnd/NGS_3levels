#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_four_names.py — 生成 12_four_names.svg
（FIG-U01-12：四种名字，不要混用——环境名/文件名/包名/命令名）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-12（P31，cols 一栏，800×700）。
数据：annotation→annot 与 checkm-genome/checkm 均为教材实例
（ch02 §2.4.1 L82、L120）；deck P31 的「2 处」数字留在页面文字不进图。
依据：教材 §2.4.1–§2.4.2（四种名字定义）、§2.5.1 L337（环境名只由 name: 决定）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 12_four_names.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 标题
    s.text(400, 56, "四种名字各管各的", 40, BLUE, "middle", "bold")

    # 四张名牌卡 2×2
    cards = [
        (110, 100, "环境名", "ngs_ug_annot", GREEN, GREEN_TINT),
        (440, 100, "文件名", "env_ug_annotation.yml", ORANGE, ORANGE_TINT),
        (110, 330, "包名", "checkm-genome", PURPLE, PURPLE_TINT),
        (440, 330, "命令名", "checkm", CYAN_DEEP, "#D8EEF4"),
    ]
    cw, chh = 260, 160
    for cx, cy, label, value, col, tint in cards:
        s.rect(cx, cy, cw, chh, tint, col, 5, rx=14)
        s.text(cx + cw / 2, cy + 54, label, 34, col, "middle", "bold")
        if value == "env_ug_annotation.yml":  # 21 字符，30px 折两行防溢出
            s.text(cx + cw / 2, cy + 100, "env_ug_", 30, INK, "middle",
                   family=MONO)
            s.text(cx + cw / 2, cy + 136, "annotation.yml", 30, INK, "middle",
                   family=MONO)
        else:
            s.text(cx + cw / 2, cy + 118, value, 30, INK, "middle",
                   family=MONO)

    # 错配虚线 ①：文件名（右上）↛ 环境名（左上）——横向间隙 372-438
    s.line(374, 180, 436, 180, RED, 5, dash="10 8")
    s.polygon([(436, 180), (422, 171), (422, 189)], RED)
    s.line(396, 172, 414, 188, RED, 5, cap="round")
    s.line(414, 172, 396, 188, RED, 5, cap="round")
    s.text(400, 302, "环境名看 name:", 30, INK, "middle", "bold")

    # 错配虚线 ②：包名（左下）↛ 命令名（右下）——横向间隙
    s.line(374, 410, 436, 410, RED, 5, dash="10 8")
    s.polygon([(436, 410), (422, 401), (422, 419)], RED)
    s.line(396, 402, 414, 418, RED, 5, cap="round")
    s.line(414, 402, 396, 418, RED, 5, cap="round")
    s.text(400, 540, "包名≠命令名", 32, INK, "middle", "bold")

    s.save("12_four_names.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
