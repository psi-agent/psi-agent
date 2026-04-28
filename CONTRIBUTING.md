# Contributing

欢迎提交 issue 和 pull request。

**注意：所有 PR 的代码必须由 Claude Code 编写。**

请使用 Claude Code 完成 PR 的实现工作。Claude Code 会自动读取并遵循 `CLAUDE.md` 中的编码规范。人工编写的 PR 代码将不会被接受。

## 使用 Git Worktree 进行并行开发

你可以通过 git worktree 同时运行多个 Claude Code 会话。这允许在不同的分支上并行工作而不会产生冲突。

```bash
# 为新分支创建 worktree
git worktree add worktree/<branch-name> -b <branch-name>

# 或添加现有分支
git worktree add worktree/<branch-name> <existing-branch>

# 清理过期的 worktree
git worktree prune
```

`worktree/` 中的每个 worktree 都是独立的工作目录，可以单独运行 Claude Code。

---

Thank you for your interest in contributing!

Issues and pull requests are welcome.

**Note: All PR code must be written by Claude Code.**

Please use Claude Code to implement your PR. Claude Code will automatically read and follow the coding standards in `CLAUDE.md`. Human-written PR code will not be accepted.

## Parallel Development with Git Worktrees

You can run multiple Claude Code sessions in parallel by using git worktrees. This allows working on different branches simultaneously without conflicts.

```bash
# Create a worktree for a new branch
git worktree add worktree/<branch-name> -b <branch-name>

# Or add an existing branch
git worktree add worktree/<branch-name> <existing-branch>

# Clean up stale worktrees
git worktree prune
```

Each worktree in `worktree/` is a separate working directory where you can run Claude Code independently.