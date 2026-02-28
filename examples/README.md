# 示例脚本

## 最小化示例

```bash
python examples/minimal_devflow.py
```

直接调用 `DevelopmentWorkflow`，适合快速开始。

## 并发执行示例

```bash
python examples/concurrent_devflow.py
```

展示如何使用 `mode="concurrent"` 来并行执行架构与实现设计，提升速度。

## 高级示例：自定义流程

```bash
# 多轮迭代优化
python examples/custom_workflow.py

# 批量处理多个需求
python examples/custom_workflow.py batch
```

展示：

- 多轮迭代工作流（基于前一步评审改进）
- 批量处理（asyncio.gather 并行化）
- 直接调用单个 Agent 的能力

## 多模型配置示例

```bash
# 为不同 Agent 分配不同的模型（成本/性能优化）
python examples/multi_model_example.py
```

在 `.env` 中配置每个角色使用的模型。看 `.env.example` 中的示例配置。

## vLLM 本地模型示例

```bash
# 使用本地 vLLM 部署的模型（如 Qwen3.5）
cp examples/.env.vllm .env
# 编辑 .env，填入你的 vLLM API endpoint
python examples/vllm_example.py
```

支持配置多个 vLLM 服务实例并为不同 Agent 分配不同模型。

## Ollama 本地模型示例

```bash
# 使用 Ollama 离线模型（推荐本地开发）
python examples/ollama_example.py --mode direct
```

前置条件：

```bash
# 1. 安装 Ollama: https://ollama.ai
# 2. 启动服务
ollama serve

# 3. 在另一个终端拉取模型
ollama pull mistral
ollama pull neural-chat
```

示例脚本支持三种运行方式：

- `--mode direct`: 在代码中直接创建 Ollama 客户端（推荐）
- `--mode env`: 通过 .env 配置（需要先配置 `MAF_PROVIDER=ollama`）
- `--mode guide`: 显示 Ollama 模型库速查表

## 直接创建客户端示例（高级）

```bash
# 在代码中直接创建多个客户端，用不同 vLLM 服务实例
python examples/direct_client_example.py
```

展示如何：

- 创建两个不同的 OpenAI 兼容客户端
- 为不同 Agent 分配不同的模型和服务端点
- 优化成本：快速任务用轻量模型，复杂任务用强力模型

### 最快开始（3 行代码）

```bash
# 超简化版本
python examples/quick_vllm.py
```

如果只想快速验证，这个脚本直接硬编码了你的 vLLM 配置。

## 核心 API

```python
from maf_devflow.config import Settings
from maf_devflow.agents import create_agents
from maf_devflow.workflow import DevelopmentWorkflow
import asyncio

async def main():
    # 1. 加载配置
    settings = Settings.from_env()
    settings.validate()

    # 2. 创建 Agent
    agents = create_agents(settings)

    # 3. 构建工作流
    workflow = DevelopmentWorkflow(agents)

    # 4. 运行
    result = await workflow.run(
        feature_request="你的需求",
        mode="sequential"  # 或 "concurrent"
    )

    # 5. 获取结果
    print(result.requirement_spec)
    print(result.architecture_design)
    print(result.implementation_plan)
    print(result.review_report)

asyncio.run(main())
```

## 环境配置

在运行示例前，复制 `.env` 并填写：

```bash
cp .env.example .env
```

选择你的模型提供商，见 [README.md](../README.md) 配置段落。
