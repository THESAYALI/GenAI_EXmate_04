"""
eval/run_search_eval.py  --  D7 / S1
Runs semantic search for your 10 questions and writes eval/search_results.md.

Questions are read from eval/questions.md (numbered lines like "1. ..." or "Q1: ...").
If fewer than 10 are found, the default ShirdiYatra questions below are used.

Run from the repo root:   python eval/run_search_eval.py
"""
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import vectorstore  # noqa: E402

DEFAULT_QUESTIONS = [
    "What time is the Kakad aarti at Shirdi?",
    "What are the Madhyan (noon) aarti and Dhoop aarti timings?",
    "Which Sansthan room is cheapest for a family of 7?",
    "How do I reach Shirdi from Hyderabad by train?",
    "Which railway station is nearest to Shirdi, and how far is it?",
    "Can single people book a Sansthan room?",
    "How long can we stay in a Sansthan room?",
    "What is the darshan queue like early in the morning?",
    "What is the Shej aarti time?",
    "Is there an online booking facility for accommodation?",
]


def load_questions():
    f = ROOT / "eval" / "questions.md"
    found = []
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*(?:\|\s*)?(?:Q\s*)?\d+\s*[.):\-|]\s*(.+?)\s*\|?\s*$", line)
            if m and len(m.group(1)) > 8:
                found.append(m.group(1))
    return found[:10] if len(found) >= 10 else DEFAULT_QUESTIONS


def main():
    n = vectorstore.build_index()
    print(f"Indexed {n} chunks")
    questions = load_questions()
    lines = [
        "# Semantic search results (D7)",
        "",
        f"Run on {date.today().isoformat()} | chunks indexed: {n} | model: all-MiniLM-L6-v2 | top 3 hits per question",
        "",
        "Verdict column: write **Good / Partial / Miss** yourself after reading the hits.",
        "",
    ]
    summary = ["| # | Question | Top score | Top source | Verdict |", "|---|---|---|---|---|"]
    for i, q in enumerate(questions, start=1):
        hits = vectorstore.semantic_search(q, k=3)
        top = hits[0] if hits else None
        summary.append(f"| {i} | {q} | {top['score'] if top else '-'} | {top['source'] if top else '-'} | _fill in_ |")
        lines += [f"## Q{i}. {q}", ""]
        for r, h in enumerate(hits, start=1):
            snippet = h["text"].replace("\n", " ")
            snippet = snippet[:260] + ("..." if len(snippet) > 260 else "")
            lines += [f"{r}. **score {h['score']}** - {h['title']} (page {h['page']})  ",
                      f"   source: {h['source']}  ",
                      f"   > {snippet}"]
        lines += ["", "**Verdict:** _Good / Partial / Miss - why?_", ""]
    lines += ["## Summary", ""] + summary + [""]
    out = ROOT / "eval" / "search_results.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
