"""Day 13 - production basics for ShirdiYatra.

One file that gives you:
  1. per-request logging of latency + tokens   (logs/requests.jsonl and GET /metrics)
  2. a simple in-memory TTL cache              (same question -> no second LLM call)
  3. input limits                              (empty / too long / huge body -> rejected)
  4. a prompt-injection guard                  (blocked BEFORE the LLM is called)

Use it in app/main.py:
    from app.production import install, guarded_answer
    install(app)
    ...
    return guarded_answer(req.question, lambda q: your_existing_rag_function(q))
"""
from __future__ import annotations

import contextvars
import hashlib
import json
import math
import re
import time
from collections import OrderedDict, deque
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# ----------------------------- settings -------------------------------------
MAX_QUESTION_CHARS = 500          # one pilgrim question never needs more
MAX_BODY_BYTES = 10_000           # reject huge request bodies early
CACHE_TTL_SECONDS = 600           # 10 minutes
CACHE_MAX_ITEMS = 128
LOG_FILE = Path("logs/requests.jsonl")
SKIP_PATHS = {"/health", "/metrics", "/docs", "/openapi.json", "/redoc"}

BLOCKED_ANSWER = (
    "I can only help with planning a Shirdi visit from official Sansthan "
    "information. I can't follow instructions that try to change my rules."
)

INJECTION_PATTERNS = [
    r"ignore (all |any |the )*(previous|prior|above|earlier|system) (instructions?|prompts?|rules?)",
    r"disregard (all |any |the )*(previous|prior|above|system)",
    r"forget (all |your |the )*(previous |prior )?(instructions?|rules?)",
    r"(reveal|show|print|repeat|leak|display).{0,40}(system prompt|hidden prompt|your instructions|your rules)",
    r"what (is|are) your (system prompt|instructions)",
    r"you are now (dan|an? unrestricted|an? unfiltered)",
    r"developer mode",
    r"jailbreak",
    r"</?system>",
]
_INJECTION_RE = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE | re.DOTALL)


# ----------------------------- input checks ---------------------------------
def validate_question(question) -> str:
    """Return a cleaned question or raise HTTPException."""
    if not isinstance(question, str) or not question.strip():
        raise HTTPException(status_code=400, detail="Question is empty.")
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", question).strip()
    if len(cleaned) > MAX_QUESTION_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"Question too long ({len(cleaned)} chars). Max is {MAX_QUESTION_CHARS}.",
        )
    return cleaned


def looks_like_injection(text: str) -> bool:
    return bool(_INJECTION_RE.search(text))


# ----------------------------- cache ----------------------------------------
class TTLCache:
    """Tiny thread-safe LRU cache with expiry."""

    def __init__(self, ttl: float = CACHE_TTL_SECONDS, max_items: int = CACHE_MAX_ITEMS):
        self.ttl = ttl
        self.max_items = max_items
        self._data: OrderedDict = OrderedDict()
        self._lock = Lock()
        self.hits = 0
        self.misses = 0

    def get(self, key: str):
        with self._lock:
            item = self._data.get(key)
            if item is None:
                self.misses += 1
                return None
            expires, value = item
            if expires < time.monotonic():
                del self._data[key]
                self.misses += 1
                return None
            self._data.move_to_end(key)
            self.hits += 1
            return value

    def set(self, key: str, value) -> None:
        with self._lock:
            self._data[key] = (time.monotonic() + self.ttl, value)
            self._data.move_to_end(key)
            while len(self._data) > self.max_items:
                self._data.popitem(last=False)

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / total, 3) if total else 0.0,
            "size": len(self._data),
        }


CACHE = TTLCache()


def make_key(question: str) -> str:
    norm = re.sub(r"\s+", " ", question.lower()).strip(" ?!.")
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


# ----------------------------- stats / logging -------------------------------
_current: contextvars.ContextVar = contextvars.ContextVar("current_request", default=None)
_RECENT: deque = deque(maxlen=1000)
_stats_lock = Lock()


