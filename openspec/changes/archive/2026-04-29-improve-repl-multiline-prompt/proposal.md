## Why

Currently, when entering multi-line input in the REPL channel, the continuation lines show only spaces for alignment, making it visually unclear that the user is still in multi-line mode. A visible continuation prompt symbol would improve the user experience by clearly indicating multi-line input state.

## What Changes

- Add a continuation prompt symbol (`. `) for multi-line input in the REPL
- Use prompt-toolkit's `prompt_continuation` parameter to display the continuation prompt

## Capabilities

### New Capabilities

(None)

### Modified Capabilities

- `repl-multi-line`: Continuation prompt visibility for multi-line input

## Impact

- `src/psi_agent/channel/repl/repl.py` - REPL implementation
- User experience when entering multi-line input in the REPL
