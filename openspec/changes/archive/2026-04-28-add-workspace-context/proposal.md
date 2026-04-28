## Why

Agent 不知道自己的 workspace 目录在哪里，导致执行 bash 命令时无法确定工作目录。需要在 system prompt 中告知 agent 其 workspace 路径，并在 bash tool 中提供设置运行目录的参数。

## What Changes

- 在 `build_system_prompt()` 中添加 workspace 目录信息
- 在 bash tool 中添加 `cwd` 参数，用于指定命令运行目录

## Capabilities

### New Capabilities

<!-- No new capabilities - this is an enhancement to existing workspace tools -->

### Modified Capabilities

<!-- No spec-level requirement changes -->

## Impact

- `examples/a-simple-bash-only-workspace/systems/system.py`: 添加 workspace 路径到 system prompt
- `examples/a-simple-bash-only-workspace/tools/bash.py`: 添加 `cwd` 参数
