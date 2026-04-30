## Why

当前测试覆盖率为 79%，存在多个关键模块覆盖率低于 70%，包括 CLI 入口点（0-52%）、workspace 操作 API（33-63%）和 schedule 执行器（54%）。低覆盖率增加了回归风险，不利于代码重构和维护。

## What Changes

- 为 `__main__.py` 添加入口点测试（当前 0%）
- 为 `workspace/snapshot/api.py` 添加完整测试（当前 33%）
- 为 `workspace/mount/api.py` 添加完整测试（当前 41%）
- 为 `channel/cli/cli.py` 添加测试（当前 40%）
- 为 `session/schedule.py` 添加测试（当前 54%）
- 为各组件 CLI 模块添加测试（当前 52-69%）
- 提升整体覆盖率目标至 90%+

## Capabilities

### New Capabilities

- `cli-entrypoint-testing`: 测试 psi-agent 主入口点和子命令路由
- `workspace-snapshot-testing`: 测试 workspace snapshot API 的完整功能
- `workspace-mount-testing`: 测试 workspace mount API 的完整功能
- `channel-cli-testing`: 测试 channel CLI 命令处理
- `schedule-execution-testing`: 测试定时任务执行器的完整逻辑

### Modified Capabilities

无现有 spec 需要修改，此变更仅增加测试代码。

## Impact

- 新增测试文件于 `tests/` 目录
- 不影响现有生产代码
- 提升 CI 质量保障能力
