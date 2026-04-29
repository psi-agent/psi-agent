## Why

当前 Codecov 已集成覆盖率报告，但缺少测试结果上传功能。上传测试结果可以在 Codecov 中查看测试失败详情、测试趋势历史，并在 PR 中显示测试状态变化。

## What Changes

- 在 pytest 命令中添加 `--junitxml=junit.xml -o junit_family=legacy` 参数生成 JUnit XML 报告
- 添加 `codecov/test-results-action@v1` 上传测试结果
- 将 `junit.xml` 添加到 `.gitignore`

## Capabilities

### New Capabilities

- `codecov-test-results`: CI 中上传 JUnit 测试结果到 Codecov，显示测试状态和失败详情

### Modified Capabilities

- `ci-workflow`: 修改 pytest 命令生成 JUnit XML，添加 test-results-action

## Impact

- `.github/workflows/ci.yml` - 添加 test-results-action，修改 pytest 命令
- `.gitignore` - 添加 `junit.xml`
