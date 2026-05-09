## ADDED Requirements

### Requirement: AI client raises RuntimeError when not initialized
OpenAI and Anthropic clients SHALL raise RuntimeError with message "Client not initialized. Use async context manager." when `chat_completions()` or `messages()` is called without entering the async context manager.

#### Scenario: OpenAI client called without context manager
- **WHEN** `OpenAICompletionsClient.chat_completions()` is called without prior `__aenter__`
- **THEN** RuntimeError SHALL be raised with message containing "Client not initialized"

#### Scenario: Anthropic client called without context manager
- **WHEN** `AnthropicMessagesClient.messages()` is called without prior `__aenter__`
- **THEN** RuntimeError SHALL be raised with message containing "Client not initialized"

### Requirement: AI client _handle_error handles APIStatusError
Both OpenAI and Anthropic clients' `_handle_error` method SHALL handle `APIStatusError` by returning a dict with `error` and `status_code` fields, using `e.status_code or 500` as the status code.

#### Scenario: APIStatusError with status_code present
- **WHEN** `_handle_error` receives an `APIStatusError` with `status_code=429`
- **THEN** it SHALL return `{"error": str(e), "status_code": 429}`

#### Scenario: APIStatusError with status_code None
- **WHEN** `_handle_error` receives an `APIStatusError` with `status_code=None`
- **THEN** it SHALL return `{"error": str(e), "status_code": 500}`

### Requirement: AI client _handle_error handles generic Exception
Both clients' `_handle_error` method SHALL handle any `Exception` subclass by returning `{"error": str(e), "status_code": 500}`.

#### Scenario: Generic exception
- **WHEN** `_handle_error` receives a generic `Exception("unexpected")`
- **THEN** it SHALL return `{"error": "unexpected", "status_code": 500}`

### Requirement: Anthropic client _handle_error handles APITimeoutError
Anthropic client's `_handle_error` SHALL handle `APITimeoutError` by returning `{"error": str(e), "status_code": 408}`.

#### Scenario: Anthropic APITimeoutError
- **WHEN** Anthropic `_handle_error` receives an `APITimeoutError`
- **THEN** it SHALL return `{"error": str(e), "status_code": 408}`

### Requirement: OpenAI streaming error paths
OpenAI client's `_stream_request` SHALL handle errors during streaming by yielding an error JSON chunk.

#### Scenario: AuthenticationError during streaming
- **WHEN** `AuthenticationError` occurs while iterating stream chunks
- **THEN** the generator SHALL yield a JSON string containing `{"error": ...}`

#### Scenario: RateLimitError during streaming
- **WHEN** `RateLimitError` occurs while iterating stream chunks
- **THEN** the generator SHALL yield a JSON string containing `{"error": ...}` with `status_code: 429`

#### Scenario: APIConnectionError during streaming
- **WHEN** `APIConnectionError` occurs while iterating stream chunks
- **THEN** the generator SHALL yield a JSON string containing `{"error": ...}` with `status_code: 502`

#### Scenario: APITimeoutError during streaming
- **WHEN** `APITimeoutError` occurs while iterating stream chunks
- **THEN** the generator SHALL yield a JSON string containing `{"error": ...}` with `status_code: 408`

### Requirement: Anthropic streaming mid-stream error paths
Anthropic client's `_stream_request` SHALL handle errors that occur after stream has started (not just during `__aenter__`).

#### Scenario: APITimeoutError mid-stream
- **WHEN** `APITimeoutError` occurs while iterating stream events
- **THEN** the generator SHALL yield an error JSON chunk

#### Scenario: APIStatusError mid-stream
- **WHEN** `APIStatusError` occurs while iterating stream events
- **THEN** the generator SHALL yield an error JSON chunk

#### Scenario: Generic exception mid-stream
- **WHEN** a generic `Exception` occurs while iterating stream events
- **THEN** the generator SHALL yield an error JSON chunk with `status_code: 500`

### Requirement: AI server start/stop lifecycle
OpenAI and Anthropic servers' `start()` and `stop()` methods SHALL handle lifecycle correctly.

#### Scenario: OpenAI server start removes existing socket
- **WHEN** `start()` is called and the socket file already exists
- **THEN** the existing socket file SHALL be removed before creating the new one

#### Scenario: OpenAI server stop with None client
- **WHEN** `stop()` is called and `self.client` is None
- **THEN** no exception SHALL be raised

#### Scenario: Anthropic server stop with None client
- **WHEN** `stop()` is called and `self.client` is None
- **THEN** no exception SHALL be raised

#### Scenario: Anthropic server stop with None runner
- **WHEN** `stop()` is called and `self._runner` is None
- **THEN** no exception SHALL be raised
