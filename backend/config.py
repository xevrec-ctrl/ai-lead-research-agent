"""Runtime configuration and model construction for the lead research agent."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from langchain_openai import ChatOpenAI


ModelRole = Literal["research", "briefing", "report", "review"]


@dataclass(frozen=True)
class Settings:
    """Environment-backed settings without leaking secret values to logs."""

    dashscope_api_key: str
    tavily_api_key: str
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    research_model: str = "qwen-plus"
    briefing_model: str = "qwen-plus"
    report_model: str = "qwen-plus"
    review_model: str = "qwen-plus"

    @classmethod
    def from_env(cls) -> "Settings":
        dashscope_api_key = os.getenv("DASHSCOPE_API_KEY", "").strip()
        tavily_api_key = os.getenv("TAVILY_API_KEY", "").strip()

        missing = [
            name
            for name, value in (
                ("DASHSCOPE_API_KEY", dashscope_api_key),
                ("TAVILY_API_KEY", tavily_api_key),
            )
            if not value
        ]
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        return cls(
            dashscope_api_key=dashscope_api_key,
            tavily_api_key=tavily_api_key,
            dashscope_base_url=os.getenv(
                "DASHSCOPE_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ).rstrip("/"),
            research_model=os.getenv("DASHSCOPE_RESEARCH_MODEL", "qwen-plus"),
            briefing_model=os.getenv("DASHSCOPE_BRIEFING_MODEL", "qwen-plus"),
            report_model=os.getenv("DASHSCOPE_REPORT_MODEL", "qwen-plus"),
            review_model=os.getenv("DASHSCOPE_REVIEW_MODEL", "qwen-plus"),
        )

    def model_for(self, role: ModelRole) -> str:
        return {
            "research": self.research_model,
            "briefing": self.briefing_model,
            "report": self.report_model,
            "review": self.review_model,
        }[role]


def create_chat_model(
    role: ModelRole,
    *,
    settings: Settings | None = None,
    streaming: bool = False,
) -> ChatOpenAI:
    """Create a Qwen model through DashScope's OpenAI-compatible endpoint."""

    runtime = settings or Settings.from_env()
    return ChatOpenAI(
        model=runtime.model_for(role),
        api_key=runtime.dashscope_api_key,
        base_url=runtime.dashscope_base_url,
        temperature=0,
        streaming=streaming,
        max_retries=2,
        timeout=90,
    )
