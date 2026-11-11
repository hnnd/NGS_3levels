"""讲义类检查：必需章节、前置引用、L1 映射、体量、参考资料。

所有检查只作用于"契约目录下确实存在讲义文件"的专题；尚未生成的材料聚合为
一条 PENDING，避免在材料未就绪阶段产生海量噪声。
"""

from __future__ import annotations

import http.client
import logging
import re
import urllib.error
import urllib.request
from dataclasses import dataclass

from tools.contract import Topic
from tools.md_utils import (
    MarkdownDoc,
    extract_labeled_dois,
    extract_urls,
    find_section,
    is_valid_doi,
    is_valid_url,
    normalize,
)
from tools.report import Finding, Status
from tools.workspace import CheckContext

logger = logging.getLogger(__name__)

# 负向后视排除路径写法：`02_lectures/prerequisites/l1_phd/l1_phd.md`、
# `l1_phd_selftest.md` 里的 token 是**文件路径**，不是模块 id 引用。
# 不排除的话，讲义里正常写出材料路径就会被误判为引用了不存在的模块。
# 后面紧跟 `/`（路径的目录段）或已知扩展名（文件名）时，这不是模块 id 引用
_PATH_TAIL = r"(?!/|\.(?:md|py|R|sh|ya?ml)\b)"
# `\b` 不可省：没有它，正则会回溯把 `l0_06_stats` 截成 `l0_06_stat` 来绕过前瞻
_L0_REF_RE = re.compile(r"(?i)(?<![\w/])l0_\d{1,2}_[a-z0-9_]+\b" + _PATH_TAIL)
_L1_REF_RE = re.compile(r"(?i)(?<![\w/])l1_[a-z0-9_]+\b" + _PATH_TAIL)
_NO_STATS_SENTINEL = "无独立统计要点"
_NO_PREREQ_SENTINEL = "无前置"
_USER_AGENT = "validate-course/1.0"


@dataclass(frozen=True)
class ResolvedLecture:
    """已在磁盘上找到讲义文件的专题。"""

    topic: Topic
    doc: MarkdownDoc
    rel_path: str


def _fail(ctx: CheckContext, check: str, level: str, subject: str, message: str) -> Finding:
    return Finding(check, level, ctx.severity(check), Status.FAIL, subject, message)


def _pending(ctx: CheckContext, check: str, level: str, subject: str, message: str) -> Finding:
    return Finding(check, level, ctx.severity(check), Status.PENDING, subject, message)


def _section_title(ctx: CheckContext, section_id: str, default: str) -> str:
    for spec in ctx.contract.sections:
        if spec.section_id == section_id:
            return spec.title
    return default


def resolve_lectures(ctx: CheckContext, level: str) -> tuple[list[ResolvedLecture], list[str]]:
    """返回 (已生成的讲义, 尚未生成的专题 id 列表)。"""
    resolved: list[ResolvedLecture] = []
    pending: list[str] = []
    for ref in ctx.workspace.lecture_refs(level):
        primary = ref.primary
        doc = ctx.workspace.doc(primary) if primary is not None else None
        if doc is None:
            pending.append(ref.topic.topic_id)
            continue
        resolved.append(
            ResolvedLecture(topic=ref.topic, doc=doc, rel_path=ctx.workspace.rel(doc.path))
        )
    return resolved, pending


def _pending_note(ctx: CheckContext, check: str, level: str, pending: list[str]) -> list[Finding]:
    if not pending:
        return []
    return [
        _pending(ctx, check, level, f"{len(pending)} 个专题",
                 f"讲义尚未生成，跳过本项检查：{', '.join(pending)}")
    ]


