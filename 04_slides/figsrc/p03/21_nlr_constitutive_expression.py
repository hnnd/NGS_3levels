#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""21_nlr_constitutive_expression.py — 生成 21_nlr_constitutive_expression.svg
（FIG-P03-21：第 41 页 cols 一栏「NLR 表达本底抑制与筛选反直觉」）【new-svg】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-21（P41，cols，800×700）。
依据：教材 §16.4.7 L347–352——核心 NLR 的表达本底本来就低：水稻 Pi-ta 的抗病与感病
等位在两种材料里都是低水平组成型表达 [@bryan2000pita]；小麦 NLR 约 88% 的本底表达
落在全部转录本的最低十分位 [@steuernagel2020nlrannotator]。压低本底有生理原因：
NLR 激活是剂量依赖的，过表达引发自身免疫并带来适合度代价 [@lai2018nlrexpression]。
所以「侵染后显著上调」不是核心 NLR 的常态；把它当硬性筛选条件，会按错误的画像
漏掉最关键的一批。替代策略是把参照系换成群体多态性：看抗/感材料间的存在缺失与
结构变异，或把结构域清单投射到 QTL 区间与 GWAS 热点。本教学子集只有日本晴，连
等位比较都做不了（教材 §16.4.7 末段与 §16.6 已知限制）。
图内中文严格取方案给定 30 字（4 句）。`88%`、`10%`、`low`、`high` 为文献值与档位标签。
结构＝左侧两根剂量管（低＝绿待命／高＝红自身免疫）；右上表达分布曲线，最低十分位
一段用绿色阴影并标 88%；右下禁行标志盖在被划掉的上调过滤条件，绿箭头指向替代路径。
曲线由固定解析函数画出（无双峰噪声），不含任何实测数字。
配色：绿色＝低表达保护与群体定位替代，红色只标自身免疫代价与严禁硬设门槛两处。
无网络；不涉及随机数。
用法：PYTHONDONTWRITEBYTECODE=1 python3 21_nlr_constitutive_expression.py
"""
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["受体低表达防免疫", "上调过滤致漏检", "投射群体定位替代", "禁硬设上调门槛"]
TEXT = "".join(PHRASES)
LOW_PCT = 88                                   # 文献值：小麦 NLR 落最低十分位的比例


def check_pct():
    if not 0 < LOW_PCT <= 100:
        raise SystemExit(f"文献比例越界：{LOW_PCT}")
    return LOW_PCT


def curve():
    """表达分布曲线（对数表达轴的左偏占位、无实测数据）：峰值居中偏右，
    左侧尾巴就是「最低十分位」所在，与 88% 阴影段对应。"""
    pts = []
    for k in range(41):
        xx = 356 + k * 9.5
        dy = 210 * math.exp(-((xx - 508) ** 2) / (2 * 30.0 ** 2))
        pts.append((xx, 356 - dy))
    return pts


def main():
    pct = check_pct()
    s = SVG(800, 700, "Constitutively low NLR expression", plan=TEXT)

    # ---------- 左：剂量决定免疫状态（两根竖管）----------
    s.text(44, 78, PHRASES[0], 30, GREEN, "start", "bold")
    s.rect(74, 268, 88, 130, GREEN_TINT, GREEN, 4, rx=8)     # 低：待命
    s.rect(198, 122, 88, 276, RED_TINT, RED, 4, rx=8)        # 高：自身免疫
    s.text(118, 434, "low", 30, GREEN, "middle", "bold")
    s.text(242, 434, "high", 30, RED, "middle", "bold")

    # ---------- 右上：表达分布曲线 + 最低十分位阴影 ----------
    s.panel(336, 92, 420, 300, WHITE, BLUE, 3)
    s.line(356, 392, 736, 392, BLUE, 4)
    s.line(356, 392, 356, 108, BLUE, 4)
    s.rect(358, 112, 74, 280, GREEN_TINT, None, 0)           # 最低十分位段
    s.polyline(curve(), BLUE, 4)
    s.text(366, 172, f"{pct}%", 30, GREEN, "start", "bold")
    s.text(624, 336, "10%", 30, GRAY, "start")
    s.text(658, 132, "expr", 30, GRAY, "middle")

    # ---------- 右下：禁行标志 + 被划掉的过滤条件 + 替代路径 ----------
    s.text(384, 452, PHRASES[1], 30, INK, "start", "bold")
    s.circle(404, 496, 22, WHITE, GRAY, 4)
    s.line(404, 480, 404, 500, GRAY, 8, cap="round")          # 禁行竖杠
    s.line(462, 492, 744, 492, GRAY, 3)
    s.cross(536, 492, 24, GRAY, 7)
    s.text(44, 566, PHRASES[3], 30, RED, "start", "bold")
    s.arrow(400, 620, 430, 620, GREEN, 6, 16)
    s.text(452, 632, PHRASES[2], 30, GREEN, "start", "bold")
    s.save("21_nlr_constitutive_expression.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 30, TEXT
    raise SystemExit(main())
