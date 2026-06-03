#!/usr/bin/env python3
"""Inventory reading files by path, size, timestamp, and SHA-256 hash.

This script is intentionally non-destructive. It helps find exact duplicate
files before any bibliography or renaming workflow tries to infer titles.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_file():
            yield path


def inventory(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in iter_files(root):
        stat = path.stat()
        rows.append(
            {
                "path": str(path),
                "relative_path": str(path.relative_to(root)),
                "name": path.name,
                "suffix": path.suffix.lower(),
                "size_bytes": stat.st_size,
                "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "sha256": sha256_file(path),
            }
        )
    return rows


def duplicate_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_hash: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_hash[row["sha256"]].append(row)

    groups = []
    for digest, matches in sorted(by_hash.items()):
        if len(matches) > 1:
            groups.append(
                {
                    "sha256": digest,
                    "size_bytes": matches[0]["size_bytes"],
                    "count": len(matches),
                    "files": [match["relative_path"] for match in matches],
                }
            )
    return groups


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["relative_path", "name", "suffix", "size_bytes", "mtime_utc", "sha256", "path"],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description="Inventory files and find exact SHA-256 duplicates.")
    parser.add_argument("root", help="Directory to scan recursively.")
    parser.add_argument("--json", help="Optional JSON report path.")
    parser.add_argument("--csv", help="Optional CSV inventory path.")
    parser.add_argument("--duplicates-json", help="Optional JSON duplicate report path.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    rows = inventory(root)
    duplicates = duplicate_groups(rows)
    total_bytes = sum(row["size_bytes"] for row in rows)

    if args.json:
        write_json(Path(args.json), {"root": str(root), "files": rows, "duplicates": duplicates})
    if args.csv:
        write_csv(Path(args.csv), rows)
    if args.duplicates_json:
        write_json(Path(args.duplicates_json), {"root": str(root), "duplicates": duplicates})

    print(f"Scanned {len(rows)} file(s) under {root}.")
    print(f"Total size: {total_bytes:,} byte(s).")
    print(f"Exact duplicate hash group(s): {len(duplicates)}.")
    for group in duplicates[:25]:
        print(f"\n{group['sha256']} ({group['count']} files, {group['size_bytes']:,} bytes)")
        for relpath in group["files"]:
            print(f"  {relpath}")
    if len(duplicates) > 25:
        print(f"\n... {len(duplicates) - 25} more duplicate group(s) omitted from console output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
