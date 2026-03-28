# Skill: `feishu-chat-create`

## 1. Skill 目标

创建一个新的飞书群组，对应 action：`feishu.chat.create`。

## 2. 前置条件

- 第一阶段模块已实现：`core`、`auth`、`runtime`、`im_chat`
- 飞书应用已申请群组读写相关权限
- 调用方能够提供 `app_id`、`app_secret`
- 调用方能够直接提供 `user_id` 或 `open_id`

## 3. 输入参数

鉴权参数：

- `app_id`
- `app_secret`

必填参数：

- `name`
- `user_id_list`

可选参数：

- `owner_id`
- `chat_mode`
- `description`

参数约束：

- `user_id_list` 只接受飞书用户标识，不接受邮箱或手机号
- 第一阶段不做成员解析

## 4. 调用方式

OpenClaw 使用说明：

- 当用户明确要“建群”“创建讨论群”“拉这些人建个群”时使用

CLI 示例：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.create --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","name":"项目临时群","user_id_list":["ou_xxx","ou_yyy"]}'
```

## 5. 输出结果

成功输出建议包含：

- `chat_id`
- `name`
- `member_count`
- `owner_id`

## 6. 失败处理

常见错误：

- 缺少权限
- 成员 ID 非法
- 群名不合法

可执行修复动作：

- 核对应用权限
- 改为提供 `user_id` / `open_id`
- 调整群名称或成员列表

## 7. 示例场景

最小示例：

- “帮我建一个项目群，把 A 和 B 拉进去”

典型业务示例：

- 根据故障值班名单快速建一个临时处理群
