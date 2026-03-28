# Skill: `feishu-chat-member-add`

## 1. Skill 目标

向已有飞书群组中添加成员，对应 action：`feishu.chat.member.add`。

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
- `user_id_list`

可选参数：

- `member_id_type`

参数约束：

- 第一阶段默认只接受 `user_id` 或 `open_id`
- 不支持邮箱、手机号自动换 ID
- `member_id_type` 默认值为 `user_id`

## 4. 调用方式

OpenClaw 使用说明：

- 当用户要“把某些人拉进群”“补齐这个群成员”时使用

CLI 示例：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.member.add --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","chat_id":"oc_xxx","user_id_list":["ou_xxx","ou_yyy"]}'
```

## 5. 输出结果

成功输出建议包含：

- `chat_id`
- `added_member_ids`
- `failed_member_ids`

## 6. 失败处理

常见错误：

- 成员已在群内
- 成员 ID 非法
- 缺少成员写权限

可执行修复动作：

- 过滤已在群内的成员
- 改用合法 `user_id` / `open_id`
- 核对应用权限

## 7. 示例场景

最小示例：

- “把这两个人拉进这个群”

典型业务示例：

- 项目扩组时批量把新增成员加入项目群
