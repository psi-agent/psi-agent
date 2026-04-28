## Why

之前的实现错误地从 session 传递 workspace 路径到 `build_system_prompt()`。这违反了 workspace 自包含的设计理念。workspace 路径应该由 `system.py` 自己通过 `__file__` 获取，无需外部传递。

## What Changes

- 移除 `runner.py` 中传递 workspace 参数的逻辑
- 修改 `system.py` 使用 `Path(__file__).parent.parent` 获取 workspace 路径
- `build_system_prompt()` 不再接受参数

## Capabilities

### New Capabilities

<!-- No new capabilities -->

### Modified Capabilities

<!-- No spec-level requirement changes -->

## Impact

- `src/psi_agent/session/runner.py`: 移除 workspace 参数传递逻辑
- `examples/a-simple-bash-only-workspace/systems/system.py`: 使用 `__file__` 获取 workspace 路径
