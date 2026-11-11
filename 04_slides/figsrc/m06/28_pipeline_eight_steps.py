#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""28_pipeline_eight_steps.py — FIG-M06-28 全流程八步流水线总览图

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-28（P48，cols 一栏 800×700，new-svg）。
教材依据：§18.4.3–18.4.8（去噪链每一步的产出是下一步输入）、§18.6（八步流程与每一步「什么结果说明流程错了」）。
图内汉字 = 方案原句逐字，共 21 字（下载预检 / 算清重叠 / 作业投递 / 诊断漏斗 / 多样性检验）；
其余为步骤编号 0–7、工具名 download、precheck、truncLen、qsub、track、taxonomy、diversity、stats
与门禁标记 gate。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 28_pipeline_eight_steps.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

s = SVG()

s.text(400, 56, "pipeline 0–7", 34, BLUE, "middle", "bold")

SPINE = 92
Y0, PITCH = 124, 68
STEPS = ["download", "precheck", "truncLen", "qsub", "track", "taxonomy", "diversity", "stats"]

# 主线（深蓝）
s.line(SPINE, Y0 - 16, SPINE, Y0 + 7 * PITCH + 16, BLUE, 5)

# 每一行的中文标注（方案原句逐字）
NOTES = {0: "下载预检", 2: "算清重叠", 3: "作业投递", 4: "诊断漏斗", 6: "多样性检验"}
GATES = (2, 5)

for i, name in enumerate(STEPS):
    y = Y0 + i * PITCH
    s.circle(SPINE, y, 21, BLUE_TINT, BLUE, 4)
    s.text(SPINE, y + 10, str(i), 30, BLUE, "middle", "bold")
    s.text(SPINE + 40, y + 11, name, 30, INK, "start")
    if i in NOTES:
        s.chip(600, y, NOTES[i], 30, GREEN_TINT, GREEN, INK, padx=18, pady=10)

# 门禁：第 2 步与第 5 步之后的自查点（绿色菱形）
for i in GATES:
    y = Y0 + i * PITCH + PITCH / 2
    s.polygon([(SPINE, y - 12), (SPINE + 12, y), (SPINE, y + 12), (SPINE - 12, y)], GREEN)
    s.line(SPINE + 18, y, 340, y, GREEN, 3, dash="8 7")
    s.text(354, y + 11, "gate", 30, GREEN, "start")

s.save("28_pipeline_eight_steps.svg")
