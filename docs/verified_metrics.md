# TrialPulse Verified Metrics

This document records the final validated metrics used across the TrialPulse Oncology analytics products.

**ClinicalTrials.gov data through:** August 7, 2026  
**Final validation:** August 8, 2026  
**Portfolio size:** 2,000 unique oncology clinical trials

---

## Executive Portfolio Metrics

| Metric | Verified Value |
|---|---:|
| Total Trials | 2,000 |
| Active Trials | 676 |
| Distinct Sponsors | 895 |
| High/Critical Priority Trials | 69 |
| High/Critical Priority Rate | 3.5% |
| Median Planned Enrollment | 55 |
| Median Planned Duration | 4.5 years |
| Data Through | August 7, 2026 |

---

## Monitoring Indicators

| Metric | Verified Value |
|---|---:|
| Stale Registry Records | 1,149 |
| Limited-Site Trials | 1,147 |
| Overdue Active Trials | 30 |
| Average Record Completeness | 87.3% |

### Monitoring Priority Distribution

| Priority | Trials |
|---|---:|
| Low | 1,394 |
| Moderate | 537 |
| High | 64 |
| Critical | 5 |
| **Total** | **2,000** |

High/Critical Priority includes both High and Critical monitoring-priority categories:

- High: 64
- Critical: 5
- Combined: 69

Monitoring-priority indicators are heuristic portfolio-review signals. They do not predict clinical success, regulatory approval, trial failure, or sponsor performance.

---

## Portfolio Status

| Status Group | Trials |
|---|---:|
| Completed | 963 |
| Active | 676 |
| Discontinued | 361 |
| **Total** | **2,000** |

---

## Phase Distribution

| Phase | Trials |
|---|---:|
| Phase I/II | 354 |
| Phase II | 1,209 |
| Phase II/III | 62 |
| Phase III | 375 |
| **Total** | **2,000** |

---

## Sponsor Class Distribution

| Sponsor Class | Trials |
|---|---:|
| OTHER | 1,219 |
| INDUSTRY | 570 |
| NIH | 96 |
| NETWORK | 86 |
| OTHER_GOV | 26 |
| FED | 2 |
| INDIV | 1 |
| **Total** | **2,000** |

---

## Record Completeness

The record-completeness score reflects whether selected analytical fields are populated. It should not be interpreted as an overall assessment of ClinicalTrials.gov data quality or reliability.

| Completeness Score | Trials |
|---|---:|
| 100 | 1,032 |
| 75 | 922 |
| 50 | 46 |
| **Total** | **2,000** |

**Average Record Completeness:** 87.3%

---

## Geographic Coverage

The geographic analytical layer contains one row per unique trial-country combination.

| Metric | Verified Value |
|---|---:|
| Trial-Country Rows | 4,545 |
| Trials with Reported Geography | 1,868 |
| Countries Covered | 85 |
| Multicountry Trials | 391 |
| Single-Country Trials | 1,477 |
| No Reported Geography | 132 |
| Geography Coverage | 93.4% |
| Average Countries per Geographic Trial | 2.4 |

Country-level trial counts are not additive to the total portfolio because one clinical trial may operate in multiple countries.

---

## Validation Checks

| Validation Check | Result |
|---|---:|
| Duplicate NCT IDs | 0 |
| Missing Sponsor Class | 0 |
| Missing Last Update Date | 0 |
| Minimum Monitoring-Priority Score | 0 |
| Maximum Monitoring-Priority Score | 95 |

---

## Analytical Definitions

**Active Trials**  
Trials grouped into the Active reporting category based on their ClinicalTrials.gov status.

**High/Critical Priority**  
Trials classified as High or Critical under the TrialPulse heuristic monitoring-priority framework.

**Stale Registry Record**  
A public registry record whose latest reported update is more than two years old under the current monitoring rules.

**Limited-Site Trial**  
A trial with fewer than three registered locations under the current monitoring rules.

**Overdue Active Trial**  
An active study whose reported completion date has already passed.

**Record Completeness**  
A descriptive completeness indicator based on selected fields used by the analytical model. It is not a measure of overall registry accuracy.

**Peer Cohort**  
For Benchmark Analysis, comparable trials share the selected study's Phase and Trial Status. The selected NCT ID itself is excluded from its peer cohort.

---

## Source

ClinicalTrials.gov API v2.

TrialPulse uses publicly available clinical-trial registry information for analytical demonstration and portfolio-review purposes.