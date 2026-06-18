"""
Deterministic validation for worked-example blocks.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from auditor import config


_WORKED_EXAMPLE = re.compile(
    r"\\begin\{workedexample\}(?:\[([^\]]*)\])?(?P<body>.*?)\\end\{workedexample\}",
    re.DOTALL,
)
_LABEL = re.compile(r"\\label\{([^{}]+)\}")
_FORMAL_ENV = re.compile(r"\\begin\{(definition|theorem|lemma|proposition|corollary|axiom|example)\}")
_TCOLORBOX = re.compile(r"\\begin\{tcolorbox\}")
_PRINT_GUARD = re.compile(r"\\LRAExcludeFromPrintEditionBegin|\\LRAExcludeFromPrintEditionEnd")
_METADATA = {
    "illustrates": re.compile(r"\\LRAWorkedExampleFor\{([^}]*)\}"),
    "uses": re.compile(r"\\LRAWorkedExampleUses\{([^}]*)\}"),
}
_BAD_TEXT_PUNCTUATION = re.compile(r"(?:â|ï»¿|�|“|”|‘|’|—|–)")


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    evidence: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "evidence": self.evidence,
        }


def validate_worked_example_block(
    tex: str,
    *,
    expected_label: str | None = None,
) -> dict[str, Any]:
    findings: list[Finding] = []
    examples = list(_WORKED_EXAMPLE.finditer(tex))
    if len(examples) != 1:
        findings.append(Finding(
            "FAIL",
            "worked_example_count",
            "Worked-example source must contain exactly one workedexample environment.",
            f"found={len(examples)}",
        ))

    body = examples[0].group("body") if examples else tex
    labels = _LABEL.findall(body)
    if len(labels) != 1:
        findings.append(Finding(
            "FAIL",
            "label_count",
            "A worked example must contain exactly one label.",
            f"labels={labels}",
        ))
    elif not labels[0].startswith("ex:"):
        findings.append(Finding(
            "FAIL",
            "label_prefix",
            "Worked-example labels must use the `ex:` prefix.",
            labels[0],
        ))
    elif expected_label and labels[0] != expected_label:
        findings.append(Finding(
            "FAIL",
            "label_mismatch",
            "Worked-example label does not match the requested label.",
            f"expected={expected_label}; found={labels[0]}",
        ))

    if _FORMAL_ENV.search(body):
        findings.append(Finding(
            "FAIL",
            "formal_environment_inside_example",
            "Worked examples must not contain formal theorem-like or example environments.",
        ))

    if _TCOLORBOX.search(tex):
        findings.append(Finding(
            "FAIL",
            "boxed_worked_example",
            "Worked examples are logical containers and must not use tcolorbox chrome.",
        ))

    if _PRINT_GUARD.search(tex):
        findings.append(Finding(
            "WARNING",
            "manual_print_guard",
            "Use the workedexample environment's built-in print exclusion rather than manual print guards.",
        ))

    if "\ufeff" in tex or _BAD_TEXT_PUNCTUATION.search(tex):
        findings.append(Finding(
            "FAIL",
            "bom_or_mojibake",
            "Worked example contains a byte-order mark, smart punctuation, or mojibake text.",
        ))

    known = _load_known_formal_labels()
    for field, pattern in _METADATA.items():
        for ref in _metadata_refs(pattern, body):
            if ref.startswith("prf:") or ref.startswith("ex:"):
                findings.append(Finding(
                    "FAIL",
                    f"{field}_nonformal_ref",
                    "Worked-example metadata must refer to formal labels, not proof or example labels.",
                    ref,
                ))
            elif known and ref not in known:
                findings.append(Finding(
                    "FAIL",
                    f"{field}_unknown_ref",
                    "Worked-example metadata references a label absent from the formal label index.",
                    ref,
                ))

    failures = sum(1 for finding in findings if finding.severity == "FAIL")
    warnings = sum(1 for finding in findings if finding.severity == "WARNING")
    return {
        "result": "PASS" if failures == 0 else "FAIL",
        "summary": {
            "failures": failures,
            "warnings": warnings,
            "findings": len(findings),
        },
        "label": labels[0] if len(labels) == 1 else None,
        "findings": [finding.as_dict() for finding in findings],
    }


def validate_worked_example_file(
    path: Path,
    *,
    expected_label: str | None = None,
) -> dict[str, Any]:
    report = validate_worked_example_block(
        path.read_text(encoding="utf-8-sig"),
        expected_label=expected_label,
    )
    report["path"] = str(path)
    return report


def format_worked_example_validation_report(report: dict[str, Any]) -> str:
    lines = [
        "# Worked Example Validation",
        f"- **Path:** `{report.get('path', '<memory>')}`",
        f"- **Result:** {report['result']}",
        f"- **Label:** `{report.get('label') or '?'}`",
        f"- **Failures:** {report['summary']['failures']}",
        f"- **Warnings:** {report['summary']['warnings']}",
        "",
    ]
    findings = report.get("findings", [])
    if not findings:
        lines += ["_No deterministic validation findings._", ""]
        return "\n".join(lines)
    lines += ["## Findings", ""]
    for finding in findings:
        lines += [
            f"### {finding['severity']}: `{finding['code']}`",
            "",
            finding["message"],
            "",
        ]
        if finding.get("evidence"):
            lines += ["```text", finding["evidence"], "```", ""]
    return "\n".join(lines)


def _metadata_refs(pattern: re.Pattern[str], text: str) -> list[str]:
    refs: list[str] = []
    for match in pattern.finditer(text):
        refs.extend(item.strip() for item in match.group(1).split(",") if item.strip())
    return refs


def _load_known_formal_labels() -> set[str]:
    index_dir = config.REPORTS_DIR / "indexes"
    candidates = sorted(
        index_dir.glob("*-formal-label-index.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return set()
    try:
        data = json.loads(candidates[0].read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return {item["label"] for item in data.get("items", []) if item.get("label")}
