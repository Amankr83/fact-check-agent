from __future__ import annotations

from typing import List
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

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
        for tag in soup(
            [
                "script",
                "style",
                "noscript",
                "svg",
                "nav",
                "header",
                "footer",
                "aside",
                "form",
                "table",
                "sup",
            ]
        ):
            tag.decompose()
        evidence.excerpt = _extract_readable_text(soup)
    except Exception:
        evidence.excerpt = ""
    return evidence


def _extract_readable_text(soup: BeautifulSoup) -> str:
    chunks = []
    description = soup.find("meta", attrs={"name": "description"})
    if description and description.get("content"):
        chunks.append(description["content"])

    main = soup.find("main") or soup.find("article") or soup.body or soup
    for tag in main.find_all(["h1", "h2", "p", "li"], limit=80):
        text = " ".join(tag.get_text(" ").split())
        if len(text) >= 45:
            chunks.append(text)

    if not chunks:
        chunks.append(" ".join(main.get_text(" ").split()))

    seen = set()
    deduped = []
    for chunk in chunks:
        normalized = chunk.lower()
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(chunk)
    return " ".join(deduped)[:2500]
