# 模块文档：`runtime`

## 1. 模块定位

`runtime` 是统一调用层，负责把 Skill 或 CLI 输入转成标准 action 调用。

## 2. 范围

In scope：

- action 注册
- 请求参数反序列化
- 基础参数校验
- 鉴权参数透传
- action 分发
- 统一输出格式

Out of scope：

- 事件回调系统
- 复杂工作流编排

## 3. 依赖关系

上游依赖：

- `core/result.py`
- `core/errors.py`

依赖的业务模块：

- `services/im_chat/actions.py`

## 4. 代码结构

- `runtime/actions.py`
- `runtime/dispatcher.py`
- `runtime/models.py`
- `runtime/validators.py`

## 5. 当前 action

- `feishu-chat-create`
- `feishu-chat-get`
- `feishu-chat-members-list`
- `feishu-chat-member-add`
- `feishu-chat-member-remove`
- `feishu-chat-disband`

## 6. 测试

对应测试目录：

- `docs/test/runtime/`
- `docs/test/test_cli_invoke.py`
