#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""14_discovery_unit_ld_inflation.py — 生成 14_discovery_unit_ld_inflation.svg
（FIG-P05-14：P31「发现单位是区域，不是单个 SNP」，cols 左栏）【data-plot】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-14（800×700，中文共 27 字）。
数据入口：`textbook/demos/ch21_thresholds_fwer_fdr.py` 部分 C（B=2000 块 ×
L=25 SNP、ρ=0.95、1 个因果块 nc=40、种子 20261104）：
  SNP 水平 BH(q=0.05) 报出 25 个「显著 SNP」；
  按块归并后只有 1 个独立位点；块内 Bonferroni + 跨块 BH 也只报 1 个位点。
本脚本用 demos 的 `bh_rejects()` 重放同一随机流（同种子同参数），三个数在
脚本内断言，改参数会当场失败。
图内中文严格取方案给定两句（16 + 11 = 27 字）；数字与 r²、q 为符号。
配色：红＝单 SNP 空间的重复计数（25 根），绿＝归并后的真实位点（1 个）。
依赖：numpy + scipy（同 demos）；无网络；种子固定。
用法：PYTHONDONTWRITEBYTECODE=1 python3 14_discovery_unit_ld_inflation.py
"""
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch21_thresholds_fwer_fdr as demo                      # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["单变异显著二十五块归并仅得一位点",     # 16
           "连锁搭便车虚报二十五倍"]             # 11
TEXT = "".join(PHRASES)

B, L, RHO, NC, SEED = 2000, 25, 0.95, 40.0, 20261104


def check_data():
    """与 demos 部分 C 同种子同参数的复算。"""
    rng = np.random.default_rng(SEED)
    u = rng.standard_normal(B)
    u[0] = rng.standard_normal() + np.sqrt(NC / RHO)
    z = np.sqrt(RHO) * np.repeat(u, L) + np.sqrt(1.0 - RHO) \
        * rng.standard_normal(B * L)
    p_all = 2.0 * stats.norm.sf(np.abs(z))
    rej = demo.bh_rejects(p_all, 0.05)
    n_snp = int(rej.sum())
    block_of = np.repeat(np.arange(B), L)
    n_block = int(np.unique(block_of[rej]).size)
    p_locus = np.minimum(1.0, L * p_all.reshape(B, L).min(axis=1))
    n_locus = int(demo.bh_rejects(p_locus, 0.05).sum())
    assert (n_snp, n_block, n_locus) == (25, 1, 1), (n_snp, n_block, n_locus)
    print(f"check: SNP 水平 {n_snp} 个显著、块归并 {n_block} 个位点、"
          f"合法位点检验 {n_locus} 个")
    return n_snp, n_block


def main():
    n_snp, n_block = check_data()
    s = SVG(800, 700, "Discovery unit: region, not single SNP", plan=TEXT)

    # ---------- 上排：单 SNP 空间的 25 个「显著 SNP」----------
    s.text(60, 78, "BH q=0.05", 30, GRAY, "start")
    x0 = 262
    for i in range(n_snp):
        s.rect(x0 + i * 19, 60, 13, 34, RED_TINT, RED, 3, rx=3)
    s.text(60, 140, f"{n_snp}", 40, RED, "start", "bold")
    s.text(120, 140, "significant SNP", 30, RED)

    # ---------- 中排：一个 LD 块，1 个因果变异拉 24 个标签 ----------
    s.rect(40, 186, 720, 176, CYAN_TINT, CYAN, 4, rx=12)
    s.rect(84, 236, 44, 60, ORANGE, None, 0, rx=6)
    for i in range(13):
        s.line(176 + i * 40, 236, 176 + i * 40, 296, CYAN, 4)
    s.line(140, 266, 680, 266, GRAY, 3, dash="10 7")
    s.text(106, 332, "causal", 30, ORANGE, "middle", "bold")
    s.text(600, 332, "r2 = 0.95", 30, CYAN_DEEP, "middle", "bold")

    # ---------- 下排：按块归并只有 1 个位点 ----------
    s.text(60, 428, "block", 30, GRAY, "start")
    s.rect(262, 402, 90, 44, GREEN_TINT, GREEN, 4, rx=6)
    s.text(60, 500, f"{n_block}", 40, GREEN, "start", "bold")
    s.text(120, 500, "locus", 30, GREEN)

    s.text(400, 590, PHRASES[0], 32, INK, "middle", "bold")
    s.text(400, 646, PHRASES[1], 32, RED, "middle", "bold")

    s.save("14_discovery_unit_ld_inflation.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 27, TEXT
    raise SystemExit(main())
