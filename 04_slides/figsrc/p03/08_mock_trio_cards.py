#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_mock_trio_cards.py — 生成 08_mock_trio_cards.svg
（FIG-P03-08：第 20 页 cols 一栏「对照完备性三联卡」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-08（P20，cols，800×700）。
依据：教材 §16.4.1.3 L120–127——三件套各管一类问题：每时点平行的未接种 Mock
（剥离昼夜节律、叶龄与取样伤害；缺了内源变化会被整体读成侵染响应）、病原体外
纯培养（提供基准参照；缺了答不了「相对体外被诱导多少」）、接种缓冲液/机械模拟
对照（分不开病原引起与接种操作引起）。
图内中文严格取方案给定 28 字（4 句）。版式＝三行横排（图标 + 缺漏后果 + 空缺
标记），底部一条总括。横排而非三张窄卡：30px 字号下一句 8 字约 240px，窄卡装不下。
红色只留在方案标红的两句（缺对照误判节律、缺体外难定诱导），其余用中性灰与深蓝，
守住「红色是唯一警示色、每图 ≤2 处」的配色纪律。
配色：深蓝/浅橙/青蓝代表三类对照实体。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 08_mock_trio_cards.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["缺对照误判节律", "缺体外难定诱导", "缺缓冲液混淆操作", "缺一则丢一问"]
TEXT = "".join(PHRASES)
# (中文句, 主色, 淡色, 文字色)：方案只把前两句标红
ROWS = [(PHRASES[0], BLUE, BLUE_TINT, RED),
        (PHRASES[1], ORANGE, ORANGE_TINT, RED),
        (PHRASES[2], CYAN, CYAN_TINT, INK)]


def flask(s, cx, cy, color, r=1.0):
    s.path(f"M {cx - 16 * r} {cy - 26 * r} L {cx + 16 * r} {cy - 26 * r} "
           f"L {cx + 16 * r} {cy - 6 * r} L {cx + 30 * r} {cy + 22 * r} "
           f"Q {cx + 33 * r} {cy + 28 * r} {cx + 22 * r} {cy + 28 * r} "
           f"L {cx - 22 * r} {cy + 28 * r} "
           f"Q {cx - 33 * r} {cy + 28 * r} {cx - 30 * r} {cy + 22 * r} "
           f"L {cx - 16 * r} {cy - 6 * r} Z", color, 4, fill=WHITE)


def icons(s, kind, cx, cy, color):
    if kind == 0:                                    # 未接种叶片
        s.path(f"M {cx - 30} {cy + 16} Q {cx - 10} {cy - 30} {cx + 30} {cy - 20} "
               f"Q {cx + 20} {cy + 24} {cx - 30} {cy + 16} Z", color, 4,
               fill=WHITE)
    elif kind == 1:                                  # 体外培养瓶
        flask(s, cx, cy, color, 1.0)
    else:                                            # 缓冲液滴
        s.path(f"M {cx} {cy - 26} Q {cx + 26} {cy + 6} {cx} {cy + 28} "
               f"Q {cx - 26} {cy + 6} {cx} {cy - 26} Z", color, 4,
               fill=WHITE)


def main():
    s = SVG(800, 700, "Three negative controls, three kinds of questions",
            plan=TEXT)

    # ---------- 三行横排：图标 + 缺漏后果 + 空缺标记 ----------
    for i, (text, main, tint, tc) in enumerate(ROWS):
        y = 62 + i * 132
        s.panel(40, y, 720, 108, tint, main, 4)
        s.rect(40, y, 12, 108, main)
        s.circle(126, y + 54, 40, WHITE, main, 4)
        icons(s, i, 126, y + 54, main)
        s.circle(222, y + 40, 17, WHITE, main, 4)
        s.text(222, y + 49, str(i + 1), 30, main, "middle", "bold")
        s.text(262, y + 68, text, 30, tc, "start", "bold")
        s.cross(688, y + 54, 22, GRAY, 7)

    # ---------- 底部总括条 ----------
    s.band(96, 520, 608, 84, PHRASES[3], BLUE, WHITE, 32)
    s.save("08_mock_trio_cards.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())
