## Purpose

Core session functionality that manages the agent's request-response cycle, tool execution, and communication with AI providers and channels.

## Requirements

### Requirement: Session provides HTTP server on Unix socket

The session SHALL provide an HTTP server listening on a Unix socket path, accepting requests from channel components.

#### Scenario: Server starts on Unix socket
- **WHEN** session is started with a socket path
- **THEN** an HTTP server is listening on that Unix socket

#### Scenario: Server accepts chat completions request
- **WHEN** channel sends POST /v1/chat/completions request
- **THEN** session receives and processes the request

### Requirement: Session acts as HTTP client to psi-ai

The session SHALL act as an HTTP client connecting to psi-ai-* components via Unix socket, forwarding requests using OpenAI chat completion protocol.

#### Scenario: Session forwards request to psi-ai
- **WHEN** session needs to call LLM
- **THEN** session sends HTTP POST request to psi-ai socket path

#### Scenario: Session receives response from psi-ai
- **WHEN** psi-ai returns chat completion response
- **THEN** session receives the response for processing

### Requirement: Session handles streaming responses

The session SHALL support streaming (SSE) responses from psi-ai-* and forward them to channel in OpenAI format.

#### Scenario: Streaming response forwarded to channel
- **WHEN** psi-ai returns streaming response
- **THEN** session forwards SSE chunks to channel in OpenAI format

### Requirement: Session returns OpenAI-format responses to channel

The session SHALL return responses to channel in OpenAI chat completion format, hiding tool calls and thinking content.

#### Scenario: Successful response returned to channel
- **WHEN** session completes processing
- **THEN** channel receives OpenAI-format response without tool call details

#### Scenario: Error response returned to channel
- **WHEN** an error occurs during processing
- **THEN** channel receives OpenAI-format error response

The session SHALL support streaming (SSE) responses from psi-ai-* and forward them to channel.

#### Scenario: Streaming response forwarded to channel
- **WHEN** psi-ai returns streaming response
- **THEN** session forwards SSE chunks to channel

### Requirement: Session calls system prompt builder

The session SHALL call the system prompt builder from workspace systems to generate system prompt. The builder takes no parameters and retrieves workspace content itself. If systems/system.py does not exist, no system prompt is included.

#### Scenario: System prompt generated on each request
- **WHEN** session processes a request and systems/system.py exists
- **THEN** session calls build_system_prompt() and includes result in messages

#### Scenario: No system prompt when systems absent
- **WHEN** workspace does not have systems/system.py
- **THEN** messages do not include a system prompt

### Requirement: Session handles tool calls from LLM

The session SHALL process tool_call responses from psi-ai, execute corresponding tools, and continue the conversation.

#### Scenario: Tool call detected and executed
- **WHEN** psi-ai returns response with tool_calls
- **THEN** session executes the tools and sends results back to psi-ai

#### Scenario: Multiple tool calls executed in parallel
- **WHEN** psi-ai returns multiple tool_calls
- **THEN** session executes all tools concurrently

### Requirement: Session starts schedule executor on startup

The session SHALL start the schedule executor when session starts.

#### Scenario: Schedule executor initialized
- **WHEN** session starts with a workspace path
- **THEN** the schedule executor SHALL be initialized with the workspace schedules

#### Scenario: Schedule executor runs in background
- **WHEN** session is running
- **THEN** all scheduled tasks SHALL run in background async tasks
- **AND** the session SHALL continue to handle HTTP requests

#### Scenario: No schedules directory
- **WHEN** workspace does not have a `schedules/` directory
- **THEN** session SHALL start normally without schedule executor

### Requirement: Schedule.get_next_run returns properly typed datetime

The `Schedule.get_next_run()` method SHALL return a properly typed `datetime` object without using type ignore comments.

#### Scenario: Type checker accepts get_next_run return type
- **WHEN** running `ty check` on `session/schedule.py`
- **THEN** no type errors are reported for the `get_next_run` method

### Requirement: SessionServer streaming handler uses correct request parameter

The `_handle_streaming()` method in `SessionServer` SHALL pass the correct request object to `response.prepare()`.

#### Scenario: Type checker accepts prepare call
- **WHEN** running `ty check` on `session/server.py`
- **THEN** no type errors are reported for the `response.prepare()` call

#### Scenario: Streaming response works correctly
- **WHEN** a streaming request is sent to the session server
- **THEN** the response is properly prepared and streaming works as expected