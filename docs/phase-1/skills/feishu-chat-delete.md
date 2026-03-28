# Skill 文档：`feishu-chat-delete`

## 1. Skill 目标

解散指定飞书群组，对应 action：`feishu.chat.delete`。

## 2. 前置条件

- 第一阶段模块已实现：`core`、`auth`、`runtime`、`im_chat`
- 飞书应用已开启机器人能力
- 飞书应用已申请群组解散相关权限
- 调用方已提供 `app_id`、`app_secret`
- 调用方已提供可解散的 `chat_id`

## 3. 输入参数

鉴权参数：

- `app_id`
- `app_secret`

必填参数：

- `chat_id`

可选参数：

- `base_url`

参数约束：

- 仅支持群模式为 `group` 的群组 ID
- 调用者必须是群主，或者是满足权限要求的群创建者/机器人
- 第一阶段不做群类型自动探测与权限自动修复

## 4. 调用方式

OpenClaw 使用说明：

- 当用户明确要“解散这个群”“删掉这个测试群”“收尾清理群组”时使用

CLI 示例：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.delete --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","chat_id":"oc_xxx"}'
```

## 5. 输出结果

成功输出建议包含：

- `chat_id`
- `status`

## 6. 失败处理

常见错误：

- `chat_id` 非法
- 调用者不是群主/创建者
- 机器人能力未开启
- 群类型不支持

可执行修复动作：

- 核对 `chat_id`
- 确认应用是否具备解散群权限
- 确认当前操作者是否满足群主或创建者要求
- 确认目标群是否为 `group` 类型

## 7. 示例场景

最小示例：

- “把这个测试群解散掉”

典型业务示例：

- 第一阶段 UAT 收尾时清理临时测试群
