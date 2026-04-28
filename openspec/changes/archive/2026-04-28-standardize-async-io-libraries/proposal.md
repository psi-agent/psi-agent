## Why

psi-agent 项目使用异步编程作为核心架构，但目前 CLAUDE.md 中的 async 生态技术选型不够明确，导致代码中出现不一致的库使用（如 httpx 和 aiohttp 混用）。统一技术选型可以提高代码一致性、减少依赖冲突，并确保团队（包括 AI 助手）在编写代码时遵循统一标准。

## What Changes

- 在 CLAUDE.md 中明确 async IO 技术选型：
  - 文件系统：统一使用 `anyio`（替代 aiofiles）
  - 网络请求：统一使用 `aiohttp`（替代 httpx）
- 更新 CLAUDE.md 中所有相关示例代码
- 更新现有代码仓库中不符合此原则的实现（psi-ai-openai-completions 客户端）

## Capabilities

### Modified Capabilities

- `CLAUDE.md`: 更新 Async 接口规范部分，明确技术选型
- `psi-ai-openai-completions`: 将 HTTP 客户端从 httpx 迁移到 aiohttp

## Impact

- 影响范围：CLAUDE.md 文档、src/psi_agent/ai/openai_completions/client.py
- 受益者：所有开发者和 AI 助手
- 依赖关系：需要更新 pyproject.toml 依赖（移除 httpx，确保 aiohttp 存在）