def check_required_sections(ctx: CheckContext) -> list[Finding]:
    """每份讲义须含全部 required 章节；统计插件 / AI 任务按适用范围检查。"""
    check = "required_sections"
    findings: list[Finding] = []
    stats_title = _section_title(ctx, "stats_plugin", "统计插件")
    for level in ctx.levels:
        resolved, pending = resolve_lectures(ctx, level)
        findings.extend(_pending_note(ctx, check, level, pending))
        for item in resolved:
            key = (level, item.topic.topic_id)
            is_stats = key in ctx.contract.stats_plugin_topics
            is_ai = key in ctx.contract.ai_task_topics
            missing: list[str] = []
            for spec in ctx.contract.sections:
                if not spec.required:
                    continue
                if spec.applies_to == "ai_task_topics" and not is_ai:
                    continue
                if find_section(item.doc, spec.title) is None:
                    missing.append(f"{spec.order}.{spec.title}")
            if missing:
                findings.append(
                    _fail(ctx, check, level, f"{item.topic.topic_id} @ {item.rel_path}",
                          f"缺少 {len(missing)} 个必需章节：{', '.join(missing)}")
                )
            findings.extend(_check_stats_body(ctx, level, item, stats_title, is_stats))
    return findings


def _check_stats_body(
    ctx: CheckContext,
    level: str,
    item: ResolvedLecture,
    stats_title: str,
    is_stats: bool,
) -> list[Finding]:
    check = "required_sections"
    section = find_section(item.doc, stats_title)
    if section is None:
        return []
    body = normalize(section.body)
    subject = f"{item.topic.topic_id} @ {item.rel_path}"
    if is_stats and (not body or _NO_STATS_SENTINEL in body):
        return [
            _fail(ctx, check, level, subject,
                  f"该专题在 stats_plugin_topics 名单内，「{stats_title}」章节必须写实，"
                  f"不能为空或写「{_NO_STATS_SENTINEL}」")
        ]
    if not is_stats and _NO_STATS_SENTINEL not in body:
        return [
            _fail(ctx, check, level, subject,
                  f"该专题不在 stats_plugin_topics 名单内，「{stats_title}」章节须显式写明"
                  f"「本讲{_NO_STATS_SENTINEL}」")
        ]
    return []


def check_prereq_reference(ctx: CheckContext) -> list[Finding]:
    """讲义「前置检查」章节引用的 L0/L1 模块 id 必须存在于契约。"""
    check = "prereq_reference"
    title = _section_title(ctx, "prerequisites", "前置检查")
    findings: list[Finding] = []
    for level in ctx.levels:
        resolved, pending = resolve_lectures(ctx, level)
        findings.extend(_pending_note(ctx, check, level, pending))
        for item in resolved:
            section = find_section(item.doc, title)
            if section is None:
                continue  # 章节缺失由 required_sections 报告，此处不重复
            subject = f"{item.topic.topic_id} @ {item.rel_path}"
            l0_refs = {m.group(0).lower() for m in _L0_REF_RE.finditer(section.body)}
            l1_refs = {m.group(0).lower() for m in _L1_REF_RE.finditer(section.body)}
            unknown_l0 = sorted(r for r in l0_refs if r not in ctx.contract.prereq_l0_ids)
            unknown_l1 = sorted(r for r in l1_refs if r not in ctx.contract.prereq_l1_ids)
            if unknown_l0:
                findings.append(
                    _fail(ctx, check, level, subject,
                          f"引用了契约 prerequisite_packs.L0 中不存在的模块 id："
                          f"{', '.join(unknown_l0)}")
                )
            if unknown_l1:
                findings.append(
                    _fail(ctx, check, level, subject,
                          f"引用了契约 prerequisite_packs.L1 中不存在的模块 id："
                          f"{', '.join(unknown_l1)}（契约 L1 只定义 mappings，未定义模块 id）")
                )
            if not l0_refs and not l1_refs and _NO_PREREQ_SENTINEL not in normalize(section.body):
                findings.append(
                    _fail(ctx, check, level, subject,
                          f"「{title}」章节未声明任何 L0/L1 模块 id")
                )
    return findings


