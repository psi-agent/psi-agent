## Why

Test suite produces runtime warnings about unawaited coroutines and unclosed aiohttp sessions. These warnings indicate tests that create async resources (coroutines, client sessions) but never properly clean them up, which can mask real resource leak bugs and clutter CI output.

## What Changes

- Fix REPL `test_empty_input_ignored` test: the `Repl.run()` method enters `async with self.client` context, but the test patches `send_message` on the client without also patching `__aenter__`/`__aexit__`. This causes the real `ReplClient.__aenter__` to create an `aiohttp.ClientSession` that is never closed, producing "Unclosed client session" warnings. Patch `ReplClient.__aenter__`/`__aexit__` to prevent real session creation.
- Fix CLI `test_main_calls_tyro` tests across all components: `tyro.cli()` is patched with `MagicMock`, but `main()` calls the return value (`tyro.cli(SomeClass)()`), which triggers `SomeClass.__call__()` creating an `_run` coroutine. Since `asyncio.run` is mocked, the coroutine is never awaited. Fix by making `tyro.cli` mock return a no-op callable (`MagicMock(return_value=None)`), so `__call__` is never invoked and no coroutine is created.
- Fix CLI `__call__` tests: when `asyncio.run` is mocked, coroutines passed to it are never awaited. Add `mock_run.side_effect = _run_coroutine_silently` (which calls `coro.close()`) to properly discard unawaited coroutines.

## Capabilities

### New Capabilities

- `test-async-cleanup`: Proper async resource cleanup patterns in tests - ensuring aiohttp sessions are closed and coroutines are properly discarded when the async runtime is mocked

### Modified Capabilities

- `repl-channel`: No spec-level changes, but test implementation needs async cleanup fixes
- `tyro-cli`: No spec-level changes, but test implementation needs coroutine cleanup fixes

## Impact

- Test files: `tests/channel/repl/test_repl.py`, `tests/channel/repl/test_cli.py`, `tests/channel/telegram/test_cli.py`, `tests/channel/cli/test_cli_integration.py`, `tests/session/test_cli.py`, `tests/ai/openai_completions/test_cli.py`, `tests/ai/anthropic_messages/test_cli.py`
- No production code changes required - all fixes are in test code
- No API or dependency changes