"""ClinicalTrials.gov API version and data freshness utilities."""

from __future__ import annotations

from typing import Any

import requests

VERSION_URL = "https://clinicaltrials.gov/api/v2/version"


def fetch_api_version(timeout: int = 20) -> dict[str, Any]:
    """Return API version metadata, including the official data timestamp."""
    response = requests.get(VERSION_URL, timeout=timeout)
    response.raise_for_status()
    payload = response.json()

    return {
        "api_version": payload.get("version"),
        "data_timestamp": payload.get("dataTimestamp"),
        "source": VERSION_URL,
    }
