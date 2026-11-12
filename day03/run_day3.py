"""Day 3 runner: download the official pages, then clean them into data/records.json.

Run from the project root (needs internet):  python day03/run_day3.py
The code itself lives in app/fetch.py, app/ingest.py and app/models.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import fetch, ingest

print("Step 1: download pages into data/raw/")
if fetch.main() != 0:
    sys.exit("No page could be downloaded - check your internet connection and try again.")

print("\nStep 2: clean data/raw/ into data/records.json")
sys.exit(ingest.main())
