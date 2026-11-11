#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""15_markdup_four_steps.py — 生成 15_markdup_four_steps.svg（FIG-U05-15：重复标记四步）

方案：reviews/course/U05_FIGP_001.md §4 FIG-U05-15（P48，cols 一栏，viewBox 800×700）。
四步链 collate → fixmate -m（补 ms/MC 标签，不能省）→ sort → markdup（打 1024 点）；
红点 2 处：缺 fixmate -m → no ms score tag；只标记，不删除。
依据教材 §7.6 第 6 步、§7.5.2/⑨-E7 指纹；「只标记不删除」＝讲义 ⑤5.8 口径。
命令名与 samtools 1.17 一致。无网络、无随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 15_markdup_four_steps.py
"""
from svghelp import *  # noqa: F401,F403


def main():
    s = SVG(800, 700)
    boxes = [(30, "collate"), (215, "fixmate -m"), (400, "sort"),
             (585, "markdup")]

    for x, name in boxes:
        s.rect(x, 120, 160, 150, WHITE, BLUE, 5, rx=14)
    for x in (190, 375, 560):
        s.arrow(x + 3, 195, x + 22, 195, BLUE, 6, head=16)

    # ① collate：按读段名聚集（双端并拢示意）
    s.text(110, 168, "collate", 32, BLUE, "middle", "bold")
    s.rect(58, 196, 58, 14, CYAN, rx=4)
    s.rect(58, 226, 58, 14, CYAN, rx=4)
    s.arrow(122, 218, 142, 218, CYAN, 5, head=12)
    s.rect(146, 205, 32, 28, CYAN, rx=4)

    # ② fixmate -m：补 ms / MC 标签（不能省，角标在盒上方）
    s.rect(245, 72, 100, 42, ORANGE, rx=21)
    s.text(295, 103, "不能省", 30, WHITE, "middle", "bold")
    s.text(295, 162, "fixmate", 32, BLUE, "middle", "bold")
    s.text(295, 196, "-m", 30, ORANGE, "middle", "bold")
    s.text(295, 230, "补 ms / MC", 30, INK, "middle", "bold")
    s.text(295, 258, "标签", 30, INK, "middle", "bold")

    # ③ sort：坐标重排
    s.text(480, 168, "sort", 32, BLUE, "middle", "bold")
    s.line(430, 240, 540, 240, GRAY, 4)
    for bx, bh in ((442, 20), (478, 30), (514, 40)):
        s.rect(bx, 240 - bh, 16, bh, CYAN, rx=3)

    # ④ markdup：读段对打橙点 1024
    s.text(665, 160, "markdup", 32, BLUE, "middle", "bold")
    s.rect(615, 188, 100, 13, CYAN, rx=4)
    s.rect(615, 210, 100, 13, CYAN, rx=4)
    s.circle(665, 194, 7, ORANGE)
    s.circle(665, 216, 7, ORANGE)
    s.text(665, 256, "1024", 30, ORANGE, "middle", "bold")

    # 红点注记 2 处（满额）
    s.line(295, 272, 295, 298, RED, 4, dash="8 8")
    s.text(295, 330, "缺它 → no ms score tag", 30, RED, "middle", "bold")
    s.line(665, 272, 665, 298, RED, 4, dash="8 8")
    s.text(665, 330, "只标记，不删除", 30, RED, "middle", "bold")

    s.save("15_markdup_four_steps.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
