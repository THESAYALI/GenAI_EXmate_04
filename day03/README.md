# Day 3: Files, Errors, Real Data + Classes & APIs

**Project:** ShirdiYatra · **Student:** Sayali Rajendra Pawar (CSE, SJ-50)
**Day:** D3 · Fri 6 Nov (submitted and fixed on Thu 12 Nov 2026)
**Repo:** https://github.com/THESAYALI/GenAI_EXmate_04
**Final commit for D3:** `b185299`

---

## 1. The task, word by word

The D3 task has two steps.

> **S1:** download a first real slice of your ShirdiYatra data from `https://sai.org.in/en/faq` and `https://sai.org.in/en/daily-programme` into `data/raw/`; `app/ingest.py` cleans it into your fields (`topic, place_or_service, timing, cost_inr, rule_or_tip, source_url`) with try/except for bad rows and saves `data/records.json`.
>
> **S2:** Record dataclass in `app/models.py`; `app/fetch.py` downloads 3+ documents with requests (timeouts, error handling).

| Phrase in the task | What it means | Where it is done |
|---|---|---|
| "download a first real slice" | Get some real pages from the official site, not made-up data | `app/fetch.py` |
| `data/raw/` | A folder for untouched downloads | `data/raw/*.html` |
| "cleans it into your fields" | Read messy HTML and keep only the six fields | `app/ingest.py` |
| "try/except for bad rows" | One broken row must not stop the program | `ingest.py`, inside the row loops |
| "saves `data/records.json`" | The cleaned output is one JSON file | `data/records.json` |
| "Record dataclass" | A small Python class that holds one record | `app/models.py` |
| "downloads 3+ documents" | At least three pages must download | `fetch.py` (we download 4) |
| "requests" | The Python library that makes HTTP calls | `import requests` |
| "timeouts, error handling" | Never wait forever; survive failures | `TIMEOUT`, retries, `try/except` |

### The four ideas behind the title

1. **Files:** reading from and writing to disk (`Path.write_text`, `read_text`, folders).
2. **Errors:** expecting failures (no internet, a 404, a bad row) and handling them calmly.
3. **Real data:** using the official Sansthan website instead of invented samples.
4. **Classes & APIs:** a `Record` class to hold data, and `requests` to call the website over HTTP (the "API" part: your program talks to a server instead of a person using a browser).

---

## 2. The data flow

```
 sai.org.in (internet)
        |
        |  app/fetch.py   (requests: timeout, retries, error handling)
        v
 data/raw/faq.html
 data/raw/daily_programme.html
 data/raw/how_to_reach.html
 data/raw/accommodations.html
 data/raw/manifest.json          <- what was downloaded, when, how big
        |
        |  app/ingest.py  (BeautifulSoup, try/except per row, dedupe)
        v
 data/records.json               <- 23 clean Record objects
        ^
        |  app/models.py  (Record dataclass defines the shape)
```

Raw data stays untouched so that you can always re-run `ingest.py` if the parsing logic changes.

---

## 3. Final folder layout

```
GenAI_EXmate_04/
├── README.md
├── app/
│   ├── cli.py          (D2)
│   ├── records.py      (D2)
│   ├── models.py       (D3)  Record dataclass
│   ├── fetch.py        (D3)  download pages
│   └── ingest.py       (D3)  clean pages into records
├── data/
│   ├── sample_records.json   (D2)
│   ├── raw/                  (D3)
│   │   ├── faq.html
│   │   ├── daily_programme.html
│   │   ├── how_to_reach.html
│   │   ├── accommodations.html
│   │   └── manifest.json
│   └── records.json          (D3)
└── day03/README.md           (this file)
```

`app/` and `data/` sit at the **repo root** because the D2 checker asked for that, and the D3 checker also found files there.

---

## 4. `app/models.py` explained

```python
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Record:
    topic: str
    place_or_service: str
    timing: str
    cost_inr: Optional[int]
    rule_or_tip: str
    source_url: str
    checked_on: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
```

