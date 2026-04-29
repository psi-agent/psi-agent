## 1. Import Ordering Fixes

- [x] 1.1 Fix import order in `src/psi_agent/ai/__init__.py` - move local imports after third-party
- [x] 1.2 Fix import order in `src/psi_agent/channel/__init__.py` - move local imports after third-party
- [x] 1.3 Fix import order in `src/psi_agent/session/__init__.py` - move local imports after third-party
- [x] 1.4 Fix import order in `src/psi_agent/workspace/__init__.py` - move local imports after third-party
- [x] 1.5 Fix import order in `src/psi_agent/__main__.py` - move tyro.conf import before local imports

## 2. Duplicate Import Removal

- [x] 2.1 Remove duplicate `json` import inside `_handle_streaming()` function in `src/psi_agent/channel/cli/cli.py:88`
- [x] 2.2 Remove duplicate `logger` import inside `_handle_streaming()` function in `src/psi_agent/channel/cli/cli.py:90`

## 3. Exception Class Docstring Fixes

- [x] 3.1 Move docstring from `pass` statement to class definition in `src/psi_agent/workspace/manifest.py:ManifestParseError`
- [x] 3.2 Move docstring from `pass` statement to class definition in `src/psi_agent/workspace/pack/api.py:PackError`
- [x] 3.3 Move docstring from `pass` statement to class definition in `src/psi_agent/workspace/mount/api.py:MountError`
- [x] 3.4 Move docstring from `pass` statement to class definition in `src/psi_agent/workspace/snapshot/api.py:SnapshotError`
- [x] 3.5 Move docstring from `pass` statement to class definition in `src/psi_agent/workspace/umount/api.py:UmountError`
- [x] 3.6 Move docstring from `pass` statement to class definition in `src/psi_agent/workspace/unpack/api.py:UnpackError`

## 4. Type Annotation Improvements

- [x] 4.1 Add specific return type for `_run_streaming_conversation()` in `src/psi_agent/session/runner.py:426` instead of `Any`

## 5. Async Pattern Fixes

- [x] 5.1 Replace `Path()` with `anyio.Path()` in `src/psi_agent/ai/openai_completions/server.py:156` for async file operations

## 6. Verification

- [x] 6.1 Run `ruff check src/` to verify no lint errors
- [x] 6.2 Run `ruff format --check src/` to verify formatting
- [x] 6.3 Run `ty check src/` to verify type checking passes
- [x] 6.4 Run `pytest tests/` to verify all tests pass
