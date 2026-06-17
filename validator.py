from __future__ import annotations

import re
from collections import Counter
from typing import Iterable, List, Set

from models import Claim, Evidence, FactCheckResult, FactStatus


STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "by",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "has",
    "have",
    "had",
    "that",
    "this",
    "it",
    "from",
}
CONTRADICTION_TERMS = {
    "false",
    "misleading",
    "incorrect",
    "debunked",
    "no evidence",
    "not true",
    "unsupported",
}


def validate_claim(claim: Claim, evidence: List[Evidence]) -> FactCheckResult:
    evidence_text = " ".join(
        f"{item.title} {item.snippet} {item.excerpt}" for item in evidence
    )
    overlap = _token_overlap(claim.text, evidence_text)
    numeric_score = _numeric_alignment(claim.text, evidence_text)
    contradiction_penalty = _contradiction_penalty(evidence_text)
    source_bonus = min(len(evidence) * 4, 16)

    confidence = int(max(0, min(100, (overlap * 55) + numeric_score + source_bonus - contradiction_penalty)))

    if confidence >= 75:
        status = FactStatus.VERIFIED
        rationale = "Retrieved evidence strongly matches the claim and key factual signals align."
    elif confidence >= 45:
        status = FactStatus.INACCURATE
        rationale = "Evidence is topically related, but one or more factual signals appear partial, outdated, or insufficiently supported."
    else:
        status = FactStatus.FALSE
        rationale = "The retrieved evidence does not support the claim with enough confidence."

    return FactCheckResult(
        claim=claim,
        status=status,
        confidence=confidence,
        correct_fact=_correct_fact(claim, evidence, status),
        rationale=rationale,
        evidence=evidence,
    )


def _token_overlap(claim_text: str, evidence_text: str) -> float:
    claim_tokens = _tokens(claim_text)
    evidence_tokens = _tokens(evidence_text)
    if not claim_tokens or not evidence_tokens:
        return 0.0
    return len(claim_tokens & evidence_tokens) / max(len(claim_tokens), 1)


def _tokens(text: str) -> Set[str]:
    return {
        token
        for token in re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", text.lower())
        if token not in STOPWORDS
    }


def _numeric_alignment(claim_text: str, evidence_text: str) -> int:
    claim_numbers = _numbers(claim_text)
    if not claim_numbers:
        return 12
    evidence_numbers = _numbers(evidence_text)
    if not evidence_numbers:
        return -8
    matches = sum(1 for number in claim_numbers if number in evidence_numbers)
    if matches == len(claim_numbers):
        return 24
    if matches:
        return 8
    return -12


def _numbers(text: str) -> List[str]:
    return [number.replace(",", "") for number in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", text)]


def _contradiction_penalty(text: str) -> int:
    lowered = text.lower()
    return 18 if any(term in lowered for term in CONTRADICTION_TERMS) else 0


def _correct_fact(claim: Claim, evidence: Iterable[Evidence], status: FactStatus) -> str:
    best = next(iter(evidence), None)
    if status == FactStatus.VERIFIED:
        return f"The claim is supported by the retrieved evidence. Primary source: {best.source_domain if best else 'n/a'}."
    if best:
        snippet = best.snippet or best.excerpt
        if snippet:
            return f"Use the retrieved source from {best.source_domain} as the correction basis: {snippet[:280]}"
    return "No reliable correction could be generated from retrieved evidence. Re-check the claim with authoritative sources."


def summarize_status(results: List[FactCheckResult]) -> Counter:
    return Counter(result.status.value for result in results)

