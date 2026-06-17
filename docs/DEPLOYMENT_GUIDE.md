# DEPLOYMENT GUIDE

## GitHub → Streamlit Cloud → Public URL

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Build production fact-check agent"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy on Streamlit Cloud

1. Open Streamlit Cloud.
2. Select **New app**.
3. Connect the GitHub repository.
4. Set the main file path to `app.py`.
5. Add optional secrets:

```toml
OPENAI_API_KEY = "optional"
SERPAPI_API_KEY = "optional"
```

6. Click **Deploy**.

### 3. Validate Public URL

- Upload a factual PDF.
- Confirm claims are extracted.
- Confirm evidence cards show URLs.
- Download Markdown and CSV reports.
- Save the public Streamlit URL for final submission.

## Production Notes

- For demos, DuckDuckGo Search is sufficient.
- For production, use a paid search API with SLA, retries, and result freshness controls.
- Add a queue worker for large PDFs so the UI remains responsive.

