#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_m4_ref_fuel_distribution.py — 生成 04_m4_ref_fuel_distribution.svg（FIG-U08-04：
M4 参考基因组清单双轨分发）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-04（P18，cols 一栏，800×700）。
定性工程数据流（教材 §11.4.2、讲义 ④ 4.2、手册 §4.4.3–§4.6.3）：
M4 定种产出「参考基因组集 ref_genomes/*.fna」→ 双轨分发 M5（GToTree+IQ-TREE
建树）与 M6（Prokka 重注释 → Roary 矩阵）；红色印章＝共同燃料（唯一红）。
零登录号（规避 ALN W17）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 04_m4_ref_fuel_distribution.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)

    # 中央输入节点（深蓝）：M4 定种产出
    s.rect(50, 270, 290, 150, BLUE, rx=16)
    s.text(195, 322, "M4 定种产出", 34, WHITE, "middle", "bold")
    s.text(195, 366, "参考基因组集", 30, WHITE, "middle")
    s.text(195, 402, "ref_genomes/*.fna", 30, "#CFE8F0", "middle")

    # 双轨管道：上青蓝 → M5；下紫 → M6
    s.arrow(346, 316, 418, 208, CYAN_DEEP, 7)
    s.arrow(346, 384, 418, 492, PURPLE, 7)
    s.rect(420, 148, 330, 116, WHITE, CYAN_DEEP, 5, rx=14)
    s.text(585, 198, "M5 建树", 34, CYAN_DEEP, "middle", "bold")
    s.text(585, 240, "GToTree + IQ-TREE", 30, INK, "middle")
    s.rect(420, 436, 330, 116, WHITE, PURPLE, 5, rx=14)
    s.text(585, 486, "M6 矩阵", 34, PURPLE, "middle", "bold")
    s.text(585, 528, "Prokka → Roary", 30, INK, "middle")

    # 红色印章：共同燃料（唯一红；实心印章盖在分叉空档，不压卡片文字）
    s.raw('<g transform="rotate(-8 452 358)">')
    s.rect(372, 324, 160, 68, RED, rx=14)
    s.text(452, 368, "共同燃料", 34, WHITE, "middle", "bold")
    s.raw("</g>")

    # 底部结论横幅
    s.rect(110, 592, 580, 62, BLUE, rx=12)
    s.text(400, 635, "M5 建树与 M6 矩阵共同燃料", 34, WHITE, "middle", "bold")

    s.save("04_m4_ref_fuel_distribution.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
