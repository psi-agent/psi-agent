## Context

The `examples/an-openclaw-like-workspace` is a reference implementation that mimics OpenClaw's behavior. Three functions need to be fixed to match OpenClaw's implementation.

### Current vs OpenClaw Implementations

**1. `is_real_conversation_message()` signature:**

Current (Python):
```python
def is_real_conversation_message(message: dict[str, Any]) -> bool:
    role = message.get("role")
    if role in ("user", "assistant"):
        return has_meaningful_conversation_content(message)
    if role in ("tool", "toolResult", "tool_result"):
        return False  # BUG: No lookback
    return False
```

OpenClaw (TypeScript):
```typescript
export function isRealConversationMessage(
  message: AgentMessage,
  messages: AgentMessage[],
  index: number,
): boolean {
  if (message.role === "user" || message.role === "assistant") {
    return hasMeaningfulConversationContent(message);
  }
  if (message.role !== "toolResult") {
    return false;
  }
  const start = Math.max(0, index - TOOL_RESULT_REAL_CONVERSATION_LOOKBACK);
  for (let i = index - 1; i >= start; i -= 1) {
    const candidate = messages[i];
    if (!candidate || candidate.role !== "user") continue;
    if (hasMeaningfulConversationContent(candidate)) return true;
  }
  return false;
}
```

**2. `_has_meaningful_text()` heartbeat handling:**

Current (Python):
```python
def _has_meaningful_text(text: str) -> bool:
    trimmed = text.strip()
    if not trimmed:
        return False
    if trimmed == SILENT_TOKEN:
        return False
    return trimmed != HEARTBEAT_OK  # Simple comparison
```

OpenClaw (TypeScript):
```typescript
function hasMeaningfulText(text: string): boolean {
  const trimmed = text.trim();
  if (!trimmed) return false;
  if (isSilentReplyText(trimmed)) return false;
  const heartbeat = stripHeartbeatToken(trimmed, { mode: "message" });
  if (heartbeat.didStrip) {
    return heartbeat.text.trim().length > 0;
  }
  return true;
}
```

**3. `SILENT_TOKEN` value:**

- OpenClaw: `SILENT_REPLY_TOKEN = "NO_REPLY"`
- Current: `SILENT_TOKEN = "SILENT_TOKEN"`

## Goals / Non-Goals

**Goals:**
- Fix all three inconsistencies to match OpenClaw's behavior
- Keep implementation simple and Pythonic (no need for full regex complexity of OpenClaw's `stripHeartbeatToken`)

**Non-Goals:**
- Full parity with OpenClaw's regex-based markup stripping (simplified version is sufficient)
- Changing Runtime info or Tool Call Style (DIFF.md already documents these as intentional differences)

## Decisions

### Decision 1: Implement `strip_heartbeat_token()` in Python

**Choice:** Create a simplified Python version that handles common cases

**Rationale:** OpenClaw's version handles many edge cases with regex. A simplified version that:
1. Strips `HEARTBEAT_OK` at start/end
2. Handles trailing punctuation (`.`, `!`, `-`)
3. Handles basic markdown wrappers (`**`, `__`, `~~`, backticks)

is sufficient for the workspace use case.

**Implementation:**
```python
def strip_heartbeat_token(text: str) -> tuple[str, bool]:
    """Strip HEARTBEAT_OK from text edges.

    Returns (remaining_text, did_strip).
    """
    HEARTBEAT_OK = "HEARTBEAT_OK"
    trimmed = text.strip()
    if not trimmed:
        return "", False

    # Handle basic markdown wrappers
    for wrapper in ["**", "__", "~~", "`"]:
        if trimmed.startswith(wrapper) and trimmed.endswith(wrapper):
            inner = trimmed[len(wrapper):-len(wrapper)]
            if inner.strip() == HEARTBEAT_OK:
                return "", True
            if inner.startswith(HEARTBEAT_OK):
                return inner[len(HEARTBEAT_OK):].strip(), True
            if inner.endswith(HEARTBEAT_OK):
                return inner[:-len(HEARTBEAT_OK)].strip(), True

    # Strip at start
    if trimmed.startswith(HEARTBEAT_OK):
        rest = trimmed[len(HEARTBEAT_OK):].strip()
        return rest, True

    # Strip at end with optional trailing punctuation
    for suffix in ["", ".", "!", "-", "---", "!!!"]:
        if trimmed.endswith(HEARTBEAT_OK + suffix):
            rest = trimmed[:-len(HEARTBEAT_OK + suffix)].strip()
            return rest, True

    return trimmed, False
```

### Decision 2: Update function signature for `is_real_conversation_message()`

**Choice:** Add `history` and `index` parameters

**Rationale:** Required for tool result lookback. The caller `_contains_real_conversation_messages()` already has access to full history via `any()` which provides index via `enumerate()`.

### Decision 3: Change `SILENT_TOKEN` to `"NO_REPLY"`

**Choice:** Use OpenClaw's token value

**Rationale:** Ensures compatibility with any tool/skill that expects OpenClaw's token format.

## Risks / Trade-offs

- **Risk:** `strip_heartbeat_token()` simplified version may miss some edge cases
  - **Mitigation:** The edge cases are rare (model wrapping HEARTBEAT_OK in unusual markup). Core functionality works.

- **Risk:** Changing `SILENT_TOKEN` could break existing workspace users
  - **Mitigation:** This is an example workspace, not a production system. The change aligns with documented OpenClaw compatibility goal.