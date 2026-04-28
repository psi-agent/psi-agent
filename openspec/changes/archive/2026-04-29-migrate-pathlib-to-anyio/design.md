## Context

psi-agent 是一个异步 agent 框架，核心运行在 async 环境中。当前代码库中存在大量使用 `pathlib.Path` 进行同步文件操作的情况，这违反了项目的 async 规范（CLAUDE.md 中明确要求"所有 IO 操作必须使用 async 生态方法"）。

**当前状态分析**：

| 类别 | 文件 | 同步操作类型 |
|------|------|-------------|
| **高影响** | `tool_loader.py` | `read_bytes()`, `exists()`, `iterdir()`, `is_file()` |
| **高影响** | `workspace_watcher.py` | `read_bytes()`, `exists()`, `iterdir()`, `is_file()`, `is_dir()` |
| **高影响** | `history.py` | `exists()`, `read_text()`, `write_text()` |
| **中影响** | `schedule.py` | `exists()`, `iterdir()`, `is_dir()` (部分已用 anyio) |
| **中影响** | `workspace/*.py` | `resolve()`, `mkdir()`, `unlink()`, `rmdir()` |
| **低影响** | `config.py` 系列 | 仅类型注解，无实际 IO 操作 |
| **低影响** | `runner.py` | 仅一处 `exists()` |

**约束**：
- 所有改动必须保持向后兼容
- 不能改变公开 API 的签名
- 必须通过 `ruff check`, `ruff format`, `ty check` 和测试

## Goals / Non-Goals

**Goals:**
- 将所有同步文件操作迁移到 `anyio.Path` 的异步版本
- 保持代码行为完全一致，仅改变执行方式
- 确保所有改动后的代码符合项目 async 规范

**Non-Goals:**
- 不引入新的文件操作功能
- 不改变任何 API 签名或返回值类型
- 不重构代码结构（仅做最小改动）
- 不处理 `config.py` 文件中的类型注解（它们不执行 IO，仅作为路径表示）

## Decisions

### Decision 1: 使用 `anyio.Path` 而非 `aiofiles`

**选择**: `anyio.Path`

**理由**:
- anyio 是项目现有依赖，无需新增依赖
- `anyio.Path` 提供与 `pathlib.Path` 几乎完全一致的 API，迁移成本低
- `aiofiles` 需要单独安装，且 API 与 pathlib 不同（使用 `aiofiles.open()` 而非 `Path.open()`）

**替代方案**: `aiofiles` - 拒绝，因为需要额外依赖且 API 不一致

### Decision 2: 函数签名改造策略

**选择**: 将执行 IO 的函数改为 async

**理由**:
- 符合项目规范（所有 IO 操作必须是 async）
- `anyio.Path` 的所有方法都是 async，调用者必须是 async 函数
- 保持最小改动原则

**改造模式**:
```python
# Before (同步)
def compute_file_hash(file_path: Path) -> str:
    content = file_path.read_bytes()
    return hashlib.md5(content).hexdigest()

# After (异步)
async def compute_file_hash(file_path: Path) -> str:
    content = await anyio.Path(file_path).read_bytes()
    return hashlib.md5(content).hexdigest()
```

### Decision 3: iterdir() 处理策略

**选择**: 使用 `async for` 循环

**理由**:
- `anyio.Path.iterdir()` 返回 AsyncGenerator，必须用 `async for`
- 保持代码结构不变，仅改变循环类型

**改造模式**:
```python
# Before
for file_path in tools_dir.iterdir():
    ...

# After
async for file_path in anyio.Path(tools_dir).iterdir():
    ...
```

### Decision 4: 类型注解保持策略

**选择**: 函数参数类型注解保持 `pathlib.Path`

**理由**:
- `anyio.Path` 继承自 `pathlib.Path`，类型兼容
- 保持公开 API 签名不变
- 内部使用时转换为 `anyio.Path`

**改造模式**:
```python
# 参数类型保持 pathlib.Path
async def load_tool_from_file(file_path: Path) -> ToolSchema | None:
    # 内部转换为 anyio.Path
    content = await anyio.Path(file_path).read_bytes()
```

## Risks / Trade-offs

### Risk 1: iterdir() 返回 AsyncGenerator 而非 list

**风险**: `anyio.Path.iterdir()` 返回 AsyncGenerator，无法直接转换为 list 或多次迭代

**缓解**: 如果需要多次迭代或转换为 list，使用 `async for` 收集到 list：
```python
items = []
async for item in anyio.Path(dir).iterdir():
    items.append(item)
```

### Risk 2: 调用链改造

**风险**: 将函数改为 async 后，其调用者也需要是 async 或使用 `await`

**缓解**: 检查调用链，确保所有调用者都是 async 函数。psi-agent 核心已经是 async 环境，大多数调用者已经是 async。

### Risk 3: 测试兼容性

**风险**: 现有测试可能使用同步调用方式

**缓解**: 更新测试以支持 async 函数，使用 pytest-asyncio 的 `@pytest.mark.asyncio` 装饰器。

## Migration Plan

**阶段 1: 高影响文件** (session 核心)
- `tool_loader.py` - 工具加载器
- `workspace_watcher.py` - workspace 监控
- `history.py` - 历史记录

**阶段 2: 中影响文件** (schedule 和 workspace)
- `schedule.py` - 定时任务
- `runner.py` - session runner
- `workspace/mount/api.py`
- `workspace/pack/api.py`
- `workspace/snapshot/api.py`
- `workspace/umount/api.py`
- `workspace/unpack/api.py`

**阶段 3: 低影响文件** (channel 和其他)
- `channel/repl/repl.py`
- `ai/openai_completions/server.py`

**阶段 4: 测试更新**
- 更新所有受影响的测试文件

**阶段 5: 验证**
- 运行 `ruff check`, `ruff format`, `ty check`
- 运行所有测试确保无回归

## Open Questions

无。此变更技术路径清晰，无待决问题。