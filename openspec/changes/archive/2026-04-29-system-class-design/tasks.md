## 1. System 类设计

- [x] 1.1 在 OpenClaw-like workspace 中创建 `System` 类
- [x] 1.2 添加 `__init__` 方法，初始化 `_workspace_dir` 和 `_previous_summary`
- [x] 1.3 将 `build_system_prompt()` 改为实例方法
- [x] 1.4 将 `compact_history()` 改为实例方法

## 2. 常量和工具函数

- [x] 2.1 添加 `_SUMMARIZATION_SYSTEM_PROMPT` 常量
- [x] 2.2 添加 `_UPDATE_SUMMARIZATION_PROMPT` 常量
- [x] 2.3 添加 `_TOOL_RESULT_MAX_CHARS` 常量
- [x] 2.4 添加 `_truncate_for_summary()` 函数

## 3. 消息序列化改进

- [x] 3.1 修改 `_build_summarization_prompt()` 处理 `thinking` 块
- [x] 3.2 修改 `_build_summarization_prompt()` 处理 `toolCall` 块
- [x] 3.3 修改 `_build_summarization_prompt()` 处理 `toolResult` 块（带截断）

## 4. 增量摘要更新

- [x] 4.1 在 `compact_history()` 中使用 `_previous_summary`
- [x] 4.2 更新 `_previous_summary` 状态

## 5. Simple workspace 更新

- [x] 5.1 创建 `System` 类（简单实现）
- [x] 5.2 将函数改为实例方法

## 6. 验证

- [x] 6.1 运行 `ruff check` 验证代码风格
- [x] 6.2 运行 `ruff format` 格式化代码
- [x] 6.3 运行 `ty check` 验证类型