"""幻灯片类检查：每个专题有 Marp deck、frontmatter 合规、@section 骨架完整、页数在区间内。"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from tools.contract import Topic
from tools.report import Finding, Severity, Status
from tools.workspace import CheckContext

logger = logging.getLogger(__name__)

_SEPARATOR_RE = re.compile(r"^---\s*$", re.MULTILINE)
_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_KV_RE = re.compile(r"^\s*([A-Za-z_]+)\s*:\s*(.+?)\s*$")


def _finding(ctx: CheckContext, check: str, level: str, subject: str, message: str,
             status: Status = Status.FAIL, severity: Severity | None = None) -> Finding:
    return Finding(check, level, severity or ctx.severity(check), status, subject, message)


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """返回 (frontmatter 键值, 正文)。无 frontmatter 时键值为空、正文为全文。"""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        kv = _KV_RE.match(line)
        if kv:
            fields[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return fields, text[match.end():]


def count_pages(body: str) -> int:
    """页数 = `---` 分隔符数 + 1（忽略代码块内的分隔符）。"""
    in_code = False
    separators = 0
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if not in_code and _SEPARATOR_RE.match(line):
            separators += 1
    return separators + 1


def deck_path_for(ctx: CheckContext, topic: Topic) -> Path | None:
    """由讲义文件名推出 deck 路径：<dir>/<level>/<stem>_slides.md。"""
    spec = ctx.contract.slides
    assert spec is not None
    ref = ctx.workspace.lecture_ref(topic)
    if ref.primary is None:
        return None
    stem = ref.primary.name
    if stem.endswith(spec.lecture_suffix):
        stem = stem[: -len(spec.lecture_suffix)]
    else:
        stem = ref.primary.stem
    return ctx.workspace.root / spec.dir / topic.level / f"{stem}{spec.file_suffix}"


def _check_one_deck(ctx: CheckContext, check: str, topic: Topic, path: Path) -> list[Finding]:
    spec = ctx.contract.slides
    assert spec is not None
    level = topic.level
    rel = ctx.workspace.rel(path)
    subject = f"{topic.topic_id} @ {rel}"
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.error("读取 deck 失败 %s: %s", path, exc)
        findings.append(_finding(ctx, check, level, subject, f"无法读取：{exc}"))
        return findings

    fields, body = _parse_frontmatter(text)
    for key, expected in spec.frontmatter_required.items():
        actual = fields.get(key)
        if actual is None or actual.lower() != str(expected).lower():
            findings.append(_finding(ctx, check, level, subject,
                                     f"frontmatter 缺少或不匹配：{key}: {expected}（实际 {actual!r}）"))

    is_stats = (level, topic.topic_id) in ctx.contract.stats_plugin_topics
    is_ai = (level, topic.topic_id) in ctx.contract.ai_task_topics
    missing: list[str] = []
    forbidden: list[str] = []
    for sec in spec.sections:
        marker = spec.marker_for(sec.section_id)
        present = marker in body
        applicable = True
        if sec.applies_to == "stats_plugin_topics":
            applicable = is_stats
        elif sec.applies_to == "ai_task_topics":
            applicable = is_ai
        if applicable and sec.required and not present:
            missing.append(f"{sec.section_id}({sec.title})")
        if not applicable and present:
            forbidden.append(f"{sec.section_id}({sec.title})")
    if missing:
        findings.append(_finding(ctx, check, level, subject, "缺少 @section 标记：" + "、".join(missing)))
    if forbidden:
        findings.append(_finding(ctx, check, level, subject,
                                 "名单外专题不应出现 @section：" + "、".join(forbidden)))

    target = spec.deck_size_targets.get(level)
    if target:
        pages = count_pages(body)
        lo, hi = target
        if not lo <= pages <= hi:
            findings.append(_finding(ctx, check, level, subject,
                                     f"页数 {pages} 超出目标区间 {lo}–{hi}",
                                     severity=Severity.WARNING))
    return findings


def check_slide_deck_match(ctx: CheckContext) -> list[Finding]:
    """每个专题有 deck；deck 合规；无孤儿 deck。契约无 slide_template 时整体跳过。"""
    check = "slide_deck_match"
    spec = ctx.contract.slides
    if spec is None:
        logger.info("契约未声明 slide_template，跳过 %s", check)
        return []
    findings: list[Finding] = []
    for level in ctx.levels:
        level_dir = ctx.workspace.root / spec.dir / level
        if not level_dir.is_dir():
            findings.append(_finding(ctx, check, level, ctx.workspace.rel(level_dir),
                                     "幻灯片目录尚未创建", status=Status.PENDING))
            continue
        expected: set[Path] = set()
        for topic in ctx.contract.curriculum.get(level, ()):
            path = deck_path_for(ctx, topic)
            if path is None:
                findings.append(_finding(ctx, check, level, topic.topic_id,
                                         "讲义尚未生成，deck 文件名无法推导", status=Status.PENDING))
                continue
            expected.add(path)
            if not path.is_file():
                findings.append(_finding(ctx, check, level, f"{topic.topic_id} @ {ctx.workspace.rel(path)}",
                                         "幻灯片尚未生成", status=Status.PENDING))
                continue
            findings.extend(_check_one_deck(ctx, check, topic, path))
        for extra in sorted(level_dir.glob(f"*{spec.file_suffix}")):
            if extra not in expected:
                findings.append(_finding(ctx, check, level, ctx.workspace.rel(extra),
                                         "孤儿 deck：不对应契约中任何专题"))
    return findings
