#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_fastq_math.py — 生成 06_fastq_math.svg
（FIG-U01-06：一次能手算的统计——NR % 4 == 2 命中行与三种截断对照）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-06（P22，cols 一栏，800×700）。
数据（与现跑一致，.ref=「设例（手算＋01_seq_stats.sh 本地现跑）」）：
  16 行 → 4 条 40 bp、40÷4,000,000=1e-5 按 %.1f 显示 0.0 X（rc=0）
  14 行 → 4 条 40 bp（第 14 行被当序列行，rc=0）
  13 行 → 3 条 30 bp（rc=0）
  本文件内以同一 awk 判据现算断言后落图（见 selfcheck()）。
依据：教材 §1.4.5 L128/L130；01_seq_stats.sh 判据 NR % 4 == 2（L103）、深度格式 %.1f。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_fastq_math.py
"""
from svghelp import *  # noqa: F401,F403

SEQ = "ACGTACGTAC"
G = 4_000_000
BH, GAP, GGAP, X0, Y0 = 13, 5, 8, 46, 108


def bar_y(i):
    return Y0 + i * (BH + GAP) + (i // 4) * GGAP


def stats(n_lines):
    """01_seq_stats.sh fastq 分支的同一判据（NR % 4 == 2）的手算复现。"""
    n = len([i for i in range(1, n_lines + 1) if i % 4 == 2])
    return n, n * len(SEQ)


def depth_str(total):
    """awk %.1f 语义：一位小数四舍五入。"""
    return f"{total / G:.1f} X"


def selfcheck():
    assert stats(16) == (4, 40) and depth_str(40) == "0.0 X"
    assert stats(14) == (4, 40)
    assert stats(13) == (3, 30)


def main():
    selfcheck()
    s = SVG(800, 700)

    # 左：16 根短横条（每 4 根一组，组内深浅交替；第 2/6/10/14 根绿色高亮）
    BW = 200
    for i in range(16):
        col = GREEN if (i + 1) % 4 == 2 else (BLUE if i % 2 == 0 else BLUE_TINT)
        s.rect(X0, bar_y(i), BW, BH, col, rx=3)
    # 命中行绿色大括号 + 判据标注（两行，避开右侧算式框）
    y_first = bar_y(1) + BH / 2
    y_last = bar_y(13) + BH / 2
    y_mid = (y_first + y_last) / 2
    s.line(258, y_first, 274, y_first, GREEN, 4)
    s.line(258, y_last, 274, y_last, GREEN, 4)
    s.line(274, y_first, 274, y_last, GREEN, 4)
    s.text(290, y_mid - 8, "每四行", 31, GREEN, weight="bold")
    s.text(290, y_mid + 30, "取第二行", 31, GREEN, weight="bold")
    s.text(X0, 448, "NR % 4 == 2", 30, GRAY, family=MONO)

    # 右：算式竖排
    fx = 430
    s.rect(fx - 16, 100, 350, 190, WHITE, PANEL, 3, rx=12)
    s.text(fx, 150, "16 ÷ 4 ＝ 4 条，40 bp", 33, INK, weight="bold")
    s.text(fx, 200, "40 ÷ 4,000,000", 30, GRAY)
    s.text(fx, 250, "→ 显示 0.0 X", 33, BLUE, weight="bold")

    # 下：三张截断对照小卡（角标统一放卡上方，30px 不压框线）
    cards = [
        (36, "16", "4 条 40 bp", GREEN, GREEN_TINT, None),
        (292, "14", "4 条 40 bp", ORANGE, ORANGE_TINT, "第 14 行被当序列行"),
        (548, "13", "3 条 30 bp", RED, RED_TINT, "截断也 rc=0"),
    ]
    for cx, n_in, res, col, tint, tag in cards:
        if tag:
            s.text(cx + 108, 462, tag, 30,
                   RED if col == RED else ORANGE, "middle", "bold")
        s.rect(cx, 478, 216, 130, tint, col, 4, rx=12)
        s.text(cx + 108, 522, n_in, 30, col, "middle", "bold")
        s.text(cx + 108, 570, res, 32, INK, "middle", "bold")

    # 底部红色结论条
    s.rect(36, 634, 728, 52, RED, rx=10)
    s.text(400, 670, "产物自洽才算对", 34, WHITE, "middle", "bold")

    s.save("06_fastq_math.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
