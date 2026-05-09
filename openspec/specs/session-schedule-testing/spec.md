## session-schedule-testing

schedule 模块的 frontmatter 解析 corner case 和 ScheduleExecutor 并发操作测试。

### parse_frontmatter

- 空 frontmatter（只有 ---\n---\n）
- 只有开头 --- 没有结尾 ---
- YAML 值含冒号（如 cron: "0 9 * * *"）
- 多行 content（--- 之后的多行文本）
- frontmatter 中有未知字段（应忽略）
- TASK.md 文件为空
- TASK.md 文件只有 content 没有 frontmatter
- frontmatter YAML 语法错误
- name 字段缺失但 cron 字段存在
- cron 字段缺失但 name 字段存在
- cron 值为空字符串

### Schedule

- get_next_run：缓存的 croniter 实例复用（多次调用应返回递增时间）
- get_next_run：cron 表达式无效时行为
- Schedule 构造：tag 为 None

### ScheduleExecutor

- add：添加同名 schedule（应覆盖）
- remove：移除不存在的 schedule（应无异常）
- update：更新不存在的 schedule
- add + remove + add 同一 schedule（生命周期测试）
- start/stop 幂等性
