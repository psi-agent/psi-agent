## Context

The OpenAI completions AI component (`psi-ai-openai-completions`) forwards chat completion requests to OpenAI-compatible APIs using the official `openai` Python SDK. When reasoning parameters (`thinking`, `reasoning_effort`) are configured via CLI flags, the server injects them into the request body before forwarding to the upstream API.

The issue: The official OpenAI SDK's `chat.completions.create()` method validates parameters and raises `TypeError` for unknown parameters like `thinking`. These parameters are provider-specific extensions (e.g., Anthropic models via OpenRouter) that the SDK doesn't recognize.

Current flow:
1. Server receives request from session
2. Server injects `thinking` and `reasoning_effort` into request body
3. Client passes entire body to `client.chat.completions.create(**body)`
4. SDK raises `TypeError: got an unexpected keyword argument 'thinking'`

## Goals / Non-Goals

**Goals:**
- Enable provider-specific parameters to be passed through without crashing the SDK
- Maintain backward compatibility with existing behavior
- Keep the solution minimal and focused

**Non-Goals:**
- Validating which providers support which parameters
- Adding new reasoning parameters beyond `thinking` and `reasoning_effort`
- Changing the CLI interface or configuration structure

## Decisions

### Decision: Use OpenAI SDK's `extra_body` parameter

The OpenAI SDK supports an `extra_body` parameter in `chat.completions.create()` for passing non-standard parameters directly to the HTTP request body. This is the intended mechanism for provider extensions.

**Rationale:**
- Officially supported by the SDK
- Cleanly separates standard vs. non-standard parameters
- No risk of future SDK version conflicts
- Parameters in `extra_body` are passed directly to the HTTP request without SDK validation

**Alternatives considered:**
1. **Filter parameters at server level**: Would lose the parameters entirely - they need to reach the upstream API
2. **Use `default_headers` or custom client**: Overkill for this simple parameter forwarding case
3. **Bypass SDK and use raw HTTP**: Would lose SDK benefits (retries, error handling, typing)

### Decision: Define known SDK parameters explicitly

Create a set of known OpenAI SDK parameters and filter the request body into two parts:
- `sdk_params`: Known parameters passed directly to `create()`
- `extra_params`: Unknown parameters passed via `extra_body`

**Known parameters (core):**
- `model`, `messages`, `temperature`, `top_p`, `n`, `stream`, `stop`
- `max_tokens`, `presence_penalty`, `frequency_penalty`, `logit_bias`
- `user`, `response_format`, `tools`, `tool_choice`, `seed`

**Known parameters (extensions we want to support via SDK):**
- None currently - `thinking` and `reasoning_effort` are provider-specific

## Risks / Trade-offs

**Risk: SDK parameter list may change** → Mitigation: Use conservative list of core parameters; new SDK parameters will be filtered into `extra_body` (harmless) until we update the known list.

**Risk: Provider-specific parameters may conflict** → Mitigation: Parameters are passed as-is; provider returns error if unsupported (expected behavior).

**Trade-off: Slight complexity increase** → The filtering logic is simple and isolated to one method.
