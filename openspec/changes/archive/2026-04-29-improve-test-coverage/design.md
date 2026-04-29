## Context

当前测试覆盖率 67%，部分模块覆盖率较低。本次变更专注于补充"容易写测试"的部分：

- 纯函数和工具函数（无外部依赖）
- 错误处理分支（通过 mock 模拟错误场景）
- CLI 参数解析（使用 tyro 的测试模式）
- Helper 函数（内部辅助函数）

**不涉及的部分**（需要复杂 mock 或外部依赖）：
- 实际网络请求
- 实际文件系统挂载操作（需要 root 权限）
- 实际 Unix socket 通信
- 需要外部服务（LLM API）的集成测试

## Goals / Non-Goals

**Goals:**
- 将整体覆盖率从 67% 提升到 80%+
- 为低覆盖率模块补充核心逻辑测试
- 发现并修复潜在的 bug（如有）
- 保持测试风格一致性（使用 pytest + pytest-asyncio）

**Non-Goals:**
- 不追求 100% 覆盖率
- 不添加需要复杂外部依赖的集成测试
- 不修改生产代码（除非发现 bug 需修复）
- 不重构现有测试结构

## Decisions

### 优先级排序

按"容易程度"和"价值"排序：

1. **高优先级**（纯函数，无依赖）：
   - `translator.py` (anthropic_messages) - 76% → 目标 90%+
   - `history.py` - 88% → 目标 95%+
   - `tool_loader.py` - 72% → 目标 85%+

2. **中优先级**（需要 mock）：
   - `server.py` (openai_completions) - 27% → 目标 70%+
   - `server.py` (session) - 49% → 目标 70%+
   - `runner.py` - 52% → 目标 70%+

3. **低优先级**（CLI 入口点，需要特殊处理）：
   - `cli.py` 文件 - 使用 tyro 的测试模式
   - `__main__.py` - 0% → 可通过 subprocess 测试

### 测试策略

- **纯函数**：直接调用，验证返回值
- **错误分支**：使用 `pytest.raises` + mock 模拟错误
- **异步函数**：使用 `pytest-asyncio` 的 `async def test_` 模式
- **CLI**：使用 tyro 的 `tyro.cli()` 测试参数解析

## Risks / Trade-offs

- **测试发现 bug** → 立即汇报给用户，不自行修复
- **Mock 过度** → 只 mock 外部依赖，不 mock 内部逻辑
- **覆盖率数字误导** → 关注实际测试质量，而非数字