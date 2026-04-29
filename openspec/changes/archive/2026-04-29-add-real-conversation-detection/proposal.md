## Why

When an agent runs for a long time with heartbeat polling enabled, the conversation history can accumulate many heartbeat messages (where the agent replies `HEARTBEAT_OK` to each poll). These messages are not real user-AI conversations, but our current `compact_history()` implementation treats them as normal messages and performs LLM summarization on them. This wastes LLM API calls and resources.

OpenClaw solves this by detecting whether messages contain "real conversation content" before compaction. If the entire history contains only heartbeat replies, silent replies (`SILENT_TOKEN`), or non-meaningful content, compaction is skipped entirely.

## What Changes

- Add a `has_meaningful_conversation_content()` function to detect if a message contains real conversation content
- Add an `is_real_conversation_message()` function to determine if a message is part of a real conversation
- Modify `compact_history()` to skip compaction when no real conversation messages exist
- Update DIFF.md to document this new feature

## Capabilities

### New Capabilities

- `real-conversation-detection`: Detects whether messages contain meaningful conversation content, distinguishing real user-AI dialogue from system artifacts like heartbeat replies and silent responses.

### Modified Capabilities

- `history-compaction`: The compaction behavior is enhanced to skip summarization when no real conversation content exists.

## Impact

- `examples/an-openclaw-like-workspace/systems/system.py`: Add real conversation detection functions and integrate into `compact_history()`
- `examples/an-openclaw-like-workspace/DIFF.md`: Document the new feature
