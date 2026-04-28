## Why

CLI arguments passed via command line are visible in process listings (`ps`, `top`, `/proc/<pid>/cmdline`), exposing sensitive credentials like API keys and tokens. This is a security risk in multi-user environments where other users can view running processes.

## What Changes

- Add `setproctitle` dependency for runtime process title modification
- Create a utility module for masking sensitive arguments in process title
- Update all CLI entry points to mask sensitive arguments immediately after parsing:
  - `psi-ai-openai-completions`: mask `--api-key`
  - `psi-ai-anthropic-messages`: mask `--api-key`
  - `psi-channel-telegram`: mask `--token`
- Document this security practice in CLAUDE.md as a coding principle

## Capabilities

### New Capabilities

- `sensitive-args-masking`: Runtime masking of sensitive CLI arguments from process listings

### Modified Capabilities

- `psi-ai-openai-completions`: Add API key masking after CLI argument parsing
- `anthropic-messages-server`: Add API key masking after CLI argument parsing
- `telegram-channel`: Add token masking after CLI argument parsing
- `claude-md`: Add security principle for sensitive argument handling

## Impact

- New dependency: `setproctitle` package
- New module: `psi_agent.utils.proctitle` for process title manipulation
- Modified files:
  - `src/psi_agent/ai/openai_completions/cli.py`
  - `src/psi_agent/ai/anthropic_messages/cli.py`
  - `src/psi_agent/channel/telegram/cli.py`
  - `CLAUDE.md`
- Security posture improved: sensitive credentials no longer visible in process listings
