## Context

This design introduces a GitHub Action workflow for automated alpha tagging. The workflow needs to interact with the GitHub API to query workflow runs, commits, and tags. It will run on a schedule and perform git operations to create and push tags.

Key constraints:
- Must run at 9:00 AM Beijing time (UTC+8)
- Must only tag commits that have passed CI.yml
- Must not create duplicate tags on already-tagged commits
- Tag format must follow `vN.N.N-alphaYYYYMMDD` pattern

## Goals / Non-Goals

**Goals:**
- Automate daily alpha tagging for CI-passed commits
- Provide clear markers for successful builds
- Enable downstream automation based on tags

**Non-Goals:**
- Creating release tags (only alpha tags)
- Modifying existing CI workflow behavior
- Handling manual tag creation or deletion

## Decisions

### 1. Workflow Trigger Mechanism
**Decision**: Use `schedule` trigger with cron expression `0 1 * * *` (1:00 UTC = 9:00 AM Beijing)

**Rationale**: GitHub Actions cron uses UTC. Beijing is UTC+8, so 9:00 AM Beijing = 1:00 AM UTC.

**Alternatives considered**:
- `workflow_dispatch` for manual triggers - kept as fallback for testing
- `repository_dispatch` for external triggers - unnecessary complexity

### 2. Workflow Structure
**Decision**: Keep the workflow simple with only 3 steps: checkout, fetch tags, and a single main step that handles all logic

**Rationale**: The logic is straightforward and doesn't benefit from being split into multiple steps with conditionals. A single step with clear comments is easier to read and maintain.

### 3. Finding Last CI-Passed Commit
**Decision**: Use GitHub CLI (`gh`) to query workflow runs

**Rationale**: `gh run list --workflow=CI.yml --branch=main --status=success --limit=1` directly gives the most recent successful run with its head SHA.

**Alternatives considered**:
- GitHub REST API with `curl` - more verbose, requires manual pagination
- GraphQL API - overkill for simple query

### 4. Finding Previous Alpha Tag
**Decision**: Use `git describe --tags --match 'v*-alpha*'` to find the most recent alpha tag reachable from current HEAD

**Rationale**: This command finds the most recent tag that is reachable from the current commit, which correctly handles tags on other branches. The output format is `vN.N.N-alphaYYYYMMDD-N-gHASH` where N is the number of commits since the tag. We extract the version prefix using `sed 's/-alpha[0-9]*-[0-9]*-g[0-9a-f]*$//'`.

**Alternatives considered**:
- `git tag --list` - doesn't consider branch topology, may find tags from unrelated branches
- `git describe --tags` without `--match` - may find non-alpha tags

### 5. Tag Format and Date Suffix
**Decision**: Use `YYYYMMDD` format for date suffix (e.g., `v0.1.0-alpha20260429`)

**Rationale**: ISO date format is unambiguous and sorts chronologically. The version prefix (vN.N.N) is inherited from the previous alpha tag.

### 6. Permission Model
**Decision**: Use `contents: write` permission in workflow

**Rationale**: Required for pushing tags to the repository. Minimal permission needed for this operation.

## Risks / Trade-offs

- **Risk**: No CI-passed commits found on a given day
  → Mitigation: Workflow exits gracefully with informative message

- **Risk**: No previous alpha tag exists to derive version prefix
  → Mitigation: Exit with clear message, require manual initial tag (e.g., `v0.1.0-alpha20260401`)

- **Risk**: Tag already exists for the date (multiple runs same day)
  → Mitigation: Check for existing tag before creating, skip if exists

- **Risk**: CI workflow name changes
  → Mitigation: Document the dependency, make workflow name configurable via env var
