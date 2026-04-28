## Why

需要在发布新版本时自动将包上传到 PyPI。当创建 tag 时，CI 应该自动构建并发布到 PyPI，实现自动化发布流程。

## What Changes

- 在 `.github/workflows/ci.yml` 中添加 PyPI 发布流程
- 当检测到 tag 时，执行 `uv build` 并使用 trusted publishing 上传到 PyPI

## Capabilities

### New Capabilities

<!-- No new capabilities - this is CI/CD configuration -->

### Modified Capabilities

<!-- No spec-level requirement changes -->

## Impact

- `.github/workflows/ci.yml`: 添加 PyPI 发布 job
