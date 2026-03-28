# 飞书服务端 API 模块规划

## 1. 规划目标

本规划面向“在 OpenClaw 中直接可用的飞书扩展 Skill”。核心思路是：

- Skill 负责自然语言调用入口
- Python 运行时负责参数校验、鉴权、调用飞书服务端 API
- 各业务模块按飞书能力域拆分
- 鉴权单独抽为独立模块

## 2. 模块拆分

对照飞书官方服务端 API 导航，当前规划如果只保留 9 个模块，会把多个独立能力域压扁在一起，尤其会遗漏消息域下的群组、消息卡片、飞书卡片、消息流、企业自定义群标签，以及机器人事件、审批、会议/妙记、搜索等。

建议拆分为 15 个模块：

### 模块 1：`core` 公共基础设施

职责：

- 配置加载
- 日志与审计
- HTTP 客户端封装
- 飞书错误码映射
- 重试、超时、限流
- 统一响应模型

不直接承载业务 API，但所有业务模块依赖该模块。

### 模块 2：`auth` 鉴权与 Access Token 管理

这是必须单独拆分的独立模块。

职责：

- 获取 `app_access_token`
- 获取 `tenant_access_token`
- 缓存与刷新 Token
- 统一为各服务模块注入认证头
- 屏蔽 SDK 与原始 HTTP 的差异

对应接口：

- `auth/v3/app_access_token/internal`
- `auth/v3/tenant_access_token/internal`

实现要点：

- 内存缓存 + 过期前提前刷新
- 失败时区分配置错误、权限错误、网络错误
- 支持后续扩展到文件缓存或 Redis 缓存

### 模块 3：`runtime` Skill 运行时与分发层

职责：

- 统一 Skill 调用入口
- action 到 service 的路由
- 请求参数反序列化
- 参数校验
- 输出结果标准化
- 统一事件入口与同步调用入口

建议 action 形式：

- `feishu.message.send`
- `feishu.chat.create`
- `feishu.card.update`
- `feishu.docx.create`
- `feishu.bitable.record.upsert`
- `feishu.calendar.event.create`

建议统一命令：

```bash
python -m feishu_extension_skills.cli invoke <action> --args-json '<json>'
```

### 模块 4：`im` 即时消息模块

优先级：高

目标能力：

- 发送文本消息
- 发送富文本消息
- 回复消息
- 编辑消息
- 召回消息
- 转发与合并转发消息
- 查询消息详情、已读状态、历史记录
- 上传/下载图片与文件
- 发送批量消息
- 表情回复
- 消息加急
- Pin 管理
- URL 预览更新

说明：

- 飞书官方“消息”服务端 API 在同一能力域下还包含“消息管理、批量消息、图片信息、文件信息、消息卡片、表情回复、消息加急、Pin、URL 预览、群组、飞书卡片、消息流、企业自定义群标签”等子域。
- 工程实现上建议将 `im` 继续拆成 `message.py`、`media.py`、`reaction.py`、`pin.py`、`url_preview.py` 等子客户端，避免单文件过大。

主要接口：

- `im/v1/messages`
- `im/v1/messages/{message_id}/reply`
- `im/v1/messages/{message_id}`
- `im/v1/messages/{message_id}/forward`
- `im/v1/messages/merge_forward`
- `im/v1/messages/{message_id}/read_users`
- `im/v1/images`
- `im/v1/files`
- `im/v1/messages/{message_id}/reactions`
- `im/v1/messages/{message_id}/urgent_app`
- `im/v1/messages/{message_id}/urgent_sms`
- `im/v1/messages/{message_id}/urgent_phone`
- `im/v1/pins`
- `im/v2/url_previews/batch_update`
- `message/v4/batch_send/`

建议首批 Skill：

- `feishu-message-send`
- `feishu-message-reply`
- `feishu-message-recall`
- `feishu-message-batch-send`
- `feishu-message-pin-list`

相关权限：

- `im:message:send_as_bot`
- `im:message:recall`
- `im:message:readonly`
- `im:message`

说明：

