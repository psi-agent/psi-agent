## Why

当前测试覆盖率为 47%，低于项目质量标准。多个核心模块覆盖率不足 80%，包括 CLI 入口点、AI 组件服务器、session 服务器等。提高测试覆盖率可以确保代码质量，减少回归风险。

## What Changes

- 为覆盖率低于 80% 的模块添加测试
- 重点覆盖以下模块：
  - `channel/cli/cli.py` (39%)
  - `ai/openai_completions/cli.py` (52%)
  - `session/cli.py` (52%)
  - `ai/anthropic_messages/cli.py` (53%)
  - `workspace/umount/api.py` (63%)
  - `ai/anthropic_messages/server.py` (65%)
  - `ai/anthropic_messages/client.py` (67%)

## Capabilities

### New Capabilities

- `test-coverage-improvement`: 为低覆盖率模块添加单元测试

### Modified Capabilities

None - 此变更仅添加测试，不修改现有功能需求。

## Impact

- 新增测试文件到 `tests/` 目录
- 无代码功能变更
- 提高整体测试覆盖率
