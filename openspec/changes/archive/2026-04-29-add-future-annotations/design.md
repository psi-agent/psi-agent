## Context

Python 3.14 supports PEP 604 union syntax (`X | Y`) and PEP 649 deferred annotation evaluation. However, `from __future__ import annotations` is still needed for:
- Forward references without string quoting
- Consistent behavior across Python versions
- Enabling modern type syntax in all contexts

Currently 36 of 52 files are missing this import.

## Goals / Non-Goals

**Goals:**
- Add `from __future__ import annotations` to all Python files
- Document this requirement in CLAUDE.md
- Maintain code quality (pass ruff, ty checks)

**Non-Goals:**
- Refactor any type annotations
- Change any runtime behavior

## Decisions

### Add import at top of file

Add `from __future__ import annotations` as the first import (after module docstring) in each file.

**Rationale:** This is the standard location for future imports in Python.

### Document in CLAUDE.md

Add a note in the type annotation conventions section requiring this import.

**Rationale:** Ensures future development follows the same convention.

## Risks / Trade-offs

None - this is a straightforward addition with no runtime impact.
