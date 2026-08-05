"""TrialPulse Oncology Streamlit application."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.api_status import fetch_api_version
from src.extract import fetch_studies, save_raw_payload
from src.insights import portfolio_insights, trial_narrative
from src.transform import load_and_transform

PROCESSED_PATH = Path("data/processed/trialpulse_oncology.csv")
RAW_PATH = Path("data/raw/oncology_trials_raw.json")

COLORS = {
    "Low": "#2E7D32",
    "Moderate": "#E59A22",
    "High": "#E76F51",
    "Critical": "#C62828",
}

st.set_page_config(
    page_title="TrialPulse Oncology",
    page_icon="🧪",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
        div[data-testid="stMetric"] {
            background: white;
            border: 1px solid #E3E8EF;
            padding: 14px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(11,31,58,.05);
        }
        .subtitle {color:#52616B; margin-top:-8px;}
        .disclaimer {
            background:#F5F7FA; border-left:4px solid #1769AA;
            padding:10px 14px; border-radius:6px; color:#3C4858;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=86400, show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load local processed data or retrieve and transform public API data."""
    if not PROCESSED_PATH.exists():
        payload = fetch_studies(condition="cancer", max_studies=2000)
        save_raw_payload(payload, RAW_PATH)
        load_and_transform(RAW_PATH, PROCESSED_PATH)

    df = pd.read_csv(PROCESSED_PATH)
    for column in [
        "start_date",
        "primary_completion_date",
        "completion_date",
        "first_post_date",
        "last_update_date",
    ]:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    return df


st.title("TrialPulse Oncology")
st.markdown(
    '<p class="subtitle">Clinical trial intelligence and explainable monitoring analytics</p>',
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="disclaimer">
    Exploratory portfolio project using public ClinicalTrials.gov records.
    Monitoring-priority scores are transparent analytical heuristics—not clinical,
    regulatory, or investment recommendations.
    </div>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(ttl=3600, show_spinner=False)
def load_api_status() -> dict:
    try:
        return fetch_api_version()
    except Exception:
        return {"api_version": None, "data_timestamp": None, "source": None}


api_status = load_api_status()
status_left, status_right = st.columns([1, 3])
with status_left:
    st.success("Live public data source")
with status_right:
    if api_status.get("data_timestamp"):
        st.caption(
            f"ClinicalTrials.gov data timestamp: {api_status['data_timestamp']} "
            f"| API version: {api_status.get('api_version') or 'Not reported'}"
        )
    else:
        st.caption("ClinicalTrials.gov freshness metadata is temporarily unavailable.")

try:
    data = load_data()
except Exception as exc:
    st.error(
        "TrialPulse could not load data. Run `python -m src.extract` and "
        "`python -m src.transform`, or verify internet access."
    )
    st.exception(exc)
    st.stop()

with st.sidebar:
    st.header("Portfolio Filters")

    phases = sorted(data["phase"].dropna().unique().tolist())
    selected_phases = st.multiselect("Phase", phases, default=phases)

    statuses = sorted(data["status"].dropna().unique().tolist())
    selected_statuses = st.multiselect("Status", statuses, default=statuses)

    risk_levels = ["Low", "Moderate", "High", "Critical"]
    selected_risks = st.multiselect(
        "Monitoring priority", risk_levels, default=risk_levels
    )

    sponsors = sorted(data["sponsor"].dropna().unique().tolist())
    selected_sponsors = st.multiselect("Sponsor", sponsors)

    search_term = st.text_input("Search NCT ID or title")

filtered = data[
    data["phase"].isin(selected_phases)
    & data["status"].isin(selected_statuses)
    & data["risk_category"].isin(selected_risks)
].copy()

if selected_sponsors:
    filtered = filtered[filtered["sponsor"].isin(selected_sponsors)]

if search_term:
    search_mask = (
        filtered["nct_id"].astype(str).str.contains(search_term, case=False, na=False)
        | filtered["brief_title"]
        .astype(str)
        .str.contains(search_term, case=False, na=False)
    )
    filtered = filtered[search_mask]

if filtered.empty:
    st.warning("No trials match the selected filters.")
    st.stop()

active_statuses = {
    "RECRUITING",
    "NOT_YET_RECRUITING",
    "ACTIVE_NOT_RECRUITING",
    "ENROLLING_BY_INVITATION",
}

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Trials", f"{len(filtered):,}")
k2.metric("Active", f"{filtered['status'].isin(active_statuses).sum():,}")
k3.metric("Median enrollment", f"{filtered['enrollment'].median():,.0f}")
k4.metric(
    "Median duration",
    f"{filtered['study_duration_days'].median() / 365.25:,.1f} yrs",
)
k5.metric("Sponsors", f"{filtered['sponsor'].nunique():,}")
k6.metric(
    "High priority",
    f"{filtered['risk_category'].isin(['High', 'Critical']).sum():,}",
)

st.subheader("Executive Insights")
for insight in portfolio_insights(filtered):
    st.markdown(f"- {insight}")

left, right = st.columns(2)

with left:
    phase_counts = (
        filtered["phase"].value_counts().rename_axis("phase").reset_index(name="trials")
    )
    fig_phase = px.bar(
        phase_counts,
        x="phase",
        y="trials",
        title="Trials by Phase",
        color_discrete_sequence=["#1769AA"],
    )
    st.plotly_chart(fig_phase, use_container_width=True)

    sponsor_counts = (
        filtered["sponsor"]
        .value_counts()
        .head(12)
        .sort_values()
        .rename_axis("sponsor")
        .reset_index(name="trials")
    )
    fig_sponsor = px.bar(
        sponsor_counts,
        x="trials",
        y="sponsor",
        orientation="h",
        title="Top Sponsors",
        color_discrete_sequence=["#008C95"],
    )
    st.plotly_chart(fig_sponsor, use_container_width=True)

with right:
    risk_counts = (
        filtered["risk_category"]
        .value_counts()
        .reindex(["Low", "Moderate", "High", "Critical"], fill_value=0)
        .rename_axis("risk_category")
        .reset_index(name="trials")
    )
    fig_risk = px.bar(
        risk_counts,
        x="risk_category",
        y="trials",
        color="risk_category",
        color_discrete_map=COLORS,
        title="Monitoring-Priority Distribution",
    )
    fig_risk.update_layout(showlegend=False)
    st.plotly_chart(fig_risk, use_container_width=True)

    scatter_data = filtered.dropna(
        subset=["study_duration_days", "enrollment"]
    ).copy()
    fig_scatter = px.scatter(
        scatter_data,
        x="study_duration_days",
        y="enrollment",
        color="risk_category",
        color_discrete_map=COLORS,
        hover_name="nct_id",
        hover_data=["phase", "sponsor"],
        title="Duration vs. Planned Enrollment",
        labels={
            "study_duration_days": "Planned duration (days)",
            "enrollment": "Planned enrollment",
        },
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Trial Explorer")

display_columns = [
    "nct_id",
    "brief_title",
    "sponsor",
    "phase",
    "status",
    "enrollment",
    "location_count",
    "risk_score",
    "risk_category",
]
st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True,
    column_config={
        "nct_id": "NCT ID",
        "brief_title": "Trial",
        "risk_score": st.column_config.ProgressColumn(
            "Priority score", min_value=0, max_value=100
        ),
    },
)

csv_data = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered portfolio",
    data=csv_data,
    file_name="trialpulse_filtered_trials.csv",
    mime="text/csv",
)

