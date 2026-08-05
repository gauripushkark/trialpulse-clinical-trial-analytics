# Data Dictionary

| Field | Type | Source / Derived | Definition |
|---|---|---|---|
| `nct_id` | text | Source | ClinicalTrials.gov study identifier |
| `brief_title` | text | Source | Public brief study title |
| `official_title` | text | Source | Official study title when provided |
| `status` | text | Source | Overall recruitment status |
| `study_type` | text | Source | Study classification |
| `phase` | text | Source | Registered study phase |
| `conditions` | text | Source | Registered conditions |
| `interventions` | text | Source | Registered interventions |
| `sponsor` | text | Source | Lead sponsor name |
| `sponsor_class` | text | Source | Lead sponsor class |
| `enrollment` | number | Source | Planned or actual enrollment count |
| `start_date` | date | Source | Registered study start date |
| `completion_date` | date | Source | Registered study completion date |
| `last_update_date` | date | Source | Last posted update date |
| `location_count` | integer | Derived | Number of registered location records |
| `country_count` | integer | Derived | Number of distinct countries |
| `study_duration_days` | number | Derived | Completion date minus start date |
| `study_age_days` | number | Derived | Current date minus start date |
| `risk_score` | integer | Derived | Transparent 0–100 monitoring-priority score |
| `risk_category` | text | Derived | Low, Moderate, High, or Critical |
| `risk_reasons` | text | Derived | Plain-English rationale for assigned points |
