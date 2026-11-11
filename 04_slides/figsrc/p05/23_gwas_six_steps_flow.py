#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""23_gwas_six_steps_flow.py — 生成 23_gwas_six_steps_flow.svg
（FIG-P05-23：P44「流程骨架：六步」，cols 左栏）【new-svg】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-23（800×700，中文共 26 字）。
依据：教材 §21.4 全节与讲义 ⑤ 的操作顺序——① 表型治理（RINT／BLUE-BLUP／
遗传力闸门）② 质控清洗（maf 0.05／geno 0.1／mind 0.1、HWE 关）③ 结构：Q
（主成分）与 K（亲缘矩阵）④ 关联（GLM 对照 + MLM 扫描）⑤ 分步诊断
（QQ → λ → 曼哈顿）⑥ 后 GWAS 候选挖掘（clump 归并 → 半衰外延 →
bedtools intersect 取基因）。重算一律投递作业调度，资产要在当前数据集上重算。
图内中文严格取方案给定三句（10 + 8 + 8 = 26 字）：第一句拆成四步标签，
第二句拆成后两步；数字编号为序号，不占汉字预算。
配色：深蓝＝主流程框，青蓝＝数据流箭头；红色只标「全链计算作业调度」一处。
无网络；不涉及随机数（纯流程示意，无计算结果）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 23_gwas_six_steps_flow.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["治理质控结构混合关联",   # 10
           "分步诊断候选挖掘",      # 8
           "全链计算作业调度"]       # 8
TEXT = "".join(PHRASES)

ROW1 = ["治理", "质控", "结构混合", "关联"]
ROW2 = ["分步诊断", "候选挖掘"]


def main():
    s = SVG(800, 700, "Six-step GWAS pipeline", plan=TEXT)

    # ---------- 第一排：四步 ----------
    w, h, gap = 168, 116, 16
    x0 = 40
    for i, label in enumerate(ROW1):
        x = x0 + i * (w + gap)
        s.rect(x, 60, w, h, BLUE_TINT, BLUE, 4, rx=12)
        s.text(x + w / 2, 112, f"{i + 1}", 30, GRAY, "middle")
        s.text(x + w / 2, 156, label, 32, BLUE, "middle", "bold")
        if i < 3:
            s.arrow(x + w + 2, 118, x + w + gap - 2, 118, CYAN_DEEP, 4, 12)

    # ---------- 第二排：两步 ----------
    s.arrow(400, 176, 400, 218, CYAN_DEEP, 5, 13)
    for i, label in enumerate(ROW2):
        x = 40 + i * (348 + 24)
        s.rect(x, 220, 348, h, CYAN_TINT, CYAN_DEEP, 4, rx=12)
        s.text(x + 40, 262, f"{i + 5}", 30, GRAY, "middle")
        s.text(x + 190, 300, label, 32, CYAN_DEEP, "middle", "bold")

    # ---------- 纪律：计算走作业调度（唯一红色警示）----------
    s.rect(40, 376, 720, 118, RED_TINT, RED, 4, rx=14)
    s.text(400, 446, PHRASES[2], 32, RED, "middle", "bold")

    # ---------- 收尾说明（不占汉字预算）----------
    s.text(400, 544, "phenotype → QC → Q+K", 30, GRAY, "middle")
    s.text(400, 592, "→ GLM/MLM → QQ·λ → clump", 30, GRAY, "middle")
    s.text(400, 640, "qsub ／ recompute on sativas413", 30, GRAY, "middle")

    s.save("23_gwas_six_steps_flow.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 26, TEXT
    assert "".join(ROW1) == PHRASES[0] and "".join(ROW2) == PHRASES[1]
    raise SystemExit(main())
