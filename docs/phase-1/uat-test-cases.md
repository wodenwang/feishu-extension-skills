# 第一阶段 UAT 用例与报告骨架

本文档用于第一阶段真实联调 UAT。目标是用同一组 `app_id` / `app_secret` 和固定测试成员，完整验证群组链路是否可以通过统一 CLI 跑通。

## 1. 测试范围

覆盖范围：

- `feishu.chat.create`
- `feishu.chat.members.list`
- `feishu.chat.member.add`
- `feishu.chat.member.remove`
- `feishu.chat.delete`
- `tenant_access_token` 获取与缓存复用
- CLI 统一入口与统一 JSON 输出

不覆盖范围：

- 联系人解析
- 邮箱/手机号转用户 ID
- 消息发送
- 卡片交互
- 群公告、群置顶、群标签

## 2. 前置条件

- 第一阶段代码已安装并可运行
- 已执行 `python -m pip install -e '.[dev]'`
- 已确认测试飞书应用具备群组读写权限
- 已准备可用的测试群管理策略
- 测试执行环境可访问飞书开放平台

## 3. 测试数据

应用凭证：

- `app_id`: `cli_a926815318b81bc4`
- `app_secret`: 已提供，不在文档中重复明文记录

测试成员：

- 王文哲: `ou_dc55aee11054ce6de978e4449c2cb0a6`
- 赵传耀: `ou_06e0a84e51f816524e32856ffcaf1a51`
- 赵志鸿: `ou_49ae97127f3acee64e92ce4b9c167574`

建议测试群策略：

- 新建一个仅用于 UAT 的临时群
- 首次建群只拉入王文哲，作为基础成员
- 后续再执行加人、查成员、移人验证

## 4. 统一执行约定

统一命令格式：

```bash
python -m feishu_extension_skills.cli invoke <action> --args-json '<json>'
```

参数约定：

- 所有 action 都显式传 `app_id` / `app_secret`
- `member_id_type` 默认使用 `user_id`
- 第一阶段不使用邮箱或手机号作为成员输入

## 5. Test Case 清单

### UAT-001: 建群成功

目的：

- 验证 `feishu.chat.create` 可成功创建群组

执行命令：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.create --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","name":"UAT-第一阶段-群组测试","user_id_list":["ou_dc55aee11054ce6de978e4449c2cb0a6"],"owner_id":"ou_dc55aee11054ce6de978e4449c2cb0a6"}'
```

预期结果：

- 返回 `ok=true`
- 返回 `chat_id`
- 返回 `name`
- 返回 `member_count`
- 返回 `owner_id`

记录点：

- 保存 `chat_id`
- 保存返回 JSON

### UAT-002: 查群成员成功

目的：

- 验证 `feishu.chat.members.list` 可读取刚创建的群成员

执行命令：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.members.list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
```

预期结果：

- 返回 `ok=true`
- 返回 `chat_id`
- `items` 中包含王文哲
- `has_more` 可为 `false`
- `page_token` 可为空

记录点：

- 对照 `member_id` 是否为王文哲
- 保存当前成员快照

### UAT-003: 拉人入群成功

目的：

- 验证 `feishu.chat.member.add` 可将新成员加入群组

执行命令：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.member.add --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>","user_id_list":["ou_06e0a84e51f816524e32856ffcaf1a51","ou_49ae97127f3acee64e92ce4b9c167574"]}'
```

预期结果：

- 返回 `ok=true`
- 返回 `chat_id`
- `added_member_ids` 至少包含赵传耀和赵志鸿
- `failed_member_ids` 为空或仅包含服务端明确拒绝的成员

记录点：

- 保存返回 JSON
- 记录实际加入成功的成员列表

### UAT-004: 再次查群成员

目的：

- 验证加人后成员列表已更新

执行命令：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.members.list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
```

预期结果：

- 返回 `ok=true`
- `items` 中包含王文哲、赵传耀、赵志鸿

记录点：

- 保存成员快照
- 对比加人前后差异

### UAT-005: 移人成功

目的：

- 验证 `feishu.chat.member.remove` 可将指定成员移出群组

