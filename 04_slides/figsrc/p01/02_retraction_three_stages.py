#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_retraction_three_stages.py — 生成 02_retraction_three_stages.svg
（FIG-P01-03：撤稿案例官方三段复盘）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-03（P14，cols 一栏，800×700）。
依据：教材 §24.6（2024-02-13 见刊，作者已声明 AI 作图 → 02-15 读者逐图指认解剖
错误、期刊发关注声明（约 48 小时）→ 02-16 正式撤稿（约 72 小时）），Crossref
记录与 Frontiers 官方页亲核。不得简化成「48 小时即被撤稿」。
图内中文只有底部方案整句（25 汉字）；三段事件用英文短标签，避免同一句在图面
重复两遍把汉字数顶到上限。**图内不写出处编号（DOI 等）**，出处只进图注与讲义
（COURSE_SYNC §7 / D134：图面不放能被当成出处标签的号码）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 02_retraction_three_stages.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "见刊声明AI，读者指认解剖错误，官方撤稿。流程拦不住内容错误。"
STAGES = [
    ("02-13", "published", "ai_figure", CYAN, "#E7F5F8"),
    ("02-15", "flagged", "anatomy_error", ORANGE, ORANGE_TINT),
    ("02-16", "retracted", "formal_notice", RED, RED_TINT),
]


def main():
    s = SVG(800, 700, "Retraction case: three official stages", plan=TEXT)

    # 纵向三段：日期 / 事件 / 该段发生了什么
    for i, (day, head, note, edge, tint) in enumerate(STAGES):
        y = 36 + i * 144
        s.rect(44, y, 420, 136, tint, edge, 5 if i == 2 else 4, rx=12)
        s.rect(44, y, 8, 136, edge)
        s.text(70, y + 46, day, 34, edge, "start", "bold")
        s.text(70, y + 90, head, 32, INK, "start", "bold")
        s.text(70, y + 122, note, 30, GRAY)

    # 右栏上：流程三个环节全部放行（绿 ✓）
    s.rect(496, 44, 260, 152, WHITE, PANEL, 3, rx=12)
    s.text(516, 76, "gates", 30, BLUE, "start", "bold")
    for j, lbl in enumerate(("review", "editor", "format")):
        s.check(530, 104 + j * 30, 9, GREEN, 6)
        s.text(552, 112 + j * 30, lbl, 30, GRAY)

    # 右栏下：真正拦住它的是内容判断（红 ✗，唯一红区）
    s.rect(496, 336, 260, 124, RED_TINT, RED, 4, rx=12)
    s.cross(626, 376, 14, RED, 9)
    s.text(626, 438, "content_check", 30, RED, "middle", "bold")

    # 段间连线（只表先后，不表间距）
    s.line(254, 172, 254, 180, GRAY, 3, dash="6 6")
    s.line(254, 316, 254, 324, GRAY, 3, dash="6 6")

    s.caption(["见刊声明AI，读者指认解剖错误，官方撤稿。",
               "流程拦不住内容错误。"], [INK, INK], 30, top=486, gap=44,
              pad_top=18)
    s.save("02_retraction_three_stages.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 25, TEXT
    raise SystemExit(main())
