## Why

36 out of 52 Python files in `src/psi_agent/` are missing `from __future__ import annotations`. This import enables modern type annotation syntax (PEP 604) and allows forward references without string quoting. Additionally, this requirement should be documented in CLAUDE.md for future development.

## What Changes

- Add `from __future__ import annotations` to all 36 Python files missing it
- Update CLAUDE.md to document this requirement in the type annotation conventions section

## Capabilities

### New Capabilities

None

### Modified Capabilities

None - this is a code quality improvement with no spec-level behavior changes.

## Impact

- 36 Python files in `src/psi_agent/` - add future annotations import
- `CLAUDE.md` - document the requirement
