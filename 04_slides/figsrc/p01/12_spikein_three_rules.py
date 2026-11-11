#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_spikein_three_rules.py — 生成 12_spikein_three_rules.svg
（FIG-P01-13：已知答案三条设计规则）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-13（P37，cols 一栏，800×700）。
依据：教材 §24.4.5 三条设计规则——① 独立性：答案在流程外独立生成，不得由被检
代码产出或按结果反推；② 对偶性：扰动与错误模式成数学对偶（换标签 ⇔ 符号翻转），
同一答案可同时检验方向；③ 阴阳平衡：必配阴性对照，否则「全部报显著」也能拿
满分。图内 20 / 1975 取自 demos 现跑（ch24_pvalue_vs_padj.py：20 个已知差异基因
＋1 975 个空假设基因），是阴阳两侧的样本量，不是评分阈值。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 12_spikein_three_rules.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "已知答案三规则：独立流程外，扰动形成对偶，配阴性对照防全阳作弊。"


def shield(s, cx, cy, w, h, fill, stroke):
    """盾牌轮廓：上平下尖（独立性徽章）。"""
    s.path(f"M {cx - w / 2} {cy - h / 2} L {cx - w / 2} {cy + h / 8} "
           f"Q {cx - w / 2} {cy + h / 2} {cx} {cy + h / 2} "
           f"Q {cx + w / 2} {cy + h / 2} {cx + w / 2} {cy + h / 8} "
           f"L {cx + w / 2} {cy - h / 2} Z", stroke, 4, fill=fill)


def main():
    s = SVG(800, 700, "Three design rules for known answers", plan=TEXT)

    rows = [
        (48, "R1", "standalone", "seed-set · no_result_peeking", CYAN, "#E7F5F8"),
        (182, "R2", "duality", "swap_labels · lfc → -lfc", BLUE, BLUE_TINT),
        (316, "R3", "negative_ctrl", None, GREEN, GREEN_TINT),
    ]
    for y, no, head, detail, edge, tint in rows:
        s.rect(40, y, 720, 118, tint, edge, 4, rx=12)
        shield(s, 98, y + 56, 58, 68, WHITE, edge)
        s.text(98, y + 66, no, 30, edge, "middle", "bold")
        s.text(142, y + 46, head, 32, edge, "start", "bold")
        if detail:
            s.text(142, y + 92, detail, 30, INK)

    # ---- 规则三：阴阳两侧的样本量对比 ----
    y3 = 316
    s.text(404, y3 + 34, "pos", 30, GREEN, "start", "bold")
    s.rect(404, y3 + 48, 52, 18, GREEN, None, 0)
    s.text(430, y3 + 104, "20", 32, GREEN, "middle", "bold")
    s.text(500, y3 + 34, "neg", 30, PURPLE, "start", "bold")
    s.rect(500, y3 + 48, 218, 18, PURPLE, None, 0)
    s.text(609, y3 + 104, "1975", 32, PURPLE, "middle", "bold")

    # 规则三的作弊路径（唯一红）
    s.rect(40, 452, 720, 62, RED_TINT, RED, 3, rx=10)
    s.text(400, 492, "all-significant  =  perfect recall", 30, RED, "middle",
           "bold")

    s.caption(["已知答案三规则：独立流程外，",
               "扰动形成对偶，",
               "配阴性对照防全阳作弊。"], [INK, INK, GREEN], 30,
              top=536, gap=40, pad_top=12)
    s.save("12_spikein_three_rules.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())
