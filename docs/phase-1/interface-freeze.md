# 第一阶段接口冻结

本文档是第一阶段进入 agent teams 编码前的接口冻结稿。

冻结目标：

- 让 `core-auth`、`runtime-cli`、`im-chat` 在统一契约上并行实现
- 明确第一阶段技术路线，避免同时出现 SDK 风格与原始 HTTP 风格两套实现
- 明确 CLI、鉴权、业务 action 的最小公共模型

## 1. 实现路线

第一阶段主实现固定为：

- HTTP 客户端：`httpx`
- 数据模型：`pydantic`
- CLI：`typer`
- 测试：`pytest`

说明：

- 第一阶段不引入飞书官方 Python SDK 作为主实现。
- `core/http.py` 统一封装 `httpx` 调用。
- 后续如需 SDK fallback，再在第二阶段或后续阶段补充。

## 2. 动作清单

第一阶段注册并支持以下 action：

- `feishu.chat.create`
- `feishu.chat.members.list`
- `feishu.chat.member.add`
- `feishu.chat.member.remove`
- `feishu.chat.delete`

说明：

- 群详情查询由 `im_chat` service/client 提供内部接口，供 `create`/成员操作返回结果复用。
- 第一阶段 CLI 对外验收要求上述 5 个 action。

## 3. `AuthContext`

```python
class AuthContext(BaseModel):
    app_id: str | None = None
    app_secret: str | None = None
    base_url: str = "https://open.feishu.cn"
```

规则：

- 优先使用调用参数里的 `app_id` / `app_secret`
- 缺失时回退环境变量 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`
- 若两者都缺失，抛配置错误
- token 缓存键为 `(base_url, app_id)`

## 4. `InvokeRequest`

```python
class InvokeRequest(BaseModel):
    action: str
    args: dict[str, Any] = Field(default_factory=dict)
```

说明：

- CLI 只做 `action` 与 `args_json` 的解析
- `runtime` 负责把 `args` 中的鉴权字段和业务字段一并传给对应 handler

## 5. `ActionResult`

```python
class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class ActionResult(BaseModel):
    ok: bool
    action: str
    data: dict[str, Any] | None = None
    error: ErrorPayload | None = None
```

规则：

- 成功时 `ok=true`、`error=null`
- 失败时 `ok=false`、`data=null`
- CLI 默认输出 `ActionResult.model_dump_json(indent=2)`

## 6. 鉴权接口

固定暴露以下接口：

- `get_tenant_access_token(auth_context) -> str`
- `get_auth_headers(auth_context) -> dict[str, str]`

行为要求：

- `get_tenant_access_token` 负责缓存命中、过期判断、刷新
- `get_auth_headers` 返回 `{"Authorization": "Bearer <token>"}`
- 刷新提前量由 `FEISHU_TOKEN_REFRESH_SKEW_SECONDS` 控制，默认 `60`

## 7. `im_chat` 输入与动作契约

### `feishu.chat.create`

必填：

- `app_id`
- `app_secret`
- `name`
- `user_id_list`

可选：

- `owner_id`
- `description`
- `chat_mode`

### `feishu.chat.members.list`

必填：

- `app_id`
- `app_secret`
- `chat_id`

可选：

- `page_size`
- `page_token`
- `member_id_type`

### `feishu.chat.member.add`

必填：

- `app_id`
- `app_secret`
- `chat_id`
- `user_id_list`

可选：

- `member_id_type`

### `feishu.chat.member.remove`

必填：

- `app_id`
- `app_secret`
- `chat_id`
- `member_id`

可选：

- `member_id_type`

### `feishu.chat.delete`

必填：

- `app_id`
- `app_secret`
- `chat_id`

统一规则：

- 第一阶段只接受飞书标识 `user_id` 或 `open_id`
- 不做邮箱、手机号解析
- `member_id_type` 默认 `user_id`

## 8. 错误模型

第一阶段统一错误码：

- `config_error`
- `validation_error`
- `action_not_found`
- `feishu_api_error`
- `http_error`
- `internal_error`

保留字段：

- `message`
- `details`

其中远端飞书错误需尽量保留：

- `code`
- `msg`
- `request_id`

## 9. HTTP 约定

认证接口：

- `POST /open-apis/auth/v3/tenant_access_token/internal`

群组接口：

- `POST /open-apis/im/v1/chats`
- `GET /open-apis/im/v1/chats/{chat_id}`
- `GET /open-apis/im/v1/chats/{chat_id}/members`
- `POST /open-apis/im/v1/chats/{chat_id}/members`
- `DELETE /open-apis/im/v1/chats/{chat_id}/members/{member_id}`
- `DELETE /open-apis/im/v1/chats/{chat_id}`

说明：

- 第一阶段不单独请求 `app_access_token`
- 直接使用 `tenant_access_token/internal` 换取 tenant token

## 10. 测试入口

统一命令：

```bash
python -m pytest
python -m pytest tests/unit
python -m pytest tests/smoke/cli
python -m feishu_extension_skills.cli invoke <action> --args-json '<json>'
```
