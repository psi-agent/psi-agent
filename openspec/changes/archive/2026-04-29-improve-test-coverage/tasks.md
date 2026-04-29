## 1. High Priority - Pure Functions

- [x] 1.1 Add tests for `translator.py` (anthropic_messages) - translate anthropic to openai
- [x] 1.2 Add tests for `translator.py` (anthropic_messages) - translate openai to anthropic
- [x] 1.3 Add tests for `translator.py` (anthropic_messages) - edge cases (empty content, special characters)
- [x] 1.4 Add tests for `history.py` - compact_history within limit
- [x] 1.5 Add tests for `history.py` - compact_history exceeding limit
- [x] 1.6 Add tests for `tool_loader.py` - load valid tool
- [x] 1.7 Add tests for `tool_loader.py` - handle invalid tool file
- [x] 1.8 Add tests for `tool_loader.py` - reload changed tool

## 2. Medium Priority - Server Request Handling

- [x] 2.1 Add tests for `server.py` (openai_completions) - handle valid non-streaming request
- [x] 2.2 Add tests for `server.py` (openai_completions) - handle invalid JSON body
- [x] 2.3 Add tests for `server.py` (openai_completions) - handle streaming request
- [x] 2.4 Add tests for `server.py` (openai_completions) - handle client not initialized
- [x] 2.5 Add tests for `server.py` (session) - handle valid request
- [x] 2.6 Add tests for `server.py` (session) - handle invalid request

## 3. Medium Priority - Runner Logic

- [x] 3.1 Add tests for `runner.py` - process user message
- [x] 3.2 Add tests for `runner.py` - handle tool call
- [x] 3.3 Add tests for `runner.py` - handle skill invocation
- [x] 3.4 Add tests for `runner.py` - error handling

## 4. Low Priority - CLI Testing

- [x] 4.1 Add tests for `cli.py` (channel) - parse valid arguments
- [x] 4.2 Add tests for `cli.py` (channel) - handle missing argument
- [x] 4.3 Add tests for `cli.py` (session) - parse valid arguments
- [x] 4.4 Add tests for `cli.py` (anthropic_messages) - parse valid arguments

## 5. Verification

- [x] 5.1 Run full test suite and verify all tests pass
- [x] 5.2 Generate coverage report and verify 80%+ coverage
- [ ] 5.3 Report any bugs discovered during testing
