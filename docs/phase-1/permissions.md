# 第一阶段权限汇总

## 1. 用途

本文档用于按“阶段”汇总第一阶段所需飞书权限，便于：

- 在飞书开发者后台一次性粘贴权限 JSON
- 从阶段视角快速核对权限范围
- 与模块文档中的权限段交叉检查

说明：

- 模块级权限仍写在各自模块文档中。
- 本文档是第一阶段的汇总视图，不替代模块文档。

## 2. 第一阶段最小权限 JSON

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

## 3. 模块到权限的映射

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

## 4. 申请说明

- 第一阶段只做建群、查群、查成员、加人、移人、解散群，上述权限通常已足够。
- 群公告、群置顶、企业自定义群标签不在第一阶段，不应提前申请额外权限。
- 权限展示名可能与文档命名略有差异，以上线前飞书开发者后台实际可申请项为准。

## 5. 第一阶段不申请的权限

```json
{
  "scopes": {
    "tenant": [
      "contact:*",
      "im:message*"
    ],
    "user": []
  }
}
```

说明：

- 上述 JSON 仅用于表达“本阶段不纳入范围的权限族”，不是可直接提交的后台权限配置。
- 卡片交互事件、审批、会议、搜索相关权限均延后到后续阶段。
