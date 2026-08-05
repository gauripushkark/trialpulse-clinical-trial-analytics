"""Transform ClinicalTrials.gov API v2 records into an analytics-ready dataset."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.risk import score_trial


def _get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
        if current is None:
            return default
    return current


def _join(values: Any) -> str:
    if values is None:
        return ""
    if isinstance(values, list):
        return " | ".join(str(value) for value in values if value not in (None, ""))
    return str(values)


def flatten_study(study: dict[str, Any]) -> dict[str, Any]:
    """Flatten a single nested API study record."""
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    conditions = protocol.get("conditionsModule", {})
    arms = protocol.get("armsInterventionsModule", {})
    sponsor = protocol.get("sponsorCollaboratorsModule", {})
    contacts = protocol.get("contactsLocationsModule", {})

    locations = contacts.get("locations", []) or []
    countries = sorted(
        {
            str(location.get("country")).strip()
            for location in locations
            if location.get("country")
        }
    )
    facilities = [
        location.get("facility")
        for location in locations
        if location.get("facility")
    ]

    phases = design.get("phases", []) or []
    interventions = [
        item.get("name")
        for item in (arms.get("interventions", []) or [])
        if item.get("name")
    ]

    lead_sponsor = sponsor.get("leadSponsor", {}) or {}
    enrollment_info = design.get("enrollmentInfo", {}) or {}

    return {
        "nct_id": identification.get("nctId"),
        "brief_title": identification.get("briefTitle"),
        "official_title": identification.get("officialTitle"),
        "status": status.get("overallStatus"),
        "study_type": design.get("studyType"),
        "phase": _join(phases),
        "conditions": _join(conditions.get("conditions", [])),
        "interventions": _join(interventions),
        "sponsor": lead_sponsor.get("name"),
        "sponsor_class": lead_sponsor.get("class"),
        "enrollment": enrollment_info.get("count"),
        "enrollment_type": enrollment_info.get("type"),
        "start_date": _get(status, "startDateStruct", "date"),
        "primary_completion_date": _get(
            status, "primaryCompletionDateStruct", "date"
        ),
        "completion_date": _get(status, "completionDateStruct", "date"),
        "first_post_date": _get(status, "studyFirstPostDateStruct", "date"),
        "last_update_date": _get(status, "studyLastUpdatePostDateStruct", "date"),
        "location_count": len(locations),
        "facility_count": len(set(facilities)),
        "country_count": len(countries),
        "countries": " | ".join(countries),
        "is_multicountry": len(countries) > 1,
    }


def transform_payload(payload: dict[str, Any]) -> pd.DataFrame:
    """Create the final analytics dataset and monitoring-priority indicators."""
    studies = payload.get("studies", [])
    if not studies:
        raise ValueError("The payload contains no studies.")

    df = pd.DataFrame(flatten_study(study) for study in studies)
    df = df.drop_duplicates(subset=["nct_id"]).copy()

    df["sponsor"] = df["sponsor"].fillna("Unknown sponsor")
    df["phase"] = df["phase"].replace("", "Not specified")
    df["status"] = df["status"].fillna("UNKNOWN")
    df["enrollment"] = pd.to_numeric(df["enrollment"], errors="coerce")

    date_columns = [
        "start_date",
        "primary_completion_date",
        "completion_date",
        "first_post_date",
        "last_update_date",
    ]
    for column in date_columns:
        df[column] = pd.to_datetime(df[column], errors="coerce")

    df["study_duration_days"] = (
        df["completion_date"] - df["start_date"]
    ).dt.days
    df.loc[df["study_duration_days"] < 0, "study_duration_days"] = np.nan

    today = pd.Timestamp(date.today())
    df["study_age_days"] = (today - df["start_date"]).dt.days
    df.loc[df["study_age_days"] < 0, "study_age_days"] = 0

    active_mask = df["status"].isin(
        [
            "RECRUITING",
            "NOT_YET_RECRUITING",
            "ACTIVE_NOT_RECRUITING",
            "ENROLLING_BY_INVITATION",
        ]
    )

    benchmarks = {
        "duration_p75": float(df["study_duration_days"].quantile(0.75)),
        "active_age_p75": float(df.loc[active_mask, "study_age_days"].quantile(0.75))
        if active_mask.any()
        else 0.0,
        "enrollment_median": float(df["enrollment"].median()),
    }

    results = df.apply(lambda row: score_trial(row, benchmarks), axis=1)
    df["risk_score"] = [result.score for result in results]
    df["risk_category"] = [result.category for result in results]
    df["risk_reasons"] = [" | ".join(result.reasons) for result in results]

    return df.sort_values(
        ["risk_score", "enrollment"], ascending=[False, False], na_position="last"
    ).reset_index(drop=True)


def load_and_transform(
    input_path: str | Path = "data/raw/oncology_trials_raw.json",
    output_path: str | Path = "data/processed/trialpulse_oncology.csv",
) -> pd.DataFrame:
    """Read raw JSON, transform it, and save a processed CSV."""
    source = Path(input_path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    df = transform_payload(payload)

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destination, index=False)
    return df


if __name__ == "__main__":
    transformed = load_and_transform()
    print(f"Saved {len(transformed)} processed trial records.")
