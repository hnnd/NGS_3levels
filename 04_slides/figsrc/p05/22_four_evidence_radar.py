#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_four_evidence_radar.py — 生成 22_four_evidence_radar.svg
（FIG-P05-22：P41「四类证据：至少两列独立指向同一基因」，cols 左栏）【new-svg】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-22（800×700，中文共 27 字）。
依据：教材 §21.4.6——候选基因收敛靠四类正交证据：变异后果（SnpEff 的
HIGH／MODERATE 破坏编码）、组织表达（组织特异表达与 eQTL 支撑）、同源功能
（抗性基因家族与通路成员）、统计共定位（coloc 的 H4 检验共享因果变异，
用于排除「同一区间、不同因果变异」的巧合）。准则是最少两列独立证据指向同一
基因才立项，禁止「取物理距离最近的基因」。
图内中文严格取方案给定三句（13 + 7 + 7 = 27 字）：四张卡的标题取
「变异／表达／同源／共定位」，余下「四项正交」作总标题。
配色：深蓝＝证据卡外框，绿＝「两项支持」准则；红色只标「同区间非同因果」一处。
无网络；不涉及随机数（纯结构示意，无计算结果）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 22_four_evidence_radar.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["变异表达同源共定位四项正交",   # 13
           "两项支持方立项",              # 7
           "同区间非同因果"]              # 7
TEXT = "".join(PHRASES)
TITLE = "四项正交"
CARDS = [("变异", "SnpEff HIGH", BLUE),
         ("表达", "eQTL tissue", CYAN_DEEP),
         ("同源", "homolog family", PURPLE),
         ("共定位", "coloc H4", GREEN)]


def main():
    s = SVG(800, 700, "Four orthogonal lines of evidence", plan=TEXT)

    s.text(400, 52, TITLE, 32, BLUE, "middle", "bold")

    # ---------- 四张证据卡（田字格）----------
    for i, (head, sub, col) in enumerate(CARDS):
        x = 40 + (i % 2) * 375
        y = 78 + (i // 2) * 190
        s.rect(x, y, 345, 168, WHITE, col, 4, rx=14)
        s.text(x + 26, y + 68, head, 34, col, "start", "bold")
        s.text(x + 26, y + 124, sub, 30, GRAY)

    # ---------- 准则：两项支持方可立项 ----------
    s.rect(40, 470, 720, 96, GREEN_TINT, GREEN, 4, rx=14)
    s.check(84, 518, 22, GREEN, 7)
    s.text(392, 530, PHRASES[1], 32, GREEN, "middle", "bold")

    # ---------- 反例：同区间非同因果（唯一红色警示）----------
    s.rect(40, 586, 720, 84, RED_TINT, RED, 4, rx=14)
    s.cross(84, 628, 18, RED)
    s.text(400, 640, PHRASES[2], 32, RED, "middle", "bold")

    s.save("22_four_evidence_radar.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    assert "".join(h for h, _, _ in CARDS) + TITLE == PHRASES[0]
    raise SystemExit(main())
