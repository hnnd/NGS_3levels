"""考核材料检查：材料存在、章节完整、评分表配平、强制评分栏、权重账目自洽。

设计要点：**权重要能被算账**。大纲里"专题作业 37%"是一个总数，拆到 8 份材料上的
分配此前只写在正文一句话里；本检查把契约声明的每份材料权重加起来，与
`assessment.levels` 的该项权重对账，任何一侧改动而另一侧没改都会被抓出来。
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

from tools.contract import AssessmentMaterial
from tools.md_utils import find_section, normalize, parse_tables, title_stem
from tools.report import Finding, Severity, Status
from tools.workspace import CheckContext

logger = logging.getLogger(__name__)

_BOLD_RE = re.compile(r"[*_`]")
_WEIGHT_CELL_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|分)")
_BARE_NUMBER_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*$")
_TOLERANCE = 0.51


def _fail(ctx: CheckContext, level: str, subject: str, message: str) -> Finding:
    return Finding("assessment_material", level, ctx.severity("assessment_material"),
                   Status.FAIL, subject, message)


def _pending(ctx: CheckContext, level: str, subject: str, message: str) -> Finding:
    return Finding("assessment_material", level, ctx.severity("assessment_material"),
                   Status.PENDING, subject, message)


def _cell_weight(cell: str) -> float | None:
    """从单元格里取权重：优先 `30%` / `30分`，其次裸数字。"""
    cleaned = _BOLD_RE.sub("", cell).strip()
    match = _WEIGHT_CELL_RE.search(cleaned)
    if match:
        return float(match.group(1))
    bare = _BARE_NUMBER_RE.match(cleaned)
    return float(bare.group(1)) if bare else None


def _row_weight(cells: tuple[str, ...]) -> float | None:
    """一行的权重取自除首列外的第一个可解析单元格（首列是评分维度名）。"""
    for cell in cells[1:]:
        weight = _cell_weight(cell)
        if weight is not None:
            return weight
    return None


def rubric_rows(section_text: str) -> tuple[tuple[str, float], ...]:
    """从「评分标准」章节抽出 (维度名, 权重) 列表。

    取该章节内**权重可解析行数最多**的那张表——评分表之外常还有交付物清单、
    等级说明等表格，按"哪张表最像评分表"选，比取第一张稳。
    """
    best: tuple[tuple[str, float], ...] = ()
    for table in parse_tables_from(section_text):
        rows: list[tuple[str, float]] = []
        for cells in table:
            if not cells or not cells[0].strip():
                continue
            name = _BOLD_RE.sub("", cells[0]).strip()
            if normalize(name) in ("合计", "总计", "总分", "小计"):
                continue
            weight = _row_weight(cells)
            if weight is not None:
                rows.append((name, weight))
        if len(rows) > len(best):
            best = tuple(rows)
    return best


@dataclass(frozen=True)
class _TextDoc:
    """让 md_utils.parse_tables 能吃一段纯文本（它只用 lines 与 fenced）。"""

    lines: tuple[str, ...]
    fenced: tuple[bool, ...]


def parse_tables_from(text: str) -> tuple[tuple[tuple[str, ...], ...], ...]:
    """对一段纯文本做表格解析，跳过代码块内的行。"""
    lines = tuple(text.splitlines())
    fenced: list[bool] = []
    inside = False
    for line in lines:
        if line.lstrip().startswith("```"):
            inside = not inside
            fenced.append(True)
            continue
        fenced.append(inside)
    return parse_tables(_TextDoc(lines=lines, fenced=tuple(fenced)))


def _check_sections(ctx: CheckContext, material: AssessmentMaterial, doc) -> list[Finding]:
    spec = ctx.contract.assessment
    assert spec is not None
    if material.anchored:
        return []
    missing = [
        f"{sec.order}.{sec.title}"
        for sec in spec.sections
        if sec.required and find_section(doc, sec.title) is None
    ]
    if missing:
        return [_fail(ctx, material.level, material.relpath,
                      "缺少必需章节：" + "、".join(missing))]
    return []


def _check_rubric(ctx: CheckContext, material: AssessmentMaterial, doc) -> list[Finding]:
    spec = ctx.contract.assessment
    assert spec is not None
    findings: list[Finding] = []
    rubric_spec = next((s for s in spec.sections if s.section_id == "rubric"), None)
    section = find_section(doc, rubric_spec.title) if rubric_spec else None
    text = section.body if section is not None else doc.text
    rows = rubric_rows(text)
    if not rows:
        return [_fail(ctx, material.level, material.relpath, "「评分标准」中找不到可解析的权重表")]

    total = sum(w for _, w in rows)
    if abs(total - 100) > _TOLERANCE:
        detail = "、".join(f"{n} {w:g}" for n, w in rows)
        findings.append(_fail(ctx, material.level, material.relpath,
                              f"评分表权重之和 {total:g} ≠ 100（{detail}）"))

    is_stats = (
        material.topic_id is not None
        and (material.level, material.topic_id) in ctx.contract.stats_plugin_topics
    )
    for row in spec.rubric_rows:
        applicable = (
            (row.applies_to == "stats_plugin_topics" and is_stats)
            or (row.applies_to == "phd_all" and material.level == "phd")
        )
        if not applicable:
            continue
        hit = next((r for r in rows if title_stem(row.title) in title_stem(r[0])), None)
        if hit is None:
            findings.append(_fail(ctx, material.level, material.relpath,
                                  f"评分表缺少强制评分栏「{row.title}」"))
        elif row.weight is not None and abs(hit[1] - row.weight) > _TOLERANCE:
            findings.append(_fail(ctx, material.level, material.relpath,
                                  f"「{row.title}」权重 {hit[1]:g} ≠ 契约要求的 {row.weight:g}"))
    return findings


def _check_weight_ledger(ctx: CheckContext, level: str) -> list[Finding]:
    """同一考核项下各材料权重之和 == 大纲声明；每层 items 之和 == 100。"""
    spec = ctx.contract.assessment
    assert spec is not None
    findings: list[Finding] = []
    declared = dict(spec.level_items.get(level, ()))
    subject = f"{level} 权重账"

    total = sum(declared.values())
    if abs(total - 100) > _TOLERANCE:
        findings.append(_fail(ctx, level, subject,
                              f"assessment.levels 各项权重之和 {total:g} ≠ 100"))

    actual: dict[str, float] = {}
    for material in spec.for_level(level):
        if material.item and material.weight is not None:
            actual[material.item] = actual.get(material.item, 0.0) + material.weight
    for item, summed in sorted(actual.items()):
        if item not in declared:
            findings.append(_fail(ctx, level, subject,
                                  f"材料计入的考核项「{item}」不在 assessment.levels 中"))
        elif abs(summed - declared[item]) > _TOLERANCE:
            findings.append(_fail(ctx, level, subject,
                                  f"「{item}」各材料权重之和 {summed:g} ≠ 大纲声明的 {declared[item]:g}"))
    for item, weight in declared.items():
        if item not in actual and normalize(item) != normalize(ctx.contract.prereq_item_title):
            findings.append(_fail(ctx, level, subject,
                                  f"考核项「{item}」（{weight:g}%）没有任何材料承载"))
    return findings


def _orphans(ctx: CheckContext, level: str) -> list[Finding]:
    spec = ctx.contract.assessment
    assert spec is not None
    root = ctx.workspace.root / "08_assessment" / level
    if not root.is_dir():
        return []
    declared = {(root / m.file).resolve() for m in spec.for_level(level)}
    findings: list[Finding] = []
    for path in sorted(root.rglob("*.md")):
        if path.resolve() not in declared:
            findings.append(_fail(ctx, level, ctx.workspace.rel(path),
                                  "孤儿材料：存在于文件系统但不在 assessment.materials 中"))
    return findings


def check_assessment_material(ctx: CheckContext) -> list[Finding]:
    """考核材料存在性、章节完整性、评分表配平与权重账目。"""
    spec = ctx.contract.assessment
    if spec is None:
        logger.info("契约未声明 assessment.materials，跳过 assessment_material")
        return []
    findings: list[Finding] = []
    for level in ctx.levels:
        materials = spec.for_level(level)
        if not materials:
            continue
        findings.extend(_check_weight_ledger(ctx, level))
        pending_files: list[str] = []
        for material in materials:
            path = ctx.workspace.root / "08_assessment" / level / material.file
            if not path.is_file():
                pending_files.append(material.file)
                continue
            doc = ctx.workspace.doc(path)
            if doc is None:
                findings.append(_fail(ctx, level, material.relpath, "材料无法解析为 Markdown"))
                continue
            findings.extend(_check_sections(ctx, material, doc))
            if material.graded:
                findings.extend(_check_rubric(ctx, material, doc))
        if pending_files:
            findings.append(_pending(
                ctx, level, f"08_assessment/{level}/",
                f"{len(pending_files)} 份考核材料尚未生成：" + "、".join(pending_files),
            ))
        findings.extend(_orphans(ctx, level))
    return findings
