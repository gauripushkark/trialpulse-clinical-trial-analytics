"""Create a Power BI-ready analytical export from TrialPulse data."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


INPUT_PATH = Path("data/processed/trialpulse_oncology.csv")
OUTPUT_PATH = Path("data/processed/trialpulse_gold_dataset.csv")


ACTIVE_STATUSES = {
    "RECRUITING",
    "NOT_YET_RECRUITING",
    "ACTIVE_NOT_RECRUITING",
    "ENROLLING_BY_INVITATION",
}

DISCONTINUED_STATUSES = {
    "TERMINATED",
    "WITHDRAWN",
    "SUSPENDED",
}


def clean_phase(value: object) -> str:
    """Convert API phase values into business-friendly labels."""
    if pd.isna(value):
        return "Not specified"

    phase_map = {
        "PHASE1": "Phase I",
        "PHASE2": "Phase II",
        "PHASE3": "Phase III",
        "PHASE4": "Phase IV",
        "EARLY_PHASE1": "Early Phase I",
        "PHASE1 | PHASE2": "Phase I/II",
        "PHASE2 | PHASE3": "Phase II/III",
    }

    normalized = str(value).strip().upper()
    return phase_map.get(normalized, normalized.title())


def create_status_group(value: object) -> str:
    """Group detailed statuses into executive reporting categories."""
    if pd.isna(value):
        return "Other"

    status = str(value).strip().upper()

    if status in ACTIVE_STATUSES:
        return "Active"
    if status == "COMPLETED":
        return "Completed"
    if status in DISCONTINUED_STATUSES:
        return "Discontinued"

    return "Other"


def build_bi_export(df: pd.DataFrame) -> pd.DataFrame:
    """Add BI-friendly dimensions, bands, flags, and sponsor metrics."""
    result = df.copy()

    result["phase_clean"] = result["phase"].apply(clean_phase)
    result["status_group"] = result["status"].apply(create_status_group)

    result["duration_years"] = result["study_duration_days"] / 365.25

    result["duration_band"] = (
        pd.cut(
            result["duration_years"],
            bins=[-np.inf, 2, 4, 6, np.inf],
            labels=[
                "Under 2 years",
                "2–4 years",
                "4–6 years",
                "6+ years",
            ],
        )
        .astype("object")
        .fillna("Duration Unknown")
    )

    result["enrollment_band"] = (
        pd.cut(
            result["enrollment"],
            bins=[-np.inf, 50, 200, 500, np.inf],
            labels=[
                "50 or fewer",
                "51–200",
                "201–500",
                "More than 500",
            ],
        )
        .astype("object")
        .fillna("Enrollment Unknown")
    )

    # -----------------------------
    # Business Sort Orders
    # -----------------------------

    phase_order_map = {
        "Early Phase I": 1,
        "Phase I": 2,
        "Phase I/II": 3,
        "Phase II": 4,
        "Phase II/III": 5,
        "Phase III": 6,
        "Phase IV": 7,
        "Not specified": 99,
    }

    risk_order_map = {
        "Low": 1,
        "Moderate": 2,
        "High": 3,
        "Critical": 4,
    }

    duration_order_map = {
        "Under 2 years": 1,
        "2–4 years": 2,
        "4–6 years": 3,
        "6+ years": 4,
        "Duration Unknown": 5,
    }

    enrollment_order_map = {
        "50 or fewer": 1,
        "51–200": 2,
        "201–500": 3,
        "More than 500": 4,
        "Enrollment Unknown": 5,
    }

    result["phase_order"] = (
        result["phase_clean"].map(phase_order_map).fillna(99).astype(int)
    )

    result["risk_order"] = (
        result["risk_category"].map(risk_order_map).fillna(99).astype(int)
    )

    result["duration_band_order"] = (
        result["duration_band"].map(duration_order_map).fillna(99).astype(int)
    )

    result["enrollment_band_order"] = (
        result["enrollment_band"].map(enrollment_order_map).fillna(99).astype(int)
    )

    today = pd.Timestamp.today().normalize()

    completion_date = pd.to_datetime(
        result["completion_date"],
        errors="coerce",
    )

    last_update_date = pd.to_datetime(
        result["last_update_date"],
        errors="coerce",
    )

    result["completion_overdue_flag"] = (
        completion_date.lt(today)
        & result["status"].isin(ACTIVE_STATUSES)
    )

    result["limited_sites_flag"] = (
        result["location_count"]
        .fillna(0)
        .lt(3)
    )

    result["stale_record_flag"] = (
        today - last_update_date
    ).dt.days.gt(730)

    result["high_priority_flag"] = result["risk_category"].isin(
        ["High", "Critical"]
    )

    sponsor_counts = (
        result.groupby("sponsor", dropna=False)["nct_id"]
        .nunique()
        .rename("sponsor_trial_count")
    )

    result = result.merge(
        sponsor_counts,
        how="left",
        left_on="sponsor",
        right_index=True,
    )

    result["sponsor_rank"] = (
        result["sponsor_trial_count"]
        .rank(method="dense", ascending=False)
        .astype("Int64")
    )

# -----------------------------
# Data Quality Indicators
# -----------------------------

    result["missing_completion_date"] = completion_date.isna()
    result["missing_enrollment"] = result["enrollment"].isna()
    result["missing_sponsor"] = result["sponsor"].isna()
    result["missing_phase"] = result["phase"].isna()

    result["data_quality_score"] = 100

    result.loc[result["missing_completion_date"], "data_quality_score"] -= 25
    result.loc[result["missing_enrollment"], "data_quality_score"] -= 25
    result.loc[result["missing_sponsor"], "data_quality_score"] -= 25
    result.loc[result["missing_phase"], "data_quality_score"] -= 25



    return result


def validate_export(df: pd.DataFrame) -> None:
    """Run basic data-quality checks."""
    errors: list[str] = []

    if df["nct_id"].duplicated().any():
        errors.append("Duplicate NCT IDs detected.")

    if (df["duration_years"].dropna() < 0).any():
        errors.append("Negative duration values detected.")

    if not df["risk_score"].dropna().between(0, 100).all():
        errors.append("Risk scores outside the 0–100 range detected.")

    if errors:
        raise ValueError(" | ".join(errors))


def main() -> None:
    """Create and save the Power BI-ready dataset."""
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_PATH}. "
            "Run `python -m src.transform` first."
        )

    source = pd.read_csv(INPUT_PATH)

    exported = build_bi_export(source)
    validate_export(exported)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    exported.to_csv(OUTPUT_PATH, index=False)

    print(f"Source rows: {len(source):,}")
    print(f"Export rows: {len(exported):,}")
    print(f"Unique trials: {exported['nct_id'].nunique():,}")
    print(f"New columns: {len(exported.columns) - len(source.columns)}")
    print(f"Saved BI-ready dataset to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()