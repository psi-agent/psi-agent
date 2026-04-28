# psi-agent

一个以**可移植性**和**组件化**为核心理念的 agent 框架。

## 简介

psi-agent 基于两个核心原则构建：

- **可移植性**：只需复制 `workspace` 目录即可完成 agent 的完整迁移。
- **组件化**：agent 由独立组件拼装而成，各组件通过 Unix socket 进行 IPC 通信，确保松耦合。

## 安装

### 使用 pip

```bash
pip install psi-agent
```

### 使用 uv

```bash
uv add psi-agent
```

## 快速开始

1. 创建 workspace 目录，包含你的 tools 和 skills：

```bash
mkdir -p workspace/{tools,skills,systems}
```

2. 启动 session 和 AI provider：

```bash
uv run psi-session \
  --workspace ./workspace \
  --channel-socket ./channel.sock \
  --ai-socket ./ai.sock
```

3. 启动 AI 组件（例如 OpenAI 兼容接口）：

```bash
uv run psi-ai-openai-completions \
  --session-socket ./ai.sock \
  --model <模型名称> \
  --api-key <你的-api-key> \
  --base-url <提供商-api-url>  # 例如 https://openrouter.ai/api/v1
```

> **注意：** `--base-url` 默认为 OpenAI 的 API。大多数用户需要指定其他提供商的 URL（例如 OpenRouter、Azure、本地 LLM 服务器）。

4. 启动 channel 与 agent 交互：

```bash
uv run psi-channel-repl --session-socket ./channel.sock
```

## 组件

psi-agent 包含四种组件类型：

| 组件 | 用途 |
|------|------|
| `psi-ai-*` | LLM 提供商适配器（OpenAI、Anthropic 等） |
| `psi-session` | Agent 运行循环，处理消息和 tool 调用 |
| `psi-channel-*` | 消息通道（REPL、Telegram、飞书等） |
| `psi-workspace-*` | Workspace 打包和挂载工具 |

### 可用命令

安装后，以下 CLI 工具可用：

- `psi-ai-openai-completions` - OpenAI 兼容的 completion 服务器
- `psi-ai-anthropic-messages` - Anthropic messages 服务器
- `psi-session` - Agent session 运行时
- `psi-channel-repl` - 交互式 REPL 界面
- `psi-channel-cli` - CLI channel 接口
- `psi-workspace-pack` - 将 workspace 打包为 squashfs
- `psi-workspace-unpack` - 将 squashfs 解压为目录
- `psi-workspace-mount` - 将 squashfs 挂载为 overlayfs
- `psi-workspace-umount` - 卸载 workspace
- `psi-workspace-snapshot` - 创建 workspace 快照

## 文档

详细文档包括 workspace 结构、tool 开发和配置，请参阅 [CLAUDE.md](CLAUDE.md)。

## 许可证

MIT License - 详见 [LICENSE.md](LICENSE.md)。
