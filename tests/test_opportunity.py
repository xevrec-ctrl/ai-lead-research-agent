import pytest

from backend.nodes.opportunity import OpportunityAnalyst


class FakeStructuredModel:
    def with_structured_output(self, _schema):
        return self

    async def ainvoke(self, _payload):
        return self._assessment()

    def __call__(self, _payload):
        return self._assessment()

    @staticmethod
    def _assessment():
        return {
            "executive_summary": "证据有限",
            "pain_points": [
                {
                    "title": "待验证问题",
                    "description": "待验证",
                    "priority": "low",
                    "evidence": [],
                }
            ],
            "score": {
                "need_fit": 1,
                "business_value": 1,
                "urgency": 1,
                "delivery_feasibility": 1,
                "evidence_quality": 1,
            },
            "recommended_solutions": [
                {
                    "name": "测试方案",
                    "target_problem": "待验证",
                    "workflow": ["人工确认"],
                    "tools_and_data": [],
                    "expected_value": "预计降低60%重复工作，响应时间小于30秒",
                    "human_approval_points": [],
                    "risks": [],
                    "source_urls": [],
                }
            ],
            "discovery_questions": [],
            "limitations": [],
        }


@pytest.mark.asyncio
async def test_opportunity_removes_unsupported_percentage_claim() -> None:
    analyst = OpportunityAnalyst(llm=FakeStructuredModel())
    result = await analyst.run(
        {
            "company": "测试企业",
            "briefings": {},
            "source_catalog": [],
        }
    )
    value = result["opportunity_assessment"]["recommended_solutions"][0][
        "expected_value"
    ]
    assert "60%" not in value
    assert "30秒" not in value
    assert "需通过试点数据验证" in value
