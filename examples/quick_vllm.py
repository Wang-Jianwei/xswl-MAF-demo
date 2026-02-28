#!/usr/bin/env python
"""
最简化版本：直接使用你的 vLLM 配置

只需 3 行代码就能启动多 Agent 协作工作流
"""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_framework.openai import OpenAIChatClient
from maf_devflow.workflow import DevelopmentWorkflow
from maf_devflow.agents import DevAgents


async def main():
    # 创建两个客户端（显式绑定 API base）
    c27b = OpenAIChatClient(
        model_id="Qwen3.5-27B",
        api_key="sk-local",
        base_url="http://10.11.13.4:8721/v1",
    )

    c35b = OpenAIChatClient(
        model_id="Qwen3.5-35B",
        api_key="sk-local",
        base_url="http://10.11.13.4:8720/v1",
    )

    # 创建 4 个 Agent
    agents = DevAgents(
        product_manager=c27b.as_agent(name="PM", instructions="快速拆解需求"),
        architect=c35b.as_agent(name="Arch", instructions="设计架构方案"),
        developer=c35b.as_agent(name="Dev", instructions="输出实现计划"),
        reviewer=c35b.as_agent(name="Review", instructions="评审并提改进建议"),
    )

    # 执行工作流
    workflow = DevelopmentWorkflow(agents)
    result = await workflow.run("实现一个消息队列系统")

    # 输出结果
    print("✓ 需求:", result.requirement_spec[:100], "...")
    print("✓ 架构:", result.architecture_design[:100], "...")
    print("✓ 实现:", result.implementation_plan[:100], "...")
    print("✓ 评审:", result.review_report[:100], "...")


if __name__ == "__main__":
    asyncio.run(main())
