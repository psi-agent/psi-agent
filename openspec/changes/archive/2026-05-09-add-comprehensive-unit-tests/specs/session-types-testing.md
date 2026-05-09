## session-types-testing

ToolRegistry 和 History 数据结构的完整单元测试。

### ToolRegistry

- `register`: 正常注册、重复注册同名工具（应覆盖还是报错？验证实际行为）、注册后 is_registered 返回 True
- `unregister`: 正常注销、注销不存在的工具（应无异常）、注销后 is_registered 返回 False
- `get`: 获取已注册工具、获取未注册工具（返回 None 或抛异常？验证实际行为）
- `list_tools`: 空注册表返回空列表、注册多个工具后返回全部
- `get_all_schemas`: 空注册表返回空列表、注册后返回对应 schemas

### History

- 构造：空列表、单条消息、多条消息
- `add_message`: 添加 user/assistant/system/tool 消息、验证消息结构
- `get_messages`: 返回所有消息、返回副本（修改返回值不影响内部）
- `clear`: 清空后 get_messages 返回空列表
