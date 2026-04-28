## 1. Helper Functions for Tool Call Parsing

- [x] 1.1 Add `extract_tool_calls_from_assistant()` function to parse tool_use blocks from assistant messages
- [x] 1.2 Add `extract_tool_result_id()` function to extract tool_call_id from tool_result messages

## 2. Tool Use/Result Pairing Repair

- [x] 2.1 Add `repair_tool_use_result_pairing()` function with single-pass algorithm
- [x] 2.2 Handle orphaned tool results (no matching tool_use)
- [x] 2.3 Handle duplicate tool results (same tool_call_id)
- [x] 2.4 Return repair report with dropped counts

## 3. Identifier Preservation in Summarization

- [x] 3.1 Add identifier preservation instructions to `_HISTORY_SUMMARY_PROMPT`
- [x] 3.2 Add identifier preservation instructions to `_UPDATE_SUMMARIZATION_PROMPT`
- [x] 3.3 Add identifier preservation instructions to `_TURN_PREFIX_SUMMARY_PROMPT`

## 4. Integration with compact_history

- [x] 4.1 Call `repair_tool_use_result_pairing()` at the end of `compact_history()`
- [x] 4.2 Add logging for dropped tool results

## 5. Testing

- [x] 5.1 Add unit tests for `extract_tool_calls_from_assistant()`
- [x] 5.2 Add unit tests for `extract_tool_result_id()`
- [x] 5.3 Add unit tests for `repair_tool_use_result_pairing()` with various scenarios
- [x] 5.4 Add integration tests for `compact_history()` with repair

## 6. Simple Workspace Update

- [x] 6.1 Add basic repair function to `examples/a-simple-bash-only-workspace/systems/system.py` for consistency
