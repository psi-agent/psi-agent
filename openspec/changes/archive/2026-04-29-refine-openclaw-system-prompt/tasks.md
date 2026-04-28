## 1. 身份声明修改

- [x] 1.1 修改 `_build_identity_section()` 返回 "You are a personal assistant running inside psi agent."

## 2. Skills 速率限制指导

- [x] 2.1 在 `_build_skills_section()` 中添加速率限制指导

## 3. 动态上下文文件处理

- [x] 3.1 从稳定上下文列表中移除 HEARTBEAT.md
- [x] 3.2 添加 `_build_dynamic_context_section()` 函数处理 HEARTBEAT.md
- [x] 3.3 修改 `build_system_prompt()` 将动态上下文放在 cache boundary 之后

## 4. 文档更新

- [x] 4.1 更新 DIFF.md 说明身份声明的改变

## 5. 验证

- [x] 5.1 运行 `ruff check` 验证代码风格
- [x] 5.2 运行 `ruff format` 格式化代码
- [x] 5.3 运行 `ty check` 验证类型
- [x] 5.4 验证 system prompt 输出包含所有修改
