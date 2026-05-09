## workspace-manifest-testing

manifest 模块的图操作、解析畸形输入和序列化往返一致性测试。

### Manifest 图操作

- 多层链解析：A → B → C，get_layer("C") 递归找到根层 A
- tag 查找不存在：find_by_tag("nonexistent") 返回 None
- get_all_tags：空 manifest 返回空列表；多层有 tag 返回全部
- default 层不存在于 layers 中：应报错或返回 None
- 同一 tag 出现在多个层：find_by_tag 返回第一个

### parse_manifest 畸形输入

- 空 JSON 字符串
- JSON 非 object（如数组、字符串、数字）
- layers 字段非 dict
- default 字段值不在 layers 中
- 层定义中 parent 指向不存在的 UUID
- 重复 tag
- 缺少 layers 字段
- 缺少 default 字段

### serialize_manifest 往返一致性

- parse → serialize → parse 结果一致
- 包含多层和 tag 的 manifest 往返一致