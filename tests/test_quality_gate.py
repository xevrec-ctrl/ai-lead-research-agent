from backend.nodes.quality_gate import EvidenceQualityGate


def test_quality_gate_accepts_only_retrieved_sources() -> None:
    url = "https://example.com/case"
    state = {
        "source_catalog": [{"url": url}],
        "opportunity_assessment": {
            "score": {"evidence_quality": 16},
            "pain_points": [
                {"evidence": [{"claim": "重复咨询较多", "source_urls": [url]}]}
            ],
            "recommended_solutions": [{"source_urls": [url]}],
        },
    }

    result = EvidenceQualityGate().run(state)

    assert result["quality_review"]["passed"] is True
    assert result["quality_review"]["citation_coverage"] == 1.0


def test_quality_gate_rejects_fabricated_source_and_requests_one_revision() -> None:
    gate = EvidenceQualityGate(max_revisions=1)
    state = {
        "source_catalog": [{"url": "https://example.com/real"}],
        "opportunity_assessment": {
            "score": {"evidence_quality": 16},
            "pain_points": [
                {
                    "evidence": [
                        {
                            "claim": "没有来源的结论",
                            "source_urls": ["https://invalid.example/fake"],
                        }
                    ]
                }
            ],
            "recommended_solutions": [{"source_urls": []}],
        },
    }

    first = gate.run(state)
    state.update(first)

    assert first["quality_review"]["passed"] is False
    assert gate.route(state) == "revise"

    second = gate.run(state)
    state.update(second)

    assert gate.route(state) == "continue"
    assert second["quality_review"]["revision_count"] == 2


def test_quality_gate_distinguishes_valid_citations_from_sufficient_evidence() -> None:
    url = "https://example.com/company"
    state = {
        "source_catalog": [{"url": url}],
        "opportunity_assessment": {
            "score": {"evidence_quality": 4},
            "pain_points": [{"evidence": [{"source_urls": [url]}]}],
            "recommended_solutions": [{"source_urls": [url]}],
        },
    }

    result = EvidenceQualityGate().run(state)["quality_review"]

    assert result["citation_coverage"] == 1.0
    assert result["passed"] is False
    assert any("证据质量评分" in issue for issue in result["issues"])
