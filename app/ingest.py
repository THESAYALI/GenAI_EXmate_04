"""app/ingest.py - clean the saved HTML in data/raw/ into records (Day 3).

Run from the project root, after `python -m app.fetch`:
    python -m app.ingest

Reads  data/raw/daily-programme.html, accomodations.html, faq.html
Writes data/records.json (list of records, each with an id).
Bad rows are skipped with try/except and reported, never crash the run.
Only official sai.org.in URLs are kept; checked_on comes from data/raw/manifest.json.
"""
import json
import os
import re
import sys
from datetime import date
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from app.models import Record

BASE = os.path.join(os.path.dirname(__file__), "..", "data")
RAW_DIR = os.path.join(BASE, "raw")
OUT_FILE = os.path.join(BASE, "records.json")
OFFICIAL_DOMAIN = "sai.org.in"

URLS = {
    "daily-programme": "https://sai.org.in/en/daily-programme",
    "accomodations": "https://sai.org.in/en/accomodations",
    "faq": "https://sai.org.in/en/faq",
}

TIME = r"\d{1,2}:\d{2}\s*(?:AM|PM)?"
TIME_ROW = re.compile(rf"^(?:{TIME}(?:\s*-\s*{TIME})?|At Sunset)$", re.I)
AARTIS = ("kakad aarti", "mid-day aarti", "dhoop aarti", "shej aarti")


def is_official(url):
    host = urlparse(url).netloc.lower()
    return host == OFFICIAL_DOMAIN or host.endswith("." + OFFICIAL_DOMAIN)


def clean(text):
    return re.sub(r"\s+", " ", text or "").strip()


def text_lines(html):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style"]):
        tag.decompose()
    return [clean(line) for line in soup.get_text("\n").split("\n") if clean(line)]


# ---- daily programme: a name line followed by a time line -------------------
def parse_programme(html, url, checked_on):
    records, problems = [], []
    lines = text_lines(html)
    for i, line in enumerate(lines):
        if not TIME_ROW.match(line) or i == 0:
            continue
        try:
            name = lines[i - 1]
            if TIME_ROW.match(name):
                raise ValueError(f"time '{line}' has no name before it")
            tip = ("One of the four main aartis" if any(a in name.lower() for a in AARTIS)
                   else "As listed on the daily programme")
            records.append(Record("Daily programme", name, line, None, tip, url, checked_on))
        except (ValueError, IndexError) as e:
            problems.append(f"daily-programme line {i}: {e}")
    return records, problems


# ---- room tariff tables -------------------------------------------------------
def to_int(text):
    m = re.search(r"\d+", text or "")
    return int(m.group()) if m else None


def parse_rooms(html, url, checked_on):
    records, problems, seen = [], [], set()
    soup = BeautifulSoup(html, "lxml")
    for table in soup.find_all("table"):
        for n, tr in enumerate(table.find_all("tr"), start=1):
            cells = [clean(td.get_text(" ")) for td in tr.find_all(["td"])]
            if len(cells) < 7:
                continue                      # header row or not a tariff row
            try:
                _, location, room_type, desc, min_cap, max_cap, rate = cells[:7]
                remark = cells[7] if len(cells) > 7 else ""
                cost, lo, hi = to_int(rate), to_int(min_cap), to_int(max_cap)
                if not location or cost is None or lo is None or hi is None:
                    raise ValueError(f"{location or 'row ' + str(n)}: no rate or capacity listed")
                kind = "non-AC" if "non" in room_type.lower() else "AC"
                key = (location, kind, desc, lo, hi, cost)
                if key in seen:
                    continue
                seen.add(key)
                name = f"{location} - {kind}" + (f" {desc}" if desc else " room")
                tip = f"{lo}-{hi} persons" + (f". {remark}" if remark else "")
                records.append(Record("Accommodation", name, "Per day, stay 24-48 hours",
                                      cost, tip, url, checked_on))
            except (ValueError, IndexError) as e:
                problems.append(f"accomodations table row {n}: {e}")
    return records, problems


# ---- FAQ facts (darshan, prasadalaya, how to reach) -------------------------
def parse_faq(html, url, checked_on):
    records, problems = [], []
    text = clean(BeautifulSoup(html, "lxml").get_text(" "))
    time = r"(\d{1,2}[:.]\d{2}\s*[AP]M)"
    facts = [
        ("Darshan", "Samadhi Mandir darshan queue",
         rf"Darshan will open from {time}\s*TO\s*{time}", "{0} to {1}", "General darshan queue timing per FAQ"),
        ("Food", "Shri Saibaba Prasadalaya",
         rf"Prasadalaya are open from {time}\s*to\s*{time}", "{0} to {1}", "Prasadalaya opening hours per FAQ"),
        ("Travel", "Shirdi airport (SAG)",
         r"airport \(SAG\)\s*just\s*(\d+)\s*km", "{0} km from Shirdi", "Nearest airport per FAQ"),
        ("Travel", "Kopargaon railway station",
         r"Kopargaon \(at\s*(\d+)\s*Km", "{0} km from Shirdi", "Nearby railway station per FAQ"),
        ("Travel", "Sainagar Shirdi railway station",
         r"Sainagar\s*\(at\s*(\d+)\s*Km", "{0} km from Shirdi", "Nearest railway station per FAQ"),
    ]
    for topic, name, pattern, timing_fmt, tip in facts:
        m = re.search(pattern, text, re.I)
        if not m:
            problems.append(f"faq: could not find '{name}'")
            continue
        records.append(Record(topic, name, timing_fmt.format(*m.groups()), None, tip, url, checked_on))
    return records, problems


PARSERS = {"daily-programme": parse_programme, "accomodations": parse_rooms, "faq": parse_faq}


def load_manifest():
    try:
        with open(os.path.join(RAW_DIR, "manifest.json"), encoding="utf-8") as f:
            return {e["name"]: e for e in json.load(f)}
    except (OSError, ValueError):
        return {}


def ingest():
    """Return (records, problems) built from data/raw/."""
    manifest = load_manifest()
    records, problems = [], []
    for name, parser in PARSERS.items():
        path = os.path.join(RAW_DIR, f"{name}.html")
        if not os.path.exists(path):
            problems.append(f"{name}: data/raw/{name}.html not found (run python -m app.fetch)")
            continue
        url = URLS[name]
        if not is_official(url):
            problems.append(f"{name}: not an official source")
            continue
        checked_on = manifest.get(name, {}).get("fetched_on") or str(date.fromtimestamp(os.path.getmtime(path)))
        try:
            with open(path, encoding="utf-8") as f:
                got, probs = parser(f.read(), url, checked_on)
        except Exception as e:      # a whole page failing must not stop the others
            problems.append(f"{name}: could not parse ({type(e).__name__}: {e})")
            continue
        records.extend(got)
        problems.extend(probs)
    return records, problems


def save(records, path=OUT_FILE):
    rows = [{"id": i, **r.to_dict()} for i, r in enumerate(records, start=1)]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    return rows


def main():
    records, problems = ingest()
    if not records:
        print("No records built.")
        for p in problems:
            print("  -", p)
        return 1
    save(records)
    print(f"Saved {len(records)} records to data/records.json")
    for r in records:
        print(" -", r.short())
    if problems:
        print(f"\n{len(problems)} skipped/problem row(s):")
        for p in problems:
            print("  WARNING:", p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
