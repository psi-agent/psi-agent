## Why

Currently, there is no automated process to tag successful builds on the main branch. This makes it difficult to track which commits have passed CI and are ready for further processing (e.g., deployment, release candidates). An automated daily tagging system would provide clear markers for CI-verified commits, enabling downstream automation and improving release traceability.

## What Changes

- Add a new GitHub Action workflow that runs daily at 9:00 AM (Beijing time)
- The workflow will automatically find the last CI-passed commit on main branch
- If that commit doesn't already have a tag, it will create an alpha tag with format `vN.N.N-alphaYYYYMMDD`
- The tag is derived from the most recent alpha tag pattern, incrementing the date suffix

## Capabilities

### New Capabilities

- `auto-alpha-tag`: Automated daily alpha tagging for CI-passed commits on main branch

### Modified Capabilities

- `ci-workflow`: The new workflow will reference the existing CI.yml workflow to determine commit success status

## Impact

- New file: `.github/workflows/auto-alpha-tag.yml`
- Reads from: `.github/workflows/CI.yml` (to check commit status)
- Requires: `contents: write` permission for pushing tags
- No breaking changes to existing functionality
