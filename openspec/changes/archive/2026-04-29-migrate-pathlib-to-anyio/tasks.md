## 1. Source Code Migration

- [x] 1.1 Fix `src/psi_agent/ai/anthropic_messages/server.py` - Replace `Path.exists()` and `Path.unlink()` with `anyio.Path` async equivalents in the `start()` method (lines 156-158)

## 2. Example Workspace Migration

- [x] 2.1 Fix `examples/a-simple-bash-only-workspace/systems/system.py` - Replace synchronous `Path.exists()`, `Path.iterdir()`, and `Path.read_text()` operations with `anyio.Path` async equivalents in `_parse_skill_description()` and `build_system_prompt()` methods

- [x] 2.2 Fix `examples/an-openclaw-like-workspace/systems/system.py` - Replace synchronous `Path.exists()` and `Path.resolve()` operations with `anyio.Path` async equivalents in `_read_bootstrap_file()`, `_build_workspace_section()`, and `_build_skills_section()` functions

## 3. Verification

- [x] 3.1 Run `ruff check` to verify no linting errors

- [x] 3.2 Run `ty check` to verify no type errors

- [x] 3.3 Run `pytest` to verify all tests pass

- [x] 3.4 Run `ruff format` to ensure consistent formatting
