# Day 10 - Streamlit UI and the "Shirdi Timeline" Card

**Project:** ShirdiYatra (slug `sanjivani-sj-50-shirdiyatra`)
**Student:** Sayali Rajendra Pawar, CSE, SJ-50, Reg No 2124UCEF2015
**Domain:** Travel and culture
**Day:** D10, Wednesday 18 November
**Repo:** https://github.com/THESAYALI/GenAI_EXmate_04
**Checkpoint:** Checkpoint 2 (live demo), git tag `checkpoint-2`

---

## Table of contents
1. The task in one paragraph
2. What ShirdiYatra is, and where Day 10 fits
3. Why this task is needed
4. My role
5. The data used (and where it comes from)
6. Shri Saibaba Sansthan links referred
7. What is required (prerequisites)
8. Project structure and where each file goes
9. What each part of ui/app.py does
10. Overall flow and how it works
11. The Shirdi timeline card in detail
12. Setup and run commands
13. Testing
14. Live demo script for Checkpoint 2
15. Problems faced and how they were solved
16. Limitations and honest notes
17. Git commands and tag
18. Submission checklist
19. Viva / explanation questions
20. Glossary

---

## 1. The task in one paragraph

Build **`ui/app.py`**, a **Streamlit chat** for ShirdiYatra that:
- calls the FastAPI backend at **`/ask`** (RAG answer) or **`/agent`** (tools + memory + approval),
- **shows citations** for every answer,
- **saves thumbs up / thumbs down** feedback,
- and has my **signature feature: a one-day "Shirdi timeline" card** that places the **4 aartis, the darshan queue hours and the prasadalaya hours on a clock**, with the **user's train arrival time marked**, so they can see **what they can attend**.

Also required: a **screenshot in the README**, a **live demo at Checkpoint 2**, and the git tag **`checkpoint-2`**.

---

## 2. What ShirdiYatra is, and where Day 10 fits

ShirdiYatra plans a Shirdi visit using the official Shri Saibaba Sansthan pages: aarti and darshan timings, Sansthan rooms for a group and budget, and how to reach Shirdi.

Target user (persona): a **family of 7 from Hyderabad with grandparents**, on a **first 2-day trip**, coming by **train to Kopargaon**, who want **Sansthan rooms**.

What was built day by day:

| Day | What was built |
|---|---|
| D1 | Project card (README), intro and menu scripts |
| D2 | Records in JSON, `records.py` (load, search, count_by, get_by_id), CLI |
| D3 | Files, errors, real data: `fetch.py`, `ingest.py`, `models.py` |
| D4 | FastAPI: `/health`, `/records`, `/search`, `POST /questions` |
| D5 | How LLMs work doc, 10 real questions, Checkpoint 1 |
| D6 | `llm.py` provider wrapper, `POST /chat`, prompts, prompt comparison |
| D7 | Chunking, embeddings, Chroma vector store, `/search/semantic` |
| D8 | RAG: `POST /ask` with citations, `eval_set.json`, `run_eval.py` |
| D9 | Tool `plan_sansthan_rooms`, hand-written agent, LangGraph agent, `POST /agent` |
| **D10** | **Streamlit UI + Shirdi timeline card (this document)** |

Days 1 to 9 are the **backend (the brain)**. Day 10 is the **frontend (the face)**.

---

## 3. Why this task is needed

| Reason | Explanation |
|---|---|
| Users cannot use APIs | A pilgrim will not open `/docs` or use curl. A chat page is the natural way to ask questions. |
| Trust | Answers about timings and money must show **where they came from**. Citations let the user check the Sansthan source. |
| Improvement loop | Thumbs up / down are stored, so wrong answers can be found and fixed later (for example to improve prompts or chunking). |
| A real planning need | Visitors ask: "My train arrives at 9:30, which aartis can I still attend?" Text alone is hard to read. A **clock** shows the whole day at once. |
| Differentiation | The timeline is the **signature feature** that makes ShirdiYatra different from a generic chatbot. |
| Demo readiness | Checkpoint 2 is a live demo. A UI makes the whole system visible in a few minutes. |

---

## 4. My role

I am the **AI / full-stack developer** for this project. For Day 10 my responsibilities are:
- connect a Streamlit frontend to the existing FastAPI backend,
- display answers with citations,
- collect and store user feedback,
- design and code the timeline clock and the "can I attend it?" logic,
- test the whole system end to end, document it, and present it at Checkpoint 2.

