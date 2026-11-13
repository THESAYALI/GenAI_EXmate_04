# ShirdiYatra - Day 7: Chunking, Embeddings and Semantic Search

**Student:** Sayali Rajendra Pawar (2124UCEF2015)  
**Product:** ShirdiYatra (Shirdi trip planner built from official Sai Sansthan pages)  
**Task (Sat 14 Nov):**
- **S1** - `app/chunking.py` + `app/embed.py`: chunk the documents (keep source, page, title) and run semantic search for 10 questions; record hits in `eval/search_results.md`.
- **S2** - `app/vectorstore.py`: index all chunks into a persistent Chroma collection; expose `GET /search/semantic?q=`.

---

## 1. What this task does (simple words)

The old `/search` finds only exact words. Semantic search finds **meaning**.
Example: the question *"when do we wake up for the morning prayer?"* has no word in common with
*"Kakad Aarti 5:15 AM"*, but the meaning is the same, so semantic search finds it.

Steps: **cut text into chunks -> turn each chunk into numbers (embedding) -> save in Chroma -> turn the question into numbers -> find the nearest chunks.**

---

## 2. Where every file is saved

```
GenAI_EXmate_04_clean/
|-- .venv/                      virtual environment (not pushed)
|-- .gitignore                  must contain: data/chroma/  and  .env  and  .venv/
|-- requirements.txt            all libraries (run: pip freeze > requirements.txt)
|-- requirements_d7.txt         new libraries for D7 (chromadb, sentence-transformers)
|
|-- app/
|   |-- __init__.py             empty file, makes app a Python package
|   |-- main.py                 FastAPI app (existing; add 2 router lines, see section 5)
|   |-- chunking.py             S1  - splits documents into chunks
|   |-- embed.py                S1  - text -> vectors
|   |-- vectorstore.py          S2  - Chroma database + semantic_search()
|   `-- semantic_routes.py      S2  - GET /search/semantic and POST /search/reindex
|
|-- eval/
|   |-- questions.md            your 10 questions (from D5)
|   |-- run_search_eval.py      S1  - runs the 10 questions
|   `-- search_results.md       S1  - OUTPUT, created when you run the script
|
|-- data/
|   |-- records.json            20 structured records (daily programme + rooms)
|   |-- raw/                    HTML pages downloaded by app/fetch.py
|   `-- chroma/                 vector database, created automatically (not pushed)
|
`-- day07/
    `-- README.md               this file
```

---

## 3. What each file does and how it works

### `app/chunking.py` (S1)
- **Reads:** `data/records.json` (or `sample_records.json`) and every `.html / .txt / .md` in `data/raw/`.
- **HTML pages:** removes scripts/menus, splits by headings (h1-h3). Each heading section is one **page**; table rows are kept as text.
- **Splitting:** sentence-aware, about 600 characters per chunk, 1 sentence overlap so facts are not cut in half.
- **Each chunk has:** `id`, `text`, `source` (official URL), `page`, `title`, `chunk_index`.
- **Test it:** `python -m app.chunking` prints the number of chunks and the first five.

### `app/embed.py` (S1)
- Uses the free local model **all-MiniLM-L6-v2** (sentence-transformers).
- `embed_texts(list)` and `embed_query(text)` return a list of 384 numbers per text.
- First run downloads the model (about 90 MB, internet needed once); later it works offline.
- **Test it:** `python -m app.embed`.

### `app/vectorstore.py` (S2)
- `build_index()` - chunks everything, embeds it and saves it in a **persistent Chroma** collection named `shirdiyatra` inside `data/chroma/`.
- `semantic_search(query, k)` - embeds the question and returns the k nearest chunks with `score` (cosine similarity, 1.0 = same meaning), `title`, `source`, `page`, `text`.
- Persistent = saved on disk, no rebuild needed after restarting the server.
- **Build it:** `python -m app.vectorstore`.

### `app/semantic_routes.py` (S2)
- `GET /search/semantic?q=your question&k=5` - returns the top matches as JSON.
- `POST /search/reindex` - rebuilds the Chroma collection after you change the data.
- If the collection is empty, the first search builds it automatically.

### `eval/run_search_eval.py` (S1)
- Reads the 10 questions from `eval/questions.md` (numbered lines). If fewer than 10 are found, default Shirdi questions are used.
- Rebuilds the index, searches each question, writes the top 3 hits (score, title, page, source, snippet) to `eval/search_results.md`.
- Leaves a **Verdict** line under each question for you to fill in.

---

## 4. What is required

| Requirement | Details |
|---|---|
| Python | 3.10 or newer |
| Libraries | `chromadb`, `sentence-transformers` (in `requirements_d7.txt`), plus your existing `fastapi`, `uvicorn` |
| Data | `data/records.json` and/or HTML files in `data/raw/` (made by D2/D3 `fetch.py`) |
| Internet | Only the first time, to download the embedding model |
| Disk | About 500 MB for the libraries and model |
| Existing files | `app/main.py` (FastAPI app from D4) |

---

## 5. How to set up and run (Windows PowerShell, from the repo root)

```powershell
# 1. activate the environment
.\.venv\Scripts\Activate.ps1

# 2. install new libraries
pip install -r requirements_d7.txt
pip freeze > requirements.txt
```

**3. Connect the router in `app/main.py`** (add after `app = FastAPI(...)`):
```python
from app.semantic_routes import router as semantic_router
app.include_router(semantic_router)
```

```powershell
# 4. check the chunks
python -m app.chunking

# 5. build the Chroma index
python -m app.vectorstore

# 6. S1 - run the 10 questions (creates eval/search_results.md)
python eval/run_search_eval.py

# 7. S2 - start the API
uvicorn app.main:app --reload
```

Open in the browser:
- `http://127.0.0.1:8000/search/semantic?q=morning aarti time`
- `http://127.0.0.1:8000/docs` (try the endpoint there)

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
 question --embed--> vector --nearest chunks--> GET /search/semantic?q=
```

---

## 7. Before you submit

1. Open `eval/search_results.md` and write **Good / Partial / Miss** for each question and a short reason. The question your data cannot answer should show low scores - mention that.
2. Make sure `.gitignore` contains `data/chroma/`.
3. Commit and push:
```powershell
git add .
git commit -m "day-07: chunking, embeddings, Chroma semantic search"
git push
```

---

## 8. Common problems

| Problem | Fix |
|---|---|
| `No chunks found` | Put data in `data/records.json` or `data/raw/` first (run `app/fetch.py`). |
| `ModuleNotFoundError: app` | Run commands from the repo root and make sure `app/__init__.py` exists. |
| Model download fails | Check the internet connection and run again. |
| `/search/semantic` gives 404 | The two router lines are missing in `app/main.py`. |
| Script blocked on activate | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`. |
| Results look outdated | Call `POST /search/reindex` or run `python -m app.vectorstore` again. |