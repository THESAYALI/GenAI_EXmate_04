# Day 13 — Production basics + README that sells + resume bullets (Sat 21 Nov)

Project: **ShirdiYatra** (`sanjivani-sj-50-shirdiyatra`) · Repo: `THESAYALI/GenAI_EXmate_04`
Local folder: `C:\Users\Sayali Pawar\Desktop\GenAI_EXmate_04_clean` (Windows, PowerShell, `.venv`)

---

## 1. The task (from the tracker)

**S1 (Session 1) — make the app production-ready**
1. Log **latency + tokens per request**
2. A **simple cache**
3. **Input limits**
4. **One prompt-injection test**
5. README section **"Production notes"** with **real numbers**

**S2 (Session 2) — sell the project**
1. README that sells ShirdiYatra: **problem**, **architecture diagram (Mermaid)**, **demo video link**, **results table**
2. `docs/resume.md` with **3 resume bullets**

---

## 2. Files in this pack and where each one goes

All paths are relative to the repo root `GenAI_EXmate_04_clean\`.

| # | File | Goes in | New / edit | Covers |
|---|------|---------|-----------|--------|
| 1 | `production.py` | `app\` | NEW | S1.1 logging, S1.2 cache, S1.3 input limits, injection guard, `/metrics` |
| 2 | `test_production.py` | `tests\` | NEW | S1.4 prompt-injection test + cache + limits tests |
| 3 | `measure.py` | `scripts\` | NEW | S1.5 produces the real numbers |
| 4 | `README.md` | repo root | REPLACES old | S2.1 problem, Mermaid, demo link, results table, Production notes |
| 5 | `resume.md` | `docs\` | NEW | S2.2 three resume bullets |
| 6 | `README.md` (this file) | `day13\` | NEW | Explains everything |
| 7 | `main.py` | `app\` | **YOU EDIT** | add `install(app)` + `guarded_answer(...)` |
| 8 | `llm.py` | `app\` | **YOU EDIT** | add `add_usage(...)` after each LLM call |
| 9 | `.gitignore` | repo root | **YOU EDIT** | add `logs/` |

Final layout:

```
GenAI_EXmate_04_clean\
├── README.md                  <- project README (S2)
├── .gitignore                 <- add:  logs/
├── app\
│   ├── main.py                <- EDIT
│   ├── llm.py                 <- EDIT
│   ├── rag.py                 (existing)
│   └── production.py          <- NEW
├── tests\
│   └── test_production.py     <- NEW
├── scripts\
│   └── measure.py             <- NEW
├── docs\
│   ├── resume.md              <- NEW
│   └── production_numbers.md  <- created by measure.py
├── day13\
│   └── README.md              <- this file
└── logs\
    └── requests.jsonl         <- created automatically (do NOT commit)
```

---

## 3. What each file does

### app/production.py
| Part | What it does |
|---|---|
| `install(app)` | Adds a middleware that times every request, stores prompt/completion tokens, cache hit and blocked flag; writes one JSON line per request to `logs/requests.jsonl`; rejects bodies over 10 KB; adds `GET /metrics`. |
| `add_usage(prompt, completion)` | Called from `llm.py` after each LLM call so token numbers are real provider numbers. |
| `TTLCache` / `CACHE` | In-memory cache, 10 minutes, 128 items, oldest removed first. |
| `validate_question()` | Empty question -> HTTP 400. More than 500 characters -> HTTP 413. Removes control characters. |
| `looks_like_injection()` | Regex guard for "ignore previous instructions", "reveal your system prompt", "developer mode", etc. |
| `guarded_answer(question, fn)` | Order: validate -> injection check (blocked, LLM never called) -> cache lookup -> call your RAG function -> estimate tokens if llm.py did not report -> store in cache. |
| `metrics_summary()` | Requests, errors, blocked, latency p50/p95/avg, avg tokens, cache hit rate. |

Settings are at the top of the file: `MAX_QUESTION_CHARS`, `MAX_BODY_BYTES`, `CACHE_TTL_SECONDS`, `CACHE_MAX_ITEMS`.

### tests/test_production.py
- cache hit and expiry, cache eviction
- same question (different case/spacing) answered only once
- empty question -> 400, too long -> 413
- **prompt-injection test**: attack text is blocked and the LLM function is called 0 times
- normal pilgrim questions are not blocked
- percentile helper

### scripts/measure.py
Sends your eval questions twice (cold, then cached), tests a 600-character input and one injection, reads `/metrics`, and writes `docs/production_numbers.md` with a table you paste into README -> Production notes.

### README.md (project README)
Sections: badge, live demo + video, problem, features, Mermaid architecture, results table, Production notes, run locally, data and honesty, repo map.

### docs/resume.md
Three resume bullets with `{placeholders}` for your real numbers.

---

## 4. Step by step

### Step 1 — put the files in place
Extract `day13_files.zip` into `C:\Users\Sayali Pawar\Desktop\GenAI_EXmate_04_clean` (right-click -> Extract All -> Browse -> that folder). Old README is backed up as `README_old.md`.

### Step 2 — edit `app\main.py`
Add the import near the top and call `install(app)` right after `app = FastAPI(...)`:

```python
from app.production import install, guarded_answer

app = FastAPI(...)
install(app)
```

Change your `/ask` endpoint (adjust the names to your code):

```python
@app.post("/ask")
def ask(req: AskRequest):
    return guarded_answer(req.question, lambda q: answer_question(q))
