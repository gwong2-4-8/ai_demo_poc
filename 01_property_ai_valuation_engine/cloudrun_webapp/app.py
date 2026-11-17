# Copyright 2026 Google LLC
# SPDX-License-Identifier: Apache-2.0
"""Cotality Property Trend & AI Valuation — Interactive BigQuery AI/ML Cloud Run WebApp."""

import html
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from google.cloud import bigquery
from google.cloud import storage

from demo_queries import (
    FEATURED_PROPERTY_PHOTOS,
    TALK_TRACKS,
    ensure_knowledge_bundle,
    get_create_core_tables_sql,
    get_step4_photo_insights_ddl,
    get_step5_screening_ddl,
    get_step6_backtest_sql,
    get_step6_forecast_ddl,
    get_step7_eval_sql,
    get_step7_predict_ddl,
    get_step8_unified_cards_sql,
)

# ---------------------------------------------------------------------------
# 1. Page Configuration (MUST be first Streamlit command)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Cotality Property Trend & AI Valuation | BigQuery AI & ML",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 2. Session State Initialization
# ---------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "show_talk_track" not in st.session_state:
    st.session_state.show_talk_track = True
if "project_id" not in st.session_state:
    st.session_state.project_id = os.environ.get("PROJECT_ID", "cotality-proj")
if "dataset_id" not in st.session_state:
    st.session_state.dataset_id = os.environ.get("DATASET_ID", "cotality_property")
if "location" not in st.session_state:
    st.session_state.location = os.environ.get("LOCATION", "US")
if "bucket_name" not in st.session_state:
    st.session_state.bucket_name = os.environ.get("BUCKET_NAME", "cotality-workshop")
if "connection_id" not in st.session_state:
    st.session_state.connection_id = os.environ.get("CONNECTION_ID", "us.cotality-conn")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

is_dark = st.session_state.theme == "dark"

# ---------------------------------------------------------------------------
# 3. SaaS Design System CSS (Zinc / shadcn tokens + Light/Dark Mode)
# ---------------------------------------------------------------------------
THEME_VARS = (
    """
    --bg-page: #09090b;
    --bg-card: #18181b;
    --bg-card-hover: #27272a;
    --bg-elevated: #27272a;
    --bg-glass: rgba(24, 24, 27, 0.75);
    --text-primary: #fafafa;
    --text-secondary: #a1a1aa;
    --text-muted: #71717a;
    --border: #27272a;
    --border-subtle: #1f1f23;
    --accent: #6366f1;
    --accent-light: #818cf8;
    --accent-bg: rgba(99, 102, 241, 0.12);
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.4);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.5);
    """
    if is_dark
    else """
    --bg-page: #fafafa;
    --bg-card: #ffffff;
    --bg-card-hover: #f4f4f5;
    --bg-elevated: #f4f4f5;
    --bg-glass: rgba(255, 255, 255, 0.85);
    --text-primary: #09090b;
    --text-secondary: #52525b;
    --text-muted: #a1a1aa;
    --border: #e4e4e7;
    --border-subtle: #f4f4f5;
    --accent: #4f46e5;
    --accent-light: #6366f1;
    --accent-bg: rgba(79, 70, 229, 0.08);
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.04);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.06);
    """
)

st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {{
    {THEME_VARS}
}}

html, body, .stApp {{
    background-color: var(--bg-page) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

/* Hide default Streamlit chrome */
header[data-testid="stHeader"] {{ background: transparent !important; height: 0 !important; min-height: 0 !important; }}
.stDeployButton, [data-testid="stToolbar"], #MainMenu, footer {{ display: none !important; }}
.block-container {{
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1440px !important;
}}

/* Typography helpers */
.app-header {{
    padding: 0.25rem 0 1.25rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.25rem;
}}
.app-header-eyebrow {{
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--accent-light);
    margin-bottom: 0.25rem;
}}
.app-header h1 {{
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--text-primary) !important;
    letter-spacing: -0.025em;
    margin: 0;
    line-height: 1.25;
}}
.app-header p {{
    font-size: 0.88rem;
    color: var(--text-secondary);
    margin: 0.35rem 0 0 0;
}}

/* Metric cards */
.metric-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    box-shadow: var(--shadow-sm);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
}}
.metric-card:hover {{
    border-color: var(--accent);
    box-shadow: var(--shadow-md);
}}
.metric-card .label {{
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
    margin-bottom: 0.4rem;
}}
.metric-card .value {{
    font-size: 1.65rem;
    font-weight: 700;
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.03em;
    line-height: 1.15;
}}
.metric-card .sub {{
    font-size: 0.76rem;
    color: var(--text-secondary);
    margin-top: 0.35rem;
}}

/* Presenter Talk Track Card */
.talk-track-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 10px;
    padding: 1.1rem 1.35rem;
    margin-bottom: 1.25rem;
    box-shadow: var(--shadow-sm);
}}
.talk-track-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 0.45rem;
}}
.talk-track-title {{
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--accent-light);
}}
.talk-track-body {{
    font-size: 0.9rem;
    color: var(--text-primary);
    line-height: 1.55;
    margin-bottom: 0.6rem;
}}
.talk-track-footer {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    font-size: 0.8rem;
    color: var(--text-secondary);
    padding-top: 0.55rem;
    border-top: 1px solid var(--border-subtle);
}}

/* Section headers */
.section-header {{
    margin: 1.25rem 0 0.85rem 0;
}}
.section-header h2 {{
    font-size: 1.12rem;
    font-weight: 600;
    color: var(--text-primary) !important;
    letter-spacing: -0.015em;
    margin: 0;
}}
.section-header p {{
    font-size: 0.82rem;
    color: var(--text-muted);
    margin: 0.15rem 0 0 0;
}}

/* Chart wrapper */
.chart-wrap {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.15rem 0.5rem 1.15rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}}
.chart-wrap .chart-title {{
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.1rem;
}}
.chart-wrap .chart-sub {{
    font-size: 0.76rem;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}}

/* Custom HTML data tables */
.data-table-wrap {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow-x: auto;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}}
.data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.83rem;
}}
.data-table th {{
    background: var(--bg-elevated);
    color: var(--text-muted);
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.69rem;
    letter-spacing: 0.06em;
    padding: 0.7rem 0.95rem;
    text-align: left;
    border-bottom: 1px solid var(--border);
    white-space: nowrap;
}}
.data-table td {{
    padding: 0.68rem 0.95rem;
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border-subtle);
    font-variant-numeric: tabular-nums;
    vertical-align: top;
}}
.data-table tr:last-child td {{ border-bottom: none; }}
.data-table tr:hover td {{
    background: var(--bg-card-hover);
    color: var(--text-primary);
}}
.mono-cell {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-primary) !important;
}}

/* Badges */
.badge {{
    display: inline-block;
    padding: 0.18rem 0.55rem;
    border-radius: 6px;
    font-size: 0.71rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    font-family: 'JetBrains Mono', monospace;
    white-space: nowrap;
}}
.badge-emerald {{ background: rgba(16, 185, 129, 0.14); color: #10b981; }}
.badge-amber   {{ background: rgba(245, 158, 11, 0.14); color: #f59e0b; }}
.badge-rose    {{ background: rgba(244, 63, 94, 0.14);  color: #f43f5e; }}
.badge-indigo  {{ background: var(--accent-bg); color: var(--accent-light); }}
.badge-cyan    {{ background: rgba(6, 182, 212, 0.14);  color: #06b6d4; }}

/* Pill-style tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 0.25rem;
    background: var(--bg-elevated);
    border-radius: 10px;
    padding: 0.3rem;
    border: 1px solid var(--border);
    flex-wrap: wrap;
}}
.stTabs [data-baseweb="tab"] {{
    border-radius: 7px;
    color: var(--text-secondary) !important;
    font-weight: 500;
    font-size: 0.82rem;
    padding: 0.45rem 0.9rem;
}}
.stTabs [aria-selected="true"] {{
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    font-weight: 600;
    box-shadow: var(--shadow-sm);
}}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{
    display: none;
}}

/* Valuation Card */
.val-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.15rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 1rem;
}}
.val-card-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.65rem;
}}
.val-card-title {{
    font-size: 1.02rem;
    font-weight: 700;
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
}}
.val-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.55rem;
    margin: 0.7rem 0;
    padding: 0.65rem;
    background: var(--bg-elevated);
    border-radius: 8px;
}}
.val-kpi-item .k {{
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
}}
.val-kpi-item .v {{
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text-primary);
    font-family: 'JetBrains Mono', monospace;
    font-variant-numeric: tabular-nums;
}}
.val-brief {{
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.5;
    padding-top: 0.55rem;
    border-top: 1px solid var(--border-subtle);
}}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# 4. Plotly Layout Helper & UI Render Helpers
# ---------------------------------------------------------------------------
def get_chart_layout(height: int = 360) -> Dict[str, Any]:
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="DM Sans, sans-serif",
            color="#a1a1aa" if is_dark else "#52525b",
            size=12,
        ),
        margin=dict(l=12, r=12, t=24, b=12),
        height=height,
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.05)" if is_dark else "rgba(0,0,0,0.05)",
            zerolinecolor="rgba(255,255,255,0.08)" if is_dark else "rgba(0,0,0,0.08)",
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.05)" if is_dark else "rgba(0,0,0,0.05)",
            zerolinecolor="rgba(255,255,255,0.08)" if is_dark else "rgba(0,0,0,0.08)",
        ),
        hoverlabel=dict(
            bgcolor="#18181b" if is_dark else "#ffffff",
            bordercolor="#27272a" if is_dark else "#e4e4e7",
            font=dict(
                family="DM Sans, sans-serif",
                size=12,
                color="#fafafa" if is_dark else "#09090b",
            ),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )


