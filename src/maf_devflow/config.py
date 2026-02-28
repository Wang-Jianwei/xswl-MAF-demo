from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    provider: str
    model_id: str
    workflow_mode: str
    openai_api_key: str | None
    openai_api_base: str | None
    azure_project_endpoint: str | None
    azure_model_deployment_name: str | None
    ollama_endpoint: str | None
    model_product_manager: str | None
    model_architect: str | None
    model_developer: str | None
    model_reviewer: str | None

    @classmethod
    def from_env(cls) -> "Settings":
        provider = os.getenv("MAF_PROVIDER", "openai").strip().lower()
        mode = os.getenv("MAF_WORKFLOW_MODE", "sequential").strip().lower()
        default_model = os.getenv("MAF_MODEL_ID", "gpt-4.1-mini").strip()

        return cls(
            provider=provider,
            model_id=default_model,
            workflow_mode=mode,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE"),
            azure_project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
            azure_model_deployment_name=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME"),
            ollama_endpoint=os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434"),
            model_product_manager=os.getenv("MAF_MODEL_PRODUCT_MANAGER"),
            model_architect=os.getenv("MAF_MODEL_ARCHITECT"),
            model_developer=os.getenv("MAF_MODEL_DEVELOPER"),
            model_reviewer=os.getenv("MAF_MODEL_REVIEWER"),
        )

    def get_model_id(self, agent_role: str) -> str:
        """获取指定角色的模型ID，如果未配置则使用默认模型。

        Args:
            agent_role: Agent 角色名('product_manager'|'architect'|'developer'|'reviewer')

        Returns:
            模型 ID
        """
        role_to_attr = {
            "product_manager": self.model_product_manager,
            "architect": self.model_architect,
            "developer": self.model_developer,
            "reviewer": self.model_reviewer,
        }
        return role_to_attr.get(agent_role) or self.model_id

    def validate(self, dry_run: bool = False) -> None:
        if self.provider not in {"openai", "azure", "ollama"}:
            raise ValueError("MAF_PROVIDER must be 'openai', 'azure', or 'ollama'")

        if self.workflow_mode not in {"sequential", "concurrent"}:
            raise ValueError("MAF_WORKFLOW_MODE must be 'sequential' or 'concurrent'")

        if dry_run:
            return

        if self.provider == "openai":
            # 如果有自定义 API base（vLLM 等），API key 可以是 dummy
            if not self.openai_api_key and not self.openai_api_base:
                raise ValueError("OPENAI_API_KEY required, or set OPENAI_API_BASE for local vLLM")
            if not self.openai_api_key:
                self.openai_api_key = "sk-local-vllm"  # type: ignore

        if self.provider == "azure":
            if not self.azure_project_endpoint:
                raise ValueError("AZURE_AI_PROJECT_ENDPOINT is required when MAF_PROVIDER=azure")
            if not self.azure_model_deployment_name:
                raise ValueError("AZURE_AI_MODEL_DEPLOYMENT_NAME is required when MAF_PROVIDER=azure")

        if self.provider == "ollama":
            if not self.ollama_endpoint:
                raise ValueError("OLLAMA_ENDPOINT is required when MAF_PROVIDER=ollama")
