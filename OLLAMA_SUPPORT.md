# Ollama 支持验证

## 代码路径确认

| 定位 | 内容 | 状态 |
|------|------|------|
| [config.py](../src/maf_devflow/config.py#L40) | `OLLAMA_ENDPOINT` 配置读取 | ✅ |
| [agents.py](../src/maf_devflow/agents.py#L39-L45) | `OllamaChatClient(host=endpoint, model_id=model)` | ✅ |
| `.env.example` | Ollama 配置示例 | ✅ |

## 关键参数修正

本项目中 `OllamaChatClient` 使用**标准 Agent Framework 参数**：

```python
# ✓ 正确方式（Agent Framework 标准）
OllamaChatClient(
    host="http://localhost:11434",     # Ollama 服务地址
    model_id="mistral"                 # 模型 ID
)

# ✗ 错误方式（不被支持）
OllamaChatClient(endpoint="...", model_id="...")  # ❌ endpoint 参数不存在
```

## 使用方法

### 方式 1：通过 .env 配置（推荐 CLI）

```bash
# 编辑 .env
echo "MAF_PROVIDER=ollama" >> .env
echo "OLLAMA_ENDPOINT=http://localhost:11434" >> .env
echo "MAF_MODEL_ID=mistral" >> .env

# 启动 Ollama 服务
ollama serve

# 在另一个终端运行 CLI
maf-devflow "实现一个简单的 Todo 系统" --mode sequential
```

### 方式 2：直接在代码中配置（推荐 Python 脚本）

```python
import asyncio
from agent_framework.ollama import OllamaChatClient
from maf_devflow.agents import DevAgents
from maf_devflow.workflow import DevelopmentWorkflow

async def main():
    # 创建客户端（使用 host 参数）
    client = OllamaChatClient(
        host="http://localhost:11434",
        model_id="mistral"
    )
    
    # 创建 Agent
    agents = DevAgents(
        product_manager=client.as_agent(...),
        architect=client.as_agent(...),
        developer=client.as_agent(...),
        reviewer=client.as_agent(...)
    )
    
    # 运行工作流
    workflow = DevelopmentWorkflow(agents)
    result = await workflow.run("需求描述")

asyncio.run(main())
```

## 前置条件

### 安装 Ollama

```bash
# macOS / Linux
curl https://ollama.ai/install.sh | sh

# Windows
# 下载: https://ollama.ai/download/windows
# 或使用 Windows Subsystem for Linux (WSL)
```

### 拉取模型

```bash
# 标准模型
ollama pull mistral          # 7B，轻量，快速
ollama pull neural-chat      # 7B，对话友好
ollama pull llama2           # 7B，通用能力
ollama pull qwen             # 7B，中文优化

# 大型模型（需要更多资源）
ollama pull llama2:13b       # 13B
ollama pull neural-chat:34b # 34B
ollama pull qwen:72b        # 72B
```

### 启动服务

```bash
# 后台启动（Linux/macOS）
ollama serve &

# 前台启动（Windows/Linux/macOS）
ollama serve

# 检查服务
curl http://localhost:11434/api/tags
```

## 完整示例

创建文件 `ollama_test.py`：

```python
#!/usr/bin/env python
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent_framework.ollama import OllamaChatClient
from maf_devflow.agents import DevAgents
from maf_devflow.workflow import DevelopmentWorkflow


async def main():
    # 创建两个客户端（混合模型）
    print("[1] 创建 Ollama 客户端...")
    
    light = OllamaChatClient(
        host="http://localhost:11434",
        model_id="mistral"
    )
    
    heavy = OllamaChatClient(
        host="http://localhost:11434",
        model_id="llama2"
    )
    
    # 创建 Agent
    print("[2] 创建 Agent...")
    agents = DevAgents(
        product_manager=light.as_agent(
            name="PM",
            instructions="快速拆解需求"
        ),
        architect=heavy.as_agent(
            name="Arch",
            instructions="设计架构"
        ),
        developer=heavy.as_agent(
            name="Dev",
            instructions="输出实现计划"
        ),
        reviewer=heavy.as_agent(
            name="Review",
            instructions="评审建议"
        ),
    )
    
    # 执行
    print("[3] 执行工作流...")
    workflow = DevelopmentWorkflow(agents)
    result = await workflow.run(
        "实现一个解析 JSON 的 Python 函数",
        mode="sequential"
    )
    
    print(f"\n✓ 需求: {result.requirement_spec[:50]}...")
    print(f"✓ 架构: {result.architecture_design[:50]}...")
    print(f"✓ 实现: {result.implementation_plan[:50]}...")
    print(f"✓ 评审: {result.review_report[:50]}...")


if __name__ == "__main__":
    asyncio.run(main())
```

运行：

```bash
python ollama_test.py
```

## 在线示例

查看 [examples/ollama_example.py](ollama_example.py)：

```bash
# 显示模型库速查表
python examples/ollama_example.py --mode guide

# 直接运行（需要 Ollama 已启动）
python examples/ollama_example.py --mode direct

# 通过 .env 环境变量运行
python examples/ollama_example.py --mode env
```

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| `Connection refused` | 检查 Ollama 是否启动: `ollama serve` |
| `Model not found` | 拉取模型: `ollama pull mistral` |
| `Endpoint not reachable` | 检查 OLLAMA_ENDPOINT 地址（default: <http://localhost:11434）> |
| 响应超时 | 使用更轻量的模型，或增加 timeout |

## 成本优化

混合使用轻量模型和强力模型：

```python
# 轻量级：需求拆解（3.5B - 7B）
light = OllamaChatClient(
    host="http://localhost:11434",
    model_id="mistral"
)

# 强力：架构、实现、评审（13B - 70B）
heavy = OllamaChatClient(
    host="http://localhost:11434",
    model_id="llama2:13b"
)

# 为不同 Agent 分配
agents = DevAgents(
    product_manager=light.as_agent(...),   # 快速
    architect=heavy.as_agent(...),         # 精准
    developer=heavy.as_agent(...),         # 精准
    reviewer=heavy.as_agent(...),          # 精准
)
```

## 总结

✅ **Ollama 完全支持**

- `agents.py` 中有 `OllamaChatClient` 创建逻辑
- `config.py` 有 `ollama_endpoint` 配置
- 支持多模型混合（轻量 + 强力）
- 支持本地完全离线运行
