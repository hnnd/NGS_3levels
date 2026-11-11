"""结构类检查：学时配平、大纲—契约对应、讲义目录对应、考核项覆盖。"""

from __future__ import annotations

import logging
import re

from tools.contract import Topic
from tools.md_utils import (
    extract_weight_percent,
    normalize,
    parse_numbered_topics,
    parse_tables,
    title_stem,
)
from tools.report import Finding, Severity, Status
from tools.workspace import CheckContext

logger = logging.getLogger(__name__)

_BOLD_RE = re.compile(r"[*_`]")
_NUMBER_RE = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*$")


def _fail(ctx: CheckContext, check: str, level: str, subject: str, message: str) -> Finding:
    return Finding(check, level, ctx.severity(check), Status.FAIL, subject, message)


def _pending(ctx: CheckContext, check: str, level: str, subject: str, message: str) -> Finding:
    return Finding(check, level, ctx.severity(check), Status.PENDING, subject, message)


def _titles_match(left: str, right: str) -> bool:
    """标题主干互相包含即视为同一专题（容忍括注、学时标注与装饰符）。"""
    a, b = title_stem(left), title_stem(right)
    return bool(a) and bool(b) and (a in b or b in a)


def check_hours_balance(ctx: CheckContext) -> list[Finding]:
    """学时配平：课堂学时之和 == total_hours；异步单元学时 == 估算值。"""
    check = "hours_balance"
    findings: list[Finding] = []
    for level in ctx.levels:
        spec = ctx.contract.levels[level]
        topics = ctx.contract.curriculum.get(level, ())
        if spec.classroom_breakdown:
            total = sum(hours for _, hours in spec.classroom_breakdown)
            detail = " + ".join(f"{k}={v:g}" for k, v in spec.classroom_breakdown)
            if total != spec.total_hours:
                findings.append(
                    _fail(ctx, check, level, f"levels.{level}.classroom_breakdown",
                          f"课堂学时之和 {total:g} != total_hours {spec.total_hours:g}（{detail}）")
                )
        else:
            total = sum(t.hours for t in topics)
            if total != spec.total_hours:
                findings.append(
                    _fail(ctx, check, level, f"curriculum.{level}",
                          f"{len(topics)} 个专题学时之和 {total:g} != total_hours "
                          f"{spec.total_hours:g}")
                )
        findings.extend(_check_async_hours(ctx, level))
    return findings


def _check_async_hours(ctx: CheckContext, level: str) -> list[Finding]:
    check = "hours_balance"
    spec = ctx.contract.levels[level]
    if not spec.async_units:
        return []
    findings: list[Finding] = []
    known = {t.topic_id: t for t in ctx.contract.curriculum.get(level, ())}
    missing = [u for u in spec.async_units if u not in known]
    if missing:
        findings.append(
            _fail(ctx, check, level, f"levels.{level}.async_units",
                  f"async_units 引用了 curriculum 中不存在的单元 id：{', '.join(missing)}")
        )
    if spec.async_hours_estimate is None:
        return findings
    total = sum(known[u].hours for u in spec.async_units if u in known)
    if total != spec.async_hours_estimate:
        findings.append(
            _fail(ctx, check, level, f"levels.{level}.async_hours_estimate",
                  f"异步单元学时之和 {total:g} != async_hours_estimate "
                  f"{spec.async_hours_estimate:g}")
        )
    return findings


