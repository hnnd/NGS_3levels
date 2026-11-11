#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_library_compatibility_tree.py — 生成 07_library_compatibility_tree.svg
（FIG-P03-07：第 19 页 cols 一栏「建库兼容性决策树」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-07（P19，cols，800×700）。
依据：教材 §16.4.1.2 L108–117——真核宿主 + 真核病原时两侧 mRNA 都有 poly(A) 尾，
Oligo(dT) 富集能同时保留；真核宿主 + 细菌病原时磁珠洗脱把无 poly(A) 的细菌转录本
几乎全丢，病原矩阵近全零且流程不报错；这类体系只有一条物理通路：双物种 rRNA 同步
去除 + 链特异性建库。
图内中文严格取方案给定 29 字（4 句）；分支卡上只写方法名 `poly(A)`，两个物种的差别
由图元自解释：左卡两条转录本都带橙色 poly(A) 尾（富集后都保留，绿勾），右卡细菌
转录本没有尾，被磁珠滤掉（红叉）。
配色：红色标「富集丢无尾细菌」与「病原矩阵近全零」这同一条危险链的两端，绿色标
唯一正确通路。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_library_compatibility_tree.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["富集丢无尾细菌", "病原矩阵全近零", "双物种去除核糖体", "链特异性不可缺"]
TEXT = "".join(PHRASES)


def transcript(s, x, y, color, tail=True, w=104):
    """一条转录本：杆 + 可选 poly(A) 尾（橙色短竖）。tail=False 即细菌转录本。"""
    s.rect(x, y, w, 20, color, None, 0, rx=6)
    if tail:
        for i in range(4):
            s.rect(x + w + 6 + i * 9, y + 2, 6, 16, ORANGE)


def main():
    s = SVG(800, 700, "Library compatibility decision tree", plan=TEXT)

    # ---------- 根：一管组织里的两套转录本 ----------
    s.panel(300, 36, 200, 92, WHITE, BLUE, 4)
    transcript(s, 316, 56, BLUE, True, 84)
    transcript(s, 316, 92, ORANGE, True, 84)

    # ---------- 两条分支 ----------
    s.path("M 356 128 L 216 196", GRAY, 4)
    s.path("M 452 128 L 584 196", RED, 4)

    # 左卡：两侧都有 poly(A) 尾，富集后都在
    s.panel(56, 200, 300, 130, CYAN_TINT, CYAN, 4)
    s.text(206, 246, "poly(A)", 30, CYAN, "middle", "bold")
    transcript(s, 92, 272, BLUE, True, 84)
    transcript(s, 92, 300, ORANGE, True, 84)
    s.check(316, 300, 18, GREEN, 6)

    # 右卡：细菌转录本无尾，被磁珠洗掉
    s.panel(444, 200, 300, 130, RED_TINT, RED, 4)
    s.text(594, 246, "poly(A)", 30, RED, "middle", "bold")
    transcript(s, 480, 272, BLUE, True, 84)          # 宿主转录本照常有尾
    s.circle(584, 310, 9, ORANGE, ORANGE, 3, dash="4 4")   # 病原：尾被洗掉（虚线圈）
    s.rect(480, 300, 84, 20, "none", ORANGE, 3, rx=6, dash="7 6")
    s.cross(584, 310, 14, RED, 5)
    s.text(594, 372, PHRASES[0], 30, RED, "middle", "bold")

    # ---------- 后果：病原矩阵近全零（同一条危险链）----------
    s.panel(444, 396, 300, 78, WHITE, RED, 3, rx=12)
    for i in range(8):
        s.rect(480 + i * 32, 452, 20, 6, RED)
    s.text(594, 508, PHRASES[1], 30, RED, "middle", "bold")

    # ---------- 唯一正确通路（绿色）----------
    s.rect(56, 528, 360, 142, GREEN_TINT, GREEN, 4, rx=16)
    s.text(236, 582, PHRASES[2], 30, GREEN, "middle", "bold")
    s.text(236, 634, PHRASES[3], 30, GREEN, "middle", "bold")
    s.arrow(424, 598, 466, 598, GREEN, 6, 16)
    s.panel(478, 528, 266, 142, WHITE, GREEN, 4)
    s.text(611, 582, "rRNA", 32, GREEN, "middle", "bold")
    s.rect(540, 606, 142, 22, GREEN_TINT, GREEN, 3, rx=6)   # 双端引物示意
    s.polygon([(682, 617), (698, 609), (698, 625)], GREEN)
    s.polygon([(540, 617), (524, 609), (524, 625)], GREEN)
    s.save("07_library_compatibility_tree.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
