## Context

当前 CI workflow (`ci.yml`) 已配置 pytest-cov 进行覆盖率检查：
- 运行 `pytest --cov=src/psi_agent --cov-fail-under=60`
- 覆盖率低于 60% 会导致 CI 失败
- 报告仅在 CI 日志中可见，PR 中无可视化展示

## Goals / Non-Goals

**Goals:**
- 在 PR 中显示覆盖率变化（增加/减少百分比）
- 上传覆盖率报告到 Codecov 服务
- 添加分支覆盖率支持
- 由 Codecov 管理覆盖率门槛（移除本地阈值检查）

**Non-Goals:**
- 不添加覆盖率徽章到 README
- 不配置 Codecov YAML 高级设置（如 coverage gates）

## Decisions

### 1. 使用官方 Codecov Action

**选择**: `codecov/codecov-action@v5`

**理由**:
- 官方维护，与 GitHub Actions 集成良好
- 支持自动检测报告格式
- 公开仓库无需 token，私有仓库支持 `CODECOV_TOKEN`

**替代方案**:
- `codecov/codecov-action@v4` - 旧版本，已弃用
- 直接 curl 上传 - 需要手动处理认证，不推荐

### 2. 报告格式选择 XML (Cobertura)

**选择**: 生成 `coverage.xml` (Cobertura 格式)

**理由**:
- pytest-cov 原生支持：`--cov-report=xml`
- Codecov 完美支持此格式
- 行业标准格式

**替代方案**:
- JSON 格式 - 需要额外配置
- HTML 格式 - 不适合 CI 上传

### 3. Token 配置策略

**选择**: 使用 `CODECOV_TOKEN` secret 进行认证

**理由**:
- Codecov 官方推荐配置
- 更可靠的上传认证
- 支持公开和私有仓库

**配置**:
- 在 GitHub 仓库 Settings → Secrets 中添加 `CODECOV_TOKEN`
- 在 action 中配置 `token: ${{ secrets.CODECOV_TOKEN }}`
- 配置 `slug: psi-agent/psi-agent` 标识仓库

## Risks / Trade-offs

**风险**: Codecov 服务可能暂时不可用
→ **缓解**: Codecov action 默认配置不会阻塞 CI