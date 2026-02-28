# maf-devflow

基于 Microsoft Agent Framework 的 Python 多 Agent 协作开发流程工具。

## 功能

- 多角色协作：产品经理、架构师、开发工程师、评审工程师
- 两种流程模式：`sequential`（串行）与 `concurrent`（并发）
- 命令行工具：输入一个需求，输出完整的开发流程产物
- `--dry-run` 离线模式：不依赖模型和 API，用于本地冒烟验证
- 可选工具执行层：支持受控文件读写与白名单命令执行（默认关闭）

## 环境要求

- Python 3.10+
- Windows / macOS / Linux

## 安装

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -e .
```

## 配置

```bash
# 复制模板后填写
cp .env.example .env
```

### OpenAI 模式

- `MAF_PROVIDER=openai`
- `OPENAI_API_KEY=...`
- `MAF_MODEL_ID=gpt-4.1-mini`（可改）

#### 可选：使用本地 vLLM 或其他 OpenAI 兼容服务

```bash
# .env 配置
MAF_PROVIDER=openai
OPENAI_API_KEY=sk-dummy  # 本地服务可以是任意值
OPENAI_API_BASE=http://10.11.13.4:8721/v1  # 你的 vLLM 服务地址
MAF_MODEL_ID=Qwen3.5-27B  # 你在 vLLM 中的模型名
```

支持同时配置多个模型：

```bash
MAF_MODEL_PRODUCT_MANAGER=Qwen3.5-27B     # 轻量级任务
MAF_MODEL_ARCHITECT=Qwen3.5-35B           # 复杂设计
MAF_MODEL_DEVELOPER=Qwen3.5-35B           # 实现计划
MAF_MODEL_REVIEWER=Qwen3.5-35B            # 严格评审
```

### Azure 模式

- `MAF_PROVIDER=azure`
- `AZURE_AI_PROJECT_ENDPOINT=...`
- `AZURE_AI_MODEL_DEPLOYMENT_NAME=...`
- 本地先执行 `az login`

### Ollama 本地模式（推荐）

#### 1. 安装 Ollama

访问 <https://ollama.ai> 下载安装，或：

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

#### 2. 启动 Ollama 服务

```bash
ollama serve
# 默认监听 http://localhost:11434
```

#### 3. 拉取模型（在新终端）

```bash
# 快速轻量模型
ollama pull mistral

# 或其他模型
ollama pull llama2
ollama pull neural-chat
ollama list  # 查看已安装模型
```

#### 4. 配置环境变量

在 `.env` 中：

```
MAF_PROVIDER=ollama
MAF_MODEL_ID=mistral
OLLAMA_ENDPOINT=http://localhost:11434
```

### 多模型支持（按角色分配不同模型）

可为不同 Agent 指定不同的模型，用于成本/性能优化。在 `.env` 中配置：

```bash
# OpenAI 示例（快速+强大+节省成本）
MAF_MODEL_ID=gpt-4.1-mini              # 默认
MAF_MODEL_PRODUCT_MANAGER=gpt-4o-mini  # 轻量级：快速拆解需求
MAF_MODEL_ARCHITECT=gpt-4               # 强力：复杂架构设计
MAF_MODEL_DEVELOPER=gpt-4               # 强力：实现计划
MAF_MODEL_REVIEWER=gpt-4                # 强力：严格评审
```

或 Ollama（成本最低）：

```bash
MAF_MODEL_ID=mistral                    # 默认
MAF_MODEL_PRODUCT_MANAGER=mistral       # 快速
MAF_MODEL_ARCHITECT=neural-chat         # 中等能力
MAF_MODEL_DEVELOPER=neural-chat         # 中等能力
MAF_MODEL_REVIEWER=llama2               # 更谨慎的评审
```

## 运行

```bash
# 串行流程
maf-devflow "实现一个支持多 agent 协作的软件研发流程工具"

# 并发流程
maf-devflow "实现一个支持多 agent 协作的软件研发流程工具" --mode concurrent

# 离线冒烟运行
maf-devflow "实现一个支持多 agent 协作的软件研发流程工具" --dry-run
```

## 可选：启用工具调用（文件/命令）

默认情况下，Agent 只进行文本推理。若要让 Developer/Reviewer 自动读写文件或执行命令，可在 `.env` 开启：

```bash
MAF_ENABLE_TOOLS=true
MAF_WORKSPACE_ROOT=.
MAF_ALLOWED_COMMANDS=python,pytest,pip
MAF_COMMAND_TIMEOUT_SECONDS=120
```

说明：

- 仅允许访问 `MAF_WORKSPACE_ROOT` 下的文件路径（防止越界访问）
- 仅允许执行白名单命令（防止任意命令执行）
- 超时可控，避免任务长时间阻塞

## 测试

```bash
pytest -q
```

## 目录结构

- `src/maf_devflow/config.py`：环境配置与校验
- `src/maf_devflow/agents.py`：MAF 客户端与角色 Agent 构建
- `src/maf_devflow/workflow.py`：多 Agent 协作流程编排
- `src/maf_devflow/cli.py`：CLI 入口
- `tests/test_workflow.py`：流程单测

## VS Code 配置

工程包含一个预配置的 `.vscode` 文件夹，方便在 Visual Studio Code 中开发：

```text
.vscode/
  ├─ settings.json      # Python 解释器、格式化和测试设置
  ├─ launch.json        # 调试当前文件/测试/CLI 的配置
  └─ tasks.json         # 安装依赖、运行测试、执行 CLI 的快捷任务
```

设置好 Python 虚拟环境后，打开项目即可自动应用这些配置。常用快捷键：

1. **Ctrl+Shift+B** 运行默认任务（安装依赖）
2. **Ctrl+Shift+P** → `Tasks: Run Task` 选择测试或 CLI
3. 在 Debug 面板选择 `Debug Tests` 或 `Debug CLI` 启动调试

这些配置让你可以轻松在 VS Code 中编辑、格式化、运行和调试代码。
