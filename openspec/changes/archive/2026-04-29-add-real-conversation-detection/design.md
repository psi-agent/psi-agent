## Context

The `an-openclaw-like-workspace` implements a system similar to OpenClaw, including system prompt building and conversation history compaction. Currently, the `compact_history()` method performs LLM summarization on all messages regardless of whether they contain meaningful conversation content.

In long-running sessions with heartbeat polling enabled, the conversation history can accumulate many messages that are not real user-AI dialogue:
- Heartbeat replies: Agent responds with `HEARTBEAT_OK` to periodic polls
- Silent replies: Agent responds with `SILENT_TOKEN` when it has nothing to say
- Tool call/thinking blocks: Internal processing artifacts without user-facing text

OpenClaw addresses this by detecting "real conversation" before compaction. If no real conversation exists, compaction is skipped entirely, saving LLM API calls.

## Goals / Non-Goals

**Goals:**
- Detect whether a message contains meaningful conversation content
- Skip compaction when the entire history contains no real conversation
- Match OpenClaw's behavior for consistency

**Non-Goals:**
- History turn limiting (not needed for this workspace)
- Tool result special lookback handling (current behavior is sufficient)
- Context injection mode configuration (not applicable without subagent support)

## Decisions

### 1. Message Content Detection Strategy

**Decision:** Implement `has_meaningful_conversation_content()` that checks:
- For string content: non-empty after trimming, not `SILENT_TOKEN`, not heartbeat-only
- For list content: at least one text block with meaningful content, or a non-tool-call/thinking block

**Rationale:** OpenClaw's approach distinguishes between:
- Empty/whitespace-only content → not meaningful
- `SILENT_TOKEN` → not meaningful (explicit silence)
- Heartbeat token stripped content → check if remaining text is non-empty
- Tool call/thinking blocks → not meaningful by themselves
- Other block types (image, etc.) → meaningful

**Alternative considered:** Simply check if content is non-empty. Rejected because heartbeat replies and silent tokens would be incorrectly treated as real conversation.

### 2. Role-based Detection

**Decision:** Implement `is_real_conversation_message()` that:
- For `user` and `assistant` roles: check if message has meaningful content
- For `toolResult` role: always return `False` (not a conversation message)
- For other roles: return `False`

**Rationale:** OpenClaw treats toolResult specially with a lookback mechanism. However, in normal conversation flow, if there's a toolResult, there's always an associated user message that triggered it. Our simpler approach is sufficient for the common case.

**Alternative considered:** Implement the 20-message lookback for toolResult. Rejected as unnecessary complexity for the expected use case.

### 3. Integration Point

**Decision:** Add the check at the beginning of `compact_history()`, before any token estimation or summarization.

**Rationale:** Early exit saves computation. If no real conversation exists, we can skip the entire compaction process including token counting and LLM calls.

## Risks / Trade-offs

**Risk:** False negatives - messages with meaningful content incorrectly classified as non-meaningful.
→ **Mitigation:** Conservative detection - only exclude clearly non-meaningful patterns (SILENT_TOKEN, heartbeat-only, empty). When in doubt, treat as meaningful.

**Risk:** False positives - non-meaningful messages incorrectly classified as meaningful.
→ **Mitigation:** Acceptable trade-off - compaction will still work, just with slightly more content than optimal.

**Trade-off:** Simpler toolResult handling vs. OpenClaw's lookback approach.
→ **Rationale:** The lookback is primarily for edge cases (orphaned toolResults). In normal operation, user messages exist and will trigger real conversation detection.
