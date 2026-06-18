"""
Indexes worked examples and legacy example candidates.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from auditor import config


WORKED_EXAMPLE = re.compile(
    r"\\begin\{workedexample\}(?:\[([^\]]*)\])?(?P<body>.*?)\\end\{workedexample\}",
    re.DOTALL | re.IGNORECASE,
)
LEGACY_EXAMPLE = re.compile(
    r"\\begin\{(example|example\*)\}(?:\[([^\]]*)\])?(?P<body>.*?)\\end\{\1\}",
    re.DOTALL | re.IGNORECASE,
)
EXAMPLES_REMARK = re.compile(
    r"\\begin\{remark\*\}\[Examples\](?P<body>.*?)\\end\{remark\*\}",
    re.DOTALL | re.IGNORECASE,
)
LABEL = re.compile(r"\\label\{([^}]+)\}")
DISPLAY_MATH = re.compile(r"\\\[|\\begin\{(aligned|align|equation|gather|cases)\*?\}")
STEP_MARKER = re.compile(r"\\textbf\{(Setup|Work|Computation|Check|Conclusion|Step|Solution)\.?\}", re.IGNORECASE)


@dataclass
class ExampleRecord:
    kind: str
    classification: str
    label: str | None
    title: str
    file: str
    line: int
    reason: str


def build_worked_example_index(scope_path: Path) -> dict[str, Any]:
    scope = scope_path.resolve()
    records: list[ExampleRecord] = []
    for tex_file in _tex_files(scope):
        records.extend(_scan_file(tex_file))

    records.sort(key=lambda item: (item.file.lower(), item.line, item.kind))
    counts = Counter(record.classification for record in records)
    return {
        "scope": _display_path(scope),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "count": len(records),
        "classification_counts": dict(sorted(counts.items())),
        "items": [asdict(record) for record in records],
    }


def write_worked_example_index(index: dict[str, Any], output_dir: Path | None = None) -> tuple[Path, Path]:
    out_dir = output_dir or (config.REPORTS_DIR / "indexes")
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = _scope_slug(index["scope"])
    json_path = out_dir / f"{slug}-worked-example-index.json"
    md_path = out_dir / f"{slug}-worked-example-index.md"
    json_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(format_worked_example_index_markdown(index), encoding="utf-8")
    return json_path, md_path


def format_worked_example_index_markdown(index: dict[str, Any]) -> str:
    lines = [
        "# Worked Example Index",
        f"- **Scope:** `{index['scope']}`",
        f"- **Generated:** {index['generated_at']}",
        f"- **Items:** {index['count']}",
        "",
        "## Classification Counts",
        "",
    ]
    if index.get("classification_counts"):
        for key, count in index["classification_counts"].items():
            lines.append(f"- `{key}`: {count}")
    else:
        lines.append("_None._")
    lines += [
        "",
        "## Items",
        "",
        "| Classification | Kind | Label | Title | File | Line | Reason |",
        "|---|---|---|---|---|---:|---|",
    ]
    for item in index.get("items", []):
        lines.append(
            "| "
            + " | ".join([
                f"`{item['classification']}`",
                f"`{item['kind']}`",
                f"`{item.get('label') or ''}`",
                item["title"].replace("|", "\\|"),
                f"`{item['file']}`",
                str(item["line"]),
                item["reason"].replace("|", "\\|"),
            ])
            + " |"
        )
    lines.append("")
    return "\n".join(lines)


def _scan_file(tex_file: Path) -> list[ExampleRecord]:
    text = tex_file.read_text(encoding="utf-8")
    starts = _line_starts(text)
    records: list[ExampleRecord] = []
    for match in WORKED_EXAMPLE.finditer(text):
        body = match.group("body")
        records.append(ExampleRecord(
            kind="workedexample",
            classification="already_worked_example",
            label=_label(body),
            title=(match.group(1) or "").strip(),
            file=_display_path(tex_file),
            line=_line_number(starts, match.start()),
            reason="Already uses the canonical workedexample environment.",
        ))
    for match in LEGACY_EXAMPLE.finditer(text):
        body = match.group("body")
        classification, reason = _classify_legacy(body)
        records.append(ExampleRecord(
            kind=match.group(1).lower(),
            classification=classification,
            label=_label(body),
            title=(match.group(2) or "").strip(),
            file=_display_path(tex_file),
            line=_line_number(starts, match.start()),
            reason=reason,
        ))
    for match in EXAMPLES_REMARK.finditer(text):
        body = match.group("body")
        records.append(ExampleRecord(
            kind="remark*[Examples]",
            classification="definition_metadata",
            label=None,
            title="Examples",
            file=_display_path(tex_file),
            line=_line_number(starts, match.start()),
            reason="Examples remark is definition-attached concept-boundary metadata, not a worked walkthrough.",
        ))
    return records


def _classify_legacy(body: str) -> tuple[str, str]:
    has_display_math = bool(DISPLAY_MATH.search(body))
    has_step_markers = bool(STEP_MARKER.search(body))
    has_list = r"\begin{enumerate}" in body or r"\begin{itemize}" in body
    word_count = len(re.findall(r"[A-Za-z]+", re.sub(r"\\[a-zA-Z]+", " ", body)))
    if has_step_markers or (has_display_math and word_count >= 40):
        return "directly_transformable", "Legacy example has worked structure or substantial displayed mathematical work."
    if has_list and word_count < 80:
        return "definition_metadata", "Short listed examples are better kept as definition-attached Examples metadata."
    return "needs_human_review", "Could be exposition, a short example, or an incomplete walkthrough; review before conversion."


def _tex_files(scope: Path) -> list[Path]:
    if scope.is_file():
        return [scope] if scope.suffix.lower() == ".tex" else []
    return sorted(path for path in scope.rglob("*.tex") if ".git" not in {part.lower() for part in path.parts})


def _label(text: str) -> str | None:
    match = LABEL.search(text)
    return match.group(1) if match else None


def _line_starts(text: str) -> list[int]:
    starts = [0]
    for match in re.finditer("\n", text):
        starts.append(match.end())
    return starts


def _line_number(line_starts: list[int], offset: int) -> int:
    lo, hi = 0, len(line_starts)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if line_starts[mid] <= offset:
            lo = mid
        else:
            hi = mid
    return lo + 1


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(config.REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(resolved).replace("\\", "/")


def _scope_slug(scope: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", scope).strip("-").lower()
    return slug or "repo"
