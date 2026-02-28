#!/usr/bin/env python
"""vLLM 本地模型配置示例

配置两个 vLLM 模型：
- Qwen3.5-27B: http://10.11.13.4:8721/v1
- Qwen3.5-35B: http://10.11.13.4:8720/v1
"""

import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from maf_devflow.config import Settings
from maf_devflow.agents import create_agents
from maf_devflow.workflow import DevelopmentWorkflow


async def main():
    """使用本地 vLLM 模型的工作流示例"""
    load_dotenv()
    settings = Settings.from_env()
    settings.validate()

    print("[Config] vLLM 模型配置：")
    print(f"  API Base: {settings.openai_api_base}")
    print(f"  产品经理: {settings.get_model_id('product_manager')}")
    print(f"  架构师:   {settings.get_model_id('architect')}")
    print(f"  开发工程师: {settings.get_model_id('developer')}")
    print(f"  评审员:   {settings.get_model_id('reviewer')}")
    print()

    agents = create_agents(settings)
    workflow = DevelopmentWorkflow(agents)

    feature_request = "使用消息队列构建高吞吐量的数据处理管道"

    print(f"[Task] {feature_request}\n")
    result = await workflow.run(feature_request, mode="sequential")

    print("✓ 需求规格:")
    print(result.requirement_spec[:500] if len(result.requirement_spec) > 500 else result.requirement_spec)
    print("\n✓ 架构设计:")
    print(result.architecture_design[:500] if len(result.architecture_design) > 500 else result.architecture_design)
    print("\n✓ 实现计划:")
    print(result.implementation_plan[:500] if len(result.implementation_plan) > 500 else result.implementation_plan)
    print("\n✓ 评审意见:")
    print(result.review_report[:500] if len(result.review_report) > 500 else result.review_report)


if __name__ == "__main__":
    asyncio.run(main())
