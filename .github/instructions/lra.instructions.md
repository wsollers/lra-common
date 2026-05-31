<!--
GENERATED FILE — DO NOT EDIT BY HAND.

Source repo: wsollers/lra-governance
Source commit: d98bb51fc80e683b38a9d1e76f4a0c91037ede0a
Generated from:
- docs/governance/...
- docs/architecture/...
- docs/governance/repo-overlays/lra-common.md

Regenerate from lra-governance.
Emergency downstream edits must be ported upstream before the next sync.
-->

# LRA Repository Instructions

This file is intended for `.github/instructions/lra.instructions.md`. Keep it
concise and refer to canonical governance docs rather than copying large docs.

## Global Agent Rules

- Treat generated instruction files as derived artifacts.
- Follow the owning repository boundary for every task.
- Do not include secrets, credentials, tokens, or machine-local private values.
- Do not modify mathematical content during governance or wrapper-generation tasks.
- Do not touch `Learning-Real-Analysis/scripts/`.
- Port emergency downstream instruction repairs back to `lra-governance`.

## Repo Overlay

# lra-common Overlay

Stub overlay for shared LaTeX infrastructure.

Owned concerns:

- `common/`,
- `bibliography/`,
- shared LaTeX macros, environments, boxes, colors, and preambles,
- common-to-volume sync expectations.

## Agent Scope

Edit shared LaTeX infrastructure here, not in volume repo copies. When changing
`common/` or `bibliography/`, expect sync workflows to propagate updates to
volume repos and the monorepo.

Do not edit canonical YAML here; that remains owned by `Learning-Real-Analysis`.

## Provider Notes

Keep provider-specific guidance concise and defer durable policy to governance docs.
