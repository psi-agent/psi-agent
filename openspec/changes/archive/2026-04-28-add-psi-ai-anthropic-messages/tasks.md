## 1. Setup

- [x] 1.1 Add `anthropic` dependency to pyproject.toml
- [x] 1.2 Create `src/psi_agent/ai/anthropic_messages/` module directory
- [x] 1.3 Create `config.py` with `AnthropicMessagesConfig` dataclass

## 2. Client Implementation

- [x] 2.1 Create `client.py` with `AnthropicMessagesClient` class
- [x] 2.2 Implement async context manager protocol (`__aenter__`, `__aexit__`)
- [x] 2.3 Implement `messages()` method for non-streaming requests
- [x] 2.4 Implement streaming support with async generator
- [x] 2.5 Add error handling for authentication, connection, and timeout errors

## 3. Server Implementation

- [x] 3.1 Create `server.py` with `AnthropicMessagesServer` class
- [x] 3.2 Implement Unix socket server setup with aiohttp
- [x] 3.3 Implement POST `/v1/messages` endpoint handler
- [x] 3.4 Implement streaming response handling (SSE)
- [x] 3.5 Implement error response mapping (401, 429, 500)
- [x] 3.6 Implement `start()` and `stop()` lifecycle methods

## 4. CLI and Package

- [x] 4.1 Create `cli.py` with tyro CLI entry point
- [x] 4.2 Create `__init__.py` with public exports
- [x] 4.3 Add `psi-ai-anthropic-messages` script entry to pyproject.toml

## 5. Testing

- [x] 5.1 Write unit tests for `AnthropicMessagesConfig`
- [x] 5.2 Write unit tests for `AnthropicMessagesClient` (mocked API)
- [x] 5.3 Write unit tests for `AnthropicMessagesServer` (mocked client)
- [x] 5.4 Run full test suite and verify all tests pass

## 6. Quality Checks

- [x] 6.1 Run `ruff check` and fix all lint errors
- [x] 6.2 Run `ruff format` and ensure code is formatted
- [x] 6.3 Run `ty check` and fix all type errors
