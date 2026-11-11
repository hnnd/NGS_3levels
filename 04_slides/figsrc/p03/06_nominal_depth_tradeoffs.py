#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""06_nominal_depth_tradeoffs.py — 生成 06_nominal_depth_tradeoffs.svg
（FIG-P03-06：第 18 页 cols 一栏「名义深度 732× 当量矛盾与三大折中」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-06（P18，cols，800×700）。
依据：教材 §16.4.1.1 L96–104——`D_used = 2×10⁹` / `4×10⁹` 按同一 0.41 Gb 复合参考、
150 bp 单端换算得名义深度 731.7 ≈ 732× 与 1463.4 ≈ 1463×；一份样本七百多到一千四
百多倍的基因组当量测序量，在十几个样本的课题里不成立。三种折中各放弃一样东西：
高密点接种（提高微区同步，牺牲重复一致性）、探针捕获（带捕获偏好）、后移首个时点
（2% 是讲义经验折中值、标设例，代价是最早那批响应基因移出观测窗口）。
数字入口：教材 §16.4.1.1 的手算（本脚本 `check_depth()` 用同一条算式重算并断言）。
图内中文严格取方案给定 29 字（4 句）；`732×`、`1463×`、`0.41 Gb`、`150 bp` 为符号
与教材既有常数，上标用 tspan 渲染（本机字体缺 ⁷/⁹ 字形，直写会出方块）。
配色：红色只标「名义深度超千倍」一处警示；三张折中卡深蓝/青蓝/紫。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 06_nominal_depth_tradeoffs.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["名义深度超千倍", "高密点接种控同步", "探针捕获带偏好", "后移时相舍早期"]
TEXT = "".join(PHRASES)
CARDS = [(PHRASES[1], BLUE, BLUE_TINT, 0.75),
         (PHRASES[2], CYAN, CYAN_TINT, 0.55),
         (PHRASES[3], PURPLE, PURPLE_TINT, 0.40)]      # 末项＝保留度，仅作示意


def check_depth():
    """与教材 §16.4.1.1 同一算式：D_used × 150 bp ÷ 0.41 Gb → 732× / 1463×。"""
    got = [round(d * 150 / 0.41e9) for d in (2e9, 4e9)]
    if got != [732, 1463]:
        raise SystemExit(f"名义深度与教材手算不一致：{got}")
    return got


def main():
    got = check_depth()
    s = SVG(800, 700, "Nominal depth and three trade-offs", plan=TEXT)

    # ---------- 顶部：名义深度指标（红色确定不可行的一档）----------
    s.rect(44, 40, 712, 150, RED_TINT, RED, 4, rx=16)
    s.sci(78, 106, "2×10", "9", 34, INK, "start", "bold")
    s.text(232, 106, "/", 34, GRAY)
    s.sci(262, 106, "4×10", "9", 34, INK, "start", "bold")
    s.text(78, 156, "0.41 Gb · 150 bp", 30, GRAY)
    s.text(722, 106, f"{got[0]}×", 34, RED, "end", "bold")
    s.text(722, 156, f"{got[1]}×", 34, RED, "end", "bold")

    s.text(400, 240, PHRASES[0], 30, RED, "middle", "bold")

    # ---------- 三张折中代价行：编号 + 代价（放弃的那一样）----------
    for i, (head, main, tint, keep) in enumerate(CARDS):
        y = 300 + i * 118
        s.panel(44, y, 712, 100, tint, main, 4)
        s.circle(102, y + 50, 28, WHITE, main, 4)
        s.text(102, y + 61, str(i + 1), 30, main, "middle", "bold")
        s.text(152, y + 62, head, 30, main, "start", "bold")
        s.rect(520, y + 30, 200, 40, WHITE, main, 3, rx=8)
        s.rect(520, y + 30, 200 * keep, 40, main, None, 0, rx=8)
    s.save("06_nominal_depth_tradeoffs.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
