## Context

psi-agent 是一个异步 agent 框架，所有 IO 操作必须使用 async 方法。当前 CLAUDE.md 规范不够明确，允许 aiofiles/httpx/aiohttp 混用，导致实际代码中出现了不一致：

- server.py 使用 aiohttp（正确）
- client.py 使用 httpx（不符合新标准）

用户希望统一技术选型为：
- 文件系统：anyio（anyio.open_file 提供异步文件操作）
- 网络请求：aiohttp（统一 HTTP 客户端和服务器）

## Goals / Non-Goals

**Goals:**
- 在 CLAUDE.md 中明确统一的技术选型
- 更新 CLAUDE.md 中的示例代码以反映新标准
- 迁移 psi-ai-openai-completions 客户端代码从 httpx 到 aiohttp

**Non-Goals:**
- 不创建新的 spec 文件（此变更不涉及功能需求）
- 不修改 server.py（已使用 aiohttp，符合标准）
- 不修改 tests 目录（暂无现有测试）

## Decisions

### 文件系统操作

使用 `anyio.open_file()` 进行异步文件读写：

```python
async def tool(file_path: str) -> str:
    async with await anyio.open_file(file_path) as f:
        return await f.read()
```

anyio 是跨 async 框架的抽象层，支持 asyncio 和 trio，提供更灵活的兼容性。

### 网络请求

使用 `aiohttp.ClientSession` 进行 HTTP 客户端请求：

```python
async with aiohttp.ClientSession() as session:
    async with session.post(url, json=body) as response:
        result = await response.json()
```

aiohttp 提供 HTTP 客户端和服务器功能，统一使用可减少依赖数量。

### 依赖变更

- 移除 httpx 依赖
- 确保 aiohttp 已在依赖中
- 添加 anyio 依赖

## Risks / Trade-offs

- **API 差异**：httpx 和 aiohttp API 不同，需要仔细迁移
- **anyio 学习曲线**：团队需熟悉 anyio 的文件操作 API
- **迁移工作量**：现有代码需要重写 HTTP 客户端部分