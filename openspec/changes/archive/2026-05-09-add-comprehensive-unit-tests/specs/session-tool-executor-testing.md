## session-tool-executor-testing

tool_executor 模块的 robustness 测试。

### execute_tool

- 工具函数抛 TypeError（参数不匹配）
- 工具函数抛 ValueError
- 工具函数抛自定义异常
- 工具函数返回 None
- 工具函数返回空字符串
- 工具函数返回非字符串（dict、list）
- tool_call 的 arguments 为空字符串
- tool_call 的 arguments 为非法 JSON

### execute_tools_parallel

- 空 tool_calls 列表
- tool_call 缺少 function 字段
- tool_call 缺少 id 字段
- 多个 tool_call 中部分失败
- 所有 tool_call 都失败
