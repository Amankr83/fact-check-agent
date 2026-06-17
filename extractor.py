from __future__ import annotations

import io
import re
from typing import Iterable, List

import fitz
import pdfplumber

from models import Claim, ClaimType, ExtractedPage


SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")
PERCENT_RE = re.compile(r"\b\d+(?:\.\d+)?\s?%")
MONEY_RE = re.compile(r"[$₹€£]\s?\d|(?:USD|INR|EUR|GBP)\s?\d", re.I)
DATE_RE = re.compile(r"\b(?:19|20)\d{2}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\b", re.I)
NUMBER_RE = re.compile(r"\b\d+(?:,\d{3})*(?:\.\d+)?\b")
TECH_RE = re.compile(r"\b(?:AI|API|LLM|model|database|algorithm|cloud|encryption|latency|accuracy|benchmark)\b", re.I)
ENTITY_RE = re.compile(r"\b[A-Z][a-zA-Z0-9&.-]+(?:\s+[A-Z][a-zA-Z0-9&.-]+){1,}\b")


def extract_pages(pdf_bytes: bytes) -> List[ExtractedPage]:
    pages: List[ExtractedPage] = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    with pdfplumber.open(io.BytesIO(pdf_bytes)) as plumber_pdf:
        for index, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if not text and index <= len(plumber_pdf.pages):
                text = (plumber_pdf.pages[index - 1].extract_text() or "").strip()
            pages.append(ExtractedPage(page_number=index, text=text))

    return pages


def extract_claims(pages: Iterable[ExtractedPage], max_claims: int) -> List[Claim]:
    claims: List[Claim] = []
    seen = set()

    for page in pages:
        for sentence in _sentences(page.text):
            normalized = _normalize(sentence)
            if normalized in seen or not _is_checkable(sentence):
                continue
            seen.add(normalized)
            claims.append(
                Claim(
                    id=len(claims) + 1,
                    text=sentence,
                    page_number=page.page_number,
                    claim_type=_classify(sentence),
                    query=_build_query(sentence),
                )
            )
            if len(claims) >= max_claims:
                return claims

    return claims


def _sentences(text: str) -> Iterable[str]:
    compact = _clean_text(text)
    for sentence in SENTENCE_RE.split(compact):
        sentence = _clean_sentence(sentence)
        if 45 <= len(sentence) <= 360:
            yield sentence


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\bExecutive Summary\b", " ", text, flags=re.I)
    text = re.sub(r"\bSection\s+\d+\s*:\s*", " ", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()


def _clean_sentence(sentence: str) -> str:
    sentence = sentence.strip(" -•\t")
    sentence = re.sub(
        r"^(?:\d{4}\s+)?(?:Global\s+)?AI\s+Industry\s+Snapshot\s+Report\s+",
        "",
        sentence,
        flags=re.I,
    )
    sentence = re.sub(
        r"^(?:AI User Growth|Global Internet Statistics|Technology Industry|Climate and Energy|Geography Check|Education and Workforce|Programming Languages|Workplace Trends|Financial Statistics|Important Note|Conclusion)\s+",
        "",
        sentence,
        flags=re.I,
    )
    return sentence.strip()


def _normalize(sentence: str) -> str:
    return re.sub(r"\W+", " ", sentence).lower().strip()


def _is_checkable(sentence: str) -> bool:
    signals = [
        PERCENT_RE.search(sentence),
        MONEY_RE.search(sentence),
        DATE_RE.search(sentence),
        NUMBER_RE.search(sentence),
        TECH_RE.search(sentence),
        ENTITY_RE.search(sentence),
    ]
    return sum(bool(signal) for signal in signals) >= 1


def _classify(sentence: str) -> ClaimType:
    if PERCENT_RE.search(sentence):
        return ClaimType.PERCENTAGE
    if MONEY_RE.search(sentence):
        return ClaimType.FINANCIAL
    if DATE_RE.search(sentence):
        return ClaimType.DATE
    if TECH_RE.search(sentence):
        return ClaimType.TECHNICAL
    if NUMBER_RE.search(sentence):
        return ClaimType.STATISTIC
    if ENTITY_RE.search(sentence):
        return ClaimType.NAMED_ENTITY
    return ClaimType.GENERAL


def _build_query(sentence: str) -> str:
    query = re.sub(r"[^a-zA-Z0-9 %$₹€£.-]", " ", sentence)
    query = re.sub(r"\s+", " ", query).strip()
    return query[:220]
