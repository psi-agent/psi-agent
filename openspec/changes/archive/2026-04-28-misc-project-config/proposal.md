## Why

项目需要完善基础设施配置：明确开源协议（AGPL v3）、添加作者邮箱、使用动态版本管理（hatch-vcs），并将现有代码风格固化到 CLAUDE.md 中，确保后续开发一致性。

## What Changes

- 软件协议从 MIT 改为 AGPL v3
- pyproject.toml 添加作者邮箱 `hzhangxyz@outlook.com`
- 使用 hatch-vcs 动态版本管理，替代硬编码版本号
- CLAUDE.md 补充代码风格规范：
  - import 顺序规范
  - async 上下文管理器规范
  - 错误处理规范
  - 类型注解规范
  - **文档字符串规范（Google style）**

## Capabilities

### New Capabilities

(None - 这是配置变更，不涉及新功能)

### Modified Capabilities

- `claude-md`: 添加代码风格规范章节（import顺序、async规范、错误处理规范、类型注解规范、文档字符串规范）

## Impact

- 影响文件：pyproject.toml, CLAUDE.md, LICENSE（新增）
- 影响范围：项目配置和开发规范
- 无代码逻辑变更