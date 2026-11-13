"""app/chat.py - builds the prompt, calls the LLM, and checks the JSON reply.

Flow:  question + retrieved records -> prompts/ files -> ask_llm() -> parse_reply()
"""
import json
import re
from pathlib import Path

from app.llm import ask_llm

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

# Two versions of the task prompt (compared in eval/prompt_compare.md)
TASK_FILES = {"v1": "task_answer_v1.md", "v2": "task_answer_v2.md"}

NO_DATA_REPLY = {
    "answer": "I don't have that information in the Sansthan data I was given.",
    "confidence": "low",
    "follow_up": "Please check the official website https://sai.org.in or ask at the Sansthan office in Shirdi.",
}


def load_prompt(filename: str) -> str:
    """Read one prompt file from the prompts/ folder."""
    return (PROMPT_DIR / filename).read_text(encoding="utf-8").strip()


def build_user_prompt(task_template: str, question: str, records) -> str:
    """Put the question and the records into the task prompt placeholders."""
    context = json.dumps(records, ensure_ascii=False, indent=2, default=str) if records else "[]"
    return task_template.replace("{question}", question).replace("{context}", context)


def parse_reply(raw: str):
    """Turn the model text into {answer, confidence, follow_up}.

    Returns (reply, ok). ok is False when the model did not give valid JSON;
    then we still return a safe reply with confidence "low".
    """
    text = (raw or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    start, end = text.find("{"), text.rfind("}")
    data = None
    if start != -1 and end > start:
        try:
            data = json.loads(text[start:end + 1])
        except json.JSONDecodeError:
            data = None
    if not isinstance(data, dict) or "answer" not in data:
        fallback = (raw or "").strip() or "Sorry, I could not prepare an answer."
        return {"answer": fallback, "confidence": "low", "follow_up": ""}, False
    confidence = str(data.get("confidence", "low")).strip().lower()
    if confidence not in ("high", "medium", "low"):
        confidence = "low"
    reply = {
        "answer": str(data["answer"]).strip(),
        "confidence": confidence,
        "follow_up": str(data.get("follow_up") or "").strip(),
    }
    return reply, True


def run_chat_raw(question: str, records, version: str = "v2"):
    """Full pipeline. Returns (reply, json_ok, raw_text)."""
    if version not in TASK_FILES:
        raise ValueError(f"Unknown prompt version '{version}'. Use one of {list(TASK_FILES)}.")
    if not records:  # nothing retrieved -> do not ask the model to guess
        return dict(NO_DATA_REPLY), True, ""
    system_prompt = load_prompt("system.md")
    task_template = load_prompt(TASK_FILES[version])
    user_prompt = build_user_prompt(task_template, question, records)
    raw = ask_llm(system_prompt, user_prompt)
    reply, ok = parse_reply(raw)
    return reply, ok, raw


def run_chat(question: str, records, version: str = "v2") -> dict:
    """Same as run_chat_raw but returns only the reply dictionary."""
    return run_chat_raw(question, records, version)[0]
