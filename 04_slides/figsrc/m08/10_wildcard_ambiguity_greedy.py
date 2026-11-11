#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""10_wildcard_ambiguity_greedy.py — FIG-M08-10 通配符贪婪吞路径与双重匹配歧义率（P24，cols，data-plot）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-10（`.cols` 一栏 800×700，data-plot）。
数据：`textbook/demos/ch23_wildcard_ambiguity.py` 现跑（500 个随机目标，种子 20261105）：
  左面板（贪婪吞路径）：目标 `results/clean/CK_1_1.fq.gz` 无约束绑定 `sample='clean/CK_1'`
    （含 `/`）vs 加字符集约束后匹配数 0；
  右面板（批量歧义率）：同前缀救援规则 500/500（100.0%）vs 异前缀 0/500（0.0%）。
本脚本 import 同函数复算并断言，图中数字与 --selftest 输出逐位一致。
图内汉字 = 方案原句逐字，共 26 字（贪婪吞路径含斜杠 / 同前缀歧义率 /
异前缀歧义率 / 唯一前缀根治）；百分比与计数为阿拉伯数字。
无网络、种子固定。用法：PYTHONDONTWRITEBYTECODE=1 python3 10_wildcard_ambiguity_greedy.py
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]           # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch23_wildcard_ambiguity as wc               # noqa: E402

from svghelp import *                              # noqa: F401,F403,E402

N_TARGETS, SEED = 500, 20261105


def data():
    """复算 demos 的三个关键数，返回 (绑定值, 约束后匹配数, 同前缀率, 异前缀率)。"""
    target_b = "results/clean/CK_1_1.fq.gz"
    pat_b = "results/{sample}_1.fq.gz"
    free = wc.match_rules(target_b, [pat_b])
    con = wc.match_rules(target_b, [pat_b], constrained=True)

    targets = wc.make_targets(N_TARGETS, SEED)
    same = ["results/quant/{sample}/quant.sf", "results/{sample}/quant.sf"]
    diff = ["results/quant/{sample}/quant.sf", "results/rescue/{sample}/quant.sf"]
    n_same = sum(1 for t in targets if len(wc.match_rules(t, same)) >= 2)
    n_diff = sum(1 for t in targets if len(wc.match_rules(t, diff)) >= 2)

    # 与 --selftest 同口径断言
    assert free and "/" in free[0][1], "无约束时应吞下 '/'"
    assert len(con) == 0, "约束后匹配数应为 0"
    assert n_same == N_TARGETS, "同前缀歧义率应为 500/500"
    assert n_diff == 0, "异前缀歧义率应为 0/500"
    return free[0][1], len(con), n_same / N_TARGETS, n_diff / N_TARGETS


def main():
    bound, n_con, r_same, r_diff = data()
    print(f"check: 绑定 sample={bound!r}；约束后匹配 {n_con}；"
          f"同前缀 {r_same:.1%}；异前缀 {r_diff:.1%}")

    s = SVG()
    s.text(400, 58, "贪婪吞路径含斜杠", 34, BLUE, "middle", "bold")

    # 左面板：无约束 vs 加约束（同一目标的匹配数对照，靠颜色区分状态）
    s.rect(46, 82, 708, 236, WHITE, PANEL, 3, rx=14)
    s.text(96, 126, "results/clean/CK_1_1.fq.gz", 30, GRAY, "start")
    rows = [("sample=clean/CK_1", RED, RED_TINT, 158),
            ("match = 0 (constrained)", GREEN, GREEN_TINT, 236)]
    for val, ink, tint, y in rows:
        s.rect(70, y, 660, 66, tint, ink, 4, rx=10)
        s.text(400, y + 44, val, 30, ink, "middle", "bold")

    # 右面板：500 个随机目标的歧义率双柱
    base = 552
    s.line(96, base, 704, base, INK, 4)
    bars = [("同前缀歧义率", r_same, RED, 250), ("异前缀歧义率", r_diff, GREEN, 512)]
    for lab, frac, col, cx in bars:
        h = max(int(frac * 200), 5)
        s.rect(cx - 76, base - h, 152, h, col, rx=8)
        s.text(cx, base - h - 16, f"{frac:.1%}", 32, col, "middle", "bold")
        s.text(cx, base + 46, lab, 30, INK, "middle")

    # 底部结论（绿）
    s.text(400, 668, "唯一前缀根治", 34, GREEN, "middle", "bold")

    return s.save("10_wildcard_ambiguity_greedy.svg")


if __name__ == "__main__":
    raise SystemExit(main())
