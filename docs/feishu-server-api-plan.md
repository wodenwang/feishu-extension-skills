# 飞书服务端 API 当前规划

本文档不再维护按阶段铺开的全量蓝图，只记录当前仓库实际保留的范围与后续扩展原则。

## 1. 当前保留模块

- `core`：配置、错误、HTTP、统一结果
- `auth`：`tenant_access_token` 获取与缓存
- `runtime`：统一 CLI 和 action 分发
- `im_chat`：飞书群组能力

## 2. 当前保留 action

- `feishu-chat-create`
- `feishu-chat-get`
- `feishu-chat-members-list`
- `feishu-chat-member-add`
- `feishu-chat-member-remove`
- `feishu-chat-disband`

## 3. 统一调用方式

```bash
feishu-extension-skills invoke <action> --args-json '<json>'
```

## 4. Skill 设计方式

按模块粒度维护 Skill。

当前固定为：

- `skills/feishu-chat/`

skill 内部覆盖同一模块下的一组 action，不再为单个 action 建独立 skill 目录。

## 5. 当前不保留的能力

以下能力暂不在仓库内保留任何占位代码或空目录：

- 即时消息
- 卡片
- 云文档 / 云空间 / 知识库
- 通讯录
- 审批
- 搜索
- 妙记 / 会议

如未来重启扩展，应先补对应设计文档，再新增模块目录和 Skill。
