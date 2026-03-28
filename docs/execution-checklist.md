# 执行检查清单

本文档用于当前结构下的持续开发与回归，不再按阶段拆分。

## 1. 开工前必须确认

1. 接口冻结稿已更新
2. 运行命令可用
3. `docs/test/` 结构完整
4. `skills/feishu-chat/SKILL.md` 与 action 对齐
5. 飞书联调凭证和权限已准备好

## 2. 当前必须稳定的内容

- `InvokeRequest`
- `ActionResult`
- `AuthContext`
- `get_tenant_access_token(auth_context)`
- `get_auth_headers(auth_context)`
- 6 个 `feishu-chat-*` action

## 3. 测试入口

- `python3 -m pytest`
- `python3 -m pytest docs/test`
- `python3 -m pytest docs/test/feishu-chat`

## 4. 结构约束

- 不恢复 `tests/` 旧目录
- 不恢复 `docs/phase-*` 目录
- 不恢复非 `feishu-chat` 的占位 service / skill