def check_l1_mapping_valid(ctx: CheckContext) -> list[Finding]:
    """每条 L1 映射的目标（硕士专题 + 章节）必须实际存在。"""
    check = "l1_mapping_valid"
    findings: list[Finding] = []
    if "phd" not in ctx.levels:
        return findings
    for mapping in ctx.contract.l1_mappings:
        subject = f"{mapping.phd_topic_ref} -> {mapping.target_topic_ref} §{mapping.section}"
        phd_topic = ctx.contract.resolve_topic_ref("phd", mapping.phd_topic_ref)
        if phd_topic is None:
            findings.append(
                _fail(ctx, check, "phd", subject,
                      f"L1 映射的 phd_topic「{mapping.phd_topic_ref}」在 curriculum.phd 中不存在")
            )
            continue
        target = ctx.contract.resolve_topic_ref(mapping.target_level, mapping.target_topic_ref)
        if target is None:
            findings.append(
                _fail(ctx, check, "phd", subject,
                      f"L1 映射的目标专题「{mapping.target_topic_ref}」在 "
                      f"curriculum.{mapping.target_level} 中不存在")
            )
            continue
        ref = ctx.workspace.lecture_ref(target)
        docs = [d for d in (ctx.workspace.doc(p) for p in ref.files) if d is not None]
        if not docs:
            findings.append(
                _pending(ctx, check, "phd", subject,
                         f"目标讲义尚未生成：{ctx.workspace.rel(ref.directory)}")
            )
            continue
        if not any(find_section(doc, mapping.section) is not None for doc in docs):
            findings.append(
                _fail(ctx, check, "phd", subject,
                      f"目标讲义 {ctx.workspace.rel(docs[0].path)} 中不存在章节"
                      f"「{mapping.section}」")
            )
    return findings


def check_lecture_size(ctx: CheckContext) -> list[Finding]:
    """讲义行数落在契约声明的区间内（越界仅告警）。"""
    check = "lecture_size"
    findings: list[Finding] = []
    for level in ctx.levels:
        target = ctx.contract.size_targets.get(level)
        if target is None:
            continue
        low, high = target
        resolved, pending = resolve_lectures(ctx, level)
        findings.extend(_pending_note(ctx, check, level, pending))
        for item in resolved:
            count = item.doc.line_count
            if count < low or count > high:
                findings.append(
                    _fail(ctx, check, level, f"{item.topic.topic_id} @ {item.rel_path}",
                          f"讲义 {count} 行，超出目标区间 {low}-{high} 行")
                )
    return findings


def check_reference_syntax(ctx: CheckContext) -> list[Finding]:
    """参考资料中的 DOI 格式与 URL 语法必须合法。"""
    check = "reference_syntax"
    title = _section_title(ctx, "references", "参考资料")
    findings: list[Finding] = []
    for level in ctx.levels:
        resolved, pending = resolve_lectures(ctx, level)
        findings.extend(_pending_note(ctx, check, level, pending))
        for item in resolved:
            section = find_section(item.doc, title)
            if section is None:
                continue  # 章节缺失由 required_sections 报告
            subject = f"{item.topic.topic_id} @ {item.rel_path}"
            bad_dois = [d for d in extract_labeled_dois(section.body) if not is_valid_doi(d)]
            if bad_dois:
                findings.append(
                    _fail(ctx, check, level, subject,
                          f"DOI 格式不合法（应形如 10.xxxx/...）：{', '.join(bad_dois)}")
                )
            bad_urls = [u for u in extract_urls(section.body) if not is_valid_url(u)]
            if bad_urls:
                findings.append(
                    _fail(ctx, check, level, subject,
                          f"URL 语法不合法：{', '.join(bad_urls)}")
                )
    return findings


def _probe(url: str, timeout: float) -> str | None:
    """探测 URL 可达性；可达返回 None，否则返回失败原因。"""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status >= 400:
                return f"HTTP {response.status}"
            return None
    except urllib.error.HTTPError as exc:
        return None if exc.code < 400 else f"HTTP {exc.code}"
    except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as exc:
        return f"{type(exc).__name__}: {exc}"


def check_reference_reachable(ctx: CheckContext) -> list[Finding]:
    """参考资料链接的网络可达性（需 --check-links 显式开启）。"""
    check = "reference_reachable"
    title = _section_title(ctx, "references", "参考资料")
    findings: list[Finding] = []
    if not ctx.check_links:
        return findings
    for level in ctx.levels:
        resolved, _ = resolve_lectures(ctx, level)
        for item in resolved:
            section = find_section(item.doc, title)
            if section is None:
                continue
            subject = f"{item.topic.topic_id} @ {item.rel_path}"
            for url in sorted(set(extract_urls(section.body))):
                if not is_valid_url(url):
                    continue
                reason = _probe(url, ctx.link_timeout)
                if reason is not None:
                    findings.append(_fail(ctx, check, level, subject, f"{url} 不可达（{reason}）"))
    return findings
