"""数据集登录号检查：材料里出现的每个登录号都必须在已核验注册表中登记。

设计理由：第 7 轮实查发现 m01 讲义写的 `PRJNA294222` 在 ENA 与 NCBI 均**查无此项**，
而它在仓库里活了三轮没被任何检查发现——此前的检查只管 DOI 语法与 URL 语法，
不管登录号真伪。真伪只能联网确认（`06_data/verify_accessions.sh`），但"是否经过核验"
可以离线强制：凡出现在材料里的登录号，必须先登记进 `06_data/accessions.tsv`。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

from tools.report import Finding, Severity, Status
from tools.workspace import CheckContext

logger = logging.getLogger(__name__)

REGISTRY_RELPATH = "06_data/accessions.tsv"

# INSDC 登录号形状：项目 / 实验 / 样本 / Run / GEO / 组装
_ACCESSION_RE = re.compile(
    r"\b("
    r"PRJ(?:NA|EB|DB)\d{4,}"          # BioProject
    r"|(?:SR|ER|DR)[RXPS]\d{5,}"      # SRA/ENA Run / Experiment / Study / Sample
    r"|GSE\d{4,}|GSM\d{5,}"           # GEO
    r"|SAM(?:N|EA|D)\d{5,}"           # BioSample
    r"|GC[AF]_\d{9}(?:\.\d+)?"        # 组装
    r"|MTBLS\d+"                      # MetaboLights
    r")\b"
)

_SCAN_DIRS = ("01_syllabus", "02_lectures", "04_slides", "05_videos",
              "06_data", "08_assessment", "09_resources", "03_code")

# 讲义里**刻意**出现的假登录号（用于演示报错），登记在此白名单并注明出处
_INTENTIONAL_FAKE = {
    "SRR999999999",   # m01 ⑨ E1：演示"登录号不存在时 prefetch 报什么错"
    "PRJNA294222",    # m01 ⑤ 5.2 订正说明：本身就是"查无此项"的反面教材，
                      # 保留在正文里是为了让学生看到"凭印象写登录号"的后果
}


def load_registry(root: Path) -> tuple[set[str], bool]:
    """读取已核验登录号注册表，返回 (登录号集合, 文件是否存在)。"""
    path = root / REGISTRY_RELPATH
    if not path.is_file():
        return set(), False
    accessions: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        accessions.add(line.split("\t", 1)[0].strip())
    return accessions, True


def _level_of(rel: str) -> str:
    for level in ("undergraduate", "master", "phd"):
        if f"/{level}/" in f"/{rel}" or rel.endswith(f"syllabus_{level}.md"):
            return level
    return "shared"


def check_dataset_accession(ctx: CheckContext) -> list[Finding]:
    """材料中出现的登录号必须已登记在 06_data/accessions.tsv（即已过在线核验）。"""
    check = "dataset_accession"
    root = ctx.workspace.root
    registry, exists = load_registry(root)
    if not exists:
        return [Finding(check, "shared", ctx.severity(check), Status.PENDING,
                        REGISTRY_RELPATH, "登录号注册表尚未建立")]

    levels = set(ctx.levels) | {"shared"}
    findings: list[Finding] = []
    seen_unregistered: dict[str, list[str]] = {}
    for scan in _SCAN_DIRS:
        base = root / scan
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if path.name.startswith("."):
                continue
            if not path.is_file() or path.suffix not in (".md", ".sh", ".R", ".py", ".yaml", ".yml"):
                continue
            rel = ctx.workspace.rel(path)
            if rel == REGISTRY_RELPATH:
                continue
            if _level_of(rel) not in levels:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                logger.warning("读取 %s 失败：%s", rel, exc)
                continue
            for match in sorted({m.group(1) for m in _ACCESSION_RE.finditer(text)}):
                if match in registry or match in _INTENTIONAL_FAKE:
                    continue
                seen_unregistered.setdefault(match, []).append(rel)

    for accession, files in sorted(seen_unregistered.items()):
        where = files[0] + (f" 等 {len(files)} 处" if len(files) > 1 else "")
        findings.append(Finding(
            check, _level_of(files[0]), ctx.severity(check), Status.FAIL, where,
            f"登录号 {accession} 未登记在 {REGISTRY_RELPATH}——"
            f"先跑 bash 06_data/verify_accessions.sh {accession} 核验后再登记",
        ))

    # 注册表里登记了却没人用：多半是材料改了而注册表没清理
    used = {a for a in registry}
    referenced: set[str] = set()
    for scan in _SCAN_DIRS:
        base = root / scan
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in (".md", ".sh", ".R", ".py", ".yaml", ".yml"):
                continue
            if ctx.workspace.rel(path) == REGISTRY_RELPATH:
                continue
            try:
                referenced.update(m.group(1) for m in _ACCESSION_RE.finditer(
                    path.read_text(encoding="utf-8")))
            except (OSError, UnicodeDecodeError):
                continue
    for orphan in sorted(used - referenced):
        findings.append(Finding(
            check, "shared", Severity.WARNING, Status.FAIL, REGISTRY_RELPATH,
            f"登录号 {orphan} 已登记但没有任何材料引用它（材料改了？注册表该清理）"))
    return findings
