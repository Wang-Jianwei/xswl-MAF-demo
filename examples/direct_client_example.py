#!/usr/bin/env python
"""
直接在代码中创建客户端的示例
"""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_framework.openai import OpenAIChatClient
from maf_devflow.workflow import DevelopmentWorkflow
from maf_devflow.agents import DevAgents


async def _probe_agent(agent_name: str, agent: object, timeout_seconds: int = 10) -> tuple[bool, str]:
    prompt = "请只回复：ok"
    try:
        await asyncio.wait_for(agent.run(prompt), timeout=timeout_seconds)
        return True, f"✓ {agent_name} 连通性正常"
    except asyncio.TimeoutError:
        return False, f"✗ {agent_name} 超时（>{timeout_seconds}s）"
    except Exception as exc:
        return False, f"✗ {agent_name} 失败：{exc}"


async def main():
    """直接创建多个客户端并分配给不同 Agent"""

    # ============ 第一阶段：创建两个 OpenAI 兼容客户端 ============
    print("[Step 1] 创建 vLLM 客户端...")

    # 轻量级模型：用于快速需求拆解
    client_1 = OpenAIChatClient(
        model_id="Qwen3.5-35B",
        api_key="sk-local",
        base_url="http://10.11.13.4:8720/v1",
    )

    # 强力模型：用于架构、实现、评审
    client_2 = OpenAIChatClient(
        model_id="Qwen3.5-35B",
        api_key="sk-local",
        base_url="http://10.11.13.4:8720/v1",
    )

    # ============ 第二阶段：为不同角色创建 Agent ============
    print("\n[Step 2] 为不同角色创建 Agent...")

    # 产品经理：用轻量级模型快速拆解需求
    product_manager = client_1.as_agent(
        name="ProductManagerAgent",
        description="快速拆解需求为清晰的目标和验收标准",
        instructions=(
            "你是产品经理。快速把用户需求拆解为：目标、边界、验收标准、优先级。"
            "输出结构化清单，简洁可执行。"
        ),
    )
    print(f"  ✓ ProductManager ({client_1.model_id})")

    # 架构师：用强力模型做复杂设计
    architect = client_2.as_agent(
        name="ArchitectAgent",
        description="深度设计实现架构和模块划分",
        instructions=(
            "你是架构师。基于需求给出详细的模块划分、数据流、技术选型与风险分析。"
            "优先可落地的最小方案，但要考虑扩展性。"
        ),
    )
    print(f"  ✓ Architect ({client_2.model_id})")

    # 开发工程师：用强力模型输出完整实现计划
    developer = client_2.as_agent(
        name="DeveloperAgent",
        description="输出详细的实现步骤和代码骨架",
        instructions=(
            "你是开发工程师。基于需求和设计输出：实现步骤、关键函数签名、"
            "伪代码或骨架代码建议，确保可直接执行。"
        ),
    )
    print(f"  ✓ Developer ({client_2.model_id})")

    # 评审员：用强力模型做严格评审
    reviewer = client_2.as_agent(
        name="ReviewerAgent",
        description="严格评审和风险识别",
        instructions=(
            "你是代码评审和质量负责人。从需求覆盖、实现可行性、性能、"
            "风险点、测试策略四个方面评审，给出具体改进建议。"
        ),
    )
    print(f"  ✓ Reviewer ({client_2.model_id})")

    print("\n[Step 2.5] 端点连通性探测（超时 10s）...")
    pm_ok, pm_msg = await _probe_agent(product_manager.name, product_manager, timeout_seconds=10)
    arch_ok, arch_msg = await _probe_agent(architect.name, architect, timeout_seconds=10)
    print(f"  {pm_msg}")
    print(f"  {arch_msg}")

    if not (pm_ok and arch_ok):
        raise RuntimeError(
            "连通性探测失败，请检查：\n"
            "1) vLLM 服务是否启动\n"
            "2) 模型 ID 是否存在\n"
            "3) 防火墙/网络策略是否允许访问上述端口"
        )

    # ============ 第三阶段：构建工作流并运行 ============
    print("\n[Step 3] 构建工作流...")

    agents = DevAgents(
        product_manager=product_manager,
        architect=architect,
        developer=developer,
        reviewer=reviewer,
    )

    workflow = DevelopmentWorkflow(agents)

    # 用户需求
    feature_request = (
        "实现一个高可用的分布式任务队列系统，支持：\n"
        "1. 任务的可靠投递和执行\n"
        "2. 失败重试和死信队列\n"
        "3. 多种消费模式（推拉结合）\n"
        "4. 消息顺序性保证"
    )

    feature_request = "写个 Python 函数，输入是一个整数列表，输出是一个新的列表，包含原列表中所有偶数的平方。"

    print(f"\n[Task] 需求描述：\n{feature_request}\n")

    print("[Step 4] 执行顺序工作流...\n")
    print("=" * 70)

    # 执行工作流
    result = await workflow.run(
        feature_request,
        mode="sequential",
        debug=True,
        debug_max_chars=800,
        # debug_agent_models={
        #     "productmanager": f"{product_manager.name}@{client_1.model_id}",
        #     "architect": f"{architect.name}@{client_2.model_id}",
        #     "developer": f"{developer.name}@{client_2.model_id}",
        #     "reviewer": f"{reviewer.name}@{client_2.model_id}",
        # },
    )

    # ============ 第四阶段：输出结果 ============
    print("=" * 70)
    print(f"\n【规格说明】（{product_manager.name} - {client_1.model_id}）\n")
    print(result.requirement_spec)

    print("\n" + "=" * 70)
    print(f"\n【架构设计】（{architect.name} - {client_2.model_id}）\n")
    print(result.architecture_design)

    print("\n" + "=" * 70)
    print(f"\n【实现计划】（{developer.name} - {client_2.model_id}）\n")
    print(result.implementation_plan)

    print("\n" + "=" * 70)
    print(f"\n【评审意见】（{reviewer.name} - {client_2.model_id}）\n")
    print(result.review_report)

    print("\n" + "=" * 70)
    print("✓ 工作流执行完成")


if __name__ == "__main__":
    asyncio.run(main())
