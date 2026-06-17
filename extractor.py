import fitz  # PyMuPDF
import pdfplumber
import io
import re
from typing import List, Dict, Any
from models import Claim, ClaimType

def extract_pages(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    pages = []
    try:
        doc = fitz.open("pdf", pdf_bytes)
        for i in range(len(doc)):
            page = doc[i]
            text = page.get_text()
            if text.strip():
                pages.append({"page_number": i + 1, "text": text})
    except Exception:
        # Fallback to pdfplumber
        pages = []
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append({"page_number": i + 1, "text": text})
        except Exception:
            pass
    return pages

def extract_claims(pages: List[Dict[str, Any]], max_claims: int) -> List[Claim]:
    claims = []
    claim_id = 1
    for page in pages:
        text = page["text"]
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 20:
                continue
            
            claim_type = ClaimType.OTHER
            if re.search(r'\b\d{4}\b', sentence):
                claim_type = ClaimType.DATE
            elif '%' in sentence or 'percent' in sentence.lower():
                claim_type = ClaimType.PERCENTAGE
            elif '$' in sentence or 'billion' in sentence.lower() or 'million' in sentence.lower():
                claim_type = ClaimType.FINANCIAL
            elif re.search(r'\d+', sentence):
                claim_type = ClaimType.STATISTIC
            elif re.search(r'\b[A-Z][a-z]+\b', sentence):
                claim_type = ClaimType.ENTITY
            
            if claim_type != ClaimType.OTHER:
                claims.append(Claim(
                    id=claim_id,
                    text=sentence,
                    page_number=page["page_number"],
                    claim_type=claim_type,
                    query=sentence
                ))
                claim_id += 1
                if len(claims) >= max_claims:
                    return claims
    return claims