---

## 5. The data used (and where it comes from)

### 5.1 `data/timeline.json` - used by the timeline card

```
{
  "checked_on": "<date I verified the times>",
  "source_url": "https://www.sai.org.in/en/daily-programme",
  "aartis":        [ {"name": "Kakad Aarti", "time": "05:15"}, ... 4 aartis ... ],
  "darshan_queue": [ {"name": "Darshan queue", "start": "06:00", "end": "21:30"} ],
  "prasadalaya":   [ {"name": "Prasadalaya (lunch)", "start": "11:30", "end": "15:00"}, ... ]
}
```

Values currently in the file:

| Item | Time in file | Note |
|---|---|---|
| Kakad Aarti (morning) | 05:15 | |
| Madhyan Aarti (noon) | 12:00 | |
| Dhoop Aarti (evening) | 18:30 | Held **at sunset**, so the time changes through the year. 18:30 is an approximate winter value. |
| Shej Aarti (night) | 22:00 | Some pages say 10:30 PM. |
| Darshan queue | 06:00 - 21:30 | |
| Prasadalaya lunch / dinner | 11:30-15:00 / 19:00-21:30 | **Sample values.** Must be verified. |

**Important:** these are the values to **verify against the official page and my own `data/records.json`** (the 12 daily programme rows) before the demo, then set `checked_on` to that date.

### 5.2 Backend data used behind the chat

| Data | Used by | Content |
|---|---|---|
| `data/records.json` | Search, RAG | 20 records: 12 daily programme rows + 8 room types (Sai Bhakta Niwas / Sai Ashram tariff) |
| Record fields | | `topic`, `place_or_service`, `timing`, `cost_inr`, `rule_or_tip`, `source_url`, plus a "checked on" date |
| `data/chroma/` | `/ask`, `/search/semantic` | Persistent Chroma vector index of the chunks (in `.gitignore`) |
| `data/room_tariff.csv` | `/agent` | Room types with min/max capacity, rate per night, extra person charge |
| `data/feedback.jsonl` | UI | Created by Day 10: one JSON line per thumbs up/down |

### 5.3 A feedback line looks like
```
{"time": "2026-11-18T10:42:10", "rating": "up", "mode": "/ask", "question": "...", "answer": "..."}
```

### 5.4 Data rules followed since Day 3
- Official domains only.
- Every record keeps its `source_url` and a "checked on" date.
- HTML tariff tables are parsed rather than typed by hand.

---

## 6. Shri Saibaba Sansthan links referred

All data in ShirdiYatra comes from the official Shri Saibaba Sansthan Trust (Shirdi) website, **sai.org.in**. These are the pages the project uses (the same four sources as `app/fetch.py`):

| Page | Link | Used for |
|---|---|---|
| Daily programme | https://www.sai.org.in/en/daily-programme | Temple opening, the four aartis, darshan, pothi, devotional songs, closing. **Main source for the timeline card.** |
| FAQ | https://www.sai.org.in/en/faq | Rules, darshan queue and general visitor questions |
| How to reach Shirdi | https://www.sai.org.in/en/how-to-reach-shirdi | Train, road and air routes, nearest station (Kopargaon) |
| Accommodation | https://www.sai.org.in/en/accomodations | Sansthan room types (Sai Bhakta Niwas, Sai Ashram) and tariff table |

Note: the Sansthan URL for accommodation is spelled **`accomodations`** (one "m"). It is spelled that way on the site itself, so the fetch code uses the same spelling.

Public non-official websites (travel blogs, temple-information sites) were used **only to cross-check** timings while preparing this day. They disagree with each other (see section 16), so **the official Sansthan page is the one cited in the app**.

---

## 7. What is required (prerequisites)

### Knowledge
- Python: functions, dictionaries, lists, JSON, f-strings, basic maths (sin / cos)
- FastAPI basics (Day 4) and the `/ask`, `/agent` endpoints (Days 8 and 9)
- Basic Streamlit: `st.chat_input`, `st.chat_message`, `st.tabs`, `st.session_state`
- Basic SVG (drawing a circle, line and arc in text)

### Software
- Python 3.10 or newer, VS Code, Git and a GitHub account
- The project virtual environment `.venv` (Windows / PowerShell)

### Packages
```powershell
pip install streamlit requests python-dotenv
pip freeze > requirements.txt
```
(`langgraph`, `fastapi`, `uvicorn`, `chromadb`, `sentence-transformers` are already installed from earlier days.)

