#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""16_qc_dashboard_gates.py — 生成 16_qc_dashboard_gates.svg
（FIG-M03-19：四大必报质控指标仪表板与合格区间）【new-svg】

方案：reviews/course/M03_FIGP_001.md §4 FIG-M03-19（P40，cols 一栏，800×700）。
图内中文按方案（比对率 配对率 重复率 可判定区 样本异常预警）。
D135（2026-11-10，总编复检）：图内英文说明短语已译中文；指标字段名
（mapped/properly paired/PERCENT_DUP/callable region 等工具输出原名）
与工具名保留英文，其余说明译中文，字数不再按 ≤30 字核验。依据：
教材 §7.6、§10.5.4。无网络、无随机数。
"""
from svghelp import *  # noqa: F401,F403


def gauge(s, x, y, name, en, barcol, lo, hi, note, ncolor):
    s.rect(x, y, 350, 250, WHITE, PANEL, 3, rx=14)
    s.text(x + 175, y + 46, name, 34, INK, "middle", "bold")
    s.text(x + 175, y + 84, en, 30, GRAY, "middle")
    s.rect(x + 40, y + 110, 270, 40, PANEL, None, rx=20)
    s.rect(x + 40, y + 110, 216, 40, barcol, None, rx=20)
    s.text(x + 40, y + 190, lo, 30, GRAY, "start")
    s.text(x + 310, y + 190, hi, 30, GRAY, "end")
    s.text(x + 175, y + 228, note, 30, ncolor, "middle", "bold")


def main():
    s = SVG(800, 700)
    s.text(400, 46, "质控四指标", 36, INK, "middle", "bold")

    gauge(s, 40, 70, "比对率", "mapped (%)", GREEN, "<85%", ">95%",
          "样本异常预警 参考选错", RED)
    gauge(s, 420, 70, "配对率", "properly paired", CYAN, "偏低", "匹配文库",
          "查插入片段长度", GRAY)
    gauge(s, 40, 356, "重复率", "PERCENT_DUP", ORANGE, "—", "无红线",
          "结合文库与深度", GRAY)
    gauge(s, 420, 356, "可判定区", "callable region", GREEN, "—",
          "必须进报告", "阴性结论范围", BLUE)

    s.text(400, 664, "每份报告四个数；重复率无通用红线", 30,
           GRAY, "middle")
    s.save("16_qc_dashboard_gates.svg")


if __name__ == "__main__":
    main()
