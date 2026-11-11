#!/usr/bin/env python3
# ============================================
# 脚本名称：make_demo_data.py
# 功能描述：生成一份微型转录组 + 4 个样本的双端 FASTQ，供本流程离线试跑
# 作者：王运生
# 日期：2026-08-29
# ============================================
"""Generate a tiny synthetic transcriptome and paired-end reads.

只用于验证流程是否跑得通，不具任何生物学意义。
主线数据就位后直接改 config.yaml / samples.tsv，Snakefile 不用动。
"""

from __future__ import annotations

import argparse
import gzip
import logging
import os
import random
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

SEED = 20260829
BASES = "ACGT"
COMPLEMENT = str.maketrans("ACGT", "TGCA")
# 处理组里人为拉高表达的转录本（用于报告里能看出组间差异）
UPREGULATED = {"tx0003", "tx0007", "tx0011"}


def set_seeds(seed: int) -> None:
    """Fix every source of randomness used here."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)


def make_transcripts(n_tx: int, tx_len: int) -> dict[str, str]:
    """Build ``n_tx`` random transcripts of length ``tx_len``."""
    return {
        f"tx{i:04d}": "".join(random.choice(BASES) for _ in range(tx_len))
        for i in range(1, n_tx + 1)
    }


def revcomp(seq: str) -> str:
    """Reverse complement of a DNA string."""
    return seq.translate(COMPLEMENT)[::-1]


def write_fasta(path: Path, transcripts: dict[str, str]) -> None:
    """Write transcripts as a plain FASTA file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for name, seq in transcripts.items():
            handle.write(f">{name}\n{seq}\n")
    logger.info("参考转录组已写出：%s（%d 条）", path, len(transcripts))


def write_pair(
    out_dir: Path,
    sample: str,
    transcripts: dict[str, str],
    n_reads: int,
    read_len: int,
    boost: float,
) -> None:
    """Sample ``n_reads`` read pairs from ``transcripts`` into gzipped FASTQ."""
    out_dir.mkdir(parents=True, exist_ok=True)
    names = list(transcripts)
    weights = [boost if n in UPREGULATED else 1.0 for n in names]
    qual = "I" * read_len
    r1_path = out_dir / f"{sample}_1.fq.gz"
    r2_path = out_dir / f"{sample}_2.fq.gz"
    with gzip.open(r1_path, "wt") as r1, gzip.open(r2_path, "wt") as r2:
        for i in range(n_reads):
            seq = transcripts[random.choices(names, weights=weights, k=1)[0]]
            start = random.randint(0, len(seq) - 300)
            frag = seq[start : start + 300]
            rid = f"@{sample}:{i}"
            r1.write(f"{rid}/1\n{frag[:read_len]}\n+\n{qual}\n")
            r2.write(f"{rid}/2\n{revcomp(frag[-read_len:])}\n+\n{qual}\n")
    logger.info("样本 %s：%s / %s（各 %d 条）", sample, r1_path.name, r2_path.name, n_reads)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=Path("data"))
    parser.add_argument("--n-transcripts", type=int, default=60)
    parser.add_argument("--transcript-length", type=int, default=1500)
    parser.add_argument("--reads-per-sample", type=int, default=20000)
    parser.add_argument("--read-length", type=int, default=100)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a shell exit code."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = parse_args(argv)
    set_seeds(SEED)
    transcripts = make_transcripts(args.n_transcripts, args.transcript_length)
    write_fasta(args.outdir / "ref" / "transcripts.fa", transcripts)
    for sample, boost in (("CK_1", 1.0), ("CK_2", 1.0), ("TR_1", 4.0), ("TR_2", 4.0)):
        write_pair(
            args.outdir / "reads",
            sample,
            transcripts,
            args.reads_per_sample,
            args.read_length,
            boost,
        )
    logger.info("演示数据就绪。下一步：snakemake -n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
