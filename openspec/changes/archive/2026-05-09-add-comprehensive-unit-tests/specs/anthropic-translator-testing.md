## anthropic-translator-testing

translator 模块的消息转换边界和畸形数据测试。

### _translate_message_to_anthropic

- content 为 None
- content 为数字（int/float）
- content 为空字符串
- content 为 list（content blocks 格式）
- role 为未知值
- tool_calls 为空数组
- tool_call.arguments 为非法 JSON
- tool_call 缺少 id/function 字段

### translate_openai_to_anthropic

- 多条 system 消息（只提取第一条）
- 无 system 消息
- 空消息列表
- messages 中只有 system 消息
- tools 为空列表
- max_tokens 已提供（不使用默认值）
- thinking 参数透传
- reasoning_effort 映射到 output_config

### translate_anthropic_to_openai

- 空 content blocks 列表
- 未知 stop_reason（默认映射为 "stop"）
- 无 usage 字段
- content 中有未知 block type（应忽略）

### StreamingTranslator

- 未知 event_type（应返回 None）
- message_start 无 message 字段
- content_block_delta 无 delta 字段
- 连续多个 thinking_delta 事件
- redacted_thinking 后的 delta 被跳过