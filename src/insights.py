"""Automated, rule-based business insight generation."""

from __future__ import annotations

import pandas as pd


def portfolio_insights(df: pd.DataFrame) -> list[str]:
    """Generate concise portfolio-level observations."""
    if df.empty:
        return ["No trials match the current filters."]

    insights: list[str] = []

    high_count = int(df["risk_category"].isin(["High", "Critical"]).sum())
    high_share = high_count / len(df)
    insights.append(
        f"{high_count:,} studies ({high_share:.1%}) are classified as high or "
        "critical monitoring priority under the current rules."
    )

    if df["phase"].notna().any():
        top_phase = df["phase"].value_counts().idxmax()
        phase_share = (df["phase"] == top_phase).mean()
        insights.append(
            f"{top_phase} is the largest phase group, representing {phase_share:.1%} "
            "of the filtered portfolio."
        )

    sponsor_counts = df["sponsor"].value_counts()
    if not sponsor_counts.empty:
        top_sponsor = sponsor_counts.index[0]
        insights.append(
            f"{top_sponsor} has the most studies in the current view "
            f"({int(sponsor_counts.iloc[0]):,})."
        )

    median_enrollment = df["enrollment"].median()
    if pd.notna(median_enrollment):
        insights.append(
            f"Median planned enrollment is {median_enrollment:,.0f} participants."
        )

    return insights


def trial_narrative(row: pd.Series, peers: pd.DataFrame) -> str:
    """Generate a benchmarked narrative for one selected trial."""
    statements: list[str] = []

    if not peers.empty:
        peer_duration = peers["study_duration_days"].median()
        peer_enrollment = peers["enrollment"].median()
        peer_locations = peers["location_count"].median()

        duration = row.get("study_duration_days")
        if pd.notna(duration) and pd.notna(peer_duration):
            comparison = "above" if duration > peer_duration else "below"
            statements.append(
                f"Its planned duration is {comparison} the peer median "
                f"({duration:,.0f} vs. {peer_duration:,.0f} days)."
            )

        enrollment = row.get("enrollment")
        if pd.notna(enrollment) and pd.notna(peer_enrollment):
            comparison = "above" if enrollment > peer_enrollment else "below"
            statements.append(
                f"Planned enrollment is {comparison} the peer median "
                f"({enrollment:,.0f} vs. {peer_enrollment:,.0f})."
            )

        locations = row.get("location_count")
        if pd.notna(locations) and pd.notna(peer_locations):
            comparison = "above" if locations > peer_locations else "below"
            statements.append(
                f"Registered location count is {comparison} the peer median "
                f"({locations:,.0f} vs. {peer_locations:,.0f})."
            )

    reasons = str(row.get("risk_reasons", "")).replace(" | ", " ")
    if reasons:
        statements.append(f"Monitoring rationale: {reasons}")

    return " ".join(statements)
