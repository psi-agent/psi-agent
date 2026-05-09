## session-tool-loader-testing

tool_loader 模块的 corner case 测试。

### parse_google_docstring

- 仅 Returns 无 Args 的文档字符串
- 仅 Args 无 Returns 的文档字符串
- 嵌套冒号（参数描述中含冒号，如 "host:port 格式"）
- 参数类型含方括号（如 "list[str]"）
- 空白行和多余空格
- Unicode 内容（中文描述）
- 空文档字符串
- 单行文档字符串（无 Args/Returns）
- Args 部分参数名和描述之间无空格

### python_type_to_openai_type

- "str" → "string"
- "int" → "integer"
- "float" → "number"
- "bool" → "boolean"
- "list" → "array"
- "dict" → "object"
- 未知类型 → "string"（默认值）
- 大写类型名 "List"、"Dict" → 对应 OpenAI 类型

### generate_tool_schema

- 无参数函数：parameters.properties 为空
- 所有参数有默认值：parameters.required 为空
- 混合必选和可选参数：required 只含必选参数
- 参数类型注解为复杂类型（Union、Optional）

### load_tool_from_file

- 空文件（无 tool 函数）
- 只有注释的文件
- tool 函数缺少类型注解
- tool 函数有复杂签名（*args, **kwargs）