def render_talk_track(key: str) -> None:
    """Renders the presenter talk track card if enabled."""
    if not st.session_state.show_talk_track:
        return
    item = TALK_TRACKS.get(key)
    if not item:
        return
    st.markdown(
        f"""
        <div class="talk-track-card">
            <div class="talk-track-header">
                <div class="talk-track-title">🎙️ {html.escape(item["title"])}</div>
                <span class="badge badge-indigo">LIVE PRESENTER TALK TRACK</span>
            </div>
            <div class="talk-track-body">{html.escape(item["narrative"])}</div>
            <div class="talk-track-footer">
                <div><strong>💡 Key Value Takeaway:</strong> {html.escape(item["takeaway"])}</div>
                <div><strong>🛡️ Technical Q&amp;A Tip:</strong> {html.escape(item["qa_tip"])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, sub: str) -> str:
    return f"""
    <div class="metric-card">
        <div class="label">{html.escape(label)}</div>
        <div class="value">{html.escape(value)}</div>
        <div class="sub">{sub}</div>
    </div>
    """


def format_badge(text: str, variant: str = "indigo") -> str:
    return f'<span class="badge badge-{variant}">{html.escape(str(text))}</span>'


def render_html_table(
    df: pd.DataFrame,
    currency_cols: Optional[List[str]] = None,
    pct_cols: Optional[List[str]] = None,
    mono_cols: Optional[List[str]] = None,
    badge_cols: Optional[Dict[str, Dict[str, str]]] = None,
    max_rows: int = 50,
) -> None:
    """Renders a DataFrame as a styled SaaS HTML table (.data-table)."""
    if df is None or df.empty:
        st.info("No rows returned.")
        return

    currency_cols = currency_cols or []
    pct_cols = pct_cols or []
    mono_cols = mono_cols or []
    badge_cols = badge_cols or {}

    subset = df.head(max_rows)
    headers = "".join(f"<th>{html.escape(str(c))}</th>" for c in subset.columns)
    rows_html = []
    for _, row in subset.iterrows():
        cells = []
        for col in subset.columns:
            val = row[col]
            if isinstance(val, (list, tuple, np.ndarray)) or hasattr(val, "tolist"):
                arr = val.tolist() if hasattr(val, "tolist") else list(val)
                tags = " ".join(format_badge(str(x), "indigo") for x in arr)
                cells.append(f"<td>{tags}</td>")
            elif pd.isna(val):
                cells.append("<td>—</td>")
            elif col in badge_cols:
                mapping = badge_cols[col]
                s_val = str(val)
                variant = mapping.get(s_val, "indigo")
                cells.append(f"<td>{format_badge(s_val, variant)}</td>")
            elif col in currency_cols and isinstance(val, (int, float, np.number)):
                cells.append(f'<td class="mono-cell">${float(val):,.0f}</td>')
            elif col in pct_cols and isinstance(val, (int, float, np.number)):
                cells.append(f'<td class="mono-cell">{float(val):,.2f}%</td>')
            elif col in mono_cols:
                cells.append(f'<td class="mono-cell">{html.escape(str(val))}</td>')
            else:
                cells.append(f"<td>{html.escape(str(val))}</td>")
        rows_html.append(f"<tr>{''.join(cells)}</tr>")

    table_html = f"""
    <div class="data-table-wrap">
        <table class="data-table">
            <thead><tr>{headers}</tr></thead>
            <tbody>{''.join(rows_html)}</tbody>
        </table>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 5. Live BigQuery Execution Helpers (Zero Mocking)
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_bq_client(project_id: str, location: str) -> bigquery.Client:
    return bigquery.Client(project=project_id, location=location)


def run_bq_query(
    sql: str,
    project_id: str,
    location: str,
    params: Optional[List[Any]] = None,
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any], Optional[str]]:
    """Executes a live BigQuery SQL statement and returns (DataFrame, telemetry, error)."""
    t0 = time.perf_counter()
    try:
        client = get_bq_client(project_id, location)
        job_config = bigquery.QueryJobConfig()
        if params:
            job_config.query_parameters = params
        job = client.query(sql, job_config=job_config)
        df = job.to_dataframe()
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        bytes_proc = job.total_bytes_processed or 0
        telemetry = {
            "elapsed_ms": elapsed_ms,
            "rows": len(df),
            "bytes_processed": bytes_proc,
            "job_id": job.job_id,
        }
        return df, telemetry, None
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        return None, {"elapsed_ms": elapsed_ms, "rows": 0, "bytes_processed": 0}, str(exc)


@st.cache_data(ttl=120, show_spinner=False)
def fetch_cached_table(
    project_id: str, dataset_id: str, location: str, query_sql: str
) -> Tuple[Optional[pd.DataFrame], Dict[str, Any], Optional[str]]:
    return run_bq_query(query_sql, project_id, location)


def render_telemetry_pill(telemetry: Dict[str, Any], sql: str, label: str = "View Executed GoogleSQL") -> None:
    kb = (telemetry.get("bytes_processed", 0) or 0) / 1024.0
    elapsed_ms = telemetry.get("elapsed_ms", 0)
    rows_cnt = telemetry.get("rows", 0)
    st.markdown(
        f'<div style="display:flex;gap:8px;align-items:center;margin:0.35rem 0 0.65rem 0;">'
        f'{format_badge("LIVE BIGQUERY SQL", "emerald")}'
        f'{format_badge(f"{elapsed_ms:,} ms", "indigo")}'
        f'{format_badge(f"{rows_cnt:,} rows", "cyan")}'
        f'{format_badge(f"{kb:,.1f} KB scanned", "amber")}'
        f"</div>",
        unsafe_allow_html=True,
    )
    with st.expander(f"🔎 {label}", expanded=False):
        st.code(sql, language="sql")


