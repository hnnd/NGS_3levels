#!/usr/bin/env python3
"""export_narration.py — 把 deck 里的旁白（<!-- 旁白：… -->）导出为逐页讲稿 Markdown（D139）。

用法：python3 04_slides/export_narration.py 04_slides/master/01_ngs_design_slides.md [-o OUT.md]
默认输出到 deck 同级的 narration/<slug>_narration.md。每页：页码、页标题、旁白全文。
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

logger = logging.getLogger(__name__)
NOTE = re.compile(r'<!--\s*\n?旁白[:：](.*?)-->', re.S)


def export(deck: Path, out: Path) -> int:
    """Write the narration script for one deck; return the number of narrated pages."""
    text = deck.read_text(encoding='utf-8')
    head = re.search(r'^header:\s*"?(.*?)"?\s*$', text, re.M)
    body = re.sub(r'\A---\n.*?\n---\n', '', text, count=1, flags=re.S)
    lines = [f'# 旁白讲稿 · {head.group(1) if head else deck.stem}', '',
             f'> 由 `{deck.name}` 的演讲者备注导出；改旁白请改 deck 本身，再重新导出。', '']
    n = 0
    for i, page in enumerate(re.split(r'\n---\s*\n', body), 1):
        m = NOTE.search(page)
        if not m:
            continue
        t = re.search(r'^#{1,2}\s+(.+)$', NOTE.sub('', page), re.M)
        title = re.sub(r'<[^>]+>', '', t.group(1)).strip() if t else '（无标题页）'
        lines += [f'## 第 {i} 页 · {title}', '', m.group(1).strip(), '']
        n += 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines), encoding='utf-8')
    logger.info('%s: %d pages -> %s', deck.name, n, out)
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('deck', type=Path)
    ap.add_argument('-o', '--out', type=Path)
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    out = a.out or a.deck.parent / 'narration' / a.deck.name.replace('_slides.md', '_narration.md')
    return 0 if export(a.deck, out) else 1


if __name__ == '__main__':
    sys.exit(main())