| Part | Explanation |
|---|---|
| `@dataclass` | Python writes `__init__`, `__repr__` and `__eq__` for you, so the class is just a list of fields |
| `topic: str` | Category, such as `daily programme` or `accommodation` |
| `place_or_service: str` | Name of the ritual, place or room type |
| `timing: str` | A time (`5:15 AM`) or a stay rule |
| `cost_inr: Optional[int]` | Rupees per day; `Optional` means it can be `None` (daily rituals are free) |
| `source_url: str` | The official page the fact came from |
| `checked_on: str = ""` | ISO date of the download; has a default, so it is optional when creating a record |
| `to_dict()` | Turns the object into a plain dictionary so `json.dumps` can save it |

**Why a class instead of a plain dictionary?** A class gives every record the same fields, catches typos in field names, and makes the code easier to read (`record.cost_inr` instead of `record["cost_inr"]`).

---

## 5. `app/fetch.py` explained

### 5.1 Settings at the top

| Constant | Value | Why |
|---|---|---|
| `BASE_DIR` | Parent of `app/` | So paths work wherever you run the script |
| `RAW_DIR` | `BASE_DIR / "data" / "raw"` | Where downloads go |
| `SOURCES` | 4 names and URLs | The pages to download |
| `ALLOWED_DOMAIN` | `sai.org.in` | Only official pages are allowed |
| `HEADERS` | A `User-Agent` | Tells the website who is calling |
| `TIMEOUT` | `(5, 15)` | 5 seconds to connect, 15 seconds to read |
| `RETRIES` | `3` | Try each page up to 3 times |

### 5.2 `download(name, url, session)`

1. **Domain check:** `urlparse(url).netloc` must equal `sai.org.in`, otherwise it returns `domain not allowed`.
2. **Retry loop** (`for attempt in range(1, RETRIES + 1)`):
   - `session.get(url, headers=HEADERS, timeout=TIMEOUT)` sends the request.
   - `raise_for_status()` turns HTTP errors (404, 500) into exceptions.
   - The content is decoded as UTF-8 with `errors="replace"`, so odd characters do not crash it.
   - An empty page is treated as an error.
   - The page is saved to `data/raw/<name>.html`.
3. **Specific error handling:**

| Exception | Meaning | What the code does |
|---|---|---|
| `Timeout` | Server too slow | Records `timeout`, waits, retries |
| `HTTPError` 4xx | Request is wrong (for example 404) | Stops retrying, because it will not fix itself |
| `HTTPError` 5xx | Server problem | Retries |
| `ConnectionError` | No internet or DNS problem | Retries |
| Other `RequestException`, `OSError`, `ValueError` | Anything else, including disk errors and empty pages | Records the message, retries |

4. It **never raises**: it always returns a result dictionary (`ok: True` or `ok: False` with an error).
5. `time.sleep(attempt)` waits 1, 2, then 3 seconds between attempts (a simple back-off).

### 5.3 `fetch_all()`
- Creates `data/raw/` if missing (`mkdir(parents=True, exist_ok=True)`).
- Uses one `requests.Session`, which reuses the connection and is faster.
- Writes `manifest.json`.

### 5.4 The exit code
`sys.exit(0 if len(ok) >= 3 else 1)`: success only if 3 or more documents downloaded, which matches the task ("3+ documents").

### 5.5 What a real run printed

```
Downloading faq ...
Downloading daily_programme ...
Downloading how_to_reach ...
Downloading accommodations ...

Downloaded 4/4 documents
  faq: OK (61247 bytes)
  daily_programme: OK (51401 bytes)
  how_to_reach: OK (73970 bytes)
  accommodations: OK (97375 bytes)
```

### 5.6 `manifest.json` structure

```json
{
  "faq": {
    "name": "faq",
    "url": "https://sai.org.in/en/faq",
    "ok": true,
    "file": "faq.html",
    "bytes": 61247,
    "fetched_on": "2026-11-12"
  }
}
```

It records, for every page, the URL, the saved file name, the size and the date. `ingest.py` reads `fetched_on` from it to fill `checked_on`.

---

## 6. `app/ingest.py` explained

### 6.1 Main parts

| Function | Job |
|---|---|
| `to_int(text)` | Finds the first number in a string (`"₹ 900"` becomes `900`) |
| `parse_daily(html, url, checked_on)` | Extracts the 12 daily programme records |
| `parse_rooms(html, url, checked_on)` | Extracts the room records from the tariff tables |
| `read_raw(name)` | Reads one raw file safely; returns `None` if it cannot be read |
| `main()` | Runs both parsers, writes `data/records.json`, prints counts |

