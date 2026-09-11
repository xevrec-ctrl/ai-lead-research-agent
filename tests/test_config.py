from __future__ import annotations

import pytest

from backend.config import Settings, create_chat_model


def test_settings_load_qwen_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-dashscope-key")
    monkeypatch.setenv("TAVILY_API_KEY", "test-tavily-key")

    settings = Settings.from_env()

    assert settings.dashscope_base_url.endswith("/compatible-mode/v1")
    assert settings.model_for("research") == "qwen-plus"
    assert settings.model_for("briefing") == "qwen-plus"
    assert settings.model_for("report") == "qwen-plus"


def test_settings_report_all_missing_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)

    with pytest.raises(ValueError, match="DASHSCOPE_API_KEY, TAVILY_API_KEY"):
        Settings.from_env()


def test_model_uses_dashscope_compatible_endpoint() -> None:
    settings = Settings(
        dashscope_api_key="test-key",
        tavily_api_key="test-search-key",
        dashscope_base_url="https://example.invalid/v1",
        research_model="qwen-test",
    )

    model = create_chat_model("research", settings=settings, streaming=True)

    assert model.model_name == "qwen-test"
    assert str(model.openai_api_base).rstrip("/") == "https://example.invalid/v1"
    assert model.streaming is True
