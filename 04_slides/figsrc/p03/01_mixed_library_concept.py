#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""01_mixed_library_concept.py — 生成 01_mixed_library_concept.svg
（FIG-P03-01：第 09 页 cols 一栏「双物种混合与双对照不对称」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-01（P09，cols，800×700）。
依据：教材 §16.1 L8–26（一片组织里两套转录本混在一起、宿主的对照是同期未接种、
病原的对照只能体外纯培养）；§16.4.1.3 L120–127（对照不对称决定可识别性）。
图内中文严格取方案给定的 27 字（4 句）。结构标签只保留 `RNA-seq`、`G11 / H2O`、
`in planta / in vitro` 这类工具名与样本名（COURSE_SYNC §7.10：工具与字段名可留英文，
英文说明性文字不进图）。上排左是「一片感染中的叶片」，蓝点宿主转录本、橙点病原
转录本；下排两张对照卡用「两枚对照牌 vs 一枚对照牌」表达不对称。
配色：深蓝宿主、浅橙病原、红色只标「来源未知」一处。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 01_mixed_library_concept.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["混合文库来源未知", "宿主配未接种", "病原配体外培养", "双对照不对称"]
TEXT = "".join(PHRASES)


def leaf(s):
    """叶片轮廓 + 主脉 + 叶缘细脉：让左面板一眼读成「一片感染中的叶子」。"""
    s.path("M 62 200 Q 120 60 262 84 Q 240 216 120 230 Q 74 226 62 200 Z",
           GREEN, 4, fill=WHITE)
    s.path("M 74 212 Q 162 148 248 94", GREEN, 3)
    for cx, cy in ((106, 168), (148, 136), (190, 108)):
        s.line(cx, cy, cx + 4, cy + 12, GREEN, 3)
    for cx, cy in ((96, 126), (120, 178), (166, 194), (112, 96)):
        s.dot(cx, cy, 11, BLUE)
    for cx, cy in ((158, 118), (208, 134), (198, 176)):
        s.dot(cx, cy, 11, ORANGE)


def main():
    s = SVG(800, 700, "One mixed library, two species, asymmetric controls",
            plan=TEXT)

    # ---------- 上排左：一片叶子里两套转录本混在一起 ----------
    s.rect(50, 56, 240, 190, "none", BLUE, 4, rx=16)
    leaf(s)

    # ---------- 上排中：一次 RNA-seq 跑同一管文库 ----------
    s.arrow(298, 150, 336, 150, CYAN, 6, 14)
    s.rect(344, 84, 150, 148, WHITE, BLUE, 4, rx=12)
    s.text(419, 128, "RNA-seq", 30, BLUE, "middle")
    for y in (146, 168, 190):
        s.rect(360, y, 52, 10, BLUE)
        s.rect(432, y, 52, 10, ORANGE)

    # ---------- 上排右：出口仍混在一起，来源未知（红，唯一警示）----------
    s.arrow(502, 150, 540, 150, CYAN, 6, 14)
    s.circle(602, 150, 40, RED_TINT, RED, 5)
    s.text(602, 163, "?", 40, RED, "middle", "bold")
    s.text(602, 272, PHRASES[0], 30, RED, "middle", "bold")

    # ---------- 下排：两张对照卡，左边两枚对照牌、右边一枚 ----------
    s.panel(50, 300, 340, 250, BLUE_TINT, BLUE, 4)
    s.rect(50, 300, 10, 250, BLUE)
    s.text(80, 356, PHRASES[1], 30, BLUE, "start", "bold")
    s.text(80, 414, "G11 / H2O", 30, INK)
    for i in range(2):                                   # 两枚：接种 + 未接种
        x = 96 + i * 92
        s.rect(x, 450, 72, 72, WHITE, BLUE, 4, rx=10)
        s.circle(x + 36, 486, 16, BLUE)

    s.panel(410, 300, 340, 250, ORANGE_TINT, ORANGE, 4)
    s.rect(410, 300, 10, 250, ORANGE)
    s.text(440, 356, PHRASES[2], 30, ORANGE, "start", "bold")
    s.text(440, 414, "in planta / in vitro", 30, INK)
    s.rect(440, 450, 72, 72, WHITE, ORANGE, 4, rx=10)    # 一枚：只有体外
    s.circle(476, 486, 16, ORANGE)

    s.caption([PHRASES[3]], [BLUE], top=580, gap=52, pad_top=30)
    s.save("01_mixed_library_concept.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())
