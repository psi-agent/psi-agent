## Context

The Telegram channel uses `python-telegram-bot` library which relies on `httpx` for HTTP requests. When a proxy is configured via `builder.proxy()`, httpx uses the proxy for all outgoing requests. However, SOCKS5 proxy support requires an additional dependency `socksio` which is not installed by default.

Current behavior:
1. HTTP/HTTPS proxies work correctly
2. SOCKS5 proxies fail at runtime with `ImportError` from httpx
3. No validation occurs at startup to catch configuration errors early

## Goals / Non-Goals

**Goals:**
- Provide clear error messages when proxy configuration fails
- Validate proxy dependencies at startup
- Document proxy requirements and limitations

**Non-Goals:**
- Change the proxy configuration API (keep using `--proxy` argument)
- Add support for proxy auto-detection
- Add proxy connection testing at startup (would add latency)

## Decisions

### Decision 1: Add optional dependency for SOCKS5 support

**Rationale:** Users who need SOCKS5 proxy can install the extra dependency. This keeps the base installation smaller for users who don't need SOCKS5.

**Implementation:**
- Add `[socks]` optional dependency group in `pyproject.toml` that includes `socksio`
- Users can install with `pip install psi-agent[socks]` or `uv sync --extra socks`

**Alternative considered:** Include `socksio` in base dependencies
- Rejected: Adds unnecessary dependency for most users

### Decision 2: Add startup validation with try-except

**Rationale:** Catch configuration errors early with clear error messages instead of failing at runtime with confusing import errors.

**Implementation:**
- In `TelegramBot.start()`, wrap the Application build in try-except
- Catch `ImportError` and `RuntimeError` from httpx/telegram
- Provide clear error message indicating missing dependency

**Alternative considered:** Pre-check for socksio import
- Rejected: Less reliable, doesn't catch all error cases

### Decision 3: Update CLI documentation

**Rationale:** Users need to know about the SOCKS5 dependency requirement.

**Implementation:**
- Update `Telegram` dataclass docstring to mention SOCKS5 requires extra dependency
- Add note in help text

## Risks / Trade-offs

- **Risk:** Users may not read documentation and still encounter errors
  - Mitigation: Clear error message at startup explains exactly what to install

- **Risk:** socksio version incompatibility with httpx
  - Mitigation: Use latest stable versions, test compatibility in CI
