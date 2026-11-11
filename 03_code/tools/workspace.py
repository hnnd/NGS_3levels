"""仓库视图：把契约中的专题解析到磁盘上的实际文件，并缓存解析结果。

材料尚未生成（目录/文件不存在）与材料存在但违约是两件事，本模块只负责
"能否解析到文件"，判定交给各 checks_* 模块。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from tools.contract import Contract, Topic
from tools.md_utils import MarkdownDoc, MarkdownReadError, load_markdown
from tools.report import Severity

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LectureRef:
    """一个专题在磁盘上的讲义定位结果。"""

    topic: Topic
    directory: Path
    files: tuple[Path, ...]

    @property
    def dir_exists(self) -> bool:
        return self.directory.is_dir()

    @property
    def has_lecture(self) -> bool:
        return bool(self.files)

    @property
    def primary(self) -> Path | None:
        return self.files[0] if self.files else None


class Workspace:
    """按契约在仓库中定位材料，并缓存已解析的 Markdown。"""

    def __init__(self, root: Path, contract: Contract) -> None:
        self._root = root
        self._contract = contract
        self._doc_cache: dict[Path, MarkdownDoc | None] = {}

    @property
    def root(self) -> Path:
        return self._root

    def rel(self, path: Path) -> str:
        """相对仓库根目录的路径字符串（便于报告阅读）。"""
        try:
            return str(path.relative_to(self._root))
        except ValueError:
            return str(path)

    def doc(self, path: Path) -> MarkdownDoc | None:
        """解析 Markdown；文件不存在或读取失败返回 None。"""
        if path in self._doc_cache:
            return self._doc_cache[path]
        parsed: MarkdownDoc | None = None
        if path.is_file():
            try:
                parsed = load_markdown(path)
            except MarkdownReadError as exc:
                logger.warning("%s", exc)
                parsed = None
        self._doc_cache[path] = parsed
        return parsed

    def syllabus_path(self, level: str) -> Path:
        return self._root / self._contract.levels[level].syllabus

    def syllabus_doc(self, level: str) -> MarkdownDoc | None:
        return self.doc(self.syllabus_path(level))

    def env_paths(self, level: str) -> tuple[Path, ...]:
        """该层次全部任务环境文件的绝对路径。"""
        return tuple(
            self._root / spec.file for spec in self._contract.levels[level].env_files
        )

    def lecture_root(self, level: str) -> Path:
        return self._root / self._contract.levels[level].lecture_dir

    def lecture_ref(self, topic: Topic) -> LectureRef:
        """定位一个专题的讲义目录与讲义文件。"""
        directory = self.lecture_root(topic.level) / topic.dir_name
        files: tuple[Path, ...] = ()
        if directory.is_dir():
            files = tuple(sorted(p for p in directory.glob("*.md") if p.is_file()))
        return LectureRef(topic=topic, directory=directory, files=files)

    def lecture_refs(self, level: str) -> tuple[LectureRef, ...]:
        return tuple(self.lecture_ref(t) for t in self._contract.curriculum.get(level, ()))

    def orphan_lecture_dirs(self, level: str) -> tuple[Path, ...]:
        """存在于文件系统但不在契约中的讲义目录。"""
        root = self.lecture_root(level)
        if not root.is_dir():
            return ()
        declared = {t.dir_name for t in self._contract.curriculum.get(level, ())}
        return tuple(sorted(p for p in root.iterdir() if p.is_dir() and p.name not in declared))

    def assessment_files(self, level: str) -> tuple[Path, ...]:
        directory = self._root / "08_assessment" / level
        if not directory.is_dir():
            return ()
        return tuple(sorted(p for p in directory.rglob("*.md") if p.is_file()))


@dataclass(frozen=True)
class CheckContext:
    """一次校验运行的只读配置。"""

    contract: Contract
    workspace: Workspace
    levels: tuple[str, ...]
    check_links: bool
    link_timeout: float

    def severity(self, check_id: str) -> Severity:
        """取契约声明的严重级别；未声明按 error 处理。"""
        for spec in self.contract.checks:
            if spec.check_id == check_id:
                return Severity.WARNING if spec.severity == "warning" else Severity.ERROR
        return Severity.ERROR
