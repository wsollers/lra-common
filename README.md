# lra-common

Shared LaTeX infrastructure for the **Learning Real Analysis** project.

This repository contains the common preamble, macros, color definitions, and
environments that are shared across all volume repositories.

## Contents

```
common/
  preamble.tex         — page layout, fonts, AMS packages
  boxes.tex            — statement boxes, pedagogical boxes, TikZ, blueprint macros, dependency figure styles
  colors.tex           — all color definitions (theorem palette, definition palette, etc.)
  environments.tex     — theorem-like environments (numbered and unnumbered)
  macros.tex           — proof macros, flash macros, citation helpers
  volume-preamble.tex  — inputs all of the above; used by every volume root
  exercise-format.tex  — exercise record stubs and tag macros
images/                — shared figures and images
scripts/
  check_bibliography.py — duplicate check and source lookup helper
```

## Shared box families

`common/boxes.tex` defines the shared semantic wrappers used by the volumes:

- formal statement boxes: `definitionbox`, `axiombox`, `theorembox`,
  `lemmabox`, `propositionbox`, and `corollarybox`;
- topic and navigation boxes: `topicbox`, toolkit boxes, blueprint boxes, and
  dependency figure boxes;
- note-side pedagogical boxes: `restatementbox` for teaching restatements and
  `derivationbox` for explanatory derivations.

Governance documents in `lra-governance/docs/governance/` define when each box
is valid and how validators interpret it.

## Bibliography workflow

Bibliography entries are no longer owned by `lra-common`. Add and maintain
entries in the owning `lra-volume-*` repository's volume bibliography shard.

## How volume repos use this

Volume repos should not carry synced copies of `common/`. Builds should obtain
`lra-common` directly, normally through the Docker image or an explicit checkout.
Volume bibliography files remain volume-owned.

## Sync workflow

There is no fan-out sync workflow. Volume builds consume `lra-common` from an
explicit checkout or the build environment.

## Canonical sources

The following files in `lra-governance` are the single source of truth:

- `predicates.yaml`
- `notation.yaml`
- `relations.yaml`

These are read-only to `lra-common` automation and are not duplicated here.
