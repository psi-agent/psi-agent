## Why

测试文件中存在多处非顶级 import，违反了 PEP 8 和项目编码规范。虽然测试代码有其特殊性，但为了代码一致性和可维护性，应将所有 import 移至文件顶级。

## What Changes

将以下测试文件中的非顶级 import 移至文件顶级：

- `tests/channel/cli/test_cli.py`: `import inspect` 移至顶级
- `tests/channel/repl/test_client.py`: `import aiohttp` 移至顶级
- `tests/session/test_server.py`: `from psi_agent.session.runner import SessionRunner` 和 `import json` 移至顶级
- `tests/ai/anthropic_messages/test_server.py`: `import json` 移至顶级
- `tests/ai/anthropic_messages/test_translator.py`: `from psi_agent.ai.anthropic_messages.translator import StreamingTranslator` 移至顶级
- `tests/ai/openai_completions/test_client.py`: `from openai import ...` 异常类型移至顶级
- `tests/ai/anthropic_messages/test_client.py`: `from anthropic import ...` 异常类型移至顶级
- `tests/workspace/test_snapshot.py`: `from uuid import uuid4` 和 `from psi_agent.workspace.manifest import Manifest` 移至顶级

## Capabilities

### New Capabilities

无新能力引入。

### Modified Capabilities

无现有能力的需求变更。此 change 仅涉及测试代码风格改进。

## Impact

**受影响的文件**：
- `tests/channel/cli/test_cli.py`
- `tests/channel/repl/test_client.py`
- `tests/session/test_server.py`
- `tests/ai/anthropic_messages/test_server.py`
- `tests/ai/anthropic_messages/test_translator.py`
- `tests/ai/openai_completions/test_client.py`
- `tests/ai/anthropic_messages/test_client.py`
- `tests/workspace/test_snapshot.py`

**兼容性**：无 API 变更，无破坏性变更。仅影响测试代码。
