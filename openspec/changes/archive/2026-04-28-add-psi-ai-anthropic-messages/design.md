## Context

psi-agent uses a component architecture where `psi-ai-*` components handle LLM provider communication. The existing `psi-ai-openai-completions` component serves as the reference implementation, using:
- HTTP over Unix socket for IPC with psi-session
- aiohttp for async HTTP server/client
- OpenAI chat completion format for request/response

Anthropic's Messages API differs from OpenAI's chat completions:
- System prompt is a top-level `system` parameter, not a message in the array
- Content is an array of blocks (text, image) rather than a string
- Tool use is native with structured `tool_use` and `tool_result` content blocks
- Streaming uses SSE with typed events (`message_start`, `content_block_delta`, etc.)

## Goals / Non-Goals

**Goals:**
- Implement `psi-ai-anthropic-messages` following the same architecture as `psi-ai-openai-completions`
- Support Anthropic Messages API with streaming
- Enable native tool use and multimodal content
- Maintain async-first design with proper error handling

**Non-Goals:**
- Converting between OpenAI and Anthropic formats (psi-session handles format adaptation)
- Supporting legacy Anthropic APIs (only Messages API v1)
- Caching or rate limiting (handled by upstream or future middleware)

## Decisions

### Use Official Anthropic SDK

**Decision**: Use the `anthropic` Python SDK for API communication.

**Rationale**:
- Official SDK handles authentication, retries, and error parsing
- Type hints for all request/response structures
- Built-in streaming support with async iterators
- Simpler than maintaining raw HTTP implementation

**Alternative considered**: Direct aiohttp calls (like `psi-ai-openai-completions`). Rejected because Anthropic's streaming protocol is more complex, and the SDK provides better ergonomics.

### Server Accepts Anthropic Format Directly

**Decision**: The server endpoint accepts Anthropic Messages API format directly at `/v1/messages`.

**Rationale**:
- No format conversion overhead
- psi-session can send Anthropic-native requests
- Simpler implementation with fewer transformation bugs

**Alternative considered**: Accept OpenAI format and convert. Rejected because:
- Conversion loses Anthropic-specific features (content blocks, tool_result)
- psi-session should handle format selection based on provider

### Config Mirrors OpenAI Component

**Decision**: Use same config structure: `session_socket`, `model`, `api_key`, `base_url`.

**Rationale**:
- Consistent CLI interface across psi-ai-* components
- Easy to swap components without changing invocation
- `base_url` enables custom endpoints (Bedrock, Vertex AI)

## Risks / Trade-offs

- **SDK dependency**: Adds `anthropic` package (~10MB). Acceptable for native support.
- **Format mismatch**: psi-session must know to send Anthropic format. Documentation will clarify.
- **Streaming complexity**: Anthropic streaming has more event types. SDK handles parsing, but server must forward correctly.
