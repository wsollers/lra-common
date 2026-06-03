# Reading Library Tools

The reading-library scripts help organize local PDF readings without changing
the bibliography or deleting files automatically.

They are meant for local reading directories such as:

```text
D:\Readings\Analysis
```

The scripts are intentionally conservative:

- inventory and scan scripts write reports;
- rename planning writes a CSV review queue;
- tab launching opens files in Chrome;
- no script renames or deletes files automatically.

## File Inventory

Use `scripts/inventory_reading_files.py` to record local filenames and exact
SHA-256 hashes.

Example:

```powershell
python scripts\inventory_reading_files.py "D:\Readings\Analysis" `
  --json "$env:TEMP\lra-reading-inventory\analysis-file-inventory.json" `
  --csv "$env:TEMP\lra-reading-inventory\analysis-file-inventory.csv" `
  --duplicates-json "$env:TEMP\lra-reading-inventory\analysis-duplicates.json"
```

Use this report to identify exact duplicate files. The hash is the authority
for exact duplicates; filenames are only hints.

## ISBN Scan

Use `scripts/scan_pdf_isbns.py` to scan PDF text for validated ISBN candidates.

Example:

```powershell
python scripts\scan_pdf_isbns.py "D:\Readings\Analysis" `
  --max-pages 12 `
  --json "$env:TEMP\lra-reading-inventory\analysis-pdf-isbns.json" `
  --jsonl "$env:TEMP\lra-reading-inventory\analysis-pdf-isbns.jsonl"
```

The default scan reads the first 12 pages of each PDF, where ISBNs usually
appear. Use `--max-pages 0` to scan all pages.

Optional metadata lookup:

```powershell
python scripts\scan_pdf_isbns.py "D:\Readings\Analysis\Complex Analysis" `
  --max-pages 12 `
  --lookup-openlibrary `
  --json "$env:TEMP\lra-reading-inventory\complex-analysis-pdf-isbns-with-lookup.json"
```

ISBNs are bibliographic clues, not final proof. Some PDFs contain multiple ISBNs
or unrelated publisher/catalog data, so lookup results should be reviewed.

## Rename Plan

Use `scripts/make_pdf_rename_plan.py` to turn an ISBN scan report into a CSV
review plan.

Example:

```powershell
python scripts\make_pdf_rename_plan.py `
  "$env:TEMP\lra-reading-inventory\analysis-pdf-isbns.json" `
  --csv "$env:TEMP\lra-reading-inventory\analysis-rename-plan.csv"
```

The CSV includes:

```text
current_path, sha256, isbn, title, author_last, suggested_filename, confidence, status, reason, duplicate_of
```

Default behavior excludes files that already look organized, such as:

```text
Mathematical Logic - Kossak.pdf
Geometry of Partial Differential Equations.pdf
Introduction to Real Analysis 3rd by Robert G. Bartle.pdf
```

It also excludes known safe-delete candidates from the default rename queue:

- files matching `Learning_Real_Analysis*`;
- second and later occurrences of the same SHA-256 hash.

To include those rows in an audit plan:

```powershell
python scripts\make_pdf_rename_plan.py `
  "$env:TEMP\lra-reading-inventory\analysis-pdf-isbns.json" `
  --csv "$env:TEMP\lra-reading-inventory\analysis-rename-plan-with-delete-candidates.csv" `
  --include-delete-candidates
```

To include already named files too:

```powershell
python scripts\make_pdf_rename_plan.py `
  "$env:TEMP\lra-reading-inventory\analysis-pdf-isbns.json" `
  --csv "$env:TEMP\lra-reading-inventory\analysis-rename-plan-full-audit.csv" `
  --include-delete-candidates `
  --include-properly-named
```

The rename plan is not an apply script. Review the CSV before any future rename
or deletion workflow.

## Chrome Reading Tabs

Use `scripts/open_reading_tabs.ps1` to open ordered PDF tab sets for study.

Supported tracks:

- `analysis`
- `metric-spaces`
- `algebra`
- `number-systems`
- `topology`
- `all`

Preview paths without opening Chrome:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\open_reading_tabs.ps1 `
  -Track analysis `
  -List
```

Open the analysis tab set:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\open_reading_tabs.ps1 `
  -Track analysis
```

By default, the script opens Chrome with a temporary profile per track. This
keeps the ordered study tabs isolated, but Chrome may ask for sign-in because
the profile is new.

Use the normal Chrome profile instead:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\open_reading_tabs.ps1 `
  -Track analysis `
  -NoNewProfile
```

The tab launcher does not inspect existing Chrome tabs. It opens the curated
paths encoded in the script.

## Relationship To Bibliography

Local PDF holdings are not the same thing as bibliography entries.

Some bibliography entries are hard-copy only. Some are PDF only. Some are both.
For that reason, local holdings should eventually live in a sidecar holdings
map rather than being forced directly into BibTeX entries.

Recommended future shape:

```yaml
tao2016analysis1:
  holdings:
    - type: pdf
      sha256: ...
      filename: Analysis 1 - Tao.pdf
      collection: analysis
    - type: print
      location: bookshelf
```