st.subheader("Comparable-Trial Detail")

trial_options = filtered.apply(
    lambda row: f"{row['nct_id']} — {str(row['brief_title'])[:90]}", axis=1
).tolist()
selection = st.selectbox("Select a trial", trial_options)
selected_nct = selection.split(" — ", 1)[0]
selected = filtered.loc[filtered["nct_id"] == selected_nct].iloc[0]

peers = data[
    (data["phase"] == selected["phase"])
    & (data["nct_id"] != selected["nct_id"])
].copy()

d1, d2, d3, d4 = st.columns(4)
d1.metric("Priority score", int(selected["risk_score"]))
d2.metric("Enrollment", f"{selected['enrollment']:,.0f}")
d3.metric("Locations", f"{selected['location_count']:,.0f}")
d4.metric(
    "Duration",
    f"{selected['study_duration_days'] / 365.25:,.1f} yrs"
    if pd.notna(selected["study_duration_days"])
    else "Unknown",
)

st.markdown(f"### {selected['brief_title']}")
st.markdown(f"**Sponsor:** {selected['sponsor']}")
st.markdown(f"**Phase / status:** {selected['phase']} / {selected['status']}")
st.markdown(f"**Conditions:** {selected['conditions']}")
st.markdown(f"**Countries:** {selected['countries'] or 'Not reported'}")

st.info(trial_narrative(selected, peers))
st.markdown(
    f"[View the public ClinicalTrials.gov record]"
    f"(https://clinicaltrials.gov/study/{selected['nct_id']})"
)

with st.expander("Methodology and limitations"):
    st.markdown(
        """
        The score identifies records that may warrant closer analytical review
        based on dates, duration, enrollment, location coverage, and update recency.
        It does not evaluate clinical efficacy, safety, protocol quality, or the
        actual probability of trial success.
        """
    )
