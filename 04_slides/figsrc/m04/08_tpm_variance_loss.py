#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FIG-M04-08 TPM 两步计算流向与深度证据抹平（data-plot：demos Part 0 手算规则）。
图内文字与版式：M04_FIGP_001.md §4 FIG-M04-08；配色：spec.md §2。
依据：教材 §14.4.3；数字复现 textbook/demos/ch14_tpm_rounding.py --selftest Part 0。"""
import math

from svghelp import *

# ---- 手算规则（与 demos/ch14_tpm_rounding.py Part 0 同式）----
TPM_A = 1 / 1.0 / (1e6 / 1.0) * 1e6        # 1 read @ 1M → 1
TPM_B = 100 / 1.0 / (100e6 / 1.0) * 1e6    # 100 reads @ 100M → 1
CV_A = 1 / math.sqrt(1)                    # 1.0
CV_B = 1 / math.sqrt(100)                  # 0.1
assert TPM_A == 1 and TPM_B == 1 and CV_A == 1.0 and abs(CV_B - 0.1) < 1e-12

s = SVG()

# ---- 上部：TPM 两步流向 ----
def flow_box(x, w, title, sub, fill):
    s.rect(x, 66, w, 96, fill, None, rx=12)
    s.text(x + w / 2, 110, title, 30, WHITE, "middle", "bold")
    s.text(x + w / 2, 146, sub, 30, WHITE, "middle")

flow_box(20, 170, "Read", "raw counts", GREEN)
flow_box(296, 200, "÷ 长度 kb", "RPK", CYAN_DEEP)
flow_box(570, 200, "÷ ΣRPK/10^6", "TPM", BLUE)
s.arrow(192, 114, 292, 114, GRAY, 6, 15)
s.arrow(498, 114, 566, 114, GRAY, 6, 15)
s.text(242, 60, "长度校正", 30, INK, "middle")
s.text(548, 60, "文库缩放", 30, INK, "middle")

# ---- 中部：证据抹平对比卡 ----
s.label(200, 224, ["相对丰度相同"], 30, BLUE, weight="bold")
s.label(600, 224, ["泊松变异系数差十倍"], 30, BLUE, weight="bold")

def sample_card(x0, name, lib, reads, rel, tpm, cv, cvh):
    s.rect(x0, 258, 360, 268, WHITE, BLUE, 5, rx=14)
    s.text(x0 + 180, 302, name, 32, BLUE, "middle", "bold")
    s.text(x0 + 180, 340, f"文库 {lib} · {reads} read", 30, GRAY, "middle")
    s.text(x0 + 30, 390, "相对丰度", 30, GRAY, "start")
    s.text(x0 + 330, 394, rel, 30, INK, "end", "bold")
    s.text(x0 + 30, 436, "TPM", 30, GRAY, "start")
    s.text(x0 + 330, 440, tpm, 32, BLUE, "end", "bold")
    s.text(x0 + 30, 482, "CV 1/√c", 30, GRAY, "start")
    s.text(x0 + 330, 486, cv, 30, INK, "end", "bold")
    s.rect(x0 + 30, 498, 300, 16, PANEL, None)
    s.rect(x0 + 30, 498, int(300 * cvh), 16, GREEN if cvh > 0.5 else ORANGE,
           None)

sample_card(20, "样本 A", "1M", "1", "1.00e-06", "1", "100%", 1.0)
sample_card(420, "样本 B", "100M", "100", "1.00e-06", "1", "10%", 0.10)

# ---- 红色警示条 ----
s.rect(20, 580, 760, 84, RED_TINT, RED, 6, rx=14)
s.text(400, 634, "证据差 10 倍 → TPM 同为 1", 32, RED, "middle",
       "bold")

s.save("08_tpm_variance_loss.svg")
