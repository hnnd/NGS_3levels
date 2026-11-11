#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""34_fragmented_peak_shift.py — FIG-M05-34 碎峰失效与模型平移偏差（data-plot）

方案：`reviews/course/M05_FIGP_001.md` §4.4 FIG-M05-34（P58，`.cols` 800×700，data-plot）。
数据入口：`textbook/demos/ch15_atac_fragment_model.py` Part 3（设例）——`--fix-bimodal` 时按默认
`d = 200 bp` 继续，把 reads 平移 `d/2 = 100 bp` 对齐，估计的峰中心系统性偏离真实 Tn5 切口
100 bp；summit 错位 → `-size 200` 的 summit ±100 bp 取窗整体错位。教材依据 §15.5.1 L349–L356。

本图不硬写 100：脚本从 demo 源码里读出 `d_forced = 200` 与 `shift = d_forced // 2` 两行，
当场算出偏移量并断言 = 100（与 `--selftest` 的 PASS 行同一条判据），所以图上的数字是与
demo 同步的推导值，不是凭记忆填的常数。

画法：上下两块用同一横轴与同一纵轴量程。上块是双端（BAMPE）定界下的正确形状——一个
平滑连续的开放区，中心一个峰；下块是单端默认模型强加 100 bp 平移后的结果——同一段开放区
被机械错位切成十几个离散小尖，峰数虚高、峰宽变窄。错位用一条位移箭头标出。

图内汉字 27 字（上限 30）：标题「模型强加平移」6 ＋ 上块名「正确」2 ＋ 纵轴「深度」2
＋ 结论「错位百碱基」5 ＋「连续开放区碎裂成小峰」10 ＝ 25，加位移标注「错位」2 ＝ 27。
W7 口径：图上不写「15 万个碎峰」这类设例量级，只写几何错位的因果。
配色：正确形状绿 `#00A087`、错位碎峰唯一警示红 `#E64B35`（碎峰 path ＋ 位移箭头合成
一个 `<g>` = 1 处，红字标注 1 处，共 2 处）。
无随机数（形状由解析函数生成）、无网络。
用法：PYTHONDONTWRITEBYTECODE=1 python3 34_fragmented_peak_shift.py
"""
import math
import re
from pathlib import Path

from svghelp import *

DEMO = (Path(__file__).resolve().parents[3] / "textbook" / "demos"
        / "ch15_atac_fragment_model.py")
src = DEMO.read_text(encoding="utf-8")
m_d = re.search(r"d_forced\s*=\s*(\d+)", src)
m_s = re.search(r"shift\s*=\s*d_forced\s*//\s*2", src)
assert m_d and m_s, "demo Part 3 的 d_forced / shift 定义未找到，须人工核对"
D_FORCED = int(m_d.group(1))
SHIFT = D_FORCED // 2
assert SHIFT == 100, SHIFT                       # 与 demo --selftest PASS 行同一判据

s = SVG()

s.text(400, 62, "模型强加平移", 36, BLUE, "middle", "bold")

# ---------------- 共用坐标系 ----------------
L, R = 100, 716
YMAX = 100.0


def py(base, v, gain):
    """把信号值 v 映射为距基线 base 的高度。"""
    return base - gain * v / YMAX


def envelope(frac):
    """真实的开放区包络：一个宽高斯（两块共用同一条）。"""
    return 100.0 * math.exp(-((frac - 0.5) / 0.19) ** 2)


# ---------- 上：双端定界，连续单峰（绿） ----------
B1, G1 = 306, 128
s.line(L, B1, R, B1, INK, 4)
s.line(L, B1, L, B1 - G1 - 34, INK, 4)
s.text(L - 8, B1 - G1 - 44, "深度", 30, GRAY, "start")

pts = [(L + (R - L) * (i / 120.0), py(B1, envelope(i / 120.0), G1))
       for i in range(121)]
s.curve(pts, GREEN, 6)
s.text(L + 34, B1 - 22, "正确", 30, GREEN, "start", "bold")

# ---------- 下：单端强加 100 bp 平移 → 碎成小尖（红） ----------
B2, G2 = 556, 118
s.line(L, B2, R, B2, INK, 4)
s.line(L, B2, L, B2 - G2 - 34, INK, 4)

NPK, HALF = 13, 0.010                            # 13 个小尖，各占开放区的一小段
peaks = []
for k in range(NPK):
    c = 0.18 + 0.64 * (k / (NPK - 1.0))
    h = envelope(c) * 0.74                       # 小尖高度随包络衰减（切碎但不消失）
    x0 = L + (R - L) * (c - HALF)
    x1 = L + (R - L) * (c + HALF)
    xc = L + (R - L) * c
    peaks.append(f"M {x0:.1f} {B2} L {xc:.1f} {py(B2, h, G2):.1f} L {x1:.1f} {B2} Z")

# 碎峰 path 与位移箭头合并成一个 <g>（红只计 1 处）
s.raw(f'<g fill="{RED}" stroke="{RED}">'
      f'<path d="{" ".join(peaks)}" fill="{RED}" stroke-width="2"/>'
      f'<line x1="{L + 46}" y1="{B2 - 104}" x2="{L + 46}" y2="{B2 - 42}" '
      f'stroke-width="4" stroke-dasharray="10 7"/>'
      f'<polygon points="{L + 46},{B2 - 28} {L + 34},{B2 - 50} {L + 58},{B2 - 50}"/>'
      f'</g>')
s.text(L + 66, B2 - 52, "错位 100 bp", 30, RED, "start", "bold")

# ---------- 结论（方案原句逐字，两行） ----------
s.text(400, 640, "错位百碱基", 32, INK, "middle", "bold")
s.text(400, 686, "连续开放区碎裂成小峰", 32, INK, "middle", "bold")

s.save("34_fragmented_peak_shift.svg")
print(f"check: demo d_forced={D_FORCED} → 平移 d/2={SHIFT} bp（与 --selftest PASS 行一致）；"
      f"碎峰 {NPK} 个（几何示意）")
