# 第一阶段第二轮回归报告

日期：2026-03-28  
执行方式：tester agent 真实回归  
环境：本地 `.venv`，真实飞书开放平台租户  
应用：`cli_a926815318b81bc4`

## 1. 回归结论

第二轮回归通过。

结论：

- `feishu.chat.member.add` 在 `member_id_type=open_id` 下真实生效
- `feishu.chat.member.remove` 在 `member_id_type=open_id` 下真实生效
- 非法 `chat_id` 现在返回远端 `feishu_api_error`
- token cache 同进程复用仍成立

是否需要打回 programmer：

- 不需要

## 2. 执行说明

本轮按照 [`docs/phase-1/uat-regression-round2.md`](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/phase-1/uat-regression-round2.md) 执行，目标群使用第一轮遗留群：

- `oc_4ebf14a797cca2cee684bfc6c50288fb`

执行时观察到：

- `member.add` 和 `member.remove` 存在短暂的最终一致性延迟
- 因此不能只看即时 `members.list`，需要做延迟核对

## 3. 测试结果

| Case ID | 结果 | 说明 | 证据 |
| --- | --- | --- | --- |
| R2-003 远端错误语义保留 | Pass | 非法 `chat_id` 返回 `feishu_api_error`，保留了远端错误语义 | [r2/00-invalid-chat.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/phase-1/uat-artifacts/r2/00-invalid-chat.json) |
| R2-001 `member.add` 真正生效 | Pass | `member.add` 后延迟核对可见赵志鸿进入群 | [r2/05-add-again.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/phase-1/uat-artifacts/r2/05-add-again.json), [r2/06-list-after-add-wait.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/phase-1/uat-artifacts/r2/06-list-after-add-wait.json) |
| R2-002 `member.remove` 真正生效 | Pass | `member.remove` 后延迟核对可见赵志鸿退出群 | [r2/07-remove-final.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/phase-1/uat-artifacts/r2/07-remove-final.json), [r2/09-list-final-after-wait.json](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/phase-1/uat-artifacts/r2/09-list-final-after-wait.json) |
| R2-004 token cache 观察 | Pass | 同进程内连续两次取 token，仅触发 1 次底层 fetch | [r2/10-token-cache-check.txt](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/phase-1/uat-artifacts/r2/10-token-cache-check.txt) |

## 4. 关键证据

### 4.1 `member.add`

CLI 返回：

- `ok=true`
- `action=feishu.chat.member.add`
- `added_member_ids` 包含赵志鸿

延迟核对后成员列表包含 3 人：

- 王文哲
- 赵传耀
- 赵志鸿

### 4.2 `member.remove`

CLI 返回：

- `ok=true`
- `action=feishu.chat.member.remove`
- `removed_member_id` 为赵志鸿

延迟核对后成员列表回到 2 人：

- 王文哲
- 赵传耀

### 4.3 远端错误语义

非法 `chat_id` 返回：

- `ok=false`
- `error.code=feishu_api_error`
- `error.message` 来自飞书远端响应

这说明程序员对远端错误解析的修复已经生效。

### 4.4 token cache

同一进程内验证结果：

- `fetch_count=1`
- `same_token=True`
- `cache_reused=True`

## 5. 清理状态

当前测试群已恢复到初始 2 人状态：

- `oc_4ebf14a797cca2cee684bfc6c50288fb`

第一轮补充建群：

- `oc_fafc6d23bd882bf80d10bd8075a211db`

如果后续不再需要，建议人工清理。

## 6. 结论

第二轮回归没有发现需要打回 programmer 的阻断问题。

当前版本已满足第二轮回归目标，第一阶段剩余工作只应是常规收尾，不再是修复回流。
