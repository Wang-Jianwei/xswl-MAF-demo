#!/usr/bin/env python
"""最小化示例：直接编程使用 maf-devflow"""

import asyncio
from pathlib import Path

# 将上级目录加入路径
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
from maf_devflow.config import Settings
from maf_devflow.agents import create_agents
from maf_devflow.workflow import DevelopmentWorkflow


async def main():
    # 加载环境变量
    load_dotenv()

    # 读取配置
    settings = Settings.from_env()
    settings.validate()

    # 创建 Agent
    agents = create_agents(settings)

    # 构建工作流
    workflow = DevelopmentWorkflow(agents)

    # 执行工作流
    feature_request = "实现一个用户认证系统，支持账密登录和第三方社交登录"
    result = await workflow.run(feature_request, mode="sequential")

    # 输出结果
    print("\n" + "=" * 60)
    print("✓ 需求规格说明")
    print("=" * 60)
    print(result.requirement_spec)

    print("\n" + "=" * 60)
    print("✓ 架构设计方案")
    print("=" * 60)
    print(result.architecture_design)

    print("\n" + "=" * 60)
    print("✓ 实现计划")
    print("=" * 60)
    print(result.implementation_plan)

    print("\n" + "=" * 60)
    print("✓ 评审意见")
    print("=" * 60)
    print(result.review_report)


if __name__ == "__main__":
    asyncio.run(main())
