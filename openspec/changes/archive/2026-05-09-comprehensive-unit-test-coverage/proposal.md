## Why

现有单元测试虽然覆盖了大部分 happy path，但从功能角度审视，存在三类关键缺陷：(1) 错误路径和异常处理几乎未测试——如 AI 客户端未初始化时调用、流式传输中途断连、manifest 解析的多种无效输入；(2) 防御性编程的 null/None 边界条件缺乏验证——如 LLM 响应中 content 为 None、tool_call arguments 为无效 JSON、mount info 缺少必要字段导致 KeyError；(3) 多步交互场景未覆盖——如 session 中多轮 tool call 循环、workspace 变更检测的混合变更、schedule 执行器的异常重试路径。这些问题在生产环境中极易触发，且缺少测试意味着回归风险高。

## What Changes

- **补全 AI 模块错误路径测试**：OpenAI/Anthropic 客户端未初始化调用、`_handle_error` 对 `APIStatusError`/通用异常的处理、流式传输中途错误、Anthropic `_handle_error` 缺少 `APITimeoutError` 测试
- **补全 translator 边界条件测试**：tool_call arguments 无效 JSON、tool result content 为 None、未知 tool 格式透传、Anthropic 响应缺少 usage/stop_reason/id/model 字段、SSE 流格式异常
- **补全 session 核心逻辑测试**：多轮 tool call 循环、workspace 变更检测的 tools_removed/skills_changed(system=None)/schedules_changed(executor=None) 路径、`_complete_fn` 对 None content 的处理、`_stream_conversation` 中 reasoning 字段端到端流式传输
- **补全 server 请求处理测试**：`_handle_chat_completions` 中 user_message content 为 None/空字符串、`_filter_for_channel` 对缺少 choices/message 字段的响应处理、server start/stop 异常路径
- **补全 schedule 执行器测试**：`_schedule_loop` 异常重试路径、CancelledError 处理、add_schedule 重复名称、remove_schedule 正在执行的 schedule、double start/stop
- **补全 workspace manifest 测试**：`parse_manifest` 对 layer 非对象/invalid parent UUID/tag 非字符串/default 无效 UUID 的处理、`resolve_chain` 断链场景、`serialize_manifest` default=None 的序列化/反序列化一致性
- **补全 workspace 操作测试**：pack 的 mksquashfs 失败路径、unpack 的 unsquashfs 失败路径、umount mount info 缺少字段的 KeyError 防护、snapshot 的 output_file 参数路径和 mount info 缺少字段防护
- **补全 channel 客户端 SSE 解析测试**：所有三个客户端（Repl/Cli/Telegram）的 null content、空字符串 content、reasoning 字段、choices 为空、delta 缺失等边界条件
- **补全 Telegram bot 测试**：`_stop()` 方法、split_message 精确边界位置、streaming 中 content_buffer 为空时的 fallback 路径
- **补全 CLI 入口测试**：所有 workspace CLI（pack/unpack/mount/umount/snapshot）的 `__call__` 和 `main` 函数

## Capabilities

### New Capabilities

- `ai-error-path-testing`: AI 客户端/服务端错误路径和异常处理的单元测试，包括未初始化调用、APIStatusError、流式传输中途错误、通用异常兜底
- `translator-edge-case-testing`: Anthropic translator 边界条件测试，包括无效 JSON arguments、None content、缺失字段响应、SSE 格式异常
- `session-conversation-testing`: Session 核心对话逻辑测试，包括多轮 tool call、workspace 变更检测混合场景、streaming reasoning 端到端
- `server-request-testing`: Session server 请求处理测试，包括 null content 防护、filter_for_channel 缺失字段、start/stop 异常路径
- `schedule-executor-edge-testing`: Schedule 执行器边界条件测试，包括异常重试、CancelledError、重复操作、并发修改
- `manifest-validation-testing`: Manifest 解析/序列化验证测试，包括无效输入类型、断链、default=None 一致性
- `workspace-operation-testing`: Workspace 操作（pack/unpack/mount/umount/snapshot）错误路径和边界条件测试
- `channel-sse-testing`: Channel 客户端 SSE 解析边界条件测试，覆盖所有三个客户端的 null/空/reasoning/缺失字段场景
- `telegram-bot-testing`: Telegram bot 完整功能测试，包括 _stop()、split_message 边界、streaming fallback
- `workspace-cli-testing`: Workspace 所有 CLI 入口的单元测试

### Modified Capabilities

## Impact

- **测试文件**：影响 `tests/` 下所有子目录，新增约 15-20 个测试文件或大幅扩展现有测试文件
- **源码**：可能发现并修复若干 bug（如 server.py 中 user_message content 为 None 时的崩溃、umount/snapshot 中 mount info 缺少字段时的 KeyError、manifest serialize_manifest default=None 不可反序列化）
- **依赖**：无新依赖，使用现有 pytest + pytest-asyncio 框架
- **CI**：测试时间可能增加，但仍在可接受范围内
