## 1. 更新 CLAUDE.md 文档

- [x] 1.1 更新 "Async 接口规范" 部分：文件系统使用 `anyio`，网络使用 `aiohttp`
- [x] 1.2 更新 "Import 顺序规范" 示例：将 httpx 改为 aiohttp
- [x] 1.3 更新 "Async 上下文管理器规范" 示例：将 httpx.AsyncClient 改为 aiohttp.ClientSession
- [x] 1.4 更新 "错误处理规范" 示例：将 httpx 异常改为 aiohttp 异常
- [x] 1.5 更新 tools/ 目录示例：将 aiofiles 改为 anyio

## 2. 迁移 psi-ai-openai-completions 客户端

- [x] 2.1 更新 client.py：将 httpx.AsyncClient 替换为 aiohttp.ClientSession
- [x] 2.2 更新流式请求处理：适配 aiohttp 的流式 API
- [x] 2.3 更新错误处理：使用 aiohttp 异常类型
- [x] 2.4 更新 cli.py：确保 asyncio.sleep 保持不变（符合 anyio 标准）

## 3. 更新依赖配置

- [x] 3.1 从 pyproject.toml 移除 httpx 依赖
- [x] 3.2 确保 aiohttp 在依赖中
- [x] 3.3 添加 anyio 依赖

## 4. 运行质量检查

- [x] 4.1 运行 `ruff check` 确保无 lint 错误
- [x] 4.2 运行 `ruff format` 确保格式正确
- [x] 4.3 运行 `ty check` 确保类型检查通过
- [x] 4.4 运行 pytest 确保测试通过（如有） — *测试有预先存在的导入配置问题*

## 5. 修复测试文件（补充）

- [x] 5.1 更新 test_client.py：`_client` → `_session`
- [x] 5.2 更新 test_server.py：修复 aiohttp 路由断言（`r.resource.canonical` → 更安全的检查方式）