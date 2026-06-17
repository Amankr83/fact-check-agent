from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    max_claims: int = int(os.getenv("FACT_CHECK_MAX_CLAIMS", "12"))
    max_evidence: int = int(os.getenv("FACT_CHECK_MAX_EVIDENCE", "5"))
    request_timeout_seconds: int = int(os.getenv("FACT_CHECK_TIMEOUT", "10"))
    user_agent: str = (
        "FactCheckAgent/1.0 (+https://streamlit.io; educational fact-checking demo)"
    )


settings = Settings()

