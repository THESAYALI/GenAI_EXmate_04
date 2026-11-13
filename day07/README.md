# ShirdiYatra - Day 7: Chunking, Embeddings and Semantic Search

**Student:** Sayali Rajendra Pawar (2124UCEF2015) | **Product:** ShirdiYatra | **Task:** D7, Sat 14 Nov

## The task in one line
Cut our Shirdi documents into small pieces (**chunks**), turn each piece into numbers (**embeddings**),
store them in a **Chroma** database, and search by *meaning* through `GET /search/semantic?q=`.

## Why semantic search?
Keyword search (D4 `/search`) only finds the exact words. If someone asks *"when do we wake up for the
morning prayer?"*, the data says *"Kakad Aarti 5:15 AM"* - no shared words, but the same meaning.
Embeddings put similar meanings close together, so the right chunk is found anyway.

## Files in this task

| File | Part | What it does |
|---|---|---|
| `app/chunking.py` | S1 | Reads `data/records.json` and `data/raw/*` (HTML/txt/md), splits into chunks of about 600 characters (sentence-aware, 1 sentence overlap). Each chunk keeps **source, page, title**. |
| `app/embed.py` | S1 | `embed_texts()` / `embed_query()` using `all-MiniLM-L6-v2` (free, local, 384-number vectors). |
| `app/vectorstore.py` | S2 | Persistent Chroma collection `shirdiyatra` in `data/chroma/`. `build_index()` stores all chunks, `semantic_search()` finds the closest ones. |
| `app/semantic_routes.py` | S2 | FastAPI router: `GET /search/semantic?q=` and `POST /search/reindex`. |
| `eval/run_search_eval.py` | S1 | Runs your 10 questions and writes `eval/search_results.md`. |
| `eval/search_results.md` | S1 | **Generated** output: top 3 hits per question + your verdict. |
| `requirements_d7.txt` | - | New libraries: `chromadb`, `sentence-transformers`. |

## How it flows

```
data/records.json + data/raw/*.html
          |  chunking.py   (split, keep source/page/title)
          v
       chunks --- embed.py ---> vectors (384 numbers each)
                                   |  vectorstore.py
                                   v
                          data/chroma/ (persistent)
                                   ^
 question --embed--> vector --find nearest--> GET /search/semantic?q=
```

### Key ideas (for your viva)
- **Chunk:** a small piece of text. Small = precise matches; too small loses context, so we use overlap.
- **Embedding:** a list of numbers capturing meaning; similar sentences get similar numbers.
- **Cosine similarity / score:** how close two vectors are. 1.0 = same meaning, near 0 = unrelated.
- **Persistent:** `data/chroma/` is saved on disk, so no rebuild after restarting the server.
- **Metadata:** `source`, `page`, `title` let us show *where* an answer came from (important for trust).

## Setup (Windows PowerShell, from repo root)

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements_d7.txt
pip freeze > requirements.txt
```
Copy the files into your repo keeping the same folders (`app/`, `eval/`). Make sure `app/__init__.py` exists.

### Connect the router to your API (`app/main.py`)
```python
from app.semantic_routes import router as semantic_router
app.include_router(semantic_router)
```

### Run
```powershell
python -m app.chunking                # preview chunks (check source/page/title)
python -m app.vectorstore             # build the Chroma index
python eval/run_search_eval.py        # S1: creates eval/search_results.md
uvicorn app.main:app --reload         # S2: open http://127.0.0.1:8000/search/semantic?q=morning aarti time
```
Also try `http://127.0.0.1:8000/docs`.

### Before committing
1. Open `eval/search_results.md`, write **Good / Partial / Miss** for each question. Q6 (the one the data cannot answer) should show low scores - say so.
2. Add `data/chroma/` to `.gitignore` (it is rebuilt by `python -m app.vectorstore`).
3. Commit:
```powershell
git add .
git commit -m "day-07: chunking, embeddings, Chroma semantic search"
git push
```

## Notes
- First run downloads the model (~90 MB, internet needed once).
- If `eval/questions.md` is missing or has fewer than 10 numbered questions, default ShirdiYatra questions are used - replace them with your own.
- If your `fetch.py` saves HTML under different names, edit `KNOWN_SOURCES` in `chunking.py` so `source` shows the official URL.