### Working backend
- `POST /ask` (Day 8) and `POST /agent` (Day 9) responding
- A `.env` file in the repo root with the LLM key, `.env` listed in `.gitignore`, and only `.env.example` committed

---

## 8. Project structure and where each file goes

All files go in the **repo root**: `C:\Users\Sayali Pawar\Desktop\GenAI_EXmate_04_clean`

```
GenAI_EXmate_04_clean\
|-- .env                    real API keys (never pushed)
|-- .env.example            empty template (pushed)
|-- .gitignore              must contain .env
|-- requirements.txt
|-- app\                    BACKEND (FastAPI)
|   |-- main.py             includes /ask and /agent
|   |-- rag.py              Day 8
|   |-- llm.py              Day 6
|   |-- tools.py            Day 9
|   |-- agent_loop.py       Day 9
|   |-- graph.py            Day 9
|   |-- agent_api.py        Day 9
|-- ui\                     FRONTEND (new folder for Day 10)
|   |-- app.py              Streamlit app (all Day 10 code in one file)
|-- data\
|   |-- records.json        scraped Sansthan data
|   |-- room_tariff.csv     Day 9
|   |-- timeline.json       Day 10 (times for the clock)
|   |-- feedback.jsonl      created automatically
|-- docs\
|   |-- timeline_screenshot.png   screenshot for this README
|-- day10\
|   |-- README.md           this file
```

`ui\` is a new folder. It is separate from `app\`, which is the backend.

---

## 9. What each part of `ui/app.py` does

The whole UI is one file with three blocks.

### Block A - Timeline logic
| Function | Job |
|---|---|
| `to_min("05:15")` | Converts a clock time to minutes after midnight (315) |
| `fmt(minutes)` | Converts minutes back to `HH:MM` |
| `load_timeline()` | Reads `data/timeline.json` |
| `event_status(data, arrival_min, buffer_min)` | Decides for every event whether the visitor can attend it |
| `clock_svg(data, arrival_min, ready_min)` | Draws the 24-hour clock as SVG text |
| `render_timeline_card()` | Streamlit widgets: train time input, travel-minutes slider, the clock and the list |

### Block B - Chat logic
| Function | Job |
|---|---|
| `call_backend(base_url, mode, question, thread_id)` | Sends the question to `/ask` or `/agent` |
| `resume_agent(...)` | Sends Approve / Reject to `/agent` after an approval pause |
| `extract_answer_and_citations(resp)` | Reads the answer and the citations from the response (tolerates different key names) |
| `save_feedback(...)` | Appends one JSON line to `data/feedback.jsonl` |
| `feedback_buttons(...)` | Shows the thumbs up / down buttons under an answer |
| `render_chat()` | History, citations expander, approval buttons and the chat box |

### Block C - Page
| Function | Job |
|---|---|
| `main()` | Page setup, sidebar (backend URL, endpoint choice, new conversation) and two tabs: **Chat** and **Shirdi timeline** |

Session memory: `st.session_state` keeps the chat history, the `thread_id` (the agent uses it for its memory) and any pending approval.

---

## 10. Overall flow and how it works

### 10.1 Big picture
```
              +---------------------------+
User  <-----> |  Streamlit  ui/app.py     |
              |  Tab 1: Chat              |
              |  Tab 2: Shirdi timeline   |
              +------+--------------+-----+
                     |              |
            HTTP POST               reads
                     |              |
        +------------v---+     +----v------------------+
        | FastAPI backend |     | data/timeline.json    |
        | /ask  /agent    |     +-----------------------+
        +--------+--------+
                 |
   RAG (Chroma + chunks from sai.org.in)  +  tools (plan_sansthan_rooms)  +  LLM
```

### 10.2 Chat with `/ask`
```
1. User types a question in the chat box.
2. UI sends POST /ask {"question": "..."} to FastAPI.
3. Backend retrieves chunks from Chroma and asks the LLM to answer ONLY from them.
4. Backend returns the answer and citations (source page, title).
5. UI shows the answer, an expandable "Citations" box and the thumbs buttons.
6. If the data does not contain the answer (for example Q6) the answer is "I don't know".
```

### 10.3 Chat with `/agent`
```
1. User: "Family of 7, AC rooms, 2 nights, what will it cost?"
2. UI sends POST /agent {"message": "...", "thread_id": "ab12cd34"}.
3. Agent searches the documents, runs plan_sansthan_rooms(7, AC, 2).
4. Agent pauses and returns status "awaiting_approval" with the proposed rooms and total.
5. UI shows the plan with Approve and Reject buttons.
6. UI sends POST /agent {"thread_id": "...", "approve": true}.
7. UI shows the final answer. The same thread_id keeps the memory, so
   "make it non-AC" in the next message still knows the group size.
