"""Markdown 解析工具：标题、章节、表格、DOI / URL。

只做结构提取，不对文字内容作任何质量判断。
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

logger = logging.getLogger(__name__)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_FENCE_RE = re.compile(r"^\s{0,3}(```|~~~)")
_TABLE_SEP_RE = re.compile(r"^:?-{2,}:?$")
_NUMBERED_TOPIC_RE = re.compile(r"^(?:专题|单元)\s*([A-Za-z]?\d+)\s*[：:]\s*(.+?)\s*$")
_TRAILING_META_RE = re.compile(r"[（(][^（()]*[)）]\s*$")
_DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"'<>)\]}，,；;、]+")
_DOI_LABEL_RE = re.compile(r"(?i)\bdoi\b\s*[:：]\s*([^\s\]\)，,；;]+)")
_URL_RE = re.compile(r"(?i)\bhttps?://[^\s<>\"'\)\]}，、；]*")
_WEIGHT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_DECORATION_RE = re.compile(
    r"[\U0001F000-\U0001FAFF\u2190-\u2BFF\uFE0F\u200D*_`~\s]+$"
)
_LEADING_MARK_RE = re.compile(r"^[*_`~\s]+")


@dataclass(frozen=True)
class Heading:
    """一个 Markdown 标题。"""

    depth: int
    text: str
    line_no: int


@dataclass(frozen=True)
class Section:
    """一个章节：标题 + 正文行。"""

    heading: Heading
    body: str


@dataclass(frozen=True)
class MarkdownDoc:
    """已解析的 Markdown 文档。"""

    path: Path
    text: str
    line_count: int
    headings: tuple[Heading, ...]
    lines: tuple[str, ...]
    fenced: tuple[bool, ...]


class MarkdownReadError(OSError):
    """Markdown 文件读取失败。"""


def normalize(text: str) -> str:
    """去掉全部空白并统一常见全角标点，用于宽松的标题比对。"""
    table = {"：": ":", "（": "(", "）": ")", "／": "/", "，": ",", "、": ","}
    cleaned = "".join(table.get(ch, ch) for ch in text)
    return re.sub(r"\s+", "", cleaned)


def title_stem(title: str) -> str:
    """取标题主干：去掉 Markdown 强调、括注与尾部装饰符号后归一化。

    大纲标题常写作 `综合实践项目（24 学时 · 课堂集中）🔒`，契约写作
    `综合实践项目（细菌基因组组装到泛基因组）`——比对时只看括注前的主干。
    """
    text = re.split(r"[（(]", title, maxsplit=1)[0]
    text = _LEADING_MARK_RE.sub("", text)
    text = _DECORATION_RE.sub("", text)
    return normalize(text)


def load_markdown(path: Path) -> MarkdownDoc:
    """读取并解析 Markdown 文件。

    Raises:
        MarkdownReadError: 文件无法读取或解码。
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise MarkdownReadError(f"读取 {path} 失败: {exc}") from exc
    lines = text.splitlines()
    fenced: list[bool] = []
    headings: list[Heading] = []
    in_fence = False
    for idx, line in enumerate(lines, start=1):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            fenced.append(True)
            continue
        fenced.append(in_fence)
        if in_fence:
            continue
        match = _HEADING_RE.match(line)
        if match:
            headings.append(Heading(depth=len(match.group(1)), text=match.group(2), line_no=idx))
    return MarkdownDoc(
        path=path,
        text=text,
        line_count=len(lines),
        headings=tuple(headings),
        lines=tuple(lines),
        fenced=tuple(fenced),
    )


def find_section(doc: MarkdownDoc, title: str) -> Section | None:
    """按标题（宽松匹配：标题行含目标标题）取章节，取不到返回 None。"""
    target = normalize(title)
    for index, heading in enumerate(doc.headings):
        if target and target in normalize(heading.text):
            end = doc.line_count
            for later in doc.headings[index + 1 :]:
                if later.depth <= heading.depth:
                    end = later.line_no - 1
                    break
            body = "\n".join(doc.lines[heading.line_no : end])
            return Section(heading=heading, body=body)
    return None


def parse_numbered_topics(doc: MarkdownDoc) -> tuple[tuple[str, str], ...]:
    """抽取大纲中形如 `### 专题3：xxx（4学时）` 或 `### 专题 p03：xxx` 的条目。

    Returns:
        (序号或专题 id, 标题) 二元组序列。
    """
    found: list[tuple[str, str]] = []
    for heading in doc.headings:
        match = _NUMBERED_TOPIC_RE.match(heading.text.strip())
        if not match:
            continue
        title = _TRAILING_META_RE.sub("", match.group(2)).strip()
        found.append((match.group(1), title))
    return tuple(found)


def parse_tables(doc: MarkdownDoc) -> tuple[tuple[tuple[str, ...], ...], ...]:
    """抽取全部 Markdown 表格；每个表格为若干行，每行为若干单元格。"""
    tables: list[tuple[tuple[str, ...], ...]] = []
    current: list[tuple[str, ...]] = []
    for line, in_fence in zip(doc.lines, doc.fenced):
        stripped = line.strip()
        if in_fence or not stripped.startswith("|"):
            if current:
                tables.append(tuple(current))
                current = []
            continue
        cells = tuple(cell.strip() for cell in stripped.strip("|").split("|"))
        if all(_TABLE_SEP_RE.match(cell.replace(" ", "")) for cell in cells if cell):
            continue
        current.append(cells)
    if current:
        tables.append(tuple(current))
    return tuple(tables)


def extract_weight_percent(cells: tuple[str, ...]) -> float | None:
    """从表格一行中抽第一个百分比数值。"""
    for cell in cells:
        match = _WEIGHT_RE.search(cell)
        if match:
            return float(match.group(1))
    return None


def extract_dois(text: str) -> tuple[str, ...]:
    """抽取符合 `10.xxxx/...` 形状的 DOI。"""
    return tuple(m.group(0).rstrip(".。") for m in _DOI_RE.finditer(text))


def extract_labeled_dois(text: str) -> tuple[str, ...]:
    """抽取显式标注 `DOI:` 后的字符串（用于发现格式不合法的 DOI）。"""
    return tuple(m.group(1) for m in _DOI_LABEL_RE.finditer(text))


def is_valid_doi(candidate: str) -> bool:
    """DOI 是否符合 `10.<registrant>/<suffix>` 形状。"""
    cleaned = candidate.strip().rstrip(".。,，)]")
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:", "DOI:"):
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix) :]
    return bool(re.fullmatch(r"10\.\d{4,9}/\S+", cleaned))


def extract_urls(text: str) -> tuple[str, ...]:
    """抽取 http(s) URL。"""
    return tuple(m.group(0).rstrip(".。,，") for m in _URL_RE.finditer(text))


def is_valid_url(candidate: str) -> bool:
    """URL 语法是否合法（scheme + 含点的 netloc + 无空白/中文）。"""
    try:
        parts = urlsplit(candidate)
    except ValueError:
        return False
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return False
    if any(ch.isspace() for ch in candidate):
        return False
    if "." not in parts.netloc:
        return False
    return all(ord(ch) < 128 for ch in parts.netloc)
