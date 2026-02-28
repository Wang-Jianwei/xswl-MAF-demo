from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Mapping

from .agents import DevAgents


@dataclass(slots=True)
class WorkflowResult:
    requirement_spec: str
    architecture_design: str
    implementation_plan: str
    review_report: str


def _response_to_text(response: Any) -> str:
    if response is None:
        return ""

    text = getattr(response, "text", None)
    if isinstance(text, str) and text.strip():
        return text.strip()

    messages = getattr(response, "messages", None)
    if isinstance(messages, list):
        chunks: list[str] = []
        for message in messages:
            chunk = getattr(message, "text", None)
            if isinstance(chunk, str) and chunk.strip():
                chunks.append(chunk.strip())
        if chunks:
            return "\n\n".join(chunks)

    return str(response)


class DevelopmentWorkflow:
    def __init__(self, agents: DevAgents) -> None:
        self._agents = agents

    @staticmethod
    def _extract_agent_model_tag(agent: Any) -> str | None:
        client = getattr(agent, "client", None)
        if client is None:
            return None

        model_id = getattr(client, "model_id", None)
        if not isinstance(model_id, str) or not model_id.strip():
            return None

        endpoint = getattr(client, "base_url", None)
        if endpoint is None:
            endpoint = getattr(client, "host", None)

        if isinstance(endpoint, str) and endpoint.strip():
            return f"{model_id}@{endpoint}"
        return model_id

    def _infer_debug_agent_models(self) -> dict[str, str]:
        inferred: dict[str, str] = {}
        role_to_agent = {
            "productmanager": self._agents.product_manager,
            "architect": self._agents.architect,
            "developer": self._agents.developer,
            "reviewer": self._agents.reviewer,
        }
        for role, agent in role_to_agent.items():
            model_tag = self._extract_agent_model_tag(agent)
            if model_tag:
                inferred[role] = model_tag
        return inferred

    @staticmethod
    def _preview_text(text: str, max_chars: int) -> str:
        normalized = text.strip()
        if len(normalized) <= max_chars:
            return normalized
        return normalized[:max_chars] + "..."

    @staticmethod
    def _trace(enabled: bool, title: str, content: str, max_chars: int) -> None:
        if not enabled:
            return
        print(f"\n[DEBUG] {title}")
        print(DevelopmentWorkflow._preview_text(content, max_chars))

    @staticmethod
    def _debug_title(role: str, phase: str, debug_agent_models: Mapping[str, str] | None) -> str:
        if not debug_agent_models:
            return f"{role} {phase}"
        model = debug_agent_models.get(role.lower())
        if model:
            return f"{role} [{model}] {phase}"
        return f"{role} {phase}"

    async def run(
        self,
        feature_request: str,
        mode: str = "sequential",
        debug: bool = False,
        debug_max_chars: int = 600,
        debug_agent_models: Mapping[str, str] | None = None,
    ) -> WorkflowResult:
        resolved_debug_models = debug_agent_models
        if debug and not resolved_debug_models:
            resolved_debug_models = self._infer_debug_agent_models()

        if mode == "concurrent":
            return await self._run_concurrent(
                feature_request,
                debug=debug,
                debug_max_chars=debug_max_chars,
                debug_agent_models=resolved_debug_models,
            )
        return await self._run_sequential(
            feature_request,
            debug=debug,
            debug_max_chars=debug_max_chars,
            debug_agent_models=resolved_debug_models,
        )

    async def _run_sequential(
        self,
        feature_request: str,
        debug: bool = False,
        debug_max_chars: int = 600,
        debug_agent_models: Mapping[str, str] | None = None,
    ) -> WorkflowResult:
        requirement_prompt = (
            "请将以下需求拆解为可开发的规格说明（目标、约束、验收标准、里程碑）：\n"
            f"{feature_request}"
        )
        self._trace(
            debug,
            self._debug_title("ProductManager", "Prompt", debug_agent_models),
            requirement_prompt,
            debug_max_chars,
        )
        requirement_spec = _response_to_text(await self._agents.product_manager.run(requirement_prompt))
        self._trace(
            debug,
            self._debug_title("ProductManager", "Response", debug_agent_models),
            requirement_spec,
            debug_max_chars,
        )

        architecture_prompt = (
            "基于以下规格说明，给出架构设计：模块边界、数据流、关键接口、潜在风险。\n"
            f"{requirement_spec}"
        )
        self._trace(
            debug,
            self._debug_title("Architect", "Prompt", debug_agent_models),
            architecture_prompt,
            debug_max_chars,
        )
        architecture_design = _response_to_text(await self._agents.architect.run(architecture_prompt))
        self._trace(
            debug,
            self._debug_title("Architect", "Response", debug_agent_models),
            architecture_design,
            debug_max_chars,
        )

        implementation_prompt = (
            "基于以下规格与架构，生成实现计划（按任务拆分）和关键代码骨架建议：\n"
            f"[规格]\n{requirement_spec}\n\n[架构]\n{architecture_design}"
        )
        self._trace(
            debug,
            self._debug_title("Developer", "Prompt", debug_agent_models),
            implementation_prompt,
            debug_max_chars,
        )
        implementation_plan = _response_to_text(await self._agents.developer.run(implementation_prompt))
        self._trace(
            debug,
            self._debug_title("Developer", "Response", debug_agent_models),
            implementation_plan,
            debug_max_chars,
        )

        review_prompt = (
            "请从需求覆盖、实现可行性、测试策略、风险控制四个方面评审以下内容并给出改进项：\n"
            f"[规格]\n{requirement_spec}\n\n[架构]\n{architecture_design}\n\n[实现]\n{implementation_plan}"
        )
        self._trace(
            debug,
            self._debug_title("Reviewer", "Prompt", debug_agent_models),
            review_prompt,
            debug_max_chars,
        )
        review_report = _response_to_text(await self._agents.reviewer.run(review_prompt))
        self._trace(
            debug,
            self._debug_title("Reviewer", "Response", debug_agent_models),
            review_report,
            debug_max_chars,
        )

        return WorkflowResult(
            requirement_spec=requirement_spec,
            architecture_design=architecture_design,
            implementation_plan=implementation_plan,
            review_report=review_report,
        )

    async def _run_concurrent(
        self,
        feature_request: str,
        debug: bool = False,
        debug_max_chars: int = 600,
        debug_agent_models: Mapping[str, str] | None = None,
    ) -> WorkflowResult:
        requirement_prompt = (
            "请将以下需求拆解为可开发的规格说明（目标、约束、验收标准、里程碑）：\n"
            f"{feature_request}"
        )
        self._trace(
            debug,
            self._debug_title("ProductManager", "Prompt", debug_agent_models),
            requirement_prompt,
            debug_max_chars,
        )
        requirement_spec = _response_to_text(await self._agents.product_manager.run(requirement_prompt))
        self._trace(
            debug,
            self._debug_title("ProductManager", "Response", debug_agent_models),
            requirement_spec,
            debug_max_chars,
        )

        architecture_prompt = (
            "基于以下规格说明，给出架构设计：模块边界、数据流、关键接口、潜在风险。\n"
            f"{requirement_spec}"
        )
        implementation_prompt = (
            "基于以下规格说明，生成实现计划（按任务拆分）和关键代码骨架建议：\n"
            f"{requirement_spec}"
        )
        self._trace(
            debug,
            self._debug_title("Architect", "Prompt", debug_agent_models),
            architecture_prompt,
            debug_max_chars,
        )
        self._trace(
            debug,
            self._debug_title("Developer", "Prompt", debug_agent_models),
            implementation_prompt,
            debug_max_chars,
        )

        architecture_task = self._agents.architect.run(architecture_prompt)
        implementation_task = self._agents.developer.run(implementation_prompt)
        architecture_resp, implementation_resp = await asyncio.gather(architecture_task, implementation_task)

        architecture_design = _response_to_text(architecture_resp)
        implementation_plan = _response_to_text(implementation_resp)
        self._trace(
            debug,
            self._debug_title("Architect", "Response", debug_agent_models),
            architecture_design,
            debug_max_chars,
        )
        self._trace(
            debug,
            self._debug_title("Developer", "Response", debug_agent_models),
            implementation_plan,
            debug_max_chars,
        )

        review_prompt = (
            "你现在是质量负责人。综合规格、架构、实现计划，输出最终评审结论与下一步行动：\n"
            f"[规格]\n{requirement_spec}\n\n[架构]\n{architecture_design}\n\n[实现]\n{implementation_plan}"
        )
        self._trace(
            debug,
            self._debug_title("Reviewer", "Prompt", debug_agent_models),
            review_prompt,
            debug_max_chars,
        )
        review_report = _response_to_text(await self._agents.reviewer.run(review_prompt))
        self._trace(
            debug,
            self._debug_title("Reviewer", "Response", debug_agent_models),
            review_report,
            debug_max_chars,
        )

        return WorkflowResult(
            requirement_spec=requirement_spec,
            architecture_design=architecture_design,
            implementation_plan=implementation_plan,
            review_report=review_report,
        )
