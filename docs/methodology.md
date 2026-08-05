# Methodology

## Population

The default extraction retrieves public interventional studies related to cancer and limits the portfolio to Phase II and Phase III records with common active and terminal statuses.

## Feature Engineering

Derived measures include:

- planned study duration
- study age
- number of registered locations
- number of represented countries
- multi-country flag
- monitoring-priority score
- monitoring-priority category
- plain-English risk reasons

## Monitoring-Priority Framework

The score is a transparent heuristic for exploratory review. Thresholds combine absolute rules with portfolio-relative benchmarks such as the 75th percentile and median.

The score does **not** measure:

- clinical efficacy
- treatment safety
- protocol quality
- regulatory compliance
- probability of approval
- probability of study success

## Comparable-Trial Benchmarking

A selected study is compared with other records in the same phase. The MVP benchmarks duration, enrollment, and registered site count against peer medians.
