# ShirdiYatra - Day 7 + Day 8: Semantic Search and RAG with Citations

**Student:** Sayali Rajendra Pawar (2124UCEF2015)  
**Product:** ShirdiYatra (Shirdi trip planner built from official Sai Sansthan pages)

**Day 7 task (Sat 14 Nov):**
- **S1** - `app/chunking.py` + `app/embed.py`: chunk the documents (keep source, page, title) and run semantic search for 10 questions; record hits in `eval/search_results.md`.
- **S2** - `app/vectorstore.py`: index all chunks into a persistent Chroma collection; expose `GET /search/semantic?q=`.

**Day 8 task (Mon 16 Nov):**
- **S1** - `app/rag.py` + `POST /ask`: answer from the retrieved chunks with citations; say "I don't know" for Q6 (the question the data cannot answer).
- **S2** - `eval/eval_set.json` (15 rows) + `eval/run_eval.py`: run 2 configs (top-k 3 vs top-k 6) and put a winner table in this README.

---

## 1. What these tasks do (simple words)

**Day 7 - semantic search.** The old `/search` finds only exact words. Semantic search finds **meaning**.
Example: *"when do we wake up for the morning prayer?"* has no word in common with *"Kakad Aarti 5:15 AM"*, but the meaning is the same, so semantic search finds it.

Steps: **cut text into chunks -> turn each chunk into numbers (embedding) -> save in Chroma -> turn the question into numbers -> find the nearest chunks.**

**Day 8 - RAG (Retrieval-Augmented Generation).** Search alone only returns text pieces. RAG goes one step further: it gives the best chunks to the LLM and asks it to write a **short answer using only those chunks**, with **citations** like `[1]`, so the reader can check the official source. If the pages do not contain the answer (weather, flight price, private hotel), the system says **"I don't know"** instead of guessing.

Steps: **question -> semantic search (top-k chunks) -> numbered context + strict system prompt -> LLM -> answer + citations.**

---

## 2. Where every file is saved

```
GenAI_EXmate_04_clean/
|-- .venv/                      virtual environment (not pushed)
|-- .env                        your API key (NOT pushed)
|-- .env.example                shows which keys are needed (pushed, no real keys)
|-- .gitignore                  must contain: data/chroma/  and  .env  and  .venv/
|-- requirements.txt            all libraries (run: pip freeze > requirements.txt)
|-- requirements_d7.txt         D7 libraries (chromadb, sentence-transformers)
|
|-- app/
|   |-- __init__.py             empty file, makes app a Python package
|   |-- main.py                 FastAPI app (D7: router lines, D8: POST /ask)
|   |-- llm.py                  D6 - LLM wrapper (Groq / Gemini), used by rag.py
|   |-- chunking.py             D7 S1 - splits documents into chunks
|   |-- embed.py                D7 S1 - text -> vectors
|   |-- vectorstore.py          D7 S2 - Chroma database + semantic_search()
|   |-- semantic_routes.py      D7 S2 - GET /search/semantic, POST /search/reindex
|   `-- rag.py                  D8 S1 - retrieve -> prompt -> answer + citations
|
|-- eval/
|   |-- questions.md            your 10 questions (from D5)
|   |-- run_search_eval.py      D7 S1 - runs the 10 questions through semantic search
|   |-- search_results.md       D7 S1 - OUTPUT of the script above
|   |-- eval_set.json           D8 S2 - 15 test questions for RAG
|   |-- run_eval.py             D8 S2 - compares 2 RAG configs
|   `-- eval_results.md         D8 S2 - OUTPUT: the winner table
|
|-- data/
|   |-- records.json            20 structured records (daily programme + rooms)
|   |-- raw/                    HTML pages downloaded by app/fetch.py
|   `-- chroma/                 vector database, created automatically (not pushed)
|
`-- day07/, day08/
    `-- README.md               this file
