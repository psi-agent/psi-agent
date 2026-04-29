## Context

The psi-agent codebase consists of 107 Python files across three main areas:
- **src/psi_agent/**: Core library code (51 files)
- **tests/**: Test suite (30 files)
- **examples/**: Example workspace implementations (7 files)

Recent commits (f9b21d2, dc293f3, eeb351f, e158fa4, bbb14bd) have already addressed several code quality issues. This design documents the systematic approach for a comprehensive audit to identify and fix remaining violations.

The CLAUDE.md file defines strict coding standards including:
- Python 3.14+ with modern type syntax
- `from __future__ import annotations` at the top of all files
- Async-first design with `anyio` for all IO operations
- Google-style docstrings
- Specific import ordering (stdlib → third-party → local)
- CLI security requirements (sensitive argument masking)

## Goals / Non-Goals

**Goals:**
- Systematically audit all 107 Python files against CLAUDE.md standards
- Categorize violations by type and severity
- Create actionable task list for fixes
- Ensure 100% compliance with documented conventions

**Non-Goals:**
- Refactoring code logic or architecture changes
- Adding new features or capabilities
- Changing public API signatures
- Performance optimizations

## Decisions

### 1. Audit Categories

The audit will check for the following violation categories (in priority order):

| Category | Severity | Auto-fixable |
|----------|----------|--------------|
| Missing `from __future__ import annotations` | High | Yes |
| Legacy type syntax (`Optional`, `Union`, `List`, `Dict`) | High | Yes |
| Import order violations | Medium | Yes |
| Missing type annotations | High | No |
| Non-async tool functions | Critical | No |
| `pathlib.Path` for IO operations | Critical | No |
| Missing/incorrect docstrings | Medium | Partial |
| Missing `__all__` in `__init__.py` | Low | Yes |
| Missing sensitive arg masking in CLI | High | No |

### 2. Audit Methodology

**Phase 1: Automated Detection**
- Use `ruff check` for import ordering (I rules)
- Use `ty check` for type annotation issues
- Custom grep patterns for legacy type syntax
- Custom script for `pathlib.Path` IO detection

**Phase 2: Manual Review**
- Review each flagged file for context
- Categorize false positives
- Prioritize fixes by impact

**Phase 3: Systematic Fixes**
- Apply auto-fixes where safe
- Manual fixes for complex cases
- Verify with test suite after each batch

### 3. File Grouping for Fixes

Files will be fixed in groups by module:
1. **Core utilities** (`utils/`) - Foundation for other modules
2. **AI components** (`ai/`) - LLM provider adapters
3. **Session** (`session/`) - Core agent logic
4. **Channel** (`channel/`) - Platform adapters
5. **Workspace** (`workspace/`) - Workspace management
6. **Tests** (`tests/`) - Test suite
7. **Examples** (`examples/`) - Example workspaces

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Auto-fix introduces bugs | Run full test suite after each batch; review diffs |
| False positives in detection | Manual review before applying fixes |
| Breaking changes to internal APIs | Only fix style/type issues, preserve signatures |
| Large number of changes | Group fixes by module, commit incrementally |
| Merge conflicts with ongoing work | Create feature branch, coordinate with team |
