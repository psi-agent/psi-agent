## channel-telegram-testing

split_message 函数的完整边界测试。

### split_message

- 恰好等于 max_length 的消息（不分割）
- 只有空格/换行的消息
- Unicode 多字节字符在边界处（如 max_length=5 时消息含中文）
- max_length=1
- max_length=0（应报错或返回空列表）
- 空字符串
- 消息长度为 max_length + 1（分割为两段）
- 连续换行符
- 消息含 Markdown 格式（**bold**、`code`、[link](url)）