#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_nlr_domain_criteria.py — 生成 20_nlr_domain_criteria.svg
（FIG-P03-20：第 39 页 cols 一栏「NLR 抗病受体组合判据与结构域真伪鉴别」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-20（P39，cols，800×700）。
依据：教材 §16.4.7 L331–343——NLR 候选的判据是「命中 NB-ARC，且命中 LRR 或 TIR」，
写成 PF00931 ∩ (PF00560 ∪ PF07723 ∪ PF01582)；课程脚本用 `comm -12` 实现交集。
组合判据专为排除两类假阳性：① 单一块 NB-ARC 片段多为假基因化、截断或重排产物，
判它是否完整基因还要看结构域覆盖度与 P-loop / Walker B / GLPL 基序是否齐全；
② LRR 是极普适的蛋白互作支架，细胞壁受体样激酶等免疫无关分子也带 LRR，脱离
NB-ARC 的单 LRR 命中没有特异性。
图内中文严格取方案给定 28 字（4 句）。`PF00931`、`PF00560`、`PF07723`、`PF01582` 为
Pfam 登录号，`NB-ARC`、`LRR`、`TIR` 为结构域名，均属符号不作英文说明。
结构＝上部一条三结构域蛋白条带（NB-ARC 居中深蓝，两侧 LRR/TIR 青蓝）＋下方交集
判条打绿勾；底部两张反例卡各打红叉。
配色：深蓝＝核心结构域，青蓝＝识别天线，绿色＝组合交集通过，红色只标两张反例卡。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 20_nlr_domain_criteria.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["核心结构域必选", "交集识别天线", "单碎片疑假基因", "游离天线无特异性"]
TEXT = "".join(PHRASES)
CORE, ANT = "PF00931", ("PF00560", "PF07723", "PF01582")


def check_ids():
    """方案与教材的组合判据：核心必选，天线三者取并集。"""
    if CORE != "PF00931" or len(ANT) != 3:
        raise SystemExit("判据与教材 §16.4.7 不一致")
    return f"{CORE} ∩ ( {ANT[0]} ∪ {ANT[1]} ∪ {ANT[2]} )"


def main():
    rule = check_ids()
    s = SVG(800, 700, "NLR domain combination criteria", plan=TEXT)

    # ---------- 上部：三结构域蛋白条带 ----------
    s.text(44, 86, PHRASES[0], 30, BLUE, "start", "bold")
    s.rect(60, 110, 180, 62, CYAN_TINT, CYAN, 4, rx=10)     # 左天线 TIR
    s.rect(240, 110, 260, 62, BLUE, BLUE, 4, rx=10)         # 核心 NB-ARC
    s.rect(500, 110, 180, 62, CYAN_TINT, CYAN, 4, rx=10)    # 右天线 LRR
    s.text(150, 152, "TIR", 30, CYAN_DEEP, "middle", "bold")
    s.text(370, 152, "NB-ARC", 30, WHITE, "middle", "bold")
    s.text(590, 152, "LRR", 30, CYAN_DEEP, "middle", "bold")
    # ---------- 判条：交集公式（箭头从核心段下沿直指判条）----------
    s.rect(44, 250, 712, 76, WHITE, BLUE, 3, rx=12)
    s.text(400, 300, rule, 30, BLUE, "middle", "bold")
    s.arrow(370, 178, 370, 244, BLUE, 5, 14)

    # ---------- 交集通过：绿勾 + 天线交集标签 ----------
    s.check(400, 366, 26, GREEN, 9)
    s.text(444, 376, PHRASES[1], 30, GREEN, "start", "bold")

    # ---------- 两张反例卡 ----------
    s.panel(44, 430, 340, 196, WHITE, RED, 4)
    s.rect(66, 462, 150, 52, BLUE_TINT, BLUE, 3, rx=8)       # 孤立核心片段
    s.text(141, 496, "NB-ARC", 30, BLUE, "middle", "bold")
    s.cross(298, 488, 26, RED, 9)
    s.text(64, 594, PHRASES[2], 30, RED, "start", "bold")

    s.panel(416, 430, 340, 196, WHITE, RED, 4)
    s.rect(444, 462, 108, 52, CYAN_TINT, CYAN, 3, rx=8)      # 孤立 LRR
    s.text(498, 496, "LRR", 30, CYAN_DEEP, "middle", "bold")
    s.cross(674, 488, 26, RED, 9)
    s.text(436, 594, PHRASES[3], 30, RED, "start", "bold")
    s.save("20_nlr_domain_criteria.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())
