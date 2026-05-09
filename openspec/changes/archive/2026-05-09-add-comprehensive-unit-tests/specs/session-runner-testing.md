## session-runner-testing

runner 模块的流式解析边界和 tool call 重构测试。

### _reconstruct_tool_calls

- 空 tool_calls 列表
- index 不连续（0, 2, 5）
- 超大 index 值
- function.name 为 None
- function.arguments 逐步拼接（多个 delta 拼接成完整 JSON）
- 多个 tool call 交错出现

### _parse_streaming_response

- SSE 行超长（> 10KB）
- 非 UTF-8 字节（应捕获 UnicodeDecodeError）
- 连续多个 error chunk
- data: [DONE] 后还有数据行
- data: 行后无内容
- data: 后跟非 JSON 字符串
- content 为 None 的 delta
- tool_calls 为 None 的 delta
- reasoning_content 字段

### format_thinking_block

- 空字符串内容
- 多行内容
- 内容含特殊字符（XML 标签、反引号）

### format_tool_call_thinking

- 空字符串内容
- 多行内容