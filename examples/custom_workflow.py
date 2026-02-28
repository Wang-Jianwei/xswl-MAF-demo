#!/usr/bin/env python
"""高级示例：自定义工作流流程和 Agent 配置"""

import asyncio
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from maf_devflow.config import Settings
from maf_devflow.agents import create_agents
from maf_devflow.workflow import DevelopmentWorkflow, _response_to_text


async def custom_workflow_with_iteration():
    """多轮迭代的工作流示例"""
    load_dotenv()
    settings = Settings.from_env()
    settings.validate()

    agents = create_agents(settings)
    workflow = DevelopmentWorkflow(agents)

    # 第一轮：初始设计
    print("[轮次 1] 初始需求设计\n")
    result1 = await workflow.run(
        "实现一个支持 WebSocket 的实时消息系统",
        mode="sequential"
    )
    print("规格说明:", result1.requirement_spec[:150], "...")
    print("架构设计:", result1.architecture_design[:150], "...")

    # 第二轮：基于评审改进
    print("\n[轮次 2] 基于评审意见优化\n")
    improvement_prompt = (
        f"基于以下评审意见，重新优化需求和架构。\n\n"
        f"原评审意见：{result1.review_report}\n\n"
        f"请提出改进后的规格说明和架构建议。"
    )
    
    improved_spec = _response_to_text(
        await agents.product_manager.run(improvement_prompt)
    )
    print("改进后的规格:", improved_spec[:150], "...")


async def batch_features():
    """批量处理多个需求的示例"""
    load_dotenv()
    settings = Settings.from_env()
    settings.validate()

    agents = create_agents(settings)
    workflow = DevelopmentWorkflow(agents)

    features = [
        "实现数据加密存储模块",
        "构建监控告警系统",
        "设计缓存策略",
    ]

    print("[批量处理] 并行处理多个需求\n")

    # 并行执行多个工作流
    tasks = [
        workflow.run(feature, mode="concurrent")
        for feature in features
    ]
    results = await asyncio.gather(*tasks)

    # 输出汇总
    for i, (feature, result) in enumerate(zip(features, results), 1):
        print(f"\n【需求 {i}】{feature}")
        print(f"  规格摘要: {result.requirement_spec[:80]}...")
        print(f"  架构摘要: {result.architecture_design[:80]}...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "batch":
        asyncio.run(batch_features())
    else:
        asyncio.run(custom_workflow_with_iteration())
