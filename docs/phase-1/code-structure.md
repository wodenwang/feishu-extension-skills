# 第一阶段代码结构规划

## 1. 目标

第一阶段只为群组模块搭建最小可运行系统，因此代码结构要满足两点：

- 足够小，避免为了未来能力过度设计
- 足够稳，后续第二阶段可以直接往上叠 `contact`、`im`、`card`

## 2. 建议目录

```text
src/feishu_extension_skills/
├── auth/
│   ├── __init__.py
│   ├── models.py
│   ├── provider.py
│   └── token_manager.py
├── cli/
│   ├── __init__.py
│   ├── __main__.py
│   └── app.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── errors.py
│   ├── http.py
│   ├── logging.py
│   └── result.py
├── runtime/
│   ├── __init__.py
│   ├── actions.py
│   ├── dispatcher.py
│   ├── models.py
│   └── validators.py
└── services/
    └── im_chat/
        ├── __init__.py
        ├── actions.py
        ├── client.py
        ├── models.py
        └── service.py
```

## 3. 文件职责

### `core/`

- `config.py`：调用参数与环境变量兜底配置对象
- `logging.py`：统一日志初始化
- `errors.py`：领域错误、飞书错误、用户输入错误
- `http.py`：HTTP client 与重试/超时封装
- `result.py`：统一 CLI 输出模型

### `auth/`

- `models.py`：token 响应模型
- `provider.py`：调用飞书鉴权接口
- `token_manager.py`：按 `app_id` 维度缓存与刷新 `tenant_access_token`

### `runtime/`

- `actions.py`：action 常量注册
- `dispatcher.py`：action 到 service handler 的映射
- `models.py`：统一请求/响应模型
- `validators.py`：入参校验与标准化

### `services/im_chat/`

- `models.py`：群组请求/响应模型
- `client.py`：直接调用飞书群组 API
- `service.py`：业务编排与参数转换
- `actions.py`：暴露给 runtime 的 handler

## 4. 测试目录建议

```text
tests/
├── unit/
│   ├── auth/
│   ├── core/
│   ├── runtime/
│   └── services/
│       └── im_chat/
└── smoke/
    └── cli/
```

## 5. 第一阶段 action 列表

- `feishu.chat.create`
- `feishu.chat.members.list`
- `feishu.chat.member.add`
- `feishu.chat.member.remove`
- `feishu.chat.delete`

## 6. 设计取舍

- 第一阶段不引入 repository、adapter、plugin registry 等更重的抽象层
- 第一阶段不引入异步任务队列
- 第一阶段不要求完整事件系统
- 第一阶段直接要求调用方提供 `user_id` / `open_id`，避免把 `contact` 变成硬依赖
- 第一阶段优先要求调用方显式传 `app_id` / `app_secret`，环境变量只作为兜底
