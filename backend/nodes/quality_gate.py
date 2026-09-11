"""Deterministic evidence checks around model-generated opportunity analysis."""

from __future__ import annotations

from typing import Literal

from ..classes import ResearchState
from ..classes.state import job_status
from ..schemas import QualityReview


class EvidenceQualityGate:
    def __init__(
        self,
        minimum_coverage: float = 0.8,
        minimum_evidence_score: int = 8,
        max_revisions: int = 1,
    ) -> None:
        self.minimum_coverage = minimum_coverage
        self.minimum_evidence_score = minimum_evidence_score
        self.max_revisions = max_revisions

    @staticmethod
    def _claim_source_groups(assessment: dict) -> list[list[str]]:
        groups: list[list[str]] = []
        for pain_point in assessment.get("pain_points", []):
            for evidence in pain_point.get("evidence", []):
                groups.append(evidence.get("source_urls", []))
        for solution in assessment.get("recommended_solutions", []):
            groups.append(solution.get("source_urls", []))
        return groups

    def run(self, state: ResearchState) -> dict:
        assessment = state.get("opportunity_assessment", {})
        allowed_urls = {item["url"] for item in state.get("source_catalog", [])}
        groups = self._claim_source_groups(assessment)
        cited_groups = [group for group in groups if group]
        valid_groups = [
            group for group in cited_groups if all(url in allowed_urls for url in group)
        ]
        used_urls = {url for group in cited_groups for url in group}
        invalid_urls = sorted(used_urls - allowed_urls)
        coverage = len(valid_groups) / len(groups) if groups else 0.0
        issues: list[str] = []

        if not groups:
            issues.append("分析结果没有可审核的事实或方案")
        if coverage < self.minimum_coverage:
            issues.append(
                f"有效引用覆盖率 {coverage:.0%}，低于要求的 {self.minimum_coverage:.0%}"
            )
        if invalid_urls:
            issues.append("存在未出现在检索结果中的来源网址")
        evidence_score = int(assessment.get("score", {}).get("evidence_quality", 0))
        if evidence_score < self.minimum_evidence_score:
            issues.append(
                f"证据质量评分 {evidence_score}/20，低于要求的 "
                f"{self.minimum_evidence_score}/20"
            )
        if not assessment.get("recommended_solutions"):
            issues.append("没有生成可实施的 Agent 方案")

        revision_count = int(state.get("quality_review", {}).get("revision_count", 0))
        passed = not issues
        if not passed:
            revision_count += 1
        review = QualityReview(
            passed=passed,
            citation_coverage=coverage,
            invalid_source_urls=invalid_urls,
            issues=issues,
            revision_count=revision_count,
        )

        job_id = state.get("job_id")
        if job_id and job_id in job_status:
            job_status[job_id]["events"].append(
                {
                    "type": "quality_review",
                    "message": "证据审核通过" if passed else "证据不足，准备修订",
                    **review.model_dump(),
                }
            )
        return {"quality_review": review.model_dump()}

    def route(self, state: ResearchState) -> Literal["revise", "continue"]:
        review = state.get("quality_review", {})
        if (
            not review.get("passed")
            and review.get("revision_count", 0) <= self.max_revisions
        ):
            return "revise"
        return "continue"
