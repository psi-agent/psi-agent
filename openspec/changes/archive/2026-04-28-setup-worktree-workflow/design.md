## Context

The project uses git for version control and Claude Code for implementation. Currently, only one Claude Code session can work on the repo at a time, as working directly in the main directory creates conflicts when switching branches mid-task.

Git worktrees solve this by creating separate working directories for different branches, allowing parallel work without interference.

## Goals / Non-Goals

**Goals:**
- Enable parallel Claude Code sessions on different branches
- Organize .gitignore with clear sections
- Document worktree workflow in CONTRIBUTING.md

**Non-Goals:**
- Automate worktree creation (manual `git worktree add` is sufficient)
- Create actual worktrees (only set up the directory structure)

## Decisions

### Directory name: `worktree/`
- Alternatives: `.worktrees/`, `wt/`, `trees/`
- Rationale: Clear, short, easy to remember. Not hidden (users should see it)

### .gitignore organization
- Group patterns by category (Python, IDE, Testing, Project, Worktree)
- Rationale: Makes it easier to maintain and understand

### CONTRIBUTING placement
- Add as new section after existing content
- Rationale: Clear separation, doesn't disrupt existing guidance

## Risks / Trade-offs

- Users may forget to clean up old worktrees → Add guidance to prune stale worktrees
- worktree/ directory clutter over time → Add `git worktree prune` tip