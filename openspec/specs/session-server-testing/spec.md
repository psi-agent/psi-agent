## session-server-testing

server 模块的请求处理边界和响应过滤测试。

### _filter_for_channel

- choices 为空列表
- choices[0] 无 message 字段
- message.content 为空字符串
- message.content 为 None
- message 有 tool_calls 字段（应被过滤）
- message 有 function_call 字段（应被过滤）
- 多个 choices（只取第一个）

### _handle_chat_completions

- stream=True 但 runner 未初始化
- messages 为空列表
- messages 中多条 user 消息
- messages 中 system 消息不在首位
- request model 字段为空字符串
- request 缺少必要字段