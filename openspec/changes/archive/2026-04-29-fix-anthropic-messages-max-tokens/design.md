## Context

The psi-ai-anthropic-messages component translates OpenAI-format requests to Anthropic Messages API format. Two issues cause requests to fail:

1. The Anthropic API requires `max_tokens` as a mandatory parameter, but the current translator only passes it through if provided by the caller. The session layer does not set `max_tokens`.

2. The session layer passes `model: "session"` as a placeholder, but the client's model injection logic only triggers when `model` is **absent**, not when it equals `"session"`.

## Goals / Non-Goals

**Goals:**
- Ensure all Anthropic Messages API requests include the required `max_tokens` parameter
- Make `max_tokens` configurable via CLI with a sensible default
- Properly replace the `"session"` model placeholder with the configured model name
- Maintain backward compatibility with callers that provide their own values

**Non-Goals:**
- Changing the session layer to send `max_tokens` or real model names
- Supporting different default values for different models

## Decisions

**Decision 1: Add `max_tokens` as CLI parameter**

Add `max_tokens` as an optional CLI parameter with default value 4096, stored in config and passed to the translator.

- **Rationale**: Making it a CLI parameter allows users to override the default without code changes. The default 4096 works for most conversational use cases.
- **Alternative considered**: Hardcode default in translator. Rejected because it's less flexible for different use cases.

**Decision 2: Replace model placeholder in client**

Modify the client's model injection logic to replace `"session"` placeholder with the configured model name, in addition to injecting when absent.

- **Rationale**: The session layer uses `"session"` as a provider-agnostic placeholder. The AI provider component should replace it with the actual model.
- **Alternative considered**: Have session send no model. Rejected because it would require changing the session layer.

## Risks / Trade-offs

- **Risk**: 4096 may be too small for some use cases requiring longer responses.
  - **Mitigation**: Users can override via `--max-tokens` CLI argument.

- **Risk**: Some models may have different token limits.
  - **Mitigation**: Users can configure appropriate value via CLI.

- **Risk**: The `"session"` placeholder is a magic string.
  - **Mitigation**: This is already the established convention in the codebase.
