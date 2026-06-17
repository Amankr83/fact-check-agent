from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ClaimType(str, Enum):
    STATISTIC = "Statistic"
    DATE = "Date"
    PERCENTAGE = "Percentage"
    FINANCIAL = "Financial"
    TECHNICAL = "Technical"
    NAMED_ENTITY = "Named entity"
    GENERAL = "General factual claim"


class FactStatus(str, Enum):
    VERIFIED = "Verified"
    INACCURATE = "Inaccurate"
    FALSE = "False"


class ExtractedPage(BaseModel):
    page_number: int
    text: str


class Claim(BaseModel):
    id: int
    text: str
    page_number: Optional[int] = None
    claim_type: ClaimType = ClaimType.GENERAL
    query: str = ""


class Evidence(BaseModel):
    title: str = "Untitled source"
    url: HttpUrl
    snippet: str = ""
    source_domain: str = ""
    excerpt: str = ""


class FactCheckResult(BaseModel):
    claim: Claim
    status: FactStatus
    confidence: int = Field(ge=0, le=100)
    correct_fact: str
    rationale: str
    evidence: List[Evidence] = Field(default_factory=list)


class FactCheckReport(BaseModel):
    file_name: str
    total_claims: int
    verified: int
    inaccurate: int
    false: int
    average_confidence: float
    results: List[FactCheckResult]

