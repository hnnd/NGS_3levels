#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09_permission_bits.py — 生成 09_permission_bits.svg
（FIG-U01-09：权限三位一组——-rw-r--r-- 十格与 755 换算）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-09（P26，cols 一栏，800×700）。
数据：755→7/5/5 算术（教材 §1.4.7 L163）。
依据：教材 §1.4.7 L163（八进制换算）、L176（444 也能删：看父目录的 w 与 x）；deck P26 表。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 09_permission_bits.py
"""
from svghelp import *  # noqa: F401,F403

BITS = "-rw-r--r--"
CELL_FILL = {0: PANEL, 1: BLUE, 2: BLUE, 3: BLUE, 4: CYAN_DEEP, 5: CYAN_DEEP,
             6: CYAN_DEEP, 7: ORANGE, 8: ORANGE, 9: ORANGE}


def mono_row(s, x_mid, y, tokens, size):
    """按等宽/全角估算宽度把 [(ch,color)] token 行居中画出。

    全角字符（如 ＝）用 sans（MONO 栈无 CJK 字形会豆腐块），拉丁用 MONO。
    """
    adv = size * 0.62
    full = size
    total = sum(full if ord(c) > 0x2000 else adv for c, _ in tokens)
    cur = x_mid - total / 2
    for c, col in tokens:
        wide = ord(c) > 0x2000
        w = full if wide else adv
        s.text(cur + w / 2, y, c, size, col, "middle", "bold",
               family=None if wide else MONO)
        cur += w


def main():
    s = SVG(800, 700)

    # 标题
    s.text(400, 56, "三位一组：属主·属组·其他", 36, BLUE, "middle", "bold")

    # 顶部十格权限条：类型位灰；三组三色
    x0, y0, cw, chh = 110, 96, 58, 84
    for i, ch in enumerate(BITS):
        tcol = INK if (i == 0 or i >= 7) else WHITE
        s.rect(x0 + i * cw, y0, cw - 6, chh, CELL_FILL[i], rx=8)
        s.text(x0 + i * cw + (cw - 6) / 2, y0 + 56, ch, 40, tcol, "middle",
               "bold", family=MONO)

    # 中部换算条：755＝4+2+1（三位数字按组着色）
    mono_row(s, 400, 250,
             [("7", BLUE), ("5", CYAN_DEEP), ("5", ORANGE),
              (" ", INK), ("＝", INK), (" ", INK),
              ("4", BLUE), ("+", GRAY), ("2", BLUE), ("+", GRAY), ("1", BLUE)],
             46)
    mono_row(s, 400, 304,
             [("r", INK), ("＝", GRAY), ("4", INK), (" ", INK),
              ("w", INK), ("＝", GRAY), ("2", INK), (" ", INK),
              ("x", INK), ("＝", GRAY), ("1", INK)], 30)

    # 下部两行三格对照：对文件 / 对目录
    rows = [
        (340, "文件", [("r", "读"), ("w", "写"), ("x", "跑")]),
        (470, "目录", [("r", "列"), ("w", "增"), ("x", "进")]),
    ]
    for ry, rname, cells in rows:
        s.text(170, ry + 44, rname, 32, GRAY, "middle", "bold")
        for ci, (bit, mean) in enumerate(cells):
            cx = 250 + ci * 150
            s.rect(cx, ry, 130, 64, WHITE, BLUE, 3, rx=10)
            s.text(cx + 40, ry + 44, bit, 32, BLUE, "middle", "bold",
                   family=MONO)
            s.text(cx + 88, ry + 44, mean, 30, INK, "middle")

    # 底部红色横幅（反直觉点）
    s.rect(150, 606, 500, 66, RED_TINT, RED, 4, rx=12)
    s.text(400, 650, "删文件看父目录", 36, RED, "middle", "bold")

    s.save("09_permission_bits.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
