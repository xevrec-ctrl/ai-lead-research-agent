import pytest

import application
from backend.classes.state import job_status
from backend.services.lead_store import LeadStore


@pytest.mark.asyncio
async def test_process_research_flattens_langgraph_updates(
    monkeypatch, tmp_path
) -> None:
    assessment = {
        "executive_summary": "证据有限",
        "pain_points": [],
        "score": {"total": 42},
        "recommended_solutions": [],
    }
    review = {"passed": False, "citation_coverage": 0.5}

    class FakeGraph:
        def __init__(self, **kwargs):
            pass

        async def run(self, thread):
            yield {"opportunity_analyst": {"opportunity_assessment": assessment}}
            yield {"quality_gate": {"quality_review": review}}
            yield {"editor": {"report": "# 测试报告"}}

    store = LeadStore(tmp_path / "leads.db")
    request = application.ResearchRequest(company="测试企业")
    store.create_lead("job-1", request.model_dump())
    job_status["job-1"]
    monkeypatch.setattr(application, "Graph", FakeGraph)
    monkeypatch.setattr(application, "lead_store", store)

    await application.process_research("job-1", request)

    lead = store.get_lead("job-1")
    assert lead["status"] == "completed"
    assert lead["reports"][0]["assessment"] == assessment
    assert lead["reports"][0]["review"] == review
