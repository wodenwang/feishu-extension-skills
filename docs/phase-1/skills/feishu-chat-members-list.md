# Skill 文档：`feishu-chat-members-list`

## 1. Skill 目标

查询指定飞书群组的成员列表，对应 action：`feishu.chat.members.list`。

## 2. 前置条件

- 第一阶段模块已实现：`core`、`auth`、`runtime`、`im_chat`
- 飞书应用已申请群组与成员读取权限
- 调用方已提供 `app_id`、`app_secret`
- 调用方已提供 `chat_id`

## 3. 输入参数

鉴权参数：

- `app_id`
- `app_secret`

必填参数：

- `chat_id`

可选参数：

- `page_size`
- `page_token`
- `member_id_type`

参数约束：

- `chat_id` 必须是飞书群组 ID
- `member_id_type` 默认值为 `user_id`

## 4. 调用方式

OpenClaw 使用说明：

- 当用户要“看群里都有谁”“列出群成员”“确认群成员名单”时使用

CLI 示例：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.members.list --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","chat_id":"oc_xxx"}'
```

## 5. 输出结果

成功输出建议包含：

- `chat_id`
- `items`
- `has_more`
- `page_token`

## 6. 失败处理

常见错误：

- `chat_id` 不存在
- 应用不在群内
- 缺少成员读取权限

可执行修复动作：

- 核对群 ID
- 确认应用是否有访问该群的权限

## 7. 示例场景

最小示例：

- “列一下这个群的成员”

典型业务示例：

- 核对故障处理群是否已拉齐值班成员
