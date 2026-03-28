# feishu-extension-skills

面向 OpenClaw / ClawHub 的飞书扩展 Skill 项目。

当前仓库已经收敛为单一交付目标：飞书群组 Skill。代码层只保留群组能力及其必要依赖模块 `core`、`auth`、`runtime`、`services/im_chat`；文档和测试目录也同步改为围绕这一条主线组织。

## 当前范围

已实现并保留的 action：

- `feishu-chat-create`
- `feishu-chat-get`
- `feishu-chat-members-list`
- `feishu-chat-member-add`
- `feishu-chat-member-remove`
- `feishu-chat-disband`

当前不再保留消息、文档、卡片、通讯录等预留目录或占位 Skill。

## 文档导航

- 总体文档索引：[docs/README.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/README.md)
- 接口冻结：[docs/interface-freeze.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/interface-freeze.md)
- 权限汇总：[docs/permissions.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/permissions.md)
- 协作规范：[AGENTS.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/AGENTS.md)

## 目录结构

```text
.
├── AGENTS.md
├── README.md
├── docs/
│   ├── modules/
│   ├── skills/
│   ├── test/
│   │   ├── auth/
│   │   ├── core/
│   │   ├── runtime/
│   │   ├── feishu-chat/
│   │   └── report/
│   └── templates/
├── skills/
│   └── feishu-chat-server-api/
└── src/
    └── feishu_extension_skills/
        ├── auth/
        ├── cli/
        ├── core/
        ├── runtime/
        └── services/
            └── im_chat/
```

## 开发命令

```bash
python3 -m pip install -e '.[dev]'
python3 -m pytest
feishu-extension-skills invoke <action> --args-json '<json>'
```

## Skill 发布

当前只发布一个模块级 Skill：

- 目录：`skills/feishu-chat-server-api/`
- ClawHub slug：`feishu-chat-server-api`

推荐发布命令：

```bash
./scripts/publish_clawhub.sh
```

首次或手动指定版本时：

```bash
./scripts/publish_clawhub.sh 0.1.0 "Initial ClawHub release"
```

运行时统一通过 `feishu-extension-skills invoke <action> --args-json '<json>'` 调用。
