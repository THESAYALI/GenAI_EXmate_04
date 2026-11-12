# Day 4 - API, analysis and smart search

**Project:** ShirdiYatra | **Author:** Sayali Rajendra Pawar | CSE | SJ-50
**Folder:** `day04/` (the real code lives in `app/` and `analysis/`)

> Copy this file to `day04/README.md` (replace the old one).

---

## Table of contents

1. [What Day 4 is about](#1-what-day-4-is-about)
2. [The actual tasks (and where each one is done)](#2-the-actual-tasks-and-where-each-one-is-done)
3. [Where is every file](#3-where-is-every-file)
4. [How everything connects](#4-how-everything-connects)
5. [Step-by-step: how to run Day 4](#5-step-by-step-how-to-run-day-4)
6. [The API: every endpoint](#6-the-api-every-endpoint)
7. [Smart search (TF-IDF + cosine)](#7-smart-search-tf-idf--cosine)
8. [Analysis: 3 facts with pandas](#8-analysis-3-facts-with-pandas)
9. [Code walkthrough, file by file](#9-code-walkthrough-file-by-file)
10. [Commit, push and tag `week-1`](#10-commit-push-and-tag-week-1)
11. [What I could and could not verify](#11-what-i-could-and-could-not-verify)
12. [Final checklist](#12-final-checklist)
13. [Troubleshooting](#13-troubleshooting)
14. [Viva / explanation questions](#14-viva--explanation-questions)

---

## 1. What Day 4 is about

Days 2 and 3 gave you clean records. Day 4 makes them **usable by other programs and by people**:

- **Session 1 (S1):** a small web service (API) built with **FastAPI**: health check, list records, get one
  record, search, and a place where a user can post a question.
- **Session 2 (S2):** **pandas** analysis (3 facts about the data) and a **smart search** that ranks records by
  how well they match a question, using TF-IDF and cosine similarity.
- Finish the week: README "How to run", commit, push and tag `week-1`.

---

## 2. The actual tasks (and where each one is done)

| # | Task from the sheet | Where it is done | Status |
|---|---|---|---|
| S1 | FastAPI service: `GET /health`, `GET /records?limit=`, `GET /records/{id}` (404 if missing), `GET /search?q=`, `POST /questions` | `app/main.py` | Code done; **not run in my check** (FastAPI was not installed there) |
| S1 | README "How to run" | root `README.md` (and section 5 below) | Done |
| S2 | `analysis/explore.py` prints 3 facts with pandas | `analysis/explore.py` | Done and run |
| S2 | `app/smart_search.py` ranks records with TF-IDF + cosine, powers `/search` | `app/smart_search.py` | Done and run |
| - | Tag `week-1` | git | A local tag exists already - see section 10 |

---

## 3. Where is every file

```
GenAI_EXmate_04_clean/
|-- requirements.txt            <- fastapi, uvicorn, pydantic, pandas, scikit-learn needed today
|-- .gitignore                  <- ignores data/questions.jsonl (user questions are not committed)
|-- app/
|   |-- main.py                 <- the FastAPI service (S1)
|   |-- smart_search.py         <- TF-IDF + cosine ranking (S2)
|   `-- records.py              <- loads the data (from Day 2/3)
|-- analysis/
|   |-- __init__.py
|   `-- explore.py              <- 3 facts with pandas (S2)
|-- data/
|   |-- records.json            <- used automatically if it exists (Day 3 output)
|   |-- sample_records.json     <- used when records.json is missing (Day 2 data)
|   `-- questions.jsonl         <- created by POST /questions (git-ignored, appears after first use)
`-- day04/
    `-- README.md               <- this file
```

Day 4 has **no script of its own** in `day04/`; the sheet asks for `app/` and `analysis/` paths.

---

## 4. How everything connects

```
          data/records.json  (if exists)         else    data/sample_records.json
                      \                                  /
                       v                                v
                 records.default_data_file()  ->  records.load_records()  ->  with_ids()
                                      |
          +---------------------------+------------------------------+
          v                           v                              v
   analysis/explore.py        app/smart_search.py             app/main.py (FastAPI)
   (pandas, 3 facts)          SmartSearch: TF-IDF matrix      loads RECORDS + SEARCH once at start
                              + cosine similarity                |
                                      ^                          +-- GET  /health
                                      |                          +-- GET  /records?limit=
                                      +--------------------------+-- GET  /records/{id}
                                         used by /search and     +-- GET  /search?q=
                                         POST /questions         +-- POST /questions -> data/questions.jsonl
```

Important: the API loads the records **once when it starts**. If you re-run Day 3 and change
`records.json`, restart `uvicorn` (with `--reload` it restarts when code changes, but not when only the JSON
changes - stop and start it yourself).

---

## 5. Step-by-step: how to run Day 4

Run everything **from the project root**.

### 5.1 Setup (once)

Windows:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Mac / Linux:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`app/main.py` uses the type hint `str | None`, which needs **Python 3.10 or newer**.

### 5.2 Start the API

```
uvicorn app.main:app --reload
```

You should see `Uvicorn running on http://127.0.0.1:8000`. Leave this terminal open.

- Interactive docs (try every endpoint in the browser): **http://127.0.0.1:8000/docs**
- Quick check: **http://127.0.0.1:8000/health**

Stop with `Ctrl + C`.

### 5.3 Run the analysis

```
python analysis/explore.py
```

### 5.4 Try the smart search without the API

```
python -m app.smart_search shej aarti
python -m app.smart_search family room 7 people
```

With no words it searches for `family room`.

---

## 6. The API: every endpoint

Base URL: `http://127.0.0.1:8000`

| Method | Path | Purpose | Notes |
|---|---|---|---|
| GET | `/health` | Is the service alive? | Returns `{"status": "ok", "records": <count>}` |
| GET | `/records?limit=10` | First N records | `limit` 1-100, default 10; out of range -> 422 |
| GET | `/records/{record_id}` | One record by id | Unknown id -> **404** `Record 999 not found` |
| GET | `/search?q=...&limit=5` | Ranked search | `q` required (min 1 char); `limit` 1-20, default 5 |
| POST | `/questions` | Save a visitor's question | Body below; returns **201** |

### Examples

Mac / Linux / Git Bash (`curl`). In Windows PowerShell type `curl.exe` instead of `curl`, or simply use the
`/docs` page, which avoids all quoting problems.

```
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/records?limit=3"
curl http://127.0.0.1:8000/records/3
curl http://127.0.0.1:8000/records/999
curl "http://127.0.0.1:8000/search?q=shej%20aarti&limit=3"
curl -X POST http://127.0.0.1:8000/questions -H "Content-Type: application/json" -d '{"question": "Which rooms fit 7 people?", "asked_by": "Sayali"}'
```

### Responses (shape)

`GET /health`

```json
{"status": "ok", "records": 23}
```

The count is the number of records in the file in use (23 with the current committed `records.json`, 20 with the
sample file, more after you re-run Day 3).

`GET /search?q=shej aarti`

```json
{
  "query": "shej aarti",
  "results": [
    {"id": 12, "topic": "daily programme", "place_or_service": "Shej Aarti",
     "timing": "10:00 PM", "cost_inr": null, "rule_or_tip": "...",
     "source_url": "https://sai.org.in/en/daily-programme", "checked_on": "2026-11-12",
     "score": 0.47}
  ]
}
```

`POST /questions` - body rules (checked by Pydantic):

| Field | Required | Rule |
|---|---|---|
| `question` | yes | 3 to 500 characters |
| `asked_by` | no | up to 80 characters |

Response (201):

```json
{"saved": true, "question": "Which rooms fit 7 people?", "suggested_records": [ {...}, {...}, {...} ]}
```

It appends one JSON line `{"asked_at": "<UTC time>", "question": ..., "asked_by": ...}` to
`data/questions.jsonl`. That file is in `.gitignore`, so questions are never pushed.

### CORS

`app/main.py` allows browser pages served from `http://127.0.0.1:5500` and `http://localhost:5500` (the VS Code
"Live Server" port). A front-end page opened from another port will be blocked by the browser; add that origin
to `allow_origins` in `main.py`.

---

## 7. Smart search (TF-IDF + cosine)

Plain keyword search (Day 2) only checks "does the word appear". Smart search **scores** every record.

**Step by step (what `SmartSearch` does):**

1. For every record, build one text: `topic + place_or_service + timing + rule_or_tip`
   (`record_text()`).
2. `TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)` turns each text into a
   vector of numbers:
   - **TF** (term frequency): how often a word appears in this record;
   - **IDF** (inverse document frequency): rare words across all records count more than common ones;
   - `ngram_range=(1, 2)`: single words and two-word phrases (e.g. `shej aarti`);
   - `stop_words="english"`: ignores `the`, `is`, `for`;
   - `sublinear_tf=True`: repeating a word many times helps less and less.
3. The vectors form a matrix, built **once** in `__init__`.
4. For a question, the same vectorizer turns the query into a vector, and `cosine_similarity` measures the
   angle between it and every record vector. Score 0 = nothing in common, 1 = identical direction.
5. Results are sorted high to low, cut to `top_k`, and **records with score 0 are left out**.

Real output from the current data:

```
$ python -m app.smart_search shej aarti
0.470  #12  Shej Aarti  (10:00 PM)
0.095  #10  Dhoop Aarti  (At Sunset)
0.087  #3  Kakad Aarti (Morning)  (5:15 AM)
0.080  #5  Aarti "Shirdi Majhe Pandharpur"  (6:20 AM)
0.080  #8  Mid-day Aarti  (12:00 PM)

$ python -m app.smart_search family room 7 people
0.176  #20  Dwarawati - noN AC-WESTREN  (...)
0.172  #14  Dwarawati - AC-WESTERN  (...)
0.167  #15  Sai Ashram Bhaktniwas - AC  (...)
```

Limits to mention honestly: it matches **words**, not meaning (a query "cheap stay" will not match "Rs 150"
unless those words are in the text); the group-size question "7 people" is not understood numerically; and
the quality depends on the data (see the room-row caveat in the Day 3 README).

---

## 8. Analysis: 3 facts with pandas

`python analysis/explore.py` reads the same file the API uses and prints:

| Fact | What it computes |
|---|---|
| Fact 1 | Number of records and how many per `topic` (`value_counts`) |
| Fact 2 | How many records have a cost; cheapest, costliest and average room price |
| Fact 3 | Number of distinct source pages and domains; records per source page |

Real output with the current committed `data/records.json`:

```
Data file: records.json

Fact 1: 23 records across 2 topics.
daily programme    12
accommodation      11

Fact 2: 11 records have a cost (12 do not).
  Cheapest : Sai Udyan - non AC - Rs 150
  Costliest: Dwarawati - AC-WESTERN - Rs 900
  Average  : Rs 427

Fact 3: 2 distinct source pages on 1 domain(s).
https://sai.org.in/en/daily-programme    12
https://sai.org.in/en/accomodations      11
```

These numbers **change** after you re-run Day 3 (more topics, more records). Re-run `explore.py` and use the
new output in your write-up. The 12 records "without a cost" are the aartis - they have no price, which is
expected.

---

## 9. Code walkthrough, file by file

### 9.1 `app/main.py`

| Part | What it does |
|---|---|
| `QUESTIONS_FILE` | `data/questions.jsonl` |
| `RECORDS = load_default()` | loads records (with ids) once at start-up |
| `SEARCH = SmartSearch(RECORDS)` | builds the TF-IDF matrix once at start-up |
| `FastAPI(title=..., version="0.1.0")` | the app object; `uvicorn app.main:app` means "file `app/main.py`, object `app`" |
| `CORSMiddleware` | allows the Live Server origins (section 6) |
| `QuestionIn` | Pydantic model; validates the POST body (3-500 chars, optional `asked_by`) |
| `health()` | status + record count |
| `list_records(limit)` | `RECORDS[:limit]`; `Query(10, ge=1, le=100)` validates the range |
| `get_record(record_id)` | loops through `RECORDS`, raises `HTTPException(404)` if no id matches |
| `search(q, limit)` | `SEARCH.search(q, top_k=limit)` wrapped as `{query, results}` |
| `post_question(payload)` | appends a JSON line, returns `201` with 3 suggested records |

### 9.2 `app/smart_search.py`

- `TEXT_FIELDS` - the four fields combined for searching.
- `record_text(record)` - joins them into one string.
- `SmartSearch.__init__` - fits the vectorizer and builds the matrix.
- `SmartSearch.search(query, top_k=5)` - returns copies of records plus a rounded `score`; returns `[]` for an
  empty query.
- `load_default()` - `records.default_data_file()` -> `load_records()` -> `with_ids()`.
- Bottom block - the command-line test (`python -m app.smart_search <words>`).

### 9.3 `analysis/explore.py`

Adds the project root to `sys.path`, loads the data into a pandas `DataFrame`, converts `cost_inr` to numbers
(`errors="coerce"` turns bad values into NaN), then prints the three facts using `value_counts`, `dropna`,
`idxmin`, `idxmax`, `mean`, `nunique`, and `urlparse` to get the domain.

### 9.4 Dependencies used today

`fastapi` (framework), `uvicorn` (server), `pydantic` (validation), `pandas` (analysis), `scikit-learn`
(TF-IDF, cosine).

---

## 10. Commit, push and tag `week-1`

State of the git repo I found in the zip:

- Branch `main`, latest commit `61f655a` "Clean reorganised version: Days 1-4 ShirdiYatra".
- A **local tag `week-1` already exists** and points to `61f655a`; `origin/main` is also at `61f655a`.
- Remote: `https://github.com/THESAYALI/GenAI_EXmate_04.git`. Your sheet also lists the repo name
  `sanjivani-sj-50-shirdiyatra` - check which one your instructor expects.
- `git status` showed modified files (`.vscode/settings.json`, `app/cli.py`, `data/raw/*`, `data/records.json`,
  `data/sample_records.json`) that are **not committed yet**.

When your work is final (after re-running Day 3, section 6 of the Day 3 README):

```
git add .
git commit -m "Days 1-4: ShirdiYatra records, ingest, API and search"
git push -u origin main
```

Then make sure the tag points at the **final** commit. If `week-1` still points at the older commit, move it:

```
git tag -f week-1
git push origin week-1 --force
```

(Use `--force` only for this tag, and only if the tag has not been graded yet.) If the tag is already right:

```
git push origin week-1
```

Check on GitHub: the repo shows the latest commit and **Tags -> week-1**.

Do not commit `.venv/` - it is in `.gitignore`. (The zip you shared contained a large `.venv`; delete it
before zipping again to keep the file small.)

---

## 11. What I could and could not verify

| Item | Result |
|---|---|
| `python -m app.smart_search ...` | Ran, output shown above |
| `python analysis/explore.py` | Ran, output shown above |
| `python day02/day02_demo.py` | Ran |
| Day 3 tests (4) | All passed |
| `uvicorn app.main:app` / endpoints | **Not run** - FastAPI is not installed in my environment. Section 6 comes from reading the code, so run it once on your PC and try `/docs` |

---

## 12. Final checklist

- [ ] `pip install -r requirements.txt` finished with no error
- [ ] `uvicorn app.main:app --reload` starts; `/docs` opens
- [ ] `/health` returns `status: ok`
- [ ] `/records?limit=3` returns 3 records
- [ ] `/records/999` returns 404
- [ ] `/search?q=shej aarti` returns Shej Aarti first
- [ ] `POST /questions` returns 201 and creates `data/questions.jsonl`
- [ ] `python analysis/explore.py` prints 3 facts (re-run after Day 3 refresh)
- [ ] `python -m app.smart_search shej aarti` works
- [ ] README "How to run" is correct
- [ ] Final commit pushed, tag `week-1` pushed and visible on GitHub

---

## 13. Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: fastapi` / `sklearn` / `pandas` | venv not active or install skipped | Activate `.venv`; `pip install -r requirements.txt` |
| `Error loading ASGI app. Could not import module "app.main"` | Wrong folder | `cd` to project root, then run uvicorn |
| `TypeError: unsupported operand type(s) for \|` | Python older than 3.10 | Use Python 3.10+ |
| Port 8000 already in use | Another server running | `uvicorn app.main:app --reload --port 8001` |
| `/health` shows old record count | API started before `records.json` changed | Stop and restart uvicorn |
| `/search` returns empty `results` | No query word occurs in any record (score 0 is dropped) | Try other words, e.g. `aarti`, `room`, `AC` |
| 422 Unprocessable Entity | Missing `q`, `limit` out of range, or question shorter than 3 chars | Fix the request (see section 6) |
| Browser front-end blocked (CORS error) | Page not served from port 5500 | Add its origin to `allow_origins` in `main.py` |
| `ValueError: empty vocabulary` | Records list is empty or text is all stop words | Check that the data file has records |
| `git push` rejected | Remote has commits you do not have | `git pull --rebase origin main`, then push |

