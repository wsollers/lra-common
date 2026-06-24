<!--
GENERATED FILE — DO NOT EDIT BY HAND.

Source repo: wsollers/lra-governance
Source commit: d98bb51fc80e683b38a9d1e76f4a0c91037ede0a
Generated from:
- docs/governance/...
- docs/architecture/...
- docs/governance/repo-overlays/lra-common.md

Regenerate from lra-governance.
Emergency downstream edits must be ported upstream.
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
- shared LaTeX macros, environments, boxes, colors, and preambles,
- canonical shared LaTeX infrastructure consumed directly by builds.

## Agent Scope

Edit shared LaTeX infrastructure here, not in volume repo copies. Do not expect
`common/` to be synced into volume repos or the monorepo. Build workflows should
obtain `lra-common` directly, normally through the Docker image or an explicit
checkout. Bibliography entries are owned by the corresponding `lra-volume-*`
repository shard.

Do not edit canonical YAML here; that remains owned by `Learning-Real-Analysis`.

## Provider Notes

Keep provider-specific guidance concise and defer durable policy to governance docs.
