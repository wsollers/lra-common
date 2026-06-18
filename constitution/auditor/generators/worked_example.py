"""
generators/worked_example.py
Generates a single worked-example block. Returns raw LaTeX.
"""

from __future__ import annotations

import json
import re

from auditor import client, config, loader


def generate_worked_example(
    content_description: str,
    chapter_subject: str,
    *,
    label: str | None = None,
    title: str | None = None,
    illustrates: list[str] | None = None,
    uses: list[str] | None = None,
    tags: list[str] | None = None,
) -> str:
    base_prompt = loader.prompt("generate_worked_example")
    formal_label_index = _load_formal_label_index()

    system = (
        base_prompt
        + "\n\n## Formal Mathematical Label Index\n\n"
        + (formal_label_index or "(not available)")
    )
    user = "\n\n".join([
        "## Chapter Subject\n\n" + chapter_subject,
        "## Content Description\n\n" + content_description,
        "## Required Label\n\n" + (label or "(invent an `ex:` label)"),
        "## Optional Title\n\n" + (title or "(none supplied)"),
        "## Illustrates Labels\n\n" + _csv(illustrates),
        "## Uses Labels\n\n" + _csv(uses),
        "## Tags\n\n" + _csv(tags),
    ])
    return client.call(system, user, expect_json=False)


def _csv(values: list[str] | None) -> str:
    return ", ".join(values or []) or "(none supplied)"


def _load_formal_label_index() -> str:
    index_dir = config.REPORTS_DIR / "indexes"
    candidates = sorted(
        index_dir.glob("*-formal-label-index.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return ""
    text = candidates[0].read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return text

    compact_items = []
    for item in data.get("items", []):
        compact_items.append({
            "label": item.get("label"),
            "type": item.get("artifact_type"),
            "title": item.get("title"),
            "file": item.get("file"),
        })
    return json.dumps({"items": compact_items}, indent=2)


def split_csv_arg(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in re.split(r"\s*,\s*", value) if item.strip()]
