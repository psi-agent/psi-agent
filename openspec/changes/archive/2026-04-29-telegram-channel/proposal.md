## Why

psi-agent currently only has a REPL channel for terminal interaction. To make agents accessible on messaging platforms, we need a Telegram channel component that allows users to interact with psi-agent through Telegram bots. This enables broader accessibility and real-world deployment scenarios.

## What Changes

- Add new `psi-channel-telegram` CLI command for starting a Telegram bot channel
- Implement Telegram bot integration using `python-telegram-bot` library with async support
- Support `--token` CLI argument for Telegram bot token input
- Handle multiple concurrent users with session isolation
- Support both text messages and basic message formatting

## Capabilities

### New Capabilities

- `telegram-channel`: Telegram bot integration for psi-agent, enabling users to interact with agents through Telegram messaging platform

### Modified Capabilities

None - this is a new channel component with no changes to existing specs.

## Impact

- **New code**: `src/psi_agent/channel/telegram/` module with CLI, client, and bot handler
- **Dependencies**: Add `python-telegram-bot` library for Telegram Bot API
- **CLI**: New entry point `psi-channel-telegram` in package configuration
- **No breaking changes**: Existing channels (REPL) remain unchanged
