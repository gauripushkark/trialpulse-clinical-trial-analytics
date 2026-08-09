"""Create a normalized trial-country dataset for geographic BI analysis."""

from pathlib import Path

import pandas as pd


INPUT_PATH = Path("data/processed/trialpulse_gold_dataset.csv")
OUTPUT_PATH = Path("data/processed/trialpulse_trial_countries.csv")


def build_trial_country_export(df: pd.DataFrame) -> pd.DataFrame:
    """Explode pipe-delimited trial countries into one row per trial-country."""

    geo = df[
        [
            "nct_id",
            "countries",
        ]
    ].copy()

    geo["country"] = geo["countries"].fillna("").str.split("|")
    geo = geo.explode("country")

    geo["country"] = geo["country"].str.strip()

    geo = geo[
        geo["country"].notna()
        & geo["country"].ne("")
    ].copy()

    geo = geo[
        [
            "nct_id",
            "country",
        ]
    ].drop_duplicates()

    return geo.reset_index(drop=True)


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    geo = build_trial_country_export(df)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    geo.to_csv(OUTPUT_PATH, index=False)

    print(f"Trials in source: {df['nct_id'].nunique():,}")
    print(f"Trial-country rows: {len(geo):,}")
    print(f"Trials with geography: {geo['nct_id'].nunique():,}")
    print(f"Distinct countries: {geo['country'].nunique():,}")
    print(f"Saved geography dataset to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()