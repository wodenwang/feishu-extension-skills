# Skill 文档：`feishu-chat`

## 1. Skill 目标

当前唯一保留的模块级 skill 以 `feishu-chat-server-api` 作为 ClawHub 发布 slug，统一承载群组管理能力。

## 2. 覆盖 action

- `feishu-chat-create`
- `feishu-chat-get`
- `feishu-chat-members-list`
- `feishu-chat-member-add`
- `feishu-chat-member-remove`
- `feishu-chat-disband`

## 3. 输入约定

所有 action 都要求：

- `app_id`
- `app_secret`

按场景补充：

- 创建群：`name`、`user_id_list`
- 查群详情：`chat_id`
- 查群成员：`chat_id`
- 加人：`chat_id`、`user_id_list`
- 移人：`chat_id`、`member_id`
- 解散群：`chat_id`

## 4. 调用方式

```bash
feishu-extension-skills invoke <action> --args-json '<json>'
```

## 5. 当前不包含

- 更新群信息
- 群发言权限管理
- 群置顶管理
- 群列表 / 群搜索
- 群分享链接
