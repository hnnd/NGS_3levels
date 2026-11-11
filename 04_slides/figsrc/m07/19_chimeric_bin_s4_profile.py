#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""19_chimeric_bin_s4_profile.py — FIG-M07-21 残缺基因组部分嵌合的 S4 形态（data-plot）

方案：textbook/reviews/course/M07_FIGP_001.md §4 FIG-M07-21（P37，`.cols` 一栏 800×700，data-plot）。
数据来源：`demos/ch19_checkm_contamination.py --selftest` 现跑输出；本脚本 import 同函数、同参数
（loci=100、reps=200、seed=20261104）复算并断言 S4（f_A/f_B/f_C = 0.88/0.85/0.75）：
  完整度 99.5%、污染度 148.0%（三个残缺基因组互补：座位几乎全被覆盖，重叠处又堆出超额副本）。
两条标尺各自独立（完整度 0–100%、污染度 0–200%），同图并排但**不能相加**，正是本页要讲的
「又缺又多」；条顶数值一位小数，与 demos 打印逐位一致。
下方片段轴：三块残缺片段各覆盖一部分座位，交叠区即超额副本的来源（示意，不给份数比例，
比例无入口）。「满格 100%/200%」为轴上限说明，非实测数字。
图内汉字 = 方案原句逐字，共 28 字（完整度近满：九成九 / 污染度爆表：一百四十八 /
残缺互补又缺又多）。
无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 19_chimeric_bin_s4_profile.py
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

KEY = "S4 部分合并(88%/142%型)"


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        r = ck.run(100, 200, 20261104)
    d = r[KEY]

    # 与 demos --selftest 同口径：图里只画这两个数
    assert abs(d["comp"] - 99.5) < 0.4
    assert abs(d["contam"] - 148.0) < 1.5
    assert d["contam"] > 100                    # 污染度破百是本图要点
    assert d["comp"] > 90                       # 完整度看似极佳

    s = SVG()

    # ---------------- 上：两条独立标尺 ----------------
    L, R = 316, 700
    ROWS = (("完整度近满：", "九成九", d["comp"], 100.0, GREEN),
            ("污染度爆表：", "一百四十八", d["contam"], 200.0, RED))
    for i, (head, tail, val, vmax, col) in enumerate(ROWS):
        y = 176 + i * 172
        s.label(298, y + 32, [head, tail], 30, col, "end", "bold", leading=1.34)
        s.rect(L, y, R - L, 64, PANEL, rx=10)
        w = max((R - L) * val / vmax, 6)
        s.rect(L, y, w, 64, col, rx=10)
        s.text(R, y - 14, f"满格 {vmax:g}%", 30, GRAY, "end")
        s.text(L + w - 16, y + 43, f"{val:.1f}%", 30, WHITE, "end", "bold")

    # ---------------- 下：座位轴 + 三块残缺片段 ----------------
    AX_L, AX_R, AX_Y = 96, 704, 446
    s.line(AX_L, AX_Y, AX_R, AX_Y, INK, 4)         # 座位轴（0 → M）
    for i in range(11):
        x = AX_L + i * (AX_R - AX_L) / 10
        s.line(x, AX_Y, x, AX_Y + 10, GRAY, 3)

    SEGS = ((0.00, 0.62, GREEN, GREEN_TINT),
            (0.26, 0.88, CYAN_DEEP, CYAN_TINT),
            (0.58, 1.00, ORANGE_DEEP, ORANGE_TINT))
    SPAN = AX_R - AX_L

    # 交叠区（超额副本来源）：只在三块片段两两相叠的竖向区间打浅红底（不加文字）
    for f0, f1 in ((0.26, 0.62), (0.58, 0.88)):
        s.rect(AX_L + f0 * SPAN, AX_Y + 18, (f1 - f0) * SPAN, 126,
               RED_TINT, rx=6)

    for k, (f0, f1, edge, tint) in enumerate(SEGS):
        y = AX_Y + 24 + k * 40
        s.rect(AX_L + f0 * SPAN, y, (f1 - f0) * SPAN, 30, tint, edge, 3, rx=10)

    s.text(400, 648, "残缺互补又缺又多", 34, RED, "middle", "bold")

    reds = s.save("19_chimeric_bin_s4_profile.svg")
    print(f"check: S4 {d['comp']:.1f}%/{d['contam']:.1f}%（红 {reds} 处）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
