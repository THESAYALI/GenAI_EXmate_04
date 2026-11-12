# ShirdiYatra 🙏

**Student:** Sayali Rajendra Pawar · CSE · Sanjivani University · SJ-50
**Domain:** Travel & culture
**Project slug:** `sanjivani-sj-50-shirdiyatra`

## Product

ShirdiYatra plans a Shirdi visit using only the Shri Saibaba Sansthan's own official pages. It tells you the aarti and darshan timings, which Sansthan rooms fit your group size and budget, and how to reach Shirdi.

## User

A family of 7 from Hyderabad (grandparents included) planning their **first 2-day Shirdi trip**. They travel by train to Kopargaon and want to stay in **Sansthan rooms**, not costly hotels.

## Problem

- Timings, room tariffs and rules are spread over many pages and languages (English, Hindi, Marathi).
- Older copies on mirror domains and fake look-alike websites show outdated or wrong prices.
- Families cannot easily tell which aartis they can attend after their train arrives, or which room mix is cheapest for 7 people.

## Data source

Official Sansthan website only (`sai.org.in`):

- https://sai.org.in/en/faq
- https://sai.org.in/en/daily-programme
- Sai Bhakta Niwas / Sai Ashram room tariff table

Format: HTML pages (English / Hindi / Marathi) with tariff tables.
Every record stores a `checked_on` date. Non-official domains are ignored.

## Dataset (20 records)

| Part | Count | Content |
|------|-------|---------|
| Daily programme | 12 | Temple open, Bhupali, Kakad Aarti, Mangal Snaan, Mid-day Aarti, Dhoop Aarti, Shej Aarti, etc. |
| Room types | 8 | Type, beds, min/max capacity, rate, extra person charge |

**Record fields:** `topic`, `place_or_service`, `timing`, `cost_inr`, `rule_or_tip`, `source_url`

## Features

1. **Shirdi timeline card** – a one-day clock view with the 4 aartis, darshan queue hours and prasadalaya hours, with the user's train arrival time marked so they see what they can attend.
2. **`plan_sansthan_rooms` tool** – given group size, AC / non-AC and number of nights, picks the cheapest mix of Sansthan rooms from a tariff CSV and returns rooms and total cost. Rules applied:
   - no single-person rooms
   - stay of 24–48 hours
   - min/max capacity and extra person charge respected
   Pure Python.

## Example questions

1. What time is the Shej aarti and the Kakad aarti in Shirdi?
2. How far is Shirdi from Kopargaon railway station and the airport?
3. Can I get a Sansthan room if I am travelling alone?
4. We are 7 people for 1 night, non-AC is fine. Which Sansthan rooms should we book and what will it cost?
5. We reach Kopargaon at 11 am on Thursday. Which aartis can we attend that day and the next morning before our 2 pm train?
6. How long is the darshan queue on Guru Purnima this year?

## Project structure

```
GenAI_EXmate_04/
├── README.md
├── day01/
│   ├── day01_intro.py      # intro script
│   └── day01_menu.py       # interactive menu
├── data/
│   └── sample_records.json # 20 records (Day 2)
└── app/
    ├── records.py          # load / search records (Day 2)
    └── cli.py              # interactive command line (Day 2)
```

## How to run

```bash
git clone https://github.com/THESAYALI/GenAI_EXmate_04.git
cd GenAI_EXmate_04
python day01/day01_intro.py
python day01/day01_menu.py
```

## Known risks

- Prices and rules change and appear in several language versions and old mirror copies.
- Ingestion must keep only official domains, store a "checked on" date, and parse HTML tariff tables into clean numbers.

## Progress

- [x] Day 1 – Python basics, Git/GitHub, README
- [ ] Day 2 – sample records, `records.py`, `cli.py`

## Links

- Repo: https://github.com/THESAYALI/GenAI_EXmate_04 git config --global user.name "THESAYALI"
