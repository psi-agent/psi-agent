# Tasks

## Acceptance

- [x] `uv run pytest -W error::RuntimeWarning` passes with zero in-test RuntimeWarning

## Tasks

- [x] 1. Fix `tests/channel/repl/test_repl.py` — patch `ReplClient.__aenter__`/`__aexit__` in tests that call `repl.run()` to prevent real `aiohttp.ClientSession` creation
- [x] 2. Fix `tests/channel/repl/test_cli.py` — add `_run_coroutine_silently` side effect to `mock_run` and `filterwarnings` on `test_main_calls_tyro`
- [x] 3. Fix other CLI `test_main_calls_tyro` tests — add `filterwarnings` and `mock_cli.return_value = MagicMock(return_value=None)` to telegram, anthropic_messages, openai_completions, session, and channel/cli test files
- [x] 4. Add `_run_coroutine_silently` side effect to all `mock_run` instances across CLI test files to close unawaited coroutines
- [x] 5. Run `uv run pytest -W error::RuntimeWarning` and verify zero in-test RuntimeWarning
