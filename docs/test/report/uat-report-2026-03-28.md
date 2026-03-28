# UAT 报告

日期：2026-03-28  
执行方式：真实联调  
环境：本地 `.venv`，测试租户  
应用：`cli_xxx`

## 1. 执行摘要

本次 UAT 的主链路结论如下：

- `feishu-chat-create`：通过
- `feishu-chat-members-list`：通过
- `feishu-chat-member-add`：失败
- `feishu-chat-member-remove`：失败
- token 缓存复用：通过（同进程）

## 2. 测试数据

测试成员：

- 王小明：`ou_xxx_owner`
- 赵小华：`ou_xxx_member_a`
- 孙小宁：`ou_xxx_member_b`

说明：

- 真实凭证、真实成员标识、真实群 ID 和原始联调证据已转移到本地忽略目录，不再提交到 GitHub。

## 3. 关键发现

### 3.1 `member.add` 返回成功不等于真实入群

第一次 UAT 暴露出一个问题：CLI 返回成功时，仍需通过后续 `members.list` 做延迟核对，不能只看即时返回值。

### 3.2 `member.remove` 需要按真实接口语义验证

移人链路需要以真实群成员变化为准，而不是只看本地封装状态。

### 3.3 远端错误语义需要保留

非法群 ID 不应被误包成本地校验错误，应该尽量保留为远端 `feishu_api_error`。

## 4. 结论

这次首轮 UAT 的主要价值是暴露真实接口与本地封装之间的偏差。后续修复回归请参考：

- [uat-regression-round2.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/report/uat-regression-round2.md)
