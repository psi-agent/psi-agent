## Why

The project currently lacks a user-facing README.md. The existing `CLAUDE.md` serves as developer documentation for AI assistants, but users need a clear, simple introduction to understand what psi-agent is, how to install it, and how to get started quickly.

## What Changes

- Create a new `README.md` file with user-focused content:
  - Project introduction and core concepts
  - Installation instructions
  - Quick start guide
  - Component overview
  - Links to detailed documentation
- Create a `README_CN.md` file with Chinese translation
- Update `pyproject.toml` to reference `README.md` instead of `CLAUDE.md`
- Clarify `--base-url` option in quick start examples (most users use non-OpenAI providers)

## Capabilities

### New Capabilities

- `user-readme`: A user-facing README.md that provides project introduction, installation, and quick start guide.
- `user-readme-cn`: A Chinese translation of the README for Chinese-speaking users.

### Modified Capabilities

None. This is a documentation-only change with no spec-level behavior changes.

## Impact

- New file: `README.md`
- New file: `README_CN.md`
- Modified file: `pyproject.toml` (readme field)
- No code changes required
