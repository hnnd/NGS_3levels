#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""28_twelve_jobs_breakdown.py — FIG-M08-28 四样本流水线 12 作业构成分解（P56，cols，data-plot）

方案：textbook/reviews/course/M08_FIGP_001.md §4 FIG-M08-28（`.cols` 一栏 800×700，data-plot）。
数据入口（可复现，两条互为校验）：
  ① 教材 §23.2 手算：`all` 1 ＋ `fastp` 4 ＋ `salmon_index` 1 ＋ `salmon_quant` 4 ＋
     `merge_counts` 1 ＋ `report` 1 ＝ $1+4+1+4+1+1=12$；
  ② 仓库实测：`03_code/master/pipelines/samples.tsv` 现有 4 行样本（本脚本按列名解析并断言
     4 行），`03_code/master/pipelines/Snakefile` 里确为 6 条 rule（本脚本解析规则名并断言）。
  单样本规则 1 作业、多样本规则按样本数 ×4，故 12 = 4 × (1 + 1 + 1) + 1 × 3。
  本脚本读文件复算并断言，图内数字与上述入口逐位一致；图注标「手算 1+4+1+4+1+1」。
图内汉字 = 方案原句逐字，共 25 字（四样本作业总数十二 / 单步任务严格构成 /
读缺清单仅一作业）；规则名与算式用 ASCII。红 1 处标「读缺清单仅一作业」。
无随机数、无网络。用法：PYTHONDONTWRITEBYTECODE=1 python3 28_twelve_jobs_breakdown.py
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from svghelp import *  # noqa: F401,F403,E402

ROOT = Path(__file__).resolve().parents[3]           # NGS_3Levels/
SAMPLES = ROOT / "03_code" / "master" / "pipelines" / "samples.tsv"
SNAKEFILE = ROOT / "03_code" / "master" / "pipelines" / "Snakefile"

# (规则名, 是否逐样本 ×1, 配色)
RULES = [("all", False, BLUE), ("fastp", True, CYAN),
         ("salmon_index", False, PURPLE), ("salmon_quant", True, CYAN_DEEP),
         ("merge_counts", False, PURPLE), ("report", False, ORANGE_DEEP)]


def data():
    """从仓库文件复算作业构成：返回 (各规则作业数, 样本数, 合计)。"""
    rows = [ln for ln in SAMPLES.read_text(encoding="utf-8").splitlines()
            if ln.strip()]
    header = rows[0].split("\t")
    assert "sample" in header, "samples.tsv 缺 sample 列"
    n_samples = len(rows) - 1
    rules_in_file = [ln.split(":")[0].split()[1]
                     for ln in SNAKEFILE.read_text(encoding="utf-8").splitlines()
                     if ln.startswith("rule ")]
    assert [r for r, _, _ in RULES] == rules_in_file, \
        f"Snakefile 规则名与预期不符：{rules_in_file}"
    counts = [(r, n_samples if per else 1) for r, per, _ in RULES]
    assert n_samples == 4 and sum(c for _, c in counts) == 12
    return counts, n_samples, sum(c for _, c in counts)


def main():
    counts, n_samples, total = data()
    print(f"check: 样本 {n_samples} 行；" +
          " ＋ ".join(f"{r} {c}" for r, c in counts) + f" = {total}")

    s = SVG()
    s.text(400, 64, "四样本作业总数十二", 36, BLUE, "middle", "bold")
    s.text(400, 118, "1+4+1+4+1+1 = 12", 30, GRAY, "middle")

    # 堆叠条：12 个作业格，逐规则分段（每格 56 px）
    unit = 56
    x0, bar_y, bar_h = 64, 156, 78
    x = x0
    for name, n in counts:
        color = dict((r, c) for r, _, c in RULES)[name]
        w = unit * n
        s.rect(x, bar_y, w - 3, bar_h, color, rx=8)
        s.text(x + w / 2, bar_y + bar_h / 2 + 11, str(n), 32, WHITE,
               "middle", "bold")
        x += w

    # 语义注记：这一条是严格构成，不是估算
    s.text(400, 286, "单步任务严格构成", 30, BLUE, "middle", "bold")

    # 图例：两行三列，色块 + 规则名
    for i, (name, n) in enumerate(counts):
        color = dict((r, c) for r, _, c in RULES)[name]
        cx = 116 + (i % 2) * 330
        cy = 344 + (i // 2) * 64
        s.rect(cx, cy - 22, 34, 44, color, rx=8)
        s.text(cx + 48, cy + 11, f"{name} {n}", 30, INK, "start")

    # 唯一警示：fastp 只有 1 个 = 清单只读到一行样本
    s.rect(80, 540, 640, 124, RED_TINT, RED, 5, rx=16)
    s.text(400, 592, "读缺清单仅一作业", 32, RED, "middle", "bold")
    s.text(400, 638, "fastp = 1 → samples.tsv", 30, RED, "middle")

    return s.save("28_twelve_jobs_breakdown.svg")


if __name__ == "__main__":
    raise SystemExit(main())
