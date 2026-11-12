# Day 4 - API, analysis, smart search

| Task | Where | Status |
|---|---|---|
| S1: FastAPI service with GET /health, /records?limit=, /records/{id} (404 if missing), /search?q=, POST /questions | `../app/main.py` | Code done; **not run** (FastAPI was missing where this was checked) |
| S1: README "How to run" | `../README.md` | Done |
| S2: `analysis/explore.py` prints 3 facts with pandas | `../analysis/explore.py` | Done and run |
| S2: `app/smart_search.py` ranks records with TF-IDF + cosine and powers /search | `../app/smart_search.py` | Done and run |
| Tag `week-1` | - | **Missing** (needs a commit first, see root README) |

How to run (from the project root):

```
pip install -r requirements.txt
uvicorn app.main:app --reload       # open http://127.0.0.1:8000/docs
python analysis/explore.py
python -m app.smart_search shej aarti
```

POST /questions saves to `data/questions.jsonl` (git-ignored) and returns 3 suggested records.