- 上述权限名称优先参考飞书官方 OpenClaw 插件公开权限清单。
- `im:message` 与 `im:message:readonly` 的边界需在实际申请时再核一次。

### 模块 5：`im_chat` 群组与会话模块

优先级：高

目标能力：

- 创建群组
- 查询群组详情
- 更新群名称、群描述、群头像等基础信息
- 拉人入群、移出群组
- 解散群组
- 查询群成员与成员权限
- 维护群管理员、群公告、群置顶、群标签等群治理能力

主要接口：

- `im/v1/chats`
- `im/v1/chats/{chat_id}`
- `im/v1/chats/{chat_id}/members`
- `im/v1/chats/{chat_id}/administrators`
- `im/v1/chats/{chat_id}/announcement`
- `im/v1/chats/{chat_id}/top_notice`
- 企业自定义群标签相关接口

建议首批 Skill：

- `feishu-chat-create`
- `feishu-chat-members-list`
- `feishu-chat-member-add`
- `feishu-chat-member-remove`
- `feishu-chat-delete`

相关权限：

- `im:chat:read`
- `im:chat:write`
- `im:chat.members:read`
- `im:chat.members:write`
- `im:chat:delete`

说明：

- 原文档将群组能力并入 `im` 主模块，但飞书官方目录已将“群组”单独列为子域，建议在工程上独立为 `chat` service。
- 如果后续要支持企业自定义群标签、群公告、群置顶消息等治理能力，应继续在该模块下按资源拆分子客户端。

### 模块 6：`card` 消息卡片与飞书卡片模块

优先级：高

目标能力：

- 发送卡片消息
- 更新应用已发送的消息卡片
- 发送仅特定人可见的卡片
- 删除仅特定人可见的卡片
- 构建飞书卡片 JSON
- 处理卡片按钮、表单、下拉选择等交互回调
- 为链接预览、群置顶、工作通知等场景复用统一卡片 DSL

主要接口：

- `im/v1/messages`
- `im/v1/messages/{message_id}` 的卡片更新能力
- `interactive/v1/card/update`
- `ephemeral/v1/send`
- `ephemeral/v1/delete`
- 飞书卡片相关回调事件

建议首批 Skill：

- `feishu-card-send`
- `feishu-card-update`
- `feishu-card-ephemeral-send`

相关权限：

- `im:message:send_as_bot`
- `im:message`
- 与卡片回调、延迟更新相关的事件权限

说明：

- 飞书官方文档把“消息卡片”和“飞书卡片”拆成两个子域；在本项目里建议统一落在 `card` 模块，避免一部分能力写在消息模块、一部分能力写在事件回调模块。
- 该模块除 API client 外，还应内置卡片模板、卡片 JSON 校验、回调载荷解析与签名校验。

### 模块 7：`docs_drive_wiki` 云文档、云空间、知识库模块

优先级：高

目标能力：

- 创建 Docx 文档
- 向文档写入内容
- 复制文档
- 上传文件到云空间
- 下载文件
- 查询文件元数据
- 创建和读取知识库节点
- 移动知识库节点

主要接口：

- `docx/v1/documents`
- `drive/v1/files/upload_all`
- `drive/v1/files/{file_token}/download`
- `drive/v1/metas/*`
- `wiki/v2/spaces`
- `wiki/v2/nodes`

建议首批 Skill：

- `feishu-docx-create`
- `feishu-drive-upload`
- `feishu-wiki-node-create`
- `feishu-wiki-node-move`

相关权限：

- `docx:document:create`
- `docx:document:readonly`
- `docx:document:write_only`
- `docs:document:copy`
- `docs:document:export`
- `docs:document.media:upload`
- `docs:document.media:download`
- `drive:drive.metadata:readonly`
- `drive:file:upload`
- `drive:file:download`
- `wiki:node:create`
- `wiki:node:read`
- `wiki:node:move`
- `wiki:node:copy`
- `wiki:node:retrieve`
- `wiki:space:read`
- `wiki:space:retrieve`
- `wiki:space:write_only`
- `space:document:retrieve`
- `space:document:move`
- `space:document:delete`
- `search:docs:read`

说明：

