## 1. 修复 tests/channel/cli/test_cli.py

- [x] 1.1 将 `import inspect` 从测试方法内移至文件顶级

## 2. 修复 tests/channel/repl/test_client.py

- [x] 2.1 将 `import aiohttp` 从测试方法内移至文件顶级

## 3. 修复 tests/session/test_server.py

- [x] 3.1 将 `from psi_agent.session.runner import SessionRunner` 从测试方法内移至文件顶级
- [x] 3.2 将 `import json` 从测试方法内移至文件顶级

## 4. 修复 tests/ai/anthropic_messages/test_server.py

- [x] 4.1 将 `import json` 从测试方法内移至文件顶级

## 5. 修复 tests/ai/anthropic_messages/test_translator.py

- [x] 5.1 将 `from psi_agent.ai.anthropic_messages.translator import StreamingTranslator` 从测试方法内移至文件顶级

## 6. 修复 tests/ai/openai_completions/test_client.py

- [x] 6.1 将 `from openai import AuthenticationError, RateLimitError, APIConnectionError, APITimeoutError` 从测试方法内移至文件顶级

## 7. 修复 tests/ai/anthropic_messages/test_client.py

- [x] 7.1 将 `from anthropic import AuthenticationError, RateLimitError, APIConnectionError` 从测试方法内移至文件顶级

## 8. 修复 tests/workspace/test_snapshot.py

- [x] 8.1 将 `from uuid import uuid4` 从 mock 内移至文件顶级
- [x] 8.2 将 `from psi_agent.workspace.manifest import Manifest` 从 mock 内移至文件顶级

## 9. 验证

- [x] 9.1 运行 `ruff check` 确保无 lint 错误
- [x] 9.2 运行 `ty check` 确保无类型错误
- [x] 9.3 运行 `pytest` 确保所有测试通过