#!/usr/bin/env python
"""并发示例：使用 concurrent 模式加速流程"""

import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from maf_devflow.config import Settings
from maf_devflow.agents import create_agents
from maf_devflow.workflow import DevelopmentWorkflow


async def main():
    load_dotenv()
    settings = Settings.from_env()
    settings.validate()

    agents = create_agents(settings)
    workflow = DevelopmentWorkflow(agents)

    feature_request = "为 API 系统增加速率限制和访问控制功能"

    print("[Info] 开始并发工作流，架构和实现将并行执行...\n")

    # 使用 concurrent 模式
    result = await workflow.run(feature_request, mode="concurrent")

    print("✓ 需求规格:")
    print(result.requirement_spec)
    print("\n✓ 架构设计:")
    print(result.architecture_design)
    print("\n✓ 实现计划:")
    print(result.implementation_plan)
    print("\n✓ 最终评审:")
    print(result.review_report)


if __name__ == "__main__":
    asyncio.run(main())
