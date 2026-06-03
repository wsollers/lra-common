#!/usr/bin/env python3
"""Create a reviewable PDF rename plan from ISBN scan reports.

This script is intentionally non-destructive. It consumes the JSON emitted by
scan_pdf_isbns.py and writes a CSV review plan. It never renames files.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any


def clean_filename_part(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" .")


def author_last_name(authors: list[str]) -> str:
    if not authors:
        return ""
    first = authors[0].strip()
    if "," in first:
        return clean_filename_part(first.split(",", 1)[0].strip())
    parts = first.split()
    return clean_filename_part(parts[-1]) if parts else ""


def looks_properly_named(filename: str) -> bool:
    """Return true for names that already look like ``Title - Author.pdf``."""
    stem = Path(filename).stem.strip()
    if " - " not in stem:
        return False
    title, author = stem.rsplit(" - ", 1)
    title = title.strip()
    author = author.strip()
    if len(title) < 4 or len(author) < 2:
        return False
    author_for_match = author.replace("_", " ")
    if re.search(r"\b(e\d+|[0-9]+e|copy|draft|notes?|lecture|pdf)\b", author_for_match, re.IGNORECASE):
        return False
    if not re.search(r"[A-Za-z]", title):
        return False
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z.'’ -]*", author_for_match))


def looks_mostly_named(filename: str) -> bool:
    """Return true for readable names that are good enough to omit by default."""
    stem = Path(filename).stem.strip()
    if looks_properly_named(filename):
        return True
    if len(stem) < 12:
        return False
    if re.search(r"^(bok%|dokumen\.pub|pdfcoffee|[0-9]+$|[0-9a-f]{8,})", stem, re.IGNORECASE):
        return False
    if re.search(r"\b(copy|draft|notes?|lecture|worksheet|problem\s*set)\b", stem, re.IGNORECASE):
        return False
    if re.search(r"\s+by\s+[A-Z][A-Za-z.'’ -]+$", stem):
        return True
    words = re.findall(r"[A-Za-z][A-Za-z.'’]*", stem)
    if len(words) < 4:
        return False
    title_words = {"a", "an", "and", "by", "for", "from", "in", "of", "on", "the", "to", "with"}
    meaningful = [word for word in words if word.lower() not in title_words]
    if len(meaningful) < 3:
        return False
    uppercase_or_title = sum(1 for word in meaningful if word[0].isupper())
    return uppercase_or_title >= max(2, len(meaningful) // 2)


def is_safe_delete_candidate(filename: str) -> bool:
    return Path(filename).name.startswith("Learning_Real_Analysis")


def first_isbn(row: dict[str, Any]) -> str:
    isbns = row.get("isbns") or []
    for candidate in isbns:
        if candidate.get("kind") == "isbn13":
            return candidate.get("normalized", "")
    if isbns:
        return isbns[0].get("normalized", "")
    return ""


def infer_status(row: dict[str, Any], metadata: dict[str, Any] | None, suggested_filename: str) -> tuple[str, str]:
    if is_safe_delete_candidate(row.get("name", "")):
        return "delete_candidate", "matches_learning_real_analysis_generated_copy"
    if row.get("_duplicate_keep_path"):
        return "delete_candidate", "duplicate_sha256_after_first_occurrence"
    if looks_properly_named(row.get("name", "")):
        return "excluded", "already_has_title_author_filename"
    if looks_mostly_named(row.get("name", "")):
        return "excluded", "already_has_readable_title_filename"
    if row.get("error"):
        return "error", "extraction_error"
    if not row.get("isbns"):
        return "manual_review", "no_isbn_found"
    if not metadata:
        return "manual_review", "isbn_found_no_metadata"
    if not suggested_filename:
        return "manual_review", "metadata_missing_title_or_author"
    if suggested_filename.lower() == row.get("name", "").lower():
        return "already_named", "suggested_name_matches_current_name"
    return "review", "ready_for_human_review"


def confidence(row: dict[str, Any], metadata: dict[str, Any] | None, suggested_filename: str) -> str:
    isbn_count = len(row.get("isbns") or [])
    if row.get("error") or isbn_count == 0:
        return "none"
    if metadata and suggested_filename and isbn_count == 1:
        return "high"
    if metadata and suggested_filename:
        return "medium"
    return "low"


def plan_row(row: dict[str, Any]) -> dict[str, str]:
    metadata = row.get("metadata") or None
    isbn = ""
    title = ""
    authors: list[str] = []
    suggested_filename = ""

    if metadata:
        isbn = metadata.get("isbn_used") or first_isbn(row)
        title = metadata.get("title") or ""
        authors = metadata.get("authors") or []
        suggested_filename = metadata.get("suggested_filename") or ""
    else:
        isbn = first_isbn(row)

    last_name = author_last_name(authors)
    if title and last_name and not suggested_filename:
        suggested_filename = f"{clean_filename_part(title)} - {last_name}.pdf"

    status, reason = infer_status(row, metadata, suggested_filename)
    return {
        "current_path": row.get("relative_path", row.get("path", "")),
        "sha256": row.get("sha256", ""),
        "isbn": isbn,
        "title": title,
        "author_last": last_name,
        "suggested_filename": suggested_filename,
        "confidence": confidence(row, metadata, suggested_filename),
        "status": status,
        "reason": reason,
        "duplicate_of": row.get("_duplicate_keep_path", ""),
    }


def load_scan(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("pdfs"), list):
        return data["pdfs"]
    raise ValueError(f"Unsupported scan report format: {path}")


def mark_duplicate_occurrences(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, str] = {}
    marked = []
    for row in rows:
        row = dict(row)
        digest = row.get("sha256")
        if digest:
            current_path = row.get("relative_path", row.get("path", ""))
            if digest in seen:
                row["_duplicate_keep_path"] = seen[digest]
            else:
                seen[digest] = current_path
        marked.append(row)
    return marked


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "current_path",
        "sha256",
        "isbn",
        "title",
        "author_last",
        "suggested_filename",
        "confidence",
        "status",
        "reason",
        "duplicate_of",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Create a reviewable PDF rename plan CSV.")
    parser.add_argument("isbn_report_json", help="JSON report from scan_pdf_isbns.py.")
    parser.add_argument("--csv", required=True, help="Output rename plan CSV path.")
    parser.add_argument(
        "--include-properly-named",
        action="store_true",
        help="Include files that already look like 'Title - Author.pdf'.",
    )
    parser.add_argument(
        "--include-delete-candidates",
        action="store_true",
        help="Include files that match known safe-delete patterns.",
    )
    args = parser.parse_args()

    source_rows = mark_duplicate_occurrences(load_scan(Path(args.isbn_report_json)))
    planned_rows = [plan_row(row) for row in source_rows]
    excluded = [row for row in planned_rows if row["status"] == "excluded"]
    delete_candidates = [row for row in planned_rows if row["status"] == "delete_candidate"]
    rows = planned_rows
    if not args.include_properly_named:
        rows = [row for row in rows if row["status"] != "excluded"]
    if not args.include_delete_candidates:
        rows = [row for row in rows if row["status"] != "delete_candidate"]
    write_csv(Path(args.csv), rows)

    by_status: dict[str, int] = {}
    by_confidence: dict[str, int] = {}
    for row in rows:
        by_status[row["status"]] = by_status.get(row["status"], 0) + 1
        by_confidence[row["confidence"]] = by_confidence.get(row["confidence"], 0) + 1

    print(f"Wrote {len(rows)} rename-plan row(s) to {args.csv}.")
    print(f"Excluded already named file(s): {len(excluded)}.")
    print(f"Safe-delete candidate file(s): {len(delete_candidates)}.")
    print("Status counts:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    print("Confidence counts:")
    for label, count in sorted(by_confidence.items()):
        print(f"  {label}: {count}")
    print("No files were renamed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
