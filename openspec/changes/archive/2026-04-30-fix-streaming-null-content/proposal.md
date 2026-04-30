## Why

When streaming LLM responses that contain tool calls but no text content, the session runner crashes with `TypeError: 'NoneType' object is not subscriptable`. This occurs because the code attempts to slice `delta['content']` without checking if it's `None` first. The LLM (tencent/hy3-preview via OpenRouter) returns `content: null` in the delta when making tool calls, which is valid OpenAI API behavior.

## What Changes

- Fix null-safety check in `_stream_conversation` method in `runner.py`
- Add guard to check if `delta['content']` is not `None` before slicing for debug logging
- Ensure streaming continues correctly when tool calls are present without text content

## Capabilities

### New Capabilities

None - this is a bug fix, not a new capability.

### Modified Capabilities

None - this is an implementation fix that doesn't change spec-level behavior. The streaming response handling should already support tool calls; this fix ensures it doesn't crash when content is null.

## Impact

- **Affected Code**: `src/psi_agent/session/runner.py` - line 559 in `_stream_conversation` method
- **Affected Components**: psi-session
- **User Impact**: Streaming responses with tool calls will no longer crash the session
