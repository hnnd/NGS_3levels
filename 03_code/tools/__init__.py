"""课程材料校验工具包。

唯一入口是 validate_course.main()；其余模块按职责拆分：
contract（契约模型）、workspace（仓库视图）、md_utils（Markdown 解析）、
checks_*（各项检查）、report（结果与报告渲染）。
"""

from __future__ import annotations

__all__ = [
    "CONTRACT_RELPATH",
    "CheckContext",
    "Contract",
    "ContractError",
    "Finding",
    "Severity",
    "Status",
    "Summary",
    "Workspace",
    "load_contract",
    "render_report",
    "summarize",
]

from tools.contract import CONTRACT_RELPATH, Contract, ContractError, load_contract
from tools.report import Finding, Severity, Status, Summary, render_report, summarize
from tools.workspace import CheckContext, Workspace
