from __future__ import annotations

import os
from typing import Any, Dict

import requests
import streamlit as st


BACKEND_URL = os.getenv("RAG_BACKEND_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="Enterprise Incident RCA Assistant",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
    :root {
        --bg: #08111f;
        --panel: #0f1b2d;
        --panel-2: #14233a;
        --border: rgba(148, 163, 184, 0.18);
        --text: #e5eefc;
        --muted: #9eb2cf;
        --accent: #5eead4;
        --accent-2: #fbbf24;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(94, 234, 212, 0.14), transparent 28%),
            radial-gradient(circle at top right, rgba(251, 191, 36, 0.12), transparent 24%),
            linear-gradient(180deg, #07101d 0%, #0b1526 100%);
        color: var(--text);
    }

    .hero {
        padding: 1.4rem 1.6rem;
        border: 1px solid var(--border);
        border-radius: 22px;
        background: linear-gradient(145deg, rgba(15, 27, 45, 0.95), rgba(20, 35, 58, 0.82));
        box-shadow: 0 22px 60px rgba(0, 0, 0, 0.28);
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2rem;
        letter-spacing: -0.03em;
        color: var(--text);
    }

    .hero p {
        margin: 0.35rem 0 0;
        color: var(--muted);
        font-size: 0.98rem;
    }

    .card {
        background: rgba(15, 27, 45, 0.86);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1rem 1rem 0.85rem;
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.18);
        margin-bottom: 0.9rem;
    }

    .card h3, .card h4 {
        margin-top: 0;
        color: var(--text);
    }

    .card .muted {
        color: var(--muted);
        font-size: 0.92rem;
    }

    .incident-id {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        background: rgba(94, 234, 212, 0.14);
        color: var(--accent);
        font-weight: 600;
        font-size: 0.84rem;
        margin-bottom: 0.55rem;
    }

    .score {
        display: inline-block;
        padding: 0.18rem 0.55rem;
        border-radius: 999px;
        background: rgba(251, 191, 36, 0.14);
        color: var(--accent-2);
        font-weight: 600;
        font-size: 0.84rem;
        margin-left: 0.35rem;
    }

    .evidence-box {
        background: rgba(20, 35, 58, 0.78);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0.95rem 1rem;
        margin-bottom: 0.8rem;
    }

    .stat-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 0.8rem 0 1rem;
    }

    .stat {
        background: rgba(15, 27, 45, 0.8);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0.9rem 1rem;
    }

    .stat-label {
        color: var(--muted);
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.25rem;
    }

    .stat-value {
        color: var(--text);
        font-size: 1.4rem;
        font-weight: 700;
    }

    @media (max-width: 900px) {
        .stat-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 640px) {
        .stat-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


def api_post(endpoint: str, *, files: Dict[str, Any] | None = None, json_payload: Dict[str, Any] | None = None):
    url = f"{BACKEND_URL}{endpoint}"
    response = requests.post(url, files=files, json=json_payload, timeout=120)
    response.raise_for_status()
    return response.json()


def format_score(score: float) -> str:
    return f"{score:.3f}"


def render_metric(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="stat">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_similar_incident(incident: Dict[str, Any]) -> None:
    metadata = incident.get("metadata", {}) or {}
    component = metadata.get("component") or incident.get("component") or ""
    severity = metadata.get("severity") or incident.get("severity") or ""
    environment = metadata.get("environment") or incident.get("environment") or ""

    st.markdown(
        f"""
        <div class="card">
            <div class="incident-id">{incident.get('incident_id', 'Unknown Incident')}</div>
            <span class="score">Similarity {format_score(float(incident.get('similarity_score', 0.0)))}</span>
            <h3>{incident.get('title', 'Untitled Incident')}</h3>
            <p class="muted">{incident.get('description', '')}</p>
            <div><strong>Root Cause:</strong> {incident.get('root_cause', '')}</div>
            <div style="margin-top:0.35rem;"><strong>Resolution:</strong> {incident.get('resolution', '')}</div>
            {f"<div class='muted' style='margin-top:0.45rem;'>Component: {component} | Severity: {severity} | Environment: {environment}</div>" if any([component, severity, environment]) else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_evidence_incident(incident: Dict[str, Any]) -> None:
    st.markdown(
        f"""
        <div class="evidence-box">
            <strong>{incident.get('incident_id', 'Unknown Incident')}</strong>
            <span class="score" style="margin-left:0.45rem;">{format_score(float(incident.get('similarity_score', 0.0)))}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="hero">
        <h1>Enterprise Incident RCA Assistant</h1>
        <p>Upload historical incident data, analyze a new incident, and retrieve the strongest evidence for likely root cause and resolution.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "latest_upload" not in st.session_state:
    st.session_state.latest_upload = None

if "latest_analysis" not in st.session_state:
    st.session_state.latest_analysis = None

with st.sidebar:
    st.markdown("## Historical Incident Dataset")
    uploaded_file = st.file_uploader(
        "Upload CSV, JSON, or Excel",
        type=["csv", "json", "xls", "xlsx"],
        help="CSV is the primary format. JSON and Excel are also supported.",
    )

    if st.button("Upload & Index", use_container_width=True):
        if not uploaded_file:
            st.warning("Choose a dataset file first.")
        else:
            with st.spinner("Indexing incidents..."):
                try:
                    payload = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type or "application/octet-stream",
                        )
                    }
                    response = api_post("/api/incidents/upload", files=payload)
                    st.session_state.latest_upload = response
                    st.success(response.get("message", "Dataset indexed."))
                except requests.HTTPError as exc:
                    detail = exc.response.json().get("detail", exc.response.text)
                    st.error(detail)
                except requests.RequestException as exc:
                    st.error(f"Unable to reach the backend: {exc}")

    if st.session_state.latest_upload:
        upload = st.session_state.latest_upload
        st.markdown("### Dataset Loaded")
        st.markdown(
            f"**{upload.get('indexed_incidents', 0):,} incidents indexed**\n\n"
            f"{upload.get('duplicates_removed', 0):,} duplicates removed · {upload.get('skipped_rows', 0):,} rows skipped"
        )

    st.divider()
    st.caption("The backend stores the latest uploaded dataset and rebuilds the FAISS index from it.")


st.markdown("## New Incident")
with st.form("incident_form"):
    description = st.text_area(
        "Describe the new incident...",
        height=180,
        placeholder="Example: Payment checkout is failing with HTTP 500 errors in production.",
    )

    option_cols = st.columns(3)
    with option_cols[0]:
        component = st.text_input("Component", placeholder="Payment Service")
    with option_cols[1]:
        severity = st.selectbox("Severity", ["", "Low", "Medium", "High", "Critical"], index=0)
    with option_cols[2]:
        environment = st.selectbox("Environment", ["", "Production", "Staging", "QA", "Development"], index=0)

    incident_type = st.text_input("Incident Type", placeholder="Service Outage")

    submitted = st.form_submit_button("Analyze Incident", use_container_width=True)


if submitted:
    if not description.strip():
        st.warning("Enter an incident description before analyzing.")
    else:
        payload = {
            "description": description.strip(),
            "component": component.strip() or None,
            "severity": severity or None,
            "environment": environment or None,
            "incident_type": incident_type.strip() or None,
        }

        with st.spinner("Retrieving similar incidents and generating RCA..."):
            try:
                response = api_post("/api/incidents/analyze", json_payload=payload)
                st.session_state.latest_analysis = response
            except requests.HTTPError as exc:
                detail = exc.response.json().get("detail", exc.response.text)
                st.error(detail)
            except requests.RequestException as exc:
                st.error(f"Unable to reach the backend: {exc}")


analysis = st.session_state.latest_analysis

if analysis:
    st.markdown("## Top 5 Similar Incidents")
    similar_incidents = analysis.get("similar_incidents", [])
    if similar_incidents:
        for incident in similar_incidents:
            render_similar_incident(incident)
    else:
        st.info("No similar incidents were returned.")

    st.markdown("## RCA Result")
    top_metric_cols = st.columns(3)
    with top_metric_cols[0]:
        render_metric("Likely Root Cause", analysis.get("root_cause", "Unavailable"))
    with top_metric_cols[1]:
        render_metric("Recommended Resolution", analysis.get("resolution", "Unavailable"))
    with top_metric_cols[2]:
        render_metric("Evidence Strength", analysis.get("evidence_strength", "Unavailable"))

    st.markdown("### Supporting Incidents")
    evidence_incidents = analysis.get("evidence_incidents", [])
    if evidence_incidents:
        evidence_cols = st.columns(min(3, len(evidence_incidents)))
        for index, incident in enumerate(evidence_incidents[:3]):
            with evidence_cols[index % len(evidence_cols)]:
                render_evidence_incident(incident)
    else:
        st.info("No supporting incidents were identified.")

    st.markdown("### AI RCA Summary")
    st.write(analysis.get("summary", "No summary was returned by the model."))

    if analysis.get("evidence_strength") == "Insufficient":
        st.warning("Insufficient historical evidence was found to determine a reliable root cause.")