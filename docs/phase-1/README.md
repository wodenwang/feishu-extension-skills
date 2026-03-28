# 第一阶段实施文档索引

本文档集只覆盖第一阶段：`core`、`auth`、`runtime`、`im_chat`。

目标是先做出“群组模块最小可运行系统”，不把消息发送、通讯录解析、卡片交互等能力提前拉进来。

## 文档阅读顺序

1. [总体说明](./README.md)
2. [代码结构规划](./code-structure.md)
3. [执行前检查清单](./execution-checklist.md)
4. [阶段权限汇总](./permissions.md)
5. [模块模板](./module-template.md)
6. [Skill 模板](./skill-template.md)
7. [模块文档：core](./modules/core.md)
8. [模块文档：auth](./modules/auth.md)
9. [模块文档：runtime](./modules/runtime.md)
10. [模块文档：im_chat](./modules/im-chat.md)
11. [Skill 文档：chat-create](./skills/feishu-chat-create.md)
12. [Skill 文档：chat-members-list](./skills/feishu-chat-members-list.md)
13. [Skill 文档：chat-member-add](./skills/feishu-chat-member-add.md)
14. [Skill 文档：chat-member-remove](./skills/feishu-chat-member-remove.md)
15. [Skill 文档：chat-delete](./skills/feishu-chat-delete.md)
16. [UAT 用例与报告骨架](./uat-test-cases.md)
17. [UAT 报告（2026-03-28）](./uat-report-2026-03-28.md)
18. [第二轮回归检查单](./uat-regression-round2.md)
19. [第二轮回归报告（2026-03-28）](./uat-report-2026-03-28-r2.md)

## 第一阶段范围

包含：

- 公共配置、日志、错误处理、HTTP 适配
- 调用时传入 `app_id` / `app_secret` 的应用级鉴权与 `tenant_access_token` 缓存
- 统一 CLI 与 action 分发
- 群组创建、查详情、查成员、加人、移人、解散

不包含：

- 邮箱/手机号换取用户 ID
- 文本消息发送与回复
- 卡片发送与交互回调
- 群公告、群置顶、企业自定义群标签

## 目录约定

第一阶段执行默认采用以下目录：

```text
src/feishu_extension_skills/
├── auth/
├── cli/
├── core/
├── runtime/
└── services/
    └── im_chat/
```

```text
tests/
├── unit/
│   ├── auth/
│   ├── core/
│   ├── runtime/
│   └── services/
│       └── im_chat/
└── smoke/
    └── cli/
```

## 调用约定

第一阶段统一命令：

```bash
python -m feishu_extension_skills.cli invoke <action> --args-json '<json>'
```

第一阶段鉴权约定：

- 优先在调用时传 `app_id` 与 `app_secret`
- `auth` 负责获取并缓存 `tenant_access_token`
- 环境变量只作为兜底

## 第一阶段交付标准

- 所有 action 都能通过统一 CLI 调用
- `im_chat` 的 5 个 Skill 有明确输入输出和错误约定
- 同一组 `app_id` / `app_secret` 的重复调用可复用缓存 token
- 阶段权限汇总文档和各模块文档中的权限 JSON 都可用于核对与复制
- 模块文档与 Skill 文档均使用统一模板
