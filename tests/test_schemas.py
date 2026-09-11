import pytest
from pydantic import ValidationError

from backend.schemas import OpportunityAssessment


def test_assessment_calculates_total_score_instead_of_trusting_model() -> None:
    assessment = OpportunityAssessment.model_validate(
        {
            "executive_summary": "存在明确的自动化机会",
            "pain_points": [
                {
                    "title": "重复整理",
                    "description": "人工整理客户消息",
                    "priority": "high",
                    "evidence": [],
                }
            ],
            "score": {
                "need_fit": 18,
                "business_value": 16,
                "urgency": 12,
                "delivery_feasibility": 17,
                "evidence_quality": 10,
            },
            "recommended_solutions": [
                {
                    "name": "客户需求分析 Agent",
                    "target_problem": "减少人工整理",
                    "workflow": ["解析消息", "分类", "人工确认"],
                    "tools_and_data": ["飞书导出文件"],
                    "expected_value": "缩短整理时间",
                }
            ],
        }
    )

    assert assessment.as_state_dict()["score"]["total"] == 73


def test_assessment_rejects_out_of_range_score() -> None:
    with pytest.raises(ValidationError):
        OpportunityAssessment.model_validate(
            {
                "executive_summary": "invalid",
                "pain_points": [{"title": "x", "description": "x", "priority": "high"}],
                "score": {
                    "need_fit": 21,
                    "business_value": 10,
                    "urgency": 10,
                    "delivery_feasibility": 10,
                    "evidence_quality": 10,
                },
                "recommended_solutions": [
                    {
                        "name": "x",
                        "target_problem": "x",
                        "workflow": ["x"],
                        "tools_and_data": ["x"],
                        "expected_value": "x",
                    }
                ],
            }
        )
