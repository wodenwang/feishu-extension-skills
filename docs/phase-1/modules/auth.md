# 模块文档：`auth`

## 1. 模块定位

`auth` 负责获取和缓存飞书访问凭证，第一阶段只需要稳定拿到 `tenant_access_token`，供 `im_chat` 调用群组 API。

第一阶段的目标用法是：调用 Skill 时直接传 `app_id` 与 `app_secret`，`auth` 负责用这组凭证换取 token 并缓存，后续重复调用时复用缓存结果。

它属于第一阶段，因为所有后续业务调用都建立在 token 获取成功之上。

## 2. 范围

In scope：

- 接收调用时传入的 `app_id` / `app_secret`
- 获取 `app_access_token`
- 获取 `tenant_access_token`
- 内存缓存与提前刷新
- 向业务 client 提供认证头

Out of scope：

- 多租户 profile 管理
- Redis 缓存
- 用户授权 token
- 更复杂的多凭证路由策略

## 3. 依赖关系

上游依赖：

- `core/config.py`
- `core/http.py`
- `core/errors.py`

下游调用方：

- `services/im_chat/client.py`

## 4. 代码结构规划

建议文件：

- `auth/models.py`
- `auth/provider.py`
- `auth/token_manager.py`

文件职责：

- `models.py`：定义飞书 token 接口响应模型
- `provider.py`：使用传入凭证直接请求飞书鉴权接口
- `token_manager.py`：以 `app_id` 为主键缓存 token、控制刷新时机

## 5. 核心数据模型

建议数据模型：

- `TenantAccessTokenResponse`
- `AppAccessTokenResponse`
- `TokenCacheEntry`
- `AuthContext`

关键方法建议：

- `get_tenant_access_token(auth_context)`
- `get_auth_headers(auth_context)`

## 6. 对外动作

`auth` 不直接暴露 Skill action。

提供内部接口：

- `token_manager.get_tenant_access_token(auth_context)`
- `token_manager.get_auth_headers(auth_context)`

## 7. 飞书 API / 外部接口

主要接口：

- `auth/v3/app_access_token/internal`
- `auth/v3/tenant_access_token/internal`

请求方式：

- `POST`

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

- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
- `FEISHU_BASE_URL`
- `FEISHU_TOKEN_REFRESH_SKEW_SECONDS`

调用时凭证：

- `app_id`
- `app_secret`

建议规则：

- 优先使用调用参数中的 `app_id` / `app_secret`
- 若调用参数缺失，再回退环境变量
- token 缓存 key 至少包含 `app_id`，必要时包含 `base_url`

## 9. 测试与验收

单元测试：

- token 未命中缓存时能正确获取
- token 即将过期时会主动刷新
- 飞书返回错误码时能抛出统一异常

冒烟测试：

- 使用传入的 `app_id` / `app_secret` 成功获取 `tenant_access_token`
- 同一组凭证第二次调用时命中缓存

验收标准：

- `im_chat` 不需要关心 token 生命周期
- `im_chat` 不需要关心凭证来自调用参数还是环境变量
- token 失败时错误信息能区分配置问题与远端问题

## 10. 后续扩展

- 支持文件缓存或 Redis 缓存
- 支持多应用 profile
- 支持 user token