- `docs`、`docx`、`drive`、`wiki` 相关权限在飞书体系中存在交叉，设计时应按最小必要权限拆分 Skill。

### 模块 8：`bitable` 多维表格模块

优先级：高

目标能力：

- 创建多维表格
- 创建数据表
- 查询表结构
- 新增、更新、查询记录
- 按条件 upsert 记录

主要接口：

- `bitable/v1/apps`
- `bitable/v1/apps/{app_token}/tables`
- `bitable/v1/apps/{app_token}/tables/{table_id}/records`
- `bitable/v1/apps/{app_token}/views`

建议首批 Skill：

- `feishu-bitable-app-create`
- `feishu-bitable-table-create`
- `feishu-bitable-record-upsert`
- `feishu-bitable-record-query`

相关权限：

- `base:app:create`
- `base:app:read`
- `base:app:update`
- `base:table:create`
- `base:table:read`
- `base:table:update`
- `base:table:delete`
- `base:record:retrieve`
- `base:record:update`
- `base:view:read`
- `base:view:write_only`

说明：

- 如果首批需求包含“新增记录”，通常还需要记录创建权限。
- 该权限名未在本次查到的官方插件文章节选中直接出现，属于基于 API 家族的推断，落地前应在飞书应用后台再核对。

### 模块 9：`calendar` 日历模块

优先级：中

目标能力：

- 查询日历
- 创建日程
- 更新日程
- 删除日程
- 查询忙闲信息
- 回复会议邀请

主要接口：

- `calendar/v4/calendars`
- `calendar/v4/calendars/{calendar_id}/events`
- `calendar/v4/freebusy/list`

建议首批 Skill：

- `feishu-calendar-event-create`
- `feishu-calendar-freebusy-query`

相关权限：

- `calendar:calendar:read`
- `calendar:calendar.event:create`
- `calendar:calendar.event:read`
- `calendar:calendar.event:update`
- `calendar:calendar.event:delete`
- `calendar:calendar.event:reply`
- `calendar:calendar.free_busy:read`

### 模块 10：`task` 任务模块

优先级：中

目标能力：

- 创建任务
- 更新任务
- 查询任务
- 获取任务清单
- 新增与读取评论

主要接口：

- `task/v2/tasks`
- `task/v2/tasklists`
- `task/v2/comments`

建议首批 Skill：

- `feishu-task-create`
- `feishu-task-update`
- `feishu-tasklist-list`

相关权限：

- `task:task:read`
- `task:task:write`
- `task:task:writeonly`
- `task:tasklist:read`
- `task:tasklist:write`
- `task:comment:read`
- `task:comment:write`

### 模块 11：`contact` 通讯录与用户搜索模块

优先级：中

目标能力：

- 通过邮箱或手机号换取用户 ID
- 查询用户基础信息
- 搜索用户
- 为其他模块提供用户标识解析

主要接口：

- `contact/v3/users/batch_get_id`
- `contact/v3/users`
- 用户搜索相关接口

建议首批 Skill：

- `feishu-user-resolve`
- `feishu-user-search`

相关权限：

- `contact:contact.base:readonly`
- `contact:user.base:readonly`
- `contact:user.basic_profile:readonly`
- `contact:user:search`

### 模块 12：`bot_event` 机器人与事件回调模块

优先级：中

目标能力：

- 接收机器人单聊消息与群聊 @ 机器人消息
- 接收消息已读、消息撤回等事件
- 接收卡片交互回调
- 统一处理事件验签、去重、重试
- 将事件回调转成内部 action，供 Skill 或业务编排调用

主要接口：

- 事件订阅回调入口
- `im.message.receive_v1`
- `im.message.message_read_v1`
- `im.message.recalled_v1`
- 各类卡片 action 回调

建议首批 Skill / Action：

- `feishu-event-dispatch`
- `feishu-bot-message-handle`
- `feishu-card-action-handle`

相关权限：

- 以消息接收、事件订阅、卡片回调为主，需按实际事件订阅项在飞书后台逐项核对

说明：

