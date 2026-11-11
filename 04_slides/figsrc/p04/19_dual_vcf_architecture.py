#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_dual_vcf_architecture.py — 生成 19_dual_vcf_architecture.svg
（FIG-P04-19：第 38 页 cols 一栏「双产物物理分流架构」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-19（P38，cols，800×700）。
依据：教材 §20.4.7 的产物表——两套产物都从同一个 `gtmask.vcf.gz` 分出，后者已
完成双等位 SNP 提取与低质量基因型置缺失（DP < 5 或 GQ < 20 置缺失、不删位点）；
`popgen.vcf.gz` 只做 `--max-missing 0.8`、**不滤 MAF**，服务 π、θ_W、D_T、SFS；
`struct.vcf.gz` 做 `--max-missing 0.9 --maf 0.05`，服务 LD 剪枝、PCA、ADMIXTURE、
TreeMix 与第 21 章 GWAS。物理持久化两套，绝不拿滤过 MAF 的产物跑多样性。
图内中文严格取方案给定 29 字（4 句）；文件名、参数与数字属符号。
结构＝Y 型分流：顶端底座 → 分流节点（物理分流）→ 左右两条产物，各自列出参数
与下游用途，绿色分支标「多样性绝对不滤次频」。
红只标「多样性绝对不滤次频」一处。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 19_dual_vcf_architecture.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["同底座提取双等位", "多样性绝对不滤次频", "结构关联滤点零五", "物理分流"]
TEXT = "".join(PHRASES)


def main():
    s = SVG(800, 700, "Two physically separate VCF products", plan=TEXT)

    # ---------- 底座 ----------
    s.rect(250, 56, 300, 84, BLUE_TINT, BLUE, 4, rx=12)
    s.text(400, 108, "gtmask.vcf.gz", 32, BLUE, "middle", "bold")
    s.text(380, 178, PHRASES[0], 30, BLUE, "end", "bold")

    # ---------- 分流 ----------
    s.line(400, 140, 400, 214, BLUE, 4)
    s.line(200, 214, 600, 214, BLUE, 4)
    s.line(200, 214, 200, 250, GREEN, 5)
    s.line(600, 214, 600, 250, BLUE, 5)
    s.chip(400, 214, PHRASES[3], 30, WHITE, BLUE, BLUE, pad=16, anchor="middle")

    # ---------- 左：popgen ----------
    s.rect(58, 250, 284, 186, GREEN_TINT, GREEN, 4, rx=12)
    s.text(200, 302, "popgen.vcf.gz", 30, GREEN, "middle", "bold")
    s.text(200, 350, "--max-missing 0.8", 30, INK, "middle")
    s.text(200, 398, "MAF: off", 30, GREEN, "middle", "bold")

    # ---------- 右：struct ----------
    s.rect(458, 250, 284, 186, BLUE_TINT, BLUE, 4, rx=12)
    s.text(600, 302, "struct.vcf.gz", 30, BLUE, "middle", "bold")
    s.text(600, 350, "--max-missing 0.9", 30, INK, "middle")
    s.text(600, 398, "--maf 0.05", 30, BLUE, "middle", "bold")

    # ---------- 产物判读 ----------
    s.text(200, 500, PHRASES[1], 30, RED, "middle", "bold")
    s.text(600, 500, PHRASES[2], 30, BLUE, "middle", "bold")

    # ---------- 下游用途 ----------
    s.text(200, 566, "π · θ_W · D_T · SFS", 30, GREEN, "middle")
    s.text(600, 566, "LD · PCA · ADMIXTURE", 30, BLUE, "middle")

    s.save("19_dual_vcf_architecture.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 29, TEXT
    raise SystemExit(main())
