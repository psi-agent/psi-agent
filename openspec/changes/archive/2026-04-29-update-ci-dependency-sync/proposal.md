## Why

CI 配置中使用 `uv sync --all-extras` 已不再需要，因为：
1. 项目已迁移到 `[dependency-groups]` (PEP 735)，`uv sync` 默认安装 `dev` 组
2. `--all-extras` 是用于 `[project.optional-dependencies]` 的，现已移除

同时，调整 ruff 检查顺序，format check 在 lint check 之前更直观（先格式化再检查）。

## What Changes

- 将 `uv sync --all-extras` 改为 `uv sync`
- 将 "Ruff format check" 步骤移到 "Ruff lint" 步骤之前

## Capabilities

### New Capabilities

无新能力引入。

### Modified Capabilities

无现有能力的需求变更。

## Impact

- **.github/workflows/ci.yml**：更新依赖安装命令和步骤顺序
- **CI 行为**：无功能变化，仅优化配置
