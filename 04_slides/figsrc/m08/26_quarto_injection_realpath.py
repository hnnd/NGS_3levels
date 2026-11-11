#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""26_quarto_injection_realpath.py — FIG-M08-26 Quarto 报告参数注入与绝对路径绑定（P51，cols）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-26（`.cols` 一栏 800×700，new-svg）。
依据：教材 §23.4.6（报告框取真实物理路径后经 -P 注入 qmd；相对路径会误读历史旧文件）。
图内汉字 = 方案原句逐字，共 29 字（参数注入真实路径 / 绝对路径绑定输入 /
防误读旧文件 / 报告渲染即现算）；命令与文件名用 ASCII。红 1 处标「防误读旧文件」。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 26_quarto_injection_realpath.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402


def main():
    s = SVG()

    # ① 规则端：取真实物理路径
    s.rect(40, 24, 720, 150, CYAN_TINT, CYAN, 4, rx=14)
    s.text(400, 64, "rule report", 30, CYAN_DEEP, "middle", "bold")
    s.text(400, 108, "os.path.realpath(counts)", 30, GRAY, "middle")
    s.text(400, 154, "参数注入真实路径", 30, BLUE, "middle", "bold")
    s.arrow(400, 176, 400, 208, CYAN, 6, 16)

    # ② 命令行参数注入（两个 -P 一行一条，避免出框）
    s.rect(40, 214, 720, 176, WHITE, BLUE, 4, rx=14)
    s.text(400, 256, "quarto render report.qmd", 30, BLUE, "middle", "bold")
    s.text(400, 300, "-P counts=/abs/counts_matrix.tsv", 30, GRAY, "middle")
    s.text(400, 340, "-P tpm=/abs/tpm_matrix.tsv", 30, GRAY, "middle")
    s.text(400, 378, "绝对路径绑定输入", 30, BLUE, "middle", "bold")
    s.arrow(400, 392, 400, 424, CYAN, 6, 16)

    # ③ 渲染产物：渲染即现算（绿色）
    s.rect(40, 430, 720, 122, GREEN_TINT, GREEN, 4, rx=14)
    s.text(400, 490, "report.html", 32, GREEN, "middle", "bold")
    s.text(400, 528, "报告渲染即现算", 30, GREEN, "middle")

    # ④ 唯一警示：不做 realpath 就误读旧文件
    s.rect(190, 566, 420, 92, RED_TINT, RED, 5, rx=14)
    s.text(400, 622, "防误读旧文件", 34, RED, "middle", "bold")

    return s.save("26_quarto_injection_realpath.svg")


if __name__ == "__main__":
    raise SystemExit(main())
