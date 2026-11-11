#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_phred_ruler.py — 生成 13_phred_ruler.svg（FIG-U03-13：Phred+33 对数标尺）

方案：reviews/course/U03_FIGP_001.md §4 FIG-U03-13（P37，cols 一栏，800×700）【data-plot】。
数据：demos/ch04_phred_q.py --selftest 表 1（纯算术，无随机数），此处调用其
q_to_p / decode_ascii 复算并断言：!33→Q0→P1.0；#35→Q2→P0.631；5→Q20→P0.01；
?→Q30→P0.001；I→Q40→P1e-4；~126→Q93→P5.01e-10。
三重标尺按 −log10(P) 对数排布；红字标「# 判错率 63% 别信」与控制字符区。
无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 13_phred_ruler.py
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch04_phred_q as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403,E402

ROWS = [("!", 33), ("#", 35), ("5", 53), ("?", 63), ("I", 73), ("~", 126)]
# 纵轴按 −log10(P) 单调排布；顶部 P=1.0 与 P=0.631 两档过近，
# 手工拉开档距（示意标尺，非等比刻度），保证每档文字互不重叠
SLOTS = {"!": 175, "#": 245, "5": 310, "?": 370, "I": 430, "~": 585}
Y_BOT = 610


def y_of(_v):
    raise NotImplementedError  # 使用 SLOTS 固定档距


def y_slot(ch):
    return SLOTS[ch]


def main():
    rows = []
    for ch, asc in ROWS:
        q = demo.decode_ascii(ch)
        p = demo.q_to_p(q)
        rows.append((ch, asc, q, p, -math.log10(p)))
    expect = {"!": 1.0, "#": 0.631, "5": 0.01, "?": 0.001, "I": 1e-4,
              "~": 5.01e-10}
    for ch, asc, q, p, v in rows:
        assert abs(p - expect[ch]) / expect[ch] < 2e-3, \
            f"{ch}: P={p} ≠ demos 现跑 {expect[ch]}"
        print(f"check: {ch} ASCII={asc} Q{q} P={p:.3g}（demos 一致）")

    s = SVG(800, 700)
    s.text(400, 46, "字符标尺对数换算", 34, BLUE, "middle", "bold")
    s.text(400, 86, "井号判错率六成别信", 30, GRAY, "middle", "bold")

    x_ascii, x_q, x_p = 200, 430, 650

    # 控制字符区（ASCII 0–31 不可见，红底）
    s.rect(90, 118, 220, 36, RED_TINT, RED, 4, rx=8)
    s.text(200, 144, "0–31 控制字符区", 24, RED, "middle", "bold")

    # 三根标尺主轴
    for x in (x_ascii, x_q, x_p):
        s.line(x, 162, x, Y_BOT + 10, INK, 5)

    for ch, asc, q, p, v in rows:
        y = y_slot(ch)
        s.line(x_ascii, y, x_p, y, PANEL, 3)
        s.text(x_ascii - 34, y + 10, f"{ch} {asc}", 28, INK, "end", "bold")
        s.text(x_q, y + 10, f"Q{q}", 28, INK, "middle", "bold")
        s.text(x_p + 30, y + 10, f"{p:.0e}", 28, INK, "start", "bold")
        if ch == "#":
            s.line(x_ascii - 90, y - 22, x_p + 130, y - 22, RED, 6)
            s.text(400, y - 30, "# 判错率 63% 别信", 30, RED, "middle",
                   "bold")

    # 标尺列头
    s.text(x_ascii, 656, "ASCII", 28, GRAY, "middle", "bold")
    s.text(x_q, 656, "Q 值", 28, GRAY, "middle", "bold")
    s.text(x_p, 656, "P_err", 28, GRAY, "middle", "bold")

    s.save("13_phred_ruler.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
