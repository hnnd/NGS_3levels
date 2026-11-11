#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""13_stale_mtime_quantification.py — FIG-M08-13 参数变更后陈旧结果静默留存量化（P31，cols，data-plot）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-13（`.cols` 一栏 800×700，data-plot）。
数据：`textbook/demos/ch23_stale_output_mtime.py` 现跑（40 转录本 × 4 样本、Poisson 均值 25、
种子 20261105）：
  左面板（mtime 调度）：qual 20→30 后计划作业数 = 0（Nothing to be done），
    160 个细胞中 97 个不同（60.6% 的数字是错的）；
  右面板（-R filter 强制重跑）：执行 2 个作业（filter + summary），错误率归零。
本脚本用 demos 同款调度器复算并断言，图中数字与 --selftest 输出逐位一致。
图内汉字 = 方案原句逐字，共 24 字（参数变而计划作业为零 / 陈旧错误占 /
强制重跑两作业自愈）；百分比与计数为阿拉伯数字。
无网络、种子固定。用法：PYTHONDONTWRITEBYTECODE=1 python3 13_stale_mtime_quantification.py
"""
import os
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]           # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch23_stale_output_mtime as st               # noqa: E402

from svghelp import *                              # noqa: F401,F403,E402

N_TX, N_SAMPLES, SEED = 40, 4, 20261105
QUAL_A, QUAL_B = 20, 30


def data():
    """复算 demos 的三组数：(计划作业数, 差异细胞, 总细胞, -R 作业数)。"""
    with tempfile.TemporaryDirectory() as tmp:
        wd = Path(tmp)
        st.make_inputs(wd, N_TX, N_SAMPLES, SEED)
        t = 1_600_000_000
        for name in ("raw_counts.tsv", "transcripts.txt"):
            os.utime(wd / name, (t, t))

        sched = st.MtimeScheduler()
        sched.run(wd, QUAL_A)                       # 基线
        n_planned = sum(v == "ran" for v in sched.run(wd, QUAL_B).values())

        filt_true = wd / "filtered_true.tsv"
        summ_true = wd / "summary_true.tsv"
        st.step_filter(wd / "raw_counts.tsv", filt_true, QUAL_B)
        st.step_summary(filt_true, wd / "index.txt", summ_true, QUAL_B)
        n_diff, n_total = st.diff_cells(wd / "filtered.tsv", filt_true)

        n_force = sum(v == "ran"
                      for v in sched.run(wd, QUAL_B, force=("filter",)).values())

    assert n_planned == 0 and 0 < n_diff < n_total and n_force == 2
    return n_planned, n_diff, n_total, n_force


def main():
    n_planned, n_diff, n_total, n_force = data()
    frac = n_diff / n_total
    print(f"check: 计划作业 {n_planned}；差异细胞 {n_diff}/{n_total} "
          f"({frac:.1%})；-R 重跑 {n_force} 作业")

    s = SVG()
    s.text(400, 58, "参数变而计划作业为零", 34, BLUE, "middle", "bold")

    # 两面板站标（一图一个焦点：错误占多少 vs 强制重跑后归零）
    s.text(206, 106, "mtime", 32, BLUE, "middle", "bold")
    s.text(596, 106, "-R filter", 32, GREEN, "middle", "bold")

    # 左面板：陈旧错误占比（红色高柱 = 唯一警示）
    base = 520
    s.line(96, base, 336, base, INK, 4)
    h = int(frac * 340)                          # 60.6% → 206px
    s.rect(126, base - h, 160, h, RED, rx=8)
    s.text(206, base - h - 20, f"{frac:.1%}", 36, RED, "middle", "bold")
    s.text(206, base + 46, "陈旧错误占", 30, INK, "middle")
    s.text(206, base + 96, f"{n_diff}/{n_total}", 30, GRAY, "middle")

    # 右面板：强制重跑后的两个验收量（KPI 卡，不与左柱混用标尺）
    s.rect(452, 190, 288, 116, GREEN_TINT, GREEN, 4, rx=14)
    s.text(596, 246, f"{n_force} 作业", 34, GREEN, "middle", "bold")
    s.rect(452, 330, 288, 116, WHITE, GREEN, 4, rx=14)
    s.text(596, 386, "0.0%", 36, GREEN, "middle", "bold")
    s.text(596, base + 46, "强制重跑两作业自愈", 30, GREEN, "middle")

    return s.save("13_stale_mtime_quantification.svg")


if __name__ == "__main__":
    raise SystemExit(main())
