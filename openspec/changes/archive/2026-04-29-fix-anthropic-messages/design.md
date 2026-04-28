## Context

The `psi-ai-anthropic-messages` component serves as a protocol adapter in the psi-agent architecture. It receives requests from `psi-session` (which uses OpenAI chat completions format) and forwards them to Anthropic-compatible APIs.

**Current State:**
- Server listens on `/v1/messages` (Anthropic endpoint)
- Client forwards requests directly to Anthropic API without translation
- `psi-session` sends requests to `/v1/chat/completions` (OpenAI endpoint)
- Result: Requests fail with 404 because endpoint mismatch

**Architecture Constraints:**
- Session uses OpenAI chat completions format as the standard protocol
- All `psi-ai-*` components must accept OpenAI format on `/v1/chat/completions`
- Each AI provider adapter handles its own format translation

## Goals / Non-Goals

**Goals:**
- Accept OpenAI chat completions format on `/v1/chat/completions`
- Translate OpenAI format to Anthropic Messages format for upstream API
- Translate Anthropic responses back to OpenAI format for session
- Support both streaming and non-streaming modes
- Handle OpenAI-specific parameters (e.g., `max_tokens` mapping)

**Non-Goals:**
- Supporting all OpenAI features (only what psi-session uses)
- Supporting legacy Anthropic `/v1/messages` endpoint on this component
- Handling multi-modal content beyond text (images, etc.) in this iteration

## Decisions

### Decision 1: Endpoint Change

**Choice:** Change from `/v1/messages` to `/v1/chat/completions`

**Rationale:**
- Consistency with other `psi-ai-*` components
- `psi-session` expects OpenAI-compatible endpoint
- Simpler than supporting both endpoints

**Alternatives Considered:**
- Support both endpoints: Adds complexity, no clear use case
- Keep `/v1/messages`: Would require changing session, breaks consistency

### Decision 2: Translation Layer Location

**Choice:** Add translation in both server (request) and client (response)

**Rationale:**
- Server translates incoming OpenAI request to Anthropic format
- Client translates outgoing Anthropic response to OpenAI format
- Clean separation of concerns

**Format Mappings:**

| OpenAI | Anthropic |
|--------|-----------|
| `messages[].role` | `messages[].role` (system → system with special handling) |
| `messages[].content` (string) | `messages[].content` (array of text blocks) |
| `max_tokens` | `max_tokens` (same) |
| `temperature` | `temperature` (same) |
| `stream` | `stream` (same) |
| `tools` | `tools` (format conversion needed) |
| Response `choices[0].message` | Response `content[0].text` |
| Streaming `data: {...}` chunks | Streaming SSE events |

### Decision 3: System Message Handling

**Choice:** Extract first system message and pass as `system` parameter

**Rationale:**
- Anthropic uses separate `system` parameter, not a message
- OpenAI includes system as first message with `role: "system"`
- Extract and convert during request translation

### Decision 4: Streaming Format Conversion

**Choice:** Convert Anthropic SSE events to OpenAI chunk format

**Rationale:**
- Anthropic sends typed events (`message_start`, `content_block_delta`, etc.)
- OpenAI expects `data: {"choices":[{"delta":{"content":"..."}}]}` chunks
- Must parse Anthropic events and emit OpenAI-compatible chunks

## Risks / Trade-offs

**Risk:** Incomplete format coverage → Mitigation: Start with text-only, extend as needed

**Risk:** Streaming conversion complexity → Mitigation: Use state machine for event parsing

**Risk:** Tool calling format differences → Mitigation: Defer to future iteration, document limitation

**Trade-off:** Simplicity over completeness - only support what psi-session currently uses
