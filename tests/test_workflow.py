import asyncio

from maf_devflow.agents import DevAgents
from maf_devflow.workflow import DevelopmentWorkflow


class _FakeResp:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeAgent:
    def __init__(self, name: str) -> None:
        self.name = name

    async def run(self, prompt: str):
        return _FakeResp(f"{self.name}: {prompt[:40]}")


def test_workflow_sequential():
    workflow = DevelopmentWorkflow(
        DevAgents(
            product_manager=_FakeAgent("pm"),
            architect=_FakeAgent("arch"),
            developer=_FakeAgent("dev"),
            reviewer=_FakeAgent("review"),
        )
    )

    result = asyncio.run(workflow.run("build feature x", mode="sequential"))

    assert "pm:" in result.requirement_spec
    assert "arch:" in result.architecture_design
    assert "dev:" in result.implementation_plan
    assert "review:" in result.review_report
