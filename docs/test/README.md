# 测试目录说明

`docs/test/` 按 3 层组织：

## 1. 自动化单测

- `docs/test/core/`
- `docs/test/auth/`
- `docs/test/runtime/`
- `docs/test/feishu-chat/`

这些目录只放可由 `pytest` 直接运行的自动化测试。

## 2. 跨模块 CLI / 集成测试

- `docs/test/test_cli_invoke.py`

这类用例覆盖 CLI 入口、dispatcher 和统一输出，不归到单一模块目录。

## 3. 真实联调 UAT 与证据

- `docs/test/report/uat-test-cases.md`
- `docs/test/report/uat-report-*.md`
- `docs/test/report/artifacts/`

这里放人工或半人工执行的 testcase、报告和证据，不与自动化单测混放。

## 4. 当前 testcase 约定

- 自动化单测：验证模型、校验、错误处理、action 分发
- CLI 集成测试：验证统一入口和结果包装
- UAT：验证真实飞书环境下的建群、查群、查成员、加人、移人、解散、token 复用和失败语义
