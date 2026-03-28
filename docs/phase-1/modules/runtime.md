# 模块文档：`runtime`

## 1. 模块定位

`runtime` 是第一阶段统一调用层，负责把 Skill 或 CLI 输入转成标准 action 调用。

在第一阶段里，`runtime` 还负责接收调用时传入的 `app_id` / `app_secret`，并把它们传递给 `auth` 与业务模块。

它属于第一阶段，因为没有统一运行时，后续每个 Skill 都会各自定义参数解析和错误输出。

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
- 权限自动探测

## 3. 依赖关系

上游依赖：

- `core/result.py`
- `core/errors.py`

下游调用方：

- CLI
- 后续 Skill

依赖的业务模块：

- `services/im_chat/actions.py`

## 4. 代码结构规划

建议文件：

- `runtime/actions.py`
- `runtime/dispatcher.py`
- `runtime/models.py`
- `runtime/validators.py`

文件职责：

- `actions.py`：维护 action 名称常量
- `dispatcher.py`：action 到 handler 的注册与调用
- `models.py`：定义统一请求模型
- `validators.py`：做轻量参数校验与默认值处理

## 5. 核心数据模型

建议数据模型：

- `InvokeRequest`
- `InvokeResponse`
- `RegisteredAction`
- `AuthArgs`

第一阶段 action 列表：

- `feishu.chat.create`
- `feishu.chat.members.list`
- `feishu.chat.member.add`
- `feishu.chat.member.remove`
- `feishu.chat.delete`

## 6. 对外动作

统一命令：

```bash
python -m feishu_extension_skills.cli invoke <action> --args-json '<json>'
```

第一阶段示例：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.members.list --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","chat_id":"oc_xxx"}'
```

## 7. 飞书 API / 外部接口

`runtime` 不直接调用飞书 API。

## 8. 权限与配置

飞书权限：

```json
{
  "scopes": {
    "tenant": [],
    "user": []
  }
}
```

环境变量：

- 继承 `core` 与 `auth` 的配置

调用时凭证：

- `app_id`
- `app_secret`

建议规则：

- 每个第一阶段 action 都允许在 `args_json` 中直接传 `app_id` / `app_secret`
- 若未传，则回退到环境变量

## 9. 测试与验收

单元测试：

- 非法 action 名称能正确报错
- JSON 参数缺失时返回统一错误
- handler 返回值能被统一包装

冒烟测试：

- 通过 CLI 成功执行一个真实 action

验收标准：

- 所有 Skill 都只能通过统一 CLI 入口触发

## 10. 后续扩展

- 事件分发入口
- action 元数据注册
- 更细粒度的 schema 校验
