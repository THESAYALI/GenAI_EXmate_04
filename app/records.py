import json
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sample_records.json"


def load_records(path=DATA_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def search(records, keyword):
    keyword = keyword.lower()
    return [
        r for r in records
        if keyword in str(r.get("topic", "")).lower()
        or keyword in str(r.get("place_or_service", "")).lower()
        or keyword in str(r.get("rule_or_tip", "")).lower()
    ]


# ---- ADD THESE TWO ----
def count_by(records, field):
    """Count records per value of a field, e.g. count_by(records, "topic")."""
    counts = {}
    for r in records:
        key = r.get(field, "unknown")
        counts[key] = counts.get(key, 0) + 1
    return counts


def get_by_id(records, record_id):
    """Return the record whose 'id' matches, or None."""
    for r in records:
        if str(r.get("id")) == str(record_id):
            return r
    return None