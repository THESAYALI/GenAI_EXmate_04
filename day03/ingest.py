"""S1: clean raw HTML into Record objects and save data/records.json."""
import json
import logging
import re
import sys
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

from app.models import Record

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("ingest")

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_FILE = BASE_DIR / "data" / "records.json"

FAQ_URL = "https://sai.org.in/en/faq"
DAILY_URL = "https://sai.org.in/en/daily-programme"

TIME_ONE = re.compile(r"\d{1,2}[:.]\d{2}\s*(?:AM|PM)", re.I)
TIME_RANGE = re.compile(
    r"\d{1,2}[:.]\d{2}\s*(?:AM|PM)?\s*(?:to|-|–)\s*\d{1,2}[:.]\d{2}\s*(?:AM|PM)",
    re.I,
)
COST = re.compile(r"(?:₹|Rs\.?|INR)\s*([\d,]+)", re.I)

TOPIC_RULES = [
    ("how_to_reach", ["reach", "train", "airport", "bus-stand", "bus stand"]),
    ("darshan", ["darshan", "pass"]),
    ("aarti", ["aarti"]),
    ("food", ["prasadalaya"]),
    ("medical", ["medical", "first aid", "hospital", "blood"]),
    ("stay_and_facilities", ["room", "locker", "baggage"]),
    ("donation", ["donat", "offering"]),
    ("safety", ["lost", "missing"]),
]


def clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def classify(question: str) -> str:
    q = question.lower()
    for topic, words in TOPIC_RULES:
        if any(w in q for w in words):
            return topic
    return "general"


def load_html(name: str) -> str:
    path = RAW_DIR / f"{name}.html"
    return path.read_text(encoding="utf-8")


def load_checked_on() -> dict:
    """Read fetch dates from manifest.json, fall back to today."""
    try:
        manifest = json.loads((RAW_DIR / "manifest.json").read_text(encoding="utf-8"))
        return {k: v.get("fetched_on", "") for k, v in manifest.items()}
    except (OSError, json.JSONDecodeError):
        return {}


# ---------- daily programme ----------
def parse_daily(html: str, checked_on: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    records, skipped = [], 0

    for li in soup.find_all("li"):
        img = li.find("img")
        if not img or "clock-" not in (img.get("src") or ""):
            continue  # not a programme row
        try:
            parts = list(li.stripped_strings)
            if len(parts) < 2:
                raise ValueError(f"expected name and time, got {parts}")
            name, timing = clean(parts[0]), clean(parts[-1])
            if not (TIME_ONE.search(timing) or "sunset" in timing.lower()):
                raise ValueError(f"no valid time in '{timing}'")
            records.append(Record(
                topic="daily_programme",
                place_or_service=name,
                timing=timing,
                cost_inr=None,
                rule_or_tip=None,
                source_url=DAILY_URL,
                checked_on=checked_on,
            ))
        except Exception as e:
            skipped += 1
            log.warning("daily programme: skipped bad row (%s)", e)

    log.info("daily programme: %d records, %d skipped", len(records), skipped)
    return records


# ---------- FAQ ----------
def faq_answer(h4) -> str:
    parts = []
    for sib in h4.next_siblings:
        if getattr(sib, "name", None) == "h4":
            break
        if hasattr(sib, "get_text"):
            parts.append(sib.get_text(" ", strip=True))
        else:
            parts.append(str(sib).strip())
    text = clean(" ".join(parts))

    if not text and h4.parent is not None:  # answer lives in the parent block
        whole = clean(h4.parent.get_text(" ", strip=True))
        text = whole.replace(clean(h4.get_text()), "", 1).strip()

    return re.sub(r"^A\.\s*", "", text).strip()


def parse_faq(html: str, checked_on: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    records, skipped = [], 0

    for h4 in soup.find_all("h4"):
        try:
            question = clean(h4.get_text())
            answer = faq_answer(h4)
            if not question or not answer:
                raise ValueError(f"empty question or answer: '{question[:40]}'")

            time_match = TIME_RANGE.search(answer) or TIME_ONE.search(answer)
            cost_match = COST.search(answer)

            records.append(Record(
                topic=classify(question),
                place_or_service=question.rstrip("?").strip()[:120],
                timing=clean(time_match.group(0)) if time_match else None,
                cost_inr=int(cost_match.group(1).replace(",", "")) if cost_match else None,
                rule_or_tip=answer[:600],
                source_url=FAQ_URL,
                checked_on=checked_on,
            ))
        except Exception as e:
            skipped += 1
            log.warning("faq: skipped bad row (%s)", e)

    log.info("faq: %d records, %d skipped", len(records), skipped)
    return records


# ---------- main ----------
def main() -> int:
    dates = load_checked_on()
    today = date.today().isoformat()
    records = []

    jobs = [
        ("daily_programme", parse_daily),
        ("faq", parse_faq),
    ]
    for name, parser in jobs:
        try:
            html = load_html(name)
        except OSError as e:
            log.error("cannot read data/raw/%s.html (%s). Run: python -m app.fetch", name, e)
            continue
        records.extend(parser(html, dates.get(name) or today))

    # remove duplicates
    seen, unique = set(), []
    for r in records:
        key = (r.topic, r.place_or_service, r.source_url)
        if key not in seen:
            seen.add(key)
            unique.append(r)

    if not unique:
        log.error("no records produced, records.json not written")
        return 1

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps([r.to_dict() for r in unique], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nSaved {len(unique)} records to {OUT_FILE}")
    by_topic = {}
    for r in unique:
        by_topic[r.topic] = by_topic.get(r.topic, 0) + 1
    for topic, n in sorted(by_topic.items()):
        print(f"  {topic}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())