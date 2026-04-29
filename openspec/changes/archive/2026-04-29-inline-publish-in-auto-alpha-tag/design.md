## Context

The current CI/CD setup has two workflows:
1. `ci.yml` - runs on push/PR, includes `check` job and `publish` job (triggered by version tags)
2. `auto-alpha-tag.yml` - runs daily, creates alpha tags for CI-passed commits

The problem: `auto-alpha-tag.yml` uses `github.token` (GITHUB_TOKEN) to push tags. GitHub's security model prevents `GITHUB_TOKEN` from triggering other workflows, so when a new tag is pushed, `ci.yml`'s `publish` job is never triggered.

Current workaround options considered:
1. Use a Personal Access Token (PAT) - requires secret management, security risk
2. Use a GitHub App token - requires app installation, more complex setup
3. Inline the publish job directly - simple, no additional secrets needed

## Goals / Non-Goals

**Goals:**
- Enable automatic PyPI publishing for alpha tags created by `auto-alpha-tag.yml`
- Keep the solution simple without additional secrets or tokens
- Maintain the existing `publish` job in `ci.yml` for manual releases

**Non-Goals:**
- Changing the `ci.yml` workflow structure
- Adding new secrets or tokens
- Modifying the tag naming convention

## Decisions

**Decision 1: Inline the publish job in auto-alpha-tag.yml**

Rationale: This is the simplest solution that doesn't require additional secrets or complex setup. The `publish` job logic is already well-defined in `ci.yml`, and copying it ensures the same publishing behavior.

Alternatives considered:
- **PAT-based approach**: Would require storing a long-lived token as a repository secret, increasing security risk
- **GitHub App**: More complex setup, requires app installation and token generation
- **Repository dispatch**: Would still need a separate workflow with a trigger mechanism

**Decision 2: Use job output to conditionally run publish**

The `auto-tag` job outputs whether a new tag was created. The `publish` job uses `needs: auto-tag` and checks the output to determine if publishing should proceed.

## Risks / Trade-offs

**Code duplication**: The `publish` job logic exists in both `ci.yml` and `auto-alpha-tag.yml`. If publishing steps change, both files need updates.
- Mitigation: Keep the job simple and well-documented. The duplication is minimal (4 steps).

**No tag trigger for alpha releases**: Alpha tags won't trigger `ci.yml` at all.
- This is acceptable because alpha releases are automated daily snapshots, not formal releases.