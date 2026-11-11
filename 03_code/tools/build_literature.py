#!/usr/bin/env python3
"""从大纲与讲义 ⑪ 中抽取已有文献（DOI）与官方链接，生成 09_resources 的清单。

只抽取、不新增：每一条都能回溯到某份讲义/大纲的具体行。重复 DOI 合并并列出全部引用处。

用法::

    python3 03_code/tools/build_literature.py            # 写入 09_resources/literature/*.md 与 external_links.md
    python3 03_code/tools/build_literature.py --dry-run  # 只打印统计
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.contract import load_contract

logger = logging.getLogger(__name__)

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\]\)|`*\"'，。》]+")
URL_RE = re.compile(r"https?://[^\s\)\]>|`\"'，。》]+")
HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)")
LEVEL_TITLE = {"undergraduate": "本科层", "master": "硕士层", "phd": "博士层"}
SKIP_URL_HOSTS = ("doi.org", "api.crossref.org", "eutils.ncbi.nlm.nih.gov")
TODAY = "2026-08-31"


@dataclass
class Citation:
    doi: str
    text: str
    sources: list[str] = field(default_factory=list)


def _clean_text(line: str, doi: str) -> tuple[str, str]:
    """返回 (引文主体, 备注)。备注取 '——' 之后的说明，或表格第一列的短标签。"""
    body = line.strip().strip("|").strip()
    body = re.sub(r"^\s*\d+\.\s*", "", body)
    body = re.sub(r"\[([^\]]+)\]\(https?://doi\.org/[^)]+\)", r"\1", body)
    body = body.replace("**", "").replace("`", "")
    cells = [c.strip() for c in body.split("|") if c.strip()]
    label = ""
    if len(cells) > 1 and len(cells[0]) < 40 and not re.search(r"\(?(19|20)\d\d\)?", cells[0]):
        label, cells = cells[0], cells[1:]
    cells = [re.sub(r"(DOI:|doi:)\s*" + re.escape(doi) + r"\S*", "", c).replace(doi, "").strip(" ｜—-:")
             for c in cells]
    body = " ｜ ".join(c for c in cells if c)
    note = ""
    if "——" in body:
        body, note = [s.strip() for s in body.split("——", 1)]
    if label and not note:
        note = label
    body = re.sub(r"\s+", " ", body).strip(" ｜—-")
    return body[:220], note[:120].replace("|", "｜")


def collect(paths: list[tuple[str, Path]]) -> dict[str, Citation]:
    """paths: (来源标签, 文件路径)。"""
    found: dict[str, Citation] = {}
    for tag, path in paths:
        section, in_code = "", False
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            m = HEADING_RE.match(line)
            if m and len(m.group(1)) == 2:
                section = m.group(2).strip()[:24]
            if in_code or "curl" in line or "99999" in line:
                continue
            dois = {d.rstrip(".,;:") for d in DOI_RE.findall(line)}
            for doi in dois:
                text, note = _clean_text(line, doi)
                src = f"{tag} L{lineno}（{section}）" + (f"：{note}" if note else "")
                cit = found.setdefault(doi, Citation(doi=doi, text=text))
                if len(text) > len(cit.text):
                    cit.text = text
                cit.sources.append(src)
    return found


def render_literature(level: str, topics: list, cits_by_topic: dict[str, list[Citation]],
                      shared: list[Citation]) -> str:
    title = LEVEL_TITLE[level]
    lines = [
        f"# {title}推荐文献清单",
        "",
        f"> 由 `03_code/tools/build_literature.py` 从 `01_syllabus/syllabus_{level}.md` 与 "
        f"`02_lectures/{level}/*/` 的 ⑪ 参考资料自动汇总 ｜ 生成日期 {TODAY}",
        "> **本清单不新增任何条目**——每条都标注了来源文件与行号，可回溯核对。同一 DOI 在多处被引用时合并为一条。",
        "",
    ]
    total = 0
    for topic in topics:
        cits = cits_by_topic.get(topic.topic_id, [])
        if not cits:
            continue
        lines += [f"## {topic.topic_id} {topic.title}", ""]
        lines += ["| # | 文献 | DOI | 引用处 / 为什么读 |", "|---|---|---|---|"]
        for i, c in enumerate(sorted(cits, key=lambda x: x.text.lower()), 1):
            srcs = "<br>".join(dict.fromkeys(c.sources))
            lines.append(f"| {i} | {c.text} | [{c.doi}](https://doi.org/{c.doi}) | {srcs} |")
            total += 1
        lines.append("")
    if shared:
        lines += ["## 附：L0 / L1 前置模块引用的文献（三层共享）", "",
                  "| # | 文献 | DOI | 引用处 |", "|---|---|---|---|"]
        for i, c in enumerate(sorted(shared, key=lambda x: x.text.lower()), 1):
            lines.append(f"| {i} | {c.text} | [{c.doi}](https://doi.org/{c.doi}) | "
                         f"{'<br>'.join(dict.fromkeys(c.sources))} |")
        lines.append("")
    lines += [
        "---",
        "",
        f"**核验说明**：所有 DOI 来自讲义 ⑪ / 大纲附录，已由 `validate_course.py` 的 `reference_syntax` 检查格式；"
        f"本清单不新增条目。本层去重后共 {total} 条。大纲中无 DOI 的条目（教材、官方文档）不在此列，见 `external_links.md`。",
        "",
    ]
    return "\n".join(lines)


def render_links(url_sources: dict[str, set[str]]) -> str:
    by_host: dict[str, list[str]] = defaultdict(list)
    for url in sorted(url_sources):
        if any(h in url for h in SKIP_URL_HOSTS):
            continue
        by_host[urlparse(url).netloc.removeprefix("www.")].append(url)
    lines = [
        "# 外部资源链接（官方文档 / 数据库 / 教程）",
        "",
        f"> 由 `03_code/tools/build_literature.py` 从 `02_lectures/**/*.md` 抽取 ｜ 生成日期 {TODAY}",
        "> 只抽取讲义已引用的链接，不新增；按域名分组，末列为引用它的讲义/模块。"
        "外部链接会失效，**每学期开课前用 `validate_course.py --check-links` 复检一次**。",
        "",
        "| 站点 | 链接 | 引用处 |", "|---|---|---|",
    ]
    for host in sorted(by_host):
        for url in by_host[host]:
            refs = ", ".join(sorted(url_sources[url]))
            lines.append(f"| {host} | <{url}> | {refs} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    root: Path = args.root
    contract = load_contract(root)
    out_dir = root / "09_resources" / "literature"
    out_dir.mkdir(parents=True, exist_ok=True)

    prereq_paths = [(p.stem, p) for p in sorted((root / "02_lectures/prerequisites").glob("*/*.md"))]
    shared = list(collect(prereq_paths).values())

    url_sources: dict[str, set[str]] = defaultdict(set)
    for level, topics in contract.curriculum.items():
        level_dir = root / contract.levels[level].lecture_dir
        cits_by_topic: dict[str, list[Citation]] = {}
        seen: dict[str, Citation] = {}
        syllabus = root / contract.levels[level].syllabus
        syl = collect([(f"大纲", syllabus)])
        for topic in topics:
            files = sorted((level_dir / topic.dir_name).glob("*.md"))
            found = collect([(f"讲义 {topic.topic_id}", f) for f in files])
            for f in files:
                for url in URL_RE.findall(f.read_text(encoding="utf-8")):
                    url_sources[url.rstrip(".,;:")].add(topic.topic_id)
            # 大纲里按专题 id 归类：行内出现 topic_id 或与讲义 DOI 相同者并入该专题
            for doi, cit in syl.items():
                if doi in found:
                    found[doi].sources = cit.sources + found[doi].sources
                elif any(re.search(rf"\b{topic.topic_id}\b", s) for s in cit.sources):
                    found[doi] = cit
            merged: list[Citation] = []
            for doi, cit in found.items():
                if doi in seen:
                    seen[doi].sources.extend(s for s in cit.sources if s not in seen[doi].sources)
                    merged.append(seen[doi])
                else:
                    seen[doi] = cit
                    merged.append(cit)
            cits_by_topic[topic.topic_id] = merged
        # 大纲里既不在讲义、也没标专题 id 的条目 → 挂到"大纲附录"伪专题
        leftovers = [c for d, c in syl.items() if d not in seen]
        text = render_literature(level, list(topics), cits_by_topic, shared)
        if leftovers:
            extra = ["## 大纲附录中未归入具体专题的文献", "", "| # | 文献 | DOI | 引用处 |", "|---|---|---|---|"]
            for i, c in enumerate(sorted(leftovers, key=lambda x: x.text.lower()), 1):
                extra.append(f"| {i} | {c.text} | [{c.doi}](https://doi.org/{c.doi}) | {'<br>'.join(c.sources)} |")
            text = text.replace("## 附：L0", "\n".join(extra) + "\n\n## 附：L0", 1)
        n_unique = len(seen) + len(leftovers)
        logger.info("%s: %d 条唯一 DOI（含大纲附录 %d 条）", level, n_unique, len(leftovers))
        if not args.dry_run:
            (out_dir / f"literature_{level}.md").write_text(text, encoding="utf-8")
    for p in prereq_paths:
        for url in URL_RE.findall(p[1].read_text(encoding="utf-8")):
            url_sources[url.rstrip(".,;:")].add(p[0])
    logger.info("外部链接 %d 条", len(url_sources))
    if not args.dry_run:
        (root / "09_resources/external_links.md").write_text(render_links(url_sources), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
