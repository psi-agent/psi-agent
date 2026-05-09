## Context

psi-agent 的现有测试存在两个层面的问题：

1. **Happy path 缺失**：多个核心模块的公共 API 完全没有测试文件（session/types.py、session/config.py），或关键成功路径未覆盖（runner._load_system、ScheduleExecutor._schedule_loop 正常执行、CliClient._send_non_streaming/_send_streaming HTTP 交互成功路径）。

2. **Corner case / robustness 缺失**：已有测试多覆盖 happy path，但对边界条件（空输入、None 值、格式畸形等）和防御性编程路径的验证不足。

经逐模块核对，以下模块的 happy path 已基本覆盖，不需要补充：channel/repl/repl.py（Repl.run 已有完整测试）、channel/telegram/bot.py（_handle_message、_mask_proxy_credentials、start 均已有大量测试）。

本次变更仅新增测试，不修改生产代码。优先补充 happy path 缺失，再补充 corner case。

## Goals / Non-Goals

**Goals:**
- 优先补充缺失的 happy path 测试（核心数据结构、辅助方法、关键成功路径）
- 为每个核心模块补充 corner case 和 robustness 测试
- 覆盖所有公共 API 的边界条件（空输入、None 值、畸形数据、异常路径）
- 确保防御性编程路径（null 检查、异常捕获、格式容错）有对应测试验证
- 测试文件遵循项目现有约定（pytest + pytest-asyncio，tests/ 目录结构对应 src/）

**Non-Goals:**
- 不追求 100% 代码覆盖率数字，而是从功能角度确保关键行为有测试
- 不修改任何生产代码
- 不新增测试框架或依赖
- 不做集成测试或端到端测试，仅限单元测试
- 不测试 CLI 入口（已有 test_cli 覆盖）
- 不为已充分测试的 happy path 重复添加测试（Repl.run、TelegramBot._handle_message 等）

## Decisions

### 1. 测试组织方式：在现有测试文件中追加测试类，或创建新测试文件

**选择**：
- 对于已有对应测试文件的模块，在现有文件中追加测试类
- 对于没有对应测试文件的模块（session/types.py、session/config.py），创建新测试文件

**理由**：
- 现有测试文件已经对应源模块，保持一致性
- 没有测试文件的模块需要新文件来承载测试
- 新测试类使用描述性命名（如 `TestToolRegistryHappyPath`、`TestToolRegistryCornerCases`）区分于现有测试

### 2. 测试数据构造：使用临时文件和内联定义

**选择**：使用 `tmp_path` fixture 和内联字符串构造测试数据。

**理由**：
- 与现有测试风格一致
- 避免引入外部 fixture 文件
- anyio.Path 与 tmp_path 配合良好

### 3. 异步测试标记：使用 `@pytest.mark.asyncio`

**选择**：继续使用 `@pytest.mark.asyncio` 装饰器标记异步测试。

**理由**：与现有测试风格一致，项目已配置 pytest-asyncio。

### 4. Mock 策略：最小化 mock，优先真实执行

**选择**：对于纯逻辑函数（parse、translate、format 等）直接调用不 mock；对于涉及 IO 或外部依赖的函数使用 `unittest.mock`。

**理由**：单元测试应验证实际行为而非 mock 行为，仅在不可避免时使用 mock。

### 5. 实现优先级：happy path 先于 corner case

**选择**：先补充缺失的 happy path 测试，再补充 corner case 测试。

**理由**：happy path 缺失意味着基本功能正确性无法验证，这是比边界条件更严重的问题。

### 6. 已充分测试的模块不重复添加 happy path 测试

**选择**：经核对确认 happy path 已充分覆盖的模块（Repl.run、TelegramBot._handle_message 等），不再添加重复的 happy path 测试，仅补充 corner case。

**理由**：避免测试冗余，集中精力在真正缺失的测试上。

## Risks / Trade-offs

- [测试与实现耦合] → 通过测试公共 API 行为而非实现细节来缓解；测试描述"应该做什么"而非"怎么做的"
- [现有测试可能需要调整 import] → 新测试仅在现有文件中追加或创建新文件，不修改现有测试代码
- [部分边界条件可能触发未发现的 bug] → 这是好事，发现 bug 后应记录但不在此变更中修复（仅补充测试）
- [CliClient HTTP 交互测试需要 mock aiohttp] → 使用 unittest.mock 隔离 aiohttp 依赖，只验证请求构造和响应解析逻辑
