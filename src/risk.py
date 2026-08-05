"""Transparent monitoring-priority scoring for clinical trial records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class RiskResult:
    score: int
    category: str
    reasons: list[str]


def categorize_score(score: int) -> str:
    """Map a 0-100 score to a monitoring-priority category."""
    if score >= 75:
        return "Critical"
    if score >= 50:
        return "High"
    if score >= 25:
        return "Moderate"
    return "Low"


def score_trial(row: pd.Series, benchmarks: dict[str, float]) -> RiskResult:
    """Calculate an explainable heuristic score.

    This is not a prediction of trial success or failure. It is a transparent
    prioritization mechanism for exploratory portfolio review.
    """
    score = 0
    reasons: list[str] = []
    today = pd.Timestamp(date.today())

    status = str(row.get("status", "")).upper()
    completed_statuses = {"COMPLETED", "TERMINATED", "WITHDRAWN"}

    completion_date = pd.to_datetime(row.get("completion_date"), errors="coerce")
    if (
        pd.notna(completion_date)
        and completion_date < today
        and status not in completed_statuses
    ):
        score += 30
        reasons.append("Expected completion date has passed while the study remains active.")

    duration = row.get("study_duration_days")
    duration_threshold = benchmarks.get("duration_p75", 0)
    if pd.notna(duration) and duration_threshold and float(duration) > duration_threshold:
        score += 20
        reasons.append("Planned duration exceeds the portfolio's 75th percentile.")

    study_age = row.get("study_age_days")
    age_threshold = benchmarks.get("active_age_p75", 0)
    active_statuses = {
        "RECRUITING",
        "NOT_YET_RECRUITING",
        "ACTIVE_NOT_RECRUITING",
        "ENROLLING_BY_INVITATION",
    }
    if (
        status in active_statuses
        and pd.notna(study_age)
        and age_threshold
        and float(study_age) > age_threshold
    ):
        score += 20
        reasons.append("The study has remained active longer than most active studies.")

    locations = row.get("location_count")
    if pd.notna(locations) and float(locations) < 3:
        score += 15
        reasons.append("The study has fewer than three registered locations.")

    enrollment = row.get("enrollment")
    enrollment_median = benchmarks.get("enrollment_median", 0)
    if (
        pd.notna(enrollment)
        and enrollment_median
        and float(enrollment) < 0.5 * enrollment_median
    ):
        score += 10
        reasons.append("Planned enrollment is less than half the portfolio median.")

    last_update = pd.to_datetime(row.get("last_update_date"), errors="coerce")
    if pd.notna(last_update) and (today - last_update).days > 730:
        score += 5
        reasons.append("The public record has not been updated in more than two years.")

    score = min(score, 100)
    if not reasons:
        reasons.append("No elevated monitoring indicators were detected by the current rules.")

    return RiskResult(score=score, category=categorize_score(score), reasons=reasons)
