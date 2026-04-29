## Why

The current README Quick Start section has several inaccuracies that may confuse users:
1. Step 1 doesn't mention the available example workspaces that users can directly use or reference
2. Step 2 incorrectly states "Start the session with an AI provider" when it only starts the session
3. Step 3 uses "AI component" terminology instead of the more accurate "AI provider"
4. Step 4's "interact with your agent" could be misunderstood; it should clarify interaction is with the agent session

## What Changes

- Add reference to `examples/` directory in Step 1, pointing users to ready-to-use workspace examples
- Correct Step 2 description from "Start the session with an AI provider" to "Start the session"
- Change Step 3 description from "Start an AI component" to "Start an AI provider"
- Clarify Step 4 from "interact with your agent" to "interact with your agent session"
- Apply all changes to both English (README.md) and Chinese (README_zh.md) versions

## Capabilities

### New Capabilities

None - this is a documentation improvement with no new functionality.

### Modified Capabilities

- `user-readme`: Added requirements for Quick Start section clarity and precision

## Impact

- `README.md` - English documentation
- `README_zh.md` - Chinese documentation
