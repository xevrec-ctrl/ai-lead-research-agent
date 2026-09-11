from fastapi.testclient import TestClient

import application


def test_generate_pdf_supports_chinese_filename_and_content() -> None:
    client = TestClient(application.app)

    response = client.post(
        "/generate-pdf",
        json={
            "company_name": "中文测试企业",
            "report_content": "# 客户机会研究报告\n\n## 企业概况\n\n这是一段中文测试内容。",
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    disposition = response.headers["content-disposition"]
    assert 'filename="research_report.pdf"' in disposition
    assert "filename*=UTF-8''" in disposition
    assert response.content.startswith(b"%PDF-")
    assert len(response.content) > 1_000