def check_syllabus_topic_match(ctx: CheckContext) -> list[Finding]:
    """契约专题标题须出现在大纲中，且大纲不含契约外专题。"""
    check = "syllabus_topic_match"
    findings: list[Finding] = []
    for level in ctx.levels:
        path = ctx.workspace.syllabus_path(level)
        doc = ctx.workspace.syllabus_doc(level)
        rel = ctx.workspace.rel(path)
        if doc is None:
            findings.append(_pending(ctx, check, level, rel, "大纲文件尚未生成"))
            continue
        topics = ctx.contract.curriculum.get(level, ())
        body = normalize(doc.text)
        for topic in topics:
            if normalize(topic.title) not in body:
                findings.append(
                    _fail(ctx, check, level, f"{topic.topic_id} @ {rel}",
                          f"契约专题标题「{topic.title}」未出现在大纲中")
                )
        listed = parse_numbered_topics(doc)
        matched: set[str] = set()
        for number, title in listed:
            hits = [t.topic_id for t in topics if _titles_match(title, t.title)]
            if not hits:
                findings.append(
                    _fail(ctx, check, level, f"{rel}:{number}",
                          f"大纲列出契约外的专题「{title}」")
                )
            matched.update(hits)
        # 同一专题标题可能在大纲中重复出现（如附录再列一遍），因此比对的是被覆盖的
        # 专题集合而非标题出现次数。
        if listed and len(matched) != len(topics):
            uncovered = [t.topic_id for t in topics if t.topic_id not in matched]
            findings.append(
                _fail(ctx, check, level, rel,
                      f"大纲的专题标题未覆盖契约专题：{', '.join(uncovered)}")
            )
    return findings


def check_lecture_dir_match(ctx: CheckContext) -> list[Finding]:
    """契约专题须有讲义目录且含讲义文件；不得存在契约外的孤儿目录。"""
    check = "lecture_dir_match"
    findings: list[Finding] = []
    for level in ctx.levels:
        root = ctx.workspace.lecture_root(level)
        if not root.is_dir():
            findings.append(
                _pending(ctx, check, level, ctx.workspace.rel(root), "讲义根目录尚未创建")
            )
            continue
        for ref in ctx.workspace.lecture_refs(level):
            rel = ctx.workspace.rel(ref.directory)
            if not ref.dir_exists:
                findings.append(
                    _pending(ctx, check, level, f"{ref.topic.topic_id} @ {rel}", "讲义目录尚未创建")
                )
            elif not ref.has_lecture:
                findings.append(
                    _pending(ctx, check, level, f"{ref.topic.topic_id} @ {rel}",
                             "目录存在但无 .md 讲义文件")
                )
        for orphan in ctx.workspace.orphan_lecture_dirs(level):
            findings.append(
                _fail(ctx, check, level, ctx.workspace.rel(orphan),
                      "孤儿目录：存在于文件系统但不在契约 curriculum 中")
            )
    return findings


def _row_weight(cells: tuple[str, ...]) -> float | None:
    percent = extract_weight_percent(cells)
    if percent is not None:
        return percent
    for cell in cells[1:]:
        match = _NUMBER_RE.match(_BOLD_RE.sub("", cell))
        if match:
            return float(match.group(1))
    return None


def _stats_topics(ctx: CheckContext, level: str) -> list[Topic]:
    ids = {tid for lvl, tid in ctx.contract.stats_plugin_topics if lvl == level}
    return [t for t in ctx.contract.curriculum.get(level, ()) if t.topic_id in ids]


def check_assessment_coverage(ctx: CheckContext) -> list[Finding]:
    """大纲评估表须含「前置准备」项且权重在契约区间内；统计插件专题须有方法说明评分项。"""
    check = "assessment_coverage"
    findings: list[Finding] = []
    low, high = ctx.contract.prereq_weight_range
    title = ctx.contract.prereq_item_title
    for level in ctx.levels:
        doc = ctx.workspace.syllabus_doc(level)
        rel = ctx.workspace.rel(ctx.workspace.syllabus_path(level))
        if doc is None:
            findings.append(_pending(ctx, check, level, rel, "大纲文件尚未生成"))
            continue
        rows = [row for table in parse_tables(doc) for row in table]
        matched = [r for r in rows if normalize(_BOLD_RE.sub("", r[0])).startswith(normalize(title))]
        if not matched:
            findings.append(
                _fail(ctx, check, level, rel, f"评估表中缺少「{title}」评分项")
            )
        else:
            weight = _row_weight(matched[0])
            if weight is None:
                findings.append(
                    _fail(ctx, check, level, rel,
                          f"「{title}」行无法解析权重：{' | '.join(matched[0])}")
                )
            elif not low <= weight <= high:
                findings.append(
                    _fail(ctx, check, level, rel,
                          f"「{title}」权重 {weight:g}% 不在契约区间 {low:g}-{high:g}%")
                )
        findings.extend(_check_stats_rubric(ctx, level, doc.text, rel))
    return findings


