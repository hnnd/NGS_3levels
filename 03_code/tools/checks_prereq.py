"""前置包材料检查：L0/L1 模块的材料文件与自测文件是否齐备且合规。

与讲义检查分开的理由：前置材料用的是 7 节简化模板（`prerequisite_packs.
material_template`），不是 11 章节讲义模板——前置材料的目标是"快速补齐并自检"，
不是系统授课。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import yaml

from tools.md_utils import find_section, load_markdown
from tools.report import Finding, Status
from tools.workspace import CheckContext

logger = logging.getLogger(__name__)

_CHECK = "prereq_material"


def _load_prereq_config(ctx: CheckContext) -> dict:
    """从契约 YAML 原文读取 prerequisite_packs 段（Contract 未建模这些字段）。"""
    try:
        raw = yaml.safe_load(ctx.contract.path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        logger.warning("读取契约失败：%s", exc)
        return {}
    if not isinstance(raw, dict):
        return {}
    packs = raw.get("prerequisite_packs")
    return packs if isinstance(packs, dict) else {}


def _module_ids(pack: dict) -> list[str]:
    """一个 pack 内声明的模块 id。"""
    if not isinstance(pack, dict):
        return []
    return [
        str(item["id"])
        for item in pack.get("modules", ())
        if isinstance(item, dict) and "id" in item
    ]


def _required_titles(packs: dict) -> list[str]:
    template = packs.get("material_template")
    if not isinstance(template, dict):
        return []
    return [
        str(s["title"])
        for s in template.get("sections", ())
        if isinstance(s, dict) and s.get("required") and "title" in s
    ]


def _material_path(root: Path, material_dir: str, module_id: str) -> Path:
    return root / material_dir / module_id / f"{module_id}.md"


def check_prereq_material(ctx: CheckContext) -> list[Finding]:
    """每个 L0/L1 模块须有材料文件（含全部必需章节）与配套自测文件。"""
    severity = ctx.severity(_CHECK)
    findings: list[Finding] = []

    packs = _load_prereq_config(ctx)
    if not packs:
        return [
            Finding(_CHECK, "-", severity, Status.FAIL, "course_contract.yaml",
                    "契约缺少 prerequisite_packs 段，无法校验前置材料")
        ]

    material_dir = str(packs.get("material_dir", ""))
    assessment_dir = str(packs.get("assessment_dir", ""))
    if not material_dir or not assessment_dir:
        return [
            Finding(_CHECK, "-", severity, Status.FAIL, "course_contract.yaml",
                    "prerequisite_packs 缺少 material_dir 或 assessment_dir")
        ]

    required_titles = _required_titles(packs)
    root = ctx.workspace.root

    # ---- L0：每模块一份材料 + 一份自测 ----
    for module_id in _module_ids(packs.get("L0", {})):
        path = _material_path(root, material_dir, module_id)
        rel = ctx.workspace.rel(path)
        if not path.is_file():
            findings.append(
                Finding(_CHECK, "prereq", severity, Status.PENDING, module_id,
                        f"前置材料尚未生成：{rel}")
            )
            continue

        doc = load_markdown(path)
        missing = [title for title in required_titles if find_section(doc, title) is None]
        if missing:
            findings.append(
                Finding(_CHECK, "prereq", severity, Status.FAIL, f"{module_id} @ {rel}",
                        f"缺少 {len(missing)} 个必需章节：{', '.join(missing)}")
            )

        selftest = root / assessment_dir / f"{module_id}_selftest.md"
        if not selftest.is_file():
            findings.append(
                Finding(_CHECK, "prereq", severity, Status.PENDING, module_id,
                        f"自测文件尚未生成：{ctx.workspace.rel(selftest)}")
            )

    # ---- L1：零新增内容，全部映射写在一份共享文档里；
    #      5 个 module id 是该文档内的锚点，不各自成文 ----
    l1 = packs.get("L1", {})
    shared = l1.get("shared_material")
    if isinstance(shared, str) and shared:
        shared_path = root / shared
        rel = ctx.workspace.rel(shared_path)
        if not shared_path.is_file():
            findings.append(
                Finding(_CHECK, "prereq", severity, Status.PENDING, "l1_phd",
                        f"L1 共享映射文档尚未生成：{rel}")
            )
        else:
            doc = load_markdown(shared_path)
            missing = [t for t in required_titles if find_section(doc, t) is None]
            if missing:
                findings.append(
                    Finding(_CHECK, "prereq", severity, Status.FAIL, f"l1_phd @ {rel}",
                            f"缺少 {len(missing)} 个必需章节：{', '.join(missing)}")
                )
            body = shared_path.read_text(encoding="utf-8")
            absent = [mid for mid in _module_ids(l1) if mid not in body]
            if absent:
                findings.append(
                    Finding(_CHECK, "prereq", severity, Status.FAIL, f"l1_phd @ {rel}",
                            f"共享文档未覆盖模块锚点：{', '.join(absent)}")
                )

    shared_test = l1.get("shared_selftest")
    if isinstance(shared_test, str) and shared_test and not (root / shared_test).is_file():
        findings.append(
            Finding(_CHECK, "prereq", severity, Status.PENDING, "l1_phd",
                    f"L1 自测尚未生成：{ctx.workspace.rel(root / shared_test)}")
        )

    return findings


_L0_INDEX_TO_ID = {
    1: "l0_01_linux", 2: "l0_02_r", 3: "l0_03_conda",
    4: "l0_04_formats", 5: "l0_05_qc", 6: "l0_06_stats",
}
_CITATION = re.compile(r"L0-([1-6])-Q(\d{1,2})")
_HEADING = re.compile(r"^#{2,4}\s*Q(\d{1,2})\b", re.MULTILINE)


def _selftest_questions(root: Path, assessment_dir: str, module_id: str) -> set[int]:
    """某模块自测里实际存在的题号。"""
    path = root / assessment_dir / f"{module_id}_selftest.md"
    if not path.is_file():
        return set()
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        logger.warning("读取自测失败 %s：%s", path, exc)
        return set()
    return {int(m.group(1)) for m in _HEADING.finditer(text)}


def check_selftest_reference(ctx: CheckContext) -> list[Finding]:
    """讲义里 `L0-<n>-Q<m>` 的引用必须能在对应自测中找到该题号。

    讲义常在自测题写出来之前就先写好引用（各轮次并行生产），题号极易写错。
    这项检查把"引用悬空"变成可机械发现的问题。
    """
    check = "selftest_reference"
    severity = ctx.severity(check)
    findings: list[Finding] = []

    packs = _load_prereq_config(ctx)
    assessment_dir = str(packs.get("assessment_dir", ""))
    if not assessment_dir:
        return []

    root = ctx.workspace.root
    cache: dict[str, set[int]] = {}

    for level in ctx.levels:
        for topic in ctx.contract.curriculum.get(level, ()):
            ref = ctx.workspace.lecture_ref(topic)
            # LectureRef 暴露的是 files 元组，没有 path 字段。
            # 早期写成 getattr(ref, "path", None) 恒为 None，导致本检查从未触发。
            path = ref.primary
            if path is None or not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            rel = ctx.workspace.rel(path)
            for m in _CITATION.finditer(text):
                idx, num = int(m.group(1)), int(m.group(2))
                module_id = _L0_INDEX_TO_ID[idx]
                if module_id not in cache:
                    cache[module_id] = _selftest_questions(root, assessment_dir, module_id)
                available = cache[module_id]
                if not available:
                    continue  # 自测尚未生成，交给 prereq_material 报 PENDING
                if num not in available:
                    findings.append(
                        Finding(check, level, severity, Status.FAIL,
                                f"{topic.topic_id} @ {rel}",
                                f"引用 L0-{idx}-Q{num}（{module_id}）在自测中不存在；"
                                f"该模块实际题号为 Q{min(available)}–Q{max(available)}")
                    )
    return findings
