## 1. 项目框架搭建

- [x] 1.1 创建 pyproject.toml，定义项目元数据（name: psi-agent, version, requires-python: >=3.14）
- [x] 1.2 添加依赖：aiohttp, httpx, loguru, tyro
- [x] 1.3 配置开发工具：ruff (check, format), ty (check), pytest
- [x] 1.4 配置 scripts 入口点：psi-ai-openai-completions
- [x] 1.5 创建 src/psi_agent/ 目录结构
- [x] 1.6 创建 src/psi_agent/__init__.py
- [x] 1.7 创建 src/psi_agent/ai/__init__.py
- [x] 1.8 创建 tests/ 目录结构

## 2. 配置模块实现

- [x] 2.1 创建 config.py，定义配置类（session_socket, model, api_key, base_url）
- [x] 2.2 配置类使用 dataclass，支持 tyro 自动解析
- [x] 2.3 编写 tests/ai/openai_completions/test_config.py

## 3. OpenAI API Client 实现

- [x] 3.1 创建 client.py，实现 httpx AsyncClient
- [x] 3.2 实现请求转发函数（添加 Authorization header）
- [x] 3.3 使用 loguru 记录请求详情（URL, headers, body摘要）
- [x] 3.4 实现 non-streaming 请求处理
- [x] 3.5 实现 streaming 请求处理（SSE chunk转发）
- [x] 3.6 编写 tests/ai/openai_completions/test_client.py

## 4. HTTP Server 实现

- [x] 4.1 创建 server.py，实现 aiohttp web.Application
- [x] 4.2 实现 Unix socket 监听（处理已存在文件的情况）
- [x] 4.3 使用 loguru 记录 server 启动、请求接收、响应发送
- [x] 4.4 实现 POST /v1/chat/completions 请求处理器
- [x] 4.5 实现 streaming response 处理（SSE 格式）
- [x] 4.6 编写 tests/ai/openai_completions/test_server.py

## 5. Python API 与 CLI 实现

- [x] 5.1 创建 __init__.py，导出主要 Python API（Server, Client, Config类）
- [x] 5.2 创建 cli.py，定义 run() 函数作为 Python API 入口
- [x] 5.3 使用 tyro.Cli 从 run() 函数生成 CLI
- [x] 5.4 实现 main() 函数入口供 script 调用
- [x] 5.5 整合 config、server、client 启动流程

## 6. 错误处理

- [x] 6.1 处理上游 API 连接失败（返回 500，loguru 记录错误）
- [x] 6.2 处理 API 认证失败（转发错误响应，loguru 记录）

## 7. 测试与质量检查

- [x] 7.1 运行 ruff format 格式化所有代码
- [x] 7.2 运行 ruff check lint 检查，修复所有问题
- [x] 7.3 运行 ty check typing 检查，修复所有问题
- [x] 7.4 运行 pytest 执行所有测试，确保全部通过
- [x] 7.5 手动测试 non-streaming 请求（curl 或 Python API）
- [x] 7.6 手动测试 streaming 请求