### 6.2 How the daily programme is parsed
On the page, each ritual is a list item (`<li>`) with a clock icon, a title and a time. The parser:
1. Looks for every `<li>` that contains an image whose `src` includes `clock-`.
2. Skips an `<li>` that contains another `<li>` (so only the innermost items count).
3. Splits the item text into lines: the **first line is the title**, the **last line is the time**.
4. Creates a `Record` with `topic = "daily programme"`, `cost_inr = None`, and a reminder in `rule_or_tip`.

### 6.3 How the rooms are parsed
1. Finds every `<table>` whose header contains "Rate per day".
2. **Maps columns by header name** (location, room type, description, min, max, rate, remark) instead of fixed positions, so a small layout change does not break it.
3. For each row:
   - Reads the rate with `to_int`; a **row with no rate is skipped**.
   - Splits `Dwarawati (Distance from temple-0.5Km)` into the name `Dwarawati` and the distance `Distance from temple-0.5Km`.
   - Builds the tip: `Capacity 3-5. <description>. <remark>. <distance>.`
4. **Deduplicates** using a key of normalized name, min, max and rate. The normalization removes spaces and punctuation and treats `Bhaktiniwas` and `Bhaktniwas` as the same spelling.

### 6.4 Error handling in `ingest.py`

| Where | Protection |
|---|---|
| Each daily item | `try/except`; prints `skipped bad daily row` |
| Each room row | `try/except`; prints `skipped bad room row` |
| Reading a file | `read_raw` catches `OSError` |
| Reading `manifest.json` | Falls back to today's date if missing or broken |
| No records at all | Prints a message and exits with code 1 |

### 6.5 A real run

```
daily programme: 12 records
accommodation: 11 records
Saved 23 records to data\records.json
```

---

## 7. The complete data: all 23 records

### 7.1 Daily programme (12 records)

Source: https://sai.org.in/en/daily-programme · cost: none (`null`)

| # | `place_or_service` | `timing` |
|---|---|---|
| 1 | Temple Open | 4:45 AM |
| 2 | Bhupali | 5:00 AM |
| 3 | Kakad Aarti (Morning) | 5:15 AM |
| 4 | Mangal Snaan In Samadhi Mandir | 5:50 AM |
| 5 | Aarti "Shirdi Majhe Pandharpur" | 6:20 AM |
| 6 | Darshan Begins In Samadhi Mandir | 6:25 AM |
| 7 | Dhuni Pooja With Rice and Ghee In Dwarkamai | 11:30 AM |
| 8 | Mid-day Aarti | 12:00 PM |
| 9 | Pothi (Devotional Reading / Study) In Samadhi Mandir | 4:00 PM |
| 10 | Dhoop Aarti | At Sunset |
| 11 | Devotional Songs in Samadhi Mandir & Cultural Programms | 8:30 - 10:00 PM |
| 12 | Shej Aarti | 10:00 PM |

Notes on reading these:
- **Darshan begins at 6:25 AM** and the temple opens at 4:45 AM, so early morning is the busiest and best time to reach.
- **Dhoop Aarti is "At Sunset"**, so its clock time changes through the year. This is why `timing` is a string, not a time object.
- The site's spelling ("Programms") is kept exactly as published.

### 7.2 Accommodation (11 records)

Source: https://sai.org.in/en/accomodations · `timing` for every row is "Rooms are allotted for a minimum of 24 and maximum of 48 hours".

| # | `place_or_service` | `cost_inr` (₹/day) | Capacity | Distance from temple |
|---|---|---|---|---|
| 1 | Sai Bhakta Niwas - NON AC | 200 | 3-5 | 1.3 km |
| 2 | Dwarawati - AC-WESTERN | 900 | 3-5 | 0.5 km |
| 3 | Sai Ashram Bhaktniwas - AC | 600 | 3-5 | 1.7 km |
| 4 | Sai Niwas - AC Western | 800 | 2-2 | 3.2 km |
| 5 | Sai Udyan - Non AC | 250 | 10-15 | 250 m |
| 6 | Shanti Niketan - Non AC | 200 | 3-4 | 100 m |
| 7 | Bus Stand - Non AC | 300 | 4-6 | 450 m |
| 8 | Dwarawati - noN AC-WESTREN | 500 | 3-5 | 0.5 km |
| 9 | Sai Udyan - non AC | 150 | 8-10 | 250 m |
| 10 | Shanti Niketan - non AC | 300 | 6-7 | 100 m |
| 11 | Bus Stand - NON AC | 500 | 10-10 | 450 m |

