"""Validate final TrialPulse portfolio metrics."""

from pathlib import Path

import pandas as pd


GOLD_PATH = Path("data/processed/trialpulse_gold_dataset.csv")
GEO_PATH = Path("data/processed/trialpulse_trial_countries.csv")


def main() -> None:
    trials = pd.read_csv(GOLD_PATH)
    geo = pd.read_csv(GEO_PATH)

    trials["last_update_date"] = pd.to_datetime(
        trials["last_update_date"], errors="coerce"
    )

    total_trials = trials["nct_id"].nunique()
    geographic_trials = geo["nct_id"].nunique()

    print("\n=== TRIALPULSE FINAL VERIFIED METRICS ===\n")

    print("PORTFOLIO")
    print(f"Total Trials: {total_trials:,}")
    print(
        f"Active Trials: "
        f"{trials.loc[trials['status_group'].eq('Active'), 'nct_id'].nunique():,}"
    )
    print(f"Distinct Sponsors: {trials['sponsor'].nunique():,}")
    print(f"High/Critical Priority: {int(trials['high_priority_flag'].sum()):,}")
    print(
        f"High/Critical Rate: "
        f"{trials['high_priority_flag'].mean():.1%}"
    )
    print(f"Median Planned Enrollment: {trials['enrollment'].median():,.0f}")
    print(f"Median Planned Duration: {trials['duration_years'].median():.1f} years")
    print(
        f"Data Through: "
        f"{trials['last_update_date'].max().strftime('%b %d, %Y')}"
    )

    print("\nMONITORING")
    print(f"Stale Registry Records: {int(trials['stale_record_flag'].sum()):,}")
    print(f"Limited-Site Trials: {int(trials['limited_sites_flag'].sum()):,}")
    print(
        f"Overdue Active Trials: "
        f"{int(trials['completion_overdue_flag'].sum()):,}"
    )
    print(
        f"Average Record Completeness: "
        f"{trials['data_quality_score'].mean():.1f}%"
    )

    print("\nSTATUS DISTRIBUTION")
    print(trials["status_group"].value_counts().to_string())

    print("\nPHASE DISTRIBUTION")
    print(
        trials["phase_clean"]
        .value_counts()
        .reindex(
            ["Phase I/II", "Phase II", "Phase II/III", "Phase III"]
        )
        .dropna()
        .astype(int)
        .to_string()
    )

    print("\nMONITORING PRIORITY DISTRIBUTION")
    print(
        trials["risk_category"]
        .value_counts()
        .reindex(["Low", "Moderate", "High", "Critical"])
        .fillna(0)
        .astype(int)
        .to_string()
    )

    print("\nSPONSOR CLASS DISTRIBUTION")
    print(trials["sponsor_class"].value_counts().to_string())

    print("\nRECORD COMPLETENESS DISTRIBUTION")
    print(
        trials["data_quality_score"]
        .value_counts()
        .sort_index(ascending=False)
        .to_string()
    )

    print("\nGEOGRAPHY")
    print(f"Trial-Country Rows: {len(geo):,}")
    print(f"Trials with Reported Geography: {geographic_trials:,}")
    print(f"Countries Covered: {geo['country'].nunique():,}")
    print(
        f"Multicountry Trials: "
        f"{int((trials['country_count'] > 1).sum()):,}"
    )
    print(
        f"Single-Country Trials: "
        f"{int((trials['country_count'] == 1).sum()):,}"
    )
    print(
        f"No Reported Geography: "
        f"{int((trials['country_count'] == 0).sum()):,}"
    )
    print(
        f"Geography Coverage: "
        f"{geographic_trials / total_trials:.1%}"
    )
    print(
        f"Avg Countries per Geographic Trial: "
        f"{len(geo) / geographic_trials:.1f}"
    )

    print("\nVALIDATION")
    print(f"Duplicate NCT IDs: {trials['nct_id'].duplicated().sum():,}")
    print(f"Missing Sponsor Class: {trials['sponsor_class'].isna().sum():,}")
    print(f"Missing Last Update Date: {trials['last_update_date'].isna().sum():,}")
    print(f"Risk Score Min: {trials['risk_score'].min():.0f}")
    print(f"Risk Score Max: {trials['risk_score'].max():.0f}")


if __name__ == "__main__":
    main()