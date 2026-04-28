## Context

psi-session sends requests with `"model": "session"` as a placeholder value. The psi-ai-openai-completions component forwards the entire request body to the upstream provider (OpenRouter), including this placeholder model value. OpenRouter rejects "session" as an invalid model ID.

The actual model is configured when starting psi-ai-openai-completions via the `--model` flag.

## Goals / Non-Goals

**Goals:**
- Fix the model ID error by using the configured model in psi-ai
- Allow session to use any placeholder model value

**Non-Goals:**
- Change the session-to-psi-ai protocol
- Support dynamic model selection per request

## Decisions

### Override model field in psi-ai-openai-completions

**方案：** In `_handle_chat_completions`, replace the incoming `model` field with the configured model before forwarding to the upstream provider.

**原因：**
- The model is a deployment concern (which LLM to use), not a per-request concern
- psi-ai is the right place to determine the actual model - it's configured with the model at startup
- Simple fix with no protocol changes

## Risks / Trade-offs

- None - this is the correct behavior. The model should be determined by psi-ai's configuration, not by the session.