```

### 10.4 Feedback
```
User clicks thumbs up/down -> save_feedback() -> one line added to data/feedback.jsonl
The button is replaced by "Feedback saved" so it cannot be clicked twice.
```

### 10.5 Timeline
```
User picks train arrival time and minutes to reach Sansthan
 -> ready = arrival + minutes
 -> every aarti / darshan / prasadalaya window is checked against "ready"
 -> clock is redrawn and the list shows attend / in progress / missed
```

---

## 11. The Shirdi timeline card in detail

### 11.1 Inputs
- Train arrival time (default 09:30)
- Minutes to reach Sansthan from the station or bus stand (slider, 0 to 180, default 60)

### 11.2 Rule for "can I attend it?"
```
ready_time = train_arrival + travel_minutes

Aarti            attendable if aarti_time >= ready_time
Darshan window   attendable if window_end  >  ready_time   (in progress if start < ready < end)
Prasadalaya      attendable if window_end  >  ready_time   (in progress if start < ready < end)
```

Example with the values in `timeline.json`: train at 09:30 + 60 minutes = ready at 10:30.

| Event | Result |
|---|---|
| Kakad Aarti 05:15 | Missed today |
| Darshan queue 06:00-21:30 | In progress, can join now |
| Prasadalaya lunch 11:30-15:00 | Can attend |
| Madhyan Aarti 12:00 | Can attend |
| Dhoop Aarti 18:30 | Can attend |
| Prasadalaya dinner 19:00-21:30 | Can attend |
| Shej Aarti 22:00 | Can attend |

### 11.3 How the clock is drawn
- A 24-hour dial: **00:00 at the top, going clockwise** (12:00 is at the bottom, 06:00 on the right).
- Position of a time = angle `minutes / 1440 * 360 - 90` degrees, converted to x, y with cos and sin.
- **Outer yellow ring** = darshan queue hours (an arc from start to end).
- **Inner green ring** = prasadalaya hours.
- **Red dots with labels** = the 4 aartis.
- **Red needle** + "Train HH:MM" in the centre = train arrival.
- **Blue dashed needle** = time the visitor is ready at Sansthan.
- Output is a text SVG shown with `st.markdown(..., unsafe_allow_html=True)`, so no extra library is needed.

### 11.3 Why a clock and not a table
A 24-hour ring shows overlaps and gaps in one glance: for example that Madhyan Aarti sits inside the lunch prasadalaya window, and how much of the day remains after the train arrives.

---

## 12. Setup and run commands

Open PowerShell in the repo root.

### 12.1 One-time setup
```powershell
cd "C:\Users\Sayali Pawar\Desktop\GenAI_EXmate_04_clean"
.\.venv\Scripts\Activate.ps1
pip install streamlit requests python-dotenv
pip freeze > requirements.txt
New-Item -ItemType Directory -Force -Path ui
New-Item -ItemType Directory -Force -Path docs
```
Copy `app.py` into `ui\` and `timeline.json` into `data\`.

### 12.2 Create `.env` (repo root, next to `app\`)
```powershell
New-Item -ItemType File -Force .env
code .env
```
Content (use the names your `app/llm.py` reads):
```
GROQ_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```
Check `.gitignore` contains `.env`. Restart uvicorn after any change to `.env`.

### 12.3 Run (two terminals)
Terminal 1 - backend:
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```
Terminal 2 - UI:
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run ui/app.py
```
Open http://localhost:8501. Sidebar: backend URL `http://127.0.0.1:8000`, endpoint `/ask` or `/agent`.

Always run `streamlit run ui/app.py` **from the repo root**, because the app finds `data/timeline.json` and `data/feedback.jsonl` relative to the root.

---

## 13. Testing

