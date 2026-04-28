## Why

pyproject.toml 中依赖版本指定使用最低版本约束（如 `>=3.9.0`），但实际安装版本已更新到最新。为了明确依赖版本并避免潜在的兼容性问题，需要将版本号更新为 PyPI 当前最新版本。

## What Changes

- 更新所有依赖版本号到 PyPI 最新版本
- 重点关注大版本升级的依赖：tyro (0.8 → 1.0)、pytest-asyncio (0.23 → 1.3)

## Capabilities

### Modified Capabilities

- `pyproject.toml`: 更新依赖版本约束

## Impact

- 影响范围：pyproject.toml, uv.lock
- 受益者：开发者（明确依赖版本）
- 依赖关系：无
- 风险：tyro 和 pytest-asyncio 大版本升级可能有 API 变化