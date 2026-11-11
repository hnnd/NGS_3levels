#!/usr/bin/env python3
# ============================================
# 脚本名称：merge_quant.py
# 功能描述：把多份 salmon quant.sf 合并成 counts / TPM 矩阵
# 作者：王运生
# 日期：2026-08-29
# ============================================
"""Merge multiple salmon ``quant.sf`` files into count and TPM matrices."""

from __future__ import annotations

import argparse
import csv
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_QUANT_COLUMNS = ("Name", "Length", "EffectiveLength", "TPM", "NumReads")


def read_quant(path: Path) -> dict[str, tuple[float, float]]:
    """Read one salmon ``quant.sf``.

    Args:
        path: Path to a ``quant.sf`` produced by ``salmon quant``.

    Returns:
        Mapping of transcript name to ``(NumReads, TPM)``.

    Raises:
        ValueError: If the file header is not a salmon quant header.
    """
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None or tuple(reader.fieldnames) != _QUANT_COLUMNS:
            raise ValueError(f"{path} 不是 salmon quant.sf（表头应为 {_QUANT_COLUMNS}）")
        return {
            row["Name"]: (float(row["NumReads"]), float(row["TPM"]))
            for row in reader
        }


def write_matrix(
    out_path: Path,
    samples: list[str],
    per_sample: list[dict[str, float]],
    features: list[str],
) -> None:
    """Write one feature-by-sample matrix as TSV."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["transcript", *samples])
        for feature in features:
            writer.writerow([feature, *(f"{d.get(feature, 0.0):.4f}" for d in per_sample)])
    logger.info("已写出 %s（%d 转录本 × %d 样本）", out_path, len(features), len(samples))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quant-files", nargs="+", required=True, type=Path)
    parser.add_argument("--sample-names", nargs="+", required=True)
    parser.add_argument("--counts-out", required=True, type=Path)
    parser.add_argument("--tpm-out", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a shell exit code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    if len(args.quant_files) != len(args.sample_names):
        logger.error(
            "文件数 (%d) 与样本名数 (%d) 不一致——检查 Snakefile 里 input 与 params 的顺序",
            len(args.quant_files),
            len(args.sample_names),
        )
        return 1

    counts: list[dict[str, float]] = []
    tpms: list[dict[str, float]] = []
    features: list[str] = []
    for path, name in zip(args.quant_files, args.sample_names):
        try:
            table = read_quant(path)
        except (OSError, ValueError) as exc:
            logger.error("读取 %s (%s) 失败：%s", name, path, exc)
            raise
        counts.append({k: v[0] for k, v in table.items()})
        tpms.append({k: v[1] for k, v in table.items()})
        if not features:
            features = list(table)
        elif set(features) != set(table):
            logger.warning("%s 的转录本集合与第一个样本不一致——索引可能不是同一份", name)
            features = sorted(set(features) | set(table))

    write_matrix(args.counts_out, args.sample_names, counts, features)
    write_matrix(args.tpm_out, args.sample_names, tpms, features)
    return 0


if __name__ == "__main__":
    sys.exit(main())
