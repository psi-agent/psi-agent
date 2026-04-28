## Why

The Anthropic Messages API requires `max_tokens` as a mandatory parameter, but the current implementation does not provide a default value when translating OpenAI-format requests to Anthropic format. Additionally, the session layer passes `model: "session"` as a placeholder, but the client only replaces the model when it's **absent**, not when it's the placeholder value. This causes all requests to fail with the error: "Missing required arguments; Expected either ('max_tokens', 'messages' and 'model') or ('max_tokens', 'messages', 'model' and 'stream') arguments to be given."

## What Changes

- Add `max_tokens` as a CLI parameter with default value 4096 in `cli.py` and `config.py`
- Pass `max_tokens` through config to the translator, which will use it as default when not provided by the caller
- Fix model replacement logic in client to replace `"session"` placeholder with the configured model name
- This ensures compatibility with the Anthropic Messages API without requiring changes to the session layer

## Capabilities

### New Capabilities

- `anthropic-request-defaults`: Ensures Anthropic Messages API requests always include the required `max_tokens` parameter (configurable via CLI with sensible default), and properly replaces the session model placeholder with the configured model name

### Modified Capabilities

- None

## Impact

- **Affected Code**: 
  - `src/psi_agent/ai/anthropic_messages/cli.py` - add `max_tokens` parameter with default
  - `src/psi_agent/ai/anthropic_messages/config.py` - add `max_tokens` field
  - `src/psi_agent/ai/anthropic_messages/translator.py` - use config's `max_tokens` as default
  - `src/psi_agent/ai/anthropic_messages/client.py` - fix model placeholder replacement
- **APIs**: CLI gains optional `--max-tokens` argument (default: 4096)
- **Dependencies**: None
- **Systems**: psi-ai-anthropic-messages component
