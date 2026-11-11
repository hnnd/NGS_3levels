#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""17_case_busco_canu_vs_flye.py — 生成 17_case_busco_canu_vs_flye.svg（FIG-U08-17：
设例 C=98.4% 下 Canu 冗余 D=6.5% vs Flye D=0.8%）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-17（P49，cols 一栏，800×700）【data-plot】。
数据：讲义 ⑩ Q1 设例（Canu 12 contigs / 4.6 Mb，C=98.4%[S=91.9, D=6.5] vs
Flye 2 contigs / 4.05 Mb，C=98.4%[S=97.6, D=0.8]）；BUSCO 粒度与 C=S+D 加法
自检调用 demos/ch08_n50_vs_completeness.py --example 4（n=124，1 基因=0.81 pp，
教材 §8.4.8、§8.4.9）。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 17_case_busco_canu_vs_flye.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "textbook"
                       / "demos"))
import ch08_n50_vs_completeness as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403,E402

# 设例（讲义 ⑩ Q1，非实测）：(名字, contig 数, 总长, C, S, D, 主色)
CASES = [
    ("Canu", 12, "4.6 Mb", 98.4, 91.9, 6.5, CYAN),
    ("Flye", 2, "4.05 Mb", 98.4, 97.6, 0.8, GREEN),
]


def main():
    # —— 数据复核：设例内部一致 + demo 例 4 粒度 ——
    for name, _, _, c, s, d, _ in CASES:
        assert abs(s + d - c) < 1e-9, f"{name}: S+D 应等于 C"
    assert demo.example4(), "demo 例 4（0.81 pp、C=S+D）应通过"
    print("check: 两组设例均 C=S+D；demo 例 4：n=124，1 基因 = 0.81 pp")

    s = SVG(800, 700)
    for i, (name, ncontig, total, c, sv, dv, color) in enumerate(CASES):
        cx = 40 + i * 380
        s.rect(cx, 100, 340, 400, WHITE, PANEL, 4, rx=16)
        s.rect(cx + 24, 124, 20, 20, color, rx=4)
        s.text(cx + 56, 144, name, 36, INK, "start", "bold")
        s.text(cx + 24, 196, f"{ncontig} contigs / {total}", 30, GRAY, "start")
        s.text(cx + 24, 248, "BUSCO bacteria_odb10", 30, GRAY, "start")
        # 堆叠条：S 主色 + D（Canu 红斜纹 / Flye 浅灰）+ 缺失灰
        bx, bw, by, bh = cx + 24, 292, 320, 46
        w_s = bw * sv / 100
        w_d = bw * dv / 100
        s.rect(bx, by, w_s, bh, color, rx=4)
        seg = [(bx + w_s, w_d)]
        s.rect(bx + w_s, by, w_d, bh, RED if name == "Canu" else PANEL, rx=0)
        if name == "Canu":  # 红色斜纹（D=6.5% 冗余警示）
            cid = s.clip("hatch", [(bx + w_s, by), (bx + w_s + w_d, by),
                                   (bx + w_s + w_d, by + bh),
                                   (bx + w_s, by + bh)])
            s.raw(f'<g clip-path="{cid}">')
            for k in range(-2, 6):
                x0 = bx + w_s + k * 12
                s.line(x0, by + bh, x0 + bh, by, WHITE, 3)
            s.raw("</g>")
        s.rect(bx + w_s + w_d, by, bw - w_s - w_d, bh, PANEL, rx=0)
        s.rect(bx, by, bw, bh, "none", INK, 2, rx=4)
        s.text(bx, by - 18, f"C={c:g}%  (S={sv:g}%)", 30, INK, "start", "bold")
        if name == "Canu":
            s.text(bx + bw, by + bh + 48, f"D={dv:g}% 冗余", 32, RED, "end",
                   "bold")
        else:
            s.text(bx + bw, by + bh + 48, f"D={dv:g}%", 32, GRAY, "end",
                   "bold")
        s.text(bx + 10, by + bh / 2 + 11, f"S={sv:g}%", 30, WHITE, "start",
               "bold")

    # 底部结论横幅
    s.rect(160, 552, 480, 62, GREEN, rx=12)
    s.text(400, 595, "C 相同看 D：选 Flye", 36, WHITE, "middle", "bold")
    s.text(400, 650, "设例（讲义 ⑩ Q1）", 30, GRAY, "middle")
    s.text(400, 688, "demos/ch08_n50_vs_completeness.py", 30, GRAY, "middle")

    s.save("17_case_busco_canu_vs_flye.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
