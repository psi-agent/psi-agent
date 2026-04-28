# psi-agent

[中文](README_zh.md) | English

A portable and componentized agent framework.

## Introduction

psi-agent is built on two core principles:

- **Portability**: Copy just the `workspace` directory to migrate your agent completely.
- **Componentization**: Agents are assembled from independent components that communicate via Unix sockets, ensuring loose coupling.

## Installation

### Using uvx (Recommended)

For quick one-off usage without cloning the repository:

```bash
uvx psi-agent <component> <subcommand> [options...]
# e.g., uvx psi-agent session --workspace ./workspace ...
```

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
psi-agent session \
  --workspace ./workspace \
  --channel-socket ./channel.sock \
  --ai-socket ./ai.sock
```

3. Start an AI component (e.g., OpenAI-compatible):

```bash
psi-agent ai openai-completions \
  --session-socket ./ai.sock \
  --model <model-name> \
  --api-key <your-api-key> \
  --base-url <provider-api-url>  # e.g., https://openrouter.ai/api/v1
```

4. Start a channel to interact with your agent:

```bash
psi-agent channel repl --session-socket ./channel.sock
```

## CLI Interfaces

psi-agent provides two CLI interfaces:

1. **Subcommand interface (preferred)**: `psi-agent <component> <subcommand>`
   - Works with `uvx` without cloning the repository
   - Single entry point, easier to discover
   - Examples: `psi-agent ai openai-completions`, `psi-agent channel repl`

2. **Standalone commands**: `psi-<component>-<subcommand>`
   - Shorter to type
   - Useful in scripts
   - Examples: `psi-ai-openai-completions`, `psi-channel-repl`

Both interfaces are functionally identical. The subcommand interface is recommended for general use.

## Components

psi-agent consists of four component types:

| Component | Purpose |
|-----------|---------|
| `psi-ai-*` | LLM provider adapters (OpenAI, Anthropic, etc.) |
| `psi-session` | Agent runtime loop, handles messages and tool calls |
| `psi-channel-*` | Message channels (REPL, Telegram, Feishu, etc.) |
| `psi-workspace-*` | Workspace packaging and mounting tools |

### Available Commands

After installation, these commands are available:

**Subcommand format (preferred):**
- `psi-agent ai openai-completions` - OpenAI-compatible completion server
- `psi-agent ai anthropic-messages` - Anthropic messages server
- `psi-agent session` - Agent session runtime
- `psi-agent channel repl` - Interactive REPL interface
- `psi-agent channel cli` - CLI channel interface
- `psi-agent channel telegram` - Telegram bot channel
- `psi-agent workspace pack` - Package workspace to squashfs
- `psi-agent workspace unpack` - Extract squashfs to directory
- `psi-agent workspace mount` - Mount squashfs as overlayfs
- `psi-agent workspace umount` - Unmount workspace
- `psi-agent workspace snapshot` - Create workspace snapshot

**Standalone format (also available):**
- `psi-ai-openai-completions`
- `psi-ai-anthropic-messages`
- `psi-session`
- `psi-channel-repl`
- `psi-channel-cli`
- `psi-channel-telegram`
- `psi-workspace-pack`
- `psi-workspace-unpack`
- `psi-workspace-mount`
- `psi-workspace-umount`
- `psi-workspace-snapshot`

## Documentation

For detailed documentation including workspace structure, tool development, and configuration, see [CLAUDE.md](CLAUDE.md).

## License

GNU Affero General Public License v3.0 - see [LICENSE.md](LICENSE.md) for details.
