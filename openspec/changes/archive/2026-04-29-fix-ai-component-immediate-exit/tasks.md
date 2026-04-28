## 1. Fix AI Component CLIs

- [x] 1.1 Fix `src/psi_agent/ai/openai_completions/cli.py` - add `()` to `tyro.cli(OpenaiCompletions)`
- [x] 1.2 Fix `src/psi_agent/ai/anthropic_messages/cli.py` - add `()` to `tyro.cli(AnthropicMessages)`

## 2. Fix Session CLI

- [x] 2.1 Fix `src/psi_agent/session/cli.py` - add `()` to `tyro.cli(Session)`

## 3. Fix Channel CLIs

- [x] 3.1 Fix `src/psi_agent/channel/cli/cli.py` - add `()` to `tyro.cli(Cli)`
- [x] 3.2 Fix `src/psi_agent/channel/repl/cli.py` - add `()` to `tyro.cli(Repl)`
- [x] 3.3 Fix `src/psi_agent/channel/telegram/cli.py` - add `()` to `tyro.cli(Telegram)`

## 4. Fix Workspace CLIs

- [x] 4.1 Fix `src/psi_agent/workspace/pack/cli.py` - add `()` to `tyro.cli(Pack)`
- [x] 4.2 Fix `src/psi_agent/workspace/unpack/cli.py` - add `()` to `tyro.cli(Unpack)`
- [x] 4.3 Fix `src/psi_agent/workspace/mount/cli.py` - add `()` to `tyro.cli(Mount)`
- [x] 4.4 Fix `src/psi_agent/workspace/umount/cli.py` - add `()` to `tyro.cli(Umount)`
- [x] 4.5 Fix `src/psi_agent/workspace/snapshot/cli.py` - add `()` to `tyro.cli(Snapshot)`

## 5. Verification

- [x] 5.1 Run `uv run psi-ai-openai-completions --help` to verify CLI works
- [x] 5.2 Run `uv run psi-session --help` to verify CLI works
- [x] 5.3 Run `uv run psi-channel-telegram --help` to verify CLI works
- [x] 5.4 Run `uv run psi-workspace-pack --help` to verify CLI works
- [x] 5.5 Run existing tests to ensure no regressions
