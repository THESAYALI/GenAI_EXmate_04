"""analysis/explore.py - print 3 facts about the ShirdiYatra records with pandas (Day 4).

Run from the project root:
    python analysis/explore.py
"""
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from app import records as db


def main():
    path = db.default_data_file()
    df = pd.DataFrame(db.with_ids(db.load_records(path)))
    df["cost_inr"] = pd.to_numeric(df["cost_inr"], errors="coerce")
    print(f"Data file: {Path(path).name}")

    print(f"\nFact 1: {len(df)} records across {df['topic'].nunique()} topics.")
    print(df["topic"].value_counts().to_string())

    priced = df.dropna(subset=["cost_inr"])
    print(f"\nFact 2: {len(priced)} records have a cost ({len(df) - len(priced)} do not).")
    if not priced.empty:
        cheapest = priced.loc[priced["cost_inr"].idxmin()]
        costliest = priced.loc[priced["cost_inr"].idxmax()]
        print(f"  Cheapest : {cheapest['place_or_service']} - Rs {cheapest['cost_inr']:.0f}")
        print(f"  Costliest: {costliest['place_or_service']} - Rs {costliest['cost_inr']:.0f}")
        print(f"  Average  : Rs {priced['cost_inr'].mean():.0f}")

    domains = df["source_url"].map(lambda u: urlparse(str(u)).netloc)
    print(f"\nFact 3: {df['source_url'].nunique()} distinct source pages on {domains.nunique()} domain(s).")
    print(df["source_url"].value_counts().to_string())


if __name__ == "__main__":
    main()