def estimate_tokens(text: str) -> int:
    """Rough fallback: ~4 characters per token."""
    return max(1, len(text or "") // 4)


def add_usage(prompt_tokens: int, completion_tokens: int) -> None:
    """Call this from app/llm.py right after every LLM call (real provider numbers)."""
    info = _current.get()
    if info is None:
        return
    info["prompt_tokens"] += int(prompt_tokens or 0)
    info["completion_tokens"] += int(completion_tokens or 0)
    info["usage_source"] = "provider"


def _flag(**kwargs) -> None:
    info = _current.get()
    if info is not None:
        info.update(kwargs)


def percentile(values: list, p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = max(0, math.ceil(p / 100 * len(ordered)) - 1)
    return float(ordered[idx])


def _write_log(entry: dict) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # logging must never break a request


def metrics_summary() -> dict:
    with _stats_lock:
        rows = list(_RECENT)
    lat = [r["latency_ms"] for r in rows]
    with_tokens = [r for r in rows if r["prompt_tokens"] or r["completion_tokens"]]
    n_tok = len(with_tokens) or 1
    return {
        "requests": len(rows),
        "errors": sum(1 for r in rows if r["status"] >= 400),
        "blocked": sum(1 for r in rows if r["blocked"]),
        "latency_ms": {
            "p50": round(percentile(lat, 50), 1),
            "p95": round(percentile(lat, 95), 1),
            "avg": round(sum(lat) / len(lat), 1) if lat else 0.0,
        },
        "tokens": {
            "avg_prompt": round(sum(r["prompt_tokens"] for r in with_tokens) / n_tok, 1),
            "avg_completion": round(sum(r["completion_tokens"] for r in with_tokens) / n_tok, 1),
            "total": sum(r["prompt_tokens"] + r["completion_tokens"] for r in rows),
            "sources": sorted({r["usage_source"] for r in with_tokens}),
        },
        "cache": CACHE.stats(),
    }


# ----------------------------- FastAPI wiring --------------------------------
def install(app: FastAPI) -> None:
    """Add request logging, body-size limit and GET /metrics."""

    @app.middleware("http")
    async def _log_requests(request: Request, call_next):
        if request.url.path in SKIP_PATHS:
            return await call_next(request)

        info = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "usage_source": "none",
            "cache_hit": False,
            "blocked": False,
        }
        token = _current.set(info)
        start = time.perf_counter()
        status = 500
        try:
            length = request.headers.get("content-length")
            if length and length.isdigit() and int(length) > MAX_BODY_BYTES:
                status = 413
                return JSONResponse({"detail": "Request body too large."}, status_code=413)
            response = await call_next(request)
            status = response.status_code
            return response
        finally:
            latency_ms = round((time.perf_counter() - start) * 1000, 1)
            _current.reset(token)
            entry = {
                "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "method": request.method,
                "path": request.url.path,
                "status": status,
                "latency_ms": latency_ms,
                **info,
            }
            with _stats_lock:
                _RECENT.append(entry)
            _write_log(entry)

    @app.get("/metrics")
    def metrics():
        return metrics_summary()


def guarded_answer(question, answer_fn):
    """Validate -> injection check -> cache -> call answer_fn(question)."""
    q = validate_question(question)

    if looks_like_injection(q):
        _flag(blocked=True)
        return {"answer": BLOCKED_ANSWER, "citations": [], "blocked": True}

    key = make_key(q)
    hit = CACHE.get(key)
    if hit is not None:
        _flag(cache_hit=True)
        return {**hit, "cached": True}

    result = answer_fn(q)
    if hasattr(result, "model_dump"):      # pydantic model -> dict
        result = result.model_dump()
    elif not isinstance(result, dict):
        result = {"answer": str(result)}

    info = _current.get()
    if info is not None and info["usage_source"] == "none":
        # llm.py did not report usage -> estimate (prompt side excludes retrieved context)
        info["prompt_tokens"] = estimate_tokens(q)
        info["completion_tokens"] = estimate_tokens(str(result.get("answer", "")))
        info["usage_source"] = "estimated"

    CACHE.set(key, result)
    return result
