#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""24_duplicate_chrom_silent_chain.py — 生成 24_duplicate_chrom_silent_chain.svg
（FIG-P03-24：第 62 页 cols 一栏「序列重名与 GTF 未同步静默吞噬链」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-24（P62，cols，800×700）。
依据：教材 §16.5.1 L377–399——双物种参考合并时，两个物种各有一条 `chr1` 是常态。
故障链全在「不报错」的环节：`samtools faidx` 遇到重名只发 Warning 而退出码仍是 0；
STAR 的 `chrName.txt` 里于是并排存着两条 `chr1`；下游按名字取序列，两条染色体的
读段被静默挤进同一个键，半个基因组的定量在无人察觉的情况下合并。
防御网是把名字清单当前置硬闸：`comm -23` 取两侧差集、`uniq -d` 取重复项，
任一清单非空即 FATAL 终止，根本不进入比对。
图内中文严格取方案给定 29 字（4 句）。`chr1`、`samtools faidx`、`chrName.txt`、
`comm -23`、`uniq -d`、`FATAL` 为命令与状态词，保留原样。
结构＝上部故障链三环（红虚线箭头串起），链条下方用「两股读段汇进同一个槽」的图元
把「单键合并」画出来；下部绿色护盾包住两条清单检查，右侧红字点出零退出码的隐蔽性
并直指 FATAL。
配色：红色只标故障链结论与零退出码两处；绿色只标硬名单拦截。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 24_duplicate_chrom_silent_chain.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["重名索引仅警告", "单键合并吞读段", "名单非空即终止", "零退出码掩盖重名"]
TEXT = "".join(PHRASES)
CHAIN = [("samtools faidx", CYAN, CYAN_TINT),
         ("chrName.txt", PURPLE, PURPLE_TINT),
         ("chr1 × 2", ORANGE, ORANGE_TINT)]


def reads(s, x, y, n, color, pitch=14):
    """一列读段短棒：示意被合并的读段。"""
    for k in range(n):
        s.rect(x, y + k * pitch, 46, 10, color, None, 0, rx=5)


def main():
    s = SVG(800, 700, "Duplicate sequence names silently swallow reads",
            plan=TEXT)

    # ---------- 上部故障链：三环 + 红虚线箭头 ----------
    for i, (lab, main, tint) in enumerate(CHAIN):
        x = 40 + i * 250
        w = 230
        s.panel(x, 58, w, 96, tint, main, 4)
        s.text(x + w / 2, 122, lab, 30, main, "middle", "bold")
        if i < 2:
            s.arrow(x + w + 4, 106, x + w + 22, 106, ORANGE, 4, 11, dash="8 6")

    # ---------- 故障链结论（红）----------
    s.text(44, 208, PHRASES[1], 30, RED, "start", "bold")

    # 两股读段汇入同一个键（槽）
    reads(s, 132, 240, 6, BLUE)
    reads(s, 500, 240, 6, ORANGE)
    s.path("M 186 286 Q 300 340 356 340", ORANGE, 5, dash="9 7")
    s.path("M 506 286 Q 420 340 400 336", ORANGE, 5, dash="9 7")
    s.rect(352, 300, 116, 96, PANEL, BLUE, 3, rx=10)
    reads(s, 387, 312, 5, BLUE, 15)
    s.text(420, 424, "chr1", 30, BLUE, "middle", "bold")
    s.line(44, 462, 756, 462, PANEL, 4)

    # ---------- 下部防御网：护盾 + 两条清单检查 ----------
    s.shield(92, 576, 88, 116, GREEN, GREEN_TINT, 5)
    s.check(92, 576, 24, GREEN, 9)
    s.text(148, 566, "comm -23", 30, GREEN, "start", "bold")
    s.text(148, 618, "uniq -d", 30, GREEN, "start", "bold")
    s.text(44, 672, PHRASES[2], 30, GREEN, "start", "bold")

    # ---------- 右侧：零退出码的隐蔽性 + FATAL ----------
    s.text(452, 528, PHRASES[3], 30, RED, "start", "bold")
    s.arrow(530, 556, 530, 606, GRAY, 6, 14)
    s.band(400, 618, 358, 66, "FATAL", BLUE, WHITE, 32)
    s.save("24_duplicate_chrom_silent_chain.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
