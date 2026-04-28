## Why

The project lacks automated CI/CD workflows and dependency management. Without GitHub Actions, there's no automated quality checks on pull requests. Without Dependabot, dependencies may become outdated or have unpatched security vulnerabilities.

## What Changes

- Add GitHub Actions workflow for CI (lint, type-check, test) on any push and any pull request
- Add Dependabot configuration for automated dependency updates
- Ensure all code quality checks (ruff lint, ruff format check, ty check, pytest) run automatically

## Capabilities

### New Capabilities

- `ci-workflow`: Automated continuous integration workflow that runs lint, format check, type checking, and tests on every push and pull request
- `dependabot`: Automated dependency updates for Python packages and GitHub Actions

### Modified Capabilities

<!-- No existing capability requirements are changing -->

## Impact

- Creates `.github/workflows/ci.yml` for CI workflow
- Creates `.github/dependabot.yml` for Dependabot configuration
- No code changes required
- Ensures all PRs pass quality checks before merge