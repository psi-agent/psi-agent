## Why

psi-workspace-* 组件的接口设计目前未定义（CLAUDE.md 中标注为"待定"）。作为 psi-agent 可移植性核心理念的关键部分，workspace 管理组件需要明确的接口规范，以便开发者能够正确实现打包、挂载、快照等功能。

## What Changes

- 定义五个 psi-workspace-* 组件的 CLI 和 Python API 接口
- 规范 manifest.json 的结构和内容（UUID 命名层、tag 支持）
- 定义 squashfs 镜像的内部结构
- 定义 overlayfs 挂载策略（支持 UUID 或 tag 指定层）
- 定义 snapshot 的行为和 manifest 更新规则
- 更新 CLAUDE.md 中的 psi-workspace-* 组件部分

## Capabilities

### New Capabilities

- `workspace-pack`: 将 workspace 目录打包成 squashfs 镜像的接口
- `workspace-unpack`: 将 squashfs 镜像解压成目录的接口（不挂载）
- `workspace-mount`: 将 squashfs 镜像挂载成 overlayfs 的接口
- `workspace-umount`: 卸载已挂载 workspace 的接口
- `workspace-snapshot`: 创建 workspace 快照的接口
- `workspace-manifest`: manifest.json 的结构和规范

### Modified Capabilities

None - 这是新能力引入。

## Impact

- **psi-workspace-* 组件**: 五个独立组件需要实现各自接口
- **CLAUDE.md**: 更新 psi-workspace-* 组件部分，添加完整接口规范
- **manifest.json**: 定义标准格式，所有组件需要遵循
- **用户工作流**: 用户通过 CLI 手动调用这些组件管理 workspace