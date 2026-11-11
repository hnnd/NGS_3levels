#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12_tpm_two_frames.py — 生成 12_tpm_two_frames.svg
（FIG-P03-12：第 28 页 cols 一栏「合并算 TPM 两个参照系错位对比」）【data-plot】

方案：reviews/course/P03_FIGP_001.md §4 FIG-P03-12（P28，cols，800×700）。
依据：教材 §16.4.4 L229–237——合并矩阵算 TPM 时，宿主与病原共享一个分母：
① 跨物种看，病原被自己的份额压掉，压低倍数 = 1/p（p = 0.5% → 200×）；
② 时序内看，份额随时相上涨，同一个恒定表达的病原基因却「涨」了 p 之比 60×，
同一个恒定表达的宿主基因「跌」到 0.704（假降约 30%）。两个现象同一个分母错误。
数字入口：`textbook/demos/ch16_mixed_tpm_bias.py --selftest`（现跑：手算 1/p =
200.0×；模拟实现 61.2× 与 0.701，分开归一化后 1.023）。本脚本直接 import 该 demo
的 `simulate()` 用同一参数（15000 宿主基因 + 12000 病原基因、2×10⁷ 分子、3 重复、
seed 20261104）重算并断言，不一致即失败退出；见回执核对表。
图内中文严格取方案给定 28 字（3 句）。`1/p`、`61.2×`、`0.701` 属符号与数值。
结构＝上排「跨物种两个参照系」双条对比（各自归一化 = 满条，合并口径 = 只剩 1/200），
下排「时序内」对数坐标双曲线（病原 61.2× 上升、宿主 0.701 下降）。
配色：浅橙＝病原、深蓝＝宿主，红色只标两处假象（时序内虚涨、宿主假降）。
无网络；随机数只用 demo 的固定种子。
用法：PYTHONDONTWRITEBYTECODE=1 python3 12_tpm_two_frames.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]          # NGS_3Levels/
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(ROOT / "textbook" / "demos"))
import numpy as np                                    # noqa: E402
from svghelp import *                                 # noqa: E402,F401,F403
from ch16_mixed_tpm_bias import P_TIME, simulate      # noqa: E402

PHRASES = ["跨物种比病原低二百倍", "时序内病原虚涨六十倍", "恒定宿主假降三成"]
TEXT = "".join(PHRASES)
N_HOST, N_PATH, MOLS, SEED = 15000, 12000, 20_000_000, 20261104
REF_PRESS, REF_START, REF_HOST, REF_SEP = 200.0, 61.2, 0.701, 1.023


class Args:
    n_host, n_path, molecules, seed = N_HOST, N_PATH, MOLS, SEED


def numbers():
    """复算 demos Part 1：恒定病原基因 48/12 倍数、恒定宿主基因、分开归一化倍数。"""
    rows = simulate(Args)
    early = [r for r in rows if r["p"] == P_TIME[0]]
    late = [r for r in rows if r["p"] == P_TIME[-1]]
    mp_e = np.mean([r["merged_p"] for r in early], axis=0)
    mp_l = np.mean([r["merged_p"] for r in late], axis=0)
    mh_e = np.mean([r["merged_h"] for r in early], axis=0)
    mh_l = np.mean([r["merged_h"] for r in late], axis=0)
    sp_e = np.mean([r["sep_p"] for r in early], axis=0)
    sp_l = np.mean([r["sep_p"] for r in late], axis=0)
    got = dict(path_fold=float(np.median(mp_l / np.maximum(mp_e, 1e-12))),
               host_fold=float(np.median(mh_l / np.maximum(mh_e, 1e-12))),
               sep_fold=float(np.median(sp_l / np.maximum(sp_e, 1e-12))),
               press=1.0 / P_TIME[0])
    for k, ref in (("press", REF_PRESS), ("path_fold", REF_START),
                   ("host_fold", REF_HOST), ("sep_fold", REF_SEP)):
        if abs(got[k] - ref) > 0.05:
            raise SystemExit(f"图面数字与 demos 现跑不一致：{k} "
                             f"got={got[k]:.3f} ref={ref}")
    return got


def main():
    g = numbers()
    s = SVG(800, 700, "Two reference frames share one wrong denominator",
            plan=TEXT)

    # ---------- 上排：跨物种 ★ 合并口径只剩 1/200 ----------
    s.text(52, 88, PHRASES[0], 30, INK, "start", "bold")
    s.text(52, 150, "1×", 32, BLUE, "start", "bold")
    s.rect(120, 124, 520, 34, BLUE, None, 0, rx=10)       # 各自归一化：满条
    s.text(52, 216, "1/p", 32, ORANGE, "start", "bold")
    s.rect(120, 190, 520, 34, WHITE, ORANGE, 2, rx=10, dash="6 6")
    s.rect(120, 190, 3, 34, ORANGE, None, 0, rx=2)        # 合并口径：约 1/200
    s.text(652, 216, "1/200", 30, ORANGE, "start", "bold")
    s.line(44, 246, 756, 246, PANEL, 4)

    # ---------- 下排：时序内方向对照（两条横排，红线上升 / 蓝线下降）----------
    s.text(44, 296, PHRASES[1], 30, RED, "start", "bold")
    s.panel(44, 312, 712, 130, ORANGE_TINT, ORANGE, 3)
    s.arrow(384, 414, 540, 342, RED, 6, 16)
    s.text(552, 356, f"{g['path_fold']:.1f}×", 34, RED, "start", "bold")

    s.text(44, 502, PHRASES[2], 30, BLUE, "start", "bold")
    s.panel(44, 518, 712, 130, BLUE_TINT, BLUE, 3)
    s.arrow(384, 546, 540, 618, BLUE, 6, 16)
    s.text(736, 584, f"{g['host_fold']:.3f}", 36, BLUE, "end", "bold")

    # 通道含义：上行橙点＝病原，下行蓝点＝宿主
    s.dot(104, 378, 18, ORANGE)
    s.dot(104, 584, 18, BLUE)
    s.save("12_tpm_two_frames.svg")
    return 0


if __name__ == "__main__":
    assert len(re.findall(r"[\u4e00-\u9fff]", TEXT)) == 28, TEXT
    raise SystemExit(main())
