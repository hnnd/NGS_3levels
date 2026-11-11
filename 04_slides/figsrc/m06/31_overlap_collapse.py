#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""31_overlap_collapse.py — FIG-M06-31 失效一：重叠不足导致的合并崩溃合成对照（data-plot）

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-31（P55，cols 一栏 800×700，data-plot）。
数据来源：`demos/ch18_overlap_trunclen.py --selftest` 现跑输出（本脚本 import 同函数、同参数复算
并断言）：S1（V4 240/200，重叠 187 bp）过滤 F 99.5%、合并 99.0%；S3（V3–V4 230/230，重叠 0 bp）
过滤 F 99.8%、合并 5.78%。两组在过滤一步几乎没有差别（Δ = 0.003），合并却差 17 倍，
且流程不报错 —— 「五列全绿、只有 merged 塌了」的合成版。
图内汉字 = 方案原句逐字，共 20 字（前四步几乎全绿 / 仅合并骤降至半成 / 静默无报错）；
其余为步骤名、场景代号、重叠值与百分比。红色只用于崩塌这一件事（红柱 + 红色 5.78%）。
无网络；随机数经 demos 同种子（20261104）复算。
用法：PYTHONDONTWRITEBYTECODE=1 python3 31_overlap_collapse.py
"""
import contextlib
import io
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]           # NGS_3Levels/
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import ch18_overlap_trunclen as ov                  # noqa: E402

from svghelp import *                              # noqa: F401,F403,E402


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        r = ov.run(20000, 2.0, 12, 20, 20261104)
    s1 = r["S1 V4 正常"]
    s3 = r["S3 V3-V4 截尾过度"]

    assert s1["overlap"] == 187 and s1["merged"] > 0.6, s1
    assert s3["overlap"] == 0 and s3["merged"] < 0.10, s3
    assert abs(s1["keep_f"] - s3["keep_f"]) < 0.05, (s1["keep_f"], s3["keep_f"])
    assert s1["merged"] > 10 * s3["merged"], s3["merged"]
    ratio = s1["merged"] / s3["merged"]
    print(f"check: S1 过滤F {100*s1['keep_f']:.1f}% / 合并 {100*s1['merged']:.1f}%；"
          f"S3 过滤F {100*s3['keep_f']:.1f}% / 合并 {100*s3['merged']:.2f}%；"
          f"Δ过滤 {abs(s1['keep_f']-s3['keep_f']):.3f}，合并比 {ratio:.0f}×")

    s = SVG()

    # 两块面板，各四根横条（轨道 = 0→100%）；横条比竖条好放标签，长步骤名不压字
    X0, X1 = 352, 656            # 条形起点、100% 位置
    STEPS = ["filtered", "denoisedF", "denoisedR", "merged"]
    H, PITCH = 30, 38

    def vals(res):
        return [res["keep_f"], res["keep_f"], res["keep_r"], res["merged"]]

    for y_top, code, overlap, res in ((146, "S1", 187, s1), (364, "S3", 0, s3)):
        s.text(X0, y_top - 40, f"{code}  ·  O = {overlap} bp", 30, INK, "start", "bold")
        vs = vals(res)
        for i, v in enumerate(vs):
            y = y_top + i * PITCH
            collapse = (i == 3 and code == "S3")
            s.rect(X0, y, X1 - X0, H, PANEL, rx=5)
            s.rect(X0, y, max(v * (X1 - X0), 7), H, RED if collapse else GREEN, rx=5)
            s.text(X0 - 16, y + 25, STEPS[i], 30, GRAY, "end")
            s.text(X1 + 14, y + 25,
                   f"{100*v:.2f}%" if collapse else f"{100*v:.1f}%",
                   30, RED if collapse else INK, "start", "bold")
        if code == "S1":
            y1 = y_top + 3 * PITCH + 15          # merged 一行的竖直中点
        else:
            y3 = y_top + 3 * PITCH + 15

    # 合并保留的落差（17 倍）：两次 merged 之间竖向下行箭头（左侧留白处，不碰任何标签）
    s.arrow(168, y1, 168, y3 - 12, ORANGE_DEEP, 5, 15)
    s.text(148, (y1 + y3) / 2 + 11, f"{ratio:.0f}×", 32, ORANGE_DEEP, "end", "bold")

    # 图内原句三句（底部逐句一行）
    s.bottom(["前四步几乎全绿", ("仅合并骤降至半成", ORANGE_DEEP, "bold"),
              ("静默无报错", INK, "bold")], y=566, gap=40, size=32)

    s.save("31_overlap_collapse.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
