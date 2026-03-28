# feishu-extension-skills

面向 OpenClaw / ClawHub 的飞书群组 Skill 项目。

当前仓库只提供一个可发布 skill：

- `feishu-chat-server-api`

这个 skill 用飞书服务端 API 管理群组，覆盖：

- 创建群组
- 查询群详情
- 查询群成员
- 拉人入群
- 移出群成员
- 解散群组

## 在 OpenClaw 中添加 Skill

推荐直接从 ClawHub 安装：

```bash
clawhub install feishu-chat-server-api
clawhub list
```

如果你的 OpenClaw 环境需要同步本地 skill 索引，再执行：

```bash
clawhub sync --all
```

安装完成后，OpenClaw 就能读取 [skills/feishu-chat-server-api/SKILL.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/skills/feishu-chat-server-api/SKILL.md) 中的说明，并在需要飞书群组操作时调用统一 CLI。

## OpenClaw 如何使用它

OpenClaw 实际调用的是统一命令：

```bash
feishu-extension-skills invoke <action> --args-json '<json>'
```

支持的 action：

- `feishu-chat-create`
- `feishu-chat-get`
- `feishu-chat-members-list`
- `feishu-chat-member-add`
- `feishu-chat-member-remove`
- `feishu-chat-disband`

## 凭证读取优先级

当前实现支持 3 层凭证来源，优先级固定如下：

1. 显式传参
2. 本地配置文件 `.local/feishu-extension-skills.json`
3. 环境变量 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`

如果这 3 层都没有命中，会直接报错。

推荐做法：

- 生产或多租户场景优先显式传 `app_id` / `app_secret`
- 本地开发或单租户调试可用 `.local/feishu-extension-skills.json`
- CI 或临时 shell 会话可用环境变量

成员相关参数只接受飞书标识：

- `user_id`
- `open_id`

如果你传的是 `ou_...` 这类 `open_id`，记得同时传：

- `member_id_type: "open_id"`

## 本地配置文件格式

默认会读取当前工作目录下的：

```text
.local/feishu-extension-skills.json
```

示例：

```json
{
  "app_id": "cli_xxx",
  "app_secret": "sec_xxx",
  "base_url": "https://open.feishu.cn",
  "timeout_seconds": 10,
  "token_refresh_skew_seconds": 60,
  "log_level": "INFO"
}
```

仓库已经忽略 `.local/`，适合本地保存真实凭证，不会上传到 GitHub。

## 凭证优先级示例

### 1. 第一优先级：显式传参

即使本地配置文件和环境变量里也有值，显式传参仍然会覆盖它们：

```bash
feishu-extension-skills invoke feishu-chat-get --args-json '{"app_id":"cli_explicit","app_secret":"sec_explicit","chat_id":"oc_xxx"}'
```

### 2. 第二优先级：本地配置文件

如果 `--args-json` 里没传 `app_id` / `app_secret`，会读取 `.local/feishu-extension-skills.json`：

```bash
feishu-extension-skills invoke feishu-chat-get --args-json '{"chat_id":"oc_xxx"}'
```

### 3. 第三优先级：环境变量

如果前两层都没有命中，则读取环境变量：

```bash
export FEISHU_APP_ID="cli_env_xxx"
export FEISHU_APP_SECRET="sec_env_xxx"

feishu-extension-skills invoke feishu-chat-get --args-json '{"chat_id":"oc_xxx"}'
```

### 4. 都没有命中时

会返回配置错误，提示缺少 `app_id` 或 `app_secret`。

## 可直接复制的示例

下面这组示例参考了仓库里的 UAT testcase，适合直接在 OpenClaw 或命令行中理解调用方式。

### 1. 建群

```bash
feishu-extension-skills invoke feishu-chat-create --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","name":"项目临时群","user_id_list":["ou_xxx_owner"],"owner_id":"ou_xxx_owner"}'
```

### 2. 查群详情

```bash
feishu-extension-skills invoke feishu-chat-get --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","chat_id":"oc_xxx"}'
```

### 3. 查群成员

如果群成员标识按 `open_id` 返回：

```bash
feishu-extension-skills invoke feishu-chat-members-list --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","chat_id":"oc_xxx","member_id_type":"open_id"}'
```

### 4. 拉人入群

下面示例使用 `open_id` 拉人：

```bash
feishu-extension-skills invoke feishu-chat-member-add --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","chat_id":"oc_xxx","user_id_list":["ou_xxx_member_a","ou_xxx_member_b"],"member_id_type":"open_id"}'
```

### 5. 移出群成员

```bash
feishu-extension-skills invoke feishu-chat-member-remove --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","chat_id":"oc_xxx","member_id":"ou_xxx_member_b","member_id_type":"open_id"}'
```

### 6. 解散群

```bash
feishu-extension-skills invoke feishu-chat-disband --args-json '{"app_id":"cli_xxx","app_secret":"sec_xxx","chat_id":"oc_xxx"}'
```

## 在 OpenClaw 中如何描述需求

下面这类自然语言请求适合直接交给 OpenClaw：

- “用飞书 skill 建一个群，群名叫项目临时群，拉入王小明和赵小华。”
- “查询这个飞书群的详情。”
- “列出这个群当前所有成员。”
- “把孙小宁拉进这个群，成员标识用 open_id。”
- “把孙小宁从群里移除。”
- “测试结束后把这个群解散。”

## 常见注意点

- `ou_...` 是 `open_id`，不是默认的 `user_id`。
- 如果加人时报 `id not exist`，先检查是不是少传了 `member_id_type: "open_id"`。
- 当前 skill 不负责邮箱、手机号、姓名到用户 ID 的解析。
- 当前 skill 只做群组管理，不包含消息发送、卡片、文档、通讯录等能力。

## 本地开发

```bash
python3 -m pip install -e '.[dev]'
./.venv/bin/python -m pytest
```

## 文档入口

- 文档索引：[docs/README.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/README.md)
- 测试说明：[docs/test/README.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/README.md)
- UAT 用例：[docs/test/report/uat-test-cases.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/test/report/uat-test-cases.md)
- 权限汇总：[docs/permissions.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/permissions.md)

## 发布

当前 ClawHub 已发布：

- slug: `feishu-chat-server-api`

仓库内继续发布新版本可用：

```bash
./scripts/publish_clawhub.sh 0.1.2 "your changelog"
```
