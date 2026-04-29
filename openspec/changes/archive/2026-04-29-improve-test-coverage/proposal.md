## Why

当前测试覆盖率为 67%，存在多个覆盖率较低的模块。补充测试可以提高代码质量、捕获潜在 bug，并为未来重构提供安全网。本次变更专注于"容易写测试但目前没写"的部分，避免需要复杂 mock 或外部依赖的测试。

## What Changes

- 为低覆盖率的纯函数和工具函数补充单元测试
- 为错误处理分支补充测试
- 为 CLI 参数解析补充测试（不涉及实际执行）
- 为 helper 函数补充测试

## Capabilities

### New Capabilities

- `test-coverage-improvement`: 补充测试覆盖率，目标是将整体覆盖率从 67% 提升到 80%+

### Modified Capabilities

无（仅添加测试，不修改现有功能）

## Impact

- 影响文件：`tests/` 目录下的测试文件
- 不影响生产代码
- 可能发现现有代码的 bug（需及时汇报）
