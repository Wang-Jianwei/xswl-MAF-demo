from __future__ import annotations

import argparse
import asyncio
from textwrap import dedent

from dotenv import load_dotenv

from .agents import DevAgents, create_agents
from .config import Settings
from .workflow import DevelopmentWorkflow, WorkflowResult


class _MockAgent:
    def __init__(self, name: str) -> None:
        self._name = name

    async def run(self, prompt: str):
        class _Resp:
            def __init__(self, text: str) -> None:
                self.text = text

        preview = prompt.strip().splitlines()[0][:120]
        return _Resp(f"[{self._name}] mock output based on: {preview}")


def _create_mock_agents() -> DevAgents:
    return DevAgents(
        product_manager=_MockAgent("ProductManagerAgent"),
        architect=_MockAgent("ArchitectAgent"),
        developer=_MockAgent("DeveloperAgent"),
        reviewer=_MockAgent("ReviewerAgent"),
    )


def _print_result(result: WorkflowResult) -> None:
    print("\n========== Multi-Agent DevFlow Result ==========")
    print("\n[1] Requirement Spec\n")
    print(result.requirement_spec)

    print("\n[2] Architecture Design\n")
    print(result.architecture_design)

    print("\n[3] Implementation Plan\n")
    print(result.implementation_plan)

    print("\n[4] Review Report\n")
    print(result.review_report)


async def _run(args: argparse.Namespace) -> None:
    load_dotenv()
    settings = Settings.from_env()

    mode = args.mode or settings.workflow_mode
    dry_run = bool(args.dry_run)

    settings.validate(dry_run=dry_run)

    if dry_run:
        agents = _create_mock_agents()
    else:
        agents = create_agents(settings)

    workflow = DevelopmentWorkflow(agents)
    result = await workflow.run(feature_request=args.prompt, mode=mode)
    _print_result(result)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="maf-devflow",
        description="Multi-agent software development workflow using Microsoft Agent Framework",
    )
    parser.add_argument("prompt", help="Feature request or development task description")
    parser.add_argument(
        "--mode",
        choices=["sequential", "concurrent"],
        default=None,
        help="Workflow execution mode (default from MAF_WORKFLOW_MODE)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run with local mock agents (no model/API call)",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        asyncio.run(_run(args))
    except Exception as exc:
        message = dedent(
            f"""
            Failed to run workflow: {exc}

            Tips:
            1) Copy .env.example to .env and fill required values.
            2) For OpenAI mode, set OPENAI_API_KEY and optionally MAF_MODEL_ID.
            3) For Azure mode, run az login and set AZURE_AI_PROJECT_ENDPOINT / AZURE_AI_MODEL_DEPLOYMENT_NAME.
            4) Use --dry-run for offline smoke test.
            """
        ).strip()
        raise SystemExit(message) from exc


if __name__ == "__main__":
    main()