```
- `req.question` = the field of your request model. If it is named differently, change it here and change `FIELD = "question"` at the top of `scripts\measure.py`.
- `answer_question(q)` = whatever function in `app\rag.py` you already call inside `/ask`. It must take the question and return a dict (or pydantic model) with `answer`.

### Step 3 — edit `app\llm.py`
After every LLM call, report the token usage.

Groq (OpenAI-style response):
```python
from app.production import add_usage
...
add_usage(resp.usage.prompt_tokens, resp.usage.completion_tokens)
```
Gemini:
```python
add_usage(resp.usage_metadata.prompt_token_count, resp.usage_metadata.candidates_token_count)
```
If you skip this, the numbers are only estimates (about 4 characters per token) and are labelled `estimated`.

### Step 4 — `.gitignore`
Add one line:
```
logs/
```

### Step 5 — run the tests
```powershell
cd "C:\Users\Sayali Pawar\Desktop\GenAI_EXmate_04_clean"
.venv\Scripts\activate
pytest -q
```
All tests in `tests\test_production.py` should pass. If `ModuleNotFoundError: app`, run `python -m pytest -q` from the repo root.

### Step 6 — start the server (fresh, so the cache is empty)
```powershell
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000/docs`, try `/ask`, then open `http://127.0.0.1:8000/metrics`.

### Step 7 — measure real numbers
Second PowerShell window:
```powershell
cd "C:\Users\Sayali Pawar\Desktop\GenAI_EXmate_04_clean"
.venv\Scripts\activate
python scripts\measure.py
```
It prints a table and saves `docs\production_numbers.md`. For the live site:
```powershell
python scripts\measure.py https://YOUR-LIVE-URL
```

### Step 8 — fill the README and resume
Open `README.md` and `docs\resume.md` in VS Code. Press `Ctrl+Shift+F` and search `<<` and `{` to find every spot to fill.

### Step 9 — commit and push
```powershell
pytest -q
git add .
git status
git commit -m "day-13: logging, cache, input limits, injection test, README, resume"
git push
```
Check `git status` first: `logs/` and `.env` must NOT be listed.

---

## 5. Data you must provide (I cannot invent these)

| What | Where to get it | Goes into |
|---|---|---|
| Live URL | Your D12 deployment (Render / Hugging Face Spaces) | README top, `docs/resume.md` |
| Demo video link | Record a 1-2 min screen recording (below), upload to YouTube (unlisted) or Google Drive | README top |
| Latency p50/p95 cold and cached | `python scripts\measure.py` | README -> Production notes |
| Cache speed-up, hit rate | `python scripts\measure.py` | README -> Production notes, resume bullet 3 |
| Avg tokens per request | `python scripts\measure.py` (needs the `llm.py` edit for real numbers) | README -> Production notes |
| Over-long input result (expect 413) | `python scripts\measure.py` | README -> Production notes |
| Injection result (expect blocked=true) | `python scripts\measure.py` | README -> Production notes |
| Results table (config, chunk size, top-k, correct /15) | D8: `python eval\run_eval.py` winner table | README -> Results, resume bullet 1 |
| Number of passing tests | Output of `pytest -q` | README -> Production notes (CI row) |
| CI badge green | GitHub Actions page of the repo (D12) | README badge |
| Hosting platform name | D12 | `docs/resume.md` bullet 3 |
| Screenshot of the timeline card (optional) | Streamlit UI | README |

### What to show in the demo video (about 2 minutes)
1. Ask a normal question -> answer with citation.
2. Ask Q6 (data cannot answer) -> "I don't know".
3. Ask the family-of-7 room question -> room planner result.
4. Show the one-day timeline card with the train arrival marked.
5. Show `/metrics` or the CI green badge in one quick shot.

---

## 6. Done checklist

- [ ] `app\production.py` is in the repo
- [ ] `main.py` calls `install(app)` and `/ask` uses `guarded_answer`
- [ ] `llm.py` calls `add_usage(...)`
- [ ] `logs/` is in `.gitignore`
- [ ] `pytest -q` is green (includes the injection test)
- [ ] `GET /metrics` returns numbers
- [ ] `docs\production_numbers.md` exists and numbers are pasted into README
- [ ] README has live URL, video link, Mermaid diagram renders on GitHub, results table filled
- [ ] No `<<...>>` or `{...}` placeholders left in `README.md` and `docs\resume.md`
- [ ] `docs\resume.md` has 3 bullets with real numbers
- [ ] Pushed to GitHub, CI green
- [ ] Tracker updated for D13

---

## 7. Troubleshooting

| Problem | Fix |
|---|---|
| `Expand-Archive` says path not found | Zip is not in Downloads. Run `Get-ChildItem $env:USERPROFILE -Recurse -Filter "day13*.zip"` to find it, or use Right-click -> Extract All. |
| `ModuleNotFoundError: No module named 'app'` | Run from the repo root and use `python -m pytest -q`. |
| `/ask` returns 422 | Your request body field name is different. Change `req.question` and `FIELD` in `measure.py`. |
| `/metrics` shows `requests: 0` | You have not called `/ask` yet, or `install(app)` is missing in `main.py`. |
| Tokens show `estimated` | Add the `add_usage(...)` line in `llm.py`. |
| Cold and cached latency look the same | Server was not restarted before `measure.py`, so everything was already cached. Restart uvicorn and run again. |
| Mermaid diagram does not render | Keep the code fence exactly as ```` ```mermaid ````. GitHub renders it on the repo page. |
| `logs/requests.jsonl` shows in `git status` | Add `logs/` to `.gitignore`, then `git rm -r --cached logs`. |
| Cache returns an old answer after you changed data | Restart uvicorn (cache is in memory) or lower `CACHE_TTL_SECONDS`. |

---

## 8. Honest limits (also written in the project README)
- The cache lives in process memory: it is lost on restart and not shared between multiple servers.
- The injection guard is pattern-based. It catches common attacks, not every attack.
- Token numbers are only exact when `llm.py` reports provider usage.
- Free-tier hosting can cold-start, so the first request may be slow.