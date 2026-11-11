#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_data_three_actions.py — 生成 01_data_three_actions.svg
（FIG-U01-01：一份数据，三个动作——接入/提交/复现）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-01（P11，cols 一栏，800×700）。
数据：无量字数字（行为示意）。
依据：教材 §1.4.6（软链接接入）、§1.4.8（提交）、§2.4.7（导出）。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_data_three_actions.py
"""
import html

from svghelp import *  # noqa: F401,F403


def rich_text(s, x, y, pre, post, post_col, size=33):
    """一行内 pre（正文色）+ post（彩色加粗）精确相邻（tspan）。"""
    s.raw(f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
          f'fill="{INK}">{html.escape(pre)}'
          f'<tspan fill="{post_col}" font-weight="bold">'
          f'{html.escape(post)}</tspan></text>')


def main():
    s = SVG(800, 700)

    # 标题
    s.text(400, 62, "一份数据，三个动作", 40, BLUE, "middle", "bold")

    # 左侧公共数据块（青蓝）
    s.rect(50, 300, 180, 130, CYAN, rx=12)
    s.text(140, 355, "公共数据", 34, WHITE, "middle", "bold")
    s.text(140, 400, "/data/lab", 30, WHITE, "middle")

    # 三张步骤卡（竖排，箭头串联）
    cards = [
        (110, "① 接入：ln -s ", "不复制", GREEN),
        (300, "② 提交：qsub ", "排队", BLUE),
        (490, "③ 复现：导出 ", "yml", PURPLE),
    ]
    cx, cw, ch = 330, 420, 120
    for cy, pre, post, col in cards:
        s.rect(cx, cy, cw, ch, WHITE, col, 5, rx=12)
        s.rect(cx, cy, 14, ch, col, rx=6)
        rich_text(s, cx + 44, cy + ch / 2 + 12, pre, post,
                  RED if post == "不复制" else col)

    # 数据块 → ①，①→②，②→③
    s.arrow(230, 365, 322, 175, GRAY, 5)
    s.arrow(cx + cw // 2, 234, cx + cw // 2, 294, GRAY, 5)
    s.arrow(cx + cw // 2, 424, cx + cw // 2, 484, GRAY, 5)

    s.save("01_data_three_actions.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
