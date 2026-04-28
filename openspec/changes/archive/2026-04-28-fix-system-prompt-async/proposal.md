## Why

`_get_cached_system_prompt` 方法在已运行的 event loop 中调用 `run_until_complete()`，导致 `RuntimeError: This event loop is already running`。

## What Changes

- 修复 `runner.py` 中的 system prompt 加载逻辑
- 在 `__aenter__` 中预加载 system prompt，而不是在请求处理时同步加载

## Capabilities

### New Capabilities

<!-- No new capabilities -->

### Modified Capabilities

<!-- No spec-level requirement changes - this is a bug fix -->

## Impact

- `src/psi_agent/session/runner.py`: 修改 `_get_cached_system_prompt` 和 `__aenter__`