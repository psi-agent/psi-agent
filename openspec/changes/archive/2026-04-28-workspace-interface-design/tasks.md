## 1. 核心数据结构

- [x] 1.1 定义 Manifest 数据结构（layers, default 字段）
- [x] 1.2 实现 Manifest JSON 解析函数
- [x] 1.3 实现 Manifest JSON 序列化函数
- [x] 1.4 编写 Manifest 相关单元测试

## 2. psi-workspace-pack 组件

- [x] 2.1 创建 psi_agent/workspace/pack 模块结构
- [x] 2.2 实现 pack Python API（输入目录、输出 squashfs 路径）
- [x] 2.3 实现 squashfs 创建逻辑（使用 mksquashfs 命令）
- [x] 2.4 实现 manifest.json 创建逻辑
- [x] 2.5 实现 CLI 入口（使用 tyro）
- [x] 2.6 编写 pack 相关单元测试

## 3. psi-workspace-unpack 组件

- [x] 3.1 创建 psi_agent/workspace/unpack 模块结构
- [x] 3.2 实现 unpack Python API（输入 squashfs、输出目录）
- [x] 3.3 实现 squashfs 解压逻辑（使用 unsquashfs 命令）
- [x] 3.4 实现 CLI 入口（使用 tyro）
- [x] 3.5 编写 unpack 相关单元测试

## 4. psi-workspace-mount 组件

- [x] 4.1 创建 psi_agent/workspace/mount 模块结构
- [x] 4.2 实现 mount Python API（输入 squashfs、输出目录、可选 layers）
- [x] 4.3 实现 squashfs 挂载逻辑（mount -t squashfs）
- [x] 4.4 实现 overlayfs 挂载逻辑（mount -t overlay）
- [x] 4.5 实现临时目录创建和管理
- [x] 4.6 实现层级配置解析（default 或用户指定）
- [x] 4.7 实现 CLI 入口（使用 tyro）
- [x] 4.8 编写 mount 相关单元测试

## 5. psi-workspace-umount 组件

- [x] 5.1 创建 psi_agent/workspace/umount 模块结构
- [x] 5.2 实现 umount Python API（挂载点路径）
- [x] 5.3 实现 overlayfs 卸载逻辑
- [x] 5.4 实现 squashfs 卸载逻辑
- [x] 5.5 实现临时目录清理逻辑
- [x] 5.6 实现 CLI 入口（使用 tyro）
- [x] 5.7 编写 umount 相关单元测试

## 6. psi-workspace-snapshot 组件

- [x] 6.1 创建 psi_agent/workspace/snapshot 模块结构
- [x] 6.2 实现 snapshot Python API（输入 squashfs、挂载点、可选输出路径）
- [x] 6.3 实现原子写入逻辑（临时文件 + mv）
- [x] 6.4 实现 diff 目录添加逻辑
- [x] 6.5 实现 manifest 更新逻辑（新层、parent、default）
- [x] 6.6 实现 squashfs 创建逻辑（添加新层）
- [x] 6.7 实现 CLI 入口（使用 tyro）
- [x] 6.8 编写 snapshot 相关单元测试

## 7. 文档更新

- [x] 7.1 更新 CLAUDE.md 中 psi-workspace-* 组件部分
- [x] 7.2 添加 manifest.json 结构规范到 CLAUDE.md
- [x] 7.3 添加 squashfs 镜像结构规范到 CLAUDE.md
- [x] 7.4 添加 CLI 使用示例到 CLAUDE.md

## 8. 集成测试

- [x] 8.1 编写 pack + mount + umount + snapshot 端到端测试
- [x] 8.2 编写多层 snapshot 测试
- [x] 8.3 编写错误处理测试（权限不足、无效输入等）