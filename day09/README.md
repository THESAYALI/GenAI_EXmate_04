New-Item -ItemType Directory -Force -Path day09 | Out-Null
@'
# Day 09 - Agent Tool, Agent Loop and LangGraph Agent (ShirdiYatra)

**Project:** ShirdiYatra (slug: sanjivani-sj-50-shirdiyatra)
**Student:** Sayali Rajendra Pawar, CSE, SJ-50
**Day / Date:** D9, Tuesday 17 November
**Repo:** https://github.com/THESAYALI/GenAI_EXmate_04

---

## 1. What is my task?

The Day 09 task has two sessions.

### Session 1 (S1) - Build an agent tool and a hand-written agent

1. **`app/tools.py` - the tool `plan_sansthan_rooms`**
   - Input: group size, AC or non-AC, and number of nights.
   - It reads a tariff CSV with these columns: min capacity, max capacity, rate, extra person charge.
   - It picks the **cheapest mix of Sansthan room types** for the whole group.
   - Rules it must follow:
     - No single-person rooms (every room has at least 2 people).
     - The stay must be 24 to 48 hours (so 1 or 2 nights).
   - Output: the rooms chosen and the **total cost**.
   - It must be **pure Python** (no external libraries).
2. **`app/agent_loop.py` - a hand-written agent**
   - An agent written by hand, with no framework.
   - It can call two things: our **RAG search** (from Day 07/08) and the new **room tool**.

### Session 2 (S2) - Rebuild it in LangGraph

3. **`app/graph.py`** rebuilds the same agent in **LangGraph** with:
   - **Memory** (it remembers the conversation, e.g. group size).
   - **One approval step** (a human approves the room plan before it is final).
4. **`POST /agent`** - an API endpoint so the agent can be used through FastAPI.

---

## 2. Why is this task needed?

| Reason | Explanation |
|---|---|
| Our project already answers questions | Days 1-8 built search, LLM chat and RAG. That only **reads** information. |
| Real users need actions, not only answers | A family of 7 does not just ask "what are the room rates?". They want "which rooms should I book and what will it cost?". That needs **calculation**, which an LLM should not guess. |
| LLMs are bad at exact maths | An LLM may invent prices. A Python tool gives **exact, repeatable** totals from official tariff data. |
| Agents combine tools | An agent decides *which* tool to use (search for timings, room tool for cost) and joins the results. |
| Learn two levels | S1 shows how an agent works inside (the loop). S2 shows how a framework (LangGraph) does the same with memory and human approval. |
| Safety | Money-related plans should be approved by a human first. That is the approval step. |

In short: **RAG gives knowledge, the tool gives correct calculation, the agent connects them, and the approval step keeps the user in control.**

---

## 3. What is my role in this task?

I am the **AI / backend developer** for ShirdiYatra. My responsibilities:

- Design the room-planning rules and implement them correctly in Python.
- Prepare the tariff data (real rates from the Sansthan website, with a "checked on" date).
- Write the agent loop so the model can choose tools and use their results.
- Rebuild the agent in LangGraph with memory and an approval step.
- Expose it through the FastAPI endpoint `POST /agent`.
- Test it, document it (this README), and push it to GitHub.

---

## 4. What is required (prerequisites)?

### Knowledge
- Python basics: functions, dictionaries, lists, loops, CSV reading.
- Basic idea of dynamic programming (used to find the cheapest mix).
- FastAPI basics (from Day 04).
- RAG basics (from Day 07 and Day 08).
- The idea of an agent: think, use a tool, observe, answer.

### Software
- Python 3.10 or newer
- VS Code
- Git and a GitHub account
- The project virtual environment `.venv`

### Packages
```powershell
pip install langgraph
pip freeze > requirements.txt
```
Already installed from earlier days: fastapi, uvicorn, chromadb, sentence-transformers.

### Files from earlier days that this task depends on
- `app/rag.py` - the RAG search the agent calls
- `app/llm.py` - the LLM wrapper (optional; the agent still runs with rules if the LLM is not available)
- `app/main.py` - the FastAPI app, where `/agent` is added
- `data/records.json` - the scraped Sansthan data (room tariff source)

---

## 5. Folder and file structure

```
GenAI_EXmate_04_clean\
|-- app\
|   |-- tools.py          (S1) room planning tool
|   |-- agent_loop.py     (S1) hand-written agent
|   |-- graph.py          (S2) LangGraph agent
|   |-- agent_api.py      (S2) POST /agent
|   |-- main.py           (edited: includes the agent router)
|   |-- rag.py            (Day 08) RAG search used by the agent
|   |-- llm.py            (Day 06) LLM wrapper used by the agent
|-- data\
|   |-- room_tariff.csv   (S1) tariff used by the tool
|-- tests\
|   |-- test_tools.py     (S1) tests for the rules
|-- day09\
|   |-- README.md         this file
|-- requirements.txt
```

