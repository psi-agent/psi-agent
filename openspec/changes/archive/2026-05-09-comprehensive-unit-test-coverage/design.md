## Context

psi-agent 当前有约 50 个测试文件，覆盖了大部分模块的 happy path。但从功能角度审视，错误路径、边界条件和多步交互场景的测试严重不足。本次变更的目标是系统性地补全这些缺失的测试，确保每个功能点的正常路径和异常路径都有对应测试。

当前测试框架：pytest + pytest-asyncio，使用 unittest.mock 进行隔离。所有测试位于 `tests/` 目录，结构与 `src/psi_agent/` 对应。

## Goals / Non-Goals

**Goals:**

- 补全所有模块的错误路径和异常处理测试，确保生产环境可能遇到的异常都有对应测试
- 补全防御性编程的 null/None 边界条件测试，验证代码对 LLM 响应、用户输入等外部数据的防御能力
- 补全多步交互场景测试，如多轮 tool call、workspace 变更检测的混合变更、schedule 执行器的异常重试
- 发现并记录现有代码中的 bug（如 server.py null content 崩溃、manifest 序列化不一致等），在测试中标记为已知问题
- 保持测试风格一致：使用 pytest + pytest-asyncio，遵循现有测试的命名和组织模式

**Non-Goals:**

- 不追求代码覆盖率数字，而是从功能角度确保关键路径有测试
- 不重构现有测试文件的结构或命名
- 不修改源码修复 bug（发现的 bug 在测试中用 `xfail` 标记，后续单独修复）
- 不添加集成测试或端到端测试，仅限单元测试
- 不修改 CI 配置或测试框架

## Decisions

### 1. 测试组织方式：扩展现有文件而非新建

**决策**：在现有测试文件中添加新的测试类/方法，而非为每个 gap 创建新文件。

**理由**：现有测试文件已经按模块组织良好，新建文件会增加维护成本且与现有结构不一致。仅当现有文件不存在时才创建新文件（如 workspace CLI 测试）。

**例外**：workspace CLI 测试（pack/unpack/mount/umount/snapshot 的 cli.py）目前完全没有测试，需要新建测试文件。

### 2. Bug 处理策略：xfail 标记

**决策**：发现的代码 bug 在测试中用 `pytest.mark.xfail` 标记，并添加注释说明问题。

**理由**：本次变更的目标是补全测试，不是修复 bug。xfail 标记可以记录已知问题，同时确保测试在 bug 修复后能自动通过。避免在补全测试的同时修改源码，降低变更风险。

**已知 bug 清单**：
- `server.py` `_handle_chat_completions`：user_message content 为 None 时 `content[:100]` 可能崩溃
- `umount/api.py` `umount`：mount info 缺少 `squashfs_mount` 等字段时抛出 KeyError 而非 UmountError
- `snapshot/api.py` `snapshot`：mount info 缺少 `upper_dir` 字段时抛出 KeyError 而非 SnapshotError
- `manifest.py` `serialize_manifest`：default=None 时序列化为空字符串，无法反序列化
- `history.py` `load_history_from_file`：JSON 内容为 dict/string 时返回非 list 类型

### 3. Mock 策略：最小化 mock 深度

**决策**：优先 mock 外部依赖（网络、文件系统、子进程），而非 mock 内部函数调用。

**理由**：过度 mock 会使测试与实现细节耦合，降低测试价值。mock 外部依赖可以在保持测试隔离的同时验证真实逻辑。

### 4. 测试优先级排序

**决策**：按功能重要性排序，先补全 high priority 的错误路径和 null 安全测试，再补全 medium priority 的边界条件，最后补全 low priority 的极端场景。

**优先级定义**：
- **High**：生产环境可能触发的错误路径、null 安全问题、数据损坏防护
- **Medium**：边界条件、多步交互、防御性编程
- **Low**：极端输入、性能边界、不太可能发生的场景

## Risks / Trade-offs

- **[测试维护成本增加]** → 新增约 200+ 个测试用例，维护成本增加。缓解：测试遵循现有模式，使用共享 fixture 减少重复。
- **[xfail 测试可能长期存在]** → xfail 标记的 bug 如果不及时修复，测试会一直处于 xfail 状态。缓解：在 xfail 注释中记录 issue 编号，定期清理。
- **[Mock 与实现不同步]** → 过度 mock 可能导致测试通过但实际代码有 bug。缓解：优先 mock 外部依赖，减少对内部实现的 mock。
- **[测试执行时间增加]** → 新增测试可能增加 CI 时间。缓解：单元测试本身执行很快，增加的时间在可接受范围内。
