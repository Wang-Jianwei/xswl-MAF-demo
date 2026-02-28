#!/usr/bin/env python
"""
Ollama 本地模型启动示例

前置条件：
1. 安装 Ollama: https://ollama.ai
2. 启动服务: ollama serve
3. 拉取模型: ollama pull mistral (或其他模型)
   - 支持模型: llama2, mistral, neural-chat, qwen, etc.

此脚本展示两种使用方式：
- 方式 A: 通过 .env 文件配置（推荐用于 CLI）
- 方式 B: 直接在代码中配置（推荐用于 Python 脚本）
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_framework.ollama import OllamaChatClient
from maf_devflow.workflow import DevelopmentWorkflow
from maf_devflow.agents import DevAgents


async def main_direct():
    """方式 B：直接在代码中创建 Ollama 客户端"""
    print("=" * 60)
    print("[Ollama 直接方式] 创建本地模型客户端")
    print("=" * 60)

    # Ollama endpoint（默认 http://localhost:11434）
    ollama_endpoint = "http://localhost:11434"
    
    # 创建客户端：轻量级 + 强力模型组合
    # 根据本地资源选择：
    # - 轻量: mistral (7B), neural-chat (7B)
    # - 中量: qwen (14B), llama2-13b
    # - 重量: llama2-70b, qwen:72b
    
    print(f"\n[1] 创建客户端...")
    light_client = OllamaChatClient(
        host=ollama_endpoint,
        model_id="mistral"  # 轻量级模型：需求拆解
    )
    print(f"  ✓ Light: mistral @ {ollama_endpoint}")
    
    heavy_client = OllamaChatClient(
        host=ollama_endpoint,
        model_id="neural-chat"  # 更强力的模型：架构、实现、评审
    )
    print(f"  ✓ Heavy: neural-chat @ {ollama_endpoint}")

    print(f"\n[2] 创建 Agent...")
    agents = DevAgents(
        product_manager=light_client.as_agent(
            name="ProductManager",
            instructions="你是产品经理。快速拆解需求为清晰的目标、约束、验收标准。输出结构化清单。"
        ),
        architect=heavy_client.as_agent(
            name="Architect",
            instructions="你是架构师。基于需求给出模块划分、数据流、技术选型建议。"
        ),
        developer=heavy_client.as_agent(
            name="Developer",
            instructions="你是开发工程师。给出实现步骤、关键函数签名、代码建议。"
        ),
        reviewer=heavy_client.as_agent(
            name="Reviewer",
            instructions="你是代码评审。评估需求覆盖、可行性、风险、测试策略。"
        ),
    )
    print("  ✓ ProductManager (mistral)")
    print("  ✓ Architect, Developer, Reviewer (neural-chat)")

    print(f"\n[3] 执行工作流...")
    feature_request = """
    实现一个简单的 Python web 框架路由系统：
    - 支持 GET/POST/PUT/DELETE
    - 支持路由参数提取
    - 支持中间件链
    """
    
    workflow = DevelopmentWorkflow(agents)
    try:
        result = await workflow.run(feature_request, mode="sequential")
        
        print(f"\n✓ 工作流完成！")
        print(f"\n[需求规格] {result.requirement_spec[:100]}...")
        print(f"\n[架构设计] {result.architecture_design[:100]}...")
        print(f"\n[实现计划] {result.implementation_plan[:100]}...")
        print(f"\n[评审意见] {result.review_report[:100]}...")
    except Exception as e:
        print(f"\n✗ 执行失败: {e}")
        print(f"\n提示：")
        print(f"  1. 确保 Ollama 已启动: ollama serve")
        print(f"  2. 确保模型已拉取: ollama pull mistral neural-chat")
        print(f"  3. 检查 Ollama 服务地址: http://localhost:11434")


async def main_via_env():
    """方式 A：通过环境变量配置（需要 .env 文件）"""
    from dotenv import load_dotenv
    from maf_devflow.config import Settings
    from maf_devflow.agents import create_agents
    
    print("\n" + "=" * 60)
    print("[Ollama 环境变量方式] 通过 .env 配置启动")
    print("=" * 60)
    
    # 加载 .env 文件
    # 确保 .env 中包含：
    # MAF_PROVIDER=ollama
    # OLLAMA_ENDPOINT=http://localhost:11434
    # MAF_MODEL_ID=mistral
    load_dotenv(Path(__file__).parent.parent / ".env")
    
    settings = Settings.from_env()
    print(f"\n[配置] Provider: {settings.provider}")
    print(f"[配置] Ollama Endpoint: {settings.ollama_endpoint}")
    print(f"[配置] Default Model: {settings.model_id}")
    
    if settings.provider != "ollama":
        print("\n⚠️  当前 .env 中 MAF_PROVIDER 不是 'ollama'")
        print("   请在 .env 中设置:")
        print("     MAF_PROVIDER=ollama")
        print("     OLLAMA_ENDPOINT=http://localhost:11434")
        print("     MAF_MODEL_ID=mistral")
        return
    
    try:
        agents = create_agents(settings)
        print(f"\n✓ 创建了 4 个 Agent")
        
        workflow = DevelopmentWorkflow(agents)
        # 只做验证，不实际执行
        print(f"✓ 工作流已就绪，可调用 workflow.run(...)")
    except Exception as e:
        print(f"\n✗ 配置失败: {e}")


# ============ 速查表 ============
OLLAMA_MODELS_GUIDE = """

【Ollama 模型速查】

轻量模型（推荐用于需求拆解）:
  mistral (7B)      - 快速、均衡
  neural-chat (7B)  - 对话友好
  phi (3B)          - 超轻量
  
中等模型（推荐用于架构、实现）:
  llama2 (13B)      - 多能，通用
  qwen:14b          - 中文友好
  
重量模型（GPU充足时）:
  llama2-70b        - 强力，完全推荐
  deepseek-coder    - 代码能力强
  
启动命令:
  ollama pull mistral           # 拉取轻量模型
  ollama pull neural-chat       # 拉取对话模型
  ollama serve                  # 启动服务

查看已有模型:
  ollama list
"""


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ollama 模型工作流示例")
    parser.add_argument(
        "--mode",
        choices=["direct", "env", "guide"],
        default="direct",
        help="执行模式: direct=直接方式, env=环境变量方式, guide=显示模型库"
    )
    
    args = parser.parse_args()
    
    if args.mode == "guide":
        print(OLLAMA_MODELS_GUIDE)
    elif args.mode == "direct":
        asyncio.run(main_direct())
    else:
        asyncio.run(main_via_env())
