# Day 02 – ShirdiYatra: Records, Fetch & CLI

## Project
ShirdiYatra helps plan a Shirdi visit using official Shri Saibaba Sansthan pages (sai.org.in): aarti and darshan timings, Sansthan rooms for groups and budget, and how to reach Shirdi.

**Target user:** a family of 7 from Hyderabad (with grandparents) on a first 2-day trip, travelling by train to Kopargaon and wanting Sansthan rooms.

## Day 02 task
Create the data records, load them, and run them from a command-line interface.

## Folder structure
```
day02/
├── __init__.py
├── cli.py                # command-line interface
├── fetch.py              # fetches data from the Sansthan pages
├── ingest.py             # loads and cleans the records
├── records.py            # record structure and helpers
├── file.py               # file helper functions
├── sample_records.json   # 20 sample records
└── README.md
```

## Record fields
| Field | Meaning |
|---|---|
| topic | what the record is about |
| place_or_service | place or service name |
| timing | time or duration |
| cost_inr | cost in rupees |
| rule_or_tip | rule or helpful tip |
| source_url | official source page |

## Data
- Source: sai.org.in (official Sansthan website only)
- 20 records: 12 daily programme rows and 8 room types (Sai Bhakta Niwas / Sai Ashram tariff)
- Every record has a "checked on" date

## Setup
```powershell
cd "C:\Examate Git\GenAI_EXmate_04"
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## How to run
```powershell
python day02\cli.py
```

## Planned feature
A one-day Shirdi timeline card with the train arrival marked, and a `plan_sansthan_rooms` tool that picks the cheapest room mix (no single-person rooms, 24 to 48 hour stay).

## Author
Sayali Rajendra Pawar, CSE, SJ-50