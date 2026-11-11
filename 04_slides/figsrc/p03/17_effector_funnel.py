#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_effector_funnel.py — 生成 17_effector_funnel.svg
（FIG-P03-17：第 35 页 cols 一栏「效应子三步串联漏斗与系统性漏检」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-17（P35，cols，800×700）。
依据：教材 §16.4.6 L303–310、§16.5.4 L424——预测流水线是三步串联：SignalP 判信号肽、
在其中剔除跨膜螺旋（先切信号肽再看成熟肽）、最后由 EffectorP 给后验概率排序。
三级串联每级只做一次二分类，误差沿链累积且无法回补：非经典的分泌途径与细菌 T3SS
效应子根本没有可被 SignalP 识别的信号肽，链上第一级就被丢掉；非模式病原的新颖特征
又常落在 EffectorP 训练分布之外。因此整条链的产物只能是「候选排序表」，是假设生成，
不是鉴定结论。
图内中文严格取方案给定 29 字（4 句）。`SignalP 6.0`、`TM`、`EffectorP 3.0` 为工具名与
概念符号，不作英文说明。三级台阶用图形语义（逐层收窄的漏斗 + 左侧三条进料标注 +
顶部红色旁路漏检箭头）表达，产物用横条排序表图元表达，不再加中文标注。
配色：青蓝＝正常分泌流，深蓝＝跨膜排除，紫色＝分类器排序，红色只标两处
（非经典漏检、产生假设非鉴定）。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 17_effector_funnel.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["信号肽漏非经典", "成熟肽排除跨膜", "分类器给后验概率", "产生假设非鉴定"]
TEXT = "".join(PHRASES)
CX = 552                                              # 漏斗中轴
# (工具名, 主色, 淡色, 上边宽, 下边宽, 顶边 y)
STEPS = [("SignalP 6.0", CYAN, CYAN_TINT, 430, 376, 96),
         ("TM", BLUE, BLUE_TINT, 360, 300, 210),
         ("EffectorP 3.0", PURPLE, PURPLE_TINT, 290, 230, 324)]
LABEL_Y = (142, 256, 370)                             # 三条左侧进料标注的基线


def main():
    s = SVG(800, 700, "Three-step effector funnel", plan=TEXT)

    # ---------- 三级台阶：逐层收窄 ----------
    for (name, main, tint, wtop, wbot, y) in STEPS:
        s.wedge(CX, y, wtop, wbot, 96, tint, main, 4)
        s.text(CX, y + 56, name, 30, main, "middle", "bold")

    # ---------- 左侧三条进料标注（箭头从标注指向台阶左沿）----------
    for i, (ph, (_, main, _, wtop, _wbot, _y)) in enumerate(
            zip(PHRASES[:3], STEPS)):
        s.text(40, LABEL_Y[i] + 11, ph, 30, INK, "start", "bold")
        # 箭头起点留出标注框右边界（最长一行约 250 宽，40+250=290）
        s.arrow(302, LABEL_Y[i] + 4, CX - wtop / 2 - 10, LABEL_Y[i] + 4,
                main, 5, 14)

    # ---------- 顶部红色旁路：非经典途径在第一级就被漏掉 ----------
    s.path(f"M {CX - 60} 100 Q {CX - 120} 60 {CX - 168} 46", RED, 5, dash="9 7")
    s.cross(CX - 182, 42, 17, RED, 7)

    # ---------- 产物：候选排序表（无文字，横条图元）----------
    s.arrow(CX, 424, CX, 464, GRAY, 6, 14)
    s.panel(330, 468, 420, 108, WHITE, BLUE, 4)
    for i, w in enumerate((360, 310, 260, 210)):
        s.rect(356, 484 + i * 22, w, 10, BLUE, None, 0, rx=5)

    # ---------- 红色免责印章：产生假设非鉴定 ----------
    s.stamp(180, 612, 268, 72, PHRASES[3], RED, RED, 30)
    s.save("17_effector_funnel.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
