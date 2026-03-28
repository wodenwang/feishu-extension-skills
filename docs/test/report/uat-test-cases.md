# 群组 UAT 用例

本文档只覆盖真实飞书环境下的 `feishu-chat` 链路，不混入自动化单测。

## 1. 覆盖范围

功能链路：

- `feishu-chat-create`
- `feishu-chat-get`
- `feishu-chat-members-list`
- `feishu-chat-member-add`
- `feishu-chat-member-remove`
- `feishu-chat-disband`

运行时链路：

- `tenant_access_token` 获取与缓存复用
- CLI 统一入口与统一 JSON 输出
- 关键失败语义

## 2. 前置条件

- 当前代码已安装并可运行
- 已执行 `python3 -m pip install -e '.[dev]'`
- 测试环境可访问飞书开放平台
- 测试应用已具备群组相关权限
- 已准备好可清理的临时测试群策略

## 3. 测试数据

应用凭证：

- `app_id`: `cli_a926815318b81bc4`
- `app_secret`: 已提供，不在文档中重复明文记录

测试成员：

- 王文哲：`ou_dc55aee11054ce6de978e4449c2cb0a6`
- 赵传耀：`ou_06e0a84e51f816524e32856ffcaf1a51`
- 赵志鸿：`ou_49ae97127f3acee64e92ce4b9c167574`

## 4. 执行约定

统一命令：

```bash
feishu-extension-skills invoke <action> --args-json '<json>'
```

统一规则：

- 所有 action 都显式传 `app_id` / `app_secret`
- 默认使用 `user_id`
- 不使用邮箱或手机号作为成员输入
- 对加人、移人结果需做延迟复核，避免被最终一致性误导

## 5. 用例矩阵

| Case ID | 分类 | 目标 |
| --- | --- | --- |
| UAT-001 | 功能 | 创建测试群 |
| UAT-002 | 功能 | 查询群详情 |
| UAT-003 | 功能 | 查询初始成员 |
| UAT-004 | 功能 | 拉人入群 |
| UAT-005 | 功能 | 复核加人后成员 |
| UAT-006 | 功能 | 移出群成员 |
| UAT-007 | 功能 | 复核移人后成员 |
| UAT-008 | 清理 | 解散测试群 |
| UAT-009 | 运行时 | 观察 token 缓存复用 |
| UAT-F01 | 失败 | 缺少必填参数 |
| UAT-F02 | 失败 | 空成员列表 |
| UAT-F03 | 失败 | 非法 action |
| UAT-F04 | 失败 | 非法 `member_id_type` |

## 6. 功能用例

### UAT-001: 创建测试群

命令：

```bash
feishu-extension-skills invoke feishu-chat-create --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","name":"UAT-群组测试","user_id_list":["ou_dc55aee11054ce6de978e4449c2cb0a6"],"owner_id":"ou_dc55aee11054ce6de978e4449c2cb0a6"}'
```

预期：

- `ok=true`
- 返回 `chat_id`
- 返回 `name`
- 返回 `owner_id`

记录：

- 保存 `chat_id`
- 保存返回 JSON

### UAT-002: 查询群详情

命令：

```bash
feishu-extension-skills invoke feishu-chat-get --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
```

预期：

- `ok=true`
- 返回 `chat_id`
- 返回群名称和所有者信息

### UAT-003: 查询初始成员

命令：

```bash
feishu-extension-skills invoke feishu-chat-members-list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
```

预期：

- `ok=true`
- `items` 中包含王文哲

### UAT-004: 拉人入群

命令：

```bash
feishu-extension-skills invoke feishu-chat-member-add --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>","user_id_list":["ou_06e0a84e51f816524e32856ffcaf1a51","ou_49ae97127f3acee64e92ce4b9c167574"]}'
```

预期：

- `ok=true`
- 返回 `chat_id`
- `added_member_ids` 反映真实入群结果

### UAT-005: 复核加人后成员

命令：

```bash
feishu-extension-skills invoke feishu-chat-members-list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
```

