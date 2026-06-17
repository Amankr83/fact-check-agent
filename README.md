# FactCheck Agent

FactCheck Agent is a production-oriented Streamlit web app that verifies factual claims inside uploaded PDFs. It extracts claims, searches live web evidence, classifies each claim, and exports an audit-ready report.

## Features

- PDF upload and page-level text extraction
- Factual claim extraction for statistics, dates, percentages, financial figures, technical claims, and named entities
- Live web evidence retrieval
- Confidence score out of 100
- Classification into Verified, Inaccurate, or False
- Evidence cards with source links
- Downloadable Markdown, CSV, and JSON reports
- Deterministic baseline that works without paid API keys

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit, upload a PDF, choose the number of claims and evidence results, then run the fact check.

## Optional Configuration

The current implementation works without secrets. These variables are reserved for stronger production integrations:

```bash
set OPENAI_API_KEY=optional
set SERPAPI_API_KEY=optional
set FACT_CHECK_MAX_CLAIMS=12
set FACT_CHECK_MAX_EVIDENCE=5
```

## Deployment

Deploy on Streamlit Cloud:

1. Push this repository to GitHub.
2. Create a new Streamlit Cloud app.
3. Set the entry point to `app.py`.
4. Add optional secrets if you use paid LLM or search APIs.
5. Deploy and test with a sample PDF.

More detail is available in `docs/DEPLOYMENT_GUIDE.md`.

## Screenshots

Placeholder:

- Landing and upload screen
- Progress indicator
- Results dashboard
- Evidence cards
- Download report panel

## Future Improvements

- Add SerpAPI or Bing Web Search for production-grade retrieval
- Add LLM-assisted claim extraction and contradiction analysis
- Add source credibility scoring
- Add persistent project history
- Add background jobs for long PDFs
- Add user authentication and team workspaces

