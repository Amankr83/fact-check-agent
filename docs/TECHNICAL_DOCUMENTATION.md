# TECHNICAL DOCUMENTATION

## Production Design Principles

- **Evidence-first:** Every classification includes URLs and snippets.
- **Transparent scoring:** Confidence is explainable through matching, mismatch, and source-count signals.
- **Graceful degradation:** The app works with deterministic rules if no LLM or paid search key is configured.
- **Extensible services:** Search, extraction, and validation are separate modules so SerpAPI, Gemini, OpenAI, or a vector database can be added later.
- **Auditability:** Reports include claim text, page number, status, confidence, correction, and evidence.

## Requirements.txt

The dependency list is in `requirements.txt` and includes Streamlit, PDF parsing, search, scraping, validation, data display, and charting libraries.

## Environment Variables

| Variable | Required | Purpose |
|---|---:|---|
| `OPENAI_API_KEY` | No | Optional enhancement for claim extraction or correction generation |
| `SERPAPI_API_KEY` | No | Future extension for more reliable search APIs |
| `FACT_CHECK_MAX_CLAIMS` | No | Default max claims processed |
| `FACT_CHECK_MAX_EVIDENCE` | No | Default evidence results per claim |

## Confidence Scoring Engine

The validator calculates:

- **Lexical overlap:** Shared meaningful tokens between claim and evidence.
- **Numeric agreement:** Numbers in the claim should appear in evidence or be semantically compatible.
- **Date agreement:** Years and dates are checked for direct support.
- **Evidence count:** Multiple independent snippets increase confidence.
- **Contradiction cues:** Terms such as "false," "misleading," "no evidence," and "debunked" reduce confidence.

## Error Handling

| Failure | Handling |
|---|---|
| Empty PDF page | Retry with pdfplumber; preserve page number |
| No claims found | Show a friendly empty state and recommend a more factual document |
| Search failure | Continue with remaining claims and classify unsupported claims conservatively |
| Page fetch failure | Use search result snippets as evidence |
| Network rate limit | Return partial report with failed evidence calls noted |

## Future Improvements

- Add SerpAPI/Bing Web Search for enterprise-grade retrieval.
- Add source credibility scoring using domain reputation and recency.
- Add exact numeric normalization for units such as million/billion/crore.
- Add an LLM judge with structured JSON output and citations.
- Add queueing for long PDFs.
- Add persistent project history and user accounts.

