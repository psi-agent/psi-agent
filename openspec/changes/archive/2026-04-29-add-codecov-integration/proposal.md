## Why

当前 CI 已有覆盖率检查（`pytest --cov`），但覆盖率报告仅在本地生成，无法在 PR 中可视化查看覆盖率变化。集成 Codecov 可以：
- 在 PR 中显示覆盖率变化（增加/减少）
- 追踪覆盖率趋势历史
- 设置覆盖率门槛保护代码质量

## What Changes

- 在 CI workflow 中添加 Codecov action 上传覆盖率报告
- 生成 XML 格式的覆盖率报告供 Codecov 解析
- 添加分支覆盖率支持 (`--cov-branch`)
- 移除本地覆盖率阈值检查，由 Codecov 管理覆盖率门槛

## Capabilities

### New Capabilities

- `codecov-integration`: CI 中集成 Codecov 服务，自动上传覆盖率报告并在 PR 中显示覆盖率变化

### Modified Capabilities

- `ci-workflow`: 修改 `.github/workflows/ci.yml` 添加 Codecov 上传步骤

## Impact

- `.github/workflows/ci.yml` - 添加 Codecov action
- `.gitignore` - 添加 `coverage.xml`
- 需要 Codecov token（公开仓库可省略，私有仓库需要 `CODECOV_TOKEN` secret）
