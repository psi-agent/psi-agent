## Context

当前 CI 只运行测试，没有发布流程。需要添加自动发布到 PyPI 的功能，当创建 tag 时触发。

## Goals / Non-Goals

**Goals:**
- 当创建 tag 时自动构建并发布到 PyPI
- 使用 GitHub Trusted Publishing（无需管理 API token）

**Non-Goals:**
- 发布到 TestPyPI
- 支持 release candidate 或 pre-release 版本

## Decisions

### 使用 GitHub Trusted Publishing

**方案：** 使用 PyPI 的 Trusted Publishing 功能，通过 OIDC 认证，无需存储 API token。

**原因：**
- 更安全：无需管理长期有效的 API token
- GitHub Actions 原生支持
- 官方推荐的最佳实践

### 发布流程设计

**触发条件：** 当推送 tag（格式 `v*`）时触发

**步骤：**
1. 检出代码
2. 安装 uv
3. 构建包：`uv build`
4. 上传到 PyPI：`uv publish`（使用 trusted publishing）

## Risks / Trade-offs

- 需要在 PyPI 上配置 Trusted Publishing（一次性设置）
- 只支持正式版本，不支持 pre-release

## PyPI 配置步骤

1. 访问 https://pypi.org/manage/project/psi-agent/settings/publishing/
2. 添加新 publisher：
   - Owner: `psi-agent`
   - Repository: `psi-agent`
   - Workflow: `ci.yml`
   - Environment: `pypi`
3. 在 GitHub 仓库设置中创建 `pypi` environment（可选，用于限制部署分支）
