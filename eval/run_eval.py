"""
D8 - S2: evaluate the RAG endpoint logic on eval/eval_set.json with 2 configs
(chunk size / top-k). Prints a table, writes eval/results.json + eval/results.md
and puts the winner table into README.md (between the EVAL markers).

Run from the repo root:   python eval/run_eval.py
Optional (uses your LLM): python eval/run_eval.py --use-llm
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from app import rag  # noqa: E402

CONFIGS = [
    {"name": "A: small chunks, top-3", "chunk_size": 40, "top_k": 3},
    {"name": "B: big chunks, top-5", "chunk_size": 120, "top_k": 5},
]
START, END = "<!-- EVAL_TABLE_START -->", "<!-- EVAL_TABLE_END -->"


def run_config(rows, cfg, use_llm):
    per_q, ok_all, retr, retr_n, idk_ok, idk_n, cited, cited_n = [], 0, 0, 0, 0, 0, 0, 0
    for r in rows:
        res = rag.answer(r["question"], cfg["top_k"], cfg["chunk_size"], use_llm)
        ans = res["answer"].lower()
        kws = [k.lower() for k in r["expected_keywords"]]
        if r["answerable"]:
            retrieved = " ".join(c["text"] for c in res["chunks_used"]).lower()
            kw_in_answer = res["confident"] and any(k in ans for k in kws)
            kw_in_chunks = any(k in retrieved for k in kws)
            retr_n += 1
            retr += kw_in_chunks
            cited_n += 1
            cited += bool(res["citations"])
            correct = kw_in_answer
        else:
            idk_n += 1
            correct = not res["confident"]
            idk_ok += correct
        ok_all += correct
        per_q.append({"id": r["id"], "answerable": r["answerable"], "correct": bool(correct),
                      "confident": res["confident"], "citations": len(res["citations"])})
    n = len(rows)
    return {
        "config": cfg,
        "accuracy": round(ok_all / n, 3),
        "retrieval_hit": round(retr / max(retr_n, 1), 3),
        "idk_correct": round(idk_ok / max(idk_n, 1), 3),
        "citation_rate": round(cited / max(cited_n, 1), 3),
        "per_question": per_q,
    }


def table(results, winner):
    lines = ["| Config | chunk_size (words) | top_k | Answer accuracy | Retrieval hit | 'I don't know' correct | Citation rate | Winner |",
             "|---|---|---|---|---|---|---|---|"]
    for r in results:
        c = r["config"]
        lines.append(f"| {c['name']} | {c['chunk_size']} | {c['top_k']} | {r['accuracy']:.0%} | {r['retrieval_hit']:.0%} "
                     f"| {r['idk_correct']:.0%} | {r['citation_rate']:.0%} | {'**YES**' if r is winner else ''} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--use-llm", action="store_true")
    args = ap.parse_args()

    rows = json.loads((ROOT / "eval" / "eval_set.json").read_text(encoding="utf-8"))
    assert len(rows) == 15, f"eval_set.json must have 15 rows, found {len(rows)}"

    results = [run_config(rows, c, args.use_llm) for c in CONFIGS]
    # winner: accuracy, then retrieval hit, then fewer chunks sent (cheaper)
    winner = max(results, key=lambda r: (r["accuracy"], r["retrieval_hit"], -r["config"]["top_k"]))
    md_table = table(results, winner)

    (ROOT / "eval" / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    detail = ["| Q | answerable | correct | confident | citations (A) | correct (B) |", "|---|---|---|---|---|---|"]
    for a, b in zip(results[0]["per_question"], results[1]["per_question"]):
        detail.append(f"| {a['id']} | {a['answerable']} | {a['correct']} | {a['confident']} | {a['citations']} | {b['correct']} |")
    (ROOT / "eval" / "results.md").write_text(
        f"# Eval results (15 questions)\n\n{md_table}\n\nWinner: **{winner['config']['name']}**\n\n## Per question\n\n" + "\n".join(detail) + "\n",
        encoding="utf-8")

    readme = ROOT / "README.md"
    if readme.exists():
        txt = readme.read_text(encoding="utf-8")
        block = f"{START}\n{md_table}\n\nWinner: **{winner['config']['name']}**\n{END}"
        if START in txt and END in txt:
            txt = txt[:txt.index(START)] + block + txt[txt.index(END) + len(END):]
        else:
            txt += "\n\n" + block + "\n"
        readme.write_text(txt, encoding="utf-8")

    print(md_table)
    print("\nWinner:", winner["config"]["name"])
    print("Saved eval/results.json, eval/results.md and updated README.md")


if __name__ == "__main__":
    main()
