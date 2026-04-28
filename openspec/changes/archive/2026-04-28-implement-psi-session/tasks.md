## 1. Setup and Types

- [x] 1.1 Create `src/psi_agent/session/` directory structure
- [x] 1.2 Implement `types.py` with ToolSchema, ToolRegistry, History types
- [x] 1.3 Implement `config.py` with SessionConfig dataclass

## 2. Tool Loading and Execution

- [x] 2.1 Implement `tool_loader.py` - scan tools directory
- [x] 2.2 Implement tool function parsing (type annotations + docstring)
- [x] 2.3 Implement OpenAI tool schema generation from function definition
- [x] 2.4 Implement tool registry with file hash tracking
- [x] 2.5 Implement tool update detection on each request
- [x] 2.6 Implement `tool_executor.py` - execute tool functions async (tools guarantee return)
- [x] 2.7 Implement tool result formatting for LLM

## 3. History Management

- [x] 3.1 Implement `history.py` - messages array management
- [x] 3.2 Implement JSON persistence (load/save)
- [x] 3.3 compact_history interface available (threshold triggering: future work)

## 4. Session Core

- [x] 4.1 Implement `runner.py` - core run loop
- [x] 4.2 Implement message processing flow
- [x] 4.3 Implement tool call handling loop
- [x] 4.4 Implement system prompt builder invocation (no parameters)
- [x] 4.5 Implement streaming response handling
- [x] 4.6 Implement OpenAI-format response to channel (hide tool calls)

## 5. HTTP Server

- [x] 5.1 Implement `server.py` - HTTP server on Unix socket
- [x] 5.2 Implement `/v1/chat/completions` endpoint
- [x] 5.3 Implement streaming (SSE) response support

## 6. CLI and Integration

- [x] 6.1 Implement `cli.py` with tyro
- [x] 6.2 Add `psi-session` entry point to pyproject.toml
- [x] 6.3 Implement `__init__.py` exports

## 7. Testing

- [x] 7.1 Create `tests/session/` directory
- [x] 7.2 Write tests for tool_loader (scan, parse, schema generation)
- [x] 7.3 Write tests for tool_executor (execution, result formatting)
- [x] 7.4 Write tests for history (memory, persistence, compaction)
- [x] 7.5 Write tests for runner (message flow, tool call loop)
- [x] 7.6 Write tests for server (endpoint, streaming)