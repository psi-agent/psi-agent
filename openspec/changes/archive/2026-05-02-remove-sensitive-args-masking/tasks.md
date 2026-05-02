## 1. Remove CLI masking calls

- [x] 1.1 Remove `mask_sensitive_args` call from `src/psi_agent/ai/openai_completions/cli.py`
- [x] 1.2 Remove `mask_sensitive_args` call from `src/psi_agent/ai/anthropic_messages/cli.py`
- [x] 1.3 Remove `mask_sensitive_args` call from `src/psi_agent/channel/telegram/cli.py`

## 2. Remove proctitle module

- [x] 2.1 Delete `src/psi_agent/utils/proctitle.py`
- [x] 2.2 Update `src/psi_agent/utils/__init__.py` to remove `mask_sensitive_args` export

## 3. Remove dependency

- [x] 3.1 Remove `setproctitle` from `pyproject.toml` dependencies

## 4. Update documentation

- [x] 4.1 Remove CLI security规范 section from `src/psi_agent/ai/CLAUDE.md`
- [x] 4.2 Update `CLAUDE.md` in project root to remove sensitive args masking references (if any)

## 5. Update tests

- [x] 5.1 Remove or update tests related to `mask_sensitive_args` (if any exist)
