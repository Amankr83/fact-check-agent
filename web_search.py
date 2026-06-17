from duckduckgo_search import DDGS
from urllib.parse import urlparse
from typing import List
from models import Evidence

def search_evidence(query: str, max_results: int = 5) -> List[Evidence]:
    evidence_list = []
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            if results:
                for r in results:
                    url = r.get("href")
                    title = r.get("title")
                    snippet = r.get("body")
                    source_domain = urlparse(url).netloc if url else None
                    
                    evidence = Evidence(
                        title=title or "Unknown Title",
                        url=url or "",
                        snippet=snippet,
                        excerpt="",
                        source_domain=source_domain
                    )
                    evidence_list.append(evidence)
    except Exception as e:
        print(f"Search error for query '{query}': {e}")
        
    return evidence_list