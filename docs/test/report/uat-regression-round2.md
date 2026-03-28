# 第二轮回归检查单

本文档用于第一轮 UAT 之后的第二轮回归。目标不是重新做完整 UAT，而是对第一轮暴露的缺陷做定点回归，确认程序员修复是否有效。

## 1. 回归目标

本轮只覆盖第一轮明确暴露的问题：

- `feishu-chat-member-add` 的假阳性
- `feishu-chat-member-remove` 的端点与参数映射
- 远端错误语义是否被误包成 `validation_error`
- token cache 观察点是否仍保持稳定

## 2. 需要回归的变更点

回归前先确认程序员是否已经提交修复：

- `member.add` 的返回值应只反映真实接口结果，不应把输入成员直接当作已加入成员
- `member.remove` 应命中真实端点，并按 Feishu 官方约定传参
- 非 2xx 或远端错误应保留为远端错误语义，不应误判为本地校验错误

## 3. 回归前提

- 当前程序已更新到最新修复版本
- 仍使用同一组 `app_id` / `app_secret`
- 仍使用第一轮的测试成员
- 回归优先在第一轮遗留测试群上执行，避免重复建群

## 4. 回归用例

### R2-001: `member.add` 真正生效

前置条件：

- 目标群当前不包含孙小宁

步骤：

1. 调用 `feishu-chat-member-add`
2. 传入孙小宁的标识
3. 立即调用 `feishu-chat-members-list`

预期：

- `member.add` 返回 `ok=true`
- 返回值中的已加入成员与真实成员列表一致
- 成员列表能看到孙小宁

判定点：

- 如果返回成功但成员列表无变化，直接打回 programmer

### R2-002: `member.remove` 真正生效

前置条件：

- 目标群包含孙小宁

步骤：

1. 调用 `feishu-chat-member-remove`
2. 传入孙小宁标识
3. 立即调用 `feishu-chat-members-list`

预期：

- `member.remove` 返回 `ok=true`
- 返回值中的移除成员与真实成员列表一致
- 成员列表不再包含孙小宁

判定点：

- 如果仍返回 `404 page not found` 或类似端点错误，直接打回 programmer

### R2-003: 远端错误语义保留

步骤：

1. 调用 `feishu-chat-members-list`
2. 使用明显无效的 `chat_id`

预期：

- 返回 `ok=false`
- `error.code` 应体现远端错误或 HTTP 错误语义
- 不应被误包成 `validation_error`

判定点：

- 如果错误仍被包装成本地校验错误，打回 programmer

### R2-004: token cache 观察

步骤：

1. 连续调用两次同一 action
2. 观察 token 获取行为

预期：

- 同进程内复用依然成立
- 如果程序员改成跨进程缓存，需要在报告里明确说明实现方式

## 5. 回归执行顺序

推荐顺序：

1. 先跑 `R2-003`，确认错误语义是否正确
2. 再跑 `R2-001`，验证加人是否真实生效
3. 再跑 `R2-002`，验证移人是否真实生效
4. 最后跑 `R2-004`，确认 token cache 行为没有回退

## 6. 回归证据记录模板

```text
Round 2 Run ID:
Date:
Executor:
Programmer handoff commit / patch:
Environment:
Chat ID:

Case ID | Result | Evidence | Needs programmer follow-up
-------- | ------ | -------- | --------------------------
R2-001 | ... | ... | yes/no
R2-002 | ... | ... | yes/no
R2-003 | ... | ... | yes/no
R2-004 | ... | ... | yes/no
```

## 7. 打回标准

出现以下任一情况，直接打回 programmer：

- `member.add` 仍然是假阳性
- `member.remove` 仍然走错端点
- 远端错误仍被误包成 `validation_error`
- 回归中出现新的 CLI 或 action 退化

## 8. 备注

- 本检查单只用于第二轮回归
- 如果回归过程中发现新问题，需要在报告里单独列出，不要混进第一轮总结
