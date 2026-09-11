from application import ResearchRequest
from backend.nodes.grounding import GroundingNode


def test_research_request_accepts_client_context() -> None:
    request = ResearchRequest(
        company="示例科技",
        company_url="https://example.com",
        industry="企业服务",
        client_need="希望减少重复的客户咨询和人工整理工作",
        our_capabilities="知识库、工作流 Agent、飞书集成",
    )

    assert request.client_need == "希望减少重复的客户咨询和人工整理工作"
    assert "飞书" in request.our_capabilities


def test_grounding_preserves_opportunity_context(monkeypatch) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    state = {
        "company": "示例科技",
        "client_need": "减少售后重复咨询",
        "our_capabilities": "知识库问答 Agent",
    }
    node = GroundingNode()
    result = None

    async def collect_state():
        nonlocal result
        async for event in node.initial_search(state):
            if isinstance(event, dict) and "type" not in event:
                result = event

    import asyncio

    asyncio.run(collect_state())
    assert result["client_need"] == state["client_need"]
    assert result["our_capabilities"] == state["our_capabilities"]
