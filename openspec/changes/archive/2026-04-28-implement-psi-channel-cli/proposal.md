## Why

目前缺少一个简单的命令行工具来与 psi-session 交互。psi-channel-cli 作为 channel 组件的最简实现，允许用户通过命令行发送消息给 session 并获取 agent 响应。

## What Changes

- 实现 psi-channel-cli 组件
- 作为 HTTP client 连接 psi-session 的 Unix socket
- 发送用户消息，接收 agent 响应，然后退出
- 编写相关单元测试

## Capabilities

### New Capabilities

- `channel-cli`: 命令行 channel 实现，连接 session socket，发送消息，输出响应

### Modified Capabilities

<!-- No existing capability requirements are changing -->

## Impact

- 新增 `src/psi_agent/channel/cli.py` 模块
- 新增 CLI 入口 `psi-channel-cli` 命令
- 新增 `tests/channel/` 测试目录
- pyproject.toml 添加新入口点