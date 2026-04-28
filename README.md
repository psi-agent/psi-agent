# psi-agent

[中文](README_zh.md) | English

A portable and componentized agent framework.

## Introduction

psi-agent is built on two core principles:

- **Portability**: Copy just the `workspace` directory to migrate your agent completely.
- **Componentization**: Agents are assembled from independent components that communicate via Unix sockets, ensuring loose coupling.

## Installation

### Using pip

```bash
pip install psi-agent
```

### Using uv

```bash
uv add psi-agent
```

## Quick Start

1. Create a workspace directory with your tools and skills:

```bash
mkdir -p workspace/{tools,skills,systems}
```

2. Start the session with an AI provider:

```bash
uv run psi-session \
  --workspace ./workspace \
  --channel-socket ./channel.sock \
  --ai-socket ./ai.sock
```

3. Start an AI component (e.g., OpenAI-compatible):

```bash
uv run psi-ai-openai-completions \
  --session-socket ./ai.sock \
  --model <model-name> \
  --api-key <your-api-key> \
  --base-url <provider-api-url>  # e.g., https://openrouter.ai/api/v1
```

4. Start a channel to interact with your agent:

```bash
uv run psi-channel-repl --session-socket ./channel.sock
```

## Components

psi-agent consists of four component types:

| Component | Purpose |
|-----------|---------|
| `psi-ai-*` | LLM provider adapters (OpenAI, Anthropic, etc.) |
| `psi-session` | Agent runtime loop, handles messages and tool calls |
| `psi-channel-*` | Message channels (REPL, Telegram, Feishu, etc.) |
| `psi-workspace-*` | Workspace packaging and mounting tools |

### Available Scripts

After installation, these CLI tools are available:

- `psi-ai-openai-completions` - OpenAI-compatible completion server
- `psi-ai-anthropic-messages` - Anthropic messages server
- `psi-session` - Agent session runtime
- `psi-channel-repl` - Interactive REPL interface
- `psi-channel-cli` - CLI channel interface
- `psi-workspace-pack` - Package workspace to squashfs
- `psi-workspace-unpack` - Extract squashfs to directory
- `psi-workspace-mount` - Mount squashfs as overlayfs
- `psi-workspace-umount` - Unmount workspace
- `psi-workspace-snapshot` - Create workspace snapshot

## Documentation

For detailed documentation including workspace structure, tool development, and configuration, see [CLAUDE.md](CLAUDE.md).

## License

GNU Affero General Public License v3.0 - see [LICENSE.md](LICENSE.md) for details.
