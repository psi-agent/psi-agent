## Why

The codebase has accumulated inconsistencies in code style and patterns that deviate from the standards defined in CLAUDE.md. A comprehensive audit is needed to identify all violations and establish a remediation plan. This ensures code quality, maintainability, and adherence to the documented conventions that all contributors should follow.

## What Changes

- **Audit Report**: Complete analysis of all Python files against CLAUDE.md standards
- **Violation Categories**: Classification of issues by type (imports, types, async, docstrings, etc.)
- **Remediation Plan**: Prioritized list of fixes needed

### Issues Identified

#### 1. Import Order Violations
- Multiple files have imports not following the stdlib → third-party → local order
- Examples: `session/runner.py`, `session/schedule.py`, `workspace/mount/api.py`, `workspace/snapshot/api.py`, `workspace/umount/api.py`

#### 2. Missing `from __future__ import annotations`
- All files correctly include this import

#### 3. Async Context Manager Pattern Issues
- `channel/repl/client.py:44`: `__aexit__` does not set `_connector = None` after closing
- `channel/telegram/client.py:43`: Same issue - `_connector` not set to `None`
- `ai/anthropic_messages/client.py:46`: Correctly sets `_client = None`
- `ai/openai_completions/client.py:42`: Correctly sets `_client = None`

#### 4. Type Annotation Issues
- `session/runner.py:119`: Uses `Any` for `_system` instead of a more specific type
- `session/runner.py:392-399`: Return type `Any` for `process_streaming_request` and `_make_streaming_response`
- `channel/telegram/bot.py:66`: Complex generic type `Application[Any, Any, Any, Any, Any, Any]` could use type alias

#### 5. Docstring Issues
- All files follow Google style docstrings correctly
- Some functions missing `Raises` section where exceptions are raised (e.g., `session/tool_loader.py:load_tool_from_file`)

#### 6. Logging Issues
- Consistent use of loguru throughout
- Appropriate log levels used

#### 7. CLI Security
- `session/cli.py`: Missing `mask_sensitive_args` call (no sensitive args in this CLI)
- All CLIs with sensitive args correctly call `mask_sensitive_args`

#### 8. pathlib.Path vs anyio.Path Usage
- `ai/openai_completions/server.py:156`: Uses `Path(self.config.session_socket)` for non-IO operation (acceptable)
- `session/config.py:27-48`: Uses `Path` for type annotations and path construction (correct - no IO)
- All IO operations correctly use `anyio.Path`

#### 9. Test File Issues
- `tests/session/test_tool_loader.py:19-30`: Missing return type annotation on async test functions
- Test files generally follow conventions but some lack type annotations on test functions

## Capabilities

### New Capabilities
- `code-quality-enforcement`: Establish automated checks and documentation for code standards compliance

### Modified Capabilities
- None - this is an audit and documentation change, not a behavioral change

## Impact

- **Documentation**: CLAUDE.md remains authoritative; this audit documents current state
- **Code Quality**: Identifies technical debt for future remediation
- **Developer Experience**: Clearer guidance on code standards
- **CI/CD**: Potential for automated linting rules to catch violations