```

---

## 3. What each file does and how it works

### Day 7

#### `app/chunking.py` (S1)
- **Reads:** `data/records.json` (or `sample_records.json`) and every `.html / .txt / .md` in `data/raw/`.
- **HTML pages:** removes scripts/menus, splits by headings (h1-h3). Each heading section is one **page**; table rows are kept as text.
- **Splitting:** sentence-aware, about 600 characters per chunk, 1 sentence overlap so facts are not cut in half.
- **Each chunk has:** `id`, `text`, `source` (official URL), `page`, `title`, `chunk_index`.
- **Test it:** `python -m app.chunking` prints the number of chunks and the first five.

#### `app/embed.py` (S1)
- Uses the free local model **all-MiniLM-L6-v2** (sentence-transformers).
- `embed_texts(list)` and `embed_query(text)` return a list of 384 numbers per text.
- First run downloads the model (about 90 MB, internet needed once); later it works offline.
- **Test it:** `python -m app.embed`.

#### `app/vectorstore.py` (S2)
- `build_index()` - chunks everything, embeds it and saves it in a **persistent Chroma** collection named `shirdiyatra` inside `data/chroma/`.
- `semantic_search(query, k)` - embeds the question and returns the k nearest chunks with `score` (cosine similarity, 1.0 = same meaning), `title`, `source`, `page`, `text`.
- Persistent = saved on disk, no rebuild needed after restarting the server.
- **Build it:** `python -m app.vectorstore`.

#### `app/semantic_routes.py` (S2)
- `GET /search/semantic?q=your question&k=5` - returns the top matches as JSON.
- `POST /search/reindex` - rebuilds the Chroma collection after you change the data.
- If the collection is empty, the first search builds it automatically.

#### `eval/run_search_eval.py` (S1)
- Reads the 10 questions from `eval/questions.md` (numbered lines). If fewer than 10 are found, default Shirdi questions are used.
- Rebuilds the index, searches each question, writes the top 3 hits (score, title, page, source, snippet) to `eval/search_results.md`.
- Leaves a **Verdict** line under each question for you to fill in.

### Day 8

#### `app/rag.py` (S1)
- `retrieve(question, top_k)` - calls `vectorstore.semantic_search` and turns every hit into a simple dict (`n`, `text`, `source`, `title`, `page`, `score`).
- `ask(question, top_k=4)` - the main function:
  1. retrieves the top-k chunks;
  2. if nothing is found, returns the "I don't know" sentence without calling the LLM;
  3. builds a numbered context `[1] (title, source) text ...` and sends it with a strict system prompt (*answer ONLY from the context, cite chunk numbers, otherwise reply exactly with the "I don't know" sentence, never guess timings, prices or rules*);
  4. calls the LLM through `app/llm.py`;
  5. if the answer says "don't know", returns the fixed sentence with **no citations**;
  6. otherwise finds the `[n]` markers in the answer and returns only the chunks that were really cited.
- Returns: `{"answer": ..., "citations": [...], "retrieved": [...]}`.
- The fixed sentence is: *"I don't know based on the official Shirdi Sansthan pages I have."*
- If your function in `llm.py` has a different name, add it to the list inside `_call_llm()`.

#### `POST /ask` in `app/main.py` (S1)
```python
from pydantic import BaseModel
from app import rag

class AskIn(BaseModel):
    question: str
    top_k: int = 4

@app.post("/ask")
def ask(body: AskIn):
    return rag.ask(body.question, body.top_k)
```
Example request: `{ "question": "What time is the Kakad aarti?", "top_k": 4 }`

#### `eval/eval_set.json` (S2)
- **15 questions**: 12 the pages can answer and **3 they cannot** (weather forecast, flight price, private hotel price).
- Each row: `id`, `question`, `answerable` (true/false), `keywords` (words that should appear in the right chunk and answer).
- The keywords are generic (for example "kakad", "kopargaon", "bhakta niwas"). Compare them with your real records and adjust any that do not match.

#### `eval/run_eval.py` (S2)
- Runs all 15 questions through `rag.ask()` with two configs: **A: top_k = 3** and **B: top_k = 6**.
- Scores:
  - **Retrieval hit** - did the retrieved chunks contain an expected keyword? (answerable rows)
  - **Answer + citation** - did the answer contain an expected keyword and cite at least one chunk? (answerable rows)
  - **Correct "I don't know"** - did the unanswerable rows get an honest refusal?
- Writes the table and the **winner** to `eval/eval_results.md` and prints it.
- Waits 1 second between questions so free LLM rate limits are not hit.

---

## 4. What is required

| Requirement | Details |
|---|---|
| Python | 3.10 or newer |
| Libraries | `chromadb`, `sentence-transformers` (in `requirements_d7.txt`), plus your existing `fastapi`, `uvicorn`, and the library your `llm.py` uses (Groq or Gemini) |
| API key | Your own key in `.env` (never pushed). `.env.example` shows the variable names |
| Data | `data/records.json` and/or HTML files in `data/raw/` (made by D2/D3 `fetch.py`) |
| Internet | First time for the embedding model; every `/ask` call for the LLM |
| Disk | About 500 MB for the libraries and model |
| Existing files | `app/main.py` (D4), `app/llm.py` (D6), D7 files |

---

## 5. How to set up and run (Windows PowerShell, from the repo root)

```powershell
# 1. activate the environment
.\.venv\Scripts\Activate.ps1

