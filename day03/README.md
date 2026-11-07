# Day 03 – ShirdiYatra: Real Data Download, Cleaning & Record Model

## Project
ShirdiYatra helps plan a Shirdi visit using official Shri Saibaba Sansthan pages (sai.org.in): aarti and darshan timings, Sansthan rooms for groups and budget, and how to reach Shirdi.

**Target user:** a family of 7 from Hyderabad (with grandparents) on a first 2-day trip, travelling by train to Kopargaon and wanting Sansthan rooms.

## Day 03 tasks

**S1 – Ingest:** Download a first real slice of data from the official Sansthan website into `data/raw/`, clean it into the project fields, handle bad rows with `try/except`, and save the result as `data/records.json`.

**S2 – Models and fetch:** Create a `Record` dataclass in `app/models.py` and write `app/fetch.py`, which downloads 3 or more documents using `requests` with timeouts and error handling.

## Data sources (official domain only)
| Name | URL | Used for |
|---|---|---|
| faq | https://sai.org.in/en/faq | FAQ records (parsed) |
| daily_programme | https://sai.org.in/en/daily-programme | Aarti and darshan timings (parsed) |
| how_to_reach | https://sai.org.in/en/how-to-reach-shirdi | Saved raw, to be parsed later |
| accommodations | https://sai.org.in/en/accomodations | Saved raw, room tariffs to be parsed later |

## Folder structure
```
GenAI_EXmate_04/
├── app/
│   ├── __init__.py
│   ├── models.py        # Record dataclass with validation
│   ├── fetch.py         # downloads pages into data/raw/
│   └── ingest.py        # cleans raw HTML into data/records.json
├── data/
│   ├── raw/
│   │   ├── faq.html
│   │   ├── daily_programme.html
│   │   ├── how_to_reach.html
│   │   ├── accommodations.html
│   │   └── manifest.json    # URL, status and fetch date of each download
│   └── records.json         # cleaned output
├── day03/
│   └── README.md
└── requirements.txt
```

## Record fields
| Field | Meaning |
|---|---|
| topic | category such as daily_programme, aarti, darshan, how_to_reach, stay_and_facilities, food, medical, donation, safety, general |
| place_or_service | name of the programme item, or the FAQ question |
| timing | time or time range, or null if none |
| cost_inr | cost in rupees as a number, or null if the page gives no price |
| rule_or_tip | rule or helpful answer text, or null |
| source_url | official page the record came from |
| checked_on | date the page was downloaded |

## How each file works

### app/models.py
Defines the `Record` dataclass. It validates every record when it is created: topic and place_or_service must not be empty, source_url must start with `https://sai.org.in/`, and cost_inr cannot be negative. An invalid record raises `ValueError`, which ingest catches.

### app/fetch.py
- Downloads every page listed in `SOURCES` using one `requests.Session`
- Timeout of 5 seconds to connect and 15 seconds to read
- Up to 3 attempts with a growing wait between attempts
- Handles timeout, connection error, HTTP error and empty response; a 4xx error is not retried
- Refuses any domain other than sai.org.in
- Saves each page to `data/raw/<name>.html` and writes `manifest.json`
- Exits with an error code if fewer than 3 documents were downloaded

### app/ingest.py
- Reads the raw HTML files and parses them with BeautifulSoup
- **Daily programme:** each list row with a clock icon becomes one record (name and time)
- **FAQ:** each question becomes one record; the answer is cleaned, a time or time range is extracted into `timing`, and a rupee amount is extracted into `cost_inr` when present
- Every row is wrapped in `try/except`; bad rows are skipped, counted and logged as warnings
- Duplicates are removed
- Saves the result to `data/records.json` and prints a count per topic

## Setup
```powershell
cd "C:\Examate Git\GenAI_EXmate_04"
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` includes `requests` and `beautifulsoup4`.

## How to run
Run from the project root, using `-m` so the `app` imports work:

```powershell
python -m app.fetch
python -m app.ingest
```

## Check the output
```powershell
ls data\raw
python -c "import json; d=json.load(open('data/records.json',encoding='utf-8')); print(len(d)); print(d[0])"
```

## Sample record
```json
{
  "topic": "daily_programme",
  "place_or_service": "Kakad Aarti (Morning)",
  "timing": "5:15 AM",
  "cost_inr": null,
  "rule_or_tip": null,
  "source_url": "https://sai.org.in/en/daily-programme",
  "checked_on": "2026-11-08"
}
```

## Results
- Documents downloaded: 4 of 4
- Daily programme records: 12
- FAQ records: about 23
- Total records saved in `data/records.json`: about 35

(Update these numbers with your own output after running.)

## Design decisions
- **Official domain only:** every record has a source_url on sai.org.in and a checked_on date.
- **No invented data:** cost_inr stays null when the page gives no price, for example locker charges are only described as "nominal".
- **Fail safely:** one bad row or one failed download never stops the whole run.
- **Raw data is kept** in `data/raw/` so results can be re-checked and re-parsed without downloading again.

## Next steps
- Parse the Sai Bhakta Niwas and Sai Ashram room tariff tables from the accommodations page
- Build the `plan_sansthan_rooms` tool (cheapest room mix for 7 people, no single-person rooms, 24 to 48 hour stay)
- Add the one-day Shirdi timeline card with the train arrival marked

## Author
Sayali Rajendra Pawar, CSE, SJ-50