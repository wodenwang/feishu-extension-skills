# feishu-extension-skills

面向 OpenClaw 的飞书扩展 Skills 项目。

本项目用于补充飞书官方 OpenClaw 插件尚未覆盖或封装不完整的能力，统一基于飞书服务端 API 实现。第一阶段主实现固定为 Python + `httpx`，后续阶段再评估是否引入官方 SDK 作为补充实现。

## 项目目标

- 为 OpenClaw 提供可直接加载的飞书 Skill。
- 以飞书服务端 API 为核心，覆盖消息、文档、知识库、多维表格、任务、日历、通讯录等能力。
- 将鉴权与 Access Token 维护独立抽象，避免每个 Skill 重复处理认证。
- 统一 Skill 调用入口、参数校验、错误处理、日志与限流策略。

## 当前初始化范围

当前仓库已经完成文档初始化，接下来进入第一阶段执行：围绕群组模块构建最小可运行系统。

- 飞书服务端 API 模块规划：[docs/feishu-server-api-plan.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/feishu-server-api-plan.md)
- 第一阶段实施文档索引：[docs/phase-1/README.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/phase-1/README.md)
- 第一阶段接口冻结：[docs/phase-1/interface-freeze.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/docs/phase-1/interface-freeze.md)
- Agent Teams 协作规范：[AGENTS.md](/Users/wenzhewang/workspace/codex/feishu-extension-skills/AGENTS.md)

## 文档分工

- `README.md`：项目入口、当前阶段、文档导航
- `AGENTS.md`：执行阶段的 agent teams 协作规范
- `docs/feishu-server-api-plan.md`：全项目的模块规划与阶段优先级
- `docs/phase-1/`：第一阶段的实施细节、模块文档、Skill 文档、权限汇总

## 建议目录结构

```text
.
├── README.md
├── docs/
│   ├── feishu-server-api-plan.md
│   └── phase-1/
├── skills/
│   ├── feishu-message-send/
│   ├── feishu-docx-create/
│   ├── feishu-bitable-record-upsert/
│   └── ...
├── src/
│   └── feishu_extension_skills/
│       ├── core/
│       ├── auth/
│       ├── runtime/
│       ├── services/
│       └── cli/
└── tests/
```

## 技术栈建议

- Python 3.11+
- CLI：`typer`
- 数据模型：`pydantic`
- HTTP：`httpx`
- 测试：`pytest`

## 第一阶段开发命令

```bash
python -m pip install -e '.[dev]'
python -m pytest
python -m feishu_extension_skills.cli invoke <action> --args-json '<json>'
```

## 参考资料

- GitHub 仓库：[wodenwang/feishu-extension-skills](https://github.com/wodenwang/feishu-extension-skills.git)
- 飞书官方 OpenClaw 插件文章：[OpenClaw 飞书官方插件上线](https://www.feishu.cn/content/article/7613711414611463386)
- 飞书 AI Assistant 代码生成指南：[AI assistant code generation guide](https://open.feishu.cn/document/ukTMukTMukTM/ukDNz4SO0MjL5QzM/AI-assistant-code-generation-guide)
- 飞书官方 Python SDK：[larksuite/oapi-sdk-python](https://github.com/larksuite/oapi-sdk-python)
- OpenClaw Skills 文档：[Skills - OpenClaw](https://docs.openclaw.ai/tools/skills)
