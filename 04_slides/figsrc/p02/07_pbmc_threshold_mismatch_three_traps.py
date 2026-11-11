#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_pbmc_threshold_mismatch_three_traps.py — 生成
07_pbmc_threshold_mismatch_three_traps.svg（FIG-P02-09：照搬 PBMC 质控阈值的三重失效）

方案：reviews/course/P02_FIGP_001.md §4 FIG-P02-09（Slide 24，cols 一栏，800×700）。
依据：教材 §17.4.4 L127–140、§17.5.2 L306–313；`06_data/phd/README.md` p02 节
（植物没有线粒体比例这个通用指标）。纯示意：无数据、无随机数、无网络。
图内汉字 = 方案指定整句逐字一致（30 汉字）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_pbmc_threshold_mismatch_three_traps.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *  # noqa: F401,F403

TEXT = "跨物种前缀失配静默全零，生理本底差异大，解离应激伪造亚群特征基因。"


def shield(s, cx, top, w, h, head, color):
    x0, x1 = cx - w / 2, cx + w / 2
    s.path(f"M {x0} {top} L {x1} {top} L {x1} {top + h - 40} "
           f"L {cx} {top + h} L {x0} {top + h - 40} Z",
           color, 5, fill=WHITE)
    s.text(cx, top + 46, head, 32, color, "middle", "bold")


def main():
    s = SVG(800, 700, "PBMC thresholds transplanted: three traps", plan=TEXT)

    # 陷阱一：人源前缀 ^MT- 在植物矩阵上匹配不到 ⇒ percent.mt 整列 0
    shield(s, 150, 60, 200, 330, "NAME", BLUE)
    s.text(150, 152, "MISMATCH", 30, BLUE, "middle", "bold")
    s.text(150, 224, "percent.mt", 30, INK, "middle")
    s.line(58, 258, 242, 258, BLUE, 4, dash="10 8")
    s.text(150, 314, "= 0", 34, BLUE, "middle", "bold")

    # 陷阱二：保卫细胞/飞翔肌天然富集线粒体 ⇒ 5% 阈值机械卡掉目标细胞
    shield(s, 400, 60, 200, 330, "BASELINE", BLUE)
    for i, (h, col) in enumerate(((44, GREEN), (70, ORANGE), (112, PURPLE))):
        s.rect(318 + i * 56, 272 - h, 42, h, col)
        s.line(312 + i * 56, 272, 366 + i * 56, 272, BLUE, 3)
    s.line(306, 226, 494, 226, ORANGE, 4, dash="10 8")
    s.text(400, 318, "mt high", 30, ORANGE, "middle", "bold")

    # 陷阱三：解离应激基因全组织爆发 ⇒ 被误认作亚群特异 marker
    shield(s, 650, 60, 200, 330, "STRESS", BLUE)
    for i in range(3):
        for j in range(3):
            s.rect(586 + j * 44, 176 + i * 40, 38, 34, ORANGE_TINT, ORANGE, 2,
                   rx=4)
    s.text(650, 318, "HSP70", 30, PURPLE, "middle", "bold")

    # 红色（1 处）：经验参数不可跨物种照搬
    s.rect(60, 418, 680, 50, RED, None, 3, rx=10)
    s.text(400, 453, "DO NOT TRANSPLANT", 32, WHITE, "middle", "bold")

    s.caption(["跨物种前缀失配静默全零，生理本底差异大，",
               "解离应激伪造亚群特征基因。"], [INK, INK], 30, top=500)
    s.save("07_pbmc_threshold_mismatch_three_traps.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
