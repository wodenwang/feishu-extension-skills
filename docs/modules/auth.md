# 模块文档：`auth`

## 1. 模块定位

`auth` 负责获取和缓存飞书访问凭证，向 `im_chat` 提供 `tenant_access_token` 与认证头。

## 2. 范围

In scope：

- 接收调用时传入的 `app_id` / `app_secret`
- 获取 `tenant_access_token`
- 内存缓存与提前刷新
- 向业务 client 提供认证头

Out of scope：

- 用户授权 token
- Redis / 文件缓存
- 多应用 profile 管理

## 3. 依赖关系

上游依赖：

- `core/config.py`
- `core/http.py`
- `core/errors.py`

下游调用方：

- `services/im_chat/client.py`

## 4. 代码结构

- `auth/models.py`
- `auth/provider.py`
- `auth/token_manager.py`

## 5. 对外接口

- `get_tenant_access_token(auth_context)`
- `get_auth_headers(auth_context)`

## 6. 测试

对应测试目录：

- `docs/test/auth/`
