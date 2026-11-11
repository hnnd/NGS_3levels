#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""29_benchmark_rss_vs_vms.py — FIG-M08-29 benchmark 定内存只看 max_rss（P59，cols，data-plot）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-29（`.cols` 一栏 800×700，data-plot）。
数据入口（教材 §23.4.5 设例，手算复核，不是实测）：
  s=7200、max_rss=3200 MB、max_vms=48000 MB、cpu_time=7100、threads=16；
  max_vms/max_rss = 48000/3200 = 15 倍；申请内存留 1.3–2 倍余量：
  3200×1.3=4160 MB、3200×2.0=6400 MB，即约 4–6 GB。
  左面板用同一标尺全景对比，右面板放到 0–8000 MB 看清申请区间；本脚本按上式复算并断言。
图内汉字 = 方案原句逐字，共 25 字（虚拟内存虚高十五倍 / 物理峰值定申请依据 /
留一点三至两倍）；指标名、单位与数值用 ASCII。红 1 处标「虚高十五倍」。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 29_benchmark_rss_vs_vms.py
"""
import sys

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

VMS, RSS = 48000, 3200          # MB（设例）
LO_MUL, HI_MUL = 1.3, 2.0


def data():
    ratio = VMS // RSS
    lo, hi = int(RSS * LO_MUL), int(RSS * HI_MUL)
    assert ratio == 15 and lo == 4160 and hi == 6400
    print(f"check: max_vms/max_rss = {VMS}/{RSS} = {ratio} 倍；"
          f"申请区间 {RSS}×{LO_MUL:g} – {RSS}×{HI_MUL:g} = {lo}–{hi} MB")
    return ratio, lo, hi


def main():
    ratio, lo, hi = data()
    s = SVG()

    s.text(400, 62, "虚拟内存虚高十五倍", 36, BLUE, "middle", "bold")

    # ---------- 左面板：同一标尺（0–48000 MB）全景，两柱等比，15 倍一眼可见 ----------
    s.rect(36, 96, 348, 392, WHITE, PANEL, 3, rx=14)
    s.text(210, 132, "0 - 48000 MB", 30, GRAY, "middle")
    base, k = 440, 250 / VMS
    s.line(66, base, 354, base, INK, 4)
    s.rect(84, base - 250, 104, 250, RED, rx=8)             # max_vms = 48000
    s.rect(252, base - RSS * k, 88, RSS * k, CYAN_DEEP, rx=6)  # max_rss
    s.text(136, 168, f"{VMS}", 32, RED, "middle", "bold")
    s.text(296, base - RSS * k - 14, f"{RSS}", 32, CYAN_DEEP,
           "middle", "bold")
    s.text(136, 480, "max_vms", 30, INK, "middle")
    s.text(296, 480, "max_rss", 30, INK, "middle")
    s.text(200, 552, f"{VMS} / {RSS} = {ratio}x", 34, RED, "middle", "bold")

    # ---------- 右面板：由物理峰值推出申请区间（两卡一箭头，不做第二套坐标） ----------
    s.rect(412, 96, 348, 392, WHITE, PANEL, 3, rx=14)
    s.text(586, 138, "max_rss -> request", 30, GRAY, "middle")

    s.rect(444, 158, 284, 76, CYAN_TINT, CYAN, 4, rx=12)
    s.text(586, 206, f"max_rss {RSS} MB", 32, CYAN_DEEP, "middle", "bold")

    s.arrow(586, 240, 586, 274, GREEN, 5, 14)
    s.text(600, 264, f"x{LO_MUL:g}-{HI_MUL:g}", 30, GREEN, "start", "bold")

    s.rect(444, 280, 284, 76, GREEN_TINT, GREEN, 4, rx=12)
    s.text(586, 328, f"{lo}-{hi} MB", 32, GREEN, "middle", "bold")

    s.text(586, 402, "留一点三至两倍", 30, GREEN, "middle", "bold")
    s.text(586, 452, "物理峰值定申请依据", 30, GREEN, "middle", "bold")

    # 底部再钉一次结论（与图题同源，不引入新数字）
    s.rect(104, 592, 592, 100, BLUE_TINT, BLUE, 4, rx=14)
    s.text(400, 650, f"{RSS} x (1.3 - 2.0) = {lo} - {hi} MB", 30, BLUE,
           "middle", "bold")

    return s.save("29_benchmark_rss_vs_vms.svg")


if __name__ == "__main__":
    raise SystemExit(main())
