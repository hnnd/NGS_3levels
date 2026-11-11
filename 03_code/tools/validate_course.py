#!/usr/bin/env python3
"""课程结构契约校验器（仓库唯一验证接缝）。

读取 00_design/course_contract.yaml，扫描大纲、讲义、conda 环境与考核材料，
输出人类可读的违规清单。只校验外部可观察的结构契约，不判断内容质量。

用法::

    python3 03_code/tools/validate_course.py
    python3 03_code/tools/validate_course.py --level master
    python3 03_code/tools/validate_course.py --check lecture_dir_match --check hours_balance
    python3 03_code/tools/validate_course.py --check-links --strict

退出码：0 = 无 error（--strict 下也无 warning）；1 = 存在违规；2 = 契约或参数错误。
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Callable, Sequence

if __package__ in (None, ""):  # 以脚本方式运行时，把 03_code/ 加入模块搜索路径
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.checks_env import check_env_tool_coverage
from tools.checks_assessment import check_assessment_material
from tools.checks_dataset import check_dataset_accession
from tools.checks_slides import check_slide_deck_match
from tools.checks_prereq import check_prereq_material, check_selftest_reference
from tools.checks_lecture import (
    check_l1_mapping_valid,
    check_lecture_size,
    check_prereq_reference,
    check_reference_reachable,
    check_reference_syntax,
    check_required_sections,
)
from tools.checks_structure import (
    check_assessment_coverage,
    check_hours_balance,
    check_lecture_dir_match,
    check_script_reference,
    check_syllabus_topic_match,
)
from tools.contract import CONTRACT_RELPATH, Contract, ContractError, LEVEL_ORDER, load_contract
from tools.report import Finding, Severity, Status, render_report, summarize
from tools.workspace import CheckContext, Workspace

logger = logging.getLogger(__name__)

CheckFn = Callable[[CheckContext], list[Finding]]

CHECK_REGISTRY: dict[str, CheckFn] = {
    "hours_balance": check_hours_balance,
    "syllabus_topic_match": check_syllabus_topic_match,
    "lecture_dir_match": check_lecture_dir_match,
    "required_sections": check_required_sections,
    "prereq_reference": check_prereq_reference,
    "l1_mapping_valid": check_l1_mapping_valid,
    "env_tool_coverage": check_env_tool_coverage,
    "lecture_size": check_lecture_size,
    "reference_syntax": check_reference_syntax,
    "reference_reachable": check_reference_reachable,
    "assessment_coverage": check_assessment_coverage,
    "prereq_material": check_prereq_material,
    "selftest_reference": check_selftest_reference,
    "slide_deck_match": check_slide_deck_match,
    "assessment_material": check_assessment_material,
    "script_reference": check_script_reference,
    "dataset_accession": check_dataset_accession,
}

EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_USAGE = 2


def find_repo_root(start: Path) -> Path:
    """从给定路径向上找出含 00_design/course_contract.yaml 的仓库根目录。"""
    for candidate in (start, *start.parents):
        if (candidate / CONTRACT_RELPATH).is_file():
            return candidate
    return start


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="validate_course.py",
        description="按 course_contract.yaml 校验课程材料的结构一致性",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--root", type=Path, default=None, help="仓库根目录（默认自动探测）")
    parser.add_argument(
        "--level", action="append", choices=list(LEVEL_ORDER), default=None,
        help="只校验指定层次，可重复",
    )
    parser.add_argument(
        "--check", action="append", choices=sorted(CHECK_REGISTRY), default=None,
        help="只执行指定检查项，可重复",
    )
    parser.add_argument("--check-links", action="store_true", help="开启参考资料网络可达性检查")
    parser.add_argument("--link-timeout", type=float, default=8.0, help="链接探测超时秒数")
    parser.add_argument("--strict", action="store_true", help="warning 也返回非零退出码")
    parser.add_argument("--verbose", "-v", action="store_true", help="输出调试日志")
    parser.add_argument("--quiet", "-q", action="store_true", help="只输出报告，抑制日志")
    return parser


def _configure_logging(verbose: bool, quiet: bool) -> None:
    level = logging.DEBUG if verbose else logging.ERROR if quiet else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s", stream=sys.stderr)


def _selected_levels(contract: Contract, requested: Sequence[str] | None) -> tuple[str, ...]:
    available = [name for name in LEVEL_ORDER if name in contract.levels]
    if not requested:
        return tuple(available)
    return tuple(name for name in available if name in requested)


def _selected_checks(
    contract: Contract, requested: Sequence[str] | None
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """返回 (待执行检查, 跳过检查)。契约声明顺序优先，未声明的按注册表补齐。"""
    declared = [spec.check_id for spec in contract.checks]
    ordered = declared + [cid for cid in CHECK_REGISTRY if cid not in declared]
    enabled_by_default = {
        spec.check_id: spec.default_enabled for spec in contract.checks
    }
    run: list[str] = []
    skipped: list[str] = []
    for check_id in ordered:
        if check_id not in CHECK_REGISTRY:
            logger.warning("契约声明的检查 %s 尚未实现，已跳过", check_id)
            skipped.append(f"{check_id}(未实现)")
            continue
        if requested is not None:
            (run if check_id in requested else skipped).append(check_id)
            continue
        if enabled_by_default.get(check_id, True):
            run.append(check_id)
        else:
            skipped.append(f"{check_id}(默认关闭)")
    return tuple(run), tuple(skipped)


def run_checks(ctx: CheckContext, check_ids: Sequence[str]) -> list[Finding]:
    """依次执行检查；单项检查异常不影响其余项。"""
    findings: list[Finding] = []
    for check_id in check_ids:
        func = CHECK_REGISTRY[check_id]
        logger.debug("执行检查 %s", check_id)
        try:
            findings.extend(func(ctx))
        except (OSError, ValueError, KeyError, TypeError) as exc:
            logger.error("检查 %s 执行失败：%s: %s", check_id, type(exc).__name__, exc)
            findings.append(
                Finding(check_id, "global", Severity.ERROR, Status.FAIL, "<validator>",
                        f"检查执行异常：{type(exc).__name__}: {exc}")
            )
    return findings


def main(argv: Sequence[str] | None = None) -> int:
    """命令行入口。"""
    args = build_parser().parse_args(argv)
    _configure_logging(args.verbose, args.quiet)

    root = (args.root or find_repo_root(Path(__file__).resolve().parent)).resolve()
    try:
        contract = load_contract(root)
    except ContractError as exc:
        logger.error("%s", exc)
        return EXIT_USAGE

    levels = _selected_levels(contract, args.level)
    if not levels:
        logger.error("没有可校验的层次（--level 与契约 levels 无交集）")
        return EXIT_USAGE
    run, skipped = _selected_checks(contract, args.check)
    if not run:
        logger.error("没有可执行的检查项")
        return EXIT_USAGE

    check_links = args.check_links or (args.check is not None and "reference_reachable" in args.check)
    ctx = CheckContext(
        contract=contract,
        workspace=Workspace(root, contract),
        levels=levels,
        check_links=check_links,
        link_timeout=args.link_timeout,
    )
    logger.info("校验层次：%s", ", ".join(levels))
    findings = run_checks(ctx, run)
    summary = summarize(findings, checks_run=run, checks_skipped=skipped)
    render_report(
        findings=findings,
        summary=summary,
        root=str(root),
        contract_path=str(contract.path.relative_to(root)),
        stream=sys.stdout,
    )
    if summary.errors or (args.strict and summary.warnings):
        return EXIT_VIOLATION
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
