"""Offline tests for Day 06 (no API key and no internet needed).

Run from the project root:   python tests/test_day06.py
(or with pytest:             pytest tests/test_day06.py)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import chat  # noqa: E402


def test_parse_plain_json():
    reply, ok = chat.parse_reply('{"answer": "Hi", "confidence": "high", "follow_up": "When?"}')
    assert ok and reply == {"answer": "Hi", "confidence": "high", "follow_up": "When?"}


def test_parse_json_inside_code_fence():
    raw = '```json\n{"answer": "Hi", "confidence": "Medium", "follow_up": ""}\n```'
    reply, ok = chat.parse_reply(raw)
    assert ok and reply["confidence"] == "medium"


def test_parse_bad_text_gives_safe_low_reply():
    reply, ok = chat.parse_reply("sorry, no json here")
    assert not ok and reply["confidence"] == "low" and reply["answer"]


def test_unknown_confidence_becomes_low():
    reply, ok = chat.parse_reply('{"answer": "x", "confidence": "very sure"}')
    assert ok and reply["confidence"] == "low"


def test_build_user_prompt_fills_placeholders():
    text = chat.build_user_prompt("Q={question}\nC={context}", "aarti?", [{"timing": "5:15"}])
    assert "aarti?" in text and "5:15" in text and "{question}" not in text


def test_no_records_means_no_llm_call():
    reply, ok, raw = chat.run_chat_raw("anything", [], "v2")
    assert ok and reply["confidence"] == "low" and raw == ""


def test_prompt_files_exist():
    for name in ["system.md", "task_answer_v1.md", "task_answer_v2.md"]:
        assert (ROOT / "prompts" / name).read_text(encoding="utf-8").strip()


def test_pipeline_with_fake_llm():
    original = chat.ask_llm
    chat.ask_llm = lambda system, user: json.dumps(
        {"answer": "5:15 AM", "confidence": "high", "follow_up": "Which day?"})
    try:
        reply = chat.run_chat("Kakad aarti time?", [{"timing": "5:15 AM"}], "v1")
    finally:
        chat.ask_llm = original
    assert reply["confidence"] == "high"


def test_env_is_ignored_and_example_has_no_real_key():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in [line.strip() for line in gitignore], ".env must be listed in .gitignore"
    example = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "your_groq_key_here" in example and "gsk_" not in example and "AIza" not in example


if __name__ == "__main__":
    failed = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("PASS", name)
            except AssertionError as exc:
                failed += 1
                print("FAIL", name, exc)
    sys.exit(1 if failed else 0)