| # | Test | Expected |
|---|---|---|
| 1 | `/ask`: "What time is the Kakad aarti?" | Correct time, citations visible |
| 2 | A question the data cannot answer | "I don't know" |
| 3 | Click thumbs up, then thumbs down on another answer | "Feedback saved", two lines in `data/feedback.jsonl` |
| 4 | `/agent`: "Family of 7, AC rooms, 2 nights, cost?" | Approval box with rooms and total |
| 5 | Press Approve | Final answer; Reject gives "will not finalise" |
| 6 | Same agent thread: "make it non-AC" | Group size remembered |
| 7 | Timeline: train 09:30, 60 minutes | Kakad missed, rest attendable (see table in 11.2) |
| 8 | Timeline: train 23:00 | Every aarti missed |
| 9 | Stop the backend and ask something | Clear "Backend error" message, no crash |
| 10 | New conversation button | History cleared, new thread id |

---

## 14. Live demo script for Checkpoint 2 (about 4 minutes)

1. **Show the backend** running and `/docs` open.
2. Start the UI. Explain the two tabs.
3. **Chat, `/ask`:** "What time is the Kakad aarti?" Open **Citations**, point at the sai.org.in source. Click **thumbs up**.
4. Ask a question the data cannot answer. Show **"I don't know"**. Click **thumbs down**.
5. Switch to **`/agent`:** "Family of 7, AC rooms for 2 nights, what will it cost?" Show the **approval step**, press **Approve**.
6. Open the **Shirdi timeline** tab. Set the **train arrival to 09:30**. Show what is **missed** and what **can be attended**. Move the travel slider to show it change.
7. Show `data/feedback.jsonl` with the saved thumbs.
8. Show the git tag: `git tag` then `checkpoint-2`.

---

## 15. Problems faced and how they were solved

| # | Problem | Cause | Solution |
|---|---|---|---|
| 1 | Checker could not find `app/` and `data/` (Day 2) | Folders were inside `day02/` | Moved `app/` and `data/` to the **repo root**. Same rule for Day 10: `ui/` at the root. |
| 2 | Missing `data/raw` and `data/records.json` (Day 3) | Fetch and ingest were not run / not committed | Ran `fetch.py` and `ingest.py`, committed the data. |
| 3 | Files downloaded as `tools (1).py`, `graph (1).py` | Browser added `(1)` to duplicates | Renamed with `Move-Item`. Python cannot import a file named `tools (1).py`. |
| 4 | Local repo moved to a new folder | Cleaned copy of the repo | Always run commands from `C:\Users\Sayali Pawar\Desktop\GenAI_EXmate_04_clean` with `.venv` active. |
| 5 | Heavy packages for RAG | `chromadb` and `sentence-transformers` | Installed inside `.venv`; `data/chroma/` added to `.gitignore`. |
| 6 | `/agent` returned 404 | `agent_router` lines missing in `app/main.py` | Added `include_router(agent_router)`. |
| 7 | UI could not read `.env` keys | `.env` placed in the wrong folder, or `load_dotenv()` missing | `.env` in repo root, `load_dotenv()` in `llm.py`, restart uvicorn. |
| 8 | Request returned 422 from `/ask` | UI sent a different field name than the backend expects | Payload in `call_backend()` adjusted to the backend's field name. |
| 9 | No citations displayed | Response key was not `citations` | `extract_answer_and_citations()` accepts `citations`, `sources`, strings or dicts. |
| 10 | Clock times looked wrong | Aarti timings differ between websites; Dhoop Aarti is at sunset | Used the official page, marked Dhoop as approximate, stored `checked_on`. |
| 11 | Streamlit could not find `data/timeline.json` | Run from inside `ui/` | Paths are built from the repo root; run `streamlit run ui/app.py` from the root. |
| 12 | Thumbs buttons reset the page | Streamlit reruns the script on each click | State kept in `st.session_state`; `st.rerun()` after saving. |
| 13 | Agent approval lost between messages | Different `thread_id` each message | One `thread_id` stored in `st.session_state`, new one only on "New conversation". |

---

## 16. Limitations and honest notes

1. **Timings disagree across the internet.** While preparing this day I found Kakad Aarti listed as 4:30 AM on some sites and 5:15 AM on others, and Shej Aarti as 10:00 PM on some and 10:30 PM on others. Third-party pages are often outdated. The app uses the Sansthan page as the source of truth. **Verify all times on https://www.sai.org.in/en/daily-programme before the demo.**
2. **Dhoop Aarti is held at sunset**, so a fixed 18:30 is only an approximation. A later improvement is to calculate it from the sunset time of the visit date.
3. **Prasadalaya hours** in `timeline.json` are sample values until I confirm them from the official page.
4. **Festival days and peak seasons** change timings and queue length. The card shows a normal day only.
5. **Queue waiting time** is not modelled. "Darshan queue open" does not mean "no waiting".
6. **Aarti entry** may need a separate pass, so "can attend" means the timing allows it, not that entry is guaranteed.
7. The timeline is **one day**; the 2-day trip view is a possible extension.
8. Feedback is stored locally in a file, not in a database.

