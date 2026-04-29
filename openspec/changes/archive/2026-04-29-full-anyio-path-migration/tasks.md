## 1. Config Files Migration

- [x] 1.1 Migrate `src/psi_agent/channel/telegram/config.py` - Replace `from pathlib import Path` with `import anyio`, change return type to `anyio.Path`
- [x] 1.2 Migrate `src/psi_agent/channel/repl/config.py` - Replace `from pathlib import Path` with `import anyio`, change return types to `anyio.Path`
- [x] 1.3 Migrate `src/psi_agent/session/config.py` - Replace `from pathlib import Path` with `import anyio`, change return types to `anyio.Path`
- [x] 1.4 Migrate `src/psi_agent/ai/anthropic_messages/config.py` - Replace `from pathlib import Path` with `import anyio`, change return type to `anyio.Path`
- [x] 1.5 Migrate `src/psi_agent/ai/openai_completions/config.py` - Replace `from pathlib import Path` with `import anyio`, change return type to `anyio.Path`

## 2. Session Files Migration

- [x] 2.1 Migrate `src/psi_agent/session/schedule.py` - Replace `from pathlib import Path` with `import anyio`, change `Schedule.task_dir` type to `anyio.Path`, update all `Path()` usages
- [x] 2.2 Migrate `src/psi_agent/session/workspace_watcher.py` - Replace `from pathlib import Path` with `import anyio`, change all type annotations and `Path()` usages
- [x] 2.3 Migrate `src/psi_agent/session/tool_loader.py` - Replace `from pathlib import Path` with `import anyio`, change all type annotations and `Path()` usages
- [x] 2.4 Migrate `src/psi_agent/session/runner.py` - Replace `from pathlib import Path` with `import anyio`, change parameter types
- [x] 2.5 Migrate `src/psi_agent/session/history.py` - Replace `from pathlib import Path` with `import anyio` if present, change parameter types

## 3. Workspace Files Migration

- [x] 3.1 Migrate `src/psi_agent/workspace/snapshot/api.py` - Replace `from pathlib import Path` with `import anyio`, change all type annotations and `Path()` usages
- [x] 3.2 Migrate `src/psi_agent/workspace/umount/api.py` - Replace `from pathlib import Path` with `import anyio`, change all type annotations and `Path()` usages
- [x] 3.3 Migrate `src/psi_agent/workspace/mount/api.py` - Replace `from pathlib import Path` with `import anyio`, change all type annotations and `Path()` usages
- [x] 3.4 Migrate `src/psi_agent/workspace/unpack/api.py` - Replace `from pathlib import Path` with `import anyio`, change all type annotations and `Path()` usages
- [x] 3.5 Migrate `src/psi_agent/workspace/pack/api.py` - Replace `from pathlib import Path` with `import anyio`, change all type annotations and `Path()` usages

## 4. AI Files Migration

- [x] 4.1 Migrate `src/psi_agent/ai/openai_completions/server.py` - Replace `from pathlib import Path` with `import anyio`, change all `Path()` usages

## 5. Verification

- [x] 5.1 Run `ruff check` to verify no lint errors
- [x] 5.2 Run `ruff format` to verify formatting
- [x] 5.3 Run `ty check` to verify type checking passes
- [x] 5.4 Run `pytest` to verify all tests pass
