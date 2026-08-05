"""Extract oncology clinical trial records from the ClinicalTrials.gov API v2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

API_URL = "https://clinicaltrials.gov/api/v2/studies"

DEFAULT_FIELDS = [
    "NCTId",
    "BriefTitle",
    "OfficialTitle",
    "OverallStatus",
    "StudyType",
    "Phase",
    "Condition",
    "InterventionName",
    "LeadSponsorName",
    "EnrollmentCount",
    "EnrollmentType",
    "StartDate",
    "PrimaryCompletionDate",
    "CompletionDate",
    "LocationFacility",
    "LocationCity",
    "LocationState",
    "LocationCountry",
    "StudyFirstPostDate",
    "LastUpdatePostDate",
]


def fetch_studies(
    condition: str = "cancer",
    page_size: int = 500,
    max_studies: int = 2000,
    timeout: int = 45,
) -> dict[str, Any]:
    """Fetch interventional Phase 2/3 studies for a condition.

    The API returns nested JSON. Pagination continues until max_studies,
    the response has no nextPageToken, or the result set is exhausted.
    """
    if page_size < 1 or page_size > 1000:
        raise ValueError("page_size must be between 1 and 1000.")
    if max_studies < 1:
        raise ValueError("max_studies must be positive.")

    params: dict[str, Any] = {
        "query.cond": condition,
        "filter.overallStatus": (
            "RECRUITING|NOT_YET_RECRUITING|ACTIVE_NOT_RECRUITING|"
            "ENROLLING_BY_INVITATION|COMPLETED|SUSPENDED|TERMINATED|WITHDRAWN"
        ),
        "filter.advanced": (
            "AREA[StudyType]INTERVENTIONAL AND "
            "(AREA[Phase]PHASE2 OR AREA[Phase]PHASE3)"
        ),
        "fields": ",".join(DEFAULT_FIELDS),
        "format": "json",
        "pageSize": min(page_size, max_studies),
        "countTotal": "true",
    }

    studies: list[dict[str, Any]] = []
    next_page_token: str | None = None
    total_count: int | None = None

    while len(studies) < max_studies:
        request_params = dict(params)
        request_params["pageSize"] = min(page_size, max_studies - len(studies))
        if next_page_token:
            request_params["pageToken"] = next_page_token

        response = requests.get(API_URL, params=request_params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()

        if total_count is None:
            total_count = payload.get("totalCount")

        batch = payload.get("studies", [])
        studies.extend(batch)

        next_page_token = payload.get("nextPageToken")
        if not next_page_token or not batch:
            break

    return {
        "source": API_URL,
        "query_condition": condition,
        "total_count_reported": total_count,
        "records_retrieved": len(studies),
        "studies": studies,
    }


def save_raw_payload(
    payload: dict[str, Any],
    output_path: str | Path = "data/raw/oncology_trials_raw.json",
) -> Path:
    """Save the raw API response for reproducibility."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    result = fetch_studies()
    destination = save_raw_payload(result)
    print(f"Saved {result['records_retrieved']} studies to {destination}")