Notes on reading these:
- **Capacity "3-5"** means the room is meant for at least 3 and at most 5 people. "Floor mattress will be provided for extra persons" appears in many tips.
- **Sai Niwas (₹800)** has capacity 2-2, and an extra person costs ₹200.
- The **Sai Bhakta Niwas** tip also lists small charges (locker deposit ₹100, chaddar deposit ₹200, mattress ₹10, chaddar ₹10).
- The odd spellings such as `noN AC-WESTREN` are copied from the website; they are not typing mistakes in the code.
- For a family of 7, one Sai Udyan or Bus Stand room (capacity up to 10 to 15) is a cheaper option than two 3-5 rooms, and it shows why `plan_sansthan_rooms` is needed.

### 7.3 One record as it looks in `records.json`

```json
{
  "topic": "accommodation",
  "place_or_service": "Dwarawati - AC-WESTERN",
  "timing": "Rooms are allotted for a minimum of 24 and maximum of 48 hours",
  "cost_inr": 900,
  "rule_or_tip": "Capacity 3-5. 3 beds AC room. Floor mattress will be provided for extra persons. Distance from temple-0.5Km.",
  "source_url": "https://sai.org.in/en/accomodations",
  "checked_on": "2026-11-12"
}
```

### 7.4 What the pages contain but the records do not

| Page | Why it is not parsed |
|---|---|
| `faq.html` | Downloaded (task S1 asks for it) but its question-and-answer content is not extracted yet; planned for a later day |
| `how_to_reach.html` | Downloaded for the train and road plan; not parsed yet |
| Rooms with no rate (for example the 6-bed AC room at Sai Bhakta Niwas) | Cannot be priced |
| Lockers (about ₹10) | Not rooms; they would always win a "cheapest" search |
| Large halls | Sleep 15 to 50 people; the table rows do not parse into the rate column |
| Accommodation rules (24 to 48 hours, no single person, ID proof) | Stored inside the `timing` field as the stay rule, and in the rules section of the README |

---

## 8. The accommodation rules that affect planning

These are published on the same page and matter for the wow feature:

1. Rooms are allotted for a **minimum of 24 and maximum of 48 hours**.
2. **No room for a single person** (halls exist at Sai Bhakta Niwas and Sai Dharmshala).
3. Couples need valid documents showing their marital status.
4. ID proof (PAN, Aadhaar, driving license) is needed for **all** members; online booking requires an Aadhaar photocopy.
5. Male and female friends are not allotted a shared room; brothers and sisters need proof of relationship.
6. Online rooms are allotted up to three hours before the booking time, subject to availability.
7. Late checkout charges the next full day.

---

## 9. Why D3 was "Partial", and how it was fixed

### 9.1 The checker's message

```
Partial
day03/ has fetch.py, ingest.py and models.py, but no data/raw files
and no records.json were committed.
Found: app/ingest.py, app/models.py, app/fetch.py
Missing: data/records.json
```

**Meaning:** the code existed, but nobody had run it and committed the output. The checker wants the *results* (the downloaded pages and the cleaned JSON), not just the scripts.

### 9.2 What went wrong on the way (and the fix)

