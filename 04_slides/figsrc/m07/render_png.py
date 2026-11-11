#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_png.py — 把 m07 新图渲染成 1600px PNG，供目检（输出只在 tasks/logs/）

用途：任务卡 M07_FIGS_001 acceptance 第 4 条「用 cairosvg 或 chromium 渲染 PNG 自查」。
输出目录 `textbook/tasks/logs/M07_FIGS_png/`（不属于交付源目录，不污染 04_slides/）。
参数：可选 1 个或多个 SVG stem（省略则渲染 imgs/07_metagenome/ 全部）。
用法：PYTHONDONTWRITEBYTECODE=1 python3 render_png.py [stem ...]
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]           # NGS_3Levels/
SRC = ROOT / "04_slides" / "master" / "imgs" / "07_metagenome"
OUT = ROOT / "textbook" / "tasks" / "logs" / "M07_FIGS_png"


def main(argv):
    import cairosvg
    OUT.mkdir(parents=True, exist_ok=True)
    stems = argv[1:] or sorted(p.stem for p in SRC.glob("*.svg"))
    for stem in stems:
        svg = SRC / f"{stem}.svg"
        png = OUT / f"{stem}.png"
        cairosvg.svg2png(url=str(svg), write_to=str(png),
                         output_width=1600)
        print(f"rendered {png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
