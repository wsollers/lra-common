# Sync workflow setup

The `sync-to-volumes.yml` workflow automatically pushes `common/` and `bibliography/` from this repo to all five volume repos whenever they change.

## Setup required

1. Create a GitHub Personal Access Token (PAT) with `repo` scope at https://github.com/settings/tokens
2. In `lra-common` repository settings → Secrets and variables → Actions, add a secret named `SYNC_PAT` with the token value.

Once set up, any push to `common/` or `bibliography/` in this repo will automatically propagate to all volume repos.

## Manual sync

To sync manually, trigger the workflow from the Actions tab with "Run workflow".
