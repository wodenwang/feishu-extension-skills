# 第二轮回归报告

日期：2026-03-28  
执行方式：真实回归  
环境：本地 `.venv`，测试租户  
应用：`cli_xxx`

## 1. 回归结论

第二轮回归通过。

结论：

- `feishu-chat-member-add` 在 `member_id_type=open_id` 下真实生效
- `feishu-chat-member-remove` 在 `member_id_type=open_id` 下真实生效
- 非法 `chat_id` 返回远端 `feishu_api_error`
- token cache 同进程复用成立

## 2. 测试数据

测试成员：

- 王小明：`ou_xxx_owner`
- 赵小华：`ou_xxx_member_a`
- 孙小宁：`ou_xxx_member_b`

说明：

- 真实凭证、真实群 ID、真实返回报文和证据文件已保存在本地忽略目录，不再提交到 GitHub。

## 3. 关键结果

- `member.add` 后延迟核对可见孙小宁进入群
- `member.remove` 后延迟核对可见孙小宁退出群
- 非法 `chat_id` 保留远端错误语义
- token cache 观察到同进程仅触发 1 次底层 fetch

## 4. 结论

第二轮回归没有再发现阻断性问题。当前仓库中仅保留脱敏后的结论性文档，本地证据不入库。
