#!/usr/bin/env python
"""多模型配置示例：为不同 Agent 分配不同的模型"""

import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from maf_devflow.config import Settings
from maf_devflow.agents import create_agents
from maf_devflow.workflow import DevelopmentWorkflow


async def main():
    """
    展示多模型配置。

    在 .env 中可配置：
    - MAF_MODEL_PRODUCT_MANAGER=gpt-4o-mini   # 轻量级，快速拆解
    - MAF_MODEL_ARCHITECT=gpt-4               # 强力，架构设计
    - MAF_MODEL_DEVELOPER=gpt-4               # 强力，实现计划
    - MAF_MODEL_REVIEWER=gpt-4                # 强力，严格评审

    或 Ollama 方案：
    - MAF_MODEL_PRODUCT_MANAGER=mistral
    - MAF_MODEL_ARCHITECT=neural-chat
    - MAF_MODEL_DEVELOPER=neural-chat
    - MAF_MODEL_REVIEWER=llama2
    """
    load_dotenv()
    settings = Settings.from_env()
    settings.validate()

    # 打印配置的模型信息
    print("[Config] Agent 模型分配：")
    print(f"  产品经理: {settings.get_model_id('product_manager')}")
    print(f"  架构师:   {settings.get_model_id('architect')}")
    print(f"  开发工程师: {settings.get_model_id('developer')}")
    print(f"  评审员:   {settings.get_model_id('reviewer')}")
    print()

    agents = create_agents(settings)
    workflow = DevelopmentWorkflow(agents)

    feature_request = "构建一个支持分布式存储的文件系统"

    print(f"[Task] {feature_request}\n")
    result = await workflow.run(feature_request, mode="sequential")

    print("✓ 需求规格:")
    print(result.requirement_spec)
    print("\n✓ 架构设计:")
    print(result.architecture_design)
    print("\n✓ 实现计划:")
    print(result.implementation_plan)
    print("\n✓ 评审意见:")
    print(result.review_report)


if __name__ == "__main__":
    asyncio.run(main())
