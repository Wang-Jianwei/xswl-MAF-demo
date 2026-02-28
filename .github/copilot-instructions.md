# Project Guidelines

## Code Style
- 使用 Python 3.10+，优先类型注解与 `dataclass(slots=True)`，参考 `src/maf_devflow/config.py`。
- 业务模块按职责拆分：配置、Agent 构建、流程编排、CLI，参考 `src/maf_devflow/`。
- 命名约定：函数/变量使用 `snake_case`，类使用 `PascalCase`。
- 输出文案以中文为主，提示信息需可直接执行，参考 `src/maf_devflow/cli.py`。

## Architecture
- 当前是单包结构：`src/maf_devflow` + `tests`，用于快速验证多 Agent 协作流程。
- 核心数据流：用户需求 -> 规格拆解 -> 架构设计 -> 实现计划 -> 评审结论。
- 流程调度位于 `DevelopmentWorkflow`，支持 `sequential` 与 `concurrent`，见 `src/maf_devflow/workflow.py`。
- Agent 实例统一在 `create_agents` 中创建，避免在业务逻辑层重复初始化，见 `src/maf_devflow/agents.py`。

## Build and Test
- 创建环境（Windows）：`python -m venv .venv` 与 `.\.venv\Scripts\Activate.ps1`。
- 安装依赖：`pip install -e .`。
- 运行 CLI：`maf-devflow "<需求描述>" --mode sequential|concurrent`。
- 离线验证：`maf-devflow "<需求描述>" --dry-run`。
- 测试命令：`pytest -q`。

## Project Conventions
- 配置从环境变量读取并集中校验，新增变量时同步更新 `src/maf_devflow/config.py` 与 `.env.example`。
- 多模型支持：`Settings.get_model_id(agent_role)` 按角色返回模型，未配置则用默认 `MAF_MODEL_ID`。
- 处理模型响应时使用统一转换函数 `_response_to_text`，避免各处手写解析逻辑，见 `src/maf_devflow/workflow.py`。
- 默认先实现最小可运行能力，再增加新编排模式或持久化能力。
- CLI 发生异常时必须给出可执行的修复建议，参考 `src/maf_devflow/cli.py`。

## Integration Points
- OpenAI 路径：`agent_framework.openai.OpenAIChatClient`（由 `MAF_PROVIDER=openai` 选择）。
- Azure 路径：`agent_framework.azure.AzureOpenAIResponsesClient` + `AzureCliCredential`（由 `MAF_PROVIDER=azure` 选择）。
- Ollama 路径：`agent_framework.ollama.OllamaChatClient`（由 `MAF_PROVIDER=ollama` 选择）。
- vLLM/本地部署：通过 `OPENAI_API_BASE` 指定自定义 endpoint，OpenAI 兼容 API（`MAF_PROVIDER=openai` + `OPENAI_API_BASE`）。
- 所有外部接入点都应在 `create_agents` 层封装，不要把凭据逻辑分散到 workflow。

## Security
- 禁止在代码、测试、日志中写入真实密钥；使用 `.env` 本地注入，`.env.example` 仅放占位符。
- 对用户输入和模型输出默认不可信，涉及执行命令/代码时先加白名单或人工确认。
- 若新增工具调用（文件、网络、系统命令），需在 README 说明数据流向与最小权限策略。
