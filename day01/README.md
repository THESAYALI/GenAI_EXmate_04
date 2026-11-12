# ShirdiYatra 🙏

> A trip planner for Shirdi that uses **only the official pages of the Shri Saibaba Sansthan**.
> It answers three questions a first-time pilgrim family always has: *When can we attend the aartis? Which Sansthan rooms should we book and what will they cost? How do we reach Shirdi?*

| | |
|---|---|
| **Student** | Sayali Rajendra Pawar |
| **Branch / Batch** | CSE, Sanjivani University, SJ-50 |
| **Domain** | Travel & culture |
| **Project slug** | `sanjivani-sj-50-shirdiyatra` |
| **GitHub** | https://github.com/THESAYALI/GenAI_EXmate_04 |
| **Current stage** | Day 1 – Python basics + Git/GitHub (project card, intro script, menu script) |

---

## Table of contents

1. [Product](#1-product)
2. [User](#2-user)
3. [Problem](#3-problem)
4. [Data source](#4-data-source)
5. [Dataset: the 20 records](#5-dataset-the-20-records)
6. [Features](#6-features)
7. [Example questions](#7-example-questions)
8. [Glossary: every word explained](#8-glossary-every-word-explained)
9. [The user journey, moment by moment](#9-the-user-journey-moment-by-moment)
10. [How the app works inside, step by step](#10-how-the-app-works-inside-step-by-step)
11. [How `plan_sansthan_rooms` thinks](#11-how-plan_sansthan_rooms-thinks)
12. [How the timeline card decides "can attend"](#12-how-the-timeline-card-decides-can-attend)
13. [Design decisions, limits and testing](#13-design-decisions-limits-and-testing)
14. [Day 1 deliverables](#14-day-1-deliverables)
15. [Project structure](#15-project-structure)
16. [How to run](#16-how-to-run)
17. [Day 3 and Day 4 plan](#17-day-3-and-day-4-plan)
18. [Risks and how I handle them](#18-risks-and-how-i-handle-them)
19. [Progress](#19-progress)

---

## 1. Product

**What it is.** ShirdiYatra is a small Python application (command line first, later a FastAPI web service) that helps a family plan a visit to Shirdi, the town of Shri Sai Baba in Maharashtra.

**What it does, in plain words.** The user tells the app who is travelling (how many people, AC or non-AC, how many nights, when the train reaches Kopargaon). The app replies with:

1. **Aarti and darshan timings.** The daily programme of the temple: temple opening, Bhupali, Kakad Aarti, Mangal Snaan, Mid-day Aarti, Dhoop Aarti, Shej Aarti and the other rows of the official programme.
2. **Which Sansthan rooms fit the group and budget.** The Sansthan runs accommodation such as Sai Bhakta Niwas and Sai Ashram, with several room types. Each type has a number of beds, a minimum and maximum capacity, a rate and an extra-person charge. The app picks the **cheapest combination of rooms** for the group and prints the total cost.
3. **How to reach Shirdi.** The nearest railway station, the airport and the road connection, taken from the official FAQ page.

**Why "from the Sansthan's own pages".** Pilgrims are warned by the Sansthan itself about fake look-alike websites. ShirdiYatra reads only official pages, so every answer carries a `source_url` and a "checked on" date that the user can verify.

**Two standout features.**

- **Shirdi timeline card.** A one-day card that places the four aartis, the darshan queue hours and the prasadalaya (free meal hall) hours on a clock. The user's **train arrival time is marked** on it, so they can see at a glance which aartis they can still attend that day.
- **`plan_sansthan_rooms` tool.** A pure-Python function that takes group size, AC or non-AC and number of nights and returns the cheapest valid mix of Sansthan rooms and the total cost, applying the Sansthan's rules (no single-person rooms, 24 to 48 hour stay).

**What it is not.** It is not a booking site and it does not take payments. It never replaces the Sansthan's own booking page. It only helps the family decide and prepare.

---

## 2. User

**Who the user is.** A **family of 7 from Hyderabad**, including **grandparents**, planning their **first 2-day trip to Shirdi**.

**Why this persona was chosen, point by point.**

| Detail | Why it matters for the design |
|---|---|
| Family of **7** | 7 people do not fit one room. The app must split the group across several room types and still stay cheap. This is exactly what `plan_sansthan_rooms` solves. |
| **Grandparents** travelling | Elders cannot wait in long queues or walk a lot. They need to know darshan queue hours and pick aartis at comfortable times. The timeline card helps them choose. |
| From **Hyderabad** | They come from another state, do not know the local routine, and may read Telugu, Hindi or English. The Sansthan pages exist in English, Hindi and Marathi, so the data layer keeps the language in mind. |
| **First visit** | They do not know the aarti names, the order of the day, or where Sansthan accommodation is. The app explains each item in simple words. |
| **2-day trip** | Short stay. Every hour counts, and the Sansthan rules allow a 24 to 48 hour room stay, so the plan must fit inside that window. |
| Travel **by train to Kopargaon** | Kopargaon is the nearest main railway station for Shirdi. Their arrival time decides which aartis they can attend on day 1 and day 2, which is what the timeline card shows. |
| Want **Sansthan rooms, not costly hotels** | Budget is the main constraint. The Sansthan's tariff is the cheaper, trusted option, so the app compares only Sansthan room types. |

**What the user wants to walk away with.** A clear plan: "Reach Kopargaon at 11 am, attend these aartis today and these tomorrow, book these rooms, total cost this much, leave in time for the 2 pm train."

---

## 3. Problem

**The problem in one line.** The information a pilgrim needs exists, but it is **scattered, repeated in several languages, sometimes outdated, and hard to combine into a plan**.

**Broken down, point by point.**

1. **Information is spread over many pages.** Timings are on the daily programme page, rules on the FAQ page, room rates in a tariff table. A family has to open and compare all of them.
2. **Several language versions.** The same page exists in English, Hindi and Marathi. Wording and layout differ, and a family can miss a rule that appears in only one version.
3. **Old copies and look-alike websites.** Mirror domains still hold older copies with old prices, and the Sansthan itself warns about **fake websites**. A family can easily land on a wrong page and trust wrong timings or tariffs.
4. **Prices and rules change.** Tariffs, capacities and rules are updated. Without a "checked on" date the user cannot know whether a number is still valid.
5. **Room choice is a puzzle.** For 7 people the family must combine room types with different bed counts, minimum and maximum capacity, rates and extra-person charges, and respect the rules (no single-person rooms, 24 to 48 hour stay). Doing this by hand is slow and often ends in a more expensive choice.
6. **Timing is personal.** Which aartis you can attend depends on **when your train arrives** and when it leaves. No page tells you that. The family has to work it out themselves, and with grandparents a mistake is costly.
7. **Questions need answers, not tables.** A user wants to ask "Can I get a room if I am travelling alone?" and get a short, sourced answer, not read five pages.

**How ShirdiYatra solves it.**

| Problem | Solution in ShirdiYatra |
|---|---|
| Scattered information | One clean dataset of 20 records with the same fields |
| Language versions | Parsed into one structure, source language noted |
| Fake or old pages | Only official domains are accepted |
| Changing prices | Each record stores a `checked_on` date |
| Room puzzle | `plan_sansthan_rooms` computes the cheapest valid mix |
| Personal timing | Timeline card with the train arrival time marked |
| Need quick answers | Question endpoint and search over the records |

---

## 4. Data source

**Where the data comes from.** Only the **official website of Shri Saibaba Sansthan Trust, Shirdi: `sai.org.in`**.

| Page | Used for |
|---|---|
| https://sai.org.in/en/faq | Rules, how to reach, accommodation rules, general questions |
| https://sai.org.in/en/daily-programme | The 12 rows of the daily programme (timings of aartis and temple) |
| Sai Bhakta Niwas / Sai Ashram tariff table | The 8 room types with beds, capacity, rate and extra-person charge |

**Format.** HTML pages in **English, Hindi and Marathi**, containing **tariff tables**.

**How the data is collected and cleaned.**

1. **Download** the page with `requests` (with a timeout and error handling) and keep the raw HTML in `data/raw/`.
2. **Accept only official domains.** Links from mirror sites or unknown domains are rejected.
3. **Parse the HTML tables** into clean numbers (for example "₹ 1,200" becomes `1200`).
4. **Map every row to the same six fields** (see next section).
5. **Store a `checked_on` date** on each record so the user knows how fresh it is.
6. **Skip bad rows safely** with `try/except` instead of crashing, and log what was skipped.
7. **Save** the result as `data/records.json`.

**Why this source.** It is the **single source of truth**. If the Sansthan changes a timing or a rate, this is where the change first appears.

**Data caution.** The data is for planning only. Before travelling, the family should confirm on `sai.org.in`.

---

## 5. Dataset: the 20 records

The dataset has **20 records**:

| Part | Count | What the rows are |
|---|---|---|
| Daily programme | **12** | Temple open, Bhupali, Kakad Aarti, Mangal Snaan, Mid-day Aarti, Dhoop Aarti, Shej Aarti and the other rows of the daily programme |
| Room types | **8** | Room types from the Sai Bhakta Niwas / Sai Ashram tariff table: type, beds, minimum capacity, maximum capacity, rate, extra-person charge |

**Fields of every record.**

| Field | Meaning | Example idea |
|---|---|---|
| `topic` | What the record is about | "Kakad Aarti" or "Non-AC 4-bed room" |
| `place_or_service` | Where or which service | "Samadhi Mandir" or "Sai Bhakta Niwas" |
| `timing` | Time of the event, or stay duration for rooms | "morning aarti time" or "24 to 48 hours" |
| `cost_inr` | Cost in rupees (empty for free events) | `0` for aarti, rate for rooms |
| `rule_or_tip` | A rule or helpful note | "No single-person rooms" |
| `source_url` | Official page the record came from | `https://sai.org.in/en/daily-programme` |

(`checked_on` is added to each record as the date it was verified.)

---

## 6. Features

### 6.1 Shirdi timeline card

- Shows **one day** of Shirdi on a clock.
- Places the **4 aartis**, the **darshan queue hours** and the **prasadalaya hours**.
- **Marks the user's train arrival time**.
- Result: the family instantly sees "we can attend Mid-day Aarti and Dhoop Aarti today, and Kakad Aarti tomorrow".

### 6.2 `plan_sansthan_rooms`

```
plan_sansthan_rooms(group_size, ac_or_non_ac, nights, tariff_csv) -> rooms, total_cost
```

- **Input:** group size, AC or non-AC, number of nights, and a tariff CSV (type, beds, min/max capacity, rate, extra-person charge).
- **Rules applied:**
  - no single-person rooms
  - stay of 24 to 48 hours
  - each room must respect its minimum and maximum capacity
  - extra-person charge is added when a room goes above its normal beds
- **Output:** the chosen rooms and the **total cost**, picked as the cheapest valid mix.
- **Pure Python**, no external library, easy to test.

### 6.3 Question answering over the records

- Search the records by keyword.
- Later (Day 4) rank them with TF-IDF and cosine similarity.
- Every answer shows its `source_url`.

---

## 7. Example questions

1. What time is the Shej aarti and the Kakad aarti in Shirdi?
2. How far is Shirdi from Kopargaon railway station and the airport?
3. Can I get a Sansthan room if I am travelling alone?
4. We are 7 people for 1 night, non-AC is fine. Which Sansthan rooms should we book and what will it cost?
5. We reach Kopargaon at 11 am on Thursday. Which aartis can we attend that day and the next morning before our 2 pm train?
6. How long is the darshan queue on Guru Purnima this year?

Question 6 is a deliberate **trap**: the official pages may not give a queue length for a future date. ShirdiYatra should answer **"not available on the official pages"** instead of guessing.

---

## 8. Glossary: every word explained

| Word | Meaning in simple words |
|---|---|
| **Shirdi** | The town in Maharashtra where Shri Sai Baba lived. Millions of pilgrims visit it every year. |
| **Sansthan** | Shri Saibaba Sansthan Trust, the official trust that runs the temple, the free meals, the accommodation and the website `sai.org.in`. |
| **Darshan** | Seeing the deity. In practice: standing in the queue and reaching the Samadhi Mandir. |
| **Darshan queue** | The line of devotees waiting for darshan. Its length changes by day, season and festival. |
| **Aarti** | A prayer ritual with song and lamps, held several times a day at fixed times. |
| **Kakad Aarti** | The first aarti of the day, early in the morning. |
| **Mid-day Aarti** | The aarti around noon. |
| **Dhoop Aarti** | The evening aarti around sunset. |
| **Shej Aarti** | The last aarti of the day, at night. |
| **Bhupali** | The early-morning prayer before the Kakad Aarti. |
| **Mangal Snaan** | The ritual morning bathing of the idol. |
| **Prasadalaya** | The Sansthan's meal hall where devotees eat prasad (blessed food). |
| **Sai Bhakta Niwas / Sai Ashram** | Sansthan-run accommodation buildings with different room types. |
| **Kopargaon** | The railway station nearest to Shirdi where the family's train arrives. |
| **Tariff** | The price list of rooms. |
| **Extra-person charge** | The money charged when more people stay in a room than its normal number of beds. |
| **Min / max capacity** | The fewest and most people a room type accepts. |
| **Record** | One row of data in `records.json` (see section 5). |
| **Ingest** | Reading raw pages and turning them into clean records. |
| **`checked_on`** | The date a record was last verified against the official page. |

---

## 9. The user journey, moment by moment

This section follows the family of 7 from the first thought of the trip to the train home. For each moment it says **what the family is doing**, **what worry they have**, and **what ShirdiYatra does**.

> The times and rupee amounts below are **dummy numbers for explanation only**. The real app always reads them from `data/records.json`, which comes from `sai.org.in`.

### Moment 0: Weeks before the trip (planning at home in Hyderabad)

| Step | Family | Worry | ShirdiYatra |
|---|---|---|---|
| 0.1 | A son opens the app and types "7 people, 2 days". | "Is it possible to stay in the Sansthan at all?" | Explains the 24 to 48 hour stay rule and that single-person rooms are not allowed. |
| 0.2 | He asks about rooms. | "Hotels are costly. What do the Sansthan rooms cost for 7 of us?" | Runs `plan_sansthan_rooms` and prints the cheapest valid room mix and total cost. |
| 0.3 | He asks about AC or non-AC. | "Grandparents need comfort, but budget matters." | Runs the planner twice (AC and non-AC) so the family sees both totals. |
| 0.4 | He asks how to reach. | "Which station do we get down at?" | Answers from the FAQ record: the train goes to Kopargaon, then road to Shirdi. |
| 0.5 | He asks about the festival crowd. | "Will the queue be long?" | Shows queue hours if available. If the page does not say, answers "not available on the official pages". |
| 0.6 | He checks the source. | "Is this real or a fake site?" | Every answer shows its `source_url` and `checked_on` date. |

### Moment 1: Day 1 morning, on the train

| Step | Family | ShirdiYatra |
|---|---|---|
| 1.1 | The train is running. They enter the arrival time "11:00 am Kopargaon". | Stores the arrival time as the **anchor** of the timeline card. |
| 1.2 | Grandparents ask "what will we manage today?" | Draws the timeline card with a marker at 11:00. Everything before it is greyed out as "missed". |

### Moment 2: Day 1, 11:00, arrival at Kopargaon

| Step | Family | ShirdiYatra |
|---|---|---|
| 2.1 | They get down at the station and look for transport. | Shows the road connection from Kopargaon to Shirdi from the FAQ record. |
| 2.2 | They worry about luggage and elders. | Reminds them of the Sansthan check-in rule from the `rule_or_tip` field. |

### Moment 3: Day 1, midday, reaching the Sansthan rooms

| Step | Family | ShirdiYatra |
|---|---|---|
| 3.1 | They go to the accommodation office. | Shows the room types the planner chose (for example, one larger room for the grandparents, others for the rest). |
| 3.2 | The counter asks "how many nights?" | Reminds that stay is 24 to 48 hours, so check-out time decides their last aarti. |
| 3.3 | They rest and freshen up. | The card shows how many hours remain before the next aarti. |

### Moment 4: Day 1, afternoon

| Step | Family | ShirdiYatra |
|---|---|---|
| 4.1 | They want to attend the **Mid-day Aarti**. | The card checks: is its time after the arrival time plus travel and check-in? If yes, it is marked "can attend", otherwise "missed". |
| 4.2 | They are hungry. | The card shows **prasadalaya hours** so they can eat at the right time. |
| 4.3 | They worry about the darshan queue with the grandparents. | Shows **darshan queue hours** and suggests the calmer slots if the records say so. |

### Moment 5: Day 1, evening

| Step | Family | ShirdiYatra |
|---|---|---|
| 5.1 | **Dhoop Aarti** (evening). | Marked "can attend" on the card. |
| 5.2 | Dinner. | Prasadalaya hours again. |
| 5.3 | **Shej Aarti** (night). | Marked "can attend", and the card warns that it ends late if elders are tired. |

### Moment 6: Day 2, early morning

| Step | Family | ShirdiYatra |
|---|---|---|
| 6.1 | Temple opens, **Bhupali**, **Kakad Aarti**, **Mangal Snaan**. | These are the earliest rows of the daily programme. The card shows which of them fit before check-out and the train. |
| 6.2 | Elders may not wake that early. | The family can choose which to skip and the card updates. |

### Moment 7: Day 2, check-out and departure

| Step | Family | ShirdiYatra |
|---|---|---|
| 7.1 | They check out of the rooms. | Reminds the stay window (24 to 48 hours) so they do not overstay and pay extra. |
| 7.2 | The return train is at 2 pm. | The user enters the departure time and the card draws a second marker. Aartis after it are marked "cannot attend". |
| 7.3 | They travel back to Kopargaon. | Shows the Shirdi to Kopargaon road info again. |

### Moment 8: After the trip

| Step | Family | ShirdiYatra |
|---|---|---|
| 8.1 | They recommend it to relatives. | The same data can serve any group size, which is why the planner takes group size as input. |

---

## 10. How the app works inside, step by step

```
sai.org.in pages
      |
      v
[1] fetch.py     download HTML with requests (timeout, error handling)
      |
      v
[2] data/raw/    raw HTML saved untouched (so we can re-check later)
      |
      v
[3] ingest.py    pick tables, clean numbers, map to 6 fields, add checked_on
      |
      v
[4] records.json 20 clean records (12 programme + 8 rooms)
      |
      +---> [5] records.py / cli.py      list and search records (Day 2)
      +---> [6] plan_sansthan_rooms      cheapest room mix (pure Python)
      +---> [7] timeline card            clock view + train marker
      +---> [8] main.py (FastAPI)        /health /records /search /questions
                  |
                  v
             [9] smart_search.py         TF-IDF + cosine ranking
```

**Step 1: fetch.** Download only official URLs. Use a timeout so the program does not hang. If a download fails, print a clear message and continue.
**Step 2: raw storage.** The untouched HTML is kept. If the parser has a bug, we can fix it without downloading again.
**Step 3: ingest.** Find the programme rows and tariff table, convert text like "Rs. 1,200/-" to the number 1200, and wrap each row in `try/except` so one broken row does not stop the whole run.
**Step 4: records.json.** The single clean file all other parts read.
**Step 5 to 9:** each feature only reads `records.json`. This keeps the code simple: **one data file, many features**.

---

## 11. How `plan_sansthan_rooms` thinks

**Goal:** cover all people with rooms so that the total cost is the **smallest** possible, without breaking a rule.

**Inputs:** group size, AC or non-AC, nights, tariff CSV.

**Rules to check:**
1. Only rooms of the chosen AC type are considered.
2. No room may end with **1 person** (no single-person rooms).
3. Every room must have people between its **min** and **max** capacity.
4. If people exceed the normal beds, add the **extra-person charge**.
5. Stay must be **24 to 48 hours**.

**Method (simple and testable):**
1. Read the tariff rows.
2. Try every combination of room counts whose capacities can hold the group (a small search, because the group is small).
3. Throw away combinations that break a rule.
4. Calculate cost = sum of rooms x rate x nights + extra-person charges.
5. Keep the combination with the lowest cost.
6. Return the rooms and the total.

**Worked example (dummy numbers, group of 7, non-AC, 1 night):**

| Room type | Beds | Min / Max | Rate | Extra person |
|---|---|---|---|---|
| Type A | 2 | 2 / 3 | 400 | 50 |
| Type B | 4 | 3 / 5 | 700 | 80 |

| Option | People per room | Cost calculation | Total |
|---|---|---|---|
| 1 | 4 + 3 in two Type B | 700 + 700 | 1400 |
| 2 | 2 + 2 + 3 in Type A | 400 + 400 + 400 + 50 | 1250 |
| 3 | 5 in Type B + 2 in Type A | 700 + 80 + 400 | 1180 |

The planner would return **Option 3** here, because it is the cheapest valid mix. With the real tariff the numbers change but the method stays the same.

**Edge cases the planner must handle:**

| Case | Expected result |
|---|---|
| Group size 1 | Refuse: "single-person rooms are not allowed" |
| Nights more than the allowed stay | Refuse with the stay rule |
| Group too big for available rooms | Say "not enough rooms in the tariff" |
| Empty or broken tariff CSV | Clear error message, no crash |

---

## 12. How the timeline card decides "can attend"

For every programme row the card does this:

```
if event_time < arrival_time + buffer:      -> "missed" (grey)
elif event_time > departure_time - buffer:  -> "cannot attend" (red)
else:                                       -> "can attend" (green)
```

- `buffer` is the time needed for travel from the station and check-in (a small constant, for example 1 to 2 hours on arrival, and about 1 hour before the train on departure).
- The same rule is applied to day 1 and day 2.

**Worked example (dummy times):** arrival Thursday 11:00, return train Friday 14:00.

| Event | Time (example) | Result |
|---|---|---|
| Kakad Aarti (Thu) | early morning | Missed |
| Mid-day Aarti (Thu) | around noon | Missed or tight, because of travel and check-in |
| Dhoop Aarti (Thu) | evening | Can attend |
| Shej Aarti (Thu) | night | Can attend |
| Kakad Aarti (Fri) | early morning | Can attend |
| Mid-day Aarti (Fri) | around noon | Can attend only if they leave later than it |

This is exactly the logic behind example question 5.

---

## 13. Design decisions, limits and testing

**Design decisions and the reason for each**

| Decision | Reason |
|---|---|
| Official pages only | Trust and safety; the Sansthan warns about fake sites |
| One clean `records.json` | All features share one source, so fixes happen once |
| Keep raw HTML | Parser bugs can be fixed without re-downloading |
| `checked_on` on every record | Prices and rules change |
| Pure-Python room planner | Easy to test, no heavy library, no hidden behaviour |
| `try/except` per row | One bad row should never stop the whole ingestion |
| CLI first, API later | Learn step by step: Day 2 CLI, Day 4 FastAPI |
| Say "not available" instead of guessing | A wrong timing or price can ruin a family's trip |

**Limits (what the app cannot do)**
- It cannot book rooms or take payments.
- It cannot know live queue length unless the official page publishes it.
- It depends on the structure of the Sansthan pages; if the website changes layout, `ingest.py` must be updated.
- It gives planning help only; the family must confirm on `sai.org.in` before travelling.

**How I will test it**

| What | How |
|---|---|
| `plan_sansthan_rooms` | Try group sizes 1, 2, 7, 20 and check results by hand |
| Rule checks | Test nights 0, 1, 2, 3 |
| Ingest | Feed one broken row and confirm the program continues |
| API | `/health` returns OK, `/records/9999` returns 404 |
| Search | Query "Shej aarti" and confirm the right record is ranked first |
| Timeline | Test arrival 11:00 and 23:00 and check the colours |

**Future ideas (after week-1)**
- Hindi and Marathi answers.
- Print-friendly one-page plan for the family.
- Festival-day mode (Guru Purnima, Ram Navami) if the official pages list special timings.

---

## 14. Day 1 deliverables

Task for Day 1 (Wed 4 Nov): *Python basics + Git/GitHub*.

| # | Deliverable | Status |
|---|---|---|
| 1 | Public repo created and cloned | Done |
| 2 | `README.md` = ShirdiYatra project card (product, user, problem, data source) | This file |
| 3 | `day01/day01_intro.py` | Prints the project card using **variables and f-strings**, then asks the user's **name** and a **question** with `input()` |
| 4 | `day01/day01_menu.py` | A **while-loop menu**: **1** about ShirdiYatra, **2** sample questions, **3** one **if/elif rule check** from the domain, **0** exit |
| 5 | Commit with prefix `day-01:` and push | Do after adding files |

**Idea for the rule check in option 3.** Ask for the group size and apply a Sansthan rule with `if/elif`, for example: if the group is 1 person, tell them single-person rooms are not allowed; elif the stay is more than 48 hours, tell them the stay limit is 24 to 48 hours; else say the plan is allowed.

---

## 15. Project structure

```
GenAI_EXmate_04/
├── README.md
├── day01/
│   ├── day01_intro.py        # project card + input()
│   └── day01_menu.py         # while-loop menu
├── data/
│   ├── raw/                  # downloaded Sansthan pages (Day 3)
│   ├── sample_records.json   # 20 sample records (Day 2)
│   └── records.json          # cleaned records (Day 3)
├── app/
│   ├── records.py            # load / search records (Day 2)
│   ├── cli.py                # interactive command line (Day 2)
│   ├── ingest.py             # raw pages -> records.json (Day 3)
│   ├── models.py             # Record dataclass (Day 3)
│   ├── fetch.py              # downloads documents with requests (Day 3)
│   ├── main.py               # FastAPI service (Day 4)
│   └── smart_search.py       # TF-IDF + cosine ranking (Day 4)
└── analysis/
    └── explore.py            # pandas facts about the records (Day 4)
```

---

## 16. How to run

```bash
git clone https://github.com/THESAYALI/GenAI_EXmate_04.git
cd GenAI_EXmate_04

# Day 1
python day01/day01_intro.py
python day01/day01_menu.py

# Later days
pip install fastapi uvicorn requests pandas scikit-learn
python app/fetch.py
python app/ingest.py
python analysis/explore.py
uvicorn app.main:app --reload     # then open http://127.0.0.1:8000/docs
```

---

## 17. Day 3 and Day 4 plan

### Day 3 (Fri 6 Nov): real data

- **S1:** download a first real slice of the data from `https://sai.org.in/en/faq` and `https://sai.org.in/en/daily-programme` into `data/raw/`. `app/ingest.py` cleans it into the fields (`topic`, `place_or_service`, `timing`, `cost_inr`, `rule_or_tip`, `source_url`), uses `try/except` for bad rows, and saves `data/records.json`.
- **S2:** `app/models.py` holds a `Record` dataclass. `app/fetch.py` downloads 3+ documents with `requests`, with timeouts and error handling.

### Day 4 (Sat 7 Nov): API and search

- **S1:** `app/main.py` is a FastAPI service.

| Method | Endpoint | What it does |
|---|---|---|
| GET | `/health` | Service status |
| GET | `/records?limit=` | List records, limited by `limit` |
| GET | `/records/{id}` | One record, **404** if missing |
| GET | `/search?q=` | Search records by text |
| POST | `/questions` | Ask a question, get an answer from the records |

  The README must have a "How to run" section (section 16).
- **S2:** `analysis/explore.py` prints 3 facts about the records using pandas. `app/smart_search.py` ranks records with TF-IDF + cosine similarity and powers `/search`. Tag the repo `week-1`:

```bash
git tag week-1
git push origin week-1
```

---

## 18. Risks and how I handle them

| Risk | Handling |
|---|---|
| Prices and rules change and appear in several versions (English, Hindi, Marathi, older mirror copies) | Keep only official domains, store `checked_on` per record |
| Fake look-alike websites | Reject any URL not on `sai.org.in` |
| HTML tariff tables are messy | Parse them into clean numbers, skip bad rows with `try/except` |
| Missing information (for example a future queue length) | Say "not available on the official pages", do not guess |
| User trusts the app blindly | Show `source_url` and tell the user to confirm on `sai.org.in` before travelling |

---

## 19. Progress

- [x] Day 1: repo, README project card, `day01_intro.py`, `day01_menu.py`
- [ ] Day 2: `data/sample_records.json`, `app/records.py`, `app/cli.py`
- [ ] Day 3: `data/raw/`, `app/ingest.py`, `app/models.py`, `app/fetch.py`
- [ ] Day 4: `app/main.py`, `analysis/explore.py`, `app/smart_search.py`, tag `week-1`

---

*Made by Sayali Rajendra Pawar, CSE, Sanjivani University (SJ-50). Data source: Shri Saibaba Sansthan Trust, Shirdi (`sai.org.in`).*