# ---------------------------------------------------------------------------
# 6. Top App Header & Controls
# ---------------------------------------------------------------------------
hdr_left, hdr_mid1, hdr_mid2, hdr_right = st.columns([6.2, 1.5, 1.3, 1.0])
with hdr_left:
    st.markdown(
        f"""
        <div class="app-header" style="border-bottom:none;margin-bottom:0.25rem;padding-bottom:0;">
            <div class="app-header-eyebrow">GOOGLE CLOUD · BIGQUERY AI &amp; ML INTERACTIVE DEMO</div>
            <h1>Cotality Residential Property Trend &amp; AI Valuation Studio</h1>
            <p>Zero-ETL Multimodal Vision (<code>ObjectRef</code>), Semantic Screening (<code>AI.IF</code> / <code>AI.CLASSIFY</code>), Multi-Metro Forecasting (<code>TimesFM</code>), &amp; Comparable Valuation (<code>TabFM</code>) in SQL · Dataset: <code>{html.escape(st.session_state.project_id)}.{html.escape(st.session_state.dataset_id)}</code></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with hdr_mid1:
    talk_label = "🎙️ Talk Track: ON" if st.session_state.show_talk_track else "🎙️ Talk Track: OFF"
    if st.button(talk_label, key="toggle_talk_track", width="stretch"):
        st.session_state.show_talk_track = not st.session_state.show_talk_track
        st.rerun()
with hdr_mid2:
    with st.popover("⚙️ GCP Config", width="stretch"):
        st.markdown("**BigQuery & GCS Target Environment**")
        new_proj = st.text_input("Project ID", value=st.session_state.project_id)
        new_ds = st.text_input("Dataset ID", value=st.session_state.dataset_id)
        new_loc = st.text_input("Location", value=st.session_state.location)
        new_bkt = st.text_input("GCS Bucket", value=st.session_state.bucket_name)
        new_conn = st.text_input("BQ Connection ID", value=st.session_state.connection_id)
        if st.button("Apply Configuration", type="primary", width="stretch"):
            st.session_state.project_id = new_proj.strip()
            st.session_state.dataset_id = new_ds.strip()
            st.session_state.location = new_loc.strip()
            st.session_state.bucket_name = new_bkt.strip()
            st.session_state.connection_id = new_conn.strip()
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()
with hdr_right:
    theme_btn = "☀️ Light" if is_dark else "🌙 Dark"
    if st.button(theme_btn, key="theme_toggle", width="stretch"):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()

st.markdown('<hr style="border:none;border-top:1px solid var(--border);margin:0.4rem 0 1rem 0;">', unsafe_allow_html=True)

PROJECT_ID = st.session_state.project_id
DATASET_ID = st.session_state.dataset_id
LOCATION = st.session_state.location
BUCKET_NAME = st.session_state.bucket_name
CONNECTION_ID = st.session_state.connection_id

# Render Opening Pitch Talk Track
render_talk_track("overview")

# ---------------------------------------------------------------------------
# 7. Top KPI Row (Live Table Inventory from BigQuery)
# ---------------------------------------------------------------------------
inventory_sql = f"""
SELECT
  table_name,
  row_count
FROM (
  SELECT 'properties' AS table_name, COUNT(*) AS row_count FROM `{PROJECT_ID}.{DATASET_ID}.properties`
  UNION ALL
  SELECT 'sold_and_rent_history', COUNT(*) FROM `{PROJECT_ID}.{DATASET_ID}.sold_and_rent_history`
  UNION ALL
  SELECT 'property_comps', COUNT(*) FROM `{PROJECT_ID}.{DATASET_ID}.property_comps`
)
"""
inv_df, inv_meta, inv_err = fetch_cached_table(PROJECT_ID, DATASET_ID, LOCATION, inventory_sql)

row_map: Dict[str, int] = {}
if inv_df is not None and not inv_df.empty:
    row_map = dict(zip(inv_df["table_name"], inv_df["row_count"]))

k1, k2, k3, k4 = st.columns(4)
with k1:
    cnt_prop = f"{row_map.get('properties', 0):,}" if not inv_err else "Not Provisioned"
    st.markdown(
        render_metric_card(
            "Active Property Listings",
            cnt_prop,
            f"<code>{DATASET_ID}.properties</code> · Clustered by Metro &amp; Type",
        ),
        unsafe_allow_html=True,
    )
with k2:
    cnt_hist = f"{row_map.get('sold_and_rent_history', 0):,}" if not inv_err else "Not Provisioned"
    st.markdown(
        render_metric_card(
            "Monthly Metro History Rows",
            cnt_hist,
            "5 Metros × 72 Months (2020–2025) · Partitioned by <code>month_date</code>",
        ),
        unsafe_allow_html=True,
    )
with k3:
    cnt_comps = f"{row_map.get('property_comps', 0):,}" if not inv_err else "Not Provisioned"
    st.markdown(
        render_metric_card(
            "Comparable Sales & Rentals",
            cnt_comps,
            "190 <code>TRAIN</code> + 50 <code>VALIDATION</code> Comps for TabFM",
        ),
        unsafe_allow_html=True,
    )
with k4:
    st.markdown(
        render_metric_card(
            "Multimodal GCS Photos",
            "6 CC0 Exterior Images",
            f"<code>gs://{html.escape(BUCKET_NAME)}/cotality_property_demo/images/</code>",
        ),
        unsafe_allow_html=True,
    )

if inv_err:
    st.warning(
        f"Live BigQuery table check returned an error or tables are not yet created: `{inv_err}`. "
        "Use the **1-Click Provision / Refresh Demo Data** button in Tab 1 or verify your GCP credentials."
    )

st.markdown("<div style='height: 0.65rem;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# 8. Pill-Style Navigation Tabs Across All 8 Demo Stages
# ---------------------------------------------------------------------------
tabs = st.tabs(
    [
        "1. Architecture & Data Setup",
        "2. Knowledge Grounding",
        "3. Multimodal Photo AI",
        "4. Screening (AI.IF / CLASSIFY)",
        "5. 12M Forecast (TimesFM)",
        "6. Comp Valuation (TabFM)",
        "7. Unified Valuation Cards",
        "8. 💬 Ask Your Data",
    ]
)

# ===========================================================================
# TAB 1: ARCHITECTURE & DATA FOUNDATION (Steps 1 & 2)
# ===========================================================================
with tabs[0]:
    render_talk_track("tab1_foundation")

    col_arch, col_ops = st.columns([6.5, 3.5])
    with col_arch:
        st.markdown(
            """
            <div class="section-header" style="margin-top:0;">
                <h2>End-to-End BigQuery AI &amp; ML Reference Architecture</h2>
                <p>Zero-ETL architecture uniting structured tables, GCS Object Tables, Open Knowledge Format, Gemini, TimesFM, and TabFM</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        arch_img_path = APP_DIR / "cotality_property_trend_demo_architecture.png"
        if arch_img_path.exists():
            st.image(str(arch_img_path), width="stretch")
        else:
            st.info("Architecture diagram image not found in application bundle.")

    with col_ops:
        st.markdown(
            """
            <div class="section-header" style="margin-top:0;">
                <h2>Live Environment &amp; Data Provisioning</h2>
                <p>Stage CC0 property photos to GCS and build the 3 core partitioned/clustered tables in BigQuery</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚀 1-Click Provision / Refresh Core Tables & GCS Photos", type="primary", width="stretch"):
            with st.status("Provisioning GCS photos and BigQuery core tables...", expanded=True) as status_box:
                try:
                    # 1. Ensure dataset exists
                    bq_client = get_bq_client(PROJECT_ID, LOCATION)
                    ds_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
                    ds_ref.location = LOCATION
                    bq_client.create_dataset(ds_ref, exists_ok=True)
                    st.write(f"✅ Verified BigQuery dataset `{PROJECT_ID}.{DATASET_ID}` (`{LOCATION}`).")

                    # 2. Upload 6 local property images to GCS
                    storage_client = storage.Client(project=PROJECT_ID)
                    bucket = storage_client.bucket(BUCKET_NAME)
                    img_dir = APP_DIR / "property_images"
                    uploaded = 0
                    for prop_id, meta in FEATURED_PROPERTY_PHOTOS.items():
                        local_f = img_dir / meta["file"]
                        if local_f.exists():
                            blob = bucket.blob(f"cotality_property_demo/images/{meta['file']}")
                            blob.upload_from_filename(str(local_f), content_type="image/jpeg")
                            uploaded += 1
                    st.write(f"✅ Uploaded `{uploaded}` CC0 property exterior photos to `gs://{BUCKET_NAME}/cotality_property_demo/images/`.")

                    # 3. Create 3 core tables
                    ddls = get_create_core_tables_sql(PROJECT_ID, DATASET_ID, BUCKET_NAME)
                    for tbl_name, ddl_sql in ddls.items():
                        _, t_meta, t_err = run_bq_query(ddl_sql, PROJECT_ID, LOCATION)
                        if t_err:
                            raise RuntimeError(f"Failed creating {tbl_name}: {t_err}")
                        st.write(f"✅ Created `{PROJECT_ID}.{DATASET_ID}.{tbl_name}` in `{t_meta['elapsed_ms']} ms`.")

                    st.cache_data.clear()
                    status_box.update(label="Core tables and GCS photos provisioned!", state="complete")
                    st.rerun()
                except Exception as provision_err:
                    status_box.update(label="Provisioning encountered an error", state="error")
                    st.error(str(provision_err))

        st.markdown(
            """
            <div class="section-header">
                <h2>Automated Data Profiling (<code>ML.DESCRIBE_DATA</code>)</h2>
                <p>Single-statement statistical profiling across numeric and categorical columns</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        profile_target = st.selectbox(
            "Select Table to Profile with ML.DESCRIBE_DATA",
            options=["property_comps", "properties", "sold_and_rent_history"],
            index=0,
        )
        run_profile = st.button("Run Live ML.DESCRIBE_DATA", width="stretch")

    if run_profile:
        desc_sql = f"""SELECT
  name,
  num_rows,
  num_nulls,
  min,
  max,
  median
FROM ML.DESCRIBE_DATA(
  TABLE `{PROJECT_ID}.{DATASET_ID}.{profile_target}`
)
ORDER BY name"""
        with st.spinner(f"Executing ML.DESCRIBE_DATA on `{profile_target}`..."):
            desc_df, desc_meta, desc_err = run_bq_query(desc_sql, PROJECT_ID, LOCATION)
        if desc_err:
            st.error(f"BigQuery error: {desc_err}")
        else:
            render_telemetry_pill(desc_meta, desc_sql, f"ML.DESCRIBE_DATA ({profile_target})")
            render_html_table(desc_df, mono_cols=["name", "min", "max", "median"])

    st.markdown(
        """
        <div class="section-header">
            <h2>Explore the 3 Core Tables in BigQuery</h2>
            <p>Live preview from <code>properties</code>, <code>sold_and_rent_history</code>, and <code>property_comps</code></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    preview_tbl = st.radio(
        "Table Preview",
        options=["properties", "sold_and_rent_history", "property_comps"],
        horizontal=True,
        label_visibility="collapsed",
    )
    prev_sql = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{preview_tbl}` LIMIT 12"
    prev_df, prev_meta, prev_err = fetch_cached_table(PROJECT_ID, DATASET_ID, LOCATION, prev_sql)
    if prev_err:
        st.error(f"Could not query `{preview_tbl}`: {prev_err}")
    else:
        render_telemetry_pill(prev_meta, prev_sql, f"Preview {preview_tbl}")
        render_html_table(
            prev_df,
            currency_cols=["list_price_usd", "current_monthly_rent_usd", "median_sold_price_usd", "avg_monthly_rent_usd", "sold_price_usd", "monthly_rent_usd"],
            mono_cols=["property_id", "comp_id", "month_date"],
        )


# ===========================================================================
# TAB 2: OPEN KNOWLEDGE FORMAT GROUNDING (Step 3)
# ===========================================================================
with tabs[1]:
    render_talk_track("tab2_okf")

    okf_files = ensure_knowledge_bundle(APP_DIR, PROJECT_ID, DATASET_ID)

    st.markdown(
        """
        <div class="section-header" style="margin-top:0;">
            <h2>Portable Semantic Layer — Open Knowledge Format (Markdown + YAML)</h2>
            <p>Inspect the governed metric and attested SQL files that ground Gemini in Cotality's institutional valuation rules</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("📂 View Open Knowledge Format Semantic Files (`effective_gross_rental_yield.md` & `effective_gross_rental_yield_sql.md`)", expanded=False):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            st.markdown("**`metrics/effective_gross_rental_yield.md`**")
            st.code(okf_files["metrics/effective_gross_rental_yield.md"], language="markdown")
        with f_col2:
            st.markdown("**`computations/effective_gross_rental_yield_sql.md`**")
            st.code(okf_files["computations/effective_gross_rental_yield_sql.md"], language="markdown")

    st.markdown(
        """
        <div class="section-header">
            <h2>Side-by-Side Comparison: 1a. Ungrounded Schema-Only vs. 1b. Open Knowledge Format Grounded</h2>
            <p>See how ungrounded Text-to-SQL suffers from metric drift while grounded <code>AI.GENERATE</code> enforces the 5% vacancy allowance and excludes distressed fixer-uppers</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    analyst_question = st.text_input(
        "Analyst Business Question",
        value="Calculate Effective Gross Rental Yield (%) and average sold price by metro_area from property_comps, ordered highest yield first.",
    )
    run_grounding_cmp = st.button(
        "⚡ Run Live Ungrounded (1a) vs. Grounded (1b) AI.GENERATE Comparison in BigQuery",
        type="primary",
    )

    # Also show the attested vs naive SQL result comparison right away from property_comps
    naive_vs_attested_sql = f"""
WITH naive_ungrounded AS (
  SELECT
    metro_area,
    COUNT(*) AS naive_comp_count,
    ROUND(AVG(100.0 * (12.0 * monthly_rent_usd) / NULLIF(sold_price_usd, 0)), 2) AS ungrounded_naive_yield_pct
  FROM `{PROJECT_ID}.{DATASET_ID}.property_comps`
  GROUP BY metro_area
),
governed_okf AS (
  SELECT
    metro_area,
    COUNT(*) AS move_in_ready_comps,
    ROUND(AVG(sold_price_usd), 0) AS avg_sold_price_usd,
    ROUND(AVG(monthly_rent_usd), 0) AS avg_monthly_rent_usd,
    ROUND(
      100.0 * SAFE_DIVIDE(
        SUM(12.0 * monthly_rent_usd * 0.95),
        SUM(sold_price_usd)
      ),
      2
    ) AS governed_effective_yield_pct
  FROM `{PROJECT_ID}.{DATASET_ID}.property_comps`
  WHERE is_fixer_upper = FALSE
  GROUP BY metro_area
)
SELECT
  g.metro_area,
  n.naive_comp_count AS ungrounded_comps_included,
  g.move_in_ready_comps AS governed_move_in_ready_comps,
  g.avg_sold_price_usd,
  g.avg_monthly_rent_usd,
  n.ungrounded_naive_yield_pct,
  g.governed_effective_yield_pct,
  ROUND(g.governed_effective_yield_pct - n.ungrounded_naive_yield_pct, 2) AS metric_drift_bps_pct
FROM governed_okf g
JOIN naive_ungrounded n USING (metro_area)
ORDER BY g.governed_effective_yield_pct DESC
"""
    cmp_df, cmp_meta, cmp_err = fetch_cached_table(PROJECT_ID, DATASET_ID, LOCATION, naive_vs_attested_sql)
    if not cmp_err and cmp_df is not None:
        ch_col, tbl_col = st.columns([5, 5])
        with ch_col:
            st.markdown(
                """
                <div class="chart-wrap">
                    <div class="chart-title">Metric Drift: Ungrounded Naive Yield vs. Governed Effective Gross Yield (%)</div>
                    <div class="chart-sub">Ungrounded SQL includes fixer-uppers and omits the 5% vacancy allowance, inflating reported yield</div>
                """,
                unsafe_allow_html=True,
            )
            fig_yield = go.Figure()
            fig_yield.add_trace(
                go.Bar(
                    x=cmp_df["metro_area"],
                    y=cmp_df["ungrounded_naive_yield_pct"],
                    name="1a. Ungrounded Naive Yield (%)",
                    marker_color="#f59e0b",
                )
            )
            fig_yield.add_trace(
                go.Bar(
                    x=cmp_df["metro_area"],
                    y=cmp_df["governed_effective_yield_pct"],
                    name="1b. Open Knowledge Format Governed Yield (%)",
                    marker_color="#6366f1",
                )
            )
            fig_yield.update_layout(**get_chart_layout(320), barmode="group", yaxis_title="Rental Yield (%)")
            st.plotly_chart(fig_yield, width="stretch", config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with tbl_col:
            render_telemetry_pill(cmp_meta, naive_vs_attested_sql, "Empirical Yield Comparison Query")
            render_html_table(
                cmp_df,
                currency_cols=["avg_sold_price_usd", "avg_monthly_rent_usd"],
                pct_cols=["ungrounded_naive_yield_pct", "governed_effective_yield_pct", "metric_drift_bps_pct"],
                mono_cols=["metro_area"],
            )

    if run_grounding_cmp:
        ungrounded_sql = f"""
WITH raw_schema AS (
  SELECT STRING_AGG(CONCAT(table_name, '.', column_name, ' (', data_type, ')'), ', ' ORDER BY table_name, ordinal_position) AS schema_ddl
  FROM `{PROJECT_ID}.{DATASET_ID}.INFORMATION_SCHEMA.COLUMNS`
  WHERE table_name IN ('properties', 'sold_and_rent_history', 'property_comps')
)
SELECT
  AI.GENERATE(
    (
      'You are a BigQuery SQL assistant. Using ONLY this raw table schema:\\n',
      schema_ddl,
      '\\n\\nWrite a BigQuery GoogleSQL query for dataset `{PROJECT_ID}.{DATASET_ID}` to answer:\\n',
      @question
    ),
    output_schema => 'sql_query STRING, formula_assumed STRING'
  ).*
FROM raw_schema
"""
        okf_context_str = "\n\n".join(f"### {k}\n{v}" for k, v in okf_files.items())
        grounded_sql = f"""
SELECT
  AI.GENERATE(
    (
      'You are a governed BigQuery SQL agent grounded in the Cotality Open Knowledge Format semantic layer:\\n',
      @okf_context,
      '\\n\\nUsing the exact governance rules and attested formula from the knowledge bundle above, write a BigQuery GoogleSQL query for `{PROJECT_ID}.{DATASET_ID}` to answer:\\n',
      @question
    ),
    output_schema => 'sql_query STRING, governance_rules_applied STRING'
  ).*
"""
        g_col1, g_col2 = st.columns(2)
        with g_col1:
            with st.spinner("Running 1a (Ungrounded AI.GENERATE)..."):
                u_df, u_meta, u_err = run_bq_query(
                    ungrounded_sql,
                    PROJECT_ID,
                    LOCATION,
                    params=[bigquery.ScalarQueryParameter("question", "STRING", analyst_question)],
                )
            st.markdown("#### ⚠️ 1a. Ungrounded (`INFORMATION_SCHEMA` Only)")
            if u_err:
                st.error(u_err)
            elif u_df is not None and not u_df.empty:
                render_telemetry_pill(u_meta, ungrounded_sql, "1a. Ungrounded AI.GENERATE SQL")
                st.markdown(f"**Formula Assumed:** {u_df.iloc[0]['formula_assumed']}")
                st.code(u_df.iloc[0]["sql_query"], language="sql")

        with g_col2:
            with st.spinner("Running 1b (Open Knowledge Format Grounded AI.GENERATE)..."):
                g_df, g_meta, g_err = run_bq_query(
                    grounded_sql,
                    PROJECT_ID,
                    LOCATION,
                    params=[
                        bigquery.ScalarQueryParameter("okf_context", "STRING", okf_context_str),
                        bigquery.ScalarQueryParameter("question", "STRING", analyst_question),
                    ],
                )
            st.markdown("#### ✅ 1b. Open Knowledge Format Grounded (`AI.GENERATE`)")
            if g_err:
                st.error(g_err)
            elif g_df is not None and not g_df.empty:
                render_telemetry_pill(g_meta, grounded_sql, "1b. Grounded AI.GENERATE SQL")
                st.markdown(f"**Governance Rules Applied:** {g_df.iloc[0]['governance_rules_applied']}")
                st.code(g_df.iloc[0]["sql_query"], language="sql")


# ===========================================================================
# TAB 3: MULTIMODAL PHOTO INSPECTION (Step 4 — ObjectRef + AI.GENERATE)
# ===========================================================================
with tabs[2]:
    render_talk_track("tab3_multimodal")

    hdr_c1, hdr_c2 = st.columns([7, 3])
    with hdr_c1:
        st.markdown(
            """
            <div class="section-header" style="margin-top:0;">
                <h2>Multimodal Exterior Photo Inspection (<code>OBJ.MAKE_REF</code> + <code>AI.GENERATE</code>)</h2>
                <p>Inspecting 6 CC0 residential property photos stored in Cloud Storage directly inside BigQuery SQL</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with hdr_c2:
        run_step4_btn = st.button(
            "🔄 Run Live Multimodal Photo Inspection in BigQuery",
            type="primary",
            width="stretch",
        )

    if run_step4_btn:
        ddl4 = get_step4_photo_insights_ddl(PROJECT_ID, DATASET_ID, CONNECTION_ID)
        with st.spinner("Executing OBJ.FETCH_METADATA(OBJ.MAKE_REF(...)) + AI.GENERATE on 6 GCS property photos..."):
            _, m4, err4 = run_bq_query(ddl4, PROJECT_ID, LOCATION)
        if err4:
            st.error(f"Multimodal query failed: {err4}")
        else:
            st.cache_data.clear()
            st.success(f"Materialized `property_photo_insights` in {m4['elapsed_ms']:,} ms!")

    photo_query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.property_photo_insights` ORDER BY property_id"
    photo_df, photo_meta, photo_err = fetch_cached_table(PROJECT_ID, DATASET_ID, LOCATION, photo_query)

    if photo_err or photo_df is None or photo_df.empty:
        st.info(
            "Table `property_photo_insights` is not yet materialized or returned an error. "
            "Click **🔄 Run Live Multimodal Photo Inspection in BigQuery** above to generate it now."
        )
        with st.expander("🔎 View Step 4 Multimodal GoogleSQL DDL", expanded=True):
            st.code(get_step4_photo_insights_ddl(PROJECT_ID, DATASET_ID, CONNECTION_ID), language="sql")
    else:
        render_telemetry_pill(photo_meta, get_step4_photo_insights_ddl(PROJECT_ID, DATASET_ID, CONNECTION_ID), "Step 4: Multimodal Photo Inspection DDL")

        # Render 3x2 Visual Gallery of the 6 Featured Properties
        rows_list = photo_df.to_dict("records")
        for idx in range(0, len(rows_list), 3):
            cols = st.columns(3)
            for j, rec in enumerate(rows_list[idx : idx + 3]):
                with cols[j]:
                    pid = rec.get("property_id", "")
                    cond = str(rec.get("exterior_condition", ""))
                    cond_variant = (
                        "emerald"
                        if any(w in cond.lower() for w in ("excellent", "good", "move-in", "ready"))
                        else ("rose" if any(w in cond.lower() for w in ("rehab", "poor", "distressed")) else "amber")
                    )
                    score = rec.get("curb_appeal_score", 0)
                    img_meta = FEATURED_PROPERTY_PHOTOS.get(pid, {})
                    local_img = APP_DIR / "property_images" / img_meta.get("file", "")
                    if local_img.exists():
                        st.image(str(local_img), width="stretch")

                    feats = rec.get("visible_features", [])
                    if hasattr(feats, "tolist"):
                        feats = feats.tolist()
                    feat_badges = " ".join(format_badge(str(f), "indigo") for f in (feats or [])[:4])

                    st.markdown(
                        f"""
                        <div class="val-card">
                            <div class="val-card-header">
                                <span class="val-card-title">{html.escape(pid)} · {html.escape(str(rec.get("metro_area", "")))}</span>
                                {format_badge(cond, cond_variant)}
                            </div>
                            <div style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:0.4rem;">{html.escape(str(rec.get("address", "")))}</div>
                            <div class="val-kpi-grid">
                                <div class="val-kpi-item">
                                    <div class="k">Architectural Style</div>
                                    <div class="v">{html.escape(str(rec.get("architectural_style", "—")))}</div>
                                </div>
                                <div class="val-kpi-item">
                                    <div class="k">Curb Appeal Score</div>
                                    <div class="v">{score} / 10</div>
                                </div>
                            </div>
                            <div style="margin-bottom:0.55rem;">{feat_badges}</div>
                            <div class="val-brief">{html.escape(str(rec.get("photo_summary", "")))}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        render_html_table(
            photo_df,
            currency_cols=["list_price_usd"],
            mono_cols=["property_id", "curb_appeal_score"],
        )


# ===========================================================================
# TAB 4: LISTING SCREENING & BUYER SEGMENTATION (Step 5 — AI.IF & AI.CLASSIFY)
# ===========================================================================
with tabs[3]:
    render_talk_track("tab4_screening")

    sc_left, sc_right = st.columns([7, 3])
    with sc_left:
        st.markdown(
            """
            <div class="section-header" style="margin-top:0;">
                <h2>Semantic Listing Screening (<code>AI.IF</code>) &amp; Buyer Segmentation (<code>AI.CLASSIFY</code>)</h2>
                <p>Zero-shot boolean screening and multi-class categorization over unstructured MLS listing remarks</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with sc_right:
        run_step5_btn = st.button(
            "🔄 Run AI.IF & AI.CLASSIFY Batch in BigQuery",
            type="primary",
            width="stretch",
        )

    if run_step5_btn:
        ddl5 = get_step5_screening_ddl(PROJECT_ID, DATASET_ID, CONNECTION_ID, 25)
        with st.spinner("Running AI.IF and AI.CLASSIFY on 25 listings in BigQuery..."):
            _, m5, err5 = run_bq_query(ddl5, PROJECT_ID, LOCATION)
        if err5:
            st.error(f"Step 5 query failed: {err5}")
        else:
            st.cache_data.clear()
            st.success(f"Materialized `properties_enriched` in {m5['elapsed_ms']:,} ms!")

    enr_sql = f"""
    SELECT
      property_id,
      address,
      metro_area,
      property_type,
      sqft,
      list_price_usd,
      is_move_in_ready,
      buyer_segment,
      listing_notes
    FROM `{PROJECT_ID}.{DATASET_ID}.properties_enriched`
    ORDER BY property_id
    """
    enr_df, enr_meta, enr_err = fetch_cached_table(PROJECT_ID, DATASET_ID, LOCATION, enr_sql)

    if enr_err or enr_df is None or enr_df.empty:
        st.info(
            "Table `properties_enriched` is not yet materialized. "
            "Click **🔄 Run AI.IF & AI.CLASSIFY Batch in BigQuery** above to generate it now."
        )
    else:
        render_telemetry_pill(enr_meta, get_step5_screening_ddl(PROJECT_ID, DATASET_ID, CONNECTION_ID, 25), "Step 5: AI.IF & AI.CLASSIFY Enriched Listings")

        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            seg_counts = enr_df["buyer_segment"].value_counts().reset_index()
            seg_counts.columns = ["buyer_segment", "count"]
            st.markdown(
                """
                <div class="chart-wrap">
                    <div class="chart-title">Buyer Segment Distribution (<code>AI.CLASSIFY</code>)</div>
                    <div class="chart-sub">Zero-shot categorization across 4 residential buyer personas</div>
                """,
                unsafe_allow_html=True,
            )
            fig_seg = go.Figure(
                go.Pie(
                    labels=seg_counts["buyer_segment"],
                    values=seg_counts["count"],
                    hole=0.58,
                    marker=dict(colors=["#6366f1", "#06b6d4", "#10b981", "#f43f5e"]),
                )
            )
            fig_seg.update_layout(**get_chart_layout(300))
            st.plotly_chart(fig_seg, width="stretch", config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with c_chart2:
            mir_metro = (
                enr_df.groupby(["metro_area", "is_move_in_ready"])
                .size()
                .unstack(fill_value=0)
                .reset_index()
            )
            st.markdown(
                """
                <div class="chart-wrap">
                    <div class="chart-title">Move-In-Ready vs. Fixer-Upper Screening by Metro (<code>AI.IF</code>)</div>
                    <div class="chart-sub">Boolean output chains directly into Step 7 TabFM as <code>NOT is_move_in_ready AS is_fixer_upper</code></div>
                """,
                unsafe_allow_html=True,
            )
            fig_mir = go.Figure()
            if True in mir_metro.columns:
                fig_mir.add_trace(
                    go.Bar(
                        x=mir_metro["metro_area"],
                        y=mir_metro[True],
                        name="Move-In Ready (TRUE)",
                        marker_color="#10b981",
                    )
                )
            if False in mir_metro.columns:
                fig_mir.add_trace(
                    go.Bar(
                        x=mir_metro["metro_area"],
                        y=mir_metro[False],
                        name="Needs Major Rehab (FALSE)",
                        marker_color="#f43f5e",
                    )
                )
            fig_mir.update_layout(**get_chart_layout(300), barmode="stack", yaxis_title="Listing Count")
            st.plotly_chart(fig_mir, width="stretch", config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        render_html_table(
            enr_df,
            currency_cols=["list_price_usd"],
            mono_cols=["property_id"],
            badge_cols={
                "is_move_in_ready": {"True": "emerald", "False": "rose"},
                "buyer_segment": {
                    "Turnkey Family Home": "emerald",
                    "Luxury Residence": "indigo",
                    "Starter / Cozy Home": "cyan",
                    "Fixer-Upper / Value-Add": "amber",
                },
            },
            max_rows=15,
        )

    # Interactive Ad-Hoc Listing Screener
    st.markdown(
        """
        <div class="section-header">
            <h2>Interactive Live Listing Screener (Test <code>AI.IF</code> + <code>AI.CLASSIFY</code> on Custom Text)</h2>
            <p>Enter any MLS listing description below (including tricky negations like "needs no roof work") to run live in BigQuery</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    custom_desc = st.text_area(
        "Custom Listing Remarks",
        value="Charming 1920s bungalow where all major structural work is already completed! Brand-new standing seam metal roof installed in 2024, needs no foundation or HVAC repairs, move right in.",
        height=80,
    )
    if st.button("🧪 Screen Custom Listing Live in BigQuery"):
        adhoc_sql = """
SELECT
  @listing_text AS listing_notes,
  AI.IF(
    (
      'Is this property move-in ready without needing major structural, roof, foundation, or full-gut renovations? ',
      'Listing Notes: ', @listing_text
    ),
    examples => [
      STRUCT(
        'Listing Notes: Needs new roof and HVAC repair. Sold as-is cash only.' AS input,
        FALSE AS output
      ),
      STRUCT(
        'Listing Notes: Roof and foundation already repaired in 2024 with transferable warranty; move-in ready!' AS input,
        TRUE AS output
      )
    ]
  ) AS is_move_in_ready,
  AI.CLASSIFY(
    @listing_text,
    categories => [
      ('Turnkey Family Home', 'Move-in ready single-family or townhome suitable for families'),
      ('Luxury Residence', 'High-end luxury home or penthouse with premium finishes or views'),
      ('Fixer-Upper / Value-Add', 'Property requiring renovation, roof/HVAC repair, or sold as-is'),
      ('Starter / Cozy Home', 'Compact condo, townhome, or entry-level residence')
    ]
  ) AS buyer_segment
"""
        with st.spinner("Executing AI.IF and AI.CLASSIFY in BigQuery..."):
            ad_df, ad_meta, ad_err = run_bq_query(
                adhoc_sql,
                PROJECT_ID,
                LOCATION,
                params=[bigquery.ScalarQueryParameter("listing_text", "STRING", custom_desc)],
            )
        if ad_err:
            st.error(ad_err)
        else:
            render_telemetry_pill(ad_meta, adhoc_sql, "Ad-Hoc AI.IF & AI.CLASSIFY Query")
            render_html_table(
                ad_df,
                badge_cols={
                    "is_move_in_ready": {"True": "emerald", "False": "rose"},
                    "buyer_segment": {
                        "Turnkey Family Home": "emerald",
                        "Luxury Residence": "indigo",
                        "Starter / Cozy Home": "cyan",
                        "Fixer-Upper / Value-Add": "amber",
                    },
                },
            )


# ===========================================================================
# TAB 5: 12-MONTH METRO PRICE & RENT FORECASTING (Step 6 — TimesFM)
# ===========================================================================
with tabs[4]:
    render_talk_track("tab5_forecast")

    fc_c1, fc_c2, fc_c3 = st.columns([5, 2.5, 2.5])
    with fc_c1:
        st.markdown(
            """
            <div class="section-header" style="margin-top:0;">
                <h2>Multi-Metro Price &amp; Rent Forecasting (<code>TimesFM</code>)</h2>
                <p>Zero-training 12-month trajectory across all 5 metro markets with 95% confidence bounds</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with fc_c2:
        run_bt_btn = st.button("📊 Run 2025 Holdout Backtest (AI.EVALUATE)", width="stretch")
    with fc_c3:
        run_fc_btn = st.button("🔄 Refresh 12M Forecast Table (AI.FORECAST)", type="primary", width="stretch")

    if run_bt_btn:
        bt_sql = get_step6_backtest_sql(PROJECT_ID, DATASET_ID)
        with st.spinner("Evaluating TimesFM holdout accuracy (2020–2024 train vs 2025 actuals)..."):
            bt_df, bt_meta, bt_err = run_bq_query(bt_sql, PROJECT_ID, LOCATION)
        if bt_err:
            st.error(bt_err)
        else:
            render_telemetry_pill(bt_meta, bt_sql, "Step 6a: TimesFM Holdout Backtest (AI.EVALUATE)")
            render_html_table(
                bt_df,
                currency_cols=["mae_usd"],
                pct_cols=["mape_pct"],
                mono_cols=["metro_area", "metric_name", "eval_months"],
            )

    if run_fc_btn:
        ddl6 = get_step6_forecast_ddl(PROJECT_ID, DATASET_ID)
        with st.spinner("Running dual AI.FORECAST across 5 metros for Sold Price and Monthly Rent..."):
            _, m6, err6 = run_bq_query(ddl6, PROJECT_ID, LOCATION)
        if err6:
            st.error(err6)
        else:
            st.cache_data.clear()
            st.success(f"Materialized `metro_12m_forecasts` in {m6['elapsed_ms']:,} ms!")

    fc_query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.metro_12m_forecasts` ORDER BY metro_area, month_date"
    fc_df, fc_meta, fc_err = fetch_cached_table(PROJECT_ID, DATASET_ID, LOCATION, fc_query)

    if fc_err or fc_df is None or fc_df.empty:
        st.info(
            "Table `metro_12m_forecasts` is not yet materialized. "
            "Click **🔄 Refresh 12M Forecast Table (AI.FORECAST)** above to run `TimesFM` now."
        )
    else:
        render_telemetry_pill(fc_meta, get_step6_forecast_ddl(PROJECT_ID, DATASET_ID), "Step 6b: Dual AI.FORECAST (TimesFM) DDL")

        metros_avail = sorted(fc_df["metro_area"].unique().tolist())
        sel_metro = st.selectbox("Select Metro Market to Inspect", options=metros_avail, index=0)
        m_sub = fc_df[fc_df["metro_area"] == sel_metro].sort_values("month_date")
        hist_sub = m_sub[m_sub["hist_sold_price_usd"].notna()]
        fut_sub = m_sub[m_sub["fc_sold_price_usd"].notna()]

        p_col, r_col = st.columns(2)
        with p_col:
            st.markdown(
                f"""
                <div class="chart-wrap">
                    <div class="chart-title">{html.escape(sel_metro)} — Median Sold Price Forecast (USD)</div>
                    <div class="chart-sub">72 months historical (2020–2025) + 12-month TimesFM forecast with 95% confidence ribbon</div>
                """,
                unsafe_allow_html=True,
            )
            fig_p = go.Figure()
            fig_p.add_trace(
                go.Scatter(
                    x=hist_sub["month_date"],
                    y=hist_sub["hist_sold_price_usd"],
                    mode="lines",
                    name="Historical Sold Price",
                    line=dict(color="#6366f1", width=2.4),
                )
            )
            if not fut_sub.empty:
                fig_p.add_trace(
                    go.Scatter(
                        x=pd.concat([fut_sub["month_date"], fut_sub["month_date"][::-1]]),
                        y=pd.concat([fut_sub["sold_upper_usd"], fut_sub["sold_lower_usd"][::-1]]),
                        fill="toself",
                        fillcolor="rgba(16, 185, 129, 0.18)",
                        line=dict(color="rgba(255,255,255,0)"),
                        hoverinfo="skip",
                        name="95% Confidence Interval",
                    )
                )
                fig_p.add_trace(
                    go.Scatter(
                        x=fut_sub["month_date"],
                        y=fut_sub["fc_sold_price_usd"],
                        mode="lines+markers",
                        name="TimesFM 12M Forecast",
                        line=dict(color="#10b981", width=2.6, dash="dash"),
                    )
                )
            fig_p.update_layout(**get_chart_layout(340), yaxis_title="Median Sold Price ($)")
            st.plotly_chart(fig_p, width="stretch", config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with r_col:
            st.markdown(
                f"""
                <div class="chart-wrap">
                    <div class="chart-title">{html.escape(sel_metro)} — Average Monthly Rent Forecast (USD)</div>
                    <div class="chart-sub">72 months historical (2020–2025) + 12-month TimesFM forecast with 95% confidence ribbon</div>
                """,
                unsafe_allow_html=True,
            )
            fig_r = go.Figure()
            fig_r.add_trace(
                go.Scatter(
                    x=hist_sub["month_date"],
                    y=hist_sub["hist_rent_usd"],
                    mode="lines",
                    name="Historical Monthly Rent",
                    line=dict(color="#06b6d4", width=2.4),
                )
            )
            if not fut_sub.empty:
                fig_r.add_trace(
                    go.Scatter(
                        x=pd.concat([fut_sub["month_date"], fut_sub["month_date"][::-1]]),
                        y=pd.concat([fut_sub["rent_upper_usd"], fut_sub["rent_lower_usd"][::-1]]),
                        fill="toself",
                        fillcolor="rgba(245, 158, 11, 0.18)",
                        line=dict(color="rgba(255,255,255,0)"),
                        hoverinfo="skip",
                        name="95% Confidence Interval",
                    )
                )
                fig_r.add_trace(
                    go.Scatter(
                        x=fut_sub["month_date"],
                        y=fut_sub["fc_rent_usd"],
                        mode="lines+markers",
                        name="TimesFM 12M Forecast",
                        line=dict(color="#f59e0b", width=2.6, dash="dash"),
                    )
                )
            fig_r.update_layout(**get_chart_layout(340), yaxis_title="Avg Monthly Rent ($)")
            st.plotly_chart(fig_r, width="stretch", config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Summary table across all 5 metros (Dec 2025 vs Dec 2026)
        summary_fc_sql = f"""
        WITH dec_2025 AS (
          SELECT metro_area, median_sold_price_usd AS sold_2025, avg_monthly_rent_usd AS rent_2025
          FROM `{PROJECT_ID}.{DATASET_ID}.sold_and_rent_history`
          WHERE month_date = '2025-12-01'
        ),
        dec_2026 AS (
          SELECT metro_area, fc_sold_price_usd AS sold_2026, fc_rent_usd AS rent_2026
          FROM `{PROJECT_ID}.{DATASET_ID}.metro_12m_forecasts`
          WHERE month_date = '2026-12-01'
        )
        SELECT
          a.metro_area,
          a.sold_2025 AS dec_2025_price_usd,
          b.sold_2026 AS dec_2026_forecast_price_usd,
          ROUND(100.0 * (b.sold_2026 - a.sold_2025) / a.sold_2025, 2) AS forecast_12m_price_appreciation_pct,
          a.rent_2025 AS dec_2025_rent_usd,
          b.rent_2026 AS dec_2026_forecast_rent_usd,
          ROUND(100.0 * (b.rent_2026 - a.rent_2025) / a.rent_2025, 2) AS forecast_12m_rent_growth_pct
        FROM dec_2025 a
        JOIN dec_2026 b USING (metro_area)
        ORDER BY forecast_12m_price_appreciation_pct DESC
        """
        s_df, _, s_err = fetch_cached_table(PROJECT_ID, DATASET_ID, LOCATION, summary_fc_sql)
        if not s_err and s_df is not None:
            render_html_table(
                s_df,
                currency_cols=["dec_2025_price_usd", "dec_2026_forecast_price_usd", "dec_2025_rent_usd", "dec_2026_forecast_rent_usd"],
                pct_cols=["forecast_12m_price_appreciation_pct", "forecast_12m_rent_growth_pct"],
                mono_cols=["metro_area"],
            )


# ===========================================================================
# TAB 6: ZERO-SHOT COMPARABLE PROPERTY VALUATION (Step 7 — TabFM)
# ===========================================================================
with tabs[5]:
    render_talk_track("tab6_tabfm")

    tb_c1, tb_c2, tb_c3 = st.columns([5, 2.5, 2.5])
    with tb_c1:
        st.markdown(
            """
            <div class="section-header" style="margin-top:0;">
                <h2>Zero-Shot Comparable Valuation (<code>TabFM</code> — <code>AI.PREDICT</code> &amp; <code>AI.EVALUATE</code>)</h2>
                <p>In-context tabular regression conditioned on 190 historical comps, chaining Step 5 <code>AI.IF</code> (<code>NOT is_move_in_ready AS is_fixer_upper</code>)</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with tb_c2:
        run_tab_eval_btn = st.button("📏 Run Validation Split AI.EVALUATE", width="stretch")
    with tb_c3:
        run_tab_pred_btn = st.button("🔄 Run TabFM AI.PREDICT Valuations", type="primary", width="stretch")

    if run_tab_eval_btn:
        ev7_sql = get_step7_eval_sql(PROJECT_ID, DATASET_ID)
        with st.spinner("Running TabFM AI.EVALUATE on 50 VALIDATION comps..."):
            ev7_df, ev7_meta, ev7_err = run_bq_query(ev7_sql, PROJECT_ID, LOCATION)
        if ev7_err:
            st.error(ev7_err)
        else:
            render_telemetry_pill(ev7_meta, ev7_sql, "Step 7a: TabFM Validation Accuracy (AI.EVALUATE)")
            render_html_table(ev7_df, currency_cols=["mae_usd"], mono_cols=["target_column", "mse_usd", "r2_score"])

    if run_tab_pred_btn:
        ddl7 = get_step7_predict_ddl(PROJECT_ID, DATASET_ID)
        with st.spinner("Running dual TabFM AI.PREDICT for Sold Price and Monthly Rent..."):
            _, m7, err7 = run_bq_query(ddl7, PROJECT_ID, LOCATION)
        if err7:
            st.error(err7)
        else:
            st.cache_data.clear()
            st.success(f"Materialized `property_comp_valuations` in {m7['elapsed_ms']:,} ms!")

    val_sql = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.property_comp_valuations` ORDER BY property_id"
    val_df, val_meta, val_err = fetch_cached_table(PROJECT_ID, DATASET_ID, LOCATION, val_sql)

    if val_err or val_df is None or val_df.empty:
        st.info(
            "Table `property_comp_valuations` is not yet materialized. "
            "Click **🔄 Run TabFM AI.PREDICT Valuations** above to generate it now."
        )
    else:
        render_telemetry_pill(val_meta, get_step7_predict_ddl(PROJECT_ID, DATASET_ID), "Step 7b: Dual AI.PREDICT (TabFM) DDL")

        sc_col1, sc_col2 = st.columns([5.2, 4.8])
        with sc_col1:
            st.markdown(
                """
                <div class="chart-wrap">
                    <div class="chart-title">Asking List Price vs. TabFM Fair-Market Valuation (USD)</div>
                    <div class="chart-sub">Points above the diagonal 1:1 parity line indicate properties priced below TabFM fair value (positive equity spread)</div>
                """,
                unsafe_allow_html=True,
            )
            fig_sc = go.Figure()
            min_v = float(min(val_df["list_price_usd"].min(), val_df["comp_predicted_sold_usd"].min())) * 0.9
            max_v = float(max(val_df["list_price_usd"].max(), val_df["comp_predicted_sold_usd"].max())) * 1.05
            fig_sc.add_trace(
                go.Scatter(
                    x=[min_v, max_v],
                    y=[min_v, max_v],
                    mode="lines",
                    name="1:1 Parity Line",
                    line=dict(color="#71717a", dash="dot", width=1.5),
                )
            )
            for seg, grp in val_df.groupby("buyer_segment"):
                fig_sc.add_trace(
                    go.Scatter(
                        x=grp["list_price_usd"],
                        y=grp["comp_predicted_sold_usd"],
                        mode="markers",
                        name=str(seg),
                        text=grp["property_id"] + " (" + grp["metro_area"] + ")",
                        hovertemplate="<b>%{text}</b><br>Asking: $%{x:,.0f}<br>TabFM Fair Value: $%{y:,.0f}<extra></extra>",
                        marker=dict(size=11, line=dict(width=1, color="#18181b")),
                    )
                )
            fig_sc.update_layout(
                **get_chart_layout(340),
                xaxis_title="Asking List Price ($)",
                yaxis_title="TabFM Predicted Sold Price ($)",
            )
            st.plotly_chart(fig_sc, width="stretch", config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with sc_col2:
            st.markdown(
                """
                <div class="chart-wrap">
                    <div class="chart-title">Estimated Instant Equity Spread by Property (<code>TabFM - Asking</code>)</div>
                    <div class="chart-sub">Featured properties PROP-101 to PROP-106 highlighted at top</div>
                """,
                unsafe_allow_html=True,
            )
            top_sub = val_df.head(10).sort_values("estimated_equity_spread_usd", ascending=True)
            bar_colors = ["#10b981" if x >= 0 else "#f43f5e" for x in top_sub["estimated_equity_spread_usd"]]
            fig_sp = go.Figure(
                go.Bar(
                    x=top_sub["estimated_equity_spread_usd"],
                    y=top_sub["property_id"] + " · " + top_sub["metro_area"],
                    orientation="h",
                    marker_color=bar_colors,
                )
            )
            fig_sp.update_layout(**get_chart_layout(340), xaxis_title="Equity Spread vs. Asking Price ($)")
            st.plotly_chart(fig_sp, width="stretch", config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        render_html_table(
            val_df,
            currency_cols=["list_price_usd", "current_monthly_rent_usd", "comp_predicted_sold_usd", "estimated_equity_spread_usd", "comp_predicted_rent_usd"],
            pct_cols=["okf_effective_yield_pct"],
            mono_cols=["property_id", "sqft"],
            badge_cols={
                "is_move_in_ready": {"True": "emerald", "False": "rose"},
                "buyer_segment": {
                    "Turnkey Family Home": "emerald",
                    "Luxury Residence": "indigo",
                    "Starter / Cozy Home": "cyan",
                    "Fixer-Upper / Value-Add": "amber",
                },
            },
            max_rows=25,
        )


# ===========================================================================
# TAB 7: UNIFIED PROPERTY VALUATION CARDS (Step 8 — The Grand Finale)
# ===========================================================================
with tabs[6]:
    render_talk_track("tab7_unified")

    u_c1, u_c2 = st.columns([7, 3])
    with u_c1:
        st.markdown(
            """
            <div class="section-header" style="margin-top:0;">
                <h2>Unified Executive Property Valuation Cards (<code>PROP-101</code> to <code>PROP-106</code>)</h2>
                <p>Single-SQL synthesis joining <code>TabFM</code> comp valuations + <code>TimesFM</code> 12M metro outlook + <code>ObjectRef</code> photo insights + <code>AI.GENERATE</code> investment brief</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with u_c2:
        regen_cards_btn = st.button("✨ Generate / Refresh Live Valuation Cards", type="primary", width="stretch")

    step8_sql = get_step8_unified_cards_sql(PROJECT_ID, DATASET_ID, CONNECTION_ID)
    if regen_cards_btn:
        st.cache_data.clear()

    with st.spinner("Executing unified multi-model SQL join & AI.GENERATE brief across PROP-101 to PROP-106..."):
        cards_df, cards_meta, cards_err = fetch_cached_table(PROJECT_ID, DATASET_ID, LOCATION, step8_sql)

    if cards_err or cards_df is None or cards_df.empty:
        st.info(
            "Ensure Steps 4 (`property_photo_insights`), 5 (`properties_enriched`), 6 (`metro_12m_forecasts`), "
            "and 7 (`property_comp_valuations`) have been materialized, then click **✨ Generate / Refresh Live Valuation Cards**."
        )
        if cards_err:
            st.caption(f"Query details: {cards_err}")
        with st.expander("🔎 View Step 8 Unified Valuation SQL", expanded=True):
            st.code(step8_sql, language="sql")
    else:
        render_telemetry_pill(cards_meta, step8_sql, "Step 8: Unified Multi-Model Valuation SQL")

        card_records = cards_df.to_dict("records")
        for idx in range(0, len(card_records), 2):
            row_cols = st.columns(2)
            for j, rec in enumerate(card_records[idx : idx + 2]):
                with row_cols[j]:
                    pid = str(rec.get("property_id", ""))
                    rec_tag = str(rec.get("recommendation_tag", "HOLD")).upper()
                    tag_variant = "emerald" if "BUY" in rec_tag else ("rose" if "PASS" in rec_tag else "amber")

                    img_info = FEATURED_PROPERTY_PHOTOS.get(pid, {})
                    local_img = APP_DIR / "property_images" / img_info.get("file", "")
                    if local_img.exists():
                        st.image(str(local_img), width="stretch")

                    ask_p = float(rec.get("list_price_usd", 0) or 0)
                    pred_p = float(rec.get("comp_predicted_sold_usd", 0) or 0)
                    spread = float(rec.get("estimated_equity_spread_usd", 0) or 0)
                    spread_str = f"+${spread:,.0f}" if spread >= 0 else f"-${abs(spread):,.0f}"
                    rent_p = float(rec.get("comp_predicted_rent_usd", 0) or 0)
                    yld_p = float(rec.get("okf_effective_yield_pct", 0) or 0)
                    m_growth = float(rec.get("metro_12m_price_growth_pct", 0) or 0)
                    r_growth = float(rec.get("metro_12m_rent_growth_pct", 0) or 0)

                    st.markdown(
                        f"""
                        <div class="val-card">
                            <div class="val-card-header">
                                <span class="val-card-title">{html.escape(pid)} · {html.escape(str(rec.get("metro_area", "")))}</span>
                                <div>
                                    {format_badge(str(rec.get("buyer_segment", "")), "indigo")}
                                    {format_badge(rec_tag, tag_variant)}
                                </div>
                            </div>
                            <div style="font-size:0.78rem;color:var(--text-secondary);margin-bottom:0.4rem;">{html.escape(str(rec.get("address", "")))}</div>
                            <div class="val-kpi-grid">
                                <div class="val-kpi-item">
                                    <div class="k">Asking vs. TabFM Fair Value</div>
                                    <div class="v">${ask_p:,.0f} → ${pred_p:,.0f} ({spread_str})</div>
                                </div>
                                <div class="val-kpi-item">
                                    <div class="k">TabFM Rent &amp; OKF Effective Yield</div>
                                    <div class="v">${rent_p:,.0f}/mo ({yld_p:.2f}%)</div>
                                </div>
                                <div class="val-kpi-item">
                                    <div class="k">TimesFM 12M Metro Outlook</div>
                                    <div class="v">{m_growth:+.2f}% Price / {r_growth:+.2f}% Rent</div>
                                </div>
                                <div class="val-kpi-item">
                                    <div class="k">Photo Condition &amp; Curb Appeal</div>
                                    <div class="v">{html.escape(str(rec.get("exterior_condition", "")))} ({rec.get("curb_appeal_score", "—")}/10)</div>
                                </div>
                            </div>
                            <div class="val-brief">
                                <strong>🤖 Gemini Executive Valuation Brief:</strong> {html.escape(str(rec.get("analyst_valuation_brief", "")))}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


# ===========================================================================
# TAB 8: ASK YOUR DATA — NATURAL LANGUAGE BIGQUERY CHAT (Grounded in OKF)
# ===========================================================================
with tabs[7]:
    render_talk_track("tab8_chat")

    st.markdown(
        """
        <div class="section-header" style="margin-top:0;">
            <h2>💬 Ask Your Data — Open Knowledge Format Grounded SQL Assistant</h2>
            <p>Ask natural-language questions across <code>properties</code>, <code>sold_and_rent_history</code>, <code>property_comps</code>, <code>property_photo_insights</code>, <code>metro_12m_forecasts</code>, and <code>property_comp_valuations</code></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sample_prompts = [
        "Which move-in-ready properties are priced below their TabFM fair value and what is their predicted gross rental yield?",
        "Compare Effective Gross Rental Yield (%) and 12-month forecasted metro price appreciation across all 5 metros.",
        "Show the 6 featured properties with their photo curb appeal score, exterior condition, and TabFM valuation spread.",
    ]
    sp_cols = st.columns(3)
    selected_preset: Optional[str] = None
    for idx, sp_text in enumerate(sample_prompts):
        with sp_cols[idx]:
            if st.button(f"💡 {sp_text[:62]}...", key=f"preset_{idx}", width="stretch"):
                selected_preset = sp_text

    user_q = st.chat_input("Ask a question about Cotality properties, metro forecasts, or rental yields...")
    active_prompt = selected_preset or user_q

    if active_prompt:
        st.session_state.chat_history.append({"role": "user", "content": active_prompt})

        okf_files = ensure_knowledge_bundle(APP_DIR, PROJECT_ID, DATASET_ID)
        okf_bundle_text = "\n\n".join(f"### {k}\n{v}" for k, v in okf_files.items())

        nl2sql_query = f"""
SELECT
  AI.GENERATE(
    (
      'You are a Principal Real Estate Analytics Engineer for Cotality. ',
      'You have access to BigQuery dataset `{PROJECT_ID}.{DATASET_ID}` containing these tables:\\n',
      '1. `{PROJECT_ID}.{DATASET_ID}.properties` (property_id, address, metro_area, neighborhood, property_type, sqft, bedrooms, bathrooms, year_built, list_price_usd, current_monthly_rent_usd, gcs_image_uri, listing_notes)\\n',
      '2. `{PROJECT_ID}.{DATASET_ID}.sold_and_rent_history` (metro_area, month_date, median_sold_price_usd, avg_monthly_rent_usd, inventory_months, mortgage_rate_pct)\\n',
      '3. `{PROJECT_ID}.{DATASET_ID}.property_comps` (comp_id, metro_area, property_type, sqft, bedrooms, bathrooms, year_built, is_fixer_upper, sold_price_usd, monthly_rent_usd, split_set)\\n',
      '4. `{PROJECT_ID}.{DATASET_ID}.property_photo_insights` (property_id, address, metro_area, list_price_usd, gcs_image_uri, architectural_style, exterior_condition, curb_appeal_score, visible_features, photo_summary)\\n',
      '5. `{PROJECT_ID}.{DATASET_ID}.properties_enriched` (same as properties + is_move_in_ready BOOL, buyer_segment STRING)\\n',
      '6. `{PROJECT_ID}.{DATASET_ID}.metro_12m_forecasts` (metro_area, month_date, hist_sold_price_usd, fc_sold_price_usd, sold_lower_usd, sold_upper_usd, hist_rent_usd, fc_rent_usd, rent_lower_usd, rent_upper_usd)\\n',
      '7. `{PROJECT_ID}.{DATASET_ID}.property_comp_valuations` (property_id, address, metro_area, property_type, sqft, bedrooms, bathrooms, year_built, is_move_in_ready, buyer_segment, list_price_usd, current_monthly_rent_usd, comp_predicted_sold_usd, comp_predicted_rent_usd, estimated_equity_spread_usd, okf_effective_yield_pct)\\n\\n',
      'Always obey the Open Knowledge Format semantic governance rules below:\\n',
      @okf_context,
      '\\n\\nReturn a valid, executable BigQuery GoogleSQL SELECT query (no markdown backticks) in `sql_query` and a concise explanation in `analyst_explanation` for the question:\\n',
      @user_question
    ),
    output_schema => 'sql_query STRING, analyst_explanation STRING'
  ).*
"""
        with st.spinner("Generating Open Knowledge Format-grounded SQL and querying BigQuery..."):
            gen_df, gen_meta, gen_err = run_bq_query(
                nl2sql_query,
                PROJECT_ID,
                LOCATION,
                params=[
                    bigquery.ScalarQueryParameter("okf_context", "STRING", okf_bundle_text),
                    bigquery.ScalarQueryParameter("user_question", "STRING", active_prompt),
                ],
            )
            if gen_err or gen_df is None or gen_df.empty:
                st.session_state.chat_history.append(
                    {"role": "assistant", "error": gen_err or "No SQL generated."}
                )
            else:
                raw_sql = str(gen_df.iloc[0]["sql_query"]).strip()
                cleaned_sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", raw_sql, flags=re.IGNORECASE).strip()
                explanation = str(gen_df.iloc[0]["analyst_explanation"])
                res_df, res_meta, res_err = run_bq_query(cleaned_sql, PROJECT_ID, LOCATION)
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "explanation": explanation,
                        "sql": cleaned_sql,
                        "df": res_df,
                        "telemetry": res_meta,
                        "error": res_err,
                    }
                )

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            if msg["role"] == "user":
                st.markdown(msg["content"])
            else:
                if msg.get("error") and msg.get("df") is None:
                    st.error(f"Query execution error: {msg['error']}")
                    if msg.get("sql"):
                        st.code(msg["sql"], language="sql")
                else:
                    st.markdown(msg.get("explanation", ""))
                    if msg.get("telemetry") and msg.get("sql"):
                        render_telemetry_pill(msg["telemetry"], msg["sql"], "Generated & Executed BigQuery SQL")
                    if msg.get("df") is not None:
                        render_html_table(msg["df"], max_rows=25)
