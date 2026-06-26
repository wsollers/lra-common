<!--
GENERATED FILE — DO NOT EDIT BY HAND.

Source repo: wsollers/lra-governance
Source commit: 0fe121116f1f6aa98359774a72c5fac67236e6a5
Generated from:
- docs/governance/...
- docs/architecture/...
- docs/governance/repo-overlays/lra-common.md

Regenerate from lra-governance.
Emergency downstream edits must be ported upstream before regeneration.
-->

# Agent Instructions

## Global Agent Rules

- Treat generated instruction files as derived artifacts.
- Follow the owning repository boundary for every task.
- Do not include secrets, credentials, tokens, or machine-local private values.
- Do not modify mathematical content during governance or wrapper-generation tasks.
- Do not touch the retired `Learning-Real-Analysis` monorepo.
- Keep context small: use governance docs as targeted references, not preload material.
- Open only the workflow, standard, schema, or overlay needed for the current task.
- Port emergency downstream instruction repairs back to `lra-governance`.

## Repo Overlay

# lra-common Overlay

Stub overlay for shared LaTeX infrastructure.

Owned concerns:

- `common/`,
- bibliography helper scripts,
- shared LaTeX macros, environments, boxes, colors, and preambles,
- canonical shared LaTeX infrastructure consumed directly by builds.

## Agent Scope

Edit shared LaTeX infrastructure here, not in volume repo staging directories.
Do not expect `common/` to be copied or committed into volume repos. Build
workflows should obtain `lra-common` directly through an explicit checkout and
mount `common/` into the Docker build container.

Add bibliography entries in the owning `lra-volume-*` repository shard.
`lra-common/bibliography/` is a retired mirror, not a sync source. Mobile photo,
screenshot, OCR, and extractor
candidates must be searched and deduplicated before promotion to a canonical
`.bib` file.

Do not edit canonical YAML here; that is owned by `lra-governance`.

## Provider Notes

Codex reads this file as the local agent entrypoint.
