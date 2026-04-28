## 1. Fix source files - Add future annotations import

- [x] 1.1 Add `from __future__ import annotations` to `src/psi_agent/utils/__init__.py`

## 2. Fix source files - Replace pathlib.Path with anyio.Path for IO

- [x] 2.1 Fix `src/psi_agent/session/history.py` - Replace `Path(history_file)` with `anyio.Path(history_file)` at lines 69 and 83
- [x] 2.2 Fix `src/psi_agent/session/server.py` - Replace synchronous `socket_path.exists()` and `socket_path.unlink()` with async `anyio.Path` methods at lines 194-199
- [x] 2.3 Fix `src/psi_agent/workspace/snapshot/api.py` - Replace synchronous `upper_dir.iterdir()` with async iteration at line 73

## 3. Fix test files - Add future annotations import

- [x] 3.1 Add `from __future__ import annotations` to `tests/__init__.py`
- [x] 3.2 Add `from __future__ import annotations` to `tests/ai/__init__.py`
- [x] 3.3 Add `from __future__ import annotations` to `tests/ai/anthropic_messages/__init__.py`
- [x] 3.4 Add `from __future__ import annotations` to `tests/ai/anthropic_messages/test_client.py`
- [x] 3.5 Add `from __future__ import annotations` to `tests/ai/anthropic_messages/test_config.py`
- [x] 3.6 Add `from __future__ import annotations` to `tests/ai/anthropic_messages/test_server.py`
- [x] 3.7 Add `from __future__ import annotations` to `tests/ai/anthropic_messages/test_translator.py`
- [x] 3.8 Add `from __future__ import annotations` to `tests/ai/openai_completions/__init__.py`
- [x] 3.9 Add `from __future__ import annotations` to `tests/ai/openai_completions/test_client.py`
- [x] 3.10 Add `from __future__ import annotations` to `tests/ai/openai_completions/test_config.py`
- [x] 3.11 Add `from __future__ import annotations` to `tests/ai/openai_completions/test_server.py`
- [x] 3.12 Add `from __future__ import annotations` to `tests/channel/__init__.py`
- [x] 3.13 Add `from __future__ import annotations` to `tests/channel/cli/test_cli.py`
- [x] 3.14 Add `from __future__ import annotations` to `tests/channel/repl/__init__.py`
- [x] 3.15 Add `from __future__ import annotations` to `tests/channel/repl/test_client.py`
- [x] 3.16 Add `from __future__ import annotations` to `tests/channel/repl/test_config.py`
- [x] 3.17 Add `from __future__ import annotations` to `tests/channel/repl/test_repl.py`
- [x] 3.18 Add `from __future__ import annotations` to `tests/channel/telegram/__init__.py`
- [x] 3.19 Add `from __future__ import annotations` to `tests/channel/telegram/test_client.py`
- [x] 3.20 Add `from __future__ import annotations` to `tests/channel/telegram/test_config.py`
- [x] 3.21 Add `from __future__ import annotations` to `tests/channel/telegram/test_split_message.py`
- [x] 3.22 Add `from __future__ import annotations` to `tests/session/__init__.py`
- [x] 3.23 Add `from __future__ import annotations` to `tests/session/schedule/__init__.py`
- [x] 3.24 Add `from __future__ import annotations` to `tests/session/schedule/test_cron.py`
- [x] 3.25 Add `from __future__ import annotations` to `tests/session/schedule/test_loader.py`
- [x] 3.26 Add `from __future__ import annotations` to `tests/session/schedule/test_schedule.py`
- [x] 3.27 Add `from __future__ import annotations` to `tests/session/test_history.py`
- [x] 3.28 Add `from __future__ import annotations` to `tests/session/test_runner.py`
- [x] 3.29 Add `from __future__ import annotations` to `tests/session/test_server.py`
- [x] 3.30 Add `from __future__ import annotations` to `tests/session/test_tool_executor.py`
- [x] 3.31 Add `from __future__ import annotations` to `tests/session/test_tool_loader.py`
- [x] 3.32 Add `from __future__ import annotations` to `tests/utils/__init__.py`
- [x] 3.33 Add `from __future__ import annotations` to `tests/workspace/__init__.py`
- [x] 3.34 Add `from __future__ import annotations` to `tests/workspace/test_integration.py`
- [x] 3.35 Add `from __future__ import annotations` to `tests/workspace/test_manifest.py`
- [x] 3.36 Add `from __future__ import annotations` to `tests/workspace/test_mount.py`
- [x] 3.37 Add `from __future__ import annotations` to `tests/workspace/test_pack.py`
- [x] 3.38 Add `from __future__ import annotations` to `tests/workspace/test_snapshot.py`
- [x] 3.39 Add `from __future__ import annotations` to `tests/workspace/test_umount.py`
- [x] 3.40 Add `from __future__ import annotations` to `tests/workspace/test_unpack.py`

## 4. Verification

- [x] 4.1 Run `ruff check` to verify no lint errors
- [x] 4.2 Run `ruff format` to verify formatting
- [x] 4.3 Run `ty check` to verify type checking passes
- [x] 4.4 Run `pytest` to verify all tests pass
