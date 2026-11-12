# Day 2 - Hand-entered records and refactor (`records.py` + `cli.py`)

**Project:** ShirdiYatra | **Author:** Sayali Rajendra Pawar | CSE | SJ-50
**Folder:** `day02/` (the real code lives in `app/`, the data in `data/`)

> Copy this file to `day02/README.md` (replace the old one).

---

## Table of contents

1. [What Day 2 is about](#1-what-day-2-is-about)
2. [The actual tasks (and where each one is done)](#2-the-actual-tasks-and-where-each-one-is-done)
3. [Where is every file](#3-where-is-every-file)
4. [How the pieces work together](#4-how-the-pieces-work-together)
5. [The data: `data/sample_records.json`](#5-the-data-datasample_recordsjson)
6. [Step-by-step: set up and run](#6-step-by-step-set-up-and-run)
7. [Code walkthrough, file by file](#7-code-walkthrough-file-by-file)
8. [Behaviours you must know before the demo](#8-behaviours-you-must-know-before-the-demo)
9. [How to do common changes by hand](#9-how-to-do-common-changes-by-hand)
10. [Final checklist](#10-final-checklist)
11. [Troubleshooting](#11-troubleshooting)
12. [Viva / explanation questions](#12-viva--explanation-questions)

---

## 1. What Day 2 is about

On Day 1 you wrote a project card and a small menu. On Day 2 you give the project **real (hand-typed) data** and
organise the code properly:

- **Session 1 (S1):** keep 15-20 records by hand as a list of dictionaries. Print them all, search by keyword,
  count records per category.
- **Session 2 (S2):** move that logic out of one script into a reusable module `app/records.py`, and build a
  menu program `app/cli.py` on top of it. Add `requirements.txt` and a local `.venv`.

In plain words: **Day 2 = a small "database" in a JSON file + helper functions + a menu to use them.**
Nothing is downloaded from the internet on this day.

---

## 2. The actual tasks (and where each one is done)

| # | Task from the sheet | Where it is done | Status |
|---|---|---|---|
| S1 | 15-20 hand-entered records (list of dicts) | `data/sample_records.json` - **20 records** (12 programme + 8 rooms) | Done |
| S1 | Print all records | `day02/day02_demo.py` (loop at the top) | Done |
| S1 | Search by keyword | `day02/day02_demo.py` -> `db.search()` in `app/records.py` | Done |
| S1 | Count per category | `day02/day02_demo.py` -> `db.count_by()` | Done |
| S2 | `app/records.py` with `load_records`, `search`, `count_by`, `get_by_id` | `app/records.py` | Done |
| S2 | `app/cli.py` menu | `app/cli.py` (8 options + exit) | Done |
| S2 | `requirements.txt` | project root `requirements.txt` | Done |
| S2 | `.venv` | create on your own PC (it is git-ignored) | **You must do this** |

Note: the task sheet text was cut off after "requirements.txt". If your sheet lists more Day 2 items, they are
not covered here.

---

## 3. Where is every file

```
GenAI_EXmate_04_clean/
|-- requirements.txt            <- list of libraries (Day 2 item)
|-- .gitignore                  <- ignores .venv/, __pycache__/, .env, data/questions.jsonl
|-- data/
|   `-- sample_records.json     <- the 20 hand-entered records (Day 2 data)
|-- app/
|   |-- __init__.py             <- empty file, makes "app" a package so "from app import records" works
|   |-- records.py              <- Day 2: helper functions (load/search/count/get/add/delete)
|   `-- cli.py                  <- Day 2: the menu program
`-- day02/
    |-- README.md               <- this file
    `-- day02_demo.py           <- Session 1 demo: print all, search, count
```

Why is the code in `app/` and not in `day02/`? The task sheet asks for the path `app/records.py` and
`app/cli.py`. The `day02/` folder only holds the demo script and this README. Later days (3 and 4) re-use the
same `app/records.py`.

---

## 4. How the pieces work together

```
data/sample_records.json
        |
        |  load_records()            (app/records.py)
        v
 list of dicts in memory  --->  search() / count_by() / get_by_id() / filter_by_topic()
        ^         |
        |         +---->  day02/day02_demo.py   (prints, searches, counts)
        |         +---->  app/cli.py            (menu with while-loop)
        |
        +---- add_record() / delete_record()  ->  save_records()  -> writes back to sample_records.json
```

Key idea: **the JSON file is the storage, the list of dicts is the working copy, the functions in
`records.py` are the only place that touch the file.** `cli.py` and `day02_demo.py` never open the JSON
themselves.

---

## 5. The data: `data/sample_records.json`

It is a JSON **list**. Each item is one **record** (a dictionary) with exactly 7 fields:

| Field | Type | Meaning | Example |
|---|---|---|---|
| `topic` | text | Category. Two values on Day 2: `Daily programme`, `Accommodation` | `Accommodation` |
| `place_or_service` | text | Name of the aarti / activity / room type | `Sai Bhakta Niwas - 3 beds attached non-AC` |
| `timing` | text | When it happens, or the stay rule for rooms | `5:15 AM` or `Per day, stay 24-48 hours` |
| `cost_inr` | number or `null` | Price in rupees. `null` when no price applies (aartis are free/unpriced) | `200` |
| `rule_or_tip` | text | Rule, capacity, or tip | `3-5 persons, 1.3 km from temple. Locker deposit 100, chaddar deposit 200` |
| `source_url` | text | Official page the fact came from | `https://sai.org.in/en/accomodations` |
| `checked_on` | text (date) | Date you checked the page | `2026-11-06` |

Counts: **12** `Daily programme` records (Temple Open 4:45 AM ... Shej Aarti 10:00 PM) and **8**
`Accommodation` records (Rs 200 to Rs 900 per day).

Records have **no `id` field** on Day 2. The "id" is simply the **position** in the list (1, 2, 3 ...). That is
what `with_ids()` adds on the fly (see section 7).

---

## 6. Step-by-step: set up and run

Always run commands **from the project root** (the folder that contains `app/`, `data/`, `day02/`).

### 6.1 One-time setup

Windows (PowerShell / VS Code terminal):

```
cd path\to\GenAI_EXmate_04_clean
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Mac / Linux:

```
cd path/to/GenAI_EXmate_04_clean
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You will see `(.venv)` at the start of the terminal line when it is active. Day 2 itself only needs plain
Python (no extra library), but installing `requirements.txt` now saves time on Days 3 and 4.

### 6.2 Run the Session 1 demo

```
python day02/day02_demo.py
```

What happens:

1. Prints `All 20 records:` with number, `[topic]`, name, timing and cost.
2. Asks `Search keyword:`. Type `aarti` (or press Enter - it defaults to `aarti`).
3. Prints the matches. For `aarti` you get 5: Kakad Aarti, Aarti "Shirdi Majhe Pandharpur", Mid-day Aarti,
   Dhoop Aarti, Shej Aarti.
4. Prints `Count per category: {'Daily programme': 12, 'Accommodation': 8}`.
5. Prints `Record #19: Sai Niwas - AC western`.

### 6.3 Run the Session 2 menu

```
python -m app.cli
```

`-m app.cli` (module mode) is needed because `cli.py` does `from app import records`. Running
`python app/cli.py` directly will fail with `ModuleNotFoundError: No module named 'app'`.

Menu:

| Choice | What it does |
|---|---|
| 1 | View all records |
| 2 | Search - asks a keyword, looks in **name and rule/tip** only |
| 3 | Show only `Daily programme` records |
| 4 | Show only `Accommodation` records |
| 5 | Add a record (asks topic, place, timing, cost, tip) - **saved to the JSON file** |
| 6 | Delete a record by its list number - **saved to the JSON file** |
| 7 | Count records per topic |
| 8 | Get one record by its number |
| 0 | Exit |

Sample session:

```
=== ShirdiYatra ===
Enter your name: Sayali
Sai Ram Sayali!

1. View all records ... 0. Exit
Choose: 2
Keyword: shej
1. [Daily programme] Shej Aarti | 10:00 PM | -
     <tip text>
```

---

## 7. Code walkthrough, file by file

### 7.1 `app/records.py` - the helper functions

Top of the file:

- `BASE_DIR` - the project root, worked out from the file's own location (so it works from any folder).
- `DATA_FILE` - path to `data/sample_records.json` (the Day 2 notebook).
- `INGESTED_FILE` - path to `data/records.json` (made on Day 3; not used until then).

| Function | Task name? | What it does |
|---|---|---|
| `load_records(path=None)` | **Required** | Opens the JSON (default: `sample_records.json`) with UTF-8 and returns the list. |
| `search(records, keyword)` | **Required** | Case-insensitive search across **every field value** of every record. Empty keyword returns `[]`. |
| `count_by(records, field="topic")` | **Required** | Returns a dict of counts per value, e.g. `{'Daily programme': 12, 'Accommodation': 8}`. |
| `get_by_id(records, record_id)` | **Required** | Returns the record with that id, or that 1-based position if records have no id; `None` if not found. |
| `with_ids(records)` | helper | Returns copies of the records with an `id` added (keeps an existing id, otherwise 1, 2, 3 ...). |
| `save_records(records)` | helper | Writes the list back to `sample_records.json` (indent 2, `ensure_ascii=False` keeps Hindi/special characters). |
| `search_records(records, keyword)` | used by CLI | Narrower search: keyword must be in `place_or_service` **or** `rule_or_tip`. |
| `filter_by_topic(records, topic)` | used by CLI | Case-insensitive match on `topic`. |
| `add_record(records, topic, place, timing, cost_inr, rule_or_tip)` | used by CLI | Builds a new dict, appends, saves. |
| `delete_record(records, number)` | used by CLI | Removes by 1-based position, saves, returns the removed record (or `None`). |
| `default_data_file()` | Day 3+ | Returns `records.json` if it exists, else `sample_records.json`. Used by Day 4, not Day 2. |

Tiny example in a Python shell:

```python
from app import records as db
data = db.load_records()
len(data)                    # 20
db.count_by(data, "topic")   # {'Daily programme': 12, 'Accommodation': 8}
db.search(data, "shej")      # [ {... Shej Aarti ...} ]
db.get_by_id(data, 19)["place_or_service"]   # 'Sai Niwas - AC western'
```

### 7.2 `app/cli.py` - the menu

- `show(items)` prints a list neatly: `n. [topic] name | timing | cost`, then the tip on the next line.
  Cost `None` prints as `-`, otherwise `Rs <amount>`.
- `main()` asks for a name, loads the data **once**, then runs `while True:` with an `if / elif` chain for the
  choices 1-8 and 0 (break). Anything else prints `Invalid choice`.
- Option 8 wraps `int(input())` in `try/except ValueError` so letters do not crash it.

### 7.3 `day02/day02_demo.py` - Session 1 demo

- Adds the project root to `sys.path` so `from app import records as db` works even though the script is inside
  `day02/`.
- Loops over `db.with_ids(data)` to print each record with its number.
- Uses `input()` for the keyword, then `db.search`, `db.count_by`, `db.get_by_id`.

### 7.4 `requirements.txt`

```
fastapi>=0.110      uvicorn>=0.29       pydantic>=2.0
requests>=2.31      beautifulsoup4>=4.12   lxml>=5.0
pandas>=2.0         scikit-learn>=1.4   pytest>=8.0
```

Day 2 uses none of these. They are for Day 3 (requests, beautifulsoup4, lxml, pytest) and Day 4 (fastapi,
uvicorn, pydantic, pandas, scikit-learn).

---

## 8. Behaviours you must know before the demo

1. **`load_records()` always reads `sample_records.json`** unless you pass a path. So `app/cli.py` always
   works on the 20 hand-entered records, even after Day 3 has created `records.json`.
2. **Add and Delete change the file permanently.** `save_records()` rewrites `sample_records.json`. If you test
   "add" and "delete", you change your Day 2 data (and `git status` will show the file as modified). Delete
   your test record afterwards, or restore with `git checkout data/sample_records.json`.
3. **`search` (demo) vs `search_records` (menu) are different.** `search` looks in all fields (so costs
   such as `200` and the source URLs also match); `search_records` looks only in name and tip.
4. **`add_record` hard-codes** `source_url = https://sai.org.in/en/faq` and `checked_on = 2026-11-06` for every
   new record.
5. **Cost input:** in menu option 5, typing letters for the cost raises `ValueError` and closes the program
   (`int(cost)` is not protected). Option 6 has the same issue for the number to delete.
6. **Numbers are positions.** If you delete record 3, records 4, 5, ... shift up by one.
7. **Run from the project root**, and use `python -m app.cli` for the menu.

---

## 9. How to do common changes by hand

**Add a 21st record by editing the file:** open `data/sample_records.json`, add a comma after the last `}` and
paste a new object with all 7 fields (use `null`, not `None`, for no cost). Run `python day02/day02_demo.py` -
it should now say `All 21 records`.

**Add a new helper function:** write it in `app/records.py` (it takes `records` as first argument and returns a
value - no `input()`/`print()` inside), then call it from `cli.py` or the demo.

**Count by something else:** `db.count_by(data, "source_url")` works for any field name.

**Check the JSON is valid:** `python -c "import json; print(len(json.load(open('data/sample_records.json', encoding='utf-8'))))"`

---

## 10. Final checklist

- [ ] `.venv` created and activated, `pip install -r requirements.txt` finished
- [ ] `data/sample_records.json` has 15-20 records (currently 20)
- [ ] `python day02/day02_demo.py` prints all, finds `aarti`, prints counts
- [ ] `python -m app.cli` opens the menu and every option 1-8 and 0 works
- [ ] `app/records.py` has `load_records`, `search`, `count_by`, `get_by_id`
- [ ] `requirements.txt` exists
- [ ] Add/Delete test records removed again (`git status` shows `sample_records.json` unchanged)
- [ ] Committed and pushed (see the root README, "Push and tag week-1")


   numbers shift up.
8. **Why `python -m app.cli`?** Module mode puts the project root on the import path, so `from app import ...`
   works.
