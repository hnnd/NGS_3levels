#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""18_contamination_linear_model.py — FIG-M07-20 混箱污染度线性增长模型（data-plot）

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-20（P36，`.cols` 一栏 800×700，data-plot）。
数据来源：`demos/ch19_checkm_contamination.py --selftest` 现跑输出；本脚本 import 同函数、同参数
（loci=100、reps=200、seed=20261104）复算并断言：
  S1 单基因组 95%：完整度 94.9%、污染度 0.0%（手算期望 95.0% / 0.0%）；
  S2 两基因组全合并：完整度 100.0%、污染度 100.0%；
  S3 三基因组全合并：完整度 100.0%、污染度 200.0%（红色 = 唯一警示处）。
**改横条**：三段场景名（单基因组／双基因组／三基因组）都是 5 个汉字，竖排三列必然横向相撞
（30 字号下每列需 ≥160px，三列再加条宽就出画布）；横排一行一个场景，左侧两行标签、
右侧 0–200% 同一标尺，读数与 demos 打印逐位一致（S1 完整度按 94.9% 打印）。
图内汉字 = 方案原句逐字，共 29 字（单基因组：零污染 / 双基因组：污染一百 /
三基因组：污染两百 / 非报错）。
无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 18_contamination_linear_model.py
"""
import contextlib
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]           # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch19_checkm_contamination as ck            # noqa: E402

from svghelp import *                              # noqa: F401,F403,E402

ROWS = (("单基因组：", "零污染", "S1 干净箱(一基因组95%)", GREEN),
        ("双基因组：", "污染一百", "S2 两基因组全合并", ORANGE),
        ("三基因组：", "污染两百", "S3 三基因组全合并", RED))


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        r = ck.run(100, 200, 20261104)
    s1, s2, s3 = (r[k] for *_, k, _ in ROWS)

    # 与 demos --selftest 同口径：图里只画这些数
    assert abs(s1["comp"] - 94.9) < 0.35 and s1["contam"] < 0.2
    assert abs(s2["comp"] - 100.0) < 0.2 and abs(s2["contam"] - 100.0) < 0.5
    assert abs(s3["comp"] - 100.0) < 0.2 and abs(s3["contam"] - 200.0) < 1.0
    assert abs(s3["contam"] - 2 * s2["contam"]) < 1.0

    s = SVG()

    L, R = 300, 700
    AX, YMAX = 132, 200.0
    BH, PITCH, Y0 = 58, 132, 232

    def xpos(v):
        return L + v / YMAX * (R - L)

    # 顶部 0–200% 标尺（污染度）
    s.line(L, AX, R, AX, INK, 4)
    for v in (0, 100, 200):
        s.line(xpos(v), AX, xpos(v), AX + 12, INK, 3)
        s.text(xpos(v), AX - 14, f"{v:g}%", 30, GRAY, "middle")

    for i, (head, tail, key, col) in enumerate(ROWS):
        d = r[key]
        y = Y0 + i * PITCH
        s.label(282, y + BH / 2, [head, tail], 30,
                RED if col == RED else BLUE, "end", "bold", leading=1.32)
        # 轨道与污染度条
        s.rect(L, y, R - L, BH, PANEL, rx=8)
        if d["contam"] > 0.5:
            s.rect(L, y, xpos(d["contam"]) - L, BH, col, rx=8)
        else:                                      # 零污染：只留一条底痕
            s.rect(L, y, 8, BH, col, rx=4)
        # 200% 会顶到右边界：满格数值改为写在条内右端（反白字）
        over = d["contam"] > 190
        s.text(xpos(d["contam"]) - (16 if over else -12),
               y + BH / 2 + 11, f"{d['contam']:.1f}%", 30,
               WHITE if over else (RED if col == RED else INK),
               "end" if over else "start", "bold")
        # 完整度字段用英文缩写 comp（黄金纪律：字段名可留英文，汉字总数守住 29）
        s.text(L + 6, y - 12, f"comp {d['comp']:.1f}%", 30, PURPLE, "start")

    s.text(700, 660, "非报错", 34, RED, "end", "bold")

    reds = s.save("18_contamination_linear_model.svg")
    print(f"check: S1 {s1['comp']:.1f}%/{s1['contam']:.1f}%；"
          f"S2 {s2['comp']:.1f}%/{s2['contam']:.1f}%；"
          f"S3 {s3['comp']:.1f}%/{s3['contam']:.1f}%（红 {reds} 处）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
