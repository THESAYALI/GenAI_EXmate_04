"""Day 2 demo: print all records, search by keyword, count per category.

Run from the project root:  python day02/day02_demo.py
The code itself lives in app/records.py; the data in data/sample_records.json.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import records as db

data = db.load_records()

print(f"All {len(data)} records:")
for i, r in enumerate(db.with_ids(data), start=1):
    cost = "-" if r["cost_inr"] is None else f"Rs {r['cost_inr']}"
    print(f"{r['id']:>2}. [{r['topic']}] {r['place_or_service']} | {r['timing']} | {cost}")

keyword = input("\nSearch keyword: ").strip() or "aarti"
found = db.search(data, keyword)
print(f"{len(found)} match(es) for '{keyword}':")
for r in found:
    print(f"  - {r['place_or_service']} ({r['timing']})")

print("\nCount per category:", db.count_by(data, "topic"))
print("Record #19:", db.get_by_id(data, 19)["place_or_service"])