- 这是“服务端 Skill”很容易漏掉的一层。没有事件回调层，卡片交互机器人、自动欢迎、审批通知反馈等场景都只能做单向调用，无法闭环。

### 模块 13：`approval` 审批与流程模块

优先级：中

目标能力：

- 查询审批定义
- 创建审批实例
- 查询审批实例、任务、抄送记录
- 在业务流中触发请假、报销、采购、用印等审批流程
- 回填审批结果到消息、文档或多维表格

主要接口：

- 审批定义相关接口
- 审批实例相关接口
- 审批任务与抄送相关接口

建议首批 Skill：

- `feishu-approval-create-instance`
- `feishu-approval-instance-query`

相关权限：

- 以审批定义读取、审批实例创建/读取、任务查询类权限为主，以上线前在飞书后台复核

### 模块 14：`vc_minutes` 视频会议与妙记模块

优先级：中

目标能力：

- 创建或查询视频会议
- 获取会议链接与会议信息
- 查询妙记记录与转写结果
- 将会议纪要沉淀到 Docx、Wiki 或 Bitable

主要接口：

- 视频会议相关接口
- 妙记相关接口

建议首批 Skill：

- `feishu-meeting-create`
- `feishu-minutes-query`

相关权限：

- 以会议读写、妙记读取类权限为主，需结合实际租户能力核对

### 模块 15：`search` 搜索模块

优先级：中

目标能力：

- 统一检索文档、知识库、消息等内容
- 作为“先搜索、后执行”的前置模块
- 为问答型 Skill 提供候选资源召回

主要接口：

- 文档搜索相关接口
- 消息搜索相关接口
- 跨资源搜索相关接口

建议首批 Skill：

- `feishu-doc-search`
- `feishu-message-search`

相关权限：

- 以 `search:*` 与对应资源的只读权限为主，具体以后台可申请权限项为准

## 3. 模块之间的依赖关系

建议依赖方向如下：

```text
skills -> runtime -> services -> auth -> core
                         \------> core
callbacks -> runtime -> services
```

说明：

- `skills/` 只暴露调用说明，不直接写业务逻辑
- `runtime` 负责把 Skill 请求转成 Python action，也负责把事件回调转成内部动作
- `services` 内按业务域调用飞书 API
- `auth` 为服务模块统一提供 Token
- `core` 提供底层公共能力

## 4. Skill 设计方式

建议每个 Skill 聚焦一个明确动作，不做“大而全”。

原则：

- 一个 Skill 对应一个明确动作
- Skill 文案只负责触发条件、参数收集与调用说明
- 真实业务逻辑统一落在 Python action 中

第一阶段的 Skill 详细模板与具体文档，统一放在：

- [第一阶段实施文档索引](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/phase-1/README.md)

## 5. V1 建议优先落地的 Skill 清单

建议按阶段推进，而不是一次性铺开所有 V1 Skill。

分阶段建议：

1. 第一阶段：`feishu-chat-create`、`feishu-chat-members-list`、`feishu-chat-member-add`、`feishu-chat-member-remove`、`feishu-chat-delete`
2. 第二阶段：`contact`、基础 `im`、静态 `card`
3. 第三阶段：`bot_event`、交互式 `card`、`approval`、`search`、`vc_minutes`

理由：

- 现阶段项目已经进入执行期，第一优先级不再是“列一个尽量全的 V1 清单”，而是先把第一阶段最小系统落地。
- 详细的第一阶段 Skill 定义和调用方式，见 `docs/phase-1/skills/`。

## 6. 权限申请策略

建议将权限分成三层：

### 第一层：基础必需

- 鉴权相关能力
- 消息发送与读取
- 群组读写
- 基础用户解析

### 第二层：高频办公

- 卡片发送与回调
- Docx
- Drive
- Wiki
- Bitable

### 第三层：协同管理

- Calendar
- Task
- Approval
- Video Meeting / Minutes
- Search

权限申请原则：

- 初版只申请 V1 Skill 所需权限
- 每新增一个模块，再补对应权限
- 阶段级汇总权限与模块级权限并存
- 对权限名称不稳定或后台展示名与文档名不完全一致的项，以上线前后台配置页为准

