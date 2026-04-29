## Context

当前 `pyproject.toml` 配置：

```toml
[project.optional-dependencies]
dev = [
    "pytest>=9.0.3",
    "pytest-asyncio>=1.3.0",
    "ruff>=0.15.12",
    "ty>=0.0.33",
]

[dependency-groups]
dev = [
    "pytest-cov>=7.1.0",
]
```

问题：
- 开发依赖分散在两个地方
- `[project.optional-dependencies]` 会随包发布，但开发工具不应作为包的可选功能

## Goals / Non-Goals

**Goals:**
- 统一开发依赖到 `[dependency-groups]`
- 确保开发工具不随包发布

**Non-Goals:**
- 不改变依赖版本
- 不添加新的开发工具

## Decisions

### 1. 使用 `[dependency-groups]` 作为唯一开发依赖配置

**理由**：
- PEP 735 专门为开发依赖设计
- 不会随包发布，符合开发工具的本质用途
- `uv` 原生支持，安装命令：`uv sync --group dev`

**替代方案**：保留 `[project.optional-dependencies]`
- 缺点：开发工具会出现在 PyPI 发布元数据中，用户可能误安装

### 2. 合并策略

将 `[project.optional-dependencies]` 的 `dev` 组内容追加到 `[dependency-groups]` 的 `dev` 组：

```toml
[dependency-groups]
dev = [
    "pytest>=9.0.3",
    "pytest-asyncio>=1.3.0",
    "pytest-cov>=7.1.0",
    "ruff>=0.15.12",
    "ty>=0.0.33",
]
```

**排序规则**：按字母顺序排列，便于维护

## Risks / Trade-offs

- **风险**：用户习惯 `pip install psi-agent[dev]` 将不再有效
- **缓解**：这是内部开发工具，外部用户不应安装；如有需要可在 README 说明
