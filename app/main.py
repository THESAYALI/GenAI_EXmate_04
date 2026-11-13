"""app/main.py - ShirdiYatra FastAPI service (Day 4 + Day 6 /chat).

Run from the project root:
    uvicorn app.main:app --reload
Docs: http://127.0.0.1:8000/docs
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.chat import run_chat
from app.llm import LLMError
from app.smart_search import SmartSearch, load_default

QUESTIONS_FILE = Path(__file__).resolve().parent.parent / "data" / "questions.jsonl"

RECORDS = load_default()
SEARCH = SmartSearch(RECORDS)

app = FastAPI(title="ShirdiYatra API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionIn(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    asked_by: str | None = Field(default=None, max_length=80)


class ChatIn(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    prompt_version: Literal["v1", "v2"] = "v2"  # which task prompt to use


class ChatOut(BaseModel):
    answer: str
    confidence: Literal["high", "medium", "low"]
    follow_up: str


@app.get("/health")
def health():
    return {"status": "ok", "records": len(RECORDS)}


@app.get("/records")
def list_records(limit: int = Query(10, ge=1, le=100)):
    return RECORDS[:limit]


@app.get("/records/{record_id}")
def get_record(record_id: int):
    for r in RECORDS:
        if r["id"] == record_id:
            return r
    raise HTTPException(status_code=404, detail=f"Record {record_id} not found")


@app.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(5, ge=1, le=20)):
    return {"query": q, "results": SEARCH.search(q, top_k=limit)}


@app.post("/questions", status_code=201)
def post_question(payload: QuestionIn):
    entry = {"asked_at": datetime.now(timezone.utc).isoformat(), **payload.model_dump()}
    QUESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with QUESTIONS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"saved": True, "question": payload.question,
            "suggested_records": SEARCH.search(payload.question, top_k=3)}


@app.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn):
    """Answer a pilgrim's question with an LLM, using only the retrieved Sansthan records.

    Steps: 1) find the 3 best records  2) send them + the question to the LLM
           3) return JSON with answer, confidence (high/medium/low) and follow_up.
    """
    records = SEARCH.search(payload.question, top_k=3)
    try:
        return run_chat(payload.question, records, payload.prompt_version)
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
