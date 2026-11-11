#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_acceptance_four_gates.py — 生成 16_acceptance_four_gates.svg（FIG-U05-16：验收四件一起做）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-16（P55，cols 一栏，viewBox 800×700）。
BAM 圆柱 → 四张检查卡（2×2）：退出码＋日志（pipefail，不删产物）｜quickcheck（只查头尾）
｜对账（view -c -F 0x900，2×模板数）｜idxstats（分 contig 看空缺）；
底部绿条「缺一件就有暗门」。依据教材 §7.4.6 L262–266（0x900=2048+256=2304 正文算术）、
§7.5.2 L369。命令与选项名与 samtools 1.17 手册一致。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 16_acceptance_four_gates.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    # 数据自检（教材 §7.4.6 L266 正文算术）
    assert 0x900 == 2048 + 256 == 2304
    print("check: 0x900 = 2048 + 256 = 2304")

    s = SVG(800, 700)

    # 顶部 BAM 圆柱
    s.raw(f'<ellipse cx="400" cy="56" rx="35" ry="11" fill="{CYAN}"/>')
    s.rect(365, 56, 70, 84, CYAN)
    s.raw(f'<ellipse cx="400" cy="140" rx="35" ry="11" fill="{CYAN}"/>')
    s.raw(f'<ellipse cx="400" cy="140" rx="35" ry="11" fill="none" '
          f'stroke="{CYAN_DEEP}" stroke-width="3"/>')
    s.text(400, 108, "BAM", 32, WHITE, "middle", "bold")

    # 汇流总线 → 四卡
    s.line(400, 152, 400, 180, BLUE, 5)
    s.line(230, 180, 570, 180, BLUE, 5)
    s.line(400, 180, 400, 385, BLUE, 5)
    s.line(230, 385, 570, 385, BLUE, 5)
    for bx in (230, 570):
        s.line(bx, 180, bx, 204, BLUE, 5)
        s.line(bx, 385, bx, 409, BLUE, 5)

    # 卡① 退出码＋日志
    s.rect(70, 206, 320, 165, WHITE, BLUE, 5, rx=14)
    s.text(100, 251, "退出码＋日志", 32, INK, "start", "bold")
    s.text(100, 293, "pipefail", 30, BLUE, "start", "bold")
    s.circle(106, 324, 8, RED)
    s.text(122, 332, "不删产物", 30, RED, "start", "bold")

    # 卡② quickcheck
    s.rect(410, 206, 320, 165, WHITE, BLUE, 5, rx=14)
    s.text(440, 251, "quickcheck", 30, BLUE, "start", "bold")
    s.text(440, 296, "只查头尾", 30, INK, "start", "bold")

    # 卡③ 对账
    s.rect(70, 411, 320, 170, WHITE, BLUE, 5, rx=14)
    s.text(100, 456, "对账", 32, INK, "start", "bold")
    s.text(100, 500, "view -c -F 0x900", 30, GRAY, "start", "bold")
    s.text(100, 544, "2 × 模板数", 30, INK, "start", "bold")

    # 卡④ idxstats
    s.rect(410, 411, 320, 170, WHITE, BLUE, 5, rx=14)
    s.text(440, 456, "idxstats", 30, BLUE, "start", "bold")
    s.text(440, 501, "分 contig 看空缺", 30, INK, "start", "bold")

    # 底部绿条
    s.rect(70, 604, 660, 56, GREEN, rx=12)
    s.text(400, 642, "缺一件就有暗门", 32, WHITE, "middle", "bold")

    s.save("16_acceptance_four_gates.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
