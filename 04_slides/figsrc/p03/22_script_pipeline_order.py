#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""22_script_pipeline_order.py — 生成 22_script_pipeline_order.svg
（FIG-P03-22：第 44 页 cols 一栏「实验操作三脚本依赖流水线」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-22（P44，cols，800×700）。
依据：教材 §16.6 L451–456 与 `03_code/phd/scripts/` 的实际参数接口——三个脚本是一条
有向依赖链：`03_dual_rnaseq_quant.sh` 产出双物种矩阵与 `qc/biomass.tsv`；它跑完才有
`03_effector_screen.sh` 需要的输入，产出 SignalP / EffectorP / OrthoFinder 三列证据；
最后 `03_dual_deseq2_lrt.R` 汇集前两步的参数做建模与候选整合。顺序颠倒不是少一个
文件的问题，是脚本直接停机。
图内中文严格取方案给定 30 字（4 句）。三个脚本名属工具文件名，保留英文。
结构＝三条工序卡自上而下串成箭头链；每卡右端用「产出文件方块」的个数表达该步交付
几件东西（图形语义，不加中文标注），末尾一条红色停机警告条。
配色：青蓝＝正常流水线进度，绿色＝证据筛选步，深蓝＝建模步，红色只标顺序颠倒停机
这一处。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 22_script_pipeline_order.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["一定量拆分得矩阵", "二筛选出三列证据", "三输入齐备再建模", "顺序颠倒停机"]
TEXT = "".join(PHRASES)
STEPS = [(PHRASES[0], "03_dual_rnaseq_quant.sh", CYAN, CYAN_TINT, 3),
         (PHRASES[1], "03_effector_screen.sh", GREEN, GREEN_TINT, 3),
         (PHRASES[2], "03_dual_deseq2_lrt.R", BLUE, BLUE_TINT, 7)]


def main():
    s = SVG(800, 700, "Three-script dependency pipeline", plan=TEXT)

    # ---------- 三条工序卡 + 依赖箭头 ----------
    for i, (ph, script, main, tint, nfiles) in enumerate(STEPS):
        y = 40 + i * 172
        s.panel(64, y, 672, 132, tint, main, 4)
        s.circle(120, y + 46, 28, WHITE, main, 4)
        s.text(120, y + 57, str(i + 1), 30, main, "middle", "bold")
        s.text(168, y + 56, ph, 30, main, "start", "bold")
        s.text(168, y + 106, script, 30, INK, "start")
        # 右端交付件：nfiles 个方块（每行 ≤ 4 个）
        for k in range(nfiles):
            s.rect(596 + (k % 4) * 26, y + 40 + (k // 4) * 26, 20, 20, main,
                   None, 0, rx=4)
        if i < 2:
            s.arrow(400, y + 134, 400, y + 168, GRAY, 6, 16)

    # ---------- 红色停机警告条 ----------
    s.band(96, 560, 608, 78, PHRASES[3], RED, WHITE, 32)
    s.save("22_script_pipeline_order.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
