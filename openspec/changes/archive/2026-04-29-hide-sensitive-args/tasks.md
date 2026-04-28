## 1. Setup

- [x] 1.1 Add `setproctitle` dependency to pyproject.toml
- [x] 1.2 Create `psi_agent/utils/` directory structure
- [x] 1.3 Create `psi_agent/utils/__init__.py`
- [x] 1.4 Create `psi_agent/utils/proctitle.py` with `mask_sensitive_args()` function

## 2. Core Implementation

- [x] 2.1 Implement `mask_sensitive_args()` function with graceful fallback
- [x] 2.2 Add unit tests for `mask_sensitive_args()` in `tests/utils/test_proctitle.py`

## 3. CLI Integration

- [x] 3.1 Update `psi-ai-openai-completions` CLI to mask `--api-key`
- [x] 3.2 Update `psi-ai-anthropic-messages` CLI to mask `--api-key`
- [x] 3.3 Update `psi-channel-telegram` CLI to mask `--token`

## 4. Documentation

- [x] 4.1 Add security principle to CLAUDE.md for sensitive argument masking

## 5. Verification

- [x] 5.1 Run `ruff check` and `ruff format`
- [x] 5.2 Run `ty check` for type checking
- [x] 5.3 Run `pytest` to verify all tests pass
- [x] 5.4 Manual test: verify process title masking with `ps aux`
