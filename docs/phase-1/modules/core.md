# 模块文档：`core`

## 1. 模块定位

`core` 是第一阶段最底层的公共基础设施模块，为 `auth`、`runtime`、`im_chat` 提供统一的配置、日志、错误、HTTP 与返回模型。

它属于第一阶段，因为没有它，后续模块会快速出现重复代码和不一致的错误处理。

## 2. 范围

In scope：

- 配置读取
- 日志初始化
- HTTP client 封装
- 通用错误类型
- 统一返回模型

Out of scope：

- 业务路由
- token 缓存逻辑
- 群组业务逻辑

## 3. 依赖关系

上游依赖：

- 无

下游调用方：

- `auth`
- `runtime`
- `services/im_chat`

## 4. 代码结构规划

建议文件：

- `core/config.py`
- `core/logging.py`
- `core/http.py`
- `core/errors.py`
- `core/result.py`

文件职责：

- `config.py`：读取调用参数，并在缺失时回退环境变量
- `logging.py`：统一日志格式与级别
- `http.py`：封装 `httpx` 或 SDK fallback 的请求入口
- `errors.py`：定义 `ConfigError`、`ValidationError`、`FeishuAPIError`
- `result.py`：定义标准成功/失败输出

## 5. 核心数据模型

建议数据模型：

- `AppConfig`
- `HTTPOptions`
- `ActionResult`
- `ErrorPayload`

统一输出建议：

```json
{
  "ok": true,
  "action": "feishu.chat.create",
  "data": {},
  "error": null
}
```

## 6. 对外动作

`core` 不直接暴露 Skill action。

它暴露的是内部能力：

- `load_config()`
- `build_http_client()`
- `ok_result()`
- `error_result()`

## 7. 飞书 API / 外部接口

无直接业务 API。

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
- `FEISHU_LOG_LEVEL`

调用时凭证：

- `app_id`
- `app_secret`

说明：

- 第一阶段推荐由 Skill / CLI 显式传入 `app_id` 与 `app_secret`
- 环境变量只作为兜底，不作为唯一入口

## 9. 测试与验收

单元测试：

- 配置缺失时报错
- HTTP timeout 配置生效
- 标准结果模型序列化正确

冒烟测试：

- CLI 启动时能成功加载配置并初始化日志

验收标准：

- 后续模块无需重复定义配置、日志、错误模型

## 10. 后续扩展

- 增加请求重试策略
- 增加 trace id 与审计字段
- 增加 SDK / 原始 HTTP 双实现切换
