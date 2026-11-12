# Day 3 - Real data: fetch, ingest, model

| Task | Where | Status |
|---|---|---|
| S1: download real pages into `data/raw/` | `../app/fetch.py` writes `../data/raw/*.html` | Code done, **not run yet** (needs internet) |
| S1: `app/ingest.py` cleans raw pages into your fields, try/except for bad rows, saves `data/records.json` | `../app/ingest.py` | Code done and tested on sample HTML; **records.json not made yet** |
| S2: Record dataclass | `../app/models.py` | Done |
| S2: `app/fetch.py` downloads 3+ documents with requests (timeouts, error handling) | `../app/fetch.py` (4 pages: faq, daily-programme, accomodations, how-to-reach-shirdi) | Done, not run on live pages |

Notes:
- The task sheet gives sugarcane URLs; they were swapped for the Sansthan pages from your project row.
- `how-to-reach-shirdi` is downloaded but not parsed yet. Distances come from the FAQ page instead.
- Each record gets a `checked_on` date from `data/raw/manifest.json`; records from non-official domains are dropped.

Run from the project root (internet needed): `python day03/run_day3.py`
Tests: `python -m pytest tests`
