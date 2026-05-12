## Decision 1: Patch ReplClient context manager methods

**Context**: `Repl.run()` enters `async with self.client` context, which calls `ReplClient.__aenter__` → creates a real `aiohttp.ClientSession`. Tests only patched `send_message` but not the context manager, so sessions were created but never closed.

**Options**:
1. Patch `ReplClient.__aenter__`/`__aexit__` to prevent real session creation
2. Patch `aiohttp.ClientSession` globally
3. Add `filterwarnings` to suppress the unclosed session warnings

**Chosen**: Option 1 — patching `ReplClient.__aenter__`/`__aexit__` with `AsyncMock` prevents the real `aiohttp.ClientSession` from being created. This is the most targeted fix: it prevents the resource leak at the source rather than masking it. Option 2 is too broad (affects all aiohttp usage). Option 3 hides the symptom rather than fixing the cause.

## Decision 2: Make tyro.cli mock return a no-op callable

**Context**: `main()` calls `tyro.cli(SomeClass)()`. When `tyro.cli` is mocked, the mock's return value is called, which triggers `SomeClass.__call__()` → `asyncio.run(self._run(...))`. Since `asyncio.run` is also mocked, the `_run` coroutine is created but never awaited.

**Options**:
1. Make `tyro.cli` mock return `MagicMock(return_value=None)` — calling it returns None, no coroutine created
2. Add `filterwarnings` to suppress the unawaited coroutine warnings
3. Restructure `main()` to separate arg parsing from execution

**Chosen**: Option 1 — `mock_cli.return_value = MagicMock(return_value=None)` means `tyro.cli(SomeClass)()` returns `MagicMock(return_value=None)`, which when called returns `None`. No `__call__` is invoked, no coroutine is created, no warning can occur. This fixes the root cause (preventing the coroutine from being created) rather than masking the symptom with `filterwarnings`.

## Decision 3: Close unawaited coroutines in mocked asyncio.run

**Context**: In `__call__` tests, `asyncio.run` is mocked. When `cli()` is called, it creates `asyncio.run(self._run(...))`. The mock receives the coroutine as an argument but doesn't await it, causing "coroutine was never awaited" warnings.

**Options**:
1. Add `mock_run.side_effect = _run_coroutine_silently` which calls `coro.close()` to properly discard the coroutine
2. Add `filterwarnings` to suppress the warnings

**Chosen**: Option 1 — calling `coro.close()` properly discards the coroutine, preventing the warning at the source. This is the correct way to handle a coroutine you don't intend to await. `filterwarnings` would hide the symptom.