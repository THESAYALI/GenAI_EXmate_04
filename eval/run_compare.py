"""eval/run_compare.py - runs the 10 questions through prompt v1 and prompt v2
and writes the result table into eval/prompt_compare.md.

Run from the project root (after putting your key in .env):
    python eval/run_compare.py
It makes 20 LLM calls (10 questions x 2 prompts). With the free tier it can take 5 to 8 minutes
because the script waits when the provider's rate limit is reached.
"""
import re
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.chat import run_chat_raw  # noqa: E402
from app.llm import LLMError, model_name, provider_name  # noqa: E402
from app.smart_search import SmartSearch, load_default  # noqa: E402

QUESTIONS_FILE = ROOT / "eval" / "questions.md"
OUTPUT_FILE = ROOT / "eval" / "prompt_compare.md"
VERSIONS = ["v1", "v2"]
PAUSE_SECONDS = 10   # pause between calls so the free-tier tokens-per-minute limit is not hit
RETRY_WAIT = 45      # seconds to wait when the provider says "429 rate limit"
MAX_TRIES = 4


def read_questions():
    """Read lines like '1. What time ...' from eval/questions.md."""
    questions = []
    for line in QUESTIONS_FILE.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if match:
            text = re.sub(r"\*\*\(.*?\)\*\*", "", match.group(2)).strip()
            questions.append((int(match.group(1)), text))
    return questions


def cell(text, limit=230):
    """Make text safe for one markdown table cell."""
    text = " ".join(str(text).split()).replace("|", "/")
    return text if len(text) <= limit else text[:limit - 3] + "..."


def call_with_retry(question, records, version):
    """Call the LLM; if the provider says 429 (rate limit), wait and try again."""
    for attempt in range(1, MAX_TRIES + 1):
        try:
            return run_chat_raw(question, records, version)
        except LLMError as exc:
            if "429" in str(exc) and attempt < MAX_TRIES:
                print(f"rate limit, waiting {RETRY_WAIT}s (try {attempt}/{MAX_TRIES}) ...", end=" ", flush=True)
                time.sleep(RETRY_WAIT)
                continue
            raise


def main():
    questions = read_questions()
    if len(questions) != 10:
        print(f"Warning: found {len(questions)} questions in eval/questions.md (expected 10).")
    search = SmartSearch(load_default())
    results = {v: {} for v in VERSIONS}

    for number, question in questions:
        records = search.search(question, top_k=3)
        for version in VERSIONS:
            print(f"Q{number} {version} ...", end=" ", flush=True)
            try:
                reply, ok, _raw = call_with_retry(question, records, version)
                results[version][number] = {"reply": reply, "ok": ok}
                print(reply["confidence"])
            except LLMError as exc:
                print("ERROR")
                print(f"  {exc}")
                results[version][number] = {
                    "reply": {"answer": f"ERROR: {exc}", "confidence": "-", "follow_up": ""}, "ok": False}
            time.sleep(PAUSE_SECONDS)

    lines = []
    lines.append("# Prompt comparison: v1 vs v2\n")
    lines.append(f"Generated on {datetime.now():%d %b %Y %H:%M} by `eval/run_compare.py` "
                 f"(provider: **{provider_name()}**, model: **{model_name()}**, temperature 0.2).\n")
    lines.append("## The two prompt versions\n")
    lines.append("| | v1 (`prompts/task_answer_v1.md`) | v2 (`prompts/task_answer_v2.md`) |")
    lines.append("|---|---|---|")
    lines.append("| Style | Short and simple: question + records + one instruction | Step by step with 5 steps, rules for each confidence level and 2 format examples |")
    lines.append("| Handles missing data | Only the general rule in the system prompt | Explicit step: do not use a nearby record, answer \"low\" |")
    lines.append("| Handles live questions | Not mentioned | Explicit: queue, crowd and availability need live data |")
    lines.append("| Follow-up | Free choice | Must help a family planning a trip |")
    lines.append("| Cost | Fewer tokens | More tokens per call |\n")

    lines.append("## Summary\n")
    lines.append("| Check | v1 | v2 |")
    lines.append("|---|---|---|")
    valid = {v: sum(1 for r in results[v].values() if r["ok"]) for v in VERSIONS}
    low = {v: sum(1 for r in results[v].values() if r["reply"]["confidence"] == "low") for v in VERSIONS}
    q6 = {v: results[v].get(6, {}).get("reply", {}).get("confidence", "-") for v in VERSIONS}
    lines.append(f"| Valid JSON replies | {valid['v1']}/10 | {valid['v2']}/10 |")
    lines.append(f"| Replies with confidence \"low\" | {low['v1']} | {low['v2']} |")
    lines.append(f"| Confidence on Q6 (must be low) | {q6['v1']} | {q6['v2']} |\n")

    lines.append("## Results per question\n")
    lines.append("| # | Question | v1 answer | v1 conf. | v2 answer | v2 conf. |")
    lines.append("|---|---|---|---|---|---|")
    for number, question in questions:
        a = results["v1"].get(number, {"reply": {"answer": "-", "confidence": "-"}})["reply"]
        b = results["v2"].get(number, {"reply": {"answer": "-", "confidence": "-"}})["reply"]
        lines.append(f"| {number} | {cell(question, 90)} | {cell(a['answer'])} | {a['confidence']} "
                     f"| {cell(b['answer'])} | {b['confidence']} |")
    lines.append("")

    lines.append("## My conclusion (write 4 to 5 lines in your own words)\n")
    lines.append("- Which version gave more correct, grounded answers? ...")
    lines.append("- Which version was more honest on Q6 (the question the data cannot answer)? ...")
    lines.append("- Which version gave better follow-up questions? ...")
    lines.append("- Which prompt will I keep, and why? ...")
    lines.append("- One thing I would improve next: ...\n")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSaved {OUTPUT_FILE}. Open it and write your conclusion at the bottom.")


if __name__ == "__main__":
    main()