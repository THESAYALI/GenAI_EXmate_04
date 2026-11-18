# ShirdiYatra

ShirdiYatra is a GenAI assistant that helps pilgrims plan a visit to Shirdi. It can look up places (temples, garden, museum, food, nearby trips), search them, answer questions using an LLM, and call an agent tool to build a trip plan. It has a Python backend and a Streamlit web UI.

## Features

- Place records for Shirdi and nearby destinations
- Keyword and semantic search over the records
- `/health` endpoint to check that the API is running
- `/ask` endpoint: answers questions with an LLM, using retrieved records as context
- Agent tool that can build an itinerary (the agent loop decides when to call it)
- Streamlit UI for searching and asking questions
- Automated tests (pytest) that use a fake LLM, so no API key or internet is needed
- Docker support: API and UI start together with `docker compose up`

## Project structure

```
GenAI_EXmate_04_clean/
├── app/
│   ├── main.py              # API entry point (routes such as /health and /ask)
│   ├── agent_api.py         # agent endpoints
│   ├── agent_loop.py        # agent loop that decides when to call tools
│   ├── tools.py             # agent tools
│   ├── records.py           # place records
│   ├── retrieval.py         # retrieval of relevant records
│   ├── smart_search.py      # search logic
│   ├── rag.py               # retrieval-augmented answering
│   ├── llm.py               # LLM client
│   ├── models.py            # data models
│   └── ...                  # chunking, embed, ingest, vectorstore, etc.
├── tests/                   # pytest tests
├── streamlit_app.py         # Streamlit UI (use your own file name)
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml           # ruff and pytest settings
└── README.md
```

## Requirements

- Python 3.10 or newer
- Docker Desktop (only for the Docker option)
- An LLM API key, only if you want real model answers (tests do not need one)

## Setup

1. Open a terminal in the project folder.
2. Create and activate a virtual environment.

   Windows (PowerShell):
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   Mac or Linux:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the packages:
   ```bash
   pip install -r requirements.txt
   ```

4. If you use a real LLM, set your key in a `.env` file or in the terminal. Never commit this file.
   ```
   API_KEY=your-key-here
   ```

## Run locally

Start the API (use the command that matches your framework):

```bash
# FastAPI
uvicorn app.main:app --reload --port 8000

# Flask
flask --app app.main run --port 8000
```

In a second terminal, start the UI:

```bash
streamlit run streamlit_app.py
```

- API health check: http://localhost:8000/health
- UI: http://localhost:8501

## Run with Docker

Make sure Docker Desktop is running, then from the project folder:

```bash
docker compose up --build
```

- UI: http://localhost:8501
- API: http://localhost:8000/health

To stop everything, press `Ctrl+C` and then run:

```bash
docker compose down
```

The compose file starts two services: `api` (the backend) and `ui` (Streamlit). The UI starts after the API reports healthy.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Returns `{"status": "ok"}` when the API is up |
| GET | `/records` | List place records |
| GET | `/search?q=...` | Search the records |
| POST | `/ask` | Send `{"question": "..."}` and get an answer |

Update the paths above if your routes are named differently.

## Tests

The tests live in `tests/` and cover records, search, `/health`, `/ask` (with a fake LLM) and the agent tool. They run without network access or an API key.

```bash
pytest
```

## Lint

```bash
ruff check .
```

This should print `All checks passed!`.

## Troubleshooting

- **Port already in use:** stop the other program using port 8000 or 8501, or change the port numbers in `docker-compose.yml`.
- **`docker compose` not found:** install or start Docker Desktop.
- **UI cannot reach the API in Docker:** inside Docker the UI must call `http://api:8000`, not `localhost`.
- **Tests fail with an import error:** run `pytest` from the project root, with your virtual environment active.
- **`ModuleNotFoundError`:** run `pip install -r requirements.txt` again.

## Author

Sayali Rajendra Pawar, Reg No 2124UCEF2015