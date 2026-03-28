# 接口冻结

本文档定义当前版本的稳定接口。

## 1. 实现路线

- HTTP 客户端：`httpx`
- 数据模型：`pydantic`
- CLI：`typer`
- 测试：`pytest`

当前不引入飞书官方 Python SDK 作为主实现。

## 2. Action 清单

- `feishu-chat-create`
- `feishu-chat-get`
- `feishu-chat-members-list`
- `feishu-chat-member-add`
- `feishu-chat-member-remove`
- `feishu-chat-disband`

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
- token 缓存键为 `(base_url, app_id)`

## 4. `InvokeRequest`

```python
class InvokeRequest(BaseModel):
    action: str
    args: dict[str, Any] = Field(default_factory=dict)
```

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

## 6. 鉴权接口

- `get_tenant_access_token(auth_context) -> str`
- `get_auth_headers(auth_context) -> dict[str, str]`

## 7. `im_chat` 契约

必填字段：

- `feishu-chat-create`：`app_id`、`app_secret`、`name`、`user_id_list`
- `feishu-chat-get`：`app_id`、`app_secret`、`chat_id`
- `feishu-chat-members-list`：`app_id`、`app_secret`、`chat_id`
- `feishu-chat-member-add`：`app_id`、`app_secret`、`chat_id`、`user_id_list`
- `feishu-chat-member-remove`：`app_id`、`app_secret`、`chat_id`、`member_id`
- `feishu-chat-disband`：`app_id`、`app_secret`、`chat_id`

统一规则：

- 只接受飞书标识 `user_id` 或 `open_id`
- 不做邮箱、手机号解析
- `member_id_type` 默认 `user_id`

## 8. 错误码

- `config_error`
- `validation_error`
- `action_not_found`
- `feishu_api_error`
- `http_error`
- `internal_error`

## 9. 测试命令

```bash
python3 -m pytest
python3 -m pytest docs/test
feishu-extension-skills invoke <action> --args-json '<json>'
```