预期：

- `ok=true`
- `items` 中包含王文哲、赵传耀、赵志鸿

### UAT-006: 移出群成员

命令：

```bash
feishu-extension-skills invoke feishu-chat-member-remove --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>","member_id":"ou_49ae97127f3acee64e92ce4b9c167574"}'
```

预期：

- `ok=true`
- 返回 `removed_member_id`
- 返回 `status` 或等价结果

### UAT-007: 复核移人后成员

命令：

```bash
feishu-extension-skills invoke feishu-chat-members-list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
```

预期：

- `ok=true`
- `items` 中不再包含赵志鸿

## 7. 清理用例

### UAT-008: 解散测试群

命令：

```bash
feishu-extension-skills invoke feishu-chat-disband --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
```

预期：

- `ok=true`
- 返回 `chat_id`
- 返回 `status=disbanded` 或等价语义

## 8. 运行时用例

### UAT-009: token 缓存复用观察

步骤：

1. 连续两次调用同一个可重复 action
2. 两次都使用相同的 `app_id` / `app_secret`
3. 观察第二次是否复用 token

示例：

```bash
feishu-extension-skills invoke feishu-chat-members-list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
feishu-extension-skills invoke feishu-chat-members-list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
```

预期：

- 两次调用都成功
- 在可观测日志中，第二次不应重新获取 token

## 9. 失败用例

### UAT-F01: 缺少必填参数

```bash
feishu-extension-skills invoke feishu-chat-members-list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>"}'
```

预期：

- `ok=false`
- `error.code=validation_error`

### UAT-F02: 空成员列表

```bash
feishu-extension-skills invoke feishu-chat-member-add --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>","user_id_list":[]}'
```

预期：

- `ok=false`
- `error.code=validation_error`

### UAT-F03: 非法 action

```bash
feishu-extension-skills invoke demo.missing --args-json '{}'
```

预期：

- `ok=false`
- `error.code=action_not_found`

### UAT-F04: 非法 `member_id_type`

```bash
feishu-extension-skills invoke feishu-chat-member-remove --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>","member_id":"ou_49ae97127f3acee64e92ce4b9c167574","member_id_type":"email"}'
```

预期：

- `ok=false`
- `error.code=validation_error`

### UAT-F05: 非法 `chat_id`

```bash
feishu-extension-skills invoke feishu-chat-members-list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"oc_invalid_chat_id"}'
```

预期：

- `ok=false`
- `error.code` 为 `feishu_api_error` 或 `http_error`
- 保留远端错误语义，不应误包成本地 `validation_error`

## 10. 执行记录模板

```text
UAT Run ID:
Date:
Executor:
Environment:
App ID:
Chat ID:

Case ID | Category | Expected | Actual | Pass/Fail | Evidence
-------- | -------- | -------- | ------ | --------- | --------
UAT-001 | 功能 | ... | ... | ... | ...
UAT-002 | 功能 | ... | ... | ... | ...
UAT-003 | 功能 | ... | ... | ... | ...
UAT-004 | 功能 | ... | ... | ... | ...
UAT-005 | 功能 | ... | ... | ... | ...
UAT-006 | 功能 | ... | ... | ... | ...
UAT-007 | 功能 | ... | ... | ... | ...
UAT-008 | 清理 | ... | ... | ... | ...
UAT-009 | 运行时 | ... | ... | ... | ...
UAT-F01 | 失败 | ... | ... | ... | ...
UAT-F02 | 失败 | ... | ... | ... | ...
UAT-F03 | 失败 | ... | ... | ... | ...
UAT-F04 | 失败 | ... | ... | ... | ...
UAT-F05 | 失败 | ... | ... | ... | ...
```

## 11. 推荐执行顺序

1. 先跑 `UAT-001` 到 `UAT-007`，验证主链路。
2. 再跑 `UAT-009` 和 `UAT-F01` 到 `UAT-F05`，确认运行时与失败语义。
3. 最后执行 `UAT-008`，完成测试群清理。
