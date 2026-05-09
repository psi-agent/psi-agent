## session-history-testing

history 模块的边界条件测试。

### load_history_from_file

- 非 JSON 数组内容（如 JSON object、JSON string、JSON number）
- 超大历史文件（大量消息）
- 文件内容为空字符串
- 文件内容为 "null"
- 文件内容为合法 JSON 但不是 list（如 dict）

### save_history_to_file

- 消息中含非 ASCII 字符（ensure_ascii=False 应保留）
- 消息中含特殊 JSON 字符（换行、引号）
- 空消息列表保存后为 "[]"

### initialize_history

- history_file 为 None（内存模式）
- history_file 路径不存在（应创建新文件）
- history_file 路径含特殊字符

### persist_history

- history_file 为 None（不写入）
- 正常写入后文件内容可被 load_history_from_file 正确读取（往返一致性）