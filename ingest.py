"""ingest.py - load data/sample_records.json into Record objects and validate them."""
import json
import os
from urllib.parse import urlparse

from app.models import Record

DATA_FILE = os.path.join("data", "sample_records.json")
OFFICIAL_DOMAIN = "sai.org.in"
REQUIRED = ["topic", "place_or_service", "timing", "cost_inr",
            "rule_or_tip", "source_url", "checked_on"]


def is_official(url):
    host = urlparse(url).netloc.lower()
    return host == OFFICIAL_DOMAIN or host.endswith("." + OFFICIAL_DOMAIN)


def load_records(path=DATA_FILE):
    """Return (good_records, problems)."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)

    good, problems = [], []
    for i, item in enumerate(raw, start=1):
        missing = [k for k in REQUIRED if k not in item]
        if missing:
            problems.append(f"Record {i}: missing {', '.join(missing)}")
            continue
        if not is_official(item["source_url"]):
            problems.append(f"Record {i}: not an official source ({item['source_url']})")
            continue
        good.append(Record(**{k: item[k] for k in REQUIRED}))
    return good, problems


def main():
    path = input(f"JSON file [{DATA_FILE}]: ").strip() or DATA_FILE
    try:
        records, problems = load_records(path)
    except FileNotFoundError:
        print("File not found:", path)
        return
    print(f"\nLoaded {len(records)} valid records.")
    for p in problems:
        print("  WARNING:", p)
    if input("Show them? (y/n): ").strip().lower() == "y":
        for r in records:
            print(" -", r.short())


if __name__ == "__main__":
    main()
