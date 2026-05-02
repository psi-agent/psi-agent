## REMOVED Requirements

### Requirement: Process title masking utility

**Reason**: 打码功能不可靠（存在时间窗口漏洞），增加代码复杂性，应通过环境变量传递敏感信息而非依赖打码。

**Migration**: 使用环境变量传递敏感信息，如 `API_KEY` 环境变量，而非命令行参数。

### Requirement: CLI entry points must mask sensitive arguments

**Reason**: 同上，删除 CLI 入口中的打码调用。

**Migration**: CLI 入口不再调用 `mask_sensitive_args`，用户应自行确保敏感信息的安全传递。