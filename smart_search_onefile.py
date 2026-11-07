import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "sample_records.json"
QUESTIONS_FILE = BASE_DIR / "data" / "questions.jsonl"


def load_records() -> list[dict]:
    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    items = raw["records"] if isinstance(raw, dict) else raw
    return [{"id": i, **r} if "id" not in r else r
            for i, r in enumerate(items, start=1)]


# ----------------------------------------------------------------------------
# Smart search: TF-IDF + cosine similarity
# ----------------------------------------------------------------------------
TEXT_FIELDS = ("topic", "place_or_service", "timing", "rule_or_tip")


def record_text(record: dict) -> str:
    return " ".join(str(record.get(f, "")) for f in TEXT_FIELDS)


class SmartSearch:
    def __init__(self, records: list[dict]):
        self.records = records
        self.vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), sublinear_tf=True
        )
        self.matrix = self.vectorizer.fit_transform(
            [record_text(r) for r in records]
        )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        if not query or not query.strip() or not self.records:
            return []
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).ravel()
        ranked = scores.argsort()[::-1][:top_k]
        return [
            {**self.records[i], "score": round(float(scores[i]), 4)}
            for i in ranked
            if scores[i] > 0  
        ]
RECORDS = load_records()
SEARCH = SmartSearch(RECORDS)

app = FastAPI(title="ShirdiYatra API", version="0.1.0")


class QuestionIn(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)
    asked_by: str | None = Field(default=None, max_length=80)


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
    entry = {
        "asked_at": datetime.now(timezone.utc).isoformat(),
        **payload.model_dump(),
    }
    QUESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with QUESTIONS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {
        "saved": True,
        "question": payload.question,
        "suggested_records": SEARCH.search(payload.question, top_k=3),
    }

def explore():
    import pandas as pd

    df = pd.DataFrame(RECORDS)
    df["cost_inr"] = pd.to_numeric(df["cost_inr"], errors="coerce")

    print(f"Fact 1: {len(df)} records across {df['topic'].nunique()} topics.")
    print(df["topic"].value_counts().to_string(), "\n")


    priced = df.dropna(subset=["cost_inr"])
    print(f"Fact 2: {len(priced)} records have a cost "
          f"({len(df) - len(priced)} without one).")
    if not priced.empty:
        cheapest = priced.loc[priced["cost_inr"].idxmin()]
        costliest = priced.loc[priced["cost_inr"].idxmax()]
        print(f"  Cheapest : {cheapest['place_or_service']} - Rs {cheapest['cost_inr']:.0f}")
        print(f"  Costliest: {costliest['place_or_service']} - Rs {costliest['cost_inr']:.0f}")
        print(f"  Average  : Rs {priced['cost_inr'].mean():.0f}\n")

    
    domains = df["source_url"].map(lambda u: urlparse(str(u)).netloc)
    print(f"Fact 3: {df['source_url'].nunique()} distinct source pages "
          f"on {domains.nunique()} domain(s).")
    print(domains.value_counts().to_string())

if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else "serve"

    if command == "serve":
        import uvicorn
        uvicorn.run("shirdiyatra:app", host="127.0.0.1", port=8000, reload=True)
    elif command == "explore":
        explore()
    elif command == "search":
        query = " ".join(sys.argv[2:]) or "family room"
        for hit in SEARCH.search(query, top_k=5):
            print(f"{hit['score']:.3f}  #{hit['id']}  {hit.get('place_or_service')}")
    else:
        print(__doc__)