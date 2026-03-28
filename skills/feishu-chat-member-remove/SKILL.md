# Skill: `feishu-chat-member-remove`

## 1. Skill 目标

将成员从已有飞书群组中移出，对应 action：`feishu.chat.member.remove`。

## 2. 前置条件

- 第一阶段模块已实现：`core`、`auth`、`runtime`、`im_chat`
- 飞书应用已申请群组成员写权限
- 调用方已提供 `app_id`、`app_secret`
- 调用方已提供 `chat_id` 和成员 ID

## 3. 输入参数

鉴权参数：

- `app_id`
- `app_secret`

必填参数：

- `chat_id`
- `member_id`

可选参数：

- `member_id_type`

参数约束：

- 第一阶段按单成员移出设计，避免一次调用承担复杂批处理逻辑
- `member_id_type` 默认值为 `user_id`

## 4. 调用方式

OpenClaw 使用说明：

- 当用户要“把某个人移出群”“清理群成员”时使用

CLI 示例：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.member.remove --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","chat_id":"oc_xxx","member_id":"ou_xxx"}'
```

## 5. 输出结果

成功输出建议包含：

- `chat_id`
- `removed_member_id`
- `status`

## 6. 失败处理

常见错误：

- 成员不在群内
- 缺少成员写权限
- 群 ID 或成员 ID 非法

可执行修复动作：

- 先查询群成员，再决定是否移除
- 核对权限与输入 ID

## 7. 示例场景

最小示例：

- “把这个人从群里移出去”

典型业务示例：

- 故障结束后清理临时群中的外部协作成员
