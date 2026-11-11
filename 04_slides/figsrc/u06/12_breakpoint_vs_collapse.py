#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_breakpoint_vs_collapse.py — 生成 12_breakpoint_vs_collapse.svg
（FIG-U06-12：回贴深度——断点骤降 vs 塌缩约 2×）

方案：reviews/course/U06_FIGP_001.md §4 FIG-U06-12（P34，cols 一栏，800×700）。
数据：定性合成示意（无实测坐标）；2× 口径＝两拷贝塌缩「约 2×」
（教材 §8.4.8 L297、§8.5.1 L379）；「低深度或过滤后可能不出现」同 L274–276。
图注标「合成示意」；不得画出具体样本实测曲线。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 12_breakpoint_vs_collapse.py
"""
from svghelp import *  # noqa: F401,F403


def track(s, y_flat, y_ano, x_drop, x_recover, label_x, label_y, mode):
    """回贴深度轨道：平稳段（深蓝）+ 异常段（红）。mode: 'drop' 或 'step'。"""
    s.line(60, y_flat, 740, y_flat, GRAY, 3, dash="8 8")
    if mode == "drop":
        pts = [(60, y_flat), (x_drop, y_flat), (x_drop, y_ano),
               (x_recover, y_ano), (x_recover, y_flat), (740, y_flat)]
    else:
        pts = [(60, y_flat), (x_drop, y_flat), (x_drop, y_ano),
               (x_recover, y_ano), (x_recover, y_flat), (740, y_flat)]
    s.polyline(pts, BLUE, 6)
    # 红色异常段（关键事件）
    if mode == "drop":
        s.line(x_drop, y_flat, x_drop, y_ano, RED, 8, cap="round")
        s.line(x_drop, y_ano, x_recover, y_ano, RED, 8, cap="round")
        s.line(x_recover, y_ano, x_recover, y_flat, RED, 8, cap="round")
        s.text((x_drop + x_recover) / 2, y_ano - 18, "0", 30, RED, "middle",
               "bold")
    else:
        s.line(x_drop, y_flat, x_drop, y_ano, RED, 8, cap="round")
        s.line(x_drop, y_ano, x_recover, y_ano, RED, 8, cap="round")
        s.line(x_recover, y_ano, x_recover, y_flat, RED, 8, cap="round")
        # ≈2× 双箭头
        xm = (x_drop + x_recover) / 2
        s.line(xm - 30, y_ano, xm - 30, y_flat, RED, 4)
        s.polygon([(xm - 30, y_ano), (xm - 38, y_ano + 12),
                   (xm - 22, y_ano + 12)], RED)
        s.polygon([(xm - 30, y_flat), (xm - 38, y_flat - 12),
                   (xm - 22, y_flat - 12)], RED)
    s.text(label_x, label_y, label_txt[mode], 32, INK, "start", "bold")


label_txt = {"drop": "断点：骤降、跨越读段消失", "step": "塌缩：≈2×"}


def main():
    s = SVG(800, 700)

    # 上轨：断点——骤降到 0
    track(s, y_flat=190, y_ano=275, x_drop=330, x_recover=470,
          label_x=60, label_y=120, mode="drop")

    # 下轨：塌缩——阶跃升到约 2×
    track(s, y_flat=470, y_ano=400, x_drop=330, x_recover=470,
          label_x=60, label_y=372, mode="step")

    # 灰色结论行 + 合成示意标注
    s.text(400, 616, "低深度或过滤后可能不出现", 30, GRAY, "middle", "bold")
    s.text(400, 668, "合成示意", 30, GRAY, "middle")

    s.save("12_breakpoint_vs_collapse.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
