import os
from pydantic import BaseModel

class Settings(BaseModel):
    max_claims: int = int(os.getenv("FACT_CHECK_MAX_CLAIMS", "12"))
    max_evidence: int = int(os.getenv("FACT_CHECK_MAX_EVIDENCE", "5"))
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    serpapi_api_key: str = os.getenv("SERPAPI_API_KEY", "")

settings = Settings()