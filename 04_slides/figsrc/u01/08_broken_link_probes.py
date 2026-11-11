#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""08_broken_link_probes.py — 生成 08_broken_link_probes.svg
（FIG-U01-08：断链三件套——cat / ls -lL / [[ -f ]] 探测；data-plot）

方案：reviews/course/U01_FIGP_001.md §4 FIG-U01-08（P25，cols 一栏，800×700）。
数据（必须与现跑一致；.ref=「行为复现，demos/ch01_symlink_checks.py --selftest」）：
  断链 cat rc=1（报 No such file or directory）；ls -lL rc=2；[[ -f ]] 守门 NOTFILE。
  本文件内在临时目录现跑同一探测并断言后落图（见 selfcheck()）。
依据：教材 §1.5.4 L293（察觉三证据）、§1.4.6 L151/L157。
无网络、无随机数；subprocess 调 bash 与 demo 同款。
用法：PYTHONDONTWRITEBYTECODE=1 python3 08_broken_link_probes.py
"""
import subprocess
import tempfile
from pathlib import Path

from svghelp import *  # noqa: F401,F403


def selfcheck():
    """与 demos/ch01_symlink_checks.py 同一断链三件套复现。"""
    with tempfile.TemporaryDirectory() as td:
        broken = Path(td) / "broken.fa"
        broken.symlink_to("reads_moved_away.fa")
        cat = subprocess.run(
            ["bash", "-c", 'cat "$1" >/dev/null', "_", str(broken)])
        lsl = subprocess.run(
            ["bash", "-c", 'ls -lL "$1" >/dev/null 2>&1', "_", str(broken)])
        guard = subprocess.run(
            ["bash", "-c",
             'if [[ -f "$1" ]]; then echo ISFILE; else echo NOTFILE; fi',
             "_", str(broken)], capture_output=True, text=True).stdout.strip()
        assert cat.returncode == 1, f"cat rc 应 1，得 {cat.returncode}"
        assert lsl.returncode == 2, f"ls -lL rc 应 2，得 {lsl.returncode}"
        assert guard == "NOTFILE", f"守门应 NOTFILE，得 {guard}"
        return cat.returncode, lsl.returncode


def main():
    cat_rc, lsl_rc = selfcheck()
    s = SVG(800, 700)

    # 标题
    s.text(400, 58, "断链：三步验真", 40, BLUE, "middle", "bold")

    # 中央（左列纵向）：断链字条（紫）→ 虚线向下 → 灰色虚影目标（打叉）
    s.rect(110, 110, 270, 92, PURPLE_TINT, PURPLE, 4, rx=10)
    s.text(245, 150, "broken.fa", 30, INK, "middle", family=MONO)
    s.text(245, 186, "ls 行首 l：看得见", 30, PURPLE, "middle")
    s.line(245, 206, 245, 252, PURPLE, 5, dash="12 8")
    s.polygon([(245, 264), (235, 246), (255, 246)], PURPLE)
    # 目标虚影 + 红叉
    s.rect(140, 270, 240, 96, WHITE, GRAY, 4, rx=10, dash="10 8")
    s.text(260, 310, "reads_moved_", 30, GRAY, "middle", family=MONO)
    s.text(260, 344, "away.fa", 30, GRAY, "middle", family=MONO)
    s.line(158, 282, 362, 354, RED, 6, cap="round")
    s.line(362, 282, 158, 354, RED, 6, cap="round")
    s.text(260, 420, "跟随读取全失败", 30, GRAY, "middle")

    # 右侧：三个探测徽章
    probes = [
        (110, f"cat → rc={cat_rc}", None),
        (290, f"ls -lL → rc={lsl_rc}", None),
        (470, "[[ -f ]]", "守门为假"),
    ]
    for by, line1, line2 in probes:
        s.rect(500, by, 290, 100, BLUE_TINT, BLUE, 4, rx=12)
        if line2:
            s.text(645, by + 44, line1, 30, BLUE, "middle", "bold",
                   family=MONO)
            s.text(645, by + 82, f"→ {line2}", 30, BLUE, "middle", "bold")
        else:
            s.text(645, by + 64, line1, 30, BLUE, "middle", "bold",
                   family=MONO)
    s.text(400, 640, "ls 看得见，读不了", 36, RED, "middle", "bold")

    s.save("08_broken_link_probes.svg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
