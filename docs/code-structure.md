# 代码结构规划

## 1. 目标

当前结构只服务于 `feishu-chat` 最小可运行系统：

- 保持目录尽可能小，避免预留空壳模块
- 让 `core`、`auth`、`runtime`、`im_chat` 的职责边界稳定

## 2. 源码目录

```text
src/feishu_extension_skills/
├── auth/
├── cli/
├── core/
├── runtime/
└── services/
    └── im_chat/
```

## 3. 测试目录

测试用例统一放到 `docs/test/`：

```text
docs/test/
├── auth/
├── core/
├── runtime/
├── feishu-chat/
├── conftest.py
├── test_cli_invoke.py
└── report/
```

约定：

- 模块单测放到对应目录，例如 `docs/test/feishu-chat/`
- 跨模块 CLI / 集成测试放在 `docs/test/` 根下
- 测试报告和联调证据放在 `docs/test/report/`

## 4. Skill 目录

```text
skills/
└── feishu-chat-server-api/
    └── SKILL.md
```

当前不保留任何消息、文档、卡片、通讯录等占位 Skill。

## 5. Action 列表

- `feishu-chat-create`
- `feishu-chat-get`
- `feishu-chat-members-list`
- `feishu-chat-member-add`
- `feishu-chat-member-remove`
- `feishu-chat-disband`
