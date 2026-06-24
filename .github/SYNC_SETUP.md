# Disabled sync workflow

The `sync-to-volumes.yml` workflow no longer pushes `common/` from this repo to
volume repos or to `Learning-Real-Analysis`. Builds should obtain `lra-common`
directly, normally through the Docker image or an explicit checkout.

## Token setup

No sync token is required for this disabled workflow.

## Manual sync

There is no manual fan-out sync path. If a build needs shared LaTeX files, use
the Docker image or explicitly check out `wsollers/lra-common`.
