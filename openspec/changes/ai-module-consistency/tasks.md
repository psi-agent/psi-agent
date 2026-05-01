## 1. Update openai-completions

- [x] 1.1 Remove model injection logic from `openai_completions/client.py`
- [x] 1.2 Change `openai_completions/server.py` to use conditional injection instead of force override

## 2. Update anthropic-messages

- [x] 2.1 Remove model injection logic from `anthropic_messages/client.py`

## 3. Update tests

- [x] 3.1 Update tests to verify conditional injection behavior
