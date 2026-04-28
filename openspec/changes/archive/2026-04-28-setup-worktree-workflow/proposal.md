## Why

The project needs a structured workflow for parallel development. Git worktrees allow multiple Claude Code sessions to work on different branches simultaneously without conflicts. Currently, .gitignore lacks organization and there's no guidance for parallel development workflow.

## What Changes

- Add `worktree/` directory for git worktrees (ignored by git)
- Organize .gitignore with clear sections and add worktree/ pattern
- Add CONTRIBUTING.md guidance about worktree-based parallel development (for human contributors)
- Add CLAUDE.md note: use `npx @fission-ai/openspec@latest` when openspec CLI is not available (for Claude Code)

## Capabilities

### New Capabilities

- `project-worktree`: Establishes worktree directory structure and gitignore patterns for parallel development workflow

### Modified Capabilities

- `claude-md`: Add openspec CLI fallback note for Claude Code (minor documentation update)

## Impact

- `.gitignore` - reorganized and extended
- `CONTRIBUTING.md` - added worktree guidance section
- `worktree/` - new directory (ignored, not tracked in git)