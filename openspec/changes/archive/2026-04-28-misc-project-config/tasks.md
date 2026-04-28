## 1. 项目配置更新

- [x] 1.1 创建 LICENSE 文件，内容为 AGPL v3 完整文本
- [x] 1.2 修改 pyproject.toml：license 改为 `{ file = "LICENSE" }`
- [x] 1.3 修改 pyproject.toml：authors 添加 email `hzhangxyz@outlook.com`
- [x] 1.4 修改 pyproject.toml：添加 hatch-vcs 配置（动态版本）

## 2. CLAUDE.md 更新

- [x] 2.1 添加 Import 顺序规范章节（stdlib → third-party → local）
- [x] 2.2 添加 Async 上下文管理器规范章节
- [x] 2.3 添加错误处理规范章节（try-except + loguru + error dict）
- [x] 2.4 添加类型注解规范章节（使用 `| None` 语法）
- [x] 2.5 添加文档字符串规范章节（Google style格式）

## 3. 质量检查

- [x] 3.1 运行 `uv sync` 确保依赖正确安装
- [x] 3.2 运行 `ruff check` 和 `ruff format` 检查代码
- [x] 3.3 验证 hatch-vcs 版本生成正确（无 tag 时应为 `0.0.0` 或类似）