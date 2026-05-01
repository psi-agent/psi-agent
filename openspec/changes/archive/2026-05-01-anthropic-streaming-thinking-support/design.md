## Context

The psi-agent framework uses a unified OpenAI chat completion protocol for inter-component communication. The `psi-ai-anthropic-messages` component translates between Anthropic's Messages API format and this internal OpenAI format.

Anthropic's extended thinking feature (available in Claude 4.x models) introduces new content block types:
- `thinking`: Contains the model's reasoning process with `thinking` text and `signature` for verification
- `redacted_thinking`: Contains encrypted thinking content that should not be exposed

The current `StreamingTranslator` class only handles `text` and `tool_use` content blocks, causing thinking content to be silently dropped during streaming translation.

### Anthropic Streaming Event Types

| Event Type | Content Block Type | Delta Type | Current Support |
|------------|-------------------|------------|-----------------|
| `content_block_start` | `text` | - | Partial (no output) |
| `content_block_start` | `tool_use` | - | Yes |
| `content_block_start` | `thinking` | - | No |
| `content_block_start` | `redacted_thinking` | - | No |
| `content_block_delta` | - | `text_delta` | Partial (wrong field check) |
| `content_block_delta` | - | `input_json_delta` | Yes |
| `content_block_delta` | - | `thinking_delta` | No |
| `content_block_delta` | - | `signature_delta` | No |

## Goals / Non-Goals

**Goals:**
- Translate `thinking` content blocks to OpenAI streaming format
- Handle `thinking_delta` and `signature_delta` events correctly
- Fix text delta handling to work with both SDK event structure and raw JSON
- Maintain backward compatibility with existing text and tool_use handling

**Non-Goals:**
- Non-streaming thinking translation (handled separately in response translation)
- Exposing `redacted_thinking` content (should be skipped, not translated)
- Changing the OpenAI protocol format (use existing `reasoning_content` field if available)

## Decisions

### Decision 1: Thinking Content Output Format

**Options considered:**
1. Add thinking content to `delta.content` alongside text
2. Use separate `delta.reasoning_content` field (OpenAI o1-style)
3. Skip thinking content entirely

**Choice:** Use `delta.reasoning_content` field.

**Rationale:** OpenAI's o1 models use `reasoning_content` in streaming chunks for reasoning tokens. This provides a clean separation between thinking and final response content, matching the OpenAI convention.

### Decision 2: Thinking Block Index Tracking

**Options considered:**
1. Track thinking blocks separately from tool calls
2. Use unified pending blocks tracking
3. No tracking needed (thinking deltas are self-contained)

**Choice:** No tracking needed for thinking blocks.

**Rationale:** Unlike tool calls which require accumulating `input_json_delta` fragments, `thinking_delta` events contain complete thinking text fragments. The `signature_delta` provides the signature at the end. No state accumulation required.

### Decision 3: Redacted Thinking Handling

**Options considered:**
1. Translate as empty reasoning_content
2. Skip entirely with no output
3. Log warning and skip

**Choice:** Skip entirely with debug log.

**Rationale:** Redacted thinking blocks contain encrypted content that Anthropic intentionally hides. Translating them would expose nothing useful. A debug log helps troubleshooting without noise.

### Decision 4: Text Delta Field Access Pattern

**Options considered:**
1. Use `delta.get("text")` only (current approach)
2. Check `delta.type == "text_delta"` then use `delta.text`
3. Use both patterns with fallback

**Choice:** Check `delta.type` discriminator first, then access appropriate field.

**Rationale:** Anthropic SDK events use typed delta objects with `type` discriminator. The current `delta.get("text")` pattern works for raw JSON but may miss SDK-structured events. Using the type discriminator is more robust and matches the pattern used for `input_json_delta`.

## Risks / Trade-offs

**Risk: OpenAI clients may not expect `reasoning_content` field**
→ Mitigation: The field is optional in OpenAI format. Clients that don't recognize it will ignore it. This matches how OpenAI o1 models work.

**Risk: Thinking signature not useful in OpenAI format**
→ Mitigation: Include signature in a metadata field or skip it. The signature is for Anthropic's internal verification.

**Risk: Breaking existing tests with new delta handling**
→ Mitigation: Add comprehensive tests for all delta types before changing implementation.

## Open Questions

- Should we include the thinking `signature` in the translated output? (Currently: skip, as it has no OpenAI equivalent)
- Should `reasoning_content` be concatenated across multiple thinking deltas? (Yes, same pattern as `content` for text)