# PART 2 SYSTEM DESIGN

## Objective

Build an AI-powered fact-checking web application that accepts PDF uploads, extracts factual claims, verifies them against live web evidence, flags inaccuracies, returns corrected facts, and exports an evidence-backed report.

## A. System Architecture

```text
User
  ↓
Streamlit Frontend
  ↓
Python Backend Orchestrator
  ↓
PDF Parser
  ↓
Claim Extraction Engine
  ↓
Web Verification Engine
  ↓
Fact Classification Engine
  ↓
Report Generator
  ↓
Results Dashboard
```

### Components

| Component | Responsibility | Implementation |
|---|---|---|
| User | Uploads PDF and reviews results | Browser-based Streamlit app |
| Frontend | Upload, progress, filters, result cards, report download | `app.py` |
| Backend | Coordinates extraction, verification, scoring, report generation | `fact_checker.py` |
| PDF Parser | Extracts text from uploaded PDFs with page-level metadata | `extractor.py` using PyMuPDF and pdfplumber fallback |
| Claim Extraction Engine | Finds checkable factual claims: statistics, dates, percentages, money, named entities, technical claims | Heuristic extractor plus optional LLM enhancement |
| Web Verification Engine | Searches live web and retrieves evidence snippets/URLs | `web_search.py` using DuckDuckGo Search, requests, BeautifulSoup |
| Fact Classification Engine | Scores claim-evidence match and assigns Verified, Inaccurate, or False | `validator.py` |
| Report Generator | Creates Markdown/CSV/JSON deliverables | `report_generator.py` |
| Results Dashboard | Shows status summary, evidence cards, confidence bars, and exports | Streamlit tabs |

## B. Technology Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Streamlit | Fast production demo, supports uploads, progress states, downloadable reports |
| Backend | Python | Strong PDF, NLP, scraping, and data tooling ecosystem |
| PDF Parsing | PyMuPDF + pdfplumber | PyMuPDF is fast; pdfplumber is a robust fallback for complex layouts |
| Claim Extraction | Regex + spaCy-style heuristics, optional OpenAI | Deterministic baseline works without keys; LLM can improve claim quality |
| Search | DuckDuckGo Search; optional SerpAPI extension point | DuckDuckGo is accessible for demos; SerpAPI is production-friendly |
| Evidence Parsing | requests + BeautifulSoup | Lightweight extraction of page title and text snippets |
| Validation | Pydantic models + lexical similarity + numeric/date matching | Transparent scoring and auditability |
| Analytics | pandas + plotly | Clean summary tables and visuals |
| Deployment | GitHub + Streamlit Cloud | Simple public URL workflow for assignment submission |

## C. Implementation Plan

1. **PDF Upload:** User uploads a PDF through Streamlit. The app stores it in memory and passes bytes to the parser.
2. **Text Extraction:** PyMuPDF extracts page text. If a page is empty or malformed, pdfplumber retries.
3. **Claim Identification:** The claim engine splits text into sentences and selects checkable claims containing statistics, dates, percentages, financial figures, technical claims, or named entities.
4. **Web Search:** Each claim is converted into a search query. The search layer fetches top evidence results.
5. **Evidence Collection:** For each result, the app stores title, URL, snippet, source domain, and retrieved page excerpt when available.
6. **Fact Classification:** The validator computes confidence using source agreement, lexical overlap, number/date consistency, contradiction cues, and source count.
7. **Generate Report:** The app outputs a dashboard plus downloadable Markdown, CSV, and JSON reports.

## D. Fact-Check Logic

| Category | Conditions | Confidence Behavior |
|---|---|---|
| Verified | High confidence evidence match; numbers/dates align; multiple evidence sources agree | 75-100 |
| Inaccurate | Evidence broadly matches topic, but number/date/entity appears outdated, partial, or mismatched | 45-74 |
| False | No supporting evidence or evidence contradicts the claim | 0-44 |

The confidence score is out of 100 and is intentionally transparent. In production, this should be calibrated with labeled fact-checking datasets.

## E. Algorithm Pseudocode

```text
function fact_check_pdf(pdf_bytes):
    pages = extract_text(pdf_bytes)
    claims = extract_claims(pages.text)
    results = []

    for claim in claims:
        query = build_search_query(claim)
        evidence_items = search_web(query, max_results=5)
        enriched_evidence = []

        for item in evidence_items:
            page_excerpt = fetch_page_excerpt(item.url)
            enriched_evidence.append(merge(item, page_excerpt))

        classification = validate_claim(claim, enriched_evidence)
        correction = generate_correct_fact(claim, enriched_evidence, classification)

        results.append({
            claim,
            classification,
            confidence,
            correction,
            evidence
        })

    report = generate_report(results)
    return dashboard_payload(report)
```

## F. UI Design Wireframes

```text
Landing Page
┌──────────────────────────────────────────────┐
│ FactCheck Agent                              │
│ Verify factual claims from PDFs with evidence│
│ [Upload PDF] [Sample Trap Document]          │
└──────────────────────────────────────────────┘

Upload Section
┌ Upload PDF ──────────────────────────────────┐
│ Drag file here                               │
│ Options: max claims, evidence per claim      │
│ [Run fact check]                             │
└──────────────────────────────────────────────┘

Progress Indicator
Extracting PDF → Identifying claims → Searching web → Classifying → Building report

Results Dashboard
┌ Summary Cards: Verified | Inaccurate | False | Avg Confidence ┐
├ Bar Chart: Claims by Category                                  ┤
├ Evidence Cards                                                  ┤
│ Claim | Classification | Confidence Bar | Correct Fact | Sources │
└ [Download Markdown] [Download CSV] [Download JSON]              ┘
```

## G. Folder Structure

```text
Fast check Agent/
  app.py
  config.py
  extractor.py
  fact_checker.py
  models.py
  report_generator.py
  validator.py
  web_search.py
  requirements.txt
  README.md
  .streamlit/
    config.toml
  docs/
    PART_1_PPT_CONTENT.md
    PART_2_SYSTEM_DESIGN.md
    TECHNICAL_DOCUMENTATION.md
    DEPLOYMENT_GUIDE.md
    DEMO_VIDEO_SCRIPT.md
    FINAL_SUBMISSION_CHECKLIST.md
```

## L. Trap Document Handling

The system detects intentional lies by requiring factual claims to earn evidence support. A trap claim such as **"ChatGPT has 2 billion daily users"** is handled as follows:

- The claim is extracted because it contains a named entity and numeric statistic.
- Search queries target the exact claim plus trusted sources.
- If public evidence supports a materially different number or only reports prompts/users in another unit, the score is reduced for numeric mismatch.
- The app classifies the claim as **False** or **Inaccurate** depending on evidence quality.
- The corrected fact is generated from top evidence, for example: "Current publicly available reporting should be cited carefully because sources distinguish users, visits, and prompts; the uploaded claim's exact figure is not supported by the retrieved evidence."