说明：

- 第一阶段的可直接复制权限 JSON，统一放在 `docs/phase-1/permissions.md` 与对应模块文档中。

## 7. 设计约束

- 优先调用飞书官方 Python SDK；如 SDK 未覆盖或不易用，再回退到原始 HTTP
- 所有 Token 管理必须经过 `auth` 模块
- 禁止在 Skill 层直接拼装敏感认证信息
- 所有写操作默认带审计日志
- 对幂等性要求高的动作需提供请求去重策略
- 所有事件回调必须校验签名并做事件去重

## 8. 需要后续补充的能力

以下能力建议在第一阶段稳定后再补：

- 消息流
- 企业自定义群标签的完整治理能力
- 文档评论
- 更细粒度的文件权限与共享
- 邮箱、服务台、管理后台、人事等更垂直业务域

这些能力当前不建议与 V1 同时落地，避免初始化阶段范围失控。

## 9. 参考依据

本规划主要基于以下资料：

- 飞书服务端 API 总目录：
  [服务端 API - 开发文档](https://open.feishu.cn/document/server-docs)
- 飞书官方消息概述：
  [消息概述](https://open.feishu.cn/document/server-docs/im-v1/introduction)
- 飞书 AI Assistant 代码生成指南：
  [AI assistant code generation guide](https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM/AI-assistant-code-generation-guide)
- 飞书官方 OpenClaw 插件文章中的权限清单：
  [OpenClaw 飞书官方插件上线](https://www.feishu.cn/content/article/7613711414611463386)
- 飞书官方 Python SDK 说明：
  [larksuite/oapi-sdk-python](https://github.com/larksuite/oapi-sdk-python)
- OpenClaw Skills 机制：
  [Skills - OpenClaw](https://docs.openclaw.ai/tools/skills)

说明：

- 本次补全重点参考了飞书官方服务端 API 左侧能力域导航，尤其是“消息”域下已单独列出的群组、消息卡片、飞书卡片、消息流、企业自定义群标签等子域。
- 文中列出的权限名，优先采用飞书官方 OpenClaw 插件文章中已公开的权限清单。
- 少量“按 API 家族推断但未在本次核对中逐条确认”的权限，文中已显式标注为待上线前复核。

## 10. 实现优先级规划

本项目的优先级判断采用以下规则：

1. 先满足最小可运行系统，再扩展业务域。
2. 同等价值下，优先实现难度更低、依赖更少的模块。
3. 同等难度下，优先选择飞书官方 OpenClaw 插件未覆盖或未独立封装好的能力。

### 第一阶段：群组模块最小实现系统

目标：

- 先把“群组”能力单独跑通，形成第一套可用的服务端 Skill。

范围：

- `core`
- `auth`
- `runtime`
- `im_chat`

第一阶段实施细节不再在本文件展开，统一见：

- [第一阶段实施文档索引](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/phase-1/README.md)
- [Agent Teams 协作规范](/Users/wenzhewang/workspace/codex/feishu-extension-skills/AGENTS.md)

### 第二阶段：低复杂度补强阶段

优先顺序：

1. `contact`
2. `im`
3. `card` 的静态卡片发送与更新能力

原因：

- `contact` 和基础 `im` 的实现难度都低于审批、会议、事件回调，且能直接提升第一阶段 Skill 的可用性。
- `card` 属于官方插件中更值得补位的能力，但其“静态发送/更新”难度明显低于“交互回调 + 状态驱动更新”，适合作为第二阶段末尾能力。

### 第三阶段：高价值但复杂度更高的协同能力

优先顺序：

1. `bot_event`
2. `card` 的交互回调能力
3. `approval`
4. `search`
5. `vc_minutes`

原因：

- `bot_event` 是卡片交互、机器人自动处理、审批结果回写等能力的技术前置。
- 交互式卡片比静态卡片更能体现本项目与官方插件的差异化，但需要先有稳定的回调层。
- `approval`、`search`、`vc_minutes` 都有明确业务价值，但权限、数据模型或租户能力差异更复杂，应放到第三阶段。
