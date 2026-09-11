from backend.services.lead_store import LeadStore
from backend.services.task_drafts import build_task_drafts


def test_lead_store_persists_report_and_requires_task_approval(tmp_path) -> None:
    store = LeadStore(tmp_path / "leads.db")
    store.create_lead("lead-1", {"company": "示例科技", "client_need": "减少重复咨询"})
    store.save_report(
        "lead-1",
        "# 报告",
        {"score": {"total": 80}},
        {"passed": True},
    )
    task = build_task_drafts(
        "lead-1",
        {
            "recommended_solutions": [
                {
                    "name": "需求分析 Agent",
                    "target_problem": "重复整理",
                    "workflow": ["分类", "人工确认"],
                }
            ]
        },
    )[0]
    task_id = store.create_task_draft(task["lead_id"], task["title"], task["details"])

    lead = store.get_lead("lead-1")
    assert lead is not None
    assert lead["status"] == "review_required"
    assert lead["tasks"][0]["status"] == "pending_approval"

    approved = store.approve_task_draft(task_id)
    assert approved is not None
    assert approved["status"] == "approved"
