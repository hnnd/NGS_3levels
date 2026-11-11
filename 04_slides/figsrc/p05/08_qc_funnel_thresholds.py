#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_qc_funnel_thresholds.py — 生成 08_qc_funnel_thresholds.svg
（FIG-P05-08：P23「质控：四个阈值，一个关掉的过滤器」，cols 左栏）【new-svg】

方案：reviews/course/P05_FIGP_001.md §4 FIG-P05-08（800×700，中文共 28 字）。
依据：教材 §21.4.3、§21.4.4、§21.5.5——质控四道闸门各管一件事：
`--geno 0.1` 标记缺失率、`--maf 0.05` 次等位基因频率下限、`--mind 0.1`
个体缺失率；第四道 `--hwe 0` 在高度自交群体（水稻）上默认关闭——自交
s≈0.95 时开启 HWE 过滤会把真实多态位点成批误杀（§21.5.5 的定量说明），
而 Wahlund 效应也会让合并样本的 HWE 检验大量偏离。
图内中文严格取方案给定两句（13 + 15 = 28 字）；四个阈值参数名与数字为工具
参数，不占汉字预算。配色：深蓝＝漏斗框线，青蓝＝清洗数据流；红色只用作
第四道闸门的「关闭」警示一处。
无网络；不涉及随机数（阈值为教材给定的配置值，不含计算结果）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 08_qc_funnel_thresholds.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from svghelp import *                                        # noqa: E402,F401,F403

PHRASES = ["次频缺失限稳健样本实际记账",           # 13
           "自交群体关哈代避免误杀真实位点"]       # 15
TEXT = "".join(PHRASES)

# 四道闸门：(参数, 上边宽, 下边宽, 主色, 淡色)
GATES = [("--geno 0.1", 640, 580, BLUE, BLUE_TINT),
         ("--maf 0.05", 580, 520, BLUE, BLUE_TINT),
         ("--mind 0.1", 520, 460, BLUE, BLUE_TINT),
         ("--hwe 0", 460, 400, RED, RED_TINT)]


def main():
    s = SVG(800, 700, "QC funnel with the disabled HWE gate", plan=TEXT)

    y = 40
    h = 116
    gap = 8
    for i, (flag, wt, wb, col, tint) in enumerate(GATES):
        top = y + i * (h + gap)
        s.wedge(400, top, wt, wb, h, tint, col, 5)
        s.text(400, top + h / 2 + 11, flag, 32, col, "middle", "bold")

    # 第四道闸门：关闭状态（唯一红色警示：锁 + 红叉）
    last = y + 3 * (h + gap)
    s.cross(508, last + h / 2, 20, RED)
    s.lock(576, last + h / 2, 30, RED)

    # 底部两句
    s.text(400, 596, PHRASES[0], 32, BLUE, "middle", "bold")
    s.text(400, 656, PHRASES[1], 32, RED, "middle", "bold")

    s.save("08_qc_funnel_thresholds.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())
