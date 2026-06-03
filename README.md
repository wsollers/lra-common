# lra-common

Shared LaTeX infrastructure for the **Learning Real Analysis** project.

This repository contains the common preamble, macros, color definitions, and
environments that are shared across all volume repositories.

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
images/                — shared figures and images
scripts/
  check_bibliography.py — legacy duplicate check and source lookup helper
```

## Bibliography workflow

Bibliography entries are no longer owned by `lra-common`. Add and maintain
entries in the owning `lra-volume-*` repository's volume bibliography shard.
The volume sync workflow copies that shard into `Learning-Real-Analysis`.

## How volume repos use this

Each `lra-volume-N` repo contains a copy of `common/` kept in sync via a
GitHub Actions workflow. Volume bibliography files are volume-owned so the
volume repos remain self-contained for Overleaf.

## Sync workflow

When this repo changes, the GitHub Actions workflow `.github/workflows/sync-to-volumes.yml` pushes updated `common/` files to each volume repo and to the monorepo automatically.

## Canonical sources

The following files in `Learning-Real-Analysis` (the monorepo) remain the single source of truth:

- `predicates.yaml`
- `notation.yaml`
- `relations.yaml`

These are read-only to all automated processes and are not duplicated here.
