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

# Claude Instructions

@AGENTS.md

If import semantics are unavailable, use the generated `AGENTS.md` content for
the same repository as the canonical local instruction body.

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
- common-to-volume sync expectations.

## Agent Scope

Edit shared LaTeX infrastructure here, not in volume repo copies. When changing
`common/`, expect sync workflows to propagate updates to volume repos and the
monorepo. Bibliography entries are owned by the corresponding `lra-volume-*`
repository shard.

Do not edit canonical YAML here; that remains owned by `Learning-Real-Analysis`.

## Provider Notes

Claude should use this wrapper as a pointer to the generated repo instructions.
