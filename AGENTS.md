# AGENTS

本仓库默认按 agent teams 协作，但当前范围已经收敛为单一模块：`feishu-chat`。

目标不是并行扩很多预留能力，而是在清晰写集边界下维护这 4 个必要模块：

- `core`
- `auth`
- `runtime`
- `services/im_chat`

## 1. 当前目标

当前唯一业务范围：

- 创建群组
- 查询群组详情
- 查询群成员
- 拉人入群
- 移出群组
- 解散群组

调用约定：

- 调用 Skill / CLI 时直接传 `app_id` 与 `app_secret`
- `auth` 使用这组凭证获取并缓存 `tenant_access_token`
- 同一组凭证重复调用时复用缓存
- 环境变量只作为兜底，不作为唯一入口

## 2. 文档优先级

执行时以以下文档为准：

1. `AGENTS.md`
2. `docs/README.md`
3. `docs/execution-checklist.md`
4. `docs/modules/*.md`
5. `docs/skills/*.md`
6. `docs/permissions.md`
7. `docs/feishu-server-api-plan.md`

若文档冲突：

- 具体实现细节以 `docs/` 当前结构下的模块文档为准
- 协作方式以 `AGENTS.md` 为准

## 3. Skill 粒度

本项目按模块粒度维护 Skill，不按单个 action 过度拆分。

当前固定约定：

- `im_chat` 对应一个 Skill，ClawHub 发布 slug 为 `feishu-chat-server-api`
- Skill 内部覆盖多个 action
- action 保持细粒度，便于 runtime 分发、测试和后续扩展

## 4. 推荐 Team 拆分

### Agent 1：`lead`

职责：

- 拆任务
- 审核交付
- 负责最终集成
- 修改根文档和跨模块修正

写入范围：

- `AGENTS.md`
- `README.md`
- `docs/**`

### Agent 2：`core-auth`

职责：

- 维护 `core`
- 维护 `auth`
- 提供配置、HTTP、错误、token 缓存

写入范围：

- `src/feishu_extension_skills/core/**`
- `src/feishu_extension_skills/auth/**`
- `docs/test/core/**`
- `docs/test/auth/**`

### Agent 3：`runtime-cli`

职责：

- 维护 CLI
- 维护 action dispatcher
- 维护统一请求/响应模型

写入范围：

- `src/feishu_extension_skills/runtime/**`
- `src/feishu_extension_skills/cli/**`
- `docs/test/runtime/**`
- `docs/test/test_cli_invoke.py`

### Agent 4：`im-chat`

职责：

- 维护群组 API client
- 维护 `im_chat` service
- 维护 6 个 action handler

写入范围：

- `src/feishu_extension_skills/services/im_chat/**`
- `docs/test/feishu-chat/**`

## 5. 文件写入边界

- `core-auth` 不修改 `runtime/**` 与 `services/**`
- `runtime-cli` 不修改 `auth/**` 内部实现
- `im-chat` 不修改 `core/**` 与 `auth/**` 内部逻辑，只依赖公开接口
- `lead` 仅在最终集成阶段做少量跨文件修正

## 6. 接口冻结点

开始并行编码前，先冻结以下接口：

- `InvokeRequest`
- `ActionResult`
- `AuthContext`
- `get_tenant_access_token(auth_context)`
- `get_auth_headers(auth_context)`
- `feishu-chat-create`
- `feishu-chat-get`
- `feishu-chat-members-list`
- `feishu-chat-member-add`
- `feishu-chat-member-remove`
- `feishu-chat-disband`

## 7. 交接格式

```text
Changed files:
- path/a.py
- path/b.py

Public interfaces:
- foo(...)
- bar(...)

Verified:
- unit tests for ...

Open issues:
- ...
```

## 8. Definition of Done

满足以下条件可视为当前版本完成：

- `feishu-extension-skills invoke <action> --args-json '<json>'` 可调用 6 个群组 action
- 支持调用时传 `app_id` / `app_secret`
- 同一组凭证重复调用可复用缓存 token
- `im_chat` 权限 JSON 与文档一致
- 至少有单元测试覆盖 `auth`、`runtime`、`im_chat`
- 至少有 1 组 CLI 冒烟样例

## 9. 不建议的做法

- 不要恢复消息、文档、卡片、通讯录等预留空目录
- 不要让多个 agent 同时修改同一个模块目录
- 不要在接口未冻结前并行实现大量逻辑
- 不要把文档 agent 和代码 agent 混进同一写集
