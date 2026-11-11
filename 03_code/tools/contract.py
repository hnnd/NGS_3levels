"""课程结构契约的加载与内存表示。

`00_design/course_contract.yaml` 是课程结构的唯一真值来源。本模块只负责把
YAML 解析成不可变对象，不做任何校验判断——判断全部放在 checks_* 模块里。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

logger = logging.getLogger(__name__)

CONTRACT_RELPATH = "00_design/course_contract.yaml"
LEVEL_ORDER: tuple[str, ...] = ("undergraduate", "master", "phd")


class ContractError(RuntimeError):
    """契约文件缺失、YAML 语法错误，或缺少校验器依赖的必需字段。"""


@dataclass(frozen=True)
class SectionSpec:
    """讲义模板中的一个章节。"""

    order: int
    section_id: str
    title: str
    required: bool
    applies_to: str | None  # None / "stats_plugin_topics" / "ai_task_topics"


@dataclass(frozen=True)
class Topic:
    """一个专题（本科称"单元"）。"""

    topic_id: str
    level: str
    title: str
    dir_name: str
    hours: float
    core_tools: tuple[str, ...]
    mode: str


@dataclass(frozen=True)
class EnvFile:
    """一个层次下的单个 conda 环境（按任务内容拆分）。"""

    file: str
    name: str
    purpose: str
    covers: tuple[str, ...]


@dataclass(frozen=True)
class Level:
    """一个层次的路径与学时账。"""

    name: str
    title: str
    total_hours: float
    lecture_dir: str
    code_dir: str
    env_files: tuple[EnvFile, ...]
    syllabus: str
    classroom_breakdown: tuple[tuple[str, float], ...]
    async_units: tuple[str, ...]
    async_hours_estimate: float | None


@dataclass(frozen=True)
class L1Mapping:
    """博士专题对硕士讲义章节的依赖映射。"""

    phd_topic_ref: str
    target_level: str
    target_topic_ref: str
    section: str


@dataclass(frozen=True)
class CheckSpec:
    """validation.checks 中的一项检查声明。"""

    check_id: str
    severity: str
    default_enabled: bool
    desc: str


@dataclass(frozen=True)
class SlideSpec:
    """slide_template：幻灯片目录、文件命名、必需 @section 与页数区间。"""

    dir: str
    file_suffix: str
    lecture_suffix: str
    frontmatter_required: Mapping[str, Any]
    section_marker: str
    sections: tuple[SectionSpec, ...]
    deck_size_targets: Mapping[str, tuple[int, int]]

    def marker_for(self, section_id: str) -> str:
        return self.section_marker.replace("{id}", section_id)


@dataclass(frozen=True)
class RubricRow:
    """考核材料评分表中的强制评分栏。"""

    row_id: str
    title: str
    applies_to: str          # "stats_plugin_topics" / "phd_all"
    weight: float | None


@dataclass(frozen=True)
class AssessmentMaterial:
    """一份考核材料的契约声明。"""

    level: str
    file: str                # 相对 08_assessment/<level>/
    topic_id: str | None
    item: str | None         # 计入 assessment.levels 的哪个考核项
    weight: float | None     # None = 模板/说明，不单独计分
    anchored: bool

    @property
    def relpath(self) -> str:
        return f"08_assessment/{self.level}/{self.file}"

    @property
    def graded(self) -> bool:
        return self.weight is not None


@dataclass(frozen=True)
class AssessmentSpec:
    """assessment.template + assessment.materials + assessment.levels 的只读视图。"""

    sections: tuple[SectionSpec, ...]
    rubric_rows: tuple[RubricRow, ...]
    materials: tuple[AssessmentMaterial, ...]
    level_items: Mapping[str, tuple[tuple[str, float], ...]]

    def for_level(self, level: str) -> tuple[AssessmentMaterial, ...]:
        return tuple(m for m in self.materials if m.level == level)

    def row(self, row_id: str) -> RubricRow | None:
        for r in self.rubric_rows:
            if r.row_id == row_id:
                return r
        return None


@dataclass(frozen=True)
class Contract:
    """整份契约的只读视图。"""

    root: Path
    path: Path
    levels: Mapping[str, Level]
    curriculum: Mapping[str, tuple[Topic, ...]]
    sections: tuple[SectionSpec, ...]
    stats_plugin_topics: frozenset[tuple[str, str]]
    ai_task_topics: frozenset[tuple[str, str]]
    prereq_l0_ids: frozenset[str]
    prereq_l1_ids: frozenset[str]
    l1_mappings: tuple[L1Mapping, ...]
    size_targets: Mapping[str, tuple[int, int]]
    checks: tuple[CheckSpec, ...]
    prereq_item_title: str
    prereq_weight_range: tuple[float, float]
    stats_rubric_title: str
    env_exempt_tools: frozenset[str]
    slides: SlideSpec | None = None
    assessment: AssessmentSpec | None = None

    def is_env_exempt(self, tool: str) -> bool:
        """该工具是否豁免 conda 环境覆盖检查（系统/许可/非 conda 渠道工具）。"""
        return tool.strip().lower() in self.env_exempt_tools

    def topic(self, level: str, topic_id: str) -> Topic | None:
        """按层次与专题 id 取专题；找不到返回 None。"""
        for item in self.curriculum.get(level, ()):
            if item.topic_id == topic_id:
                return item
        return None

    def resolve_topic_ref(self, level: str, ref: str) -> Topic | None:
        """解析契约内的专题引用。

        L1 映射写作 `p03_host_pathogen` / `m04_rnaseq`，而 curriculum 的 id 是
        `p03` / `m04`——取第一个下划线前的前缀做解析。
        """
        direct = self.topic(level, ref)
        if direct is not None:
            return direct
        return self.topic(level, ref.split("_", 1)[0])


def _require(data: Mapping[str, Any], key: str, ctx: str) -> Any:
    if key not in data:
        raise ContractError(f"契约缺少必需字段：{ctx}.{key}")
    return data[key]


def _as_pair(raw: Any, ctx: str) -> tuple[float, float]:
    if not isinstance(raw, Sequence) or isinstance(raw, str) or len(raw) != 2:
        raise ContractError(f"{ctx} 需为 [min, max] 两元列表，实际为 {raw!r}")
    return float(raw[0]), float(raw[1])


def _parse_level(name: str, raw: Mapping[str, Any]) -> Level:
    breakdown_raw = raw.get("classroom_breakdown") or {}
    breakdown = tuple((str(k), float(v)) for k, v in breakdown_raw.items())
    async_hours = raw.get("async_hours_estimate")
    return Level(
        name=name,
        title=str(raw.get("title", name)),
        total_hours=float(_require(raw, "total_hours", f"levels.{name}")),
        lecture_dir=str(_require(raw, "lecture_dir", f"levels.{name}")),
        code_dir=str(raw.get("code_dir", "")),
        env_files=tuple(
            EnvFile(
                file=str(_require(item, "file", f"levels.{name}.env_files")),
                name=str(item.get("name", "")),
                purpose=str(item.get("purpose", "")),
                covers=tuple(str(x) for x in item.get("covers", ())),
            )
            for item in _require(raw, "env_files", f"levels.{name}")
            if isinstance(item, dict)
        ),
        syllabus=str(_require(raw, "syllabus", f"levels.{name}")),
        classroom_breakdown=breakdown,
        async_units=tuple(str(u) for u in raw.get("async_units", ())),
        async_hours_estimate=None if async_hours is None else float(async_hours),
    )


def _parse_topics(level: str, raw_items: Sequence[Mapping[str, Any]]) -> tuple[Topic, ...]:
    topics: list[Topic] = []
    for raw in raw_items:
        ctx = f"curriculum.{level}"
        topics.append(
            Topic(
                topic_id=str(_require(raw, "id", ctx)),
                level=level,
                title=str(_require(raw, "title", ctx)),
                dir_name=str(_require(raw, "dir", ctx)),
                hours=float(_require(raw, "hours", ctx)),
                core_tools=tuple(str(t) for t in raw.get("core_tools", ())),
                mode=str(raw.get("mode", "")),
            )
        )
    return tuple(topics)


def _parse_sections(raw_items: Sequence[Mapping[str, Any]]) -> tuple[SectionSpec, ...]:
    specs: list[SectionSpec] = []
    for raw in raw_items:
        specs.append(
            SectionSpec(
                order=int(_require(raw, "order", "lecture_template.sections")),
                section_id=str(_require(raw, "id", "lecture_template.sections")),
                title=str(_require(raw, "title", "lecture_template.sections")),
                required=bool(raw.get("required", False)),
                applies_to=None if raw.get("applies_to") is None else str(raw["applies_to"]),
            )
        )
    return tuple(sorted(specs, key=lambda s: s.order))


def _parse_topic_tags(raw_items: Sequence[Mapping[str, Any]]) -> frozenset[tuple[str, str]]:
    return frozenset((str(item["level"]), str(item["id"])) for item in raw_items)


def _parse_assessment(raw: Mapping[str, Any]) -> tuple[str, tuple[float, float], str]:
    title = "前置准备"
    weight_range = (5.0, 10.0)
    for item in raw.get("common_items", ()):
        if item.get("id") == "prerequisite_prep":
            title = str(item.get("title", title))
            weight_range = _as_pair(
                item.get("weight_percent", [5, 10]),
                "assessment.common_items.prerequisite_prep.weight_percent",
            )
    rubric_title = "方法选择与结果可信度说明"
    for item in raw.get("rubric_requirements", ()):
        if item.get("id") == "method_justification":
            rubric_title = str(item.get("title", rubric_title))
    return title, weight_range, rubric_title


def _parse_assessment_spec(raw: Mapping[str, Any] | None) -> AssessmentSpec | None:
    """解析 assessment.template / materials / levels；未声明 materials 时返回 None。"""
    if not raw or "materials" not in raw:
        return None
    template = raw.get("template", {}) or {}
    sections = tuple(
        SectionSpec(
            order=i + 1,
            section_id=str(_require(item, "id", "assessment.template.sections")),
            title=str(item.get("title", item["id"])),
            required=bool(item.get("required", True)),
            applies_to=None,
        )
        for i, item in enumerate(template.get("sections", ()))
    )
    rows = tuple(
        RubricRow(
            row_id=str(_require(item, "id", "assessment.template.rubric_rows")),
            title=str(item.get("title", item["id"])),
            applies_to=str(item.get("applies_to", "")),
            weight=float(item["weight"]) if item.get("weight") is not None else None,
        )
        for item in template.get("rubric_rows", ())
    )
    materials: list[AssessmentMaterial] = []
    for level, entries in (raw.get("materials") or {}).items():
        for entry in entries or ():
            materials.append(
                AssessmentMaterial(
                    level=str(level),
                    file=str(_require(entry, "file", f"assessment.materials.{level}")),
                    topic_id=str(entry["topic"]) if entry.get("topic") else None,
                    item=str(entry["item"]) if entry.get("item") else None,
                    weight=float(entry["weight"]) if entry.get("weight") is not None else None,
                    anchored=bool(entry.get("anchored", False)),
                )
            )
    level_items = {
        str(level): tuple(
            (str(item.get("title", "")), float(item.get("weight", 0)))
            for item in (spec.get("items") or ())
        )
        for level, spec in (raw.get("levels") or {}).items()
    }
    return AssessmentSpec(
        sections=sections,
        rubric_rows=rows,
        materials=tuple(materials),
        level_items=level_items,
    )


def _parse_slides(raw: Mapping[str, Any] | None) -> SlideSpec | None:
    """解析 slide_template；契约未声明时返回 None（幻灯片检查整体跳过）。"""
    if not raw:
        return None
    sections = [
        SectionSpec(
            order=i + 1,
            section_id=str(_require(item, "id", "slide_template.sections")),
            title=str(item.get("title", item["id"])),
            required=bool(item.get("required", True)),
            applies_to=item.get("applies_to"),
        )
        for i, item in enumerate(raw.get("sections", ()))
    ]
    targets = {
        name: (int(spec["min"]), int(spec["max"]))
        for name, spec in raw.get("deck_size_targets", {}).items()
    }
    fm = raw.get("frontmatter_required", {})
    return SlideSpec(
        dir=str(raw.get("dir", "04_slides")),
        file_suffix=str(raw.get("file_suffix", "_slides.md")),
        lecture_suffix=str(raw.get("lecture_suffix", "_lecture.md")),
        frontmatter_required=dict(fm) if isinstance(fm, Mapping) else {},
        section_marker=str(raw.get("section_marker", "<!-- @section: {id} -->")),
        sections=tuple(sections),
        deck_size_targets=targets,
    )


def load_contract(root: Path) -> Contract:
    """从仓库根目录加载契约。

    Args:
        root: 仓库根目录（含 00_design/）。

    Returns:
        解析后的只读 Contract 对象。

    Raises:
        ContractError: 文件不存在、YAML 语法错误或缺少必需字段。
    """
    path = root / CONTRACT_RELPATH
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"无法读取契约文件 {path}: {exc}") from exc
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ContractError(f"契约 YAML 解析失败 {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError(f"契约根节点应为映射，实际为 {type(data).__name__}")

    exempt_raw = data.get("env_exempt_tools", ())
    exempt_tools: set[str] = set()
    if isinstance(exempt_raw, list):
        for item in exempt_raw:
            if isinstance(item, dict) and "tool" in item:
                exempt_tools.add(str(item["tool"]).strip().lower())
            elif isinstance(item, str):
                exempt_tools.add(item.strip().lower())

    levels_raw = _require(data, "levels", "<root>")
    curriculum_raw = _require(data, "curriculum", "<root>")
    template_raw = _require(data, "lecture_template", "<root>")
    packs_raw = data.get("prerequisite_packs", {})
    validation_raw = data.get("validation", {})

    levels = {name: _parse_level(name, raw) for name, raw in levels_raw.items()}
    curriculum = {name: _parse_topics(name, raw) for name, raw in curriculum_raw.items()}

    l0_ids = frozenset(str(m["id"]) for m in packs_raw.get("L0", {}).get("modules", ()))
    l1_raw = packs_raw.get("L1", {})
    l1_ids = frozenset(str(m["id"]) for m in l1_raw.get("modules", ()))
    l1_mappings: list[L1Mapping] = []
    for mapping in l1_raw.get("mappings", ()):
        for dep in mapping.get("depends_on", ()):
            l1_mappings.append(
                L1Mapping(
                    phd_topic_ref=str(mapping.get("phd_topic", "")),
                    target_level=str(dep.get("level", "")),
                    target_topic_ref=str(dep.get("topic", "")),
                    section=str(dep.get("section", "")),
                )
            )

    size_targets = {
        name: (int(raw["min"]), int(raw["max"]))
        for name, raw in data.get("lecture_size_targets", {}).items()
    }
    checks = tuple(
        CheckSpec(
            check_id=str(raw["id"]),
            severity=str(raw.get("severity", "error")),
            default_enabled=bool(raw.get("default_enabled", True)),
            desc=str(raw.get("desc", "")),
        )
        for raw in validation_raw.get("checks", ())
    )
    prereq_title, prereq_range, rubric_title = _parse_assessment(data.get("assessment", {}))

    logger.debug("契约加载完成：%d 个层次，%d 项检查", len(levels), len(checks))
    return Contract(
        root=root,
        path=path,
        levels=levels,
        curriculum=curriculum,
        sections=_parse_sections(_require(template_raw, "sections", "lecture_template")),
        stats_plugin_topics=_parse_topic_tags(data.get("stats_plugin_topics", ())),
        ai_task_topics=_parse_topic_tags(data.get("ai_task_topics", ())),
        prereq_l0_ids=l0_ids,
        prereq_l1_ids=l1_ids,
        l1_mappings=tuple(l1_mappings),
        size_targets=size_targets,
        checks=checks,
        prereq_item_title=prereq_title,
        prereq_weight_range=prereq_range,
        stats_rubric_title=rubric_title,
        env_exempt_tools=frozenset(exempt_tools),
        slides=_parse_slides(data.get("slide_template")),
        assessment=_parse_assessment_spec(data.get("assessment")),
    )
