#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""07_symlink_cost.py — 生成 07_symlink_cost.svg
（FIG-U01-07：cp 与 ln -s 的空间账——data-plot）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-07（P24，cols 一栏，800×700）。
数据（必须与现跑一致；.ref=「行为复现，demos/ch01_symlink_checks.py --selftest」）：
  真实文件 reads.fa = 15 B；活链接自身 lstat = 8 B = 目标串 "reads.fa" 字节数。
  本文件内以 os.lstat/os.path.getsize 现算断言后落图（见 selfcheck()）。
依据：教材 §1.4.6 L146–157（逻辑长度 ≠ 磁盘块/配额记账）、§1.5.4 前半。
无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 07_symlink_cost.py
"""
import os
import tempfile
from pathlib import Path

from svghelp import *  # noqa: F401,F403


def selfcheck():
    """与 demos/ch01_symlink_checks.py 同一行为复现：15 B 文件 / 8 B 活链接。"""
    with tempfile.TemporaryDirectory() as td:
        real = Path(td) / "reads.fa"
        real.write_text(">r1\nACGTACGTAC\n")     # 15 B，与 demo 同款
        good = Path(td) / "good.fa"
        good.symlink_to("reads.fa")
        assert os.path.getsize(real) == 15, "真实文件应 15 B"
        assert os.lstat(good).st_size == 8 == len("reads.fa"), "活链接应 8 B"
        return 15, 8


def file_block(s, x, y, w, path, tag, tint=CYAN, edge=CYAN_DEEP):
    """文件块：填充 + 路径 + 字节数角标（路径用 sans 30px 防溢出）。"""
    s.rect(x, y, w, 92, tint, edge, 4, rx=10)
    s.text(x + w / 2, y + 40, path, 30, INK, "middle")
    s.text(x + w / 2, y + 74, tag, 30, edge, "middle", "bold")


def dash_arrow(s, x1, y1, x2, y2, color, dash="12 8", sw=5, head=16):
    s.line(x1, y1, x2 - head, y2, color, sw, dash=dash, cap="round")
    s.polygon([(x2, y2), (x2 - head, y2 - head * 0.62),
               (x2 - head, y2 + head * 0.62)], color)


def main():
    real_b, link_b = selfcheck()
    s = SVG(800, 700)

    # ===== 左栏：cp：数据搬一份（x24-390）=====
    s.text(205, 58, "cp：数据搬一份", 36, BLUE, "middle", "bold")
    file_block(s, 24, 110, 170, "/data/lab/", f"{real_b} B")
    s.arrow(200, 156, 240, 156, GRAY, 6)
    s.polygon([(240, 148), (240, 164), (252, 156)], GRAY)
    file_block(s, 254, 110, 136, "~/ngs/fq/", f"{real_b} B")
    s.text(205, 250, "配额翻倍", 34, RED, "middle", "bold")

    # ===== 右栏：ln -s：只写一张字条（x410-790）=====
    s.text(600, 58, "ln -s：只写一张字条", 36, PURPLE, "middle", "bold")
    # 个人区字条（内容=目标路径字符串）
    s.rect(414, 110, 158, 92, PURPLE_TINT, PURPLE, 4, rx=10)
    s.text(493, 150, "reads.fa", 30, INK, "middle", family=MONO)
    s.text(493, 186, f"{link_b} B", 30, PURPLE, "middle", "bold")
    # 虚线穿透箭头 → 同一公共区文件块（无第二块）
    dash_arrow(s, 578, 156, 634, 156, PURPLE)
    file_block(s, 642, 110, 148, "ngs/", f"{real_b} B")
    s.text(560, 250, f"{link_b} B → 指向原文件", 30, PURPLE, "middle", "bold")

    # ===== 底部灰色一行 =====
    s.text(400, 640, "链接大小＝目标名字节数", 32, GRAY, "middle", "bold")

    s.save("07_symlink_cost.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
