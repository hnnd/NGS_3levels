#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""20_annotation_bias_false_specific.py — 生成 20_annotation_bias_false_specific.svg
（FIG-U08-20：注释流程不统一制造假特异基因暴涨）

方案：reviews/course/U08_FIGP_001.md §4 FIG-U08-20（P61，cols 一栏，800×700）【data-plot】。
数据（与 demos 现跑一致）：demos/ch11_annotation_bias.py run_panel(seed=20261104)
——统一注释（12 株全 P1）各株特异家族 1,629–1,657（中位约 1,640）；
混入 1 株宽松注释（第 12 株 P2）后特异家族暴至 8,150，其中背景噪声 ORF 7,919 ＋
真基因漏检 221 ＋ 真实株特异 10，假特异占比 99.9%（教材 §11.5.1、§9.5.2）。
无网络；种子固定。用法：PYTHONDONTWRITEBYTECODE=1 python3 20_annotation_bias_false_specific.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "textbook"
                       / "demos"))
import ch11_annotation_bias as demo  # noqa: E402

from svghelp import *  # noqa: F401,F403,E402


def main():
    # 注：demo 的 run_panel 仅在 verbose=True 时计算 n_noise12 等分解量
    # （verbose=False 分支在 demo 内即 UnboundLocalError），故用默认 verbose。
    r = demo.run_panel(seed=20261104)
    uni = r["uni_spec"]
    hot = r["mix_spec"][11]
    med = sorted(uni)[len(uni) // 2 - 1: len(uni) // 2 + 1]
    med = sum(med) / len(med)
    fake = r["n_noise12"] + r["n_miss"]
    share = fake / hot
    # —— 数据复核（与 U08_FIGP_001 §0 demos 现跑输出一致）——
    assert 1629 <= min(uni) and max(uni) <= 1657, f"统一面板特异应 1629–1657：{uni}"
    assert abs(med - 1640) <= 8, f"中位应约 1640：{med}"
    assert hot == 8150, f"混入 P2 后第 12 株特异应 8150：{hot}"
    assert abs(share - 0.999) < 2e-3, f"假特异占比应 99.9%：{share:.1%}"
    print(f"check: 统一注释特异 {min(uni)}–{max(uni)}（中位 {med:.0f}）；"
          f"混入 1 株宽松注释 → 特异 {hot}；假特异 {share:.1%}"
          f"（{r['n_noise12']} 噪声 ＋ {r['n_miss']} 漏检 ＋ {r['n_real']} 真实）")

    s = SVG(800, 700)
    X0, Y0, Y1 = 90, 170, 540
    hmax = 8150.0
    H = Y1 - Y0

    def bh(v):
        return H * v / hmax

    # 左组标题（统一注释）
    s.text(X0, 66, f"统一注释：特异约 {med:.0f}", 34, BLUE, "start", "bold")
    # 右组标题（混入 1 株宽松注释；右对齐于红柱上方）
    s.text(760, 116, f"混入宽松注释：特异 {hot}", 34, INK, "end", "bold")

    # 11 根深蓝矮柱（统一注释 P1）
    bw, gap = 26, 10
    for j, v in enumerate(uni[:11]):
        x = X0 + j * (bw + gap)
        s.rect(x, Y1 - bh(v), bw, bh(v), BLUE, rx=3)
    # 中位虚线
    s.line(X0 - 10, Y1 - bh(med), X0 + 11 * (bw + gap) - gap + 10,
           Y1 - bh(med), GRAY, 3, dash="12 9")
    s.text(X0 + 5 * (bw + gap), Y1 - bh(med) - 16, "median", 30, GRAY,
           "middle")
    # 第 12 根红色巨柱（混入 P2；唯一红＝巨柱）
    x12 = X0 + 11 * (bw + gap) + 40
    s.rect(x12, Y0, 90, Y1 - Y0, RED, rx=4)

    # 基线与株号标注（ASCII）
    s.line(X0 - 14, Y1, x12 + 104, Y1, INK, 3)
    s.text(X0, Y1 + 44, "strain 1–11 (P1)", 30, GRAY, "start")
    s.text(x12 + 45, Y1 + 44, "strain 12 (P2)", 30, GRAY, "middle")

    # 分解气泡（深灰；红仅巨柱）
    s.rect(360, 600, 400, 56, WHITE, PANEL, 3, rx=12)
    s.text(560, 638, f"假特异 {share:.1%}", 32, INK, "middle", "bold")
    s.text(400, 682, f"{r['n_noise12']:,} 噪声 ORF ＋ {r['n_miss']} 漏检真基因"
           f" ＋ {r['n_real']} 真实", 30, GRAY, "middle")

    s.save("20_annotation_bias_false_specific.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