执行命令：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.member.remove --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>","member_id":"ou_49ae97127f3acee64e92ce4b9c167574"}'
```

预期结果：

- 返回 `ok=true`
- 返回 `chat_id`
- 返回 `removed_member_id`
- 返回 `status`

记录点：

- 保存返回 JSON
- 记录被移除成员

### UAT-006: 再次查群成员并核对

目的：

- 验证移人后成员列表已回退

执行命令：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.members.list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
```

预期结果：

- 返回 `ok=true`
- `items` 中包含王文哲和赵传耀
- `items` 中不再包含赵志鸿

记录点：

- 保存移人后的成员快照

### UAT-008: 解散测试群

目的：

- 验证 `feishu.chat.delete` 可解散指定测试群

执行命令：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.delete --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
```

预期结果：

- 返回 `ok=true`
- 返回 `chat_id`
- 返回 `status`

记录点：

- 保存返回 JSON
- 确认群组已从飞书侧消失，或在后续访问时返回已解散相关错误

### UAT-007: token 缓存复用观察

目的：

- 验证同一组 `app_id` / `app_secret` 重复调用时会复用 `tenant_access_token`

执行方式：

1. 连续执行两次同一 action，例如 `feishu.chat.members.list`
2. 两次都使用相同的 `app_id` / `app_secret`
3. 若环境开启 DEBUG 或请求日志，观察第二次不应再次触发 token 获取

执行命令示例：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.members.list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
python -m feishu_extension_skills.cli invoke feishu.chat.members.list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>"}'
```

预期结果：

- 两次调用都返回 `ok=true`
- 若可观察请求日志，第二次不应重新获取 token
- 若不可直接观察日志，则至少确认两次调用均成功且无额外鉴权异常

## 6. 失败用例

### UAT-F01: 缺少必填参数

命令示例：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.members.list --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>"}'
```

预期结果：

- 返回 `ok=false`
- `error.code` 为 `validation_error`

### UAT-F02: 空成员列表

命令示例：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.member.add --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>","user_id_list":[]}'
```

预期结果：

- 返回 `ok=false`
- `error.code` 为 `validation_error`

### UAT-F03: 非法 action

命令示例：

```bash
python -m feishu_extension_skills.cli invoke demo.missing --args-json '{}'
```

预期结果：

- 返回 `ok=false`
- `error.code` 为 `action_not_found`

### UAT-F04: 非法 member_id_type

命令示例：

```bash
python -m feishu_extension_skills.cli invoke feishu.chat.member.remove --args-json '{"app_id":"cli_a926815318b81bc4","app_secret":"<provided>","chat_id":"<chat_id>","member_id":"ou_49ae97127f3acee64e92ce4b9c167574","member_id_type":"email"}'
```

预期结果：

- 返回 `ok=false`
- `error.code` 为 `validation_error`

## 7. 执行记录模板

```text
UAT Run ID:
Date:
Executor:
Environment:
App ID:
Chat ID:

Case ID | Command | Expected | Actual | Pass/Fail | Evidence
-------- | ------- | -------- | ------ | --------- | --------
UAT-001 | ... | ... | ... | ... | ...
UAT-002 | ... | ... | ... | ... | ...
UAT-003 | ... | ... | ... | ... | ...
UAT-004 | ... | ... | ... | ... | ...
UAT-005 | ... | ... | ... | ... | ...
UAT-006 | ... | ... | ... | ... | ...
UAT-007 | ... | ... | ... | ... | ...
UAT-008 | ... | ... | ... | ... | ...
UAT-F01 | ... | ... | ... | ... | ...
UAT-F02 | ... | ... | ... | ... | ...
UAT-F03 | ... | ... | ... | ... | ...
UAT-F04 | ... | ... | ... | ... | ...
```

## 8. 清理说明

- UAT 结束后先将新增成员移除，恢复到最小可接受成员集
- 若群组仅用于本次 UAT，可保留 `chat_id` 供后续复测
- 第一阶段提供删群 action，若当前群无须保留，应优先通过 `feishu.chat.delete` 清理
- 清理完成后记录最终成员快照，避免后续测试误用脏状态

## 9. 报告骨架

建议最终报告按以下结构填写：

```text
1. Test Summary
2. Test Environment
3. Test Data
4. Execution Log
5. Failed Cases
6. Cleanup Status
7. Conclusion
8. Open Issues
```
