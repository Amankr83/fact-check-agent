from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class FactStatus(Enum):
    VERIFIED = "Verified"
    INACCURATE = "Inaccurate"
    FALSE = "False"

class ClaimType(Enum):
    STATISTIC = "Statistic"
    DATE = "Date"
    PERCENTAGE = "Percentage"
    FINANCIAL = "Financial"
    TECHNICAL = "Technical"
    ENTITY = "Named Entity"
    OTHER = "Other"

class Claim(BaseModel):
    id: int
    text: str
    page_number: Optional[int] = None
    claim_type: ClaimType = ClaimType.OTHER
    query: Optional[str] = None

class Evidence(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    excerpt: Optional[str] = None
    source_domain: Optional[str] = None

class FactCheckResult(BaseModel):
    claim: Claim
    status: FactStatus
    confidence: int
    correct_fact: str
    rationale: str
    evidence: List[Evidence]

class FactCheckReport(BaseModel):
    file_name: str
    total_claims: int
    verified: int
    inaccurate: int
    false: int
    average_confidence: float
    results: List[FactCheckResult]