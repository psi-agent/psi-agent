## Why

当前 `uv run ty check` 报告了约 100+ 行类型检查错误，主要集中在测试文件中。这些错误会导致 CI 检查失败，需要修复以确保代码质量。

## What Changes

- 修复测试文件中的类型注解问题
- 为 mock 对象添加适当的类型断言
- 修复 `response.text` 的类型检查问题（`str | None` vs `str`）
- 修复 AsyncMock 赋值给方法的问题

## Capabilities

### New Capabilities

无（仅修复类型检查错误，不添加新功能）

### Modified Capabilities

无

## Impact

- 影响文件：`tests/` 目录下的测试文件
- 不影响生产代码
- 确保 `uv run ruff check && uv run ruff format && uv run ty check` 全部通过
