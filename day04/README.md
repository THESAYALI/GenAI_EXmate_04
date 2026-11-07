## How to run

### 1. Setup
```powershell
cd "C:\Examate Git\GenAI_EXmate_04"
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Build the data
```powershell
python -m app.fetch      # downloads official pages into data/raw/
python -m app.ingest     # cleans them into data/records.json
```

### 3. Start the API
```powershell
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs for interactive docs.

### 4. Endpoints
| Method | Path | Description |
|---|---|---|
| GET | /health | service status and record count |
| GET | /records?limit=20 | list records (limit 1 to 100) |
| GET | /records/{id} | one record, 404 if missing |
| GET | /search?q=text&top_k=5 | TF-IDF + cosine ranked search |
| POST | /questions | save a visitor question (JSON: `{"question": "..."}`) |

Example:
```powershell
Invoke-RestMethod "http://127.0.0.1:8000/search?q=morning aarti"
```

### 5. Analysis
```powershell
python analysis\explore.py
```
Prints 3 facts about the records (topics, length of the temple day, data gaps).