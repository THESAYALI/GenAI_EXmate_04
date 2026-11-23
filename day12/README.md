[![CI](https://github.com/THESAYALI/GenAI_EXmate_04/actions/workflows/ci.yml/badge.svg)](https://github.com/THESAYALI/GenAI_EXmate_04/actions/workflows/ci.yml)



New-Item -ItemType Directory -Force day12 | Out-Null
@'
# Day 12 - CI/CD and Deployment (ShirdiYatra)

**Date:** Fri 20 Nov 2026
**Project:** ShirdiYatra (slug `sanjivani-sj-50-shirdiyatra`), a Shirdi trip-planning assistant
**Repo:** https://github.com/THESAYALI/GenAI_EXmate_04



---

## 1. Day 12 task

**S1:** `.github/workflows/ci.yml` (ruff, pytest, docker build); green badge in README; 1 PR from a feature branch merged after CI is green.

**S2:** deploy ShirdiYatra (Render / Hugging Face Spaces); live URL in README and in the tracker; `/health` works publicly.

### Checklist
- [ ] `ci.yml` exists in `.github/workflows/`
- [ ] CI runs ruff, pytest and docker build
- [ ] CI badge is at the top of the main README and shows green
- [ ] One PR from `feature/day-12-ci` merged after CI was green
- [ ] App deployed and live
- [ ] Live URL in main README
- [ ] Live URL in the course tracker
- [ ] `<live-url>/health` opens publicly (test in an incognito window)

---

## 2. Where the files are

Repo root: `C:\Users\Sayali Pawar\Desktop\GenAI_EXmate_04_clean`

    GenAI_EXmate_04_clean/
    |
    |-- .github/
    |   `-- workflows/
    |       `-- ci.yml                  CI pipeline (S1)
    |-- app/                            FastAPI application (main.py, rag.py, llm.py, tools.py, ...)
    |-- data/                           records and question data used by /health, /records, /search
    |-- tests/
    |   |-- conftest.py                 `client` fixture using FastAPI TestClient
    |   |-- test_health.py              /health returns 200 and JSON
    |   |-- test_api.py                 /records list, get by id, not found
    |   |-- test_project_files.py       checks ci.yml, Dockerfile, .env.example exist
    |   `-- (other existing tests)      test_day06.py, test_ingest.py, test_tools.py
    |-- day12/
    |   `-- README.md                   this file
    |-- Dockerfile                      container image (uvicorn, uses $PORT, default 8000)
    |-- .dockerignore                   keeps .venv, .env, data/chroma, tests, etc. out of the image
    |-- ruff.toml                       lint rules
    |-- requirements.txt                full project dependencies
    |-- requirements-dev.txt            requirements.txt + pytest + ruff (used by CI)
    |-- render.yaml                     optional Render blueprint
    |-- .env.example                    template for API keys (committed)
    |-- .env                            real API keys (NEVER committed, in .gitignore)
    `-- README.md                       main project README (badge + live URL go here)

---

## 3. What each Day 12 file does

| File | Location | Purpose |
|------|----------|---------|
| `ci.yml` | `.github/workflows/` | GitHub Actions pipeline: runs on every push and pull request to `main` |
| `ruff.toml` | root | Lint config: rules E and F, ignores E501 (line length) and E741 (variable `l`), excludes `.venv`, `day*`, `data/chroma`, `Rag Application` |
| `requirements-dev.txt` | root | Installs `requirements.txt` plus `pytest` and `ruff` |
| `Dockerfile` | root | Builds the image: Python 3.12 slim, installs requirements, copies `app/` and `data/`, runs as non-root user, starts `uvicorn app.main:app` on `$PORT` (default 8000), has a HEALTHCHECK on `/health` |
| `.dockerignore` | root | Excludes `.git`, `.venv`, `.env`, `data/chroma`, tests, docs from the image |
| `render.yaml` | root | Optional Render blueprint (Docker, free plan, health check `/health`) |
| `tests/conftest.py` | tests | Provides the `client` fixture (FastAPI `TestClient`) |
| `tests/test_health.py` | tests | Checks `/health` returns HTTP 200 and a JSON object |
| `tests/test_api.py` | tests | Checks `/records`, `/records/{id}` and 404 for unknown id |
| `tests/test_project_files.py` | tests | Checks `ci.yml`, `Dockerfile` and `.env.example` exist |

Fixes made to existing code during Day 12:
- `app/main.py`: `app.include_router(rag_router)` moved to after `app = FastAPI(...)` (ruff F821).
- `app/llm.py`: `FakeLLM` test double added, left over from an older version's tests.
- Old Flask-style tests (`test_records.py`, `test_search.py`) removed and replaced with `test_api.py`.

---

## 4. What is needed (requirements)

### On your PC
- Python 3.12 or newer with the project `.venv`
- Git, and a GitHub account (repo `THESAYALI/GenAI_EXmate_04`)
- VS Code (optional)
- Docker Desktop (optional; CI builds the image for you)

### Accounts
- GitHub (CI, PR, badge)
- Hugging Face (deploy option A, recommended) or Render (option B)

### Secrets (never commit these)
Names are the ones in your `.env`, for example `GROQ_API_KEY` and `GEMINI_API_KEY`. They go into the platform's secret/environment settings, not into git.

### Python packages
- Runtime: everything in `requirements.txt` (FastAPI, uvicorn, chromadb, sentence-transformers, langgraph, ...)
- CI/dev: `requirements-dev.txt`

---

## 5. How CI works (S1)

File: `.github/workflows/ci.yml`. Triggers: push to `main`, and any pull request into `main`.

**Job 1: ruff + pytest**
1. Check out the code
2. Set up Python 3.11 with pip cache
3. `pip install -r requirements-dev.txt`
4. `ruff check .` (lint)
5. `pytest -q` (tests)

**Job 2: docker build + /health** (runs only if Job 1 passes)
1. Check out the code
2. `docker build -t shirdiyatra:ci .`
3. Start the container and call `/health` until it answers (up to 60 seconds)

The first CI run is slow (about 5 to 10 minutes) because `requirements.txt` includes torch and chromadb.

### Run the same checks locally
    .venv\Scripts\activate
    pip install -r requirements-dev.txt
    ruff check .
    pytest -q

Both must pass before pushing.

---

## 6. Step by step: branch, PR, merge

    git checkout -b feature/day-12-ci
    git add .github ruff.toml requirements-dev.txt render.yaml Dockerfile .dockerignore tests app/main.py app/llm.py
    git status
    git commit -m "day-12: add CI workflow, ruff config, Dockerfile fixes, update tests for FastAPI"
    git push -u origin feature/day-12-ci

1. Open https://github.com/THESAYALI/GenAI_EXmate_04/pull/new/feature/day-12-ci and click **Create pull request**.
2. Open the **Actions** tab and wait for both jobs to turn green.
3. If a job fails, open it, copy the red error text and fix it.
4. Click **Merge pull request** only after both jobs are green.
5. Switch back and update:

        git checkout main
        git pull

6. Add the CI badge as the first line of the main README (after the Hugging Face header, if you use one):

        [![CI](https://github.com/THESAYALI/GenAI_EXmate_04/actions/workflows/ci.yml/badge.svg)](https://github.com/THESAYALI/GenAI_EXmate_04/actions/workflows/ci.yml)

---

## 7. Deploy (S2)

### Option A: Hugging Face Spaces (recommended)
The project uses torch, sentence-transformers and chromadb, so the image is large. Hugging Face gives about 16 GB RAM free; Render's free plan has only 512 MB and will probably crash.

1. Go to https://huggingface.co/new-space. Name: `shirdiyatra`, SDK: **Docker** (Blank), visibility: Public.
2. Put this at the very top of the main `README.md`, above the badge:

        ---
        title: ShirdiYatra
        sdk: docker
        app_port: 8000
        ---

3. Commit and push it to GitHub.
4. Push to the Space (the password is a Hugging Face **Write** access token):

        git remote add space https://huggingface.co/spaces/yourusername/shirdiyatra
        git push space main --force

5. In the Space open **Settings, Variables and secrets** and add your API keys (names from `.env`).
6. Wait for the build to finish. The live URL is `https://PASTE-YOUR-REAL-URL-HERE`.

### Option B: Render
1. https://render.com, then **New +**, **Web Service**, connect the GitHub repo.
2. Runtime: **Docker**. Plan: **Free**. Health Check Path: `/health`.
3. Add the API keys under **Environment**.
4. Create the service and wait for the deploy.

### Verify the deploy
    curl https://PASTE-YOUR-REAL-URL-HERE/health

Also open the same URL in an incognito window. It must load without logging in.

### Known limits on the live site
- `/health`, `/records` and `/search` work.
- Semantic search and `/ask` need the Chroma index. `data/chroma/` is in `.gitignore`, so those endpoints may not work live unless the index is rebuilt there.
- Free Render services sleep when idle, so the first request can take about 50 seconds.

---

## 8. Live links (fill in after deploy)

- **Live app:** https://PASTE-YOUR-REAL-URL-HERE
- **Health:** https://PASTE-YOUR-REAL-URL-HERE/health
- **API docs:** https://PASTE-YOUR-REAL-URL-HERE/docs
- **Tracker:** paste the live app URL in the course tracker

---

## 9. Troubleshooting

| Problem | Fix |
|---------|-----|
| `ruff` shows `F821 Undefined name app` | `app.include_router(...)` must come after `app = FastAPI(...)` in `app/main.py` |
| pytest: `cannot import name FakeLLM` | Old test files; `tests/conftest.py` should only use `TestClient` and `app` |
| pytest: `get_json` not found, `/api/records` 404 | Old Flask-style tests; use `resp.json()` and `/records` |
| pytest: `No module named app.search` | Old test; delete `tests/test_search.py` |
| `git add` says `pathspec did not match` | One of the listed files does not exist; remove it from the command |
| CI Docker job fails at `/health` | Check that `data/` exists in the repo and `requirements.txt` has `fastapi` and `uvicorn` |
| Docker command not found locally | Docker is not installed; CI builds the image instead |
| Render deploy crashes or runs out of memory | Use Hugging Face Spaces instead |
| `.env` appears in `git status` | Stop; add `.env` to `.gitignore` before committing |
| Browser saves `ci (1).yml` or renames dotfiles | Rename the file, or create it with PowerShell |

---

## 10. Final submission checklist

1. `ruff check .` and `pytest -q` pass locally
2. PR from `feature/day-12-ci` merged after green CI
3. Green CI badge visible at the top of the main README
4. App deployed, and `/health` opens in an incognito window
5. Live URL added to the main README
6. Live URL pasted in the tracker
7. This file is committed:

        git add day12/README.md
        git commit -m "day-12: add day12 README"
        git push
'@ | Set-Content -Encoding UTF8 day12\README.md



