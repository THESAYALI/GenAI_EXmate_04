"""
D8 - S1: RAG over ShirdiYatra records.

POST /ask  ->  retrieve chunks  ->  answer ONLY from those chunks, with citations.
If the chunks do not cover the question (e.g. Q6), the answer is "I don't know".

Works out of the box (pure Python, no API key needed):
  * chunking  : records are packed into chunks of ~chunk_size words (source kept)
  * retrieval : BM25 keyword ranking, top_k chunks
  * answer    : extractive (best matching lines) + [1] [2] citations
  * optional  : set use_llm=true (or RAG_USE_LLM=1) to let app/llm.py write the
                answer from the same chunks. The "I don't know" gate runs BEFORE
                the LLM, so unanswerable questions never reach it.

CLI test:   python -m app.rag "What time is the Kakad aarti?"
"""
import json
import math
import os
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_CANDIDATES = [ROOT / "data" / "records.json", ROOT / "data" / "sample_records.json"]

IDK = ("I don't know. The ShirdiYatra data I have does not cover that, so I won't guess. "
       "Please check sai.org.in or ask the Sansthan office.")

STOPWORDS = set("""
a an the is are was were be been am do does did can could should would will shall may might
of in on at to for from by with about into over under and or but if then than so as it its
this that these those i we you he she they them our your my me us what which who whom when
where why how any some there here also not no yes please tell give get need want know
""".split())
# words that appear in almost every record - they must not count as "the question is covered"
GENERIC = {"shirdi", "sansthan", "sai", "baba", "temple", "trust", "yatra", "shri"}

MIN_SCORE = 1.0       # BM25 score of best chunk must reach this
MIN_COVERAGE = 0.5    # share of question keywords that must appear in best chunk


# ----------------------------------------------------------------- data
def load_records():
    for p in DATA_CANDIDATES:
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data = data.get("records", [])
            return data
    raise FileNotFoundError("No data/records.json or data/sample_records.json found")


def record_to_line(rec):
    parts = [str(rec.get("topic", "")).strip(), str(rec.get("place_or_service", "")).strip()]
    line = " | ".join(p for p in parts if p)
    if rec.get("timing"):
        line += f" | timing: {rec['timing']}"
    if rec.get("cost_inr") not in (None, "", 0):
        line += f" | cost: Rs {rec['cost_inr']}"
    if rec.get("rule_or_tip"):
        line += f" | tip: {rec['rule_or_tip']}"
    return line


# ----------------------------------------------------------------- chunking
def build_chunks(records, chunk_size):
    """Pack record lines into chunks of at most ~chunk_size words (a record is never split)."""
    chunks, cur, words = [], [], 0

    def flush():
        nonlocal cur, words
        if cur:
            chunks.append({
                "chunk_id": len(chunks),
                "text": "\n".join(x["text"] for x in cur),
                "lines": cur,
                "source_url": cur[0]["source_url"],
            })
        cur, words = [], 0

    for i, rec in enumerate(records):
        text = record_to_line(rec)
        n = len(text.split())
        if cur and words + n > chunk_size:
            flush()
        cur.append({
            "text": text,
            "record_id": rec.get("id", i),
            "source_url": rec.get("source_url", ""),
            "checked_on": rec.get("checked_on", ""),
        })
        words += n
    flush()
    return chunks


# ----------------------------------------------------------------- retrieval (BM25)
def tokenize(text):
    toks = re.findall(r"[a-z0-9]+", text.lower())
    toks = [t[:-1] if len(t) > 3 and t.endswith("s") else t for t in toks]
    return ["time" if t in ("timing", "timin") else t for t in toks]


def keywords(question):
    return [t for t in tokenize(question) if t not in STOPWORDS]


class BM25:
    def __init__(self, chunks, k1=1.5, b=0.75):
        self.docs = [tokenize(c["text"]) for c in chunks]
        self.k1, self.b = k1, b
        self.avgdl = sum(len(d) for d in self.docs) / max(len(self.docs), 1)
        self.df = Counter()
        for d in self.docs:
            self.df.update(set(d))
        self.n = len(self.docs)

    def score(self, q_tokens, i):
        d = self.docs[i]
        tf = Counter(d)
        s = 0.0
        for t in q_tokens:
            if t not in tf:
                continue
            idf = math.log(1 + (self.n - self.df[t] + 0.5) / (self.df[t] + 0.5))
            s += idf * tf[t] * (self.k1 + 1) / (tf[t] + self.k1 * (1 - self.b + self.b * len(d) / self.avgdl))
        return s


@lru_cache(maxsize=8)
def _index(chunk_size):
    chunks = build_chunks(load_records(), chunk_size)
    return chunks, BM25(chunks)


