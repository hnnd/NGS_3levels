#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_contig_name_limit_rename.py — 生成 21_contig_name_limit_rename.svg（FIG-U07-21：contig 名超限报错与重命名联动）

方案：reviews/course/U07_FIGP_001.md §4.3 FIG-U07-21（P63，cols 一栏，viewBox 800×700）。
数据：无量字数字。Prokka 1.14.6 源码 MAXCONTIGIDLEN = 37；示例
tig00000001|arrow|polished_round2_contig_1 共 42 字符越线报错；
--compliant 重命名须同步 FASTA、.fai、BAM @SQ（教材 §9.4.4 L204、§9.5.2）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 21_contig_name_limit_rename.py
"""
from svghelp import *  # noqa: F401,F403

LONG_NAME = "tig00000001|arrow|polished_round2_contig_1"


def main():
    assert len(LONG_NAME) == 42
    print(f"check: contig 名 {len(LONG_NAME)} 字符 > 37 上限")

    s = SVG(800, 700)

    # 左：超长 contig 名（红框报错块，红色语义处 1）
    s.text(40, 96, "名字超三十七字符", 32, BLUE, "start", "bold")
    s.rect(40, 116, 720, 64, WHITE, RED, 6, rx=10)
    s.text(60, 158, LONG_NAME, 30, INK, "start")
    s.rect(40, 204, 190, 52, RED, rx=10)
    s.text(135, 240, "报错中断", 30, WHITE, "middle", "bold")
    s.text(60, 300, "42 > 37", 30, GRAY, "start")

    # 中：Prokka --compliant 重编号算子（青蓝）
    s.arrow(236, 230, 324, 230, GRAY, 6)
    s.rect(330, 185, 260, 105, CYAN, rx=14)
    s.text(460, 232, "--compliant", 30, WHITE, "middle", "bold")
    s.text(460, 270, "--centre", 30, WHITE, "middle")
    s.text(460, 345, "重命名联动", 32, CYAN_DEEP, "middle", "bold")

    # 右：联动链条（FASTA → .fai → @SQ）
    s.arrow(594, 238, 634, 238, GRAY, 6)
    s.rect(640, 180, 150, 54, BLUE, rx=10)
    s.text(715, 216, "FASTA", 30, WHITE, "middle", "bold")
    s.arrow(715, 238, 715, 258, GRAY, 5, head=12)
    s.rect(640, 262, 150, 54, BLUE, rx=10)
    s.text(715, 298, ".fai", 30, WHITE, "middle", "bold")
    s.arrow(715, 320, 715, 340, GRAY, 5, head=12)
    s.rect(640, 344, 150, 54, BLUE, rx=10)
    s.text(715, 380, "@SQ", 30, WHITE, "middle", "bold")

    # 底部红色同步警示条（红色语义处 2）
    s.rect(270, 560, 260, 58, RED, rx=12)
    s.text(400, 601, "同步更名", 32, WHITE, "middle", "bold")

    s.save("21_contig_name_limit_rename.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
