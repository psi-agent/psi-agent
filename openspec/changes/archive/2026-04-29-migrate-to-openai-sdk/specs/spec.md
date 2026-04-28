## ADDED Requirements

### Requirement: OpenAI SDK client integration

The `OpenAICompletionsClient` SHALL use the official `openai` SDK's `AsyncOpenAI` client for all HTTP communication with OpenAI-compatible APIs.

#### Scenario: Non-streaming request with SDK
- **WHEN** a chat completion request is made without streaming
- **THEN** the SDK's `client.chat.completions.create()` method is called
- **AND** the response is returned as a typed object

#### Scenario: Streaming request with SDK
- **WHEN** a chat completion request is made with streaming enabled
- **THEN** the SDK's streaming API is used with `stream=True`
- **AND** chunks are yielded as SSE-formatted strings

### Requirement: SDK error handling

The client SHALL handle SDK-specific exceptions and convert them to the existing error response format.

#### Scenario: Authentication error
- **WHEN** the API returns a 401 error
- **THEN** an `AuthenticationError` exception is caught
- **AND** `{"error": "Authentication failed", "status_code": 401}` is returned

#### Scenario: Rate limit error
- **WHEN** the API returns a 429 error
- **THEN** a `RateLimitError` exception is caught
- **AND** `{"error": "Rate limit exceeded", "status_code": 429}` is returned

#### Scenario: Connection error
- **WHEN** the API is unreachable
- **THEN** an `APIConnectionError` exception is caught
- **AND** `{"error": "Connection failed", "status_code": 500}` is returned

### Requirement: Backward compatibility

The refactored client SHALL maintain identical external behavior to the current implementation.

#### Scenario: Same method signature
- **WHEN** the client is used
- **THEN** the `chat_completions(request_body, stream)` method signature remains unchanged

#### Scenario: Same response format
- **WHEN** a request completes
- **THEN** the response dict structure matches the current implementation
