## Why

当前 `pyproject.toml` 同时使用 `[project.optional-dependencies]` 和 `[dependency-groups]` 定义开发依赖，造成配置分散和混淆。`[project.optional-dependencies]` 是 PEP 621 标准用于可选功能依赖，会随包发布；而 `[dependency-groups]` 是 PEP 735 新标准（2024年9月），专门用于纯开发工具依赖，不会发布。开发工具应统一放在 `[dependency-groups]` 中。

## What Changes

- 将 `[project.optional-dependencies]` 中的 `dev` 组内容合并到 `[dependency-groups]` 的 `dev` 组
- 删除 `[project.optional-dependencies]` 整个部分
- 更新 CLAUDE.md 文档中关于开发依赖安装的说明（如有）

## Capabilities

### New Capabilities

无新能力引入。

### Modified Capabilities

无现有能力的需求变更。

## Impact

- **pyproject.toml**：合并依赖配置
- **开发工作流**：开发者使用 `uv sync --group dev` 或 `uv pip install --group dev` 安装开发依赖
- **包发布**：不再包含 `dev` 作为可选依赖（原本就不应该包含）
