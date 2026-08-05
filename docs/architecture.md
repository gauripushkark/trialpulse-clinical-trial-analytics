# Architecture

```mermaid
flowchart TD
    A[ClinicalTrials.gov API v2] --> B[src/extract.py]
    B --> C[data/raw/oncology_trials_raw.json]
    C --> D[src/transform.py]
    D --> E[Feature Engineering]
    E --> F[src/risk.py]
    F --> G[data/processed/trialpulse_oncology.csv]
    G --> H[app.py]
    H --> I[Executive KPIs]
    H --> J[Interactive Charts]
    H --> K[Trial Explorer]
    H --> L[Comparable-Trial Narrative]
```

## Design Choices

- **API v2:** current official ClinicalTrials.gov REST interface.
- **Local analytical dataset:** stable, simple, and appropriate for a weekend portfolio MVP.
- **Rule-based scoring:** transparent and auditable; avoids unsupported claims of predictive accuracy.
- **Streamlit:** enables a free, interactive public application using a Python-only stack.
