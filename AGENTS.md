# AGENTS

本仓库进入执行阶段后，建议默认采用 agent teams 的方式推进。

目标不是“让多个 agent 同时改很多文件”，而是把任务拆成边界清晰、写集不重叠、可并行验证的工作流。

## 1. 当前项目状态

当前目标是完成第一阶段最小可运行系统：

- `core`
- `auth`
- `runtime`
- `services/im_chat`

第一阶段业务范围：

- 创建群组
- 查询群组详情
- 查询群成员
- 拉人入群
- 移出群组

调用约定：

- 调用 Skill / CLI 时直接传 `app_id` 与 `app_secret`
- `auth` 使用这组凭证获取并缓存 `tenant_access_token`
- 后续同一组凭证重复调用时复用缓存
- 环境变量只作为兜底，不作为唯一入口

## 2. 文档优先级

执行阶段以以下文档为准：

1. `AGENTS.md`
2. `docs/phase-1/README.md`
3. `docs/phase-1/execution-checklist.md`
4. `docs/phase-1/modules/*.md`
5. `docs/phase-1/skills/*.md`
6. `docs/phase-1/permissions.md`
7. `docs/feishu-server-api-plan.md`

若文档冲突：

- 第一阶段实现细节，以 `docs/phase-1/` 为准
- 协作方式，以 `AGENTS.md` 为准

## 3. 推荐 Team 拆分

建议至少使用 4 个 agent 角色：

### Agent 1：`lead`

职责：

- 拆解任务与安排并行顺序
- 控制模块边界与接口稳定性
- 审核各 agent 交付物
- 负责最终集成与验收

写入范围：

- `AGENTS.md`
- `README.md`
- 根级流程文档
- 最终集成时的跨模块修正

### Agent 2：`core-auth`

职责：

- 实现 `core`
- 实现 `auth`
- 提供通用配置、HTTP、错误、token 缓存

写入范围：

- `src/feishu_extension_skills/core/**`
- `src/feishu_extension_skills/auth/**`
- `tests/unit/core/**`
- `tests/unit/auth/**`

### Agent 3：`runtime-cli`

职责：

- 实现 CLI
- 实现 action dispatcher
- 定义统一请求/响应模型

写入范围：

- `src/feishu_extension_skills/runtime/**`
- `src/feishu_extension_skills/cli/**`
- `tests/unit/runtime/**`
- `tests/smoke/cli/**`

### Agent 4：`im-chat`

职责：

- 实现群组 API client
- 实现 `im_chat` service
- 实现 4 个 action handler

写入范围：

- `src/feishu_extension_skills/services/im_chat/**`
- `tests/unit/services/im_chat/**`

### 可选 Agent 5：`skills-docs`

职责：

- 创建或维护 `skills/**/SKILL.md`
- 保持 Skill 文案与 Python action 对齐
- 维护阶段文档中的调用示例

写入范围：

- `skills/**`
- `docs/phase-1/skills/**`

## 4. 并行策略

第一阶段建议按两个波次推进。

### 波次 1：底座先行

并行执行：

- `core-auth`
- `runtime-cli`

串行约束：

- `runtime-cli` 可先定义接口与模型，但最终联调要等 `auth` 输出稳定

交付物：

- 配置模型
- token manager
- CLI 主入口
- dispatcher 与统一 result 模型

### 波次 2：业务模块接入

并行执行：

- `im-chat`
- `skills-docs`

串行约束：

- `im-chat` 依赖 `auth` 的 token 接口与 `runtime` 的 action 注册方式稳定

交付物：

- `im_chat` client / service / actions
- 4 个 Skill 文档或实际 `SKILL.md`
- CLI 冒烟调用样例

## 5. 文件写入边界

使用 agent teams 时，必须尽量保持写集不重叠。

推荐边界：

- `core-auth` 不修改 `runtime/**` 与 `services/**`
- `runtime-cli` 不修改 `auth/**` 的内部实现
- `im-chat` 不修改 `core/**` 与 `auth/**` 的内部逻辑，只依赖公开接口
- `skills-docs` 不修改 Python 实现文件

允许的例外：

- `lead` 在最终集成阶段可做少量跨文件修正

## 6. 接口冻结点

开始并行编码前，先冻结以下接口：

- `InvokeRequest`
- `ActionResult`
- `AuthContext`
- `get_tenant_access_token(auth_context)`
- `get_auth_headers(auth_context)`
- `feishu.chat.create`
- `feishu.chat.members.list`
- `feishu.chat.member.add`
- `feishu.chat.member.remove`

未冻结前，不建议大规模并行写代码。

## 7. 交接格式

每个 agent 完成后，交付内容应至少包含：

- 修改了哪些文件
- 提供了哪些接口
- 依赖了哪些外部接口或配置
- 当前已完成测试
- 仍未解决的问题

推荐格式：

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

## 8. 第一阶段 Definition of Done

满足以下条件才能视为第一阶段完成：

- `python -m feishu_extension_skills.cli invoke <action> --args-json '<json>'` 可调用 4 个群组 action
- 支持调用时传 `app_id` / `app_secret`
- 同一组凭证重复调用可复用缓存 token
- `im_chat` 权限 JSON 已与文档一致
- 至少有单元测试覆盖 `auth`、`runtime`、`im_chat`
- 至少有 1 组 CLI 冒烟样例

## 9. 不建议的做法

- 不要让多个 agent 同时修改同一个模块目录
- 不要在接口未冻结前并行实现大量业务逻辑
- 不要把文档 agent 和代码 agent 混在同一写集里
- 不要在第一阶段提前引入 `contact`、消息发送、卡片交互

## 10. 下一阶段扩展建议

第一阶段稳定后，下一轮 agent teams 建议改成：

- Team A：`contact`
- Team B：`im`
- Team C：`card-static`
- Team D：`tests-and-skills`

原因：

- 这是第二阶段最适合并行推进的 3 个业务方向
- 写集天然可分离
- 价值高且复杂度仍可控
