# Day 3 - Real data: fetch, ingest, model

**Project:** ShirdiYatra | **Author:** Sayali Rajendra Pawar | CSE | SJ-50
**Folder:** `day03/` (the real code lives in `app/`, the downloaded pages in `data/raw/`)

> Copy this file to `day03/README.md` (replace the old one).

---

## Table of contents

1. [What Day 3 is about](#1-what-day-3-is-about)
2. [The actual tasks (and where each one is done)](#2-the-actual-tasks-and-where-each-one-is-done)
3. [Where is every file](#3-where-is-every-file)
4. [The pipeline in one picture](#4-the-pipeline-in-one-picture)
5. [Step-by-step: how to run Day 3](#5-step-by-step-how-to-run-day-3)
6. [IMPORTANT: current state of the repo (read this)](#6-important-current-state-of-the-repo-read-this)
7. [Code walkthrough, file by file](#7-code-walkthrough-file-by-file)
8. [The output: `data/records.json`](#8-the-output-datarecordsjson)
9. [Tests](#9-tests)
10. [Known limits](#10-known-limits)
11. [Final checklist](#11-final-checklist)
12. [Troubleshooting](#12-troubleshooting)
13. [Viva / explanation questions](#13-viva--explanation-questions)

---

## 1. What Day 3 is about

Day 2 used 20 records typed by hand. Day 3 replaces typing with **real data from the official website**:

1. **Fetch** - download pages from `sai.org.in` and save them untouched in `data/raw/`.
2. **Ingest** - read those saved pages, pull out the facts, clean them, and write them in the same record
   format to `data/records.json`.
3. **Model** - describe one record as a Python `dataclass` (`Record`) so every record has the same fields.

Why two separate steps? You download **once** (slow, needs internet, can fail) and can then re-run and fix the
cleaning code **many times offline**, without hitting the website again.

Safety rules built in: timeouts and error handling on every download, `try/except` per row so one bad row never
stops the run, only official `sai.org.in` URLs accepted (the Sansthan warns about fake look-alike sites), and
every record carries a `checked_on` date.

---

## 2. The actual tasks (and where each one is done)

| # | Task from the sheet | Where it is done | Status |
|---|---|---|---|
| S1 | Download real pages into `data/raw/` | `app/fetch.py` writes `data/raw/*.html` + `manifest.json` | Code done; pages are in the repo |
| S1 | `app/ingest.py`: clean raw pages into your fields, `try/except` for bad rows, save `data/records.json` | `app/ingest.py` | Code done and tested; **see section 6** |
| S2 | `Record` dataclass | `app/models.py` | Done |
| S2 | `app/fetch.py` downloads 3+ documents with `requests` (timeouts, error handling) | `app/fetch.py` - **4 pages**: faq, daily-programme, accomodations, how-to-reach-shirdi | Done |
| - | Runner for the whole day | `day03/run_day3.py` | Done |
| - | Tests on sample HTML | `tests/test_ingest.py` | 4 tests, all pass |

Notes from your project:

- The task sheet gives sugarcane URLs; they were swapped for your Sansthan pages (from your project row).
- `how-to-reach-shirdi` is downloaded but **not parsed**. The travel distances come from the FAQ page instead.
- Records from any non-official domain are dropped.

---

## 3. Where is every file

```
GenAI_EXmate_04_clean/
|-- requirements.txt              <- requests, beautifulsoup4, lxml, pytest are needed today
|-- app/
|   |-- models.py                 <- Record dataclass (S2)
|   |-- fetch.py                  <- download pages (S1/S2)
|   `-- ingest.py                 <- clean pages -> records (S1)
|-- data/
|   |-- raw/
|   |   |-- faq.html              <- saved copy of https://sai.org.in/en/faq
|   |   |-- daily_programme.html  <- saved copy of .../daily-programme   (see section 6 about the name)
|   |   |-- accommodations.html   <- saved copy of .../accomodations     (see section 6 about the name)
|   |   |-- how_to_reach.html     <- saved copy of .../how-to-reach-shirdi (not parsed)
|   |   `-- manifest.json         <- log of each download (url, ok, bytes, date)
|   |-- records.json              <- OUTPUT of ingest (the cleaned records)
|   `-- sample_records.json       <- Day 2 data (used only if records.json is missing)
|-- tests/
|   `-- test_ingest.py            <- 4 tests with small fake HTML pages
`-- day03/
    |-- README.md                 <- this file
    `-- run_day3.py               <- runs fetch, then ingest
```

---

## 4. The pipeline in one picture

```
 https://sai.org.in/en/faq
 https://sai.org.in/en/daily-programme            app/fetch.py                     data/raw/
 https://sai.org.in/en/accomodations     ---->   requests.get(timeout)   ---->   *.html  +  manifest.json
 https://sai.org.in/en/how-to-reach-shirdi        is_official() check
                                                                                       |
                                                                                       v
                                                                                 app/ingest.py
                                                         parse_programme  (name line + time line)
                                                         parse_rooms      (tariff table rows)
                                                         parse_faq        (regex: darshan, food, distances)
                                                         try/except on every row, official-domain check
                                                                                       |
                                                                                       v
                                                                          list of Record objects (app/models.py)
                                                                                       |
                                                                                       v
                                                                             data/records.json  (with ids)
```

---

## 5. Step-by-step: how to run Day 3

Run everything **from the project root**. You need **internet** for step 2.

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

### 5.2 Run the whole day with one command

```
python day03/run_day3.py
```

It prints two steps:

```
Step 1: download pages into data/raw/
faq                    saved (xxxxx bytes)
daily-programme        saved (xxxxx bytes)
accomodations          saved (xxxxx bytes)
how-to-reach-shirdi    saved (xxxxx bytes)

4/4 pages saved in data/raw/ on <today's date>

Step 2: clean data/raw/ into data/records.json
Saved NN records to data/records.json
 - Daily programme | Temple Open | 4:45 AM | -
 ...
```

If a page fails you will see `FAILED - timed out` / `HTTP 403` etc. instead of `saved`. As long as **at least
one** page is saved, the run continues to step 2; if none is saved the runner stops with a message.

### 5.3 Or run the two steps separately

```
python -m app.fetch      # only download
python -m app.ingest     # only clean (offline)
```

### 5.4 Check the result

```
python -m app.ingest                                   # prints each record and any warnings
python -c "import json; d=json.load(open('data/records.json', encoding='utf-8')); print(len(d), d[0])"
python -m pytest tests                                 # the 4 tests
```

---

## 6. IMPORTANT: current state of the repo (read this)

I opened the zip and ran the Day 3 code. Three things do **not** match, and you should fix them before
submitting:

### 6.1 The saved files do not match what the current code expects

| | Current `app/fetch.py` / `app/ingest.py` expect | What is actually in `data/raw/` |
|---|---|---|
| Daily programme file | `daily-programme.html` | `daily_programme.html` |
| Rooms file | `accomodations.html` | `accommodations.html` |
| `manifest.json` format | a **list** `[ {"name": "faq", ...}, ... ]` | a **dictionary** `{"faq": {...}, "daily_programme": {...}}` |

The raw files and `records.json` were made by an **earlier version** of the code (commit `b185299`), before
the code was cleaned up. Result: running **only** `python -m app.ingest` right now crashes with
`TypeError: string indices must be integers, not 'str'` (the manifest is a dict, the code expects a list).

### 6.2 The committed `data/records.json` is old

It has **23 records** (12 programme + 11 accommodation), topics are written in lowercase
(`daily programme`, `accommodation`), and it has **no** Darshan / Food / Travel records. The current
`ingest.py` produces those extra topics.

### 6.3 The fix (one command, needs internet)

```
python day03/run_day3.py
```

This re-downloads with the correct names, writes a list-style `manifest.json`, and rebuilds `records.json`
with the current code. Then commit the new `data/raw/*` and `data/records.json`. You can delete the old
`daily_programme.html`, `accommodations.html`, `how_to_reach.html` afterwards (the new names are
`daily-programme.html`, `accomodations.html`, `how-to-reach-shirdi.html`).

In a test copy where I only renamed the files and converted the manifest (no new download), the current
ingest produced **41 records**: 12 Daily programme, 24 Accommodation, 3 Travel, 1 Darshan, 1 Food, plus
14 warnings about skipped rows. Your numbers can differ because the live pages change.

> The root `README.md` and old `day03/README.md` say "not run yet". That is out of date - the pages **were**
> downloaded once. Update the status text when you finish.

---

## 7. Code walkthrough, file by file

### 7.1 `app/models.py` - the `Record` dataclass

```python
@dataclass
class Record:
    topic: str              # "Daily programme", "Accommodation", "Darshan", "Food", "Travel"
    place_or_service: str   # "Kakad Aarti (Morning)", "Shanti Niketan - non-AC room"
    timing: str             # "5:15 AM", "Per day, stay 24-48 hours", "17 km from Shirdi"
    cost_inr: Optional[int] # None if the page lists no amount, 0 if free
    rule_or_tip: str
    source_url: str         # official domain only (sai.org.in)
    checked_on: str         # date the page was downloaded
```

- `to_dict()` - converts to a normal dict (uses `asdict`) so it can be saved as JSON.
- `short()` - one-line text: `topic | name | timing | cost` (`-` for None, `Free` for 0, `Rs N` otherwise).
- Run `python -m app.models` to see the sample line `Daily programme | Kakad Aarti (Morning) | 5:15 AM | -`.

### 7.2 `app/fetch.py` - download

| Item | Meaning |
|---|---|
| `RAW_DIR` | `data/raw/` |
| `OFFICIAL_DOMAIN` | `sai.org.in` |
| `TIMEOUT = (5, 20)` | wait max 5 s to connect and 20 s to read |
| `HEADERS` | sends a `User-Agent` so the site does not treat it as an empty bot |
| `PAGES` | dict `{file name: url}` of the 4 pages |
| `is_official(url)` | true only for `sai.org.in` or `*.sai.org.in` (blocks `sai.org.in.evil.com`) |
| `fetch_page(name, url)` | downloads one page, saves `<name>.html`, **never raises** - returns a log entry `{name, url, fetched_on, ok, bytes, error}` |
| `fetch_all()` | runs `fetch_page` for every page and writes `manifest.json` |
| `main()` | prints one line per page, returns `0` if at least one page saved else `1` |

Errors handled separately: `Timeout`, `HTTPError` (404/403/500), other `RequestException` (no internet, SSL),
and `OSError` (cannot write the file). The site spells the rooms page `accomodations` (one "m") - keep it.

### 7.3 `app/ingest.py` - clean the pages

Main flow in `ingest()`:

1. `load_manifest()` - reads `manifest.json` into a lookup by page name (empty dict if unreadable).
2. For each of the 3 parsed pages (`daily-programme`, `accomodations`, `faq`):
   - file missing -> add a problem message and continue;
   - URL not official -> skip;
   - `checked_on` = the manifest's `fetched_on`, or the file's modified date as a fallback;
   - call the parser inside `try/except` so one broken page does not stop the others.
3. `save()` adds an `id` (1, 2, 3 ...) to each record and writes `data/records.json`.
4. `main()` prints each record and every warning; returns `1` if no record could be built.

The three parsers:

**`parse_programme`** - the page is a list of "name" line followed by "time" line.
`text_lines()` strips `script`/`style` and splits the page into clean text lines. A line that matches the
`TIME_ROW` pattern (e.g. `5:15 AM`, `8:30 - 10:00 PM`, `At Sunset`) is a time; the line **before** it is the
name. If the line before is also a time, that row is reported as a problem. The four main aartis (Kakad,
Mid-day, Dhoop, Shej) get the tip "One of the four main aartis".

**`parse_rooms`** - reads every `<table>`, every `<tr>`; a row needs at least 7 `<td>` cells. It takes
location, room type, description, min capacity, max capacity, rate (and remark), converts numbers with
`to_int()`, marks the room `AC` or `non-AC`, builds the name `Location - kind description`, the tip
`min-max persons. remark`, and the timing `Per day, stay 24-48 hours`. Rows with no rate or capacity raise
`ValueError` -> reported in the problems list and skipped. Exact duplicates are skipped using a `seen` set.

**`parse_faq`** - turns the whole page into one string and runs 5 regular expressions:

| Fact | Topic | Example result |
|---|---|---|
| Darshan opening hours | Darshan | `06:00 AM to 9:30 PM` |
| Prasadalaya (dining hall) hours | Food | `10:00AM to 10:00 PM` |
| Shirdi airport (SAG) distance | Travel | `17 km from Shirdi` |
| Kopargaon railway station distance | Travel | `17 km from Shirdi` |
| Sainagar Shirdi station distance | Travel | `4 km from Shirdi` |

If a pattern is not found (page wording changed) a `faq: could not find ...` problem is logged instead of
crashing.

### 7.4 `day03/run_day3.py`

Adds the project root to `sys.path`, calls `fetch.main()` (stops with a message if nothing downloaded), then
`ingest.main()`. It contains no logic of its own.

---

## 8. The output: `data/records.json`

A JSON list. Each item is a `Record` plus an `id`:

```json
{
  "id": 3,
  "topic": "Daily programme",
  "place_or_service": "Kakad Aarti (Morning)",
  "timing": "5:15 AM",
  "cost_inr": null,
  "rule_or_tip": "One of the four main aartis",
  "source_url": "https://sai.org.in/en/daily-programme",
  "checked_on": "2026-11-12"
}
```

Same fields as Day 2 (plus `id`), so `app/records.py`, the API and the analysis work on it without change.
`default_data_file()` in `records.py` picks `records.json` automatically when it exists.

---

## 9. Tests

`tests/test_ingest.py` uses **small hand-written HTML** shaped like the Sansthan pages (not real downloads):

| Test | Checks |
|---|---|
| `test_programme_rows_and_aarti_tip` | 5 programme rows parsed, `At Sunset` and a time range kept, aarti tip added |
| `test_rooms_skip_bad_rows_and_duplicates` | duplicate row removed; rows with missing rate or bad capacity `x` skipped (2 problems) |
| `test_faq_facts` | darshan, prasadalaya, airport and Sainagar values extracted |
| `test_only_official_domains` | `sai.org.in` and `www.sai.org.in` pass; `sai.org.in.evil.com` and look-alikes fail |

Run: `python -m pytest tests`. All four pass. Passing tests prove the parser logic on small samples; they do
**not** prove the live pages parse perfectly (see next section).

---

## 10. Known limits

1. **Room rows from the live page are not all clean.** In my test run on the saved accommodation page some
   rows came out with wrong names or prices, for example `01. - non-AC ...` with `Rs 5`, `Lockers ... Rs 10`,
   `SD-HALL ... Rs 20`, and names starting with `NON AC - ...`. Reason: the real table has 9 columns (it
   includes a "Room Images" column) and the location name is merged across several rows, but `parse_rooms`
   assumes a fixed 7-column layout. The hand-checked Day 2 file (`sample_records.json`) has the correct
   values (e.g. Sai Bhakta Niwas non-AC Rs 200, Shanti Niketan Rs 200/300, AC rooms Rs 600-900).
   **Open `data/records.json` after running and check the Accommodation rows before you rely on them.**
   A better parser would read the header row and use column names instead of fixed positions.
2. `how-to-reach-shirdi` is saved but not parsed.
3. Parsing depends on the website's current layout and wording; if the Sansthan changes the page, re-run fetch
   and look at the warnings.
4. Only English pages are used (no Hindi/Marathi).

---

## 11. Final checklist

- [ ] `pip install -r requirements.txt` done (needs `requests`, `beautifulsoup4`, `lxml`)
- [ ] `python day03/run_day3.py` run with internet -> 4/4 pages saved
- [ ] `data/raw/` has `faq.html`, `daily-programme.html`, `accomodations.html`, `how-to-reach-shirdi.html`, `manifest.json`
- [ ] `data/records.json` rebuilt with the current code (not the old 23-record file)
- [ ] Spot-checked 3-4 accommodation rows against the website
- [ ] `python -m pytest tests` -> 4 passed
- [ ] Every record has `source_url` on `sai.org.in` and a `checked_on` date
- [ ] Old mismatched files removed, status text in README updated
- [ ] Committed and pushed

---

## 12. Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `FAILED - ConnectionError` / `timed out` | No internet, VPN or firewall | Check network, retry; timeout is 5 s connect / 20 s read |
| `FAILED - HTTP 403` | Site blocked the request | Retry later; the `User-Agent` header is already set |
| `FAILED - SSLError` | Certificate problem on your network | Try another network; do not disable verification in submitted code |
| `TypeError: string indices must be integers` in ingest | Old dictionary-style `manifest.json` | Run `python day03/run_day3.py` to regenerate it (section 6) |
| `... data/raw/daily-programme.html not found (run python -m app.fetch)` | Raw files have the old names | Same fix: run `python day03/run_day3.py` |
| `ModuleNotFoundError: bs4` / `lxml` / `requests` | Libraries not installed in the active venv | Activate `.venv`, `pip install -r requirements.txt` |
| `No records built.` | No raw files found, or all parsers failed | Read the printed problems list |
| `faq: could not find '...'` warning | Page wording changed | Open `faq.html`, adjust the regex in `parse_faq` |
| `pytest` not found | Not installed | `pip install pytest` or use `python -m pytest tests` |

