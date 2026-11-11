#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_dangerous_fixes_silencing.py — 生成 15_dangerous_fixes_silencing.svg
（FIG-P01-16：三大危险修复形态剖析）

方案：reviews/course/P01_FIGP_001.md §4 FIG-P01-16（P42，cols 一栏，800×700）。
依据：教材 §24.4.6 与 §24.5.3——三种「只让报错消失」的修复各自抹掉一层证据：
  ① round()：消除 `not integers` 报错，但把 TPM 这类已归一化的量当作原始 counts
     再算一次 size factor，等于二次归一化（demos 里 2.38× 被压成 1.03×）；
  ② na.omit()/na.rm=TRUE：消除缺失值报错，但缺失往往正是上游 ID 匹配失败的
     唯一痕迹，删掉等于销毁证据；
  ③ 删 batch 变量：消除 `not full rank` 报错，但把批次效应永久吸收进处理组效应。
图内不放数字（第 ① 条的 2.38× / 1.03× 已在 09、22 两张 data-plot 图给出来源）。
红色恰好 2 处：右侧统一红叉（三张卡片共用）＋底部红条。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 15_dangerous_fixes_silencing.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "危险修复三形态：取整抹单位，删缺失毁线索，删协变量藏混杂。关错非修。"
CARDS = [
    ("1", "round()", "non-integer_error_gone", "TPM → 2nd normalization",
     BLUE, BLUE_TINT),
    ("2", "na.omit()", "NA_error_gone", "ID-match_evidence_lost",
     ORANGE, ORANGE_TINT),
    ("3", "drop_batch", "not_full_rank_gone", "confounding_hidden_in_effect",
     PURPLE, PURPLE_TINT),
]


def main():
    s = SVG(800, 700, "Dangerous fixes that only silence errors", plan=TEXT)

    for i, (no, code, gone, cost, edge, tint) in enumerate(CARDS):
        y = 20 + i * 152
        s.rect(40, y, 560, 144, tint, edge, 4, rx=12)
        s.badge(64, y + 40, no, edge, WHITE, 30, "start")
        s.text(122, y + 50, code, 32, edge, "start", "bold")
        # 明细行下移 6 个单位：原 y+90 的字框顶（y+66）与编号徽章底边（y+70）
        # 只差 4 px，目检已呈现「文字顶到徽章下沿」的拥挤感
        s.text(66, y + 96, gone, 30, INK)
        s.text(66, y + 128, cost, 30, GRAY)

    # 红叉 1：三张卡片共用的统一否定标志
    s.line(660, 205, 736, 281, RED, 12, cap="round")
    s.line(660, 281, 736, 205, RED, 12, cap="round")
    s.line(698, 292, 698, 376, RED, 4, dash="10 9")

    # 红条 2：修复 ≠ 解决
    s.rect(40, 476, 560, 62, RED_TINT, RED, 4, rx=10)
    s.text(320, 516, "error_gone ≠ problem_fixed", 30, RED, "middle", "bold")

    s.caption(["危险修复三形态：取整抹单位，删缺失毁线索，",
               "删协变量藏混杂。关错非修。"], [INK, INK], 30,
              top=556, gap=44, pad_top=16)
    s.save("15_dangerous_fixes_silencing.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