# 2. install libraries
pip install -r requirements_d7.txt
pip freeze > requirements.txt
```

**3. Connect the routes in `app/main.py`**
```python
from app.semantic_routes import router as semantic_router
app.include_router(semantic_router)
# plus the POST /ask code from section 3 (Day 8)
```

```powershell
# 4. check the chunks and the index (Day 7)
python -m app.chunking
python -m app.vectorstore

# 5. D7 S1 - run the 10 questions (creates eval/search_results.md)
python eval\run_search_eval.py

# 6. start the API
uvicorn app.main:app --reload

# 7. D8 S2 - stop the server (Ctrl+C), then run the RAG evaluation
python eval\run_eval.py
```

Open in the browser:
- `http://127.0.0.1:8000/search/semantic?q=morning aarti time`
- `http://127.0.0.1:8000/docs` -> try **POST /ask** with a normal question and with *"What is the weather forecast for Shirdi next week?"* (it must answer "I don't know").

---

## 6. How the data flows

```
data/records.json + data/raw/*.html
            |  chunking.py   (split; keep source, page, title)
            v
         chunks --- embed.py ---> vectors (384 numbers each)
                                     |  vectorstore.py
                                     v
                            data/chroma/  (saved on disk)
                                     ^
 question --embed--> vector --nearest chunks (top-k)
                                     |
                                     v
                         rag.py: numbered context + system prompt
                                     |  llm.py
                                     v
                    answer with [1] [2] citations  (or "I don't know")
                                     |
                                     v
                                 POST /ask
```

---

## 7. Evaluation results

### 7.1 Day 7 - search check
Open `eval/search_results.md` and write **Good / Partial / Miss** for each question with a short reason. The question your data cannot answer should show low scores - mention that.

### 7.2 Day 8 - RAG configs
Paste the table from `eval/eval_results.md` here:

| Config | Retrieval hit | Answer + citation | Correct "I don't know" | Score |
|---|---|---|---|---|
| A: top_k=3 | _fill in_ | _fill in_ | _fill in_ | _fill in_ |
| B: top_k=6 | _fill in_ | _fill in_ | _fill in_ | _fill in_ |

**Winner:** _fill in_

**Why it won (write in your own words):** _for example: more chunks found the answer more often, or added noise and made the model cite wrong chunks._

---

## 8. Before you submit

1. Day 7: fill the **Verdict** lines in `eval/search_results.md`.
2. Day 8: run `python eval\run_eval.py`, paste the table in section 7.2 and write why the winner won.
3. Test `POST /ask` in `/docs` with one answerable question (answer + citations) and Q6 (must say "I don't know").
4. Make sure `.gitignore` contains `data/chroma/`, `.env` and `.venv/`, and that `.env` is **not** in `git status`.
5. Commit and push:
```powershell
git add .
git status
git commit -m "day-08: RAG with citations, /ask endpoint, eval of 2 configs"
git push
```
6. Check the commit on https://github.com/THESAYALI/GenAI_EXmate_04.

---

## 9. Common problems

| Problem | Fix |
|---|---|
| `No chunks found` | Put data in `data/records.json` or `data/raw/` first (run `app/fetch.py`). |
| `ModuleNotFoundError: app` | Run commands from the repo root and make sure `app/__init__.py` exists. |
| `No module named chromadb` / `sentence_transformers` | `python -m pip install -r requirements_d7.txt` with the venv activated. |
| Model download fails | Check the internet connection and run again. |
| `/search/semantic` gives 404 | The two router lines are missing in `app/main.py`. |
| `/ask` gives 404 | The `POST /ask` code is missing in `app/main.py`. |
| `No LLM function found in app/llm.py` | Add your function name to the list in `_call_llm()` in `app/rag.py`. |
| LLM error 401 / missing key | Check your key in `.env` and that the virtual environment is active. |
| LLM error 429 (rate limit) | Wait a minute and run again; `run_eval.py` already waits 1 second per question. |
| Every answer is "I don't know" | Check that `build_index()` ran and that `semantic_search` returns hits; test `/search/semantic` first. |
| Script blocked on activate | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`. |
| Results look outdated | Call `POST /search/reindex` or run `python -m app.vectorstore` again. |