## Context

psi-agent is a Python project using `uv` for package management, with quality checks defined in pyproject.toml:
- `ruff check` — lint
- `ruff format --check` — format check
- `ty check` — type checking (needs to be added)
- `pytest` — tests

Currently there is no `.github` directory, so no CI/CD or Dependabot is configured.

## Goals / Non-Goals

**Goals:**
- Automate quality checks on every push and pull request
- Enable Dependabot for Python dependencies and GitHub Actions
- Ensure PRs cannot be merged without passing CI

**Non-Goals:**
- Deployment/release automation (future work)
- Security scanning beyond Dependabot (future work)
- Complex matrix testing across Python versions (Python 3.14 only)

## Decisions

### Use GitHub Actions for CI

**Rationale:** GitHub Actions is native to GitHub, free for public repos, and widely adopted. Alternatives considered:
- CircleCI: More features but requires external integration
- Travis CI: Less commonly used now for GitHub projects

### Use uv for Python setup

**Rationale:** The project already uses `uv` for package management. Using `uv` in CI is faster than pip and consistent with local development. Alternatives considered:
- pip: Slower, requires separate dependency installation steps
- poetry: Not used in this project

### Dependabot weekly updates

**Rationale:** Weekly updates balance keeping dependencies fresh without excessive PR noise. Alternatives considered:
- Daily: Too noisy, many PRs to review
- Monthly: Too infrequent, security updates delayed

## Risks / Trade-offs

- **CI time:** Initial setup may have 2-3 minute runtimes → acceptable for PR checks
- **Dependabot PR volume:** May create multiple PRs initially → review and merge in batches
- **uv ecosystem:** Dependabot's uv support is newer than pip → monitor for any compatibility issues
- **ty availability:** `ty` is a new type checker, ensure it's available in CI environment → fallback to `pyright` if needed