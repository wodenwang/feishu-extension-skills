# UAT 报告

日期：2026-03-28  
执行方式：agent team 并行设计 + lead 真实联调执行  
环境：本地 `.venv`，真实飞书开放平台租户  
应用：`cli_a926815318b81bc4`  

## 1. 执行摘要

本次 UAT 已完成当前版本真实联调。

结论：

- `feishu-chat-create`：通过
- `feishu-chat-members-list`：通过
- `feishu-chat-member-add`：失败
- `feishu-chat-member-remove`：失败
- token 缓存复用：通过（同进程）
- 基础失败用例：部分通过

整体判定：

- 当前最小系统已具备“真实建群 + 查成员”的可用性
- “加人”“移人”当前不能判定为通过，且存在实现与真实接口不一致的问题
- 当前状态不满足完整 DoD

## 2. 测试数据

测试成员：

- 王文哲：`ou_dc55aee11054ce6de978e4449c2cb0a6`
- 赵传耀：`ou_06e0a84e51f816524e32856ffcaf1a51`
- 赵志鸿：`ou_49ae97127f3acee64e92ce4b9c167574`

本次产生的测试群：

- `oc_4ebf14a797cca2cee684bfc6c50288fb`
  - 用途：建群 -> 查成员 -> 加人 -> 再查成员 -> 移人失败
  - 当前状态：群内仍为 2 人
- `oc_fafc6d23bd882bf80d10bd8075a211db`
  - 用途：补充验证“创建时直接带 3 人”
  - 当前状态：群内为 3 人

说明：

- 当时版本尚未提供删群 action，因此本次 UAT 无法通过 CLI 自动清理测试群

## 3. 执行结果

| Case ID | 结果 | 说明 | 证据 |
| --- | --- | --- | --- |
| UAT-001 建群成功 | Pass | 成功创建测试群，返回 `chat_id`、`name`、`owner_id` | [01-create.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/report/artifacts/01-create.json) |
| UAT-002 查群成员成功 | Pass | 成功列出 2 位初始成员 | [02-list-initial.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/report/artifacts/02-list-initial.json) |
| UAT-003 拉人入群成功 | Fail | CLI 返回成功，但后续成员列表未出现第 3 人 | [03-add.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/report/artifacts/03-add.json) |
| UAT-004 再次查群成员 | Fail | 加人后群成员仍为 2 人，未出现赵志鸿 | [04-list-after-add.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/report/artifacts/04-list-after-add.json) |
| UAT-005 移人成功 | Fail | 当前实现命中错误路径，返回 `404 page not found` | [05-remove.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/report/artifacts/05-remove.json) |
| UAT-006 移人后核对 | Blocked | 由于移人 action 失败，未形成有效移人后快照 | 无 |
| UAT-007 token 缓存复用 | Pass | 同进程内连续两次取 token，仅触发 1 次 fetch | [10-token-cache-check.txt](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/report/artifacts/10-token-cache-check.txt) |
| UAT-F01 非法群 ID | Fail | 返回了 `validation_error`，未按预期保留远端错误语义 | [07-list-invalid-chat.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/report/artifacts/07-list-invalid-chat.json) |
| UAT-F02 非法 action | Pass | 正确返回 `action_not_found` | [08-unknown-action.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/report/artifacts/08-unknown-action.json) |
| UAT-F03 坏 JSON | Pass | 正确返回 `validation_error` | [09-bad-json.txt](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/report/artifacts/09-bad-json.txt) |

## 4. 补充验证

为区分“用户数据有问题”还是“加人链路有问题”，额外做了一个补充验证：

- 直接在建群时把 3 位测试成员一起传入
- 结果：建群成功，且成员列表中确实能查到 3 个人

这说明：

- 提供给 UAT 的 3 个成员标识是可用的
- `create` 链路对这 3 个 open_id 是可工作的
- `member.add` 当前失败更像是实现问题或接口映射问题，不是测试数据问题

## 5. 关键发现

### 5.1 `feishu-chat-member-add` 结果建模有误

真实接口返回了：

- `invalid_id_list`
- `not_existed_id_list`
- `pending_approval_id_list`

当前实现却把请求里的输入成员直接回填为 `added_member_ids`。这会产生“CLI 看起来成功，但成员并未实际进群”的假阳性。

### 5.2 `feishu-chat-member-remove` 当前端点实现错误

当前代码使用：

- `DELETE /open-apis/im/v1/chats/{chat_id}/members`

真实联调结果显示这一路径直接返回 `404 page not found`。

补充协议探测表明：

- `DELETE /open-apis/im/v1/chats/{chat_id}/members` 才会命中真实接口
- 但当前参数映射仍未跑通成功移人

### 5.3 远端错误被错误包成 `validation_error`

对非法 `chat_id` 的真实响应包含远端错误结构，但当前 `FeishuAPIEnvelope` 对额外字段处理过严，最终被包装成了 `validation_error`。这不符合当时版本“保留远端错误语义”的目标。

### 5.4 token 缓存在 CLI 场景下有边界

当前 token 缓存是进程内内存缓存。

已验证：

- 同一 Python 进程内会复用

尚未满足：

- 独立 CLI 进程之间天然不共享内存缓存

这意味着如果严格按“多次 `python -m ...` 调用”理解，当前实现并不能跨进程复用 token。

## 6. 清理状态

当前仍遗留 2 个测试群：

- `oc_4ebf14a797cca2cee684bfc6c50288fb`
- `oc_fafc6d23bd882bf80d10bd8075a211db`

原因：

- 当时版本无删群 action
- `member.remove` 当前未跑通，无法经由 CLI 回滚补充验证群的第 3 位成员

建议：

- 通过飞书客户端或人工管理方式清理这两个测试群

## 7. 最终结论

本次 UAT 证明当时代码状态是“部分可用”：

- 可用：建群、查成员、统一 CLI、基础错误输出、同进程 token 缓存
- 不可用：加人、移人、远端错误语义保真、跨 CLI 进程 token 复用

因此当时版本不建议标记为完成版。下一步应优先修复：

1. `member.add` 的请求/响应映射
2. `member.remove` 的真实端点与参数约定
3. 远端错误结构的兼容解析
4. token 缓存是否要升级为跨进程缓存
