## 1. Session Runner Tests

- [x] 1.1 Add tests for session runner initialization with valid/invalid workspace
- [x] 1.2 Add tests for message processing loop (user message → AI → response)
- [x] 1.3 Add tests for tool call handling (execute tool, return result)
- [x] 1.4 Add tests for tool execution error handling
- [x] 1.5 Add tests for history management (append, compact)

## 2. Session Server Tests

- [x] 2.1 Add tests for HTTP server startup and shutdown
- [x] 2.2 Add tests for request handling (POST /chat)
- [x] 2.3 Add tests for error responses (invalid request, server error)

## 3. Workspace Snapshot Tests

- [x] 3.1 Add tests for snapshot creation with tag
- [x] 3.2 Add tests for snapshot creation without tag
- [x] 3.3 Add tests for layer parent relationship
- [x] 3.4 Add tests for manifest default update
- [x] 3.5 Add tests for error handling (invalid mount, permissions)

## 4. Workspace Umount Tests

- [x] 4.1 Add tests for unmount valid mount point
- [x] 4.2 Add tests for unmount non-existent mount
- [x] 4.3 Add tests for cleanup operations (work directory)
- [x] 4.4 Add tests for permission handling

## 5. Tool Executor Tests

- [x] 5.1 Add tests for tool execution with valid tool
- [x] 5.2 Add tests for tool execution with invalid tool
- [x] 5.3 Add tests for tool execution timeout
- [x] 5.4 Add tests for tool execution error propagation

## 6. Error Handling Tests

- [x] 6.1 Add tests for async error handling (network, timeout)
- [x] 6.2 Add tests for invalid input handling
- [x] 6.3 Add tests for resource cleanup on error

## 7. Coverage Verification

- [x] 7.1 Run coverage report and verify 80%+ overall coverage
- [x] 7.2 Verify all core modules have 70%+ coverage
- [x] 7.3 Update CI configuration if needed for coverage threshold
