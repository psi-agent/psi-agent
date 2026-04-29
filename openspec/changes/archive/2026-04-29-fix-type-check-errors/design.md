## Context

当前 `uv run ty check` 报告了约 100+ 行类型检查错误，主要分为以下几类：

1. **`response.text` 类型问题**：aiohttp 的 `web.Response.text` 类型注解是 `str | None`，但在实际使用中总是 `str`
2. **AsyncMock 赋值问题**：将 `AsyncMock` 赋值给类方法时，类型检查器无法识别这是测试 mock
3. **StreamResponse vs Response**：返回类型是联合类型时，访问 `text` 属性需要类型缩窄

## Goals / Non-Goals

**Goals:**
- 修复所有 `uv run ty check` 报告的类型错误
- 确保 `uv run ruff check && uv run ruff format && uv run ty check` 全部通过
- 保持测试代码的可读性和可维护性

**Non-Goals:**
- 不修改生产代码
- 不添加 `# type: ignore` 注释（除非绝对必要）
- 不改变测试逻辑

## Decisions

### 决策 1：使用 `isinstance` 进行类型缩窄

对于 `response.text` 类型问题，使用 `isinstance(response, web.Response)` 进行类型缩窄，而不是类型断言或 `# type: ignore`。

**理由**：这是类型安全的做法，且符合 Python 的惯用模式。

### 决策 2：使用 `# pyright: ignore` 处理 AsyncMock 赋值

对于将 `AsyncMock` 赋值给方法的情况，使用 `# pyright: ignore[reportInvalidAssignment]` 注释。

**理由**：这是测试代码中的常见模式，mock 替换方法是合理的。ty/pyright 无法理解这种测试模式。

### 决策 3：使用 `assert response.text is not None` 断言

对于确定 `response.text` 不为 None 的情况，添加断言让类型检查器知道。

**理由**：这是测试代码，断言失败意味着测试失败，这是合理的行为。

## Risks / Trade-offs

- **过度使用 ignore 注释** → 只在真正无法通过类型系统表达时使用
- **测试逻辑变化** → 修复类型时不改变测试逻辑
