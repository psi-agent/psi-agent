## 1. CLAUDE.md Compliance Review

- [x] 1.1 Review `src/psi_agent/session/runner.py` for CLAUDE.md compliance
- [x] 1.2 Review `src/psi_agent/session/server.py` for CLAUDE.md compliance
- [x] 1.3 Review `src/psi_agent/channel/repl/repl.py` for CLAUDE.md compliance
- [x] 1.4 Review `src/psi_agent/channel/repl/client.py` for CLAUDE.md compliance
- [x] 1.5 Review `src/psi_agent/channel/repl/config.py` for CLAUDE.md compliance
- [x] 1.6 Review `src/psi_agent/channel/repl/cli.py` for CLAUDE.md compliance
- [x] 1.7 Review `src/psi_agent/channel/cli/cli.py` for CLAUDE.md compliance

## 2. Test Coverage Improvements

- [x] 2.1 Add tests for `runner.py` uncovered lines (streaming with tool calls, error handling)
- [x] 2.2 Add tests for `client.py` uncovered lines (streaming callback, error cases)
- [x] 2.3 Add tests for `repl.py` uncovered lines (non-streaming mode)
- [x] 2.4 Add tests for `cli.py` uncovered lines (non-streaming mode)
- [x] 2.5 Add tests for `repl/cli.py` uncovered lines

## 3. Quality Checks

- [x] 3.1 Run full test suite to verify all tests pass
- [x] 3.2 Verify patch coverage is >90%
- [x] 3.3 Run `ruff check` and `ruff format`
- [x] 3.4 Run `ty check`
