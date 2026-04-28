## Why

psi-agent 项目目前只有 CLAUDE.md 指导文件，缺少 Python package 框架和实际组件实现。需要建立项目基础设施（pyproject.toml）并实现 psi_agent.ai.openai_completions 子包，作为 LLM 提供商适配层的基础实现。

## What Changes

- 创建 pyproject.toml，定义项目元数据和依赖，包含 script 入口点
- 创建 src/psi_agent/ 目录结构，组织组件源代码
- 实现 psi_agent.ai.openai_completions 子包：
  - 提供 Python API 用于程序化调用
  - 提供 CLI 入口（通过 tyro 封装 Python API）
  - 启动 HTTP server 监听 Unix socket
  - 接收 OpenAI chat completion 格式请求
  - 转发请求给底层 OpenAI-compatible API
  - 返回响应给 psi-session
- 使用 loguru 进行详细日志记录
- 编写单元测试放在 tests/ 目录

## Capabilities

### New Capabilities
- `psi-ai-openai-completions`: LLM 提供商适配组件，使用 HTTP over Unix socket，支持 OpenAI chat completion 协议

### Modified Capabilities

(None - this is the first component implementation)

## Impact

- 新增文件：pyproject.toml, src/psi_agent/ai/openai_completions/, tests/
- 依赖：aiohttp, httpx, loguru, tyro
- 脚本入口：psi-ai-openai-completions (CLI)
- 受影响：后续 psi-session 和 psi-channel-* 组件将使用相同通信模式