from __future__ import annotations

from typing import List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

from config import settings
from models import Evidence


def search_evidence(query: str, max_results: int) -> List[Evidence]:
    results: List[Evidence] = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results, safesearch="moderate"):
            href = item.get("href") or item.get("url")
            if not href:
                continue
            domain = urlparse(href).netloc.replace("www.", "")
            evidence = Evidence(
                title=item.get("title") or "Untitled source",
                url=href,
                snippet=item.get("body") or "",
                source_domain=domain,
            )
            results.append(enrich_evidence(evidence))
    return results


def enrich_evidence(evidence: Evidence) -> Evidence:
    try:
        response = requests.get(
            str(evidence.url),
            timeout=settings.request_timeout_seconds,
            headers={"User-Agent": settings.user_agent},
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()
        text = " ".join(soup.get_text(" ").split())
        evidence.excerpt = text[:1200]
    except Exception:
        evidence.excerpt = ""
    return evidence

