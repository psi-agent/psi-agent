## 1. 合并依赖配置

- [x] 1.1 将 `[project.optional-dependencies]` 的 dev 组内容合并到 `[dependency-groups]` 的 dev 组
- [x] 1.2 删除 `[project.optional-dependencies]` 整个部分
- [x] 1.3 将 `[dependency-groups]` 移动到 `[project.dependencies]` 下面，方便查看依赖
- [x] 1.4 对 `[dependency-groups]` dev 组中的依赖按字母顺序排序

## 2. 验证

- [x] 2.1 运行 `uv sync --group dev` 验证依赖安装正常
- [x] 2.2 运行 `ruff check` 和 `ruff format` 验证代码质量工具正常
- [x] 2.3 运行 `pytest` 验证测试正常
