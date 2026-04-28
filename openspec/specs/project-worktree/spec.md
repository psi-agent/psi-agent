## ADDED Requirements

### Requirement: Worktree directory structure
The project SHALL provide a `worktree/` directory for git worktrees, ignored by git.

#### Scenario: Parallel development
- **WHEN** user wants to run multiple Claude Code sessions on different branches
- **THEN** user SHALL create worktrees in `worktree/` directory using `git worktree add`

### Requirement: Organized gitignore patterns
`.gitignore` SHALL be organized with clear section headers grouping related patterns.

#### Scenario: Pattern organization
- **WHEN** developer reads .gitignore
- **THEN** patterns SHALL be grouped by category (Python, IDE, Testing, Project, Worktree)

### Requirement: Worktree workflow documentation
CONTRIBUTING.md SHALL document the worktree workflow for parallel Claude Code sessions.

#### Scenario: Parallel session guidance
- **WHEN** developer wants to work on multiple tasks simultaneously
- **THEN** CONTRIBUTING.md SHALL explain how to use `worktree/` directory with git worktrees

### Requirement: Openspec CLI fallback documentation
CONTRIBUTING.md SHALL document the fallback command when openspec CLI is not installed.

#### Scenario: Openspec not found
- **WHEN** openspec command is not available on the system
- **THEN** CONTRIBUTING.md SHALL instruct users to use `npx @fission-ai/openspec@latest` as fallback