## Why

psi-session 是 psi-agent 框架的核心组件，负责 agent 的运行循环。目前只有 psi-ai-openai-completions 实现，缺少 session 组件无法组成完整的 agent 系统。

## What Changes

- 实现 psi-session 组件的核心运行循环
- 实现 tool 动态扫描、注册和执行机制
- 实现 history 内存管理和可选 JSON 持久化
- 实现 system prompt builder 调用接口
- 作为 HTTP server 接收 channel 请求
- 作为 HTTP client 调用 psi-ai-* 服务
- 编写完整的单元测试

## Capabilities

### New Capabilities

- `session-core`: Session 核心运行循环，处理消息流转
- `tool-execution`: Tool 动态加载、注册和执行机制
- `history-management`: 对话历史的内存管理和持久化

### Modified Capabilities

<!-- No existing capability requirements are changing -->

## Impact

- 新增 `src/psi_agent/session/` 目录及模块
- 新增 CLI 入口 `psi-session` 命令
- 新增 `tests/session/` 测试目录
- pyproject.toml 添加新入口点
- 新增 workspace 相关类型定义