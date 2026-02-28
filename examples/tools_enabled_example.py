#!/usr/bin/env python
"""启用工具调用的工作流示例。

目标：让 Developer/Reviewer 在流程中自动调用工具：
1) 写入示例源码文件
2) 写入测试文件
3) 执行 pytest 验证

前置条件：
- .env 中启用工具：
  MAF_ENABLE_TOOLS=true
  MAF_WORKSPACE_ROOT=.
  MAF_ALLOWED_COMMANDS=python,pytest,pip
  MAF_COMMAND_TIMEOUT_SECONDS=120
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from maf_devflow.agents import create_agents
from maf_devflow.config import Settings
from maf_devflow.workflow import DevelopmentWorkflow


async def main() -> None:
    load_dotenv(Path(__file__).parent.parent / ".env")
    settings = Settings.from_env()
    settings.validate()

    if not settings.enable_tools:
        raise SystemExit(
            "未开启工具调用。请在 .env 中设置 MAF_ENABLE_TOOLS=true，"
            "并配置 MAF_WORKSPACE_ROOT/MAF_ALLOWED_COMMANDS。"
        )

    print("[Config] 工具调用已启用")
    print(f"  provider={settings.provider}")
    print(f"  workspace_root={settings.workspace_root}")
    print(f"  allowed_commands={settings.allowed_commands}")

    agents = create_agents(settings)
    workflow = DevelopmentWorkflow(agents)

    feature_request = (
        "请完成一个最小可运行的 Python 任务清单模块，并且必须调用工具执行以下动作：\n"
        "1) 写入 generated/todo_core.py，包含函数 add_task(tasks: list[str], task: str) -> list[str]。\n"
        "2) 写入 tests/test_generated_todo_core.py，覆盖 add_task 的基本行为。\n"
        "3) 执行命令：pytest -q tests/test_generated_todo_core.py。\n"
        "4) 在输出中给出：创建了哪些文件、测试命令和结果摘要。"
    )

    result = await workflow.run(
        feature_request=feature_request,
        mode="sequential",
        debug=True,
        debug_max_chars=1200,
    )

    print("\n========== Tool-Enabled Workflow Result ==========")
    print("\n[1] Requirement Spec\n")
    print(result.requirement_spec)
    print("\n[2] Architecture Design\n")
    print(result.architecture_design)
    print("\n[3] Implementation Plan\n")
    print(result.implementation_plan)
    print("\n[4] Review Report\n")
    print(result.review_report)


if __name__ == "__main__":
    asyncio.run(main())
