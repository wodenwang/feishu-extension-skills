# 权限汇总

本文档汇总当前保留范围所需的飞书权限。

## 1. 最小权限 JSON

```json
{
  "scopes": {
    "tenant": [
      "im:chat:read",
      "im:chat:write",
      "im:chat.members:read",
      "im:chat.members:write",
      "im:chat:delete"
    ],
    "user": []
  }
}
```

## 2. 模块到权限的映射

### `core`

```json
{
  "scopes": {
    "tenant": [],
    "user": []
  }
}
```

### `auth`

```json
{
  "scopes": {
    "tenant": [],
    "user": []
  }
}
```

### `runtime`

```json
{
  "scopes": {
    "tenant": [],
    "user": []
  }
}
```

### `im_chat`

```json
{
  "scopes": {
    "tenant": [
      "im:chat:read",
      "im:chat:write",
      "im:chat.members:read",
      "im:chat.members:write",
      "im:chat:delete"
    ],
    "user": []
  }
}
```

## 3. 当前不申请

```json
{
  "scopes": {
    "tenant": [
      "im:message*",
      "contact:*"
    ],
    "user": []
  }
}
```

说明：

- 上述 JSON 仅用于表达当前不纳入范围的权限族
- 消息、卡片、文档、通讯录等能力不在当前仓库结构中