def retrieve(question, top_k=4, chunk_size=80):
    chunks, bm25 = _index(chunk_size)
    q = keywords(question)
    scored = sorted(((bm25.score(q, i), i) for i in range(len(chunks))), reverse=True)
    return [dict(chunks[i], score=round(s, 3)) for s, i in scored[:top_k] if s > 0]


# ----------------------------------------------------------------- answering
def _coverage(question, chunk):
    kws = [k for k in keywords(question) if k not in GENERIC]
    if not kws:
        return 0.0
    ctoks = set(tokenize(chunk["text"]))
    return sum(1 for k in kws if k in ctoks) / len(kws)


def _extractive(question, hits, max_lines=3):
    kws = set(keywords(question))
    cand = []
    for rank, ch in enumerate(hits):
        for ln in ch["lines"]:
            overlap = len(kws & set(tokenize(ln["text"])))
            if overlap:
                cand.append((overlap, -rank, ln))
    cand.sort(key=lambda x: (x[0], x[1]), reverse=True)
    if not cand:
        return []
    best = cand[0][0]
    # keep only the lines that match the question as well as the best line does
    return [c[2] for c in cand if c[0] >= best][:max_lines]


def _try_llm(question, lines):
    """Optional: let app/llm.py phrase the answer. Returns None if anything fails."""
    try:
        from app import llm  # your D6 wrapper
    except Exception:
        return None
    context = "\n".join(f"[{i}] {l['text']}" for i, l in enumerate(lines, 1))
    prompt = ("You are the ShirdiYatra assistant. Answer ONLY from the numbered context. "
              "Cite sources like [1]. If the context does not contain the answer, say exactly: I don't know.\n\n"
              f"Context:\n{context}\n\nQuestion: {question}\nAnswer:")
    for name in ("ask_llm", "generate", "complete", "call_llm", "chat_completion", "chat"):
        fn = getattr(llm, name, None)
        if callable(fn):
            try:
                out = fn(prompt)
                if isinstance(out, dict):
                    out = out.get("answer") or out.get("text")
                if isinstance(out, str) and out.strip():
                    return out.strip()
            except Exception:
                continue
    return None


def answer(question, top_k=4, chunk_size=80, use_llm=None):
    if use_llm is None:
        use_llm = os.getenv("RAG_USE_LLM") == "1"
    cfg = {"top_k": top_k, "chunk_size": chunk_size}
    hits = retrieve(question, top_k, chunk_size)

    # ---- "I don't know" gate
    if not hits or hits[0]["score"] < MIN_SCORE or _coverage(question, hits[0]) < MIN_COVERAGE:
        return {"question": question, "answer": IDK, "confident": False,
                "citations": [], "chunks_used": [], "config": cfg, "mode": "refused"}

    lines = _extractive(question, hits)
    if not lines:
        return {"question": question, "answer": IDK, "confident": False,
                "citations": [], "chunks_used": [], "config": cfg, "mode": "refused"}

    # ---- citations: one number per distinct source_url
    numbers, citations = {}, []
    for ln in lines:
        url = ln["source_url"]
        if url not in numbers:
            numbers[url] = len(numbers) + 1
            citations.append({"n": numbers[url], "source_url": url,
                              "record_ids": [], "checked_on": ln["checked_on"], "snippet": ln["text"][:160]})
        citations[numbers[url] - 1]["record_ids"].append(ln["record_id"])

    text, mode = None, "extractive"
    if use_llm:
        text = _try_llm(question, lines)
        mode = "llm" if text else "extractive"
    if not text:
        text = "From the Sansthan pages:\n" + "\n".join(f"- {l['text']} [{numbers[l['source_url']]}]" for l in lines)
    elif "[" not in text:
        text += " " + " ".join(f"[{c['n']}]" for c in citations)

    return {"question": question, "answer": text, "confident": True, "citations": citations,
            "chunks_used": [{"chunk_id": h["chunk_id"], "score": h["score"], "text": h["text"]} for h in hits],
            "config": cfg, "mode": mode}


# ----------------------------------------------------------------- FastAPI route
try:
    from fastapi import APIRouter
    from pydantic import BaseModel, Field

    router = APIRouter(tags=["rag"])

    class AskRequest(BaseModel):
        question: str = Field(..., min_length=3)
        top_k: int = Field(4, ge=1, le=10)
        chunk_size: int = Field(80, ge=20, le=400)
        use_llm: bool = False

    @router.post("/ask")
    def ask(req: AskRequest):
        return answer(req.question, req.top_k, req.chunk_size, req.use_llm)
except ImportError:  # FastAPI not installed - CLI still works
    router = None


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What time is the Kakad aarti?"
    print(json.dumps(answer(q), indent=2, ensure_ascii=False))
