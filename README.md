# lra-common

Shared LaTeX infrastructure for the **Learning Real Analysis** project.

This repository contains the common preamble, macros, color definitions, environments, and bibliography that are shared across all volume repositories.

## Contents

```
common/
  preamble.tex         — page layout, fonts, AMS packages
  boxes.tex            — tcolorbox, TikZ, blueprint macros, dependency figure styles
  colors.tex           — all color definitions (theorem palette, definition palette, etc.)
  environments.tex     — theorem-like environments (numbered and unnumbered)
  macros.tex           — proof macros, flash macros, citation helpers
  volume-preamble.tex  — inputs all of the above; used by every volume-N-main.tex
  exercise-format.tex  — exercise record stubs and tag macros
bibliography/
  volume-*.bib         — canonical split bibliography by volume
  general-reference.bib
  analysis.bib         — legacy pointer only; do not add entries here
images/                — shared figures and images
scripts/
  check_bibliography.py — duplicate check and source lookup helper
```

## Bibliography workflow

Add bibliography entries only in `lra-common`. For phone photos, screenshots,
OCR output, or extractor candidates, follow
`docs/workflows/bibliography-entry.md`: search first, add the entry to the
single canonical split `.bib` file, run `python scripts/check_bibliography.py`,
then commit and push.

## How volume repos use this

Each `lra-volume-N` repo contains a copy of `common/` and `bibliography/` that is kept in sync via a GitHub Actions workflow. The volume repos are self-contained so they can be linked directly to Overleaf.

## Sync workflow

When this repo changes, the GitHub Actions workflow `.github/workflows/sync-to-volumes.yml` pushes updated files to each volume repo and to the monorepo automatically.

## Canonical sources

The following files in `Learning-Real-Analysis` (the monorepo) remain the single source of truth:

- `predicates.yaml`
- `notation.yaml`
- `relations.yaml`

These are read-only to all automated processes and are not duplicated here.
