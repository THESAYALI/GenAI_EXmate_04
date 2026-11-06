# app/records.py
# Day 2: helper functions for ShirdiYatra records
# Author: Sayali Rajendra Pawar | CSE | SJ-50

import json
import os

# Where the notebook (JSON file) is kept
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "sample_records.json")


def load_records():
    """Open the JSON file and return all records as a list."""
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_records(records):
    """Write the list back into the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def search_records(records, keyword):
    """Return records whose name or tip contains the keyword."""
    keyword = keyword.lower()
    found = []
    for r in records:
        if keyword in r["place_or_service"].lower() or keyword in r["rule_or_tip"].lower():
            found.append(r)
    return found


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