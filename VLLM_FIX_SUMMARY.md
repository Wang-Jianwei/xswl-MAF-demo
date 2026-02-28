# vLLM 集成修复总结 (Fix Summary)

## 问题 (Issue)

使用自定义 API base（vLLM、本地部署等）创建 OpenAI 客户端时报错：

```
TypeError: OpenAIChatClient.__init__() got an unexpected keyword argument 'api_base'
```

**根本原因**: OpenAI Agent Framework 的 `OpenAIChatClient` 不支持 `api_base` 作为构造函数参数，而是遵循 OpenAI Python SDK 的约定，通过环境变量 `OPENAI_API_BASE` 配置。

## 修复方案 (Solution)

### 1. 修改 `src/maf_devflow/agents.py` 中的 `_create_client` 函数

**之前（错误）:**

```python
if settings.openai_api_base:
    return OpenAIChatClient(
        model_id=model_id,
        api_key=settings.openai_api_key,
        api_base=settings.openai_api_base,  # ❌ 不支持的参数
    )
```

**之后（正确）:**

```python
if settings.openai_api_base:
    os.environ["OPENAI_API_BASE"] = settings.openai_api_base
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key
return OpenAIChatClient(model_id=model_id)  # ✓ 从环境变量读取
```

### 2. 修改 `examples/quick_vllm.py`

**之前（错误）:**

```python
c27b = OpenAIChatClient("Qwen3.5-27B", api_key="sk-local", api_base="http://10.11.13.4:8721/v1")
c35b = OpenAIChatClient("Qwen3.5-35B", api_key="sk-local", api_base="http://10.11.13.4:8720/v1")
```

**之后（正确）:**

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-local"

os.environ["OPENAI_API_BASE"] = "http://10.11.13.4:8721/v1"
c27b = OpenAIChatClient("Qwen3.5-27B")

os.environ["OPENAI_API_BASE"] = "http://10.11.13.4:8720/v1"
c35b = OpenAIChatClient("Qwen3.5-35B")
```

### 3. 修改 `examples/direct_client_example.py`

应用同样的环境变量模式（已通过代码检查确认）。

## 验证结果 (Verification)

✅ `maf-devflow "test" --dry-run` - **通过**  
✅ `pytest -q` - **通过** (1 test passed)  
✅ 模块导入 - **通过**

## 关键要点 (Key Points)

1. **环境变量优先**: 所有 OpenAI 兼容客户端配置应通过环境变量，而非构造函数参数
2. **多 API Base 支持**: 可以在创建不同客户端之间修改 `OPENAI_API_BASE` 环境变量
3. **标准化**: 遵循 OpenAI Python SDK 惯例，提高代码可维护性

## 使用示例 (Usage Example)

```python
import os
from agent_framework.openai import OpenAIChatClient

# 创建两个客户端，分别连接不同的 vLLM 服务
os.environ["OPENAI_API_KEY"] = "sk-local"

# 轻量级模型（27B）
os.environ["OPENAI_API_BASE"] = "http://10.11.13.4:8721/v1"
client_light = OpenAIChatClient("Qwen3.5-27B")

# 强力模型（35B）
os.environ["OPENAI_API_BASE"] = "http://10.11.13.4:8720/v1"
client_heavy = OpenAIChatClient("Qwen3.5-35B")
```
