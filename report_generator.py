from __future__ import annotations

import json
from io import StringIO

import pandas as pd

from models import FactCheckReport


def build_markdown_report(report: FactCheckReport) -> str:
    lines = [
        f"# Fact-Check Report: {report.file_name}",
        "",
        "## Summary",
        "",
        f"- Total claims: {report.total_claims}",
        f"- Verified: {report.verified}",
        f"- Inaccurate: {report.inaccurate}",
        f"- False: {report.false}",
        f"- Average confidence: {report.average_confidence:.1f}/100",
        "",
        "## Claim Results",
        "",
    ]

    for result in report.results:
        lines.extend(
            [
                f"### Claim {result.claim.id}: {result.status.value}",
                "",
                f"**Claim:** {result.claim.text}",
                "",
                f"**Confidence:** {result.confidence}/100",
                "",
                f"**Correct fact:** {result.correct_fact}",
                "",
                f"**Rationale:** {result.rationale}",
                "",
                "**Evidence:**",
            ]
        )
        for item in result.evidence:
            lines.append(f"- [{item.title}]({item.url}) - {item.snippet}")
        lines.append("")

    return "\n".join(lines)


def build_dataframe(report: FactCheckReport) -> pd.DataFrame:
    rows = []
    for result in report.results:
        rows.append(
            {
                "claim_id": result.claim.id,
                "page": result.claim.page_number,
                "claim": result.claim.text,
                "claim_type": result.claim.claim_type.value,
                "status": result.status.value,
                "confidence": result.confidence,
                "correct_fact": result.correct_fact,
                "evidence_urls": "; ".join(str(item.url) for item in result.evidence),
            }
        )
    return pd.DataFrame(rows)


def build_csv_report(report: FactCheckReport) -> str:
    buffer = StringIO()
    build_dataframe(report).to_csv(buffer, index=False)
    return buffer.getvalue()


def build_json_report(report: FactCheckReport) -> str:
    return json.dumps(report.model_dump(mode="json"), indent=2)

