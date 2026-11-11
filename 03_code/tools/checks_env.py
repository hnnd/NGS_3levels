"""环境检查：契约中各专题声明的 core_tools 必须出现在对应层次的 conda 环境里。

工具名匹配刻意宽松：允许版本号（`bwa=0.7.17`）、渠道前缀（`r-seurat` 对
`seurat`）、以及 `gatk` 对 `gatk4`、`bwa` 对 `bwa-mem2` 这类变体。
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Iterable

import yaml

from tools.report import Finding, Status
from tools.workspace import CheckContext

logger = logging.getLogger(__name__)

_VERSION_SEPARATORS = "=<>!~ "
_CHANNEL_PREFIXES = ("r-", "bioconductor-", "python-", "perl-", "py-", "bio-")


def _dep_name(entry: str) -> str:
    name = entry.strip()
    for sep in _VERSION_SEPARATORS:
        name = name.split(sep, 1)[0]
    return name.strip().lower()


def _iter_dependencies(raw: Any) -> Iterable[str]:
    if not isinstance(raw, list):
        return ()
    names: list[str] = []
    for entry in raw:
        if isinstance(entry, str):
            names.append(_dep_name(entry))
        elif isinstance(entry, dict):
            for nested in entry.values():
                if isinstance(nested, list):
                    names.extend(_dep_name(str(item)) for item in nested)
    return [n for n in names if n]


def _candidates(dep: str) -> set[str]:
    names = {dep}
    for prefix in _CHANNEL_PREFIXES:
        if dep.startswith(prefix) and len(dep) > len(prefix):
            names.add(dep[len(prefix) :])
    return names


def tool_present(tool: str, deps: Iterable[str]) -> bool:
    """工具是否出现在依赖列表中（宽松匹配）。"""
    target = tool.strip().lower()
    if not target:
        return False
    for dep in deps:
        for name in _candidates(dep):
            if name == target:
                return True
            if name.startswith(target) and len(name) > len(target):
                nxt = name[len(target)]
                if not nxt.isalpha():
                    return True
    return False


def _load_dependencies(path: Path) -> tuple[list[str], str | None]:
    """读取单个环境文件的依赖名列表。返回 (依赖名, 失败原因)。"""
    if not path.is_file():
        return [], "环境文件尚未创建"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        return [], f"读取失败：{exc}"
    except yaml.YAMLError as exc:
        return [], f"YAML 解析失败：{exc}"
    if not isinstance(data, dict):
        return [], "环境文件根节点不是映射"
    return list(_iter_dependencies(data.get("dependencies"))), None


def check_env_tool_coverage(ctx: CheckContext) -> list[Finding]:
    """每个专题须被至少一个环境 covers，且其 core_tools 出现在这些环境的依赖并集中。

    环境按任务内容拆分（单一大环境在 bioconda 上通常解不出来），因此覆盖检查
    以「covers 该专题的环境集合」为单位，而不是全层一个文件。
    """
    check = "env_tool_coverage"
    severity = ctx.severity(check)
    findings: list[Finding] = []

    for level in ctx.levels:
        specs = ctx.contract.levels[level].env_files
        deps_by_file: dict[str, list[str]] = {}
        for spec in specs:
            path = ctx.workspace.root / spec.file
            deps, problem = _load_dependencies(path)
            rel = ctx.workspace.rel(path)
            if problem is not None:
                status = Status.PENDING if "尚未创建" in problem else Status.FAIL
                findings.append(Finding(check, level, severity, status, rel, problem))
                continue
            deps_by_file[spec.file] = deps

        for topic in ctx.contract.curriculum.get(level, ()):
            # 只对声明了非豁免工具的专题要求环境覆盖：
            # 课题设计/汇报这类专题 core_tools 为空，本就不需要环境。
            needed = {
                t.strip().lower()
                for t in topic.core_tools
                if t.strip() and not ctx.contract.is_env_exempt(t)
            }
            if not needed:
                logger.debug("专题 %s 无需环境（core_tools 为空或全豁免）", topic.topic_id)
                continue

            covering = [s for s in specs if topic.topic_id in s.covers]
            if not covering:
                findings.append(
                    Finding(check, level, severity, Status.FAIL, topic.topic_id,
                            f"专题 {topic.topic_id} 未被任何 env_files 条目 covers——"
                            f"学生不知道该建哪个环境")
                )
                continue

            missing_files = [s.file for s in covering if s.file not in deps_by_file]
            if missing_files:
                findings.append(
                    Finding(check, level, severity, Status.PENDING, topic.topic_id,
                            f"覆盖本专题的环境文件尚未创建：{', '.join(missing_files)}")
                )
                continue

            union: set[str] = set()
            for spec in covering:
                union.update(deps_by_file[spec.file])
            env_names = ", ".join(s.name or s.file for s in covering)

            for tool in sorted(needed):
                if not tool_present(tool, union):
                    findings.append(
                        Finding(check, level, severity, Status.FAIL,
                                f"{tool} @ {topic.topic_id}",
                                f"专题 {topic.topic_id} 声明的核心工具「{tool}」"
                                f"未出现在覆盖它的环境中（{env_names}）")
                    )
    return findings
