"""Deterministic task drafts derived from an approved opportunity assessment."""

from __future__ import annotations

from typing import Any


def build_task_drafts(lead_id: str, assessment: dict[str, Any]) -> list[dict[str, Any]]:
    drafts: list[dict[str, Any]] = []
    for solution in assessment.get("recommended_solutions", []):
        name = str(solution.get("name", "Agent 方案验证"))
        drafts.append(
            {
                "lead_id": lead_id,
                "title": f"验证{name}的客户需求与数据条件",
                "details": {
                    "target_problem": solution.get("target_problem", ""),
                    "workflow": solution.get("workflow", []),
                    "tools_and_data": solution.get("tools_and_data", []),
                    "approval_points": solution.get("human_approval_points", []),
                    "risks": solution.get("risks", []),
                    "next_step": "与客户确认数据来源、权限边界和验收指标",
                    "status": "pending_approval",
                },
            }
        )
    return drafts
