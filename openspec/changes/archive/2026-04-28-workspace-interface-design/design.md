## Context

psi-agent 的核心理念是**可移植性**——用户只需复制 workspace 目录即可完成 agent 移植。psi-workspace-* 组件负责管理 workspace 的打包、挂载、快照等操作，是实现可移植性的关键。

当前状态：
- workspace 目录结构已定义（tools/, skills/, schedules/, systems/）
- psi-workspace-* 组件接口标注为"待定"
- 需要支持 squashfs 镜像和 overlayfs 挂载

约束：
- 所有组件使用 tyro 实现 CLI
- 所有 IO 操作必须是 async
- 使用 loguru 记录日志
- 错误通过异常抛出

## Goals / Non-Goals

**Goals:**
- 定义五个 psi-workspace-* 组件的完整接口
- 规范 manifest.json 结构
- 定义 squashfs 镜像内部结构
- 定义 overlayfs 挂载策略
- 支持 snapshot 的原子写入

**Non-Goals:**
- 不定义 psi-session 如何使用 workspace（已在 CLAUDE.md 中定义）
- 不定义网络传输或远程 workspace 管理
- 不定义 workspace 版本控制（除 snapshot 外）

## Decisions

### 1. 组件拆分策略

**决定：** 拆分为五个独立组件（mount, umount, snapshot, pack, unpack）

**理由：**
- 每个功能独立，用户按需调用
- 符合 Unix 哲学：一个工具做一件事
- 便于独立测试和维护

**替代方案：** 单一 psi-workspace 组件带子命令
- 缺点：增加复杂度，不符合 psi-agent 组件化理念

### 2. Squashfs 镜像结构

**决定：**
```
workspace.squashfs
├── manifest.json          # 元信息
├── <uuid-1>/              # 基础层（第一个 pack 的目录）
├── <uuid-2>/              # 后续 snapshot 添加的层
├── <uuid-3>/
└── ...
```

**manifest.json 结构：**
```json
{
  "layers": {
    "<uuid-1>": { "tag": "v1.0" },
    "<uuid-2>": { "parent": "<uuid-1>", "tag": "v1.1" },
    "<uuid-3>": { "parent": "<uuid-2>" }
  },
  "default": "<uuid-3>"
}
```

**理由：**
- UUID 作为层名保证唯一性，避免命名冲突
- tag 是可选的，方便用户记忆和引用
- default 存储单个层 UUID，表示当前最新状态
- mount 时可通过 UUID 或 tag 指定要挂载的层

### 3. Overlayfs 挂载策略

**决定：**
1. 将 squashfs 挂载到临时目录（只读）
2. 根据指定的层（UUID 或 tag）解析出完整层级链
3. 创建 upper 和 work 目录
4. 使用 overlayfs 挂载到用户指定路径

**层级链解析：**
- 从指定层开始，沿 parent 链向上追溯，直到根层
- overlayfs lowerdir 按从上到下的顺序排列

**挂载命令示例：**
```bash
mount -t squashfs workspace.squashfs /tmp/squashfs-xxx -o loop
mount -t overlay overlay /target/path \
  -o lowerdir=/tmp/squashfs-xxx/<uuid-3>:/tmp/squashfs-xxx/<uuid-2>:/tmp/squashfs-xxx/<uuid-1> \
  -o upperdir=/tmp/upper-xxx \
  -o workdir=/tmp/work-xxx
```

**理由：**
- squashfs 只读，需要 upper 层支持写入
- overlayfs 提供写入层分离
- 用户可通过 UUID 或 tag 指定要挂载的层版本

### 4. Snapshot 原子写入

**决定：**
1. 复制原始 squashfs 到临时文件（同目录，确保同文件系统）
2. 添加 diff 目录到 squashfs
3. 更新 manifest.json
4. mv 临时文件到目标路径

**理由：**
- 避免系统崩溃导致数据损坏
- 同文件系统保证 mv 是原子操作
- 临时文件在目标文件附近确保同文件系统

### 5. 错误处理策略

**决定：**
- 记录日志（loguru）
- 抛出异常（Python API）
- CLI 捕获异常并显示错误信息

**理由：**
- 日志在任何时候都需要记录
- Python API 使用异常是 Python 惯例
- CLI 需要友好的错误显示

## Risks / Trade-offs

### 风险：Overlayfs 需要 root 权限

**缓解：**
- 文档中明确说明权限要求
- 提供错误提示引导用户使用 sudo

### 风险：Snapshot 可能很慢（复制整个 squashfs）

**缓解：**
- 文档中说明 snapshot 性能特点
- 未来可考虑增量 snapshot

### 风险：临时文件可能占用大量空间

**缓解：**
- 使用系统临时目录（/tmp）
- 提供 --temp-dir 选项让用户指定

### Trade-off：不支持分支（多个 parent）

**理由：**
- 简化实现
- 大多数场景是线性历史
- 未来可扩展
