# ShirdiYatra

**Track:** Travel & culture | **Roll/ID:** SJ-50

## Project card

| Field | Detail |
|---|---|
| **Product** | ShirdiYatra plans a Shirdi visit from the Sansthan's own pages: aarti and darshan timings, which Sansthan rooms fit your group and budget, and how to reach. |
| **User** | A family of 7 from Hyderabad (grandparents included) planning their first 2-day Shirdi trip by train to Kopargaon, who want to stay in Sansthan rooms, not costly hotels. |
| **Problem** | Prices and rules change and appear in several versions (English, Hindi, Marathi pages, older mirror copies), and the site warns about fake look-alike websites. |
| **Data source** | Official Shri Saibaba Sansthan pages (HTML, with tariff tables): `sai.org.in/en/faq`, `sai.org.in/en/daily-programme`, `sai.org.in/en/accomodations` |

## Where things are

Each `dayNN/` folder has its own README with that day's checklist. The shared code lives in `app/`, `data/` and `analysis/` because the task sheet asks for those paths; the day folders point to it.

```
README.md  requirements.txt  .gitignore
day01/  README.md  day01_intro.py  day01_menu.py
day02/  README.md  day02_demo.py          -> code in app/records.py, app/cli.py; data in data/sample_records.json
day03/  README.md  run_day3.py            -> code in app/models.py, app/fetch.py, app/ingest.py
day04/  README.md                         -> code in app/main.py, app/smart_search.py, analysis/explore.py
app/        __init__ records cli models fetch ingest smart_search main
analysis/   explore.py
data/       sample_records.json   raw/ (filled by fetch)   records.json (made by ingest)
tests/      test_ingest.py
```

## Status: done and missing

| Day | Done | Missing |
|---|---|---|
| **D1** | README project card; `day01/day01_intro.py`; `day01/day01_menu.py` | Push to GitHub (nothing is committed yet) |
| **D2** | 20 hand-entered records in `data/sample_records.json`; print all / search / count in `day02/day02_demo.py`; `app/records.py` (`load_records`, `search`, `count_by`, `get_by_id`); `app/cli.py`; `requirements.txt` | Create your own `.venv`. The sheet text is cut off after "requirements.txt", so any later D2 item is unchecked |
| **D3** | `app/models.py` (Record dataclass); `app/fetch.py` (requests, timeouts, error handling, 4 pages); `app/ingest.py` (try/except per row, official-domain check, checked-on date); tests pass on sample HTML | Run `python day03/run_day3.py` with internet to fill `data/raw/` and create `data/records.json`. Fetch and ingest have not been run on the live pages |
| **D4** | `app/main.py` (/health, /records, /records/{id}, /search, POST /questions); `app/smart_search.py` (TF-IDF + cosine); `analysis/explore.py` (3 facts); How to run below | Run the API once on your machine (FastAPI was not installed where this was checked). Commit, push and tag `week-1` |

## How to run

```
python -m venv .venv
.venv\Scripts\activate           # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt

python day01/day01_intro.py
python day01/day01_menu.py
python day02/day02_demo.py
python -m app.cli                # menu: view, search, add, delete, count, get by number
python day03/run_day3.py         # needs internet: fetch pages, then build data/records.json
python analysis/explore.py       # 3 facts with pandas
python -m app.smart_search shej aarti
uvicorn app.main:app --reload    # API docs at http://127.0.0.1:8000/docs
```

Run everything from the project root. After Day 3 has been run, the API, search and analysis use `data/records.json` automatically; before that they use `data/sample_records.json`.

## Push and tag week-1

```
git add .
git commit -m "Days 1-4: ShirdiYatra records, ingest, API and search"
git push -u origin main
git tag week-1
git push origin week-1
```

The remote in this folder is `https://github.com/THESAYALI/GenAI_EXmate_04.git`; your sheet also lists the repo name `sanjivani-sj-50-shirdiyatra`. Check which one your instructor expects.
