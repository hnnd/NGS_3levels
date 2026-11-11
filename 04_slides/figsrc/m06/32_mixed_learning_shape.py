#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""32_mixed_learning_shape.py — FIG-M06-32 错误模型混学形态对比

方案：textbook/reviews/course/M06_FIGP_001.md §4 FIG-M06-32（P56，cols 一栏
800×700，new-svg）。
教材依据：§18.5.2（单 run 学到的模型紧贴实测；把两个测序批次的数据混在一起学，
拟合线被横向拉平、同时偏离两批各自的实测，两端都失真）。
图内汉字 = 方案原句逐字，共 21 字（单批次紧密贴合 / 混学散布脱离拟合 / 模型两头失真）；
其余标注为 Q 值、err_F.pdf 字段名与坐标刻度。
无网络、无随机数。用法：PYTHONDONTWRITEBYTECODE=1 python3 32_mixed_learning_shape.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403
from svghelp import BLUE, CYAN, GRAY, INK, RED, SVG, WHITE

QS = [10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40]
PW, PH, PY = 336, 410, 90


def qx(x0, x1, q):
    return x0 + (q - 10) / 30 * (x1 - x0)


def panel(s, x, title, mixed):
    s.rect(x, PY, PW, PH, WHITE, BLUE, 4, rx=16)
    s.text(x + PW / 2, PY + 44, title, 32, INK, "middle", "bold")
    x0, x1 = x + 44, x + PW - 40
    ytop, ybase = PY + 92, PY + 318

    s.line(x0, ytop, x0, ybase, BLUE, 4)
    s.line(x0, ybase, x1, ybase, BLUE, 4)
    for q in (10, 20, 30, 40):
        px = qx(x0, x1, q)
        s.line(px, ybase, px, ybase + 9, BLUE, 3)
        s.text(px, ybase + 36, str(q), 30, GRAY, "middle")
    s.text(x + PW / 2, PY + 386, "Q", 30, GRAY, "middle", "bold")

    # 理论期望线（青蓝虚线）：Q 越高错误率越低
    s.line(x0 + 6, ytop + 4, x1 - 6, ybase - 22, CYAN, 4, dash="11 8")

    if mixed:
        # 混学拟合线被拉平（红：唯一警示），两端同时脱离两批实测
        s.line(x0 + 6, ytop + 64, x1 - 6, ytop + 112, RED, 7)
        for i, q in enumerate(QS):
            px = qx(x0, x1, q)
            base = ytop + 64 + i * 4.8
            # 两批各自的实测：一批在上、一批在下，拟合线夹在中间两头都错
            s.circle(px, base - 26 - 5 * (i % 2), 6, INK)
            s.circle(px, base + 30 + 5 * (i % 2), 6, INK)
    else:
        # 单 run：拟合线紧贴实测黑点
        s.line(x0 + 6, ytop + 4, x1 - 6, ybase - 22, BLUE, 7)
        for i, q in enumerate(QS):
            s.circle(qx(x0, x1, q), ytop + 8 + i * 12.6 + (5 if i % 2 else -5),
                     6, BLUE)

    s.text(x + 14, PY + 78, "err_F.pdf", 30, GRAY, "start")


def main():
    s = SVG(800, 700)
    panel(s, 32, "单批次紧密贴合", False)
    panel(s, 432, "混学散布脱离拟合", True)

    s.text(400, 620, "模型两头失真", 34, RED, "middle", "bold")

    s.save("32_mixed_learning_shape.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
