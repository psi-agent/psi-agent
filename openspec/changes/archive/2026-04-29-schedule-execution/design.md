## Context

psi-agent workspace 定义了 `schedules/` 目录结构，每个任务有 `TASK.md` 文件包含 YAML frontmatter（含 `cron` 字段）和任务指令。psi-session 目前只处理用户消息，没有定时任务执行能力。

**当前 session 架构：**
- `runner.py` - 主运行循环，处理消息
- `server.py` - HTTP 服务器，接收 channel 请求
- `tool_loader.py` - 加载 tools
- `history.py` - 对话历史管理

## Goals / Non-Goals

**Goals:**
- 加载 workspace 的 `schedules/` 目录中的定时任务
- 解析标准 5 字段 cron 表达式
- 按时间表触发任务，将 TASK.md 内容作为消息发送给 LLM
- 支持多个定时任务并发运行

**Non-Goals:**
- 不支持分布式调度（单进程内运行）
- 不支持任务持久化（重启后重新计算下次执行时间）
- 不支持任务动态添加/删除（启动时加载）

## Decisions

### 1. 使用 `croniter` 库解析 cron 表达式

**Rationale:** `croniter` 是 Python 中最成熟的 cron 解析库，支持标准 5 字段格式，计算下次执行时间准确。

**Alternatives considered:**
- `apscheduler`: 功能更全但更重，适合更复杂的调度场景
- 手动解析: 容易出错，不值得重复造轮子

### 2. 使用 `asyncio` 实现调度循环

**Rationale:** session 已经是 async 架构，使用 `asyncio.create_task` 可以轻松集成定时任务，不需要额外的线程或进程。

**实现方式：**
```python
async def schedule_loop(schedule: Schedule, runner: Runner):
    while True:
        next_time = schedule.get_next_run()
        delay = next_time - datetime.now()
        await asyncio.sleep(delay.total_seconds())
        await runner.run(schedule.task_content)
```

### 3. 任务触发时发送 TASK.md 内容作为用户消息

**Rationale:** 保持简单，TASK.md 的内容就是任务指令，LLM 会根据指令执行相应操作。

### 4. 模块结构

```
src/psi_agent/session/
├── schedule.py       # Schedule 加载器和执行器
└── runner.py         # 集成 schedule 执行
```

## Risks / Trade-offs

**Risk: 任务执行时间可能超过调度间隔**
→ Mitigation: 记录警告日志，跳过本次执行（不重叠执行）

**Risk: 时区问题**
→ Mitigation: 使用本地时间，与 cron 标准一致。未来可扩展支持时区配置。

**Trade-off: 不支持任务持久化**
→ 接受。重启后重新计算执行时间。如需持久化，可在 workspace 中自行实现。
