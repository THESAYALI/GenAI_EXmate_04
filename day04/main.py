"""ShirdiYatra FastAPI service."""
import json
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from app.smart_search import SmartSearch

BASE_DIR = Path(__file__).resolve().parent.parent
RECORDS_FILE = BASE_DIR / "data" / "records.json"
QUESTIONS_FILE = BASE_DIR / "data" / "questions.jsonl"

state = {"records": [], "engine": None}
write_lock = threading.Lock()


def load_records() -> list:
    try:
        raw = json.loads(RECORDS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise RuntimeError(
            f"Cannot load {RECORDS_FILE}: {e}. Run 'python -m app.ingest' first."
        )
    # id = position in the file, starting at 1
    return [{"id": i + 1, **rec} for i, rec in enumerate(raw)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["records"] = load_records()
    state["engine"] = SmartSearch(state["records"])
    yield


app = FastAPI(
    title="ShirdiYatra API",
    description="Official Shirdi Sansthan information: timings, facilities, FAQs.",
    version="1.0.0",
    lifespan=lifespan,
)


class QuestionIn(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    name: str | None = Field(default=None, max_length=80)


def run_search(query: str, top_k: int) -> list:
    hits = state["engine"].search(query, top_k=top_k)
    return [
        {"score": round(score, 4), **state["records"][idx]}
        for idx, score in hits
    ]


@app.get("/health")
def health():
    return {"status": "ok", "records": len(state["records"])}


@app.get("/records")
def list_records(limit: int = Query(20, ge=1, le=100)):
    records = state["records"][:limit]
    return {"count": len(records), "total": len(state["records"]), "records": records}


@app.get("/records/{record_id}")
def get_record(record_id: int):
    for rec in state["records"]:
        if rec["id"] == record_id:
            return rec
    raise HTTPException(status_code=404, detail=f"Record {record_id} not found")


@app.get("/search")
def search(
    q: str = Query(..., min_length=2, description="search text"),
    top_k: int = Query(5, ge=1, le=20),
):
    results = run_search(q, top_k)
    return {"query": q, "count": len(results), "results": results}


@app.post("/questions", status_code=201)
def post_question(payload: QuestionIn):
    entry = {
        "question": payload.question.strip(),
        "name": payload.name,
        "received_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        with write_lock:
            QUESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with QUESTIONS_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Could not save question: {e}")

    return {"saved": True, **entry, "top_matches": run_search(entry["question"], 3)}