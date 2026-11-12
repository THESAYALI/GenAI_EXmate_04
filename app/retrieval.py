"""Tiny keyword-based retrieval. No LLM, no network - easy to read and test."""

import re
from typing import Optional

from app.data import FACTS

# Words that carry no meaning for matching.
STOPWORDS = {
    "a", "an", "the", "is", "are", "of", "to", "in", "at", "for", "and", "or",
    "do", "does", "i", "my", "me", "we", "what", "which", "when", "where", "how",
    "can", "there", "it", "on", "any", "from", "near", "get", "much",
}

# Words that mean the user wants LIVE information. Our data is static,
# so we must refuse these instead of guessing.
LIVE_WORDS = {"now", "current", "currently", "live", "today", "tonight", "wait", "waiting", "queue", "crowd"}

NOT_FOUND = (
    "Sorry, I don't have that information. My data only covers general, "
    "static facts about Shirdi (aarti and darshan timings, travel, stay, food, "
    "nearby places, booking). Please check the official Sansthan website or helpline."
)


def tokenize(text: str) -> list[str]:
    """Lowercase the text and split it into meaningful words."""
    words = re.findall(r"[a-z]+", text.lower())
    return [w for w in words if w not in STOPWORDS]


def find_best_match(question: str) -> tuple[Optional[dict], int]:
    """Return (best_fact, score) for the question, or (None, 0) if nothing fits.

    Score = how many question words appear in a fact's keyword list.
    A question asking for live info (queue, now, current...) is rejected,
    because static data can never answer it correctly.
    """
    words = set(tokenize(question))

    if words & LIVE_WORDS:
        return None, 0

    best_fact, best_score = None, 0
    for fact in FACTS:
        score = len(words & set(fact["keywords"]))
        if score > best_score:
            best_fact, best_score = fact, score

    return best_fact, best_score


def answer_question(question: str) -> dict:
    """Public helper used by the API: always returns a dict with an answer."""
    fact, score = find_best_match(question)
    if fact is None:
        return {"answered": False, "answer": NOT_FOUND, "source": None, "score": 0}
    return {"answered": True, "answer": fact["answer"], "source": fact["id"], "score": score}