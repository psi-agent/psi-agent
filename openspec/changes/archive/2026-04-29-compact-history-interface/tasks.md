## 1. 类型定义

- [x] 1.1 在 `examples/an-openclaw-like-workspace/systems/system.py` 中定义 `CompleteFn` 类型别名

## 2. Token 估算

- [x] 2.1 添加 `_estimate_tokens()` 函数，使用 chars/4 启发式方法

## 3. 切割点算法

- [x] 3.1 添加 `_find_cut_point()` 函数，从后往前累积 token
- [x] 3.2 添加 `_find_turn_start()` 函数，找到 turn 起始的 user 消息

## 4. 摘要提示词

- [x] 4.1 添加 `_HISTORY_SUMMARY_PROMPT` 常量
- [x] 4.2 添加 `_TURN_PREFIX_SUMMARY_PROMPT` 常量
- [x] 4.3 添加 `_build_summarization_prompt()` 函数

## 5. compact_history 函数修改 (OpenClaw-like)

- [x] 5.1 修改函数签名，添加 `complete_fn` 和 `keep_recent_tokens` 参数
- [x] 5.2 实现切割点检测逻辑
- [x] 5.3 实现 split turn 检测和处理
- [x] 5.4 实现历史摘要生成
- [x] 5.5 实现 turn prefix 摘要生成（split turn 时）

## 6. compact_history 函数修改 (Simple)

- [x] 6.1 修改 simple workspace 的函数签名，添加 `complete_fn` 参数
- [x] 6.2 实现基于 token 的简单截断逻辑

## 7. 验证

- [x] 7.1 运行 `ruff check` 验证代码风格
- [x] 7.2 运行 `ruff format` 格式化代码
- [x] 7.3 运行 `ty check` 验证类型
