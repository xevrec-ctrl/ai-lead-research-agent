"""Structured outputs used by the decision workflow."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class Evidence(BaseModel):
    claim: str = Field(
        description="A concise fact or inference supporting the analysis"
    )
    source_urls: list[str] = Field(
        default_factory=list,
        description="URLs from the supplied source catalog that support the claim",
    )
    confidence: float = Field(ge=0, le=1)


class OpportunityScore(BaseModel):
    need_fit: int = Field(ge=0, le=20, description="Match with the client's need")
    business_value: int = Field(ge=0, le=20)
    urgency: int = Field(ge=0, le=20)
    delivery_feasibility: int = Field(ge=0, le=20)
    evidence_quality: int = Field(ge=0, le=20)

    @property
    def total(self) -> int:
        return sum(
            (
                self.need_fit,
                self.business_value,
                self.urgency,
                self.delivery_feasibility,
                self.evidence_quality,
            )
        )


class PainPoint(BaseModel):
    title: str
    description: str
    evidence: list[Evidence] = Field(default_factory=list)
    priority: str = Field(description="high, medium, or low")


class AgentSolution(BaseModel):
    name: str
    target_problem: str
    workflow: list[str]
    tools_and_data: list[str]
    expected_value: str
    human_approval_points: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)


class OpportunityAssessment(BaseModel):
    executive_summary: str
    pain_points: list[PainPoint] = Field(min_length=1, max_length=5)
    score: OpportunityScore
    recommended_solutions: list[AgentSolution] = Field(min_length=1, max_length=3)
    discovery_questions: list[str] = Field(default_factory=list, max_length=8)
    limitations: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def limit_high_priority_solutions(self) -> "OpportunityAssessment":
        if len(self.recommended_solutions) > 3:
            raise ValueError("No more than three solutions may be recommended")
        return self

    def as_state_dict(self) -> dict:
        result = self.model_dump()
        result["score"]["total"] = self.score.total
        return result


class QualityReview(BaseModel):
    passed: bool
    citation_coverage: float = Field(ge=0, le=1)
    invalid_source_urls: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    revision_count: int = Field(ge=0)
