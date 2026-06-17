from __future__ import annotations

import plotly.express as px
import streamlit as st

from config import settings
from fact_checker import fact_check_pdf
from models import FactStatus
from report_generator import (
    build_csv_report,
    build_dataframe,
    build_json_report,
    build_markdown_report,
)


st.set_page_config(
    page_title="FactCheck Agent",
    page_icon="FC",
    layout="wide",
    initial_sidebar_state="expanded",
)


STATUS_COLORS = {
    FactStatus.VERIFIED.value: "#12805C",
    FactStatus.INACCURATE.value: "#B7791F",
    FactStatus.FALSE.value: "#C2413D",
}


def main() -> None:
    inject_styles()
    render_header()

    with st.sidebar:
        st.markdown("### Analysis controls")
        max_claims = st.slider(
            "Claims to verify",
            3,
            30,
            settings.max_claims,
            help="Higher values take longer because every claim triggers live evidence search.",
        )
        max_evidence = st.slider(
            "Evidence sources per claim",
            2,
            8,
            settings.max_evidence,
            help="More sources improve coverage but may increase runtime.",
        )
        st.divider()
        st.markdown("### What gets checked")
        st.caption(
            "Statistics, dates, percentages, financial figures, technical claims, "
            "named entities, and other factual statements."
        )
        st.divider()
        st.markdown("### Confidence model")
        st.caption(
            "Scores combine text overlap, number/date agreement, source count, "
            "and contradiction signals. Treat low-confidence results as review flags."
        )

    uploaded = st.file_uploader(
        "Upload a PDF to verify",
        type=["pdf"],
        help="Use a factual report, article, pitch deck, or research PDF.",
    )

    if not uploaded:
        render_empty_state()
        return

    render_file_panel(uploaded)

    run = st.button("Run fact check", type="primary", use_container_width=True)
    if not run and "last_report" not in st.session_state:
        st.info("Ready to analyze. Click **Run fact check** to extract claims and gather live evidence.")
        return

    if run:
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(message: str, value: float) -> None:
            status_text.markdown(f"**{message}**")
            progress_bar.progress(min(max(value, 0.0), 1.0))

        with st.spinner("Fact-checking document with live web evidence..."):
            st.session_state.last_report = fact_check_pdf(
                uploaded.getvalue(),
                uploaded.name,
                max_claims=max_claims,
                max_evidence=max_evidence,
                progress=update_progress,
            )

    render_report(st.session_state.last_report)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }
        .hero {
            border: 1px solid #E7E2D8;
            background: linear-gradient(135deg, #FFFBF2 0%, #F5F8FF 58%, #F8FFF8 100%);
            padding: 28px 30px;
            border-radius: 8px;
            margin-bottom: 22px;
        }
        .hero-kicker {
            color: #37546D;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .hero h1 {
            color: #152033;
            font-size: 2.55rem;
            line-height: 1.04;
            margin: 0 0 10px 0;
        }
        .hero p {
            color: #42526B;
            font-size: 1.02rem;
            max-width: 820px;
            margin: 0;
        }
        .workflow {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 10px;
            margin: 12px 0 22px 0;
        }
        .workflow-step {
            border: 1px solid #E5E8EF;
            background: #FFFFFF;
            border-radius: 8px;
            padding: 12px;
            color: #334155;
            font-size: 0.88rem;
            min-height: 70px;
        }
        .workflow-step strong {
            display: block;
            color: #172033;
            margin-bottom: 4px;
        }
        .file-panel {
            border: 1px solid #E2E8F0;
            background: #FFFFFF;
            border-radius: 8px;
            padding: 16px 18px;
            margin-bottom: 14px;
        }
        .status-badge {
            border-radius: 999px;
            color: #FFFFFF;
            display: inline-block;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            padding: 5px 10px;
            text-transform: uppercase;
        }
        .evidence-card {
            border-top: 1px solid #EEF2F7;
            padding-top: 10px;
            margin-top: 10px;
        }
        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E5E8EF;
            border-radius: 8px;
            padding: 12px 14px;
        }
        @media (max-width: 800px) {
            .workflow { grid-template-columns: 1fr; }
            .hero h1 { font-size: 2rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="hero-kicker">AI evidence workspace</div>
            <h1>FactCheck Agent</h1>
            <p>Upload a PDF, extract factual claims, retrieve live web evidence, and review each verdict with confidence scores, correction notes, and source links.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="workflow">
            <div class="workflow-step"><strong>1. Upload</strong>PDF report or article</div>
            <div class="workflow-step"><strong>2. Extract</strong>Checkable factual claims</div>
            <div class="workflow-step"><strong>3. Search</strong>Live web evidence</div>
            <div class="workflow-step"><strong>4. Classify</strong>Verified, inaccurate, false</div>
            <div class="workflow-step"><strong>5. Export</strong>Markdown, CSV, JSON</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("Start with a source document")
        st.write(
            "Use the upload control above to analyze a report, whitepaper, investor memo, "
            "or research document. The app will preserve the evidence trail for every claim."
        )
    with right:
        st.metric("Input", "PDF")
        st.metric("Outputs", "Dashboard + reports")
        st.metric("Scoring", "0-100 confidence")


def render_file_panel(uploaded) -> None:
    size_kb = len(uploaded.getvalue()) / 1024
    st.markdown(
        f"""
        <div class="file-panel">
            <strong>Selected file:</strong> {uploaded.name}<br>
            <span style="color:#5B667A;">Size: {size_kb:,.1f} KB</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_report(report) -> None:
    st.success(f"Analyzed {report.total_claims} claims from {report.file_name}.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Verified", report.verified)
    c2.metric("Inaccurate", report.inaccurate)
    c3.metric("False", report.false)
    c4.metric("Avg confidence", f"{report.average_confidence:.1f}/100")

    df = build_dataframe(report)
    if df.empty:
        st.warning("No checkable claims were found. Try a PDF with more dates, statistics, named entities, or factual statements.")
        return

    chart_col, table_col = st.columns([1.05, 1])
    with chart_col:
        chart_df = df.groupby("status", as_index=False).size()
        fig = px.bar(
            chart_df,
            x="status",
            y="size",
            color="status",
            text="size",
            color_discrete_map=STATUS_COLORS,
        )
        fig.update_layout(
            showlegend=False,
            yaxis_title="Claims",
            xaxis_title="",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=30, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)
    with table_col:
        st.dataframe(
            df[["claim_id", "claim_type", "status", "confidence"]],
            use_container_width=True,
            hide_index=True,
        )

    tab_results, tab_table, tab_downloads = st.tabs(["Evidence review", "Full table", "Export"])
    with tab_results:
        status_filter = st.segmented_control(
            "Filter by status",
            ["All", FactStatus.VERIFIED.value, FactStatus.INACCURATE.value, FactStatus.FALSE.value],
            default="All",
        )
        filtered_results = [
            result
            for result in report.results
            if status_filter == "All" or result.status.value == status_filter
        ]
        for result in filtered_results:
            render_result_card(result)

    with tab_table:
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab_downloads:
        markdown_report = build_markdown_report(report)
        csv_report = build_csv_report(report)
        json_report = build_json_report(report)
        d1, d2, d3 = st.columns(3)
        d1.download_button("Download Markdown", markdown_report, "fact_check_report.md", "text/markdown")
        d2.download_button("Download CSV", csv_report, "fact_check_report.csv", "text/csv")
        d3.download_button("Download JSON", json_report, "fact_check_report.json", "application/json")


def render_result_card(result) -> None:
    color = STATUS_COLORS[result.status.value]
    with st.container(border=True):
        top = st.columns([3, 1])
        with top[0]:
            st.markdown(f"**Claim {result.claim.id}** · Page {result.claim.page_number or 'n/a'} · {result.claim.claim_type.value}")
            st.write(result.claim.text)
        with top[1]:
            st.markdown(
                f'<span class="status-badge" style="background:{color};">{result.status.value}</span>',
                unsafe_allow_html=True,
            )
            st.metric("Confidence", f"{result.confidence}/100")

        st.progress(result.confidence / 100)
        st.markdown(f"**Correct fact:** {result.correct_fact}")
        st.caption(result.rationale)

        if not result.evidence:
            st.warning("No evidence sources were retrieved for this claim.")
            return

        with st.expander("Evidence sources", expanded=result.status != FactStatus.VERIFIED):
            for item in result.evidence:
                st.markdown('<div class="evidence-card">', unsafe_allow_html=True)
                st.markdown(f"**[{item.title}]({item.url})**")
                st.caption(item.source_domain)
                if item.snippet:
                    st.write(item.snippet)
                elif item.excerpt:
                    st.write(item.excerpt[:360])
                st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
