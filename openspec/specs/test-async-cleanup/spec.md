## ADDED Requirements

### Requirement: REPL tests SHALL properly clean up aiohttp client sessions
Tests that invoke `Repl.run()` SHALL prevent real `aiohttp.ClientSession` creation by patching `ReplClient.__aenter__` and `ReplClient.__aexit__`, or by ensuring the session is properly closed in teardown.

#### Scenario: REPL test with empty input
- **WHEN** `test_empty_input_ignored` calls `repl.run()` with mocked `_read_input` and `send_message`
- **THEN** no "Unclosed client session" warning SHALL be emitted

#### Scenario: REPL test with EOF exit
- **WHEN** `test_eof_exits_repl` calls `repl.run()` with mocked `_read_input`
- **THEN** no "Unclosed client session" warning SHALL be emitted

#### Scenario: REPL test with keyboard interrupt
- **WHEN** `test_keyboard_interrupt_exits_repl` calls `repl.run()` with mocked `_read_input`
- **THEN** no "Unclosed client session" warning SHALL be emitted

### Requirement: CLI main tests SHALL not create unawaited coroutines
Tests that patch `tyro.cli` to verify `main()` calls SHALL make the mock return a no-op callable (`MagicMock(return_value=None)`) so that calling the return value does not trigger the CLI dataclass `__call__` method, preventing coroutine creation entirely.

#### Scenario: Telegram main calls tyro
- **WHEN** `test_main_calls_tyro` calls `main()` with `tyro.cli` patched and `mock_cli.return_value = MagicMock(return_value=None)`
- **THEN** no "coroutine was never awaited" warning SHALL be emitted

#### Scenario: Session main calls tyro
- **WHEN** `test_main_calls_tyro` calls `main()` with `tyro.cli` patched and `mock_cli.return_value = MagicMock(return_value=None)`
- **THEN** no "coroutine was never awaited" warning SHALL be emitted

#### Scenario: OpenAI completions main calls tyro
- **WHEN** `test_main_calls_tyro` calls `main()` with `tyro.cli` patched and `mock_cli.return_value = MagicMock(return_value=None)`
- **THEN** no "coroutine was never awaited" warning SHALL be emitted

#### Scenario: Anthropic messages main calls tyro
- **WHEN** `test_main_calls_tyro` calls `main()` with `tyro.cli` patched and `mock_cli.return_value = MagicMock(return_value=None)`
- **THEN** no "coroutine was never awaited" warning SHALL be emitted

### Requirement: Mocked asyncio.run SHALL properly discard coroutines
Tests that mock `asyncio.run` SHALL use a side effect that calls `coro.close()` on the received coroutine, properly discarding it rather than leaving it unawaited.

#### Scenario: CLI __call__ test with mocked asyncio.run
- **WHEN** a test calls `cli()` with `asyncio.run` mocked and `mock_run.side_effect = _run_coroutine_silently`
- **THEN** no "coroutine was never awaited" warning SHALL be emitted