## 1. Add future annotations to all Python files

- [x] 1.1 Add `from __future__ import annotations` to `src/psi_agent/__init__.py`
- [x] 1.2 Add `from __future__ import annotations` to `src/psi_agent/workspace/manifest.py`
- [x] 1.3 Add `from __future__ import annotations` to `src/psi_agent/session/config.py`
- [x] 1.4 Add `from __future__ import annotations` to `src/psi_agent/session/history.py`
- [x] 1.5 Add `from __future__ import annotations` to `src/psi_agent/session/server.py`
- [x] 1.6 Add `from __future__ import annotations` to `src/psi_agent/session/tool_executor.py`
- [x] 1.7 Add `from __future__ import annotations` to `src/psi_agent/session/tool_loader.py`
- [x] 1.8 Add `from __future__ import annotations` to `src/psi_agent/session/types.py`
- [x] 1.9 Add `from __future__ import annotations` to `src/psi_agent/session/runner.py`
- [x] 1.10 Add `from __future__ import annotations` to `src/psi_agent/ai/openai_completions/__init__.py`
- [x] 1.11 Add `from __future__ import annotations` to `src/psi_agent/ai/openai_completions/config.py`
- [x] 1.12 Add `from __future__ import annotations` to `src/psi_agent/ai/openai_completions/server.py`
- [x] 1.13 Add `from __future__ import annotations` to `src/psi_agent/ai/openai_completions/client.py`
- [x] 1.14 Add `from __future__ import annotations` to `src/psi_agent/ai/anthropic_messages/__init__.py`
- [x] 1.15 Add `from __future__ import annotations` to `src/psi_agent/ai/anthropic_messages/config.py`
- [x] 1.16 Add `from __future__ import annotations` to `src/psi_agent/ai/anthropic_messages/client.py`
- [x] 1.17 Add `from __future__ import annotations` to `src/psi_agent/ai/anthropic_messages/server.py`
- [x] 1.18 Add `from __future__ import annotations` to `src/psi_agent/ai/anthropic_messages/translator.py`
- [x] 1.19 Add `from __future__ import annotations` to `src/psi_agent/workspace/pack/__init__.py`
- [x] 1.20 Add `from __future__ import annotations` to `src/psi_agent/workspace/pack/api.py`
- [x] 1.21 Add `from __future__ import annotations` to `src/psi_agent/workspace/unpack/__init__.py`
- [x] 1.22 Add `from __future__ import annotations` to `src/psi_agent/workspace/unpack/api.py`
- [x] 1.23 Add `from __future__ import annotations` to `src/psi_agent/workspace/mount/__init__.py`
- [x] 1.24 Add `from __future__ import annotations` to `src/psi_agent/workspace/mount/api.py`
- [x] 1.25 Add `from __future__ import annotations` to `src/psi_agent/workspace/umount/__init__.py`
- [x] 1.26 Add `from __future__ import annotations` to `src/psi_agent/workspace/umount/api.py`
- [x] 1.27 Add `from __future__ import annotations` to `src/psi_agent/workspace/snapshot/__init__.py`
- [x] 1.28 Add `from __future__ import annotations` to `src/psi_agent/workspace/snapshot/api.py`
- [x] 1.29 Add `from __future__ import annotations` to `src/psi_agent/channel/repl/__init__.py`
- [x] 1.30 Add `from __future__ import annotations` to `src/psi_agent/channel/repl/client.py`
- [x] 1.31 Add `from __future__ import annotations` to `src/psi_agent/channel/repl/config.py`
- [x] 1.32 Add `from __future__ import annotations` to `src/psi_agent/channel/repl/repl.py`
- [x] 1.33 Add `from __future__ import annotations` to `src/psi_agent/channel/telegram/__init__.py`
- [x] 1.34 Add `from __future__ import annotations` to `src/psi_agent/channel/telegram/bot.py`
- [x] 1.35 Add `from __future__ import annotations` to `src/psi_agent/channel/telegram/client.py`
- [x] 1.36 Add `from __future__ import annotations` to `src/psi_agent/channel/telegram/config.py`

## 2. Update CLAUDE.md documentation

- [x] 2.1 Add requirement for `from __future__ import annotations` in the type annotation conventions section

## 3. Verification

- [x] 3.1 Run `uv run ruff check && uv run ruff format && uv run ty check` to verify all checks pass