---

## 6. What each file does

| File | Session | Purpose |
|---|---|---|
| `data/room_tariff.csv` | S1 | Tariff table: room type, AC flag, min/max capacity, rate per night, extra person charge, source URL, checked-on date. |
| `app/tools.py` | S1 | `plan_sansthan_rooms(group_size, ac, nights)`. Finds the cheapest room mix using the rules. Pure Python. |
| `app/agent_loop.py` | S1 | The hand-written agent. Contains the tool list, the think-act-observe loop, and adapters to the RAG search and the LLM. |
| `tests/test_tools.py` | S1 | Checks the rules: no single rooms, 1 or 2 nights only, cheapest mix. |
| `app/graph.py` | S2 | The LangGraph version: nodes, routes, memory (`MemorySaver`) and the approval `interrupt`. |
| `app/agent_api.py` | S2 | FastAPI router with `POST /agent`. Handles a new message or an approval answer. |
| `app/main.py` | S2 | Edited to include `agent_router`. |

---

## 7. Overall flow

### 7.1 Big picture

```
User question
     |
     v
   AGENT  ---------------------------+
     |                               |
     |  needs facts?                 |  needs a cost / room plan?
     v                               v
 RAG search (Day 08)        plan_sansthan_rooms (tools.py)
 timings, rules, routes     reads data/room_tariff.csv
     |                               |
     +---------------+---------------+
                     v
               Final answer
```

### 7.2 S1 - hand-written agent loop (`agent_loop.py`)

```
question
   |
   v
[Step 1] Ask the LLM (or rule planner): what next?  -> returns JSON
   |
   +-- {"action":"tool", ...}  -> run the tool -> save the result as an observation -> go back to Step 1
   |
   +-- {"action":"final", ...} -> return the answer
(stops after MAX_STEPS = 5 to avoid endless loops)
```

Example with "family of 7, AC, 2 nights, cost?":
1. Step 1 -> call `search_docs` (get Sansthan context).
2. Step 2 -> call `plan_sansthan_rooms(7, True, 2)`.
3. Step 3 -> final answer with the rooms and the total.

### 7.3 S2 - LangGraph flow (`graph.py`)

```
START
  |
  v
understand   (read the message; get group size / AC / nights; merge with memory)
  |
  v
rag          (search the Sansthan documents)
  |
  +-- room question and all 3 values known? --yes--> rooms (run the tool)
  |                                                     |
  |                                         plan ok? --yes--> approval (PAUSE, ask the user)
  |                                              |                    |
  |                                              no                   v
  +-- no --------------------------------------> answer <-------------+
                                                   |
                                                  END
```

- **Memory:** `MemorySaver` stores the state per `thread_id`. Say "family of 7" in one message and "make it non-AC" in the next; the group size is remembered.
- **Approval:** the `approval` node calls `interrupt(...)`. The graph stops and returns the proposed plan. The user answers `approve: true` or `false`, and the graph continues.

### 7.4 API flow (`POST /agent`)

```
Request 1: {"thread_id":"t1","message":"family of 7, AC, 2 nights, cost?"}
Response 1: {"status":"awaiting_approval","proposal":{ rooms, total_cost }}

Request 2: {"thread_id":"t1","approve":true}
Response 2: {"status":"done","answer":"Approved. Cheapest Sansthan rooms ..."}
```

---

## 8. How the tool `plan_sansthan_rooms` performs

### Rules
1. The rate of a room covers `min_capacity` people.
2. Each extra person above that (up to `max_capacity`) pays `extra_person_charge` per night.
3. No room may have only 1 person.
4. `nights` must be 1 or 2 (stay of 24 to 48 hours).
5. Only rooms matching the AC / non-AC choice are used.

### Cost of one room
```
room_cost = (rate_per_night + extra_people * extra_person_charge) * nights
extra_people = max(0, occupants - min_capacity)
```

### Why dynamic programming, not a simple greedy choice
A greedy choice (always take the biggest room) can be more expensive. The tool tries every valid way to fill the group and keeps the **cheapest**:

```
best[0] = cost 0, no rooms
for n in 1..group_size:
    for each room type, for each valid occupant count k of that room:
        candidate = best[n - k] + cost of one room with k people
        keep the cheapest candidate for best[n]
answer = best[group_size]
```
If `best[group_size]` cannot be reached (e.g. it would need a single-person room), the tool returns an error instead of a bad plan.

### Output
```
{
  "ok": true,
  "group_size": 7, "ac": true, "nights": 2, "stay_hours": 48,
  "rooms": [ {room_type, count, occupants_per_room, cost_per_room, subtotal}, ... ],
  "total_cost": ...
}
```
or `{"ok": false, "error": "..."}`.

### Edge cases handled
- Group of 1 -> error (no single-person rooms).
- 0 or 3+ nights -> error (stay must be 24-48 hours).
- Wrong AC value or text -> error message instead of a crash.
- Group size that cannot be split into valid rooms -> clear error.

---

## 9. Setup (step by step)

```powershell
cd "C:\Users\Sayali Pawar\Desktop\GenAI_EXmate_04_clean"
.\.venv\Scripts\Activate.ps1
pip install langgraph
pip freeze > requirements.txt
```

Edit `app/main.py`:
```python
from app.agent_api import router as agent_router
app.include_router(agent_router)
```

Replace the sample rates in `data/room_tariff.csv` with the real Sai Bhakta Niwas / Sai Ashram tariff from `data/records.json`, and fill the `checked_on` column.

If the agent prints "RAG search not connected", edit `search_docs()` in `app/agent_loop.py` so it calls your real function in `app/rag.py`. Do the same for `call_llm()` and `app/llm.py`.

---

## 10. How to run

```powershell
python -m app.tools            # S1: the tool, interactive
python -m app.agent_loop       # S1: the hand-written agent, interactive
uvicorn app.main:app --reload  # S2: API; open http://127.0.0.1:8000/docs
```

---

## 11. Test cases

| Input | Expected result |
|---|---|
| 7 people, AC, 2 nights | Valid plan, 48 hours, all people placed, every room has 2+ people |
| 6 people, non-AC, 1 night | Cheapest plan, total not more than one big room |
| 1 person | Error: no single-person rooms |
| 4 people, 3 nights | Error: stay must be 24-48 hours |
| 4 people, 0 nights | Error: stay must be 24-48 hours |
| "What time is the Kakad aarti?" | Answer from RAG only, no room tool |
| Question not in the data | "I don't know" |

Run the checks:
```powershell
python -m pytest tests -q
```
(if pytest is missing: `pip install pytest`)

---

## 12. API examples

**1. Ask for a plan**
```json
{"thread_id": "t1", "message": "We are a family of 7, AC rooms for 2 nights, what will it cost?"}
```
Returns `status: awaiting_approval` with the proposed rooms and total.

**2. Approve**
```json
{"thread_id": "t1", "approve": true}
```
Returns `status: done` and the final answer.

**3. Reject**
```json
{"thread_id": "t1", "approve": false}
```

**4. Memory test (same thread)**
```json
{"thread_id": "t1", "message": "make it non-AC"}
```
Group size and nights come from memory.

---

## 13. Hand-written agent vs LangGraph

| Point | `agent_loop.py` (S1) | `graph.py` (S2) |
|---|---|---|
| Control flow | A Python `for` loop | Nodes and edges in a graph |
| Memory | None between runs | Saved per `thread_id` |
| Human approval | None | Built-in `interrupt` |
| Easy to extend | Edit the loop | Add a node and an edge |
| Best for learning | How an agent really works | How real projects structure agents |

---

## 14. Common problems and fixes

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: app` | Run commands from the repo root; make sure `app/__init__.py` exists. |
| `No module named langgraph` | `pip install langgraph` inside the `.venv`. |
| "RAG search not connected" | Update `search_docs()` to your real `app/rag.py` function name. |
| `/agent` returns 404 | You forgot the two lines in `app/main.py`. |
| Totals look too low or high | Replace the sample rates in `room_tariff.csv` with real ones. |
| `.venv` not active | `.\.venv\Scripts\Activate.ps1` |

---

## 15. Git commands (push the Day 09 work)

```powershell
git status
git add app/tools.py app/agent_loop.py app/graph.py app/agent_api.py app/main.py data/room_tariff.csv tests day09 requirements.txt README.md
git commit -m "day-09: plan_sansthan_rooms tool, agent loop, LangGraph agent with approval, POST /agent"
git push
```

---

## 16. Submission checklist

- [ ] `app/tools.py` works and returns rooms and total cost
- [ ] No single-person rooms, 24-48 hour rule enforced
- [ ] `data/room_tariff.csv` has real rates and a checked-on date
- [ ] `app/agent_loop.py` calls both RAG search and the room tool
- [ ] `app/graph.py` has memory and one approval step
- [ ] `POST /agent` works at `/docs`
- [ ] Tests pass
- [ ] This README is in `day09/`
- [ ] Commit message starts with `day-09:` and is pushed to GitHub

---

## 17. Summary

Day 09 turns ShirdiYatra from a question-answering app into a small **planning agent**. The tool does the exact room-cost calculation, the RAG search supplies verified Sansthan facts, the agent loop connects them, and LangGraph adds memory and a human approval step behind `POST /agent`.
'@ | Set-Content -Path day09\README.md -Encoding UTF8
code day09\README.md