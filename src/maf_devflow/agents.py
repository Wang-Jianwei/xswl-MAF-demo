from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import Settings
from .tooling import build_dev_tools


@dataclass(slots=True)
class DevAgents:
    product_manager: Any
    architect: Any
    developer: Any
    reviewer: Any


def _create_client(settings: Settings, model_id: str) -> Any:
    """创建指定模型的客户端。"""
    if settings.provider == "openai":
        from agent_framework.openai import OpenAIChatClient

        return OpenAIChatClient(
            model_id=model_id,
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
        )
    elif settings.provider == "azure":
        from agent_framework.azure import AzureOpenAIResponsesClient
        from azure.identity import AzureCliCredential

        return AzureOpenAIResponsesClient(
            project_endpoint=settings.azure_project_endpoint,
            deployment_name=settings.azure_model_deployment_name,
            credential=AzureCliCredential(),
        )
    else:
        from agent_framework.ollama import OllamaChatClient

        return OllamaChatClient(
            host=settings.ollama_endpoint,
            model_id=model_id,
        )


def create_agents(settings: Settings) -> DevAgents:
    """创建多 Agent，每个 Agent 可使用不同的模型。"""
    pm_model = settings.get_model_id("product_manager")
    arch_model = settings.get_model_id("architect")
    dev_model = settings.get_model_id("developer")
    review_model = settings.get_model_id("reviewer")

    pm_client = _create_client(settings, pm_model)
    arch_client = _create_client(settings, arch_model)
    dev_client = _create_client(settings, dev_model)
    review_client = _create_client(settings, review_model)
    dev_tools = None
    if settings.enable_tools:
        dev_tools = build_dev_tools(
            workspace_root=settings.workspace_root,
            allowed_commands=settings.allowed_commands,
            command_timeout_seconds=settings.command_timeout_seconds,
        )

    product_manager = pm_client.as_agent(
        name="ProductManagerAgent",
        description="Breaks requests into clear goals and acceptance criteria",
        instructions=(
            "你是产品经理。把用户需求拆解为：目标、边界、验收标准、优先级。"
            "输出结构化清单，简洁可执行。"
        ),
    )
    architect = arch_client.as_agent(
        name="ArchitectAgent",
        description="Designs implementation architecture and milestones",
        instructions=(
            "你是架构师。基于需求给出模块划分、数据流、技术选型与风险。"
            "优先可落地的最小方案。"
        ),
    )
    developer = dev_client.as_agent(
        name="DeveloperAgent",
        description="Produces implementation plan and key code skeleton",
        instructions=(
            "你是开发工程师。基于需求和设计输出实现步骤、关键函数签名、"
            "伪代码或骨架代码建议。可在必要时调用工具读写工作区文件并执行白名单命令验证。"
        ),
        tools=dev_tools,
    )
    reviewer = review_client.as_agent(
        name="ReviewerAgent",
        description="Reviews output quality, risks, and test strategy",
        instructions=(
            "你是代码评审。检查需求覆盖、实现可行性、风险点、测试建议。"
            "给出可执行改进项。可在必要时调用工具执行测试命令验证结论。"
        ),
        tools=dev_tools,
    )

    return DevAgents(
        product_manager=product_manager,
        architect=architect,
        developer=developer,
        reviewer=reviewer,
    )
