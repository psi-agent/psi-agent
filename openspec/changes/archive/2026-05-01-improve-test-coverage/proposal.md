## Why

当前测试覆盖率总体为 89%，但部分关键模块覆盖率不足，存在未测试的代码路径。这些低覆盖率区域包括错误处理分支、边缘情况、以及部分服务器启动逻辑。提高测试覆盖率可以增强代码质量保证，减少回归风险。

## What Changes

- 为覆盖率低于 80% 的模块添加测试
- 为覆盖率在 80%-90% 之间的模块补充缺失的测试用例
- 重点覆盖错误处理路径和边缘情况

### 覆盖率改进目标

| 模块 | 当前覆盖率 | 目标覆盖率 |
|------|-----------|-----------|
| `ai/anthropic_messages/server.py` | 65% | 90% |
| `workspace/umount/api.py` | 63% | 85% |
| `session/cli.py` | 74% | 90% |
| `ai/openai_completions/cli.py` | 77% | 90% |
| `ai/anthropic_messages/cli.py` | 78% | 90% |
| `workspace/mount/api.py` | 78% | 90% |
| `ai/openai_completions/server.py` | 78% | 90% |
| `session/server.py` | 76% | 90% |

## Capabilities

### New Capabilities

- `low-coverage-module-testing`: 为低覆盖率模块（<80%）添加测试，覆盖错误处理和边缘情况

### Modified Capabilities

- `test-coverage-improvement`: 扩展现有规范，增加对低覆盖率模块的测试要求

## Impact

- **测试文件**：新增和修改 `tests/` 目录下的测试文件
- **CI/CD**：提高覆盖率阈值要求
- **代码质量**：减少未测试代码路径，降低回归风险
