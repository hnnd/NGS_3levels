"""校验结果的数据结构与人类可读报告渲染。

三个状态维度：
- Severity: 契约声明的严重级别（error / warning）。
- Status:   FAIL    —— 材料已存在但违反契约；
            PENDING —— 材料尚未生成，无法判定（不计入退出码）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, Sequence, TextIO

logger = logging.getLogger(__name__)

_LINE_WIDTH = 78


class Severity(Enum):
    """契约声明的严重级别。"""

    ERROR = "error"
    WARNING = "warning"


class Status(Enum):
    """违规状态：材料存在但违约 vs 材料尚未生成。"""

    FAIL = "FAIL"
    PENDING = "PENDING"


@dataclass(frozen=True)
class Finding:
    """一条校验结果。"""

    check_id: str
    level: str
    severity: Severity
    status: Status
    subject: str
    message: str

    @property
    def tag(self) -> str:
        if self.status is Status.PENDING:
            return "PENDING"
        return "ERROR" if self.severity is Severity.ERROR else "WARN"


@dataclass(frozen=True)
class Summary:
    """报告汇总计数。"""

    errors: int
    warnings: int
    pending: int
    checks_run: Sequence[str] = field(default_factory=tuple)
    checks_skipped: Sequence[str] = field(default_factory=tuple)

    @property
    def total(self) -> int:
        return self.errors + self.warnings + self.pending


def summarize(
    findings: Iterable[Finding],
    checks_run: Sequence[str] = (),
    checks_skipped: Sequence[str] = (),
) -> Summary:
    """按 severity/status 统计违规条目。"""
    errors = warnings = pending = 0
    for finding in findings:
        if finding.status is Status.PENDING:
            pending += 1
        elif finding.severity is Severity.ERROR:
            errors += 1
        else:
            warnings += 1
    return Summary(
        errors=errors,
        warnings=warnings,
        pending=pending,
        checks_run=tuple(checks_run),
        checks_skipped=tuple(checks_skipped),
    )


_LEVEL_LABEL = {
    "global": "全局 / 契约自身",
    "undergraduate": "本科生 / undergraduate",
    "master": "硕士生 / master",
    "phd": "博士生 / phd",
}
_LEVEL_SORT = {"global": 0, "undergraduate": 1, "master": 2, "phd": 3}
_STATUS_SORT = {Status.FAIL: 0, Status.PENDING: 1}


def _sort_key(finding: Finding) -> tuple[int, str, int, str]:
    return (
        _LEVEL_SORT.get(finding.level, 9),
        finding.check_id,
        _STATUS_SORT[finding.status],
        finding.subject,
    )


def render_report(
    findings: Sequence[Finding],
    summary: Summary,
    root: str,
    contract_path: str,
    stream: TextIO,
) -> None:
    """把违规清单写入给定流（按层次 → 检查项分组）。"""
    write = stream.write
    write("=" * _LINE_WIDTH + "\n")
    write("课程结构契约校验报告\n")
    write(f"仓库根目录 : {root}\n")
    write(f"契约文件   : {contract_path}\n")
    write("=" * _LINE_WIDTH + "\n")

    ordered = sorted(findings, key=_sort_key)
    current_level = ""
    current_check = ""
    for finding in ordered:
        if finding.level != current_level:
            current_level = finding.level
            current_check = ""
            label = _LEVEL_LABEL.get(current_level, current_level)
            write(f"\n【{label}】\n")
        if finding.check_id != current_check:
            current_check = finding.check_id
            write(f"\n  ── {current_check} [{finding.severity.value}] " + "─" * 20 + "\n")
        subject = finding.subject or "-"
        write(f"    [{finding.tag:<7}] {subject}\n")
        write(f"              {finding.message}\n")

    if not ordered:
        write("\n  （无违规项）\n")

    write("\n" + "=" * _LINE_WIDTH + "\n")
    write("汇总\n")
    write(f"  error   (材料存在但违反契约) : {summary.errors}\n")
    write(f"  warning (建议修正)           : {summary.warnings}\n")
    write(f"  pending (材料尚未生成)       : {summary.pending}\n")
    if summary.checks_run:
        write(f"  已执行检查 : {', '.join(summary.checks_run)}\n")
    if summary.checks_skipped:
        write(f"  已跳过检查 : {', '.join(summary.checks_skipped)}\n")
    write("=" * _LINE_WIDTH + "\n")
