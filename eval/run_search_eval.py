"""Run the 10 ShirdiYatra questions through semantic search
and write eval/search_results.md (top hits: source, page, distance)."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import vectorstore as vs  # noqa: E402

TOP_K = 3
QUESTIONS_FILE = ROOT / "eval" / "questions.md"
OUT_FILE = ROOT / "eval" / "search_results.md"


def load_questions():
    qs = []
    for line in QUESTIONS_FILE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\s*(?:\d+[.)]|[-*])\s*(?:Q\d+[:.)]?\s*)?(.+\?)\s*$", line)
        if m:
            qs.append(m.group(1).strip())
    return qs[:10]


def get_search_fn():
    for name in ("search", "semantic_search", "query", "search_chunks"):
        if hasattr(vs, name):
            return getattr(vs, name)
    raise SystemExit("No search function found in app/vectorstore.py - rename it in get_search_fn()")


def main():
    search = get_search_fn()
    questions = load_questions()
    lines = ["# Semantic search results", "",
             f"Top {TOP_K} hits per question (lower distance = closer match).", ""]
    for i, q in enumerate(questions, 1):
        lines += [f"## Q{i}. {q}", "",
                  "| # | Source | Page | Title | Distance |",
                  "|---|--------|------|-------|----------|"]
        hits = search(q, TOP_K)
        for rank, h in enumerate(hits, 1):
            meta = h.get("metadata", h)
            lines.append(
                f"| {rank} | {meta.get('source', '')} | {meta.get('page', '')} | "
                f"{meta.get('title', '')} | {float(h.get('distance', 0)):.4f} |"
            )
        lines.append("")
    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_FILE} for {len(questions)} questions")


if __name__ == "__main__":
    main()