## Why

从功能角度审视现有测试，发现两个层面的问题：

1. **Happy path 缺失**（更严重）：多个核心模块的公共 API 完全没有测试，或关键成功路径未覆盖。这意味着基本功能正确性无法验证。
2. **Corner case / robustness 缺失**：已有测试多覆盖 happy path，但对边界条件（空输入、异常值、并发冲突、格式畸形等）和防御性编程路径的验证不足。

补充这些测试可确保核心组件在真实使用中不会因外部数据畸形或边界情况而崩溃，同时验证基本功能正确性。

## What Changes

### Happy Path 缺失（优先级高）

经逐模块核对源码与现有测试，确认以下 happy path 缺失：

- **session/types.py**（无测试文件）：`ToolSchema` 构造、`ToolRegistry` 的 register/get/unregister/list_tools/clear、`History` 的构造/add_message/clear 均无专门测试。这些是核心数据结构，所有其他模块依赖它们。
- **session/config.py**（无测试文件）：`SessionConfig` 的 6 个辅助方法（channel_socket_path、ai_socket_path、workspace_path、history_file_path、tools_dir、systems_dir）均无测试。路径拼接的正确性直接影响 socket 通信和文件定位。
- **session/runner.py**：
  - `_load_system()` 函数完全没有测试。该函数动态加载 System 类实例，是 System 接口（build_system_prompt + compact_history）的入口。
  - `_handle_workspace_changes` 中处理 schedule 变更的三个分支（schedules_added → add_schedule、schedules_modified → update_schedule、schedules_removed → remove_schedule）没有测试。现有测试只覆盖了 tools 和 skills 变更。
  - `_build_messages` 在有 System 实例时的 `compact_history` 路径没有测试。现有测试只覆盖了无 System 实例的路径。
- **session/schedule.py**：
  - `ScheduleExecutor._schedule_loop` 的正常执行路径（等待 → 执行 → 继续等待）没有测试。现有测试只覆盖了 start/stop/add/remove/update 的生命周期，未验证循环体内的正常执行。
  - `ScheduleExecutor._execute_task` 的正常成功路径没有测试（只测了错误路径 test_executor_handles_task_execution_error）。
- **channel/cli/client.py**：`CliClient._send_non_streaming` 和 `_send_streaming` 的实际 HTTP 交互成功路径没有测试。现有测试（test_cli.py）只测了 send_message 在无 context 时抛异常；test_cli_integration.py 通过 mock send_message 测试了上层 Cli._run，但没有测试 CliClient 内部的 HTTP 请求/响应解析逻辑（JSON 解析、choices 提取、SSE 流解析）。

以下模块经核对后 happy path 已基本覆盖，不需要补充：

- **channel/repl/repl.py**：`Repl.run()` 已有完整测试（流式/非流式、EOF、KeyboardInterrupt、空输入、历史持久化、_send_and_display 路径）。
- **channel/telegram/bot.py**：`_handle_message`、`_handle_message_non_streaming`、`_handle_message_streaming`、`_mask_proxy_credentials`、`start()` 均已有大量测试（test_bot_streaming.py 有 1500+ 行）。

### Corner Case / Robustness 缺失

- **session/types.py**: 补充 ToolRegistry 和 History 的完整单元测试（重复注册、注销不存在工具、list_tools 空注册表、History 大量消息等）
- **session/config.py**: 补充 SessionConfig 所有辅助方法的测试（history_file_path None/非None、tools_dir/systems_dir 路径拼接）
- **session/tool_loader.py**: 补充 parse_google_docstring 的 corner case（仅 Returns 无 Args、嵌套冒号、空白行、Unicode 内容）；python_type_to_openai_type 未覆盖类型（List、Dict 大写）；generate_tool_schema 边界（无参数函数、所有参数有默认值）；load_tool_from_file 更多异常路径（空文件、只有注释的文件）
- **session/tool_executor.py**: 补充 execute_tool 的更多异常类型（TypeError 参数不匹配）；execute_tools_parallel 空 tool_calls 列表、tool_call 缺少 function/id 字段
- **session/workspace_watcher.py**: 补充 WorkspaceWatcher 的复合变更场景（同时新增+修改+删除）、initialize 空 workspace、连续多次 check_for_changes 的幂等性、scan 函数对非目录条目的处理
- **session/history.py**: 补充 load_history_from_file 非 JSON 数组内容、超大历史文件；save_history_to_file 原子性；initialize_history 路径含特殊字符
- **session/schedule.py**: 补充 parse_frontmatter 的 corner case（空 frontmatter、只有 --- 没有内容、YAML 值含冒号、多行 content）；Schedule.get_next_run 缓存的 croniter 实例复用；ScheduleExecutor 并发 add/remove/update
- **session/server.py**: 补充 _filter_for_channel 的更多边界（无 choices、无 message、content 为空字符串）；_handle_chat_completions 更多畸形请求（stream=True 但 runner 未初始化、messages 中多条 user 消息只取最后一条）
- **session/runner.py**: 补充 _reconstruct_tool_calls 的更多边界（空列表、index 不连续、超大 index）；_parse_streaming_response 的更多畸形 SSE（超长行、非 UTF-8 字节、连续多个 error chunk）；format_thinking_block/format_tool_call_thinking 空内容
- **workspace/manifest.py**: 补充 Manifest 的图操作测试（多层链解析、循环引用检测、tag 查找不存在、get_all_tags 空 manifest）；parse_manifest 更多畸形输入（空 JSON、非 object、layers 非 dict、default 不在 layers 中、重复 tag）；serialize_manifest 往返一致性
- **channel/telegram/bot.py**: 补充 split_message 的更多边界（恰好等于 max_length、只有空格/换行、Unicode 多字节字符在边界处、max_length=1）
- **ai/anthropic_messages/translator.py**: 补充 _translate_message_to_anthropic 的更多边界（content 为 None、content 为数字、空 tool_calls 数组、arguments 非法 JSON）；translate_openai_to_anthropic 多 system 消息只取第一条；translate_anthropic_to_openai 空 content blocks、未知 stop_reason

## Capabilities

### New Capabilities
- `session-types-testing`: ToolRegistry 和 History 数据结构的完整单元测试，覆盖所有公共方法的正常行为和边界条件
- `session-config-testing`: SessionConfig 辅助方法的完整测试
- `session-tool-loader-testing`: tool_loader 模块的 corner case 测试，包括 docstring 解析、类型映射、schema 生成、动态加载异常路径
- `session-tool-executor-testing`: tool_executor 模块的 robustness 测试，包括参数不匹配、空调用列表、畸形 tool_call 结构
- `session-workspace-watcher-testing`: workspace_watcher 的复合变更和幂等性测试
- `session-history-testing`: history 模块的边界条件测试，包括畸形 JSON、特殊路径、大文件
- `session-schedule-testing`: schedule 模块的 frontmatter 解析 corner case 和 ScheduleExecutor 正常路径及并发操作测试
- `session-server-testing`: server 模块的请求处理边界和响应过滤测试
- `session-runner-testing`: runner 模块的流式解析边界、tool call 重构、_load_system 和 schedule 变更处理测试
- `workspace-manifest-testing`: manifest 模块的图操作、解析畸形输入和序列化往返一致性测试
- `channel-telegram-testing`: split_message 函数的完整边界测试
- `channel-cli-testing`: CliClient 的 _send_non_streaming 和 _send_streaming HTTP 交互成功路径测试
- `anthropic-translator-testing`: translator 模块的消息转换边界和畸形数据测试

### Modified Capabilities

## Impact

- 仅新增测试文件和测试用例，不修改任何生产代码
- 新增约 12 个测试文件/测试类，覆盖约 120+ 个新测试用例
- 不影响现有测试，所有新测试独立于现有测试
- 依赖 pytest 和 pytest-asyncio（已有）
