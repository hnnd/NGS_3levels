#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_candidate_scale_sanity.py — 生成 19_candidate_scale_sanity.svg
（FIG-P03-19：第 37 页 cols 一栏「效应子筛选候选规模量级自检卡」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-19（P37，cols，800×700）。
依据：教材 §16.4.6 L317–318、§16.5.4 L428——三步筛选的产出规模本身是一条黄金
判据：稻瘟菌 70-15 注释 11,109 个编码蛋白基因，分泌组通常占 5%–10%，跨膜排除与
EffectorP 排序后候选收敛到数十至数百。产出三千以上，第一嫌疑是把未切信号肽的全长
序列甚至核酸序列投给了分类器；只有个位数则先查物种界选项。数量级不对不是参数
微调问题，是输入形态错了。
数字入口：11,109 来自教材 §16.4.6（[@dean2005magnaporthe] 的 70-15 注释）；5%–10%
与「数十至数百」是教材明写的经验法则，非实测。`scale_check()` 只做量级换算与区间
次序断言，不生成任何未标注的经验数字。
图内中文严格取方案给定 28 字（4 句）。`11,109`、`5%–10%`、`3000`、`0–9` 为数值。
结构＝左侧三层递减量级卡（蛋白组 → 分泌组 → 候选，条长按量级等比），右侧一条竖直
判读标尺：上端红点标「3000」（超此数＝输入形态可疑），下端橙点标「0–9」（低此数＝
物种界选项可疑），中段绿点标达标区间；底部一条红字结论。
配色：深蓝＝蛋白组基准，青蓝＝分泌组，绿色＝正常候选区间，红色只标超三千这一处。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 19_candidate_scale_sanity.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["全蛋白组万余", "分泌组数百千余", "候选数十至数百", "超三千查输入形态"]
TEXT = "".join(PHRASES)
PROTEOME = 11109                               # 教材 §16.4.6：70-15 编码蛋白基因
SEC_LO, SEC_HI = 0.05, 0.10                    # 教材经验法则：分泌组占比
TOO_MANY = 3000                                # 教材判据：超三千先查输入形态
FEW = 9                                        # 教材判据：个位数先查物种界选项


def scale_check():
    lo, hi = PROTEOME * SEC_LO, PROTEOME * SEC_HI
    if not (lo <= hi < TOO_MANY):
        raise SystemExit(f"量级次序不成立：{lo}–{hi} vs {TOO_MANY}")
    if FEW >= lo:
        raise SystemExit(f"阈值次序不成立：{FEW} vs {lo}")
    return f"{lo:.0f}", f"{hi:.0f}"


def main():
    sec_lo, sec_hi = scale_check()
    s = SVG(800, 700, "Candidate scale sanity check", plan=TEXT)

    # ---------- 左侧三层递减量级卡 ----------
    rows = [(PHRASES[0], BLUE, 470, f"{PROTEOME:,}"),
            (PHRASES[1], CYAN, 210, f"{sec_lo}–{sec_hi}"),
            (PHRASES[2], GREEN, 92, "")]
    for i, (ph, main, w, val) in enumerate(rows):
        y = 66 + i * 148
        s.text(44, y, ph, 30, main, "start", "bold")
        s.rect(44, y + 24, 470, 38, WHITE, main, 3, rx=10)
        s.rect(44, y + 24, w, 38, main, None, 0, rx=10)
        if val:
            s.text(44, y + 104, val, 30, main, "start", "bold")

    # ---------- 右侧竖直判读标尺 ----------
    x = 566
    s.line(x, 56, x, 520, PANEL, 6)
    for cy, col, tint, lab in ((92, RED, RED_TINT, str(TOO_MANY)),
                               (300, GREEN, GREEN_TINT, ""),
                               (476, ORANGE, ORANGE_TINT, f"0–{FEW}")):
        s.circle(x, cy, 26, tint, col, 4)
        if lab:
            s.text(x + 44, cy + 11, lab, 30, col, "start", "bold")
        else:
            s.check(x, cy, 17, GREEN, 7)

    # ---------- 底部结论（唯一红色）----------
    s.band(96, 566, 608, 78, PHRASES[3], RED, WHITE, 32)
    s.save("19_candidate_scale_sanity.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())
