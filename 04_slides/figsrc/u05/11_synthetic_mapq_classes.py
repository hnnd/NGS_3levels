#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11_synthetic_mapq_classes.py — 生成 11_synthetic_mapq_classes.svg（FIG-U05-11：合成批 MAPQ）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-11（P34，cols 一栏，viewBox 800×700）【data-plot】。
bwa 口径三类散点（各 600 条）：unique 全 60（绿）/ conserved 全 0（红）/
diverged 聚 11（橙）；bowtie2 对照小点 42/1/6（灰）；红横幅 mapped 100%、
MAPQ=0 占 600/1800＝33.3%。数据由 demos/ch07_mapq_multimapping.py 的函数现跑取数
（固定种子 20261103，与方案 §0.2 及 deck P34 现表逐位一致，Q5）；不手抄。
依据教材 §7.4.5 L226。无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 11_synthetic_mapq_classes.py
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]  # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch07_mapq_multimapping as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403


def main():
    # ---- 与 demos --selftest Part 2 完全相同的合成流程（固定种子） ----
    rng = np.random.default_rng(demo.SEED)
    genome, copy_pos, unit_seqs = demo.make_genome_with_repeats(
        rng, 40000, 5, 1200, 150)
    reads, class_of = demo.make_reads(rng, genome, copy_pos, unit_seqs, 150,
                                      600)
    aln = demo.ToyAligner(genome)
    sc_per, sc_min = 0, int(-0.6 * 150 - 0.6)
    bwa_q, bt2_q = {}, {}
    mapq0_total = 0
    for read, cls in zip(reads, class_of):
        (_, s1, s2, known, sub_n, f_rep, t1, t2) = aln.score_read(read, 150)
        qb = demo.bwa_mem_mapq_se(score=s1, sub=s2 if known else 0,
                                  sub_n=sub_n, frac_rep=f_rep, l=150)
        qt = demo.bowtie2_mapq2(t1, t2 if known else None, sc_per, sc_min,
                                monotone=True)
        bwa_q.setdefault(cls, []).append(qb)
        bt2_q.setdefault(cls, []).append(qt)
        mapq0_total += (qb == 0)

    means_b = {c: float(np.mean(bwa_q[c])) for c in bwa_q}
    means_t = {c: float(np.mean(bt2_q[c])) for c in bt2_q}
    z_b = {c: 100.0 * np.mean([q == 0 for q in bwa_q[c]]) for c in bwa_q}
    assert {c: round(v, 2) for c, v in means_b.items()} == \
        {"unique": 60.0, "conserved": 0.0, "diverged": 11.0}, \
        f"bwa 均值 {means_b}"
    assert {c: round(v, 2) for c, v in means_t.items()} == \
        {"unique": 42.0, "conserved": 1.0, "diverged": 6.0}, \
        f"bt2 均值 {means_t}"
    assert z_b == {"unique": 0.0, "conserved": 100.0, "diverged": 0.0}, z_b
    assert mapq0_total == 600 and mapq0_total / 1800 == 1 / 3
    print(f"check: bwa 均值 60.00/0.00/11.00；bt2 均值 42.00/1.00/6.00；"
          f"MAPQ=0 {mapq0_total}/1800=33.3%")

    s = SVG(800, 700)

    # 绘图区：x 90–760，y 120–540（MAPQ 0–60，7 px/unit）
    yb, yt, x0 = 540, 120, 90
    cols = {"unique": 180, "conserved": 420, "diverged": 660}
    colors = {"unique": GREEN, "conserved": RED, "diverged": ORANGE}

    def yq(q):
        return yb - q * (yb - yt) / 60.0

    # 红横幅（顶部横贯）
    s.rect(40, 28, 740, 60, RED, rx=12)
    s.text(410, 66, "mapped 100%，MAPQ=0 占 600/1800＝33.3%", 30, WHITE,
           "middle", "bold")
    s.raw(f'<text x="22" y="330" font-family="{FONT}" font-size="30" '
          f'fill="{GRAY}" text-anchor="middle" font-weight="bold" '
          f'transform="rotate(-90 22 330)">bwa MAPQ</text>')
    s.text(100, 195, "全部比上", 32, INK, "start", "bold")

    # 轴与刻度
    s.line(x0, yb, 760, yb, GRAY, 5)
    s.line(x0, yb, x0, yt, GRAY, 5)
    for v in (0, 20, 40, 60):
        s.line(x0 - 8, yq(v), x0, yq(v), GRAY, 4)
        s.text(x0 - 14, yq(v) + 10, str(v), 30, GRAY, "end", "bold")

    # 三类散点（确定性抖动，固定种子）
    jrng = np.random.default_rng(20261103)
    for cls in ("unique", "conserved", "diverged"):
        for i, q in enumerate(bwa_q[cls]):
            jx = int(jrng.integers(-66, 67))
            s.circle(cols[cls] + jx, yq(q), 4.5, colors[cls])

    # 组均值（conserved 列由中文注记占位，均值 0.00 画在簇上方）
    s.text(180, 630, "mean 60.00", 30, GREEN, "middle", "bold")
    s.text(660, 630, "mean 11.00", 30, ORANGE, "middle", "bold")
    s.text(420, 496, "mean 0.00", 30, RED, "middle", "bold")
    s.text(420, 630, "三分之一位置不可区分", 30, INK, "middle", "bold")

    # bowtie2 对照小点（灰；diverged 偏到列右空区，避免压 conserved 均值）
    bt2v = {"unique": 42, "conserved": 1, "diverged": 6}
    bt2x = {"unique": 80, "conserved": 320, "diverged": 575}
    for cls in bt2v:
        bx = bt2x[cls]
        s.circle(bx, yq(bt2v[cls]), 7, GRAY)
        if cls == "diverged":
            s.text(bx + 24, yq(bt2v[cls]) + 10, "bt2", 30, GRAY, "start",
                   "bold")
        else:
            s.text(bx - 20, yq(bt2v[cls]) + 10, "bt2", 30, GRAY, "end",
                   "bold")

    # 类别名
    for cls in cols:
        s.text(cols[cls], 585, cls, 30, GRAY, "middle", "bold")


    s.save("11_synthetic_mapq_classes.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
