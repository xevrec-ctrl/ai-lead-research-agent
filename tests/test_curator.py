from backend.nodes.curator import Curator


def test_company_evidence_rejects_high_scoring_wrong_entity() -> None:
    curator = Curator()
    context = {"company": "四川宜宾若离网络科技服务有限责任公司", "industry": "Unknown"}
    documents = [
        {
            "title": "四川宜宾若离网络科技服务有限责任公司",
            "content": "企业登记信息",
            "url": "https://example.com/right",
            "score": 0.7,
            "doc_type": "company",
        },
        {
            "title": "Ruyi Network Technology Company Profile",
            "content": "An unrelated company",
            "url": "https://example.com/wrong",
            "score": 0.99,
            "doc_type": "company",
        },
    ]

    results = curator.evaluate_documents(documents, context)

    assert [item["url"] for item in results] == ["https://example.com/right"]
    assert results[0]["evaluation"]["entity_match"] is True


def test_general_industry_evidence_requires_supplied_industry() -> None:
    curator = Curator()
    document = {
        "title": "网络技术服务行业数字化趋势",
        "content": "网络技术服务企业正在采用自动化工作流",
        "url": "https://example.com/industry",
        "score": 0.8,
        "doc_type": "industry",
    }

    assert (
        curator.evaluate_documents(
            [document], {"company": "目标企业有限责任公司", "industry": "Unknown"}
        )
        == []
    )
    assert (
        len(
            curator.evaluate_documents(
                [document],
                {"company": "目标企业有限责任公司", "industry": "网络技术服务"},
            )
        )
        == 1
    )


def test_company_website_ranks_above_third_party_result() -> None:
    curator = Curator()
    documents = [
        {
            "title": "腾讯控股有限公司第三方资料",
            "url": "https://example.com/tencent",
            "score": 0.99,
            "doc_type": "company",
        },
        {
            "title": "投资者关系",
            "url": "https://www.tencent.com/investors",
            "score": 0,
            "source": "company_website",
            "doc_type": "company",
        },
    ]

    results = curator.evaluate_documents(
        documents, {"company": "腾讯控股有限公司", "industry": "互联网"}
    )

    assert results[0]["source"] == "company_website"
