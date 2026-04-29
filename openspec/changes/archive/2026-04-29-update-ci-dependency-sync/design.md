## Context

当前 CI 配置：

```yaml
- name: Install dependencies
  run: uv sync --all-extras

- name: Ruff lint
  run: uv run ruff check

- name: Ruff format check
  run: uv run ruff format --check
```

问题：
- `--all-extras` 用于安装 `[project.optional-dependencies]` 的所有可选依赖，但项目已迁移到 `[dependency-groups]`
- `uv sync` 默认安装 `dependency-groups` 中的 `dev` 组，无需额外参数
- ruff 检查顺序：format check 应在 lint 之前，逻辑更清晰

## Goals / Non-Goals

**Goals:**
- 简化 CI 配置，移除不必要的参数
- 优化检查步骤顺序

**Non-Goals:**
- 不改变 CI 的功能行为
- 不添加新的检查步骤

## Decisions

### 1. 使用 `uv sync` 替代 `uv sync --all-extras`

**理由**：
- 项目已使用 `[dependency-groups]` 定义开发依赖
- `uv sync` 默认安装 `dev` 组（包含 pytest, ruff, ty 等）
- `--all-extras` 是针对 `[project.optional-dependencies]` 的，已不适用

### 2. Format check 在 lint check 之前

**理由**：
- 格式问题通常是代码风格问题，应该先修复
- Lint 检查的是代码质量和潜在错误，更重要
- 先格式化再检查，输出更清晰

## Risks / Trade-offs

无显著风险。CI 行为保持一致。
