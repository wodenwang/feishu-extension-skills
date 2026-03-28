# 第一阶段执行前检查清单

本文档用于在正式启动 agent teams 编码、测试之前做最后一轮准备。

目标不是重复规划，而是把“还没落地的关键前置项”明确出来，避免多 agent 开工后再返工。

## 1. 必须先完成的事项

以下事项建议在正式编码前完成：

1. 冻结接口草案
2. 明确技术实现路线
3. 固化测试策略
4. 创建真实代码文件骨架
5. 创建真实 `SKILL.md` 骨架
6. 准备联调环境与验收口径

## 2. 当前仍缺的重要项

### 2.1 接口还没有真正冻结

虽然 `AGENTS.md` 已列出冻结点，但当前仓库里还没有对应的实际接口草案文件。

建议先落成最小代码或接口文档：

- `InvokeRequest`
- `ActionResult`
- `AuthContext`
- `get_tenant_access_token(auth_context)`
- `get_auth_headers(auth_context)`
- `feishu.chat.create`
- `feishu.chat.members.list`
- `feishu.chat.member.add`
- `feishu.chat.member.remove`

如果不先落这一步，多 agent 会各自按自己的理解写模型，后面集成一定冲突。

### 2.2 第一阶段到底走 SDK 还是原始 HTTP，尚未定死

当前文档写的是“优先 SDK，必要时回退 HTTP”，但第一阶段更适合先做单一路线。

建议在开工前明确：

- 第一阶段默认是否直接使用 `httpx`
- 还是直接用飞书官方 Python SDK
- 如果两者并存，谁是主实现，谁是 fallback

否则 `core-auth` 和 `im-chat` agent 会在 client 层走出两套风格。

### 2.3 测试策略只有原则，没有样例文件

目前 `tests/` 目录只有空骨架，还没有：

- `conftest.py`
- mock client 约定
- fixture 命名规则
- smoke test 输入样例

建议正式编码前，至少先补：

- `tests/unit/conftest.py`
- `tests/smoke/cli/conftest.py`
- 一份最小测试命名约定

### 2.4 Skill 目录仍然只有占位目录

`skills/feishu-chat-*` 目录已经建了，但还没有真正的 `SKILL.md`。

如果要让 `skills-docs` agent 并行工作，建议先把 4 个第一阶段 Skill 的文件创建出来，即使先写最小占位内容也可以。

### 2.5 缺少包管理与开发命令入口

在正式编码前，建议先补以下至少一项：

- `pyproject.toml`
- 或 `requirements.txt` + `requirements-dev.txt`

并明确开发命令：

- 安装依赖
- 运行单元测试
- 运行 smoke test
- 执行 CLI

没有这一步，agent teams 会各自假设依赖管理方式。

## 3. 强烈建议补充但不一定阻塞开工的事项

### 3.1 明确真实飞书联调租户

建议先确认：

- 用哪个飞书应用做第一阶段联调
- 是否已有 `app_id` / `app_secret`
- 权限是否已申请
- 是否有专门测试群或测试成员

### 3.2 明确错误码映射策略

建议先决定：

- 是保留飞书原始错误码
- 还是统一映射为内部错误类型
- CLI 输出里保留哪些字段

### 3.3 明确日志最小字段

建议先统一：

- `action`
- `app_id` 的脱敏形式
- `chat_id`
- `request_id`
- `status`

## 4. 建议的开工顺序

正式编码前，推荐先做这 5 步：

1. 补 `pyproject.toml` 与基础开发命令
2. 补接口冻结草案文件
3. 补测试骨架文件与最小 fixture
4. 补 4 个第一阶段 `SKILL.md`
5. 再按 `AGENTS.md` 分波次并行开发

## 5. 开工判定标准

满足以下条件后，再让 agent teams 正式进入编码：

- 接口冻结草案已存在
- 依赖管理方式已确定
- 测试入口已存在
- 第一阶段 Skill 文件已存在
- 联调租户与权限准备完成

如果这些条件还没满足，现在进入多 agent 并行开发，返工概率会偏高。
