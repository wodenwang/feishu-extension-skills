# 文档索引

本文档集只覆盖当前保留范围：`core`、`auth`、`runtime`、`im_chat` 与模块级 Skill `feishu-chat-server-api`。

## 阅读顺序

1. [代码结构](./code-structure.md)
2. [执行检查清单](./execution-checklist.md)
3. [接口冻结](./interface-freeze.md)
4. [权限汇总](./permissions.md)
5. [模块文档：core](./modules/core.md)
6. [模块文档：auth](./modules/auth.md)
7. [模块文档：runtime](./modules/runtime.md)
8. [模块文档：im_chat](./modules/im-chat.md)
9. [Skill 文档：feishu-chat](./skills/feishu-chat.md)
10. [测试目录说明](./test/README.md)
11. [测试报告目录](./test/report/)

## 当前目录约定

```text
docs/
├── modules/
├── skills/
├── test/
│   ├── auth/
│   ├── core/
│   ├── runtime/
│   ├── feishu-chat/
│   └── report/
└── templates/
```

## 调用约定

统一命令：

```bash
feishu-extension-skills invoke <action> --args-json '<json>'
```

鉴权约定：

- 优先在调用时传 `app_id` 与 `app_secret`
- `auth` 负责获取并缓存 `tenant_access_token`
- 环境变量只作为兜底