def _check_stats_rubric(ctx: CheckContext, level: str, syllabus_text: str, rel: str) -> list[Finding]:
    check = "assessment_coverage"
    topics = _stats_topics(ctx, level)
    if not topics:
        return []
    rubric = ctx.contract.stats_rubric_title
    files = ctx.workspace.assessment_files(level)
    corpus = normalize(syllabus_text)
    for path in files:
        doc = ctx.workspace.doc(path)
        if doc is not None:
            corpus += normalize(doc.text)
    if normalize(rubric) in corpus:
        return []
    ids = ", ".join(t.topic_id for t in topics)
    where = f"{rel} + 08_assessment/{level}/"
    if not files:
        return [
            _pending(ctx, check, level, where,
                     f"统计插件专题（{ids}）的考核材料尚未生成，无法确认含「{rubric}」评分项")
        ]
    return [
        _fail(ctx, check, level, where,
              f"统计插件专题（{ids}）的考核材料中未出现「{rubric}」评分项")
    ]


# --- 脚本引用检查 -------------------------------------------------------------
# 【第 6 轮新增】m07 讲义引用的 `03_code/master/scripts/07_compositional_analysis.R`
# 缺失了两轮无人发现——校验器此前只查"讲义→L0 题号"与"讲义→章节"，
# 没查"讲义→脚本文件"。这一项把跨目录引用也纳入。

_SCRIPT_EXT = r"(?:sh|R|r|py|nf|smk|Rmd|qmd)"
_PATH_REF_RE = re.compile(rf"(0[0-9]_[a-z_]+/[A-Za-z0-9_./-]+\.{_SCRIPT_EXT})\b")
# 裸文件名只认仓库命名规范 `NN_name.ext`（PROJECT.md §3.1），避免误伤学生自建文件
_BARE_REF_RE = re.compile(rf"`(\d{{2}}_[A-Za-z0-9_]+\.{_SCRIPT_EXT})`")
_SCAN_DIRS = ("01_syllabus", "02_lectures", "04_slides", "05_videos",
              "08_assessment", "09_resources", "03_code")


def _ref_level(rel: str) -> str:
    for level in ("undergraduate", "master", "phd"):
        if f"/{level}/" in f"/{rel}":
            return level
    return "shared"


def check_script_reference(ctx: CheckContext) -> list[Finding]:
    """材料中引用的脚本文件必须真实存在。

    两类引用分别处理：
    - **显式路径**（`03_code/master/scripts/x.sh`）→ error，路径写错就是断链
    - **裸文件名**（`` `04_deseq2_analysis.R` ``）→ warning，按 03_code 下同名文件查找，
      找不到多半是重命名后漏改，但也可能是学生自建文件，故只告警
    """
    check = "script_reference"
    root = ctx.workspace.root
    code_names = {p.name for p in root.glob("03_code/**/*") if p.is_file()}
    findings: list[Finding] = []
    levels = set(ctx.levels) | {"shared"}
    for scan in _SCAN_DIRS:
        base = root / scan
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.md")):
            if path.name.startswith("."):
                continue
            rel = ctx.workspace.rel(path)
            level = _ref_level(rel)
            if level not in levels:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                logger.warning("读取 %s 失败：%s", rel, exc)
                continue
            for match in sorted({m.group(1) for m in _PATH_REF_RE.finditer(text)}):
                if not (root / match).exists():
                    findings.append(_fail(ctx, check, level, rel,
                                          f"引用的脚本不存在：{match}"))
            for match in sorted({m.group(1) for m in _BARE_REF_RE.finditer(text)}):
                if match not in code_names:
                    findings.append(Finding(
                        check, level, Severity.WARNING, Status.FAIL, rel,
                        f"引用的脚本名在 03_code/ 下找不到同名文件：{match}"))
    return findings
