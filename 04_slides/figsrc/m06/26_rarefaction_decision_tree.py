#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""26_rarefaction_decision_tree.py — FIG-M06-26 抽平决策树卡片

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-26（P44，cols 一栏 800×700，new-svg）。
教材依据：§18.4.9（Observed、Chao1、Faith's PD 直接受深度影响须抽平；Jaccard、Unweighted UniFrac
同样须抽平；Shannon、Simpson、Bray–Curtis 抽平或相对丰度均可并写明口径；差异丰度检验不抽平，
改用为组成性数据设计的方法 ANCOM-BC / ALDEx2）。
图内汉字 = 方案原句逐字，共 23 字（种类数必须抽平 / 指数可选相对丰度 / 差异丰度严禁抽平）；
其余为 ASV counts、Observed、Chao1、Faith's PD、Jaccard、Shannon、Simpson、ANCOM-BC、ALDEx2 等名。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 26_rarefaction_decision_tree.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

s.text(400, 54, "rarefaction", 34, BLUE, "middle", "bold")

# ---------------- 根：ASV 计数表 ----------------
s.chip(400, 128, "ASV counts", 32, BLUE_TINT, BLUE, BLUE, padx=22, pady=12)

# 分叉主干
s.line(400, 152, 400, 184, BLUE, 5)
s.line(216, 184, 584, 184, BLUE, 5)
s.line(216, 184, 216, 212, BLUE, 5)
s.line(584, 184, 584, 212, BLUE, 5)

# ---------------- 左分支：多样性统计 ----------------
s.rect(44, 212, 344, 424, WHITE, CYAN, 4, rx=14)
s.text(216, 262, "diversity", 30, CYAN_DEEP, "middle", "bold")
s.text(216, 310, "Observed · Chao1", 30, GRAY, "middle")
s.text(216, 352, "Faith's PD", 30, GRAY, "middle")
s.text(216, 394, "Jaccard · UniFrac(uw)", 30, GRAY, "middle")
s.line(70, 420, 362, 420, PANEL, 4)

s.text(216, 484, "种类数必须抽平", 30, INK, "middle", "bold")
s.line(70, 508, 362, 508, PANEL, 4)
s.text(216, 560, "指数可选相对丰度", 30, GREEN, "middle", "bold")
s.text(216, 604, "Shannon · Simpson", 30, GRAY, "middle")

# ---------------- 右分支：差异丰度检验（红框警示） ----------------
s.rect(412, 212, 344, 424, RED_TINT, RED, 5, rx=14)
s.text(584, 268, "差异丰度严禁抽平", 30, RED, "middle", "bold")
s.line(438, 300, 730, 300, RED_TINT, 4, dash="10 8")

s.text(584, 372, "ANCOM-BC", 30, BLUE, "middle", "bold")
s.text(584, 424, "ALDEx2", 30, BLUE, "middle", "bold")
s.line(438, 480, 730, 480, RED_TINT, 4, dash="10 8")
s.text(584, 552, "raw counts", 30, GRAY, "middle")
s.text(584, 596, "keep variance", 30, GRAY, "middle")

s.save("26_rarefaction_decision_tree.svg")
