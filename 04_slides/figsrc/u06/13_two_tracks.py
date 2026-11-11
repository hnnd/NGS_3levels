#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_two_tracks.py — 生成 13_two_tracks.svg（FIG-U06-13：两条评估轨道）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-13（P35，cols 一栏，800×700）。
数据：登录号 GCA_987216485（已登记 ../06_data/accessions.tsv）；其余定性。
校内无参考：QUAST 错接栏为空，报告必须写"未检查错接"（教材 §8.4.8 L280、
§8.5.2 L385）；主线有标准答案：QUAST -r 看错接数（§8.6 L425/L449）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 13_two_tracks.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 左泳道：校内——无参考
    s.rect(40, 80, 720, 220, BLUE_TINT, rx=18)
    s.text(70, 142, "校内：无参考", 34, BLUE, "start", "bold")
    s.rect(70, 172, 340, 78, WHITE, PANEL, 3, rx=12)
    s.text(240, 222, "只能无参考 QUAST", 32, INK, "middle", "bold")
    s.rect(430, 172, 300, 78, WHITE, RED, 5, rx=12)
    s.text(580, 222, "写\"未检查错接\"", 32, RED, "middle", "bold")

    # 右泳道：主线——有标准答案
    s.rect(40, 340, 720, 220, GREEN_TINT, rx=18)
    s.text(70, 402, "主线：有标准答案", 34, GREEN, "start", "bold")
    s.rect(70, 432, 340, 78, WHITE, GREEN, 4, rx=12)
    s.text(240, 482, "GCA_987216485", 32, INK, "middle", "bold")
    s.rect(430, 432, 300, 78, WHITE, GREEN, 4, rx=12)
    s.text(580, 482, "QUAST -r 看错接数", 32, INK, "middle", "bold")

    s.save("13_two_tracks.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
