#!/usr/bin/env python3
"""Scan PDFs for ISBNs and produce hash-to-ISBN metadata.

The script is intentionally non-destructive. It extracts ISBN candidates from
PDF text, validates checksums, and can optionally query Open Library to produce
reviewable filename suggestions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - argparse reports this at runtime.
    PdfReader = None  # type: ignore[assignment]


ISBN_RE = re.compile(
    r"(?i)(?:ISBN(?:-1[03])?\s*(?:\:|\s))?"
    r"((?:97[89][-\s]?)?(?:[0-9][-\s]?){9}[0-9X])"
)


@dataclass(frozen=True)
class IsbnCandidate:
    raw: str
    normalized: str
    kind: str


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_isbn(raw: str) -> str:
    return re.sub(r"[^0-9Xx]", "", raw).upper()


def isbn10_valid(value: str) -> bool:
    if len(value) != 10 or not re.fullmatch(r"[0-9]{9}[0-9X]", value):
        return False
    total = 0
    for index, char in enumerate(value):
        digit = 10 if char == "X" else int(char)
        total += (10 - index) * digit
    return total % 11 == 0


def isbn13_valid(value: str) -> bool:
    if len(value) != 13 or not value.isdigit() or not value.startswith(("978", "979")):
        return False
    total = 0
    for index, char in enumerate(value[:12]):
        total += int(char) * (1 if index % 2 == 0 else 3)
    check = (10 - (total % 10)) % 10
    return check == int(value[-1])


def isbn_kind(value: str) -> str | None:
    if isbn13_valid(value):
        return "isbn13"
    if isbn10_valid(value):
        return "isbn10"
    return None


def extract_text(path: Path, max_pages: int | None) -> str:
    if PdfReader is None:
        raise RuntimeError("pypdf is required. Install it or run in the Codex workspace runtime.")
    reader = PdfReader(str(path))
    page_count = len(reader.pages)
    limit = page_count if max_pages is None else min(max_pages, page_count)
    pieces: list[str] = []
    for index in range(limit):
        try:
            pieces.append(reader.pages[index].extract_text() or "")
        except Exception as exc:  # Keep one difficult PDF from blocking the inventory.
            pieces.append(f"\n[page {index + 1} extraction failed: {exc}]\n")
    return "\n".join(pieces)


def find_isbns(text: str) -> list[IsbnCandidate]:
    by_value: dict[str, IsbnCandidate] = {}
    for match in ISBN_RE.finditer(text):
        raw = match.group(1)
        normalized = normalize_isbn(raw)
        kind = isbn_kind(normalized)
        if kind:
            by_value[normalized] = IsbnCandidate(raw=raw, normalized=normalized, kind=kind)
    return sorted(by_value.values(), key=lambda item: (item.kind, item.normalized))


def clean_filename_part(value: str) -> str:
    value = re.sub(r"[\\/:*?\"<>|]", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" .")


def author_last_name(authors: list[str]) -> str | None:
    if not authors:
        return None
    first = authors[0].strip()
    if "," in first:
        return first.split(",", 1)[0].strip()
    parts = first.split()
    return parts[-1] if parts else None


def lookup_openlibrary(isbn: str) -> dict[str, Any] | None:
    query = urllib.parse.urlencode(
        {
            "bibkeys": f"ISBN:{isbn}",
            "format": "json",
            "jscmd": "data",
        }
    )
    url = f"https://openlibrary.org/api/books?{query}"
    with urllib.request.urlopen(url, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get(f"ISBN:{isbn}")


def metadata_from_openlibrary(isbns: list[str], delay_seconds: float) -> dict[str, Any] | None:
    for isbn in isbns:
        try:
            data = lookup_openlibrary(isbn)
        except Exception:
            data = None
        if data:
            title = data.get("title")
            authors = [author.get("name", "") for author in data.get("authors", []) if author.get("name")]
            suggested = None
            last = author_last_name(authors)
            if title and last:
                suggested = f"{clean_filename_part(title)} - {clean_filename_part(last)}.pdf"
            return {
                "lookup_source": "openlibrary",
                "isbn_used": isbn,
                "title": title,
                "authors": authors,
                "publish_date": data.get("publish_date"),
                "publishers": [publisher.get("name", "") for publisher in data.get("publishers", [])],
                "suggested_filename": suggested,
            }
        if delay_seconds:
            time.sleep(delay_seconds)
    return None


def iter_pdfs(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() == ".pdf":
            yield path


def scan_pdf(path: Path, root: Path, max_pages: int | None, do_lookup: bool, delay_seconds: float) -> dict[str, Any]:
    stat = path.stat()
    row: dict[str, Any] = {
        "path": str(path),
        "relative_path": str(path.relative_to(root)),
        "name": path.name,
        "size_bytes": stat.st_size,
        "sha256": sha256_file(path),
        "isbns": [],
        "metadata": None,
        "error": None,
    }
    try:
        text = extract_text(path, max_pages)
        candidates = find_isbns(text)
        row["isbns"] = [
            {"raw": candidate.raw, "normalized": candidate.normalized, "kind": candidate.kind}
            for candidate in candidates
        ]
        if do_lookup and candidates:
            lookup_order = [candidate.normalized for candidate in candidates if candidate.kind == "isbn13"]
            lookup_order.extend(candidate.normalized for candidate in candidates if candidate.kind == "isbn10")
            row["metadata"] = metadata_from_openlibrary(lookup_order, delay_seconds)
    except Exception as exc:
        row["error"] = str(exc)
    return row


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    parser = argparse.ArgumentParser(description="Scan PDFs for ISBNs and optional title/author metadata.")
    parser.add_argument("root", help="Directory containing PDFs to scan recursively.")
    parser.add_argument("--max-pages", type=int, default=12, help="Pages to scan from the start of each PDF. Use 0 for all pages.")
    parser.add_argument("--lookup-openlibrary", action="store_true", help="Query Open Library for title/author suggestions.")
    parser.add_argument("--lookup-delay", type=float, default=0.2, help="Delay between ISBN lookup attempts.")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit nonzero if any PDF cannot be extracted.")
    parser.add_argument("--json", help="Optional JSON report path.")
    parser.add_argument("--jsonl", help="Optional JSON Lines report path.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    max_pages = None if args.max_pages == 0 else args.max_pages
    rows = []
    for path in iter_pdfs(root):
        row = scan_pdf(path, root, max_pages, args.lookup_openlibrary, args.lookup_delay)
        rows.append(row)
        marker = "ISBN" if row["isbns"] else "----"
        if row["error"]:
            marker = "ERR "
        print(f"{marker} {row['relative_path']}")

    if args.json:
        output = Path(args.json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps({"root": str(root), "pdfs": rows}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.jsonl:
        output = Path(args.jsonl)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8") as handle:
            for row in rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    with_isbn = sum(1 for row in rows if row["isbns"])
    with_metadata = sum(1 for row in rows if row["metadata"])
    errors = sum(1 for row in rows if row["error"])
    print(f"\nScanned {len(rows)} PDF(s) under {root}.")
    print(f"PDF(s) with validated ISBN candidate(s): {with_isbn}.")
    if args.lookup_openlibrary:
        print(f"PDF(s) with metadata lookup result: {with_metadata}.")
    print(f"PDF extraction error(s): {errors}.")
    return 1 if args.fail_on_error and errors else 0


if __name__ == "__main__":
    sys.exit(main())