| Problem seen | Cause | Fix |
|---|---|---|
| `can't open file '...day03\app\fetch.py'` | Running from the wrong folder | Run from the repo root: `python app\fetch.py` |
| `source : The term 'source' is not recognized` | `source` is a Linux/Mac command | On Windows use `.venv\Scripts\activate` |
| `ModuleNotFoundError: No module named 'app'` | Running `python -m app.cli` from the wrong folder or with a missing `app/` | Run from the repo root |
| Two `.venv` folders | A second venv was created inside `day03/` | Deleted `day03\.venv`; keep one at the repo root |
| `can't open file 'app\ingest.py'` | `ingest.py` was saved in `day03/`, not `app/` | `move day03\ingest.py app\` (same for `models.py`) |
| 19 accommodation records with duplicates | The same room appeared in several tabs, with the distance in the name and different spellings | Strip the distance, normalize the name, then dedupe → 11 records |
| `IndentationError: unexpected indent` | A pasted block had extra leading spaces | Replaced the whole `parse_rooms` function in one piece |
| `warning: LF will be replaced by CRLF` | Windows line-ending note from Git | Harmless; ignore it |
| Files shown as `deleted: day03/...` | The old copies were moved to `app/` | `git add -A app data day02 day03` records the move |

### 9.3 The final Git steps

```powershell
git add -A app data day02 day03
git status --short
git commit -m "D3: move code to app/, add raw pages and records.json"
git push
```

Result: `16 files changed`, pushed as `40230c4..b185299  main -> main`.

---

## 10. How to test that D3 works

| Test | Command | Expected |
|---|---|---|
| Download | `python app\fetch.py` | `Downloaded 4/4 documents` |
| Files exist | `dir data\raw` | 4 HTML files and `manifest.json` |
| Clean | `python app\ingest.py` | `Saved 23 records to data\records.json` |
| Count | `python -c "import json; print(len(json.load(open('data/records.json', encoding='utf-8'))))"` | `23` |
| Error handling (offline) | Turn off Wi-Fi and run `fetch.py` | Retry messages, then `FAILED`, no crash, exit code 1 |
| Error handling (bad URL) | Add a fake URL to `SOURCES` | `FAILED (http error 404)` or `domain not allowed` for other domains |
| Bad row | Edit one raw HTML row to remove the time | `skipped bad daily row`; other rows still saved |

---

## 11. Likely viva questions and answers

**Q1. Why do you save raw pages instead of parsing directly?**
So parsing can be repeated and improved without hitting the website again, and so you have proof of what the page said on the day it was checked.

**Q2. What is a timeout and why two values?**
It limits waiting. `(5, 15)` means 5 seconds to connect and 15 seconds to read the response. Without it, a hung server would freeze the program.

**Q3. Why do you not retry on a 404?**
A 4xx error means the request is wrong, so repeating it will not help. A 5xx error is a server fault and may be temporary, so it is retried.

**Q4. Why a dataclass?**
It gives every record a fixed, named set of fields with almost no code, and `asdict` converts it to JSON-ready data.

**Q5. Why is `cost_inr` sometimes `null`?**
Daily rituals have no price. `Optional[int]` allows `None`, and JSON stores it as `null`.

**Q6. Why map table columns by header name?**
If the site adds or reorders a column, a header-based lookup still finds the right one; fixed positions would silently read the wrong data.

**Q7. How do you avoid duplicates?**
A key made of the normalized name, min capacity, max capacity and rate. A room already seen is skipped.

**Q8. Why only `sai.org.in`?**
It is the official source, so the data is trustworthy, and the allow-list also stops the program from downloading from unknown sites.

**Q9. Why store `checked_on`?**
Prices and timings change. The date tells the user how fresh each fact is.

**Q10. What would break your parser?**
A redesign of the Sansthan site (different tags or table headers). The `try/except` and the "no records" exit code make such a failure visible instead of silent.

---

## 12. What D3 leaves ready for the next days

- `data/records.json` is the single source of truth for the CLI and the planner.
- The room records already carry `cost_inr`, capacity and distance, which is all `plan_sansthan_rooms` needs: choose a mix of rooms whose capacities cover 7 people at the lowest total daily cost, with no single-person rooms and a 24 to 48 hour stay.
- The daily programme records can feed the **one-day Shirdi timeline card**, with the train arrival at Kopargaon marked on it.
- `faq.html` and `how_to_reach.html` are already downloaded for the "how to reach" and rules features.

---

## 13. Quick summary

| Item | Status |
|---|---|
| `app/models.py`: `Record` dataclass | Done |
| `app/fetch.py`: 4 pages, timeouts, retries, error handling | Done |
| `app/ingest.py`: try/except, dedupe, saves JSON | Done |
| `data/raw/`: 4 HTML files + `manifest.json` | Committed |
| `data/records.json`: 23 records (12 daily + 11 rooms) | Committed |
| Pushed to GitHub | Yes, commit `b185299` |
| Checker | Re-scans every morning; D3 should turn OK |
