#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""02_mainline_data_funnel.py — 生成 02_mainline_data_funnel.svg
（FIG-P04-02：第 11 页 cols 一栏「主线数据四层漏斗与名义深度」）【new-svg】

方案：reviews/course/P04_FIGP_001.md §4 FIG-P04-02（P11，cols，800×700）。
依据：教材 §20.1 L14–17——贯穿数据集 PRJEB53625（稻瘟菌全球集合）经测序量
质控筛出 40 个唯一教学分离株，紧凑基因组约 40 Mb，实测 18.44 Gb，
名义深度 18.44 Gb / (40 Mb × 40) = 11.5×。
数字入口：`06_data/phd/manifests/p04_runs.tsv` 实测——40 个 run 的 `base_count`
落在 403 747 920–510 291 172（0.404–0.510 Gb），合计 18 441 762 641（18.44 Gb）；
`06_data/phd/README.md` p04 记「40 个分离株、base_count 0.4–1.5 Gb、约 11×
覆盖度」。本脚本直接读该清单核行数与合计，再按同一闭式重算名义深度
18.44 Gb / (40 Mb × 40) = 11.5×，不一致即失败退出；见回执核对表。
图内中文严格取方案给定 26 字（4 句）；`runs`、`Gb`、`Mb` 与数字属符号。
结构＝四级收敛漏斗（257 runs → 测序量档 → 40 株 18.44 Gb → 11.5×），
底部一条染色体尺标出 40 Mb 的紧凑基因组，再给一行可计算器复核的算式。
红色只标 40 这个样本量边界一处（本图没有警示句，故不画红底横幅）。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 02_mainline_data_funnel.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["全球集合筛选", "实测四十株单倍体", "紧凑基因组", "名义深度十一倍"]
TEXT = "".join(PHRASES)

RUNS, N_ISO, GB, GENOME_MB = 257, 40, 18.44, 40.0


MANIFEST = (Path(__file__).resolve().parents[3] / "06_data" / "phd"
            / "manifests" / "p04_runs.tsv")


def numbers():
    """与 06_data/phd/manifests/p04_runs.tsv 的实测口径对账。"""
    if MANIFEST.exists():
        rows = MANIFEST.read_text(encoding="utf-8").strip().splitlines()[1:]
        counts = [float(r.split("\t")[2]) for r in rows if r.strip()]
        if len(counts) != N_ISO:
            raise SystemExit(f"清单分离株数 {len(counts)} ≠ {N_ISO}")
        total_gb = sum(counts) / 1e9
        if abs(total_gb - GB) > 0.01:
            raise SystemExit(f"清单合计 {total_gb:.2f} Gb ≠ {GB}")
        if min(counts) < 0.4e9 or max(counts) > 1.5e9:
            raise SystemExit("清单 base_count 超出 0.4–1.5 Gb 档")
    depth = GB * 1e9 / (GENOME_MB * 1e6 * N_ISO)
    if abs(depth - 11.5) > 0.05:
        raise SystemExit(f"名义深度不一致：{depth:.2f}")
    return depth


def main():
    depth = numbers()
    s = SVG(800, 700, "Main dataset funnel", plan=TEXT)

    cx = 290
    stages = [
        (64, 430, BLUE_TINT, BLUE, f"{RUNS} runs", None, None),
        (160, 350, CYAN_TINT, CYAN_DEEP, "0.4–1.5 Gb", None, None),
        (256, 270, GREEN_TINT, GREEN, f"{GB} Gb", PHRASES[1], GREEN),
        (352, 190, ORANGE_TINT, ORANGE, f"{depth:.1f}×", PHRASES[3], ORANGE),
    ]
    for y, w, tint, edge, label, note, ncol in stages:
        s.wedge(cx, y, w, w - 26, 84, tint, edge, 4)
        s.text(cx, y + 54, label, 32, edge, "middle", "bold")
        if note:
            s.text(530, y + 53, note, 30, ncol, "start", "bold")
    s.text(530, 117, PHRASES[0], 30, BLUE, "start", "bold")

    # 样本量边界：40 株这一级右侧的红色计数
    s.text(378, 288, str(N_ISO), 30, RED, "start", "bold")

    # ---------- 底部：40 Mb 基因组尺 + 可复核算式 ----------
    s.text(60, 496, PHRASES[2], 30, BLUE, "start", "bold")
    s.rect(60, 514, 470, 30, BLUE_TINT, BLUE, 3, rx=15)
    s.text(552, 542, "40 Mb", 30, BLUE, "start", "bold")
    s.line(60, 580, 740, 580, PANEL, 3)
    s.text(400, 634, f"{GB} Gb ÷ (40 Mb × {N_ISO}) = {depth:.1f}×", 30,
           GRAY, "middle")

    s.save("02_mainline_data_funnel.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 26, TEXT
    raise SystemExit(main())
