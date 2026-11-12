# app/records.py
# Day 2: helper functions for ShirdiYatra records
# Functions required by the task: load_records, search, count_by, get_by_id
# (search_records, filter_by_topic, add_record, delete_record are used by app/cli.py)

import json
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
# The hand-entered "notebook" from Day 2
DATA_FILE = os.path.join(BASE_DIR, "data", "sample_records.json")
# Written by app/ingest.py on Day 3 (real data cleaned from data/raw/)
INGESTED_FILE = os.path.join(BASE_DIR, "data", "records.json")


def default_data_file():
    """Day 3+ data (records.json) if it exists, else the Day 2 sample file."""
    return INGESTED_FILE if os.path.exists(INGESTED_FILE) else DATA_FILE


def load_records(path=None):
    """Open the JSON file and return all records as a list."""
    with open(path or DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_records(records):
    """Write the list back into the sample JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def with_ids(records):
    """Copies of the records, each with an 'id' (keeps an existing id, else position 1, 2, 3...)."""
    return [{**r, "id": r.get("id", i)} for i, r in enumerate(records, start=1)]


def search(records, keyword):
    """Case-insensitive keyword search across every field."""
    keyword = keyword.strip().lower()
    if not keyword:
        return []
    return [r for r in records
            if any(keyword in str(value).lower() for value in r.values())]


def search_records(records, keyword):
    """Return records whose name or tip contains the keyword."""
    keyword = keyword.lower()
    found = []
    for r in records:
        if keyword in r["place_or_service"].lower() or keyword in r["rule_or_tip"].lower():
            found.append(r)
    return found


def count_by(records, field="topic"):
    """Count records per value of a field, e.g. {'Daily programme': 12, 'Accommodation': 8}."""
    counts = {}
    for r in records:
        key = r.get(field)
        counts[key] = counts.get(key, 0) + 1
    return counts


def get_by_id(records, record_id):
    """Return the record with this id (or this 1-based position if records have no id), else None."""
    for r in with_ids(records):
        if r["id"] == record_id:
            return r
    return None


def filter_by_topic(records, topic):
    """Return only 'Daily programme' or only 'Accommodation' records."""
    return [r for r in records if r["topic"].lower() == topic.lower()]


def add_record(records, topic, place_or_service, timing, cost_inr, rule_or_tip):
    """Add a new record and save it."""
    new = {
        "topic": topic,
        "place_or_service": place_or_service,
        "timing": timing,
        "cost_inr": cost_inr,
        "rule_or_tip": rule_or_tip,
        "source_url": "https://sai.org.in/en/faq",
        "checked_on": "2026-11-06",
    }
    records.append(new)
    save_records(records)
    return new


def delete_record(records, number):
    """Delete the record by its list number (1, 2, 3...) and save."""
    if 1 <= number <= len(records):
        removed = records.pop(number - 1)
        save_records(records)
        return removed
    return None
