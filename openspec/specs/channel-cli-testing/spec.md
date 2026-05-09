## channel-cli-testing

CliClient 的 _send_non_streaming 和 _send_streaming HTTP 交互成功路径测试。

### CliClient._send_non_streaming

- mock aiohttp 返回 200 响应，验证返回 content 字符串
- mock aiohttp 返回非 200 状态码，验证返回错误字符串
- mock aiohttp 返回空 choices，验证返回 "Error: No response from session"
- mock aiohttp 抛出 ClientConnectorError，验证返回连接错误字符串
- mock aiohttp 抛出 TimeoutError，验证返回超时错误字符串

### CliClient._send_streaming

- mock SSE 响应，验证正确解析 content chunks 并返回完整内容
- mock SSE 响应含 reasoning 字段，验证 reasoning 被记录但不返回
- mock SSE 响应含 [DONE] 标记，验证正确终止
- mock SSE 响应含无效 JSON 行，验证跳过不崩溃
- mock aiohttp 返回非 200 状态码，验证返回错误字符串
- on_chunk 回调在 content 非空时被调用

### CliClient.send_message

- config.stream=True 时分发到 _send_streaming
- config.stream=False 时分发到 _send_non_streaming
- 未初始化 session 时抛出 RuntimeError
