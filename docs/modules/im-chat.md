# 模块文档：`im_chat`

## 1. 模块定位

`im_chat` 是当前唯一保留的业务模块，负责飞书群组能力。

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
- 邮箱/手机号到用户 ID 的解析
- 与消息发送联动的欢迎逻辑

## 3. 依赖关系

上游依赖：

- `core`
- `auth`
- `runtime`

下游调用方：

- `skills/feishu-chat-server-api/`

## 4. 代码结构

- `services/im_chat/models.py`
- `services/im_chat/client.py`
- `services/im_chat/service.py`
- `services/im_chat/actions.py`

## 5. 对外动作

- `feishu-chat-create`
- `feishu-chat-get`
- `feishu-chat-members-list`
- `feishu-chat-member-add`
- `feishu-chat-member-remove`
- `feishu-chat-disband`

## 6. 测试

对应测试目录：

- `docs/test/feishu-chat/`

CLI / 集成测试：

- `docs/test/test_cli_invoke.py`
