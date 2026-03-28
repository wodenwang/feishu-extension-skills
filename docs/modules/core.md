# 模块文档：`core`

## 1. 模块定位

`core` 是公共基础设施模块，为 `auth`、`runtime`、`im_chat` 提供统一的配置、错误、HTTP 与返回模型。

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

下游调用方：

- `auth`
- `runtime`
- `services/im_chat`

## 4. 代码结构

- `core/config.py`
- `core/logging.py`
- `core/http.py`
- `core/errors.py`
- `core/result.py`

## 5. 测试

对应测试目录：

- `docs/test/core/`