---

## 17. Git commands and tag

```powershell
git status
git add ui data/timeline.json docs day10 .env.example .gitignore requirements.txt
git status
git commit -m "day-10: Streamlit UI with citations, feedback and Shirdi timeline"
git push
git tag checkpoint-2
git push origin checkpoint-2
```
- Confirm `.env` does **not** appear in `git status`.
- Add the screenshot first (`docs\timeline_screenshot.png`), then commit, push and tag, so the tag contains it.
- If the push is rejected: `git pull --rebase`, then `git push`.

### Screenshot

![Shirdi timeline card](../docs/timeline_screenshot.png)

(Take the screenshot of the **Shirdi timeline** tab with a train time set, for example 09:30, and save it as `docs/timeline_screenshot.png`.)

---

## 18. Submission checklist

- [ ] `ui/app.py` runs with `streamlit run ui/app.py` from the repo root
- [ ] Chat works with `/ask` and with `/agent` (approval step works)
- [ ] Citations are shown under answers
- [ ] Thumbs up / down are saved in `data/feedback.jsonl`
- [ ] Timeline card shows 4 aartis, darshan queue, prasadalaya and the train arrival
- [ ] `data/timeline.json` verified on sai.org.in and `checked_on` filled
- [ ] Screenshot saved in `docs/` and shown in this README
- [ ] `.env` not pushed; `.env.example` pushed
- [ ] Commit message starts with `day-10:`
- [ ] Tag `checkpoint-2` created and pushed
- [ ] Live demo rehearsed (section 14)

---

## 19. Viva / explanation questions

**1. Why do you need a UI when the API already works?**
Users cannot call APIs. The UI also shows citations and collects feedback.

**2. What is the difference between `/ask` and `/agent`?**
`/ask` is retrieval plus an LLM answer from the documents. `/agent` can also run tools (room planning), remembers the conversation by `thread_id` and pauses for human approval.

**3. How do citations work?**
The backend returns the source of each retrieved chunk. The UI reads them from the response and shows them in an expander.

**4. How is the "can I attend it?" decision made?**
ready time = train arrival + travel minutes. Aartis must be at or after ready time; windows must end after it.

**5. How is the clock drawn?**
Each time is converted to minutes, then to an angle (minutes / 1440 * 360, starting at the top), then to x and y with cos and sin. Rings are SVG arcs and the aartis are dots.

**6. Where is the feedback stored and why?**
In `data/feedback.jsonl`, one line per click, so wrong answers can be reviewed and prompts or chunking improved.

**7. Why is `.env` not pushed?**
It holds secret API keys. Only `.env.example` with empty values is committed.

**8. What would you improve next?**
Compute sunset for Dhoop Aarti, add a 2-day itinerary, add festival-day timings, store feedback in a database.

---

## 20. Glossary

| Term | Meaning |
|---|---|
| Aarti | A devotional ritual with lamps and songs. Four a day at Shirdi: Kakad (morning), Madhyan (noon), Dhoop (sunset), Shej (night). |
| Darshan | Seeing / worshipping the deity. Pilgrims wait in a queue for darshan. |
| Prasadalaya | The Sansthan dining hall serving prasad (meal) to devotees. |
| Sansthan | Shri Saibaba Sansthan Trust (Shirdi), the temple trust and the official source of all data. |
| Samadhi Mandir | The main temple holding Sai Baba's samadhi. |
| RAG | Retrieval-Augmented Generation: find relevant document chunks first, then let the LLM answer from them. |
| Citation | The source (page, title, URL) shown with an answer. |
| Streamlit | A Python library for building web apps quickly. |
| FastAPI | The Python web framework used for the backend. |
| Agent | A program where the model chooses tools (search, room planner) and uses their results. |
| thread_id | An id that tells the agent which conversation (memory) a message belongs to. |
| Checkpoint | A course review point; `checkpoint-2` is the git tag for the Day 10 demo. |