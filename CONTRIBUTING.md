# Contributing

Thank you for your interest in contributing!

Issues and pull requests are welcome.

**Note: All PR code must be written by a coding agent (not manually by humans).**

You may use any coding agent of your choice. If you use Claude Code, it will automatically read and follow the coding standards in `CLAUDE.md`. If you use an alternative coding agent, please ensure:

1. OpenSpec is installed (for change management workflow)
2. The agent is configured to read and understand `CLAUDE.md` content

Human-written PR code will not be accepted.

## Parallel Development with Git Worktrees

You can run multiple coding agent sessions in parallel by using git worktrees. This allows working on different branches simultaneously without conflicts.

```bash
# Create a worktree for a new branch
git worktree add worktree/<branch-name> -b <branch-name>

# Or add an existing branch
git worktree add worktree/<branch-name> <existing-branch>

# Clean up stale worktrees
git worktree prune
```

Each worktree in `worktree/` is a separate working directory where you can run a coding agent independently.

---

# 贡献指南

欢迎提交 issue 和 pull request。

**注意：所有 PR 的代码必须由 coding agent 编写（而非人工编写）。**

您可以使用任意 coding agent。如果您使用 Claude Code，它会自动读取并遵循 `CLAUDE.md` 中的编码规范。如果您使用其他 coding agent，请确保：

1. 已安装 OpenSpec（用于变更管理工作流）
2. 该 agent 已配置为读取并理解 `CLAUDE.md` 的内容

人工编写的 PR 代码将不会被接受。

## 使用 Git Worktree 进行并行开发

你可以通过 git worktree 同时运行多个 coding agent 会话。这允许在不同的分支上并行工作而不会产生冲突。

```bash
# 为新分支创建 worktree
git worktree add worktree/<branch-name> -b <branch-name>

# 或添加现有分支
git worktree add worktree/<branch-name> <existing-branch>

# 清理过期的 worktree
git worktree prune
```

`worktree/` 中的每个 worktree 都是独立的工作目录，可以单独运行 coding agent。
