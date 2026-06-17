from __future__ import annotations

from statistics import mean
from typing import Callable, Optional

from config import settings
from extractor import extract_claims, extract_pages
from models import FactCheckReport, FactStatus
from validator import validate_claim
from web_search import search_evidence


ProgressCallback = Optional[Callable[[str, float], None]]


def fact_check_pdf(
    pdf_bytes: bytes,
    file_name: str,
    max_claims: int = settings.max_claims,
    max_evidence: int = settings.max_evidence,
    progress: ProgressCallback = None,
) -> FactCheckReport:
    _emit(progress, "Extracting PDF text", 0.1)
    pages = extract_pages(pdf_bytes)

    _emit(progress, "Identifying factual claims", 0.25)
    claims = extract_claims(pages, max_claims=max_claims)

    results = []
    for index, claim in enumerate(claims, start=1):
        base_progress = 0.25 + (index / max(len(claims), 1)) * 0.6
        _emit(progress, f"Searching evidence for claim {index}/{len(claims)}", base_progress)
        try:
            evidence = search_evidence(claim.query or claim.text, max_results=max_evidence)
        except Exception:
            evidence = []
        results.append(validate_claim(claim, evidence))

    _emit(progress, "Building report", 0.95)
    verified = sum(1 for item in results if item.status == FactStatus.VERIFIED)
    inaccurate = sum(1 for item in results if item.status == FactStatus.INACCURATE)
    false = sum(1 for item in results if item.status == FactStatus.FALSE)
    average_confidence = mean([item.confidence for item in results]) if results else 0.0

    _emit(progress, "Complete", 1.0)
    return FactCheckReport(
        file_name=file_name,
        total_claims=len(results),
        verified=verified,
        inaccurate=inaccurate,
        false=false,
        average_confidence=average_confidence,
        results=results,
    )


def _emit(progress: ProgressCallback, message: str, value: float) -> None:
    if progress:
        progress(message, value)

