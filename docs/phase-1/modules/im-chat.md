# 模块文档：`im_chat`

## 1. 模块定位

`im_chat` 是第一阶段唯一的业务模块，负责群组与会话能力。

它属于第一阶段，因为它能在依赖最少的条件下做出第一套可用的飞书服务端 Skill，并且符合“优先补官方插件未覆盖或未独立封装能力”的目标。

## 2. 范围

In scope：

- 创建群组
- 查询群组详情
- 查询群成员
- 拉人入群
- 移出群组
- 解散群组

Out of scope：

- 群公告
- 群置顶
- 企业自定义群标签
- 与消息发送联动的自动欢迎逻辑
- 邮箱/手机号到用户 ID 的解析

## 3. 依赖关系

上游依赖：

- `core`
- `auth`
- `runtime`

下游调用方：

- 第一阶段 5 个群组 Skill

## 4. 代码结构规划

建议文件：

- `services/im_chat/models.py`
- `services/im_chat/client.py`
- `services/im_chat/service.py`
- `services/im_chat/actions.py`

文件职责：

- `models.py`：定义群组创建、成员列表、成员变更等模型
- `client.py`：直接请求飞书群组 API
- `service.py`：做 receive_id、member_id 列表等业务校验
- `actions.py`：把 service 暴露给 runtime

## 5. 核心数据模型

建议输入模型：

- `CreateChatInput`
- `ListChatMembersInput`
- `AddChatMembersInput`
- `RemoveChatMembersInput`

建议输出模型：

- `ChatSummary`
- `ChatMemberSummary`
- `ChatOperationResult`

建议最小输入约束：

- 第一阶段优先要求调用方传入 `app_id` 与 `app_secret`
- 第一阶段只接受 `user_id` 或 `open_id`
- 不做邮箱、手机号、姓名到用户 ID 的自动解析

## 6. 对外动作

action 列表：

- `feishu.chat.create`
- `feishu.chat.members.list`
- `feishu.chat.member.add`
- `feishu.chat.member.remove`
- `feishu.chat.delete`

CLI 示例：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.create --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","name":"项目临时群","user_id_list":["ou_xxx","ou_yyy"]}'
```

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.members.list --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","chat_id":"oc_xxx"}'
```

## 7. 飞书 API / 外部接口

主要接口：

- `im/v1/chats`
- `im/v1/chats/{chat_id}`
- `im/v1/chats/{chat_id}/members`

建议映射：

- 创建群组：`POST /open-apis/im/v1/chats`
- 查询群组：`GET /open-apis/im/v1/chats/{chat_id}`
- 查询成员：`GET /open-apis/im/v1/chats/{chat_id}/members`
- 拉人入群：`POST /open-apis/im/v1/chats/{chat_id}/members`
- 移出群组：`DELETE /open-apis/im/v1/chats/{chat_id}/members/{member_id}`
- 解散群组：`DELETE /open-apis/im/v1/chats/{chat_id}`

## 8. 权限与配置

飞书权限：

- 第一阶段最小权限集合如下：

```json
{
  "scopes": {
    "tenant": [
      "im:chat:read",
      "im:chat:write",
      "im:chat.members:read",
      "im:chat.members:write",
      "im:chat:delete"
    ],
    "user": []
  }
}
```

环境变量：

- 继承 `core` 与 `auth` 的公共配置

调用时凭证：

- `app_id`
- `app_secret`

## 9. 测试与验收

单元测试：

- 创建群组参数合法性校验
- 成员列表分页参数处理
- 加人/移人时的空列表与重复成员处理
- 解散群时的权限与群类型约束

冒烟测试：

- 成功创建测试群
- 成功查询测试群成员
- 成功向测试群加人、移人
- 成功解散测试群

验收标准：

- 5 个 action 都能通过 CLI 成功调用
- 常见飞书错误码能转成统一错误消息
- 不依赖 `contact` 也能完成完整链路

## 10. 后续扩展

- 第二阶段接入 `contact`，支持邮箱/手机号解析成员
- 第二阶段与 `im` 联动，支持建群后自动发第一条消息
- 第三阶段扩展群公告、群置顶、企业自定义群标签
