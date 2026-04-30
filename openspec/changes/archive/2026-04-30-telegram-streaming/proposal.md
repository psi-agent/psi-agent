## Why

Telegram 消息支持编辑功能，可以利用此特性实现流式输出效果，让用户实时看到 AI 响应的生成过程，提升用户体验。当前 Telegram channel 仅支持等待完整响应后一次性发送，用户需要等待较长时间才能看到任何输出。

## What Changes

- Telegram channel 新增流式输出模式（默认启用），通过编辑消息实现实时更新效果
- CLI 新增 `--no-stream` 开关用于禁用流式模式
- CLI 新增 `--stream-interval` 参数控制消息编辑的最小时间间隔（默认 1 秒）
- Client 新增 `send_message_stream()` 方法支持流式请求和消息编辑

## Capabilities

### New Capabilities

- `telegram-streaming-output`: Telegram channel 流式输出功能，通过消息编辑实现实时响应显示

### Modified Capabilities

- `telegram-channel`: 新增 CLI 参数（`--no-stream`, `--stream-interval`）和流式请求支持

## Impact

- `src/psi_agent/channel/telegram/cli.py` — 新增 `no_stream` 和 `stream_interval` 参数
- `src/psi_agent/channel/telegram/config.py` — 新增配置字段
- `src/psi_agent/channel/telegram/client.py` — 新增 `send_message_stream()` 方法
- `src/psi_agent/channel/telegram/bot.py` — 实现流式消息编辑逻辑
- `openspec/specs/telegram-channel/spec.md` — 新增流式相关需求
