## 1. Core Implementation

- [x] 1.1 Create `src/psi_agent/__main__.py` with dynamic subcommand discovery
- [x] 1.2 Add `psi-agent` script entry to `pyproject.toml`

## 2. Documentation

- [x] 2.1 Add brief unified CLI mention to `README.md`
- [x] 2.2 Add brief unified CLI mention to `README_CN.md`

## 3. Verification

- [x] 3.1 Verify `uv run psi-agent --help` displays available subcommands
- [x] 3.2 Verify `uv run psi-agent ai openai-completions --help` matches `psi-ai-openai-completions --help`
- [x] 3.3 Run lint, format, and type checks
