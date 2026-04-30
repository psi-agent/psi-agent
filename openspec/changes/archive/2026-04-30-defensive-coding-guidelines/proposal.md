## Why

The psi-agent system has experienced multiple crashes due to null-safety issues when processing streaming responses from LLM providers. These issues stem from inconsistent defensive coding practices across components. The OpenAI streaming API specification allows fields to be `null` or absent in delta chunks, but our code often assumes non-null values. This change establishes systematic defensive coding guidelines and applies them consistently across all components.

## What Changes

- Add defensive coding guidelines section to CLAUDE.md (~20 lines)
- Apply null-safety patterns across all components:
  - **psi-ai-***: OpenAI completions client/server, Anthropic messages translator
  - **psi-session**: Runner, server, tool executor
  - **psi-channel-***: REPL client, Telegram client, CLI client
- Standardize on `dict.get("key") is not None` pattern for null checks before operations

## Capabilities

### New Capabilities

- `defensive-coding`: Guidelines and patterns for null-safe handling of external data

### Modified Capabilities

- `streaming-null-handling`: Extend to cover all streaming code paths across all components

## Impact

- **Affected Components**: All components that handle external data (LLM responses, user input)
- **Affected Files**:
  - `src/psi_agent/session/runner.py` - streaming delta processing
  - `src/psi_agent/session/server.py` - request handling
  - `src/psi_agent/session/tool_executor.py` - tool call processing
  - `src/psi_agent/ai/openai_completions/client.py` - streaming response handling
  - `src/psi_agent/ai/anthropic_messages/translator.py` - response translation
  - `src/psi_agent/channel/repl/client.py` - streaming display
  - `src/psi_agent/channel/telegram/client.py` - streaming display
  - `src/psi_agent/channel/cli/cli.py` - streaming display
- **CLAUDE.md**: Add defensive coding guidelines section

## Root Cause Pattern

All crashes share the same pattern: **assuming external data fields are non-null without verification**.

```python
# Problematic: assumes value is a string
result += data["field"]

# Safe: checks for null before operation
if data.get("field") is not None:
    result += data["field"]
```
