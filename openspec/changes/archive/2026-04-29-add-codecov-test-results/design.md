## Context

当前 CI 已集成 Codecov 覆盖率报告上传。pytest 支持生成 JUnit XML 格式的测试结果报告，Codecov 提供 `test-results-action` 可以解析并展示测试结果。

## Goals / Non-Goals

**Goals:**
- 在 PR 中显示测试结果状态
- 上传 JUnit XML 测试报告到 Codecov
- 支持查看测试失败详情

**Non-Goals:**
- 不修改测试本身
- 不配置 Codecov YAML 高级设置

## Decisions

### 1. 使用 JUnit XML 格式

**选择**: `--junitxml=junit.xml -o junit_family=legacy`

**理由**:
- pytest 原生支持 JUnit XML 格式
- Codecov test-results-action 完美支持
- `junit_family=legacy` 确保兼容性

### 2. 使用 codecov/test-results-action@v1

**选择**: 官方 test-results-action

**理由**:
- 与 codecov/codecov-action 配套
- 支持自动检测 JUnit XML 格式
- 使用相同的 `CODECOV_TOKEN`

### 3. 条件执行 `if: ${{ !cancelled() }}`

**选择**: 即使前面步骤失败也上传测试结果

**理由**:
- 测试失败时更需要查看测试结果
- `!cancelled()` 确保只有手动取消时才不上传

## Risks / Trade-offs

**风险**: 测试结果文件可能较大
→ **缓解**: JUnit XML 文件通常较小，且会被 gitignore